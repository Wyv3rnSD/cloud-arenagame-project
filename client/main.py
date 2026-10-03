import math
import pygame
import random

from camera import Camera
from crate import Crate
from GUNS.pellet import Pellet
from GUNS.shotgun import Shotgun
from map import GameMap
from maps import load_map, map_choices
from network import NetworkManager
from player import Player
from powerups import (
    roll_powerup_type,
    apply_powerup,
    POWERUP_TYPES
)
from remote_player import RemotePlayer
from config import SLOT_COLORS
from UI.create_lobby import CreateLobbyScreen
from UI.join_lobby import JoinLobbyScreen
from UI.lobby_screen import LobbyScreen
from UI.map_select_screen import MapSelectScreen
from UI.multiplayer_menu import MultiplayerMenu
from UI.title_screen import TitleScreen

# Initialize Pygame
pygame.init()

# Screen Settings
WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cloud Arena - Multiplayer")

# World Settings
WORLD_WIDTH = 3000
WORLD_HEIGHT = 2000

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.Font(None, 36)
crate_font = pygame.font.Font(None, 22)
status_font = pygame.font.Font(None, 32)
hud_font = pygame.font.Font(None, 26)

# UI Screens
MAP_CHOICES = map_choices()
DEFAULT_MAP_KEY = MAP_CHOICES[0][0]

title_screen = TitleScreen(WIDTH, HEIGHT)
multiplayer_menu = MultiplayerMenu(WIDTH, HEIGHT)
create_lobby_screen = CreateLobbyScreen(WIDTH, HEIGHT, MAP_CHOICES)
join_lobby_screen = JoinLobbyScreen(WIDTH, HEIGHT)
lobby_screen = LobbyScreen(WIDTH, HEIGHT)
map_select_screen = MapSelectScreen(WIDTH, HEIGHT, MAP_CHOICES)

# Networking
network = NetworkManager()
network.start()

# Game State
game_state = "title"
is_multiplayer = False
remote_players = {}  # player_id -> RemotePlayer
last_net_update_time = 0

