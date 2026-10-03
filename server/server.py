import asyncio
import json
import logging
import os
import random
import string
import time
from http import HTTPStatus

import websockets

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("GameServer")

# Room code alphabet: letters and numbers excluding ambiguous characters (0, O, 1, I, L)
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
MAX_PLAYERS_PER_ROOM = 4

# Map spawn positions for 4 players (corners)
DEFAULT_SPAWNS = [
    (150, 150),     # Slot 0: Top-Left
    (2850, 150),    # Slot 1: Top-Right
    (150, 1850),    # Slot 2: Bottom-Left
    (2850, 1850),   # Slot 3: Bottom-Right
]


class ConnectedPlayer:
    def __init__(self, player_id, name, websocket, slot, is_host=False):
        self.player_id = player_id
        self.name = name
        self.websocket = websocket
        self.slot = slot
        self.is_host = is_host
        self.ready = False
        self.last_state = {
            "x": 0.0,
            "y": 0.0,
            "vx": 0.0,
            "vy": 0.0,
            "aim_angle": 0.0,
            "health": 100,
            "shield": 50,
            "status": None
        }

    def to_dict(self):
        return {
            "id": self.player_id,
            "name": self.name,
            "slot": self.slot,
            "is_host": self.is_host,
            "ready": self.ready
        }


class GameRoom:
    def __init__(self, code, host_player, map_key="arena1"):
        self.code = code
        self.host_id = host_player.player_id
        self.map_key = map_key
        self.state = "lobby"  # "lobby" or "in_game"
        self.players = {host_player.player_id: host_player}
        self.available_slots = [1, 2, 3]  # Slot 0 is taken by host
        self.created_at = time.time()
        self.crate_state = None

    def add_player(self, player_id, name, websocket):
        if len(self.players) >= MAX_PLAYERS_PER_ROOM:
            return None, "Room is full (max 4 players)"
        if self.state != "lobby":
            return None, "Match has already started"

        slot = self.available_slots.pop(0) if self.available_slots else len(self.players)
        player = ConnectedPlayer(player_id, name, websocket, slot, is_host=False)
        self.players[player_id] = player
        return player, None

    def remove_player(self, player_id):
        if player_id not in self.players:
            return None

        player = self.players.pop(player_id)
        if player.slot in [0, 1, 2, 3] and player.slot not in self.available_slots:
            self.available_slots.append(player.slot)
            self.available_slots.sort()

        # Host migration if the host left
        if player.is_host and self.players:
            new_host_id = next(iter(self.players.keys()))
            self.players[new_host_id].is_host = True
            self.host_id = new_host_id
            logger.info(f"Room {self.code}: New host is {self.players[new_host_id].name}")

        return player

    def get_summary(self):
        return {
            "code": self.code,
            "map": self.map_key,
            "state": self.state,
            "players": [p.to_dict() for p in self.players.values()],
            "max_players": MAX_PLAYERS_PER_ROOM
        }

    async def broadcast(self, message, exclude_id=None):
        payload = json.dumps(message)
        dead_connections = []
        for pid, player in self.players.items():
            if exclude_id and pid == exclude_id:
                continue
            try:
                await player.websocket.send(payload)
            except Exception:
                dead_connections.append(pid)

        for pid in dead_connections:
            self.remove_player(pid)


