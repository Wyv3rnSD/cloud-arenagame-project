import asyncio
import json
import logging
import queue
import threading
import websockets
try:
    from config import DEFAULT_SERVER_URL
except ImportError:
    from client.config import DEFAULT_SERVER_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NetworkManager")


class NetworkManager:
    def __init__(self, server_url=DEFAULT_SERVER_URL):
        self.server_url = server_url
        self.websocket = None
        self.loop = None
        self.thread = None
        self.running = False

        # Thread-safe queue for incoming messages consumed by Pygame main thread
        self.in_queue = queue.Queue()

        # Internal asyncio queue for outgoing messages
        self.out_queue = None

        # Network State
        self.connected = False
        self.connection_error = None
        self.player_id = None
        self.player_name = "Player"
        self.room_code = None
        self.is_host = False
        self.slot = 0
        self.current_map = "arena1"
        self.room_players = []  # list of player dicts
        self.last_error = None

    def start(self, server_url=None):
        """Starts the background networking thread."""
        if self.running:
            return

        if server_url:
            self.server_url = server_url

        self.running = True
        self.thread = threading.Thread(target=self._thread_main, daemon=True)
        self.thread.start()

    def _thread_main(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connection_loop())

    async def _connection_loop(self):
        self.out_queue = asyncio.Queue()
        while self.running:
            try:
                logger.info(f"Connecting to {self.server_url}...")
                async with websockets.connect(
                    self.server_url,
                    ping_interval=20,
                    ping_timeout=20
                ) as ws:
                    self.websocket = ws
                    self.connected = True
                    self.connection_error = None
                    logger.info("Connected to server!")

                    # Notify Pygame
                    self.in_queue.put({"type": "_connected"})

                    # Run sender and receiver concurrently
                    receiver_task = asyncio.create_task(self._receive_loop(ws))
                    sender_task = asyncio.create_task(self._send_loop(ws))

                    done, pending = await asyncio.wait(
                        [receiver_task, sender_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    for task in pending:
                        task.cancel()

            except Exception as e:
                self.connected = False
                self.connection_error = str(e)
                logger.warning(f"Connection error: {e}. Retrying in 2 seconds...")
                self.in_queue.put({"type": "_connection_error", "error": str(e)})
                await asyncio.sleep(2.0)

    async def _receive_loop(self, ws):
        try:
            async for message in ws:
                try:
                    data = json.loads(message)
                    self._handle_internal_state(data)
                    self.in_queue.put(data)
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        finally:
            self.connected = False

    async def _send_loop(self, ws):
        while self.running:
            msg = await self.out_queue.get()
            try:
                payload = json.dumps(msg)
                await ws.send(payload)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                break

    def _handle_internal_state(self, data):
        """Update internal network state so client code can inspect it directly."""
        msg_type = data.get("type")

        if msg_type == "room_created":
            self.room_code = data.get("room_code")
            self.player_id = data.get("player_id")
            self.slot = data.get("slot", 0)
            self.is_host = True
            self.current_map = data.get("map", "arena1")
            self.room_players = data.get("room_data", {}).get("players", [])
            self.last_error = None

        elif msg_type == "room_joined":
            self.room_code = data.get("room_code")
            self.player_id = data.get("player_id")
            self.slot = data.get("slot", 1)
            self.is_host = data.get("is_host", False)
            self.current_map = data.get("map", "arena1")
            self.room_players = data.get("room_data", {}).get("players", [])
            self.last_error = None

        elif msg_type == "room_update":
            room_data = data.get("room_data", {})
            self.room_players = room_data.get("players", [])
            self.current_map = room_data.get("map", self.current_map)
            # Recheck if we became the host via host migration
            for p in self.room_players:
                if p.get("id") == self.player_id and p.get("is_host"):
                    self.is_host = True

        elif msg_type == "error":
            self.last_error = data.get("message", "Unknown error")

        elif msg_type == "left_room":
            self.room_code = None
            self.is_host = False
            self.room_players = []

    def send(self, data):
        """Thread-safe call to enqueue a message to send to the server."""
        if not self.running or not self.loop:
            return
        if self.out_queue is not None:
            self.loop.call_soon_threadsafe(self.out_queue.put_nowait, data)

    def poll_messages(self):
        """Call this in the Pygame game loop every frame to get all received messages."""
        messages = []
        while not self.in_queue.empty():
            try:
                messages.append(self.in_queue.get_nowait())
            except queue.Empty:
                break
        return messages

    # ---------- Public Convenience Actions ----------

    def create_room(self, player_name, map_key="arena1"):
        self.player_name = player_name
        self.send({
            "type": "create_room",
            "name": player_name,
            "map": map_key
        })

    def join_room(self, room_code, player_name):
        self.player_name = player_name
        self.send({
            "type": "join_room",
            "room_code": room_code,
            "name": player_name
        })

    def leave_room(self):
        self.send({"type": "leave_room"})

    def change_map(self, map_key):
        self.send({"type": "change_map", "map": map_key})

    def start_match(self):
        self.send({"type": "start_match"})

    def send_player_update(self, x, y, vx, vy, aim_angle, health, shield, status):
        self.send({
            "type": "player_update",
            "x": round(x, 2),
            "y": round(y, 2),
            "vx": round(vx, 2),
            "vy": round(vy, 2),
            "aim_angle": round(aim_angle, 3),
            "health": health,
            "shield": shield,
            "status": status
        })

    def send_shoot(self, pellets_data):
        self.send({
            "type": "shoot",
            "pellets": pellets_data
        })

    def send_hit_player(self, target_id, damage, is_freeze=False):
        self.send({
            "type": "hit_player",
            "target_id": target_id,
            "damage": damage,
            "is_freeze": is_freeze
        })

    def send_crate_spawn(self, crate_id, x, y, crate_type):
        self.send({
            "type": "crate_spawn",
            "crate_id": crate_id,
            "x": x,
            "y": y,
            "crate_type": crate_type
        })

    def send_pickup_crate(self, crate_id, powerup_type):
        self.send({
            "type": "pickup_crate",
            "crate_id": crate_id,
            "powerup_type": powerup_type
        })

    def stop(self):
        self.running = False
        if self.loop and self.loop.is_running():
            async def _cleanup():
                try:
                    if self.websocket:
                        await self.websocket.close()
                except Exception:
                    pass
            try:
                fut = asyncio.run_coroutine_threadsafe(_cleanup(), self.loop)
                fut.result(timeout=0.5)
            except Exception:
                pass
            self.loop.call_soon_threadsafe(self.loop.stop)