# Game Objects
player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
camera = Camera(WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
game_map = GameMap(load_map(DEFAULT_MAP_KEY))
shotgun = Shotgun()
pellets = []

# Powerup Crates
crate = None
CRATE_FIRST_SPAWN_DELAY = 3000
CRATE_RESPAWN_DELAY = 8000
next_crate_time = 0
pickup_notice = None
PICKUP_NOTICE_DURATION = 2200

# Respawn
RESPAWN_DELAY = 3000
respawn_at = None

# Stat Viewer (hold TAB)
show_stats = False


def spawn_crate():
    if not game_map.crate_spawns:
        return None
    x, y = random.choice(game_map.crate_spawns)
    crate_type = roll_powerup_type()
    return Crate(x, y, crate_type)


def start_match(map_key, spawn_pos=None, is_multi=False):
    global game_map, shotgun, pellets
    global crate, next_crate_time
    global pickup_notice, is_multiplayer
    global respawn_at

    is_multiplayer = is_multi
    respawn_at = None
    game_map = GameMap(load_map(map_key))

    if spawn_pos:
        player.position.x = spawn_pos[0]
        player.position.y = spawn_pos[1]
    else:
        spawn_x, spawn_y = game_map.spawns[0]
        player.position.x = spawn_x
        player.position.y = spawn_y

    player.velocity = pygame.Vector2(0, 0)
    player.health = player.max_health
    player.shield = player.max_shield
    player.speed_multiplier = 1.0
    player.controls_scrambled = False
    player.frozen_until = 0

    shotgun = Shotgun()
    pellets = []
    crate = None
    pickup_notice = None

    if not is_multiplayer or (is_multiplayer and network.is_host):
        next_crate_time = pygame.time.get_ticks() + CRATE_FIRST_SPAWN_DELAY
    else:
        # Non-host clients receive crate spawns from the host/server
        next_crate_time = float("inf")


def draw_grid(screen, camera):
    grid_size = 100
    for x in range(0, WORLD_WIDTH + 1, grid_size):
        screen_x = x - camera.position.x
        pygame.draw.line(screen, (50, 50, 55), (screen_x, 0), (screen_x, HEIGHT))

    for y in range(0, WORLD_HEIGHT + 1, grid_size):
        screen_y = y - camera.position.y
        pygame.draw.line(screen, (50, 50, 55), (0, screen_y), (WIDTH, screen_y))


def draw_crosshair(screen):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    size = 10
    gap = 4

    pygame.draw.line(screen, (255, 255, 255), (mouse_x - size, mouse_y), (mouse_x - gap, mouse_y), 2)
    pygame.draw.line(screen, (255, 255, 255), (mouse_x + gap, mouse_y), (mouse_x + size, mouse_y), 2)
    pygame.draw.line(screen, (255, 255, 255), (mouse_x, mouse_y - size), (mouse_x, mouse_y - gap), 2)
    pygame.draw.line(screen, (255, 255, 255), (mouse_x, mouse_y + gap), (mouse_x, mouse_y + size), 2)
    pygame.draw.circle(screen, (255, 255, 255), (mouse_x, mouse_y), 2)


def draw_ammo(screen, shotgun, font):
    ammo_text = f"{shotgun.ammo}/{shotgun.reserve_ammo}"
    ammo_surface = font.render(ammo_text, True, (255, 255, 255))
    ammo_rect = ammo_surface.get_rect(topright=(WIDTH - 25, 20))
    screen.blit(ammo_surface, ammo_rect)

    if shotgun.reloading:
        reload_surface = font.render("RELOADING...", True, (255, 220, 100))
        reload_rect = reload_surface.get_rect(topright=(WIDTH - 25, 55))
        screen.blit(reload_surface, reload_rect)


def draw_health(screen, player):
    bar_width = 250
    bar_height = 20
    x = 25
    y = 25

    # Health Background & Bar
    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
    health_width = bar_width * max(0, player.health) / player.max_health
    pygame.draw.rect(screen, (60, 200, 80), (x, y, health_width, bar_height))

    # Shield Background & Bar
    shield_y = y + bar_height + 5
    pygame.draw.rect(screen, (50, 50, 50), (x, shield_y, bar_width, bar_height))
    shield_width = bar_width * max(0, player.shield) / player.max_shield
    pygame.draw.rect(screen, (60, 140, 255), (x, shield_y, shield_width, bar_height))


def draw_status_effect(screen, player, font):
    label = None
    color = (255, 255, 255)

    if player.is_frozen():
        label = "FROZEN"
        color = (150, 220, 255)
    elif player.controls_scrambled:
        label = "CONTROLS SCRAMBLED"
        color = (200, 80, 200)
    elif player.speed_multiplier > 1:
        label = "SPEED BOOST"
        color = (255, 200, 60)
    elif player.speed_multiplier < 1:
        label = "SLOWED"
        color = (140, 140, 140)

    if label is None:
        return

    status_surface = font.render(label, True, color)
    status_rect = status_surface.get_rect(midtop=(WIDTH // 2, 20))
    screen.blit(status_surface, status_rect)


def draw_pickup_notice(screen, notice, font):
    if notice is None:
        return

    label, color, end_time = notice
    if pygame.time.get_ticks() >= end_time:
        return

    notice_surface = font.render(label, True, color)
    notice_rect = notice_surface.get_rect(midtop=(WIDTH // 2, 60))
    screen.blit(notice_surface, notice_rect)


def draw_multiplayer_hud(screen, hud_font):
    if not is_multiplayer:
        return

    # Room Code badge top-right below ammo
    room_text = f"ROOM: {network.room_code}"
    room_surf = hud_font.render(room_text, True, (180, 180, 185))
    screen.blit(room_surf, (WIDTH - 150, 95))

    # Alive players count
    alive_remote = sum(1 for rp in remote_players.values() if rp.is_alive)
    total_alive = alive_remote + (1 if player.health > 0 else 0)
    alive_text = f"ALIVE: {total_alive}/{len(remote_players) + 1}"
    alive_surf = hud_font.render(alive_text, True, (220, 220, 220))
    screen.blit(alive_surf, (25, 80))


def draw_stats_panel(screen, hud_font, status_font, player, remote_players, is_multiplayer):
    entries = [(player.name, player.slot, player.health, player.shield, player.max_health, player.max_shield, player.health > 0)]
    if is_multiplayer:
        for rp in remote_players.values():
            entries.append((rp.name, rp.slot, rp.health, rp.shield, rp.max_health, rp.max_shield, rp.is_alive))
    entries.sort(key=lambda e: e[1])

    panel_width = 340
    row_height = 34
    panel_height = 50 + row_height * len(entries)
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = 90

    panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_surf.fill((20, 20, 25, 215))
    screen.blit(panel_surf, (panel_x, panel_y))
    pygame.draw.rect(screen, (90, 90, 100), (panel_x, panel_y, panel_width, panel_height), 2)

    title_surf = status_font.render("PLAYER STATS", True, (240, 240, 240))
    screen.blit(title_surf, (panel_x + panel_width // 2 - title_surf.get_width() // 2, panel_y + 10))

    row_y = panel_y + 46
    for name, slot, health, shield, max_health, max_shield, alive in entries:
        color = SLOT_COLORS[slot % len(SLOT_COLORS)]
        pygame.draw.circle(screen, color, (panel_x + 24, row_y + 11), 8)

        name_color = (230, 230, 230) if alive else (140, 140, 140)
        name_surf = hud_font.render(name, True, name_color)
        screen.blit(name_surf, (panel_x + 42, row_y + 2))

        if alive:
            status_text = f"HP {max(0, int(health))}/{int(max_health)}  SH {max(0, int(shield))}/{int(max_shield)}"
            status_color = (200, 200, 200)
        else:
            status_text = "ELIMINATED"
            status_color = (220, 80, 80)
        status_surf = hud_font.render(status_text, True, status_color)
        screen.blit(status_surf, (panel_x + panel_width - status_surf.get_width() - 15, row_y + 2))

        row_y += row_height


# ==================== MAIN GAME LOOP ====================
running = True

while running:
    current_time = pygame.time.get_ticks()

    # ---------------- Network Message Polling ----------------
    for msg in network.poll_messages():
        msg_type = msg.get("type")

        if msg_type == "room_created":
            player.player_id = network.player_id
            player.slot = network.slot
            player.name = network.player_name
            create_lobby_screen.set_status("")
            game_state = "lobby"

        elif msg_type == "room_joined":
            player.player_id = network.player_id
            player.slot = network.slot
            player.name = network.player_name
            join_lobby_screen.set_status("")
            game_state = "lobby"

        elif msg_type == "error":
            err = msg.get("message", "An error occurred")
            if game_state == "create_lobby":
                create_lobby_screen.set_status(err, is_error=True)
            elif game_state == "join_lobby":
                join_lobby_screen.set_status(err, is_error=True)

        elif msg_type == "match_start":
            map_key = msg.get("map", "arena1")
            spawns = msg.get("spawns", {})
            players_data = msg.get("players", [])

            remote_players.clear()
            for p in players_data:
                pid = p["id"]
                if pid != network.player_id:
                    pos = spawns.get(pid, (150, 150))
                    remote_players[pid] = RemotePlayer(pid, p["name"], p["slot"], pos[0], pos[1])

            my_spawn = spawns.get(network.player_id, (150, 150))
            start_match(map_key, spawn_pos=my_spawn, is_multi=True)
            game_state = "game"
            pygame.mouse.set_visible(False)

        elif msg_type == "players_state":
            players_dict = msg.get("players", {})
            for pid, pdata in players_dict.items():
                if pid in remote_players:
                    remote_players[pid].update_state(pdata)

        elif msg_type == "player_shot":
            pid = msg.get("player_id")
            for p in msg.get("pellets", []):
                pellets.append(Pellet(
                    (p["x"], p["y"]),
                    (p["dx"], p["dy"]),
                    p["v"],
                    p["dmg"],
                    effect=p.get("eff"),
                    owner_id=pid
                ))

        elif msg_type == "player_damaged":
            target = msg.get("target_id")
            damage = msg.get("damage", 8)
            if target == network.player_id and player.health > 0:
                player.take_damage(damage)
                if msg.get("is_freeze"):
                    player.apply_freeze(3000)

        elif msg_type == "crate_spawned":
            cdata = msg.get("crate")
            if cdata:
                crate = Crate(cdata["x"], cdata["y"], cdata["crate_type"])

        elif msg_type == "crate_collected":
            crate = None
            pid = msg.get("player_id")
            ptype = msg.get("powerup_type")
            if pid != network.player_id and ptype in POWERUP_TYPES:
                _, label, color = POWERUP_TYPES[ptype]
                collector_name = remote_players[pid].name if pid in remote_players else "Opponent"
                pickup_notice = (
                    f"{collector_name.upper()} PICKED UP: {label}",
                    color,
                    current_time + PICKUP_NOTICE_DURATION
                )

        elif msg_type == "player_disconnected":
            pid = msg.get("player_id")
            if pid in remote_players:
                del remote_players[pid]

    # ---------------- Event Handling ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Title Screen
        if game_state == "title":
            action = title_screen.handle_event(event)
            if action == "multiplayer":
                game_state = "multiplayer_menu"
            elif action == "map_select":
                game_state = "map_select"
            elif action == "quit":
                running = False

        # Multiplayer Menu
        elif game_state == "multiplayer_menu":
            action = multiplayer_menu.handle_event(event)
            if action == "create":
                game_state = "create_lobby"
            elif action == "join":
                game_state = "join_lobby"
            elif action == "back":
                game_state = "title"

        # Create Lobby
        elif game_state == "create_lobby":
            result = create_lobby_screen.handle_event(event)
            if result:
                action, name, map_key = result
                if action == "create":
                    create_lobby_screen.set_status("Connecting to cloud...", is_error=False)
                    network.create_room(name, map_key)
                elif action == "back":
                    game_state = "multiplayer_menu"

        # Join Lobby
        elif game_state == "join_lobby":
            result = join_lobby_screen.handle_event(event)
            if result:
                action, code, name = result
                if action == "join":
                    join_lobby_screen.set_status("Joining lobby...", is_error=False)
                    network.join_room(code, name)
                elif action == "back":
                    game_state = "multiplayer_menu"

        # Lobby Screen
        elif game_state == "lobby":
            action = lobby_screen.handle_event(event, network.is_host)
            if action == "start":
                network.start_match()
            elif action == "leave":
                network.leave_room()
                game_state = "multiplayer_menu"

        # Map Select Screen (Solo Practice)
        elif game_state == "map_select":
            action = map_select_screen.handle_event(event)
            if action == "back":
                game_state = "title"
            elif action is not None:
                start_match(action, is_multi=False)
                game_state = "game"
                pygame.mouse.set_visible(False)

        # In-Game
        elif game_state == "game":
            # Shoot
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if player.health > 0:
                    new_pellets = shotgun.shoot(player, camera, pellets)
                    if new_pellets and is_multiplayer:
                        p_data = [{
                            "x": round(pellet.position.x, 1),
                            "y": round(pellet.position.y, 1),
                            "dx": round(pellet.direction.x, 3),
                            "dy": round(pellet.direction.y, 3),
                            "v": pellet.velocity,
                            "dmg": pellet.damage,
                            "eff": pellet.effect
                        } for pellet in new_pellets]
                        network.send_shoot(p_data)

            # Keyboard
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if player.health > 0:
                        shotgun.start_reload()

                if event.key == pygame.K_ESCAPE:
                    if is_multiplayer:
                        network.leave_room()
                        game_state = "multiplayer_menu"
                    else:
                        game_state = "title"
                    pygame.mouse.set_visible(True)

                # Local damage test
                if event.key == pygame.K_h:
                    player.take_damage(20)

                if event.key == pygame.K_TAB:
                    show_stats = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_TAB:
                    show_stats = False

    # ---------------- Screen Rendering ----------------
    if game_state == "title":
        pygame.mouse.set_visible(True)
        title_screen.draw(screen)

    elif game_state == "multiplayer_menu":
        pygame.mouse.set_visible(True)
        multiplayer_menu.draw(screen)

    elif game_state == "create_lobby":
        pygame.mouse.set_visible(True)
        create_lobby_screen.draw(screen)

    elif game_state == "join_lobby":
        pygame.mouse.set_visible(True)
        join_lobby_screen.draw(screen)

    elif game_state == "lobby":
        pygame.mouse.set_visible(True)
        map_display_name = dict(MAP_CHOICES).get(network.current_map, network.current_map)
        lobby_screen.draw(screen, network.room_code, network.room_players, map_display_name, network.is_host)

    elif game_state == "map_select":
        pygame.mouse.set_visible(True)
        map_select_screen.draw(screen)

    elif game_state == "game":
        # 0. Respawn Handling
        if player.health <= 0:
            if respawn_at is None:
                respawn_at = current_time + RESPAWN_DELAY
            elif current_time >= respawn_at:
                if game_map.spawns:
                    if is_multiplayer:
                        spawn_idx = player.slot % len(game_map.spawns)
                    else:
                        spawn_idx = random.randrange(len(game_map.spawns))
                    spawn_x, spawn_y = game_map.spawns[spawn_idx]
                    player.position.x = spawn_x
                    player.position.y = spawn_y

                player.velocity = pygame.Vector2(0, 0)
                player.health = player.max_health
                player.shield = player.max_shield
                player.speed_multiplier = 1.0
                player.controls_scrambled = False
                player.frozen_until = 0
                respawn_at = None
        else:
            respawn_at = None

        # 1. Update Local Player
        if player.health > 0:
            player.update(WORLD_WIDTH, WORLD_HEIGHT, game_map.walls)
        shotgun.update()
        camera.update(player)

        # 2. Update Remote Players
        if is_multiplayer:
            for rp in remote_players.values():
                rp.update()

        # 3. Update Pellets & Check Hits
        for pellet in pellets:
            pellet.update(game_map.walls)

            # Hit Local Player (if shot by opponent)
            if is_multiplayer and pellet.active and player.health > 0:
                if pellet.owner_id is not None and pellet.owner_id != network.player_id:
                    if (pellet.position - player.position).length() <= player.radius + pellet.radius:
                        pellet.active = False
                        player.take_damage(pellet.damage)
                        if pellet.effect == "freeze":
                            player.apply_freeze(3000)
                        network.send_hit_player(network.player_id, pellet.damage, pellet.effect == "freeze")

        pellets = [p for p in pellets if p.active]

        # 4. Periodic Network Player State Broadcast (~30 Hz)
        if is_multiplayer and current_time - last_net_update_time >= 33:
            last_net_update_time = current_time
            aim_dir = player.get_aim_direction(camera)
            aim_angle = math.atan2(aim_dir.y, aim_dir.x) if aim_dir.length() > 0 else 0.0

            status_label = None
            if player.is_frozen():
                status_label = "FROZEN"
            elif player.controls_scrambled:
                status_label = "CONTROLS SCRAMBLED"
            elif player.speed_multiplier > 1:
                status_label = "SPEED BOOST"
            elif player.speed_multiplier < 1:
                status_label = "SLOWED"

            network.send_player_update(
                player.position.x,
                player.position.y,
                player.velocity.x,
                player.velocity.y,
                aim_angle,
                player.health,
                player.shield,
                status_label
            )

        # 5. Crates Logic
        if not is_multiplayer or (is_multiplayer and network.is_host):
            if crate is None and current_time >= next_crate_time:
                crate = spawn_crate()
                if crate and is_multiplayer:
                    network.send_crate_spawn(1, crate.rect.centerx, crate.rect.centery, crate.crate_type)

        if crate is not None and player.health > 0 and player.rect.colliderect(crate.rect):
            apply_powerup(player, shotgun, crate.crate_type)
            _, picked_label, picked_color = POWERUP_TYPES[crate.crate_type]
            pickup_notice = (
                f"PICKED UP: {picked_label}",
                picked_color,
                current_time + PICKUP_NOTICE_DURATION
            )
            if is_multiplayer:
                network.send_pickup_crate(1, crate.crate_type)
            crate = None
            if not is_multiplayer or (is_multiplayer and network.is_host):
                next_crate_time = current_time + CRATE_RESPAWN_DELAY

        # 6. Render World
        screen.fill((25, 25, 30))
        draw_grid(screen, camera)
        game_map.draw(screen, camera)

        # Draw Crate
        if crate is not None:
            crate.draw(screen, camera, crate_font)

        # Draw Pellets
        for pellet in pellets:
            pellet.draw(screen, camera)

        # Draw Remote Players
        if is_multiplayer:
            for rp in remote_players.values():
                rp.draw(screen, camera)

        # Draw Local Player
        if player.health > 0:
            player.draw(screen, camera)
        else:
            # Eliminated Overlay
            elim_surf = font.render("YOU HAVE BEEN ELIMINATED", True, (240, 60, 60))
            elim_rect = elim_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            screen.blit(elim_surf, elim_rect)

            if respawn_at is not None:
                seconds_left = max(0, (respawn_at - current_time) / 1000)
                respawn_surf = status_font.render(f"Respawning in {seconds_left:.1f}s", True, (200, 200, 200))
                respawn_rect = respawn_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 15))
                screen.blit(respawn_surf, respawn_rect)

            esc_surf = hud_font.render("Press ESC to return to lobby", True, (160, 160, 160))
            esc_rect = esc_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 45))
            screen.blit(esc_surf, esc_rect)

        # 7. Render UI & HUD
        draw_health(screen, player)
        draw_ammo(screen, shotgun, font)
        draw_crosshair(screen)
        draw_status_effect(screen, player, status_font)
        draw_pickup_notice(screen, pickup_notice, status_font)
        draw_multiplayer_hud(screen, hud_font)

        if show_stats:
            draw_stats_panel(screen, hud_font, status_font, player, remote_players, is_multiplayer)

    # Display update & 60 FPS tick
    pygame.display.flip()
    clock.tick(FPS)

# Clean Exit
network.stop()
pygame.quit()