class RoomManager:
    def __init__(self):
        self.rooms = {}  # code -> GameRoom
        self.player_room_map = {}  # player_id -> code

    def generate_code(self):
        for _ in range(100):
            code = "".join(random.choices(CODE_ALPHABET, k=4))
            if code not in self.rooms:
                return code
        # Fallback to 5 chars if dense
        return "".join(random.choices(CODE_ALPHABET, k=5))

    def create_room(self, player_id, player_name, websocket, map_key="arena1"):
        code = self.generate_code()
        host = ConnectedPlayer(player_id, player_name, websocket, slot=0, is_host=True)
        room = GameRoom(code, host, map_key=map_key)
        self.rooms[code] = room
        self.player_room_map[player_id] = code
        logger.info(f"Room {code} created by {player_name} (ID: {player_id}) on map {map_key}")
        return room, host

    def join_room(self, code, player_id, player_name, websocket):
        code = code.upper().strip()
        room = self.rooms.get(code)
        if not room:
            return None, None, f"Room '{code}' does not exist"

        player, err = room.add_player(player_id, player_name, websocket)
        if err:
            return None, None, err

        self.player_room_map[player_id] = code
        logger.info(f"Player {player_name} joined room {code} (Slot {player.slot})")
        return room, player, None

    def get_room_for_player(self, player_id):
        code = self.player_room_map.get(player_id)
        if code:
            return self.rooms.get(code)
        return None

    def remove_player(self, player_id):
        code = self.player_room_map.pop(player_id, None)
        if not code or code not in self.rooms:
            return None, None

        room = self.rooms[code]
        player = room.remove_player(player_id)
        logger.info(f"Player {player_id} left room {code}")

        if not room.players:
            # Room is empty, destroy it
            del self.rooms[code]
            logger.info(f"Room {code} closed (empty)")
            return None, player

        return room, player


manager = RoomManager()


async def tick_broadcast_loop():
    """Runs at 30 ticks/second to broadcast real-time game snapshots to active matches."""
    tick_rate = 30
    tick_interval = 1.0 / tick_rate

    while True:
        start_time = time.time()
        for room in list(manager.rooms.values()):
            if room.state == "in_game":
                # Aggregate active states of players in this room
                players_snapshot = {}
                for pid, p in room.players.items():
                    players_snapshot[pid] = {
                        "slot": p.slot,
                        "name": p.name,
                        **p.last_state
                    }

                msg = {
                    "type": "players_state",
                    "players": players_snapshot
                }
                await room.broadcast(msg)

        elapsed = time.time() - start_time
        sleep_duration = max(0.001, tick_interval - elapsed)
        await asyncio.sleep(sleep_duration)


