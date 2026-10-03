import math
import pygame
try:
    from config import SLOT_COLORS
except ImportError:
    from client.config import SLOT_COLORS


class RemotePlayer:
    def __init__(self, player_id, name, slot, x, y):
        self.player_id = player_id
        self.name = name
        self.slot = slot
        self.color = SLOT_COLORS[slot % len(SLOT_COLORS)]

        self.position = pygame.Vector2(x, y)
        self.target_position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.aim_angle = 0.0

        self.radius = 20
        self.health = 100
        self.max_health = 100
        self.shield = 50
        self.max_shield = 50
        self.status = None
        self.is_alive = True

        self.font = pygame.font.Font(None, 22)

    def update_state(self, data):
        self.target_position.x = data.get("x", self.target_position.x)
        self.target_position.y = data.get("y", self.target_position.y)
        self.velocity.x = data.get("vx", 0)
        self.velocity.y = data.get("vy", 0)
        self.aim_angle = data.get("aim_angle", self.aim_angle)
        self.health = data.get("health", self.health)
        self.shield = data.get("shield", self.shield)
        self.status = data.get("status", None)
        self.is_alive = self.health > 0

    def update(self):
        # Smooth interpolation towards target network position
        diff = self.target_position - self.position
        if diff.length() > 250:
            # Snap if teleported or huge lag spike
            self.position = self.target_position.copy()
        else:
            self.position += diff * 0.35

    def draw(self, screen, camera):
        if not self.is_alive:
            return

        screen_pos = camera.apply(self.position)
        center = (int(screen_pos.x), int(screen_pos.y))

        # Status color or base slot color
        if self.status == "FROZEN":
            body_color = (150, 220, 255)
        elif self.status == "CONTROLS SCRAMBLED":
            body_color = (200, 80, 200)
        elif self.status == "SPEED BOOST":
            body_color = (255, 210, 70)
        elif self.status == "SLOWED":
            body_color = (140, 140, 140)
        else:
            body_color = self.color

        # Body circle
        pygame.draw.circle(screen, body_color, center, self.radius)
        # Outline
        pygame.draw.circle(screen, (30, 30, 35), center, self.radius, 2)

        # Aim barrel / line
        barrel_length = 26
        barrel_end = (
            int(screen_pos.x + math.cos(self.aim_angle) * barrel_length),
            int(screen_pos.y + math.sin(self.aim_angle) * barrel_length)
        )
        pygame.draw.line(screen, (240, 240, 240), center, barrel_end, 3)

        # Name plate above head
        name_surf = self.font.render(self.name, True, (245, 245, 245))
        name_rect = name_surf.get_rect(center=(center[0], center[1] - 38))
        screen.blit(name_surf, name_rect)

        # Mini Health & Shield Bar above head
        bar_width = 46
        bar_height = 5
        bar_x = center[0] - bar_width // 2
        bar_y = center[1] - 26

        # Health background & bar
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        hp_pct = max(0.0, min(1.0, self.health / self.max_health))
        pygame.draw.rect(screen, (60, 200, 80), (bar_x, bar_y, int(bar_width * hp_pct), bar_height))

        # Shield bar (if any shield)
        if self.shield > 0:
            shield_pct = max(0.0, min(1.0, self.shield / self.max_shield))
            pygame.draw.rect(screen, (60, 140, 255), (bar_x, bar_y - 3, int(bar_width * shield_pct), 2))
