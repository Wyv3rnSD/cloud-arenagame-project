import pygame
from UI.button import Button
try:
    from config import SLOT_COLORS
except ImportError:
    from client.config import SLOT_COLORS


class LobbyScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.title_font = pygame.font.Font(None, 65)
        self.code_font = pygame.font.Font(None, 80)
        self.label_font = pygame.font.Font(None, 30)
        self.slot_font = pygame.font.Font(None, 34)
        self.badge_font = pygame.font.Font(None, 24)
        self.button_font = pygame.font.Font(None, 45)

        center_x = screen_width // 2

        # Buttons
        btn_width = 300
        btn_height = 65

        self.start_button = Button(
            center_x - btn_width - 15,
            605,
            btn_width,
            btn_height,
            "START MATCH",
            self.button_font
        )
        self.start_button.normal_color = (100, 205, 120)
        self.start_button.hover_color = (130, 230, 150)

        self.leave_button = Button(
            center_x + 15,
            605,
            btn_width,
            btn_height,
            "LEAVE LOBBY",
            self.button_font
        )
        self.leave_button.normal_color = (220, 100, 100)
        self.leave_button.hover_color = (240, 130, 130)

        # Single centered leave button when not host
        self.client_leave_button = Button(
            center_x - btn_width // 2,
            605,
            btn_width,
            btn_height,
            "LEAVE LOBBY",
            self.button_font
        )
        self.client_leave_button.normal_color = (220, 100, 100)
        self.client_leave_button.hover_color = (240, 130, 130)

    def handle_event(self, event, is_host):
        if is_host:
            if self.start_button.is_clicked(event):
                return "start"
            if self.leave_button.is_clicked(event):
                return "leave"
        else:
            if self.client_leave_button.is_clicked(event):
                return "leave"

        return None

    def draw(self, screen, room_code, players, map_name, is_host):
        screen.fill((130, 130, 130))
        center_x = self.screen_width // 2

        # ---------------- Title & Room Code Panel ----------------
        header_panel = pygame.Rect(100, 15, self.screen_width - 200, 155)
        pygame.draw.rect(screen, (195, 195, 195), header_panel)
        pygame.draw.rect(screen, (160, 160, 160), header_panel, 2)

        # Room Code
        display_code = room_code if room_code else "----"
        code_surf = self.code_font.render(f"ROOM CODE: {display_code}", True, (20, 20, 25))
        code_rect = code_surf.get_rect(center=(center_x, 60))
        screen.blit(code_surf, code_rect)

        sub_label = self.label_font.render(
            "Share this 4-letter code with your friends to join (Max 4 Players)",
            True,
            (60, 60, 65)
        )
        sub_rect = sub_label.get_rect(center=(center_x, 105))
        screen.blit(sub_label, sub_rect)

        map_info_surf = self.label_font.render(f"Selected Arena: {map_name.upper()}", True, (40, 110, 200))
        map_info_rect = map_info_surf.get_rect(center=(center_x, 140))
        screen.blit(map_info_surf, map_info_rect)

        # ---------------- 4 Player Slots ----------------
        slot_width = 380
        slot_height = 80
        slot_gap = 15
        slots_start_y = 190

        # Build map of occupied slots
        slot_to_player = {}
        for p in players:
            slot_to_player[p.get("slot", 0)] = p

        for i in range(4):
            slot_x = center_x - slot_width // 2
            slot_y = slots_start_y + i * (slot_height + slot_gap)
            slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)

            color = SLOT_COLORS[i % len(SLOT_COLORS)]
            player = slot_to_player.get(i)

            if player:
                # Occupied Slot
                pygame.draw.rect(screen, (220, 220, 220), slot_rect)
                pygame.draw.rect(screen, color, slot_rect, 3)

                # Colored avatar circle
                circle_center = (slot_x + 35, slot_y + slot_height // 2)
                pygame.draw.circle(screen, color, circle_center, 18)

                # Player Name
                name_text = player.get("name", "Player")
                name_surf = self.slot_font.render(name_text, True, (25, 25, 30))
                screen.blit(name_surf, (slot_x + 70, slot_y + 18))

                # Role Badge (Host / Player)
                is_player_host = player.get("is_host", False)
                badge_text = "HOST" if is_player_host else f"PLAYER {i + 1}"
                badge_color = (220, 160, 40) if is_player_host else (80, 140, 220)
                badge_surf = self.badge_font.render(badge_text, True, badge_color)
                screen.blit(badge_surf, (slot_x + 72, slot_y + 48))

                # Ready indicator
                ready_surf = self.badge_font.render("CONNECTED", True, (60, 160, 80))
                screen.blit(ready_surf, (slot_rect.right - 110, slot_y + slot_height // 2 - 8))
            else:
                # Empty Slot
                pygame.draw.rect(screen, (170, 170, 170), slot_rect)
                pygame.draw.rect(screen, (150, 150, 150), slot_rect, 2)

                empty_surf = self.slot_font.render(f"Slot {i + 1}: Waiting for player...", True, (90, 90, 95))
                empty_rect = empty_surf.get_rect(center=slot_rect.center)
                screen.blit(empty_surf, empty_rect)

        # ---------------- Action Buttons ----------------
        if is_host:
            self.start_button.draw(screen)
            self.leave_button.draw(screen)
        else:
            waiting_surf = self.label_font.render("Waiting for the host to start the match...", True, (240, 240, 240))
            waiting_rect = waiting_surf.get_rect(center=(center_x, 575))
            screen.blit(waiting_surf, waiting_rect)
            self.client_leave_button.draw(screen)