async def handle_client(websocket):
    player_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    logger.info(f"Client connected: {player_id} from {websocket.remote_address}")

    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type")

            # ---------------- LOBBY ACTIONS ----------------
            if msg_type == "create_room":
                player_name = data.get("name", "Player").strip() or "Player"
                map_key = data.get("map", "arena1")
                room, host = manager.create_room(player_id, player_name, websocket, map_key)

                await websocket.send(json.dumps({
                    "type": "room_created",
                    "room_code": room.code,
                    "player_id": player_id,
                    "slot": host.slot,
                    "is_host": True,
                    "map": room.map_key,
                    "room_data": room.get_summary()
                }))

            elif msg_type == "join_room":
                room_code = data.get("room_code", "").upper().strip()
                player_name = data.get("name", "Player").strip() or "Player"
                room, player, err = manager.join_room(room_code, player_id, player_name, websocket)

                if err:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": err
                    }))
                else:
                    # Notify joiner
                    await websocket.send(json.dumps({
                        "type": "room_joined",
                        "room_code": room.code,
                        "player_id": player_id,
                        "slot": player.slot,
                        "is_host": False,
                        "map": room.map_key,
                        "room_data": room.get_summary()
                    }))
                    # Notify all others in room
                    await room.broadcast({
                        "type": "room_update",
                        "room_data": room.get_summary()
                    })

            elif msg_type == "leave_room":
                room, player = manager.remove_player(player_id)
                if room:
                    await room.broadcast({
                        "type": "room_update",
                        "room_data": room.get_summary(),
                        "left_player": player.name if player else "A player"
                    })
                await websocket.send(json.dumps({"type": "left_room"}))

            elif msg_type == "change_map":
                room = manager.get_room_for_player(player_id)
                if room and room.host_id == player_id:
                    new_map = data.get("map", "arena1")
                    room.map_key = new_map
                    await room.broadcast({
                        "type": "room_update",
                        "room_data": room.get_summary()
                    })

            elif msg_type == "start_match":
                room = manager.get_room_for_player(player_id)
                if room and room.host_id == player_id and room.state == "lobby":
                    room.state = "in_game"
                    # Generate spawn positions map: player_id -> (x, y)
                    spawns = {}
                    for pid, p in room.players.items():
                        spawn_idx = p.slot % len(DEFAULT_SPAWNS)
                        spawns[pid] = DEFAULT_SPAWNS[spawn_idx]

                    logger.info(f"Match started in room {room.code} on {room.map_key} with {len(room.players)} players")
                    await room.broadcast({
                        "type": "match_start",
                        "map": room.map_key,
                        "spawns": spawns,
                        "players": [p.to_dict() for p in room.players.values()]
                    })

            # ---------------- GAMEPLAY ACTIONS ----------------
            elif msg_type == "player_update":
                room = manager.get_room_for_player(player_id)
                if room and player_id in room.players:
                    player = room.players[player_id]
                    player.last_state = {
                        "x": data.get("x", 0.0),
                        "y": data.get("y", 0.0),
                        "vx": data.get("vx", 0.0),
                        "vy": data.get("vy", 0.0),
                        "aim_angle": data.get("aim_angle", 0.0),
                        "health": data.get("health", 100),
                        "shield": data.get("shield", 50),
                        "status": data.get("status", None)
                    }

            elif msg_type == "shoot":
                room = manager.get_room_for_player(player_id)
                if room and room.state == "in_game":
                    # Broadcast shot event to other players in the room immediately
                    await room.broadcast({
                        "type": "player_shot",
                        "player_id": player_id,
                        "pellets": data.get("pellets", [])
                    }, exclude_id=player_id)

            elif msg_type == "hit_player":
                room = manager.get_room_for_player(player_id)
                if room and room.state == "in_game":
                    target_id = data.get("target_id")
                    damage = data.get("damage", 8)
                    is_freeze = data.get("is_freeze", False)
                    await room.broadcast({
                        "type": "player_damaged",
                        "target_id": target_id,
                        "attacker_id": player_id,
                        "damage": damage,
                        "is_freeze": is_freeze
                    })

            elif msg_type == "crate_spawn":
                room = manager.get_room_for_player(player_id)
                if room and room.host_id == player_id:
                    room.crate_state = {
                        "id": data.get("crate_id"),
                        "x": data.get("x"),
                        "y": data.get("y"),
                        "crate_type": data.get("crate_type")
                    }
                    await room.broadcast({
                        "type": "crate_spawned",
                        "crate": room.crate_state
                    })

            elif msg_type == "pickup_crate":
                room = manager.get_room_for_player(player_id)
                if room and room.state == "in_game":
                    crate_id = data.get("crate_id")
                    powerup_type = data.get("powerup_type")
                    room.crate_state = None
                    await room.broadcast({
                        "type": "crate_collected",
                        "crate_id": crate_id,
                        "player_id": player_id,
                        "powerup_type": powerup_type
                    })

            elif msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logger.error(f"Error handling client {player_id}: {e}")
    finally:
        room, player = manager.remove_player(player_id)
        if room:
            await room.broadcast({
                "type": "room_update",
                "room_data": room.get_summary(),
                "left_player": player.name if player else "A player"
            })
            if room.state == "in_game":
                await room.broadcast({
                    "type": "player_disconnected",
                    "player_id": player_id
                })
        logger.info(f"Client disconnected: {player_id}")


async def process_request(*args):
    """Answer Render HTTP health checks on the same port as WebSockets."""
    if len(args) == 2 and hasattr(args[1], "path"):
        connection, request = args
        is_websocket = request.headers.get("Upgrade", "").lower() == "websocket"
        if request.path in ("/", "/health", "/healthz") and not is_websocket:
            return connection.respond(HTTPStatus.OK, "ok\n")
        return None

    path, request_headers = args
    is_websocket = request_headers.get("Upgrade", "").lower() == "websocket"
    if path in ("/", "/health", "/healthz") and not is_websocket:
        return HTTPStatus.OK, [("Content-Type", "text/plain")], b"ok\n"
    return None


async def main():
    port = int(os.environ.get("PORT", 8765))
    host = "0.0.0.0"

    logger.info(f"Starting Cloud Arena Game Server on {host}:{port}...")

    # Start tick loop
    asyncio.create_task(tick_broadcast_loop())

    async with websockets.serve(
        handle_client,
        host,
        port,
        process_request=process_request,
        ping_interval=20,
        ping_timeout=20,
    ):
        logger.info(f"Server is listening on ws://{host}:{port}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shut down by user.")
