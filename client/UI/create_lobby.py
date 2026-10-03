import pygame
from UI.button import Button
from UI.text_input import TextInput


class CreateLobbyScreen:
    def __init__(self, screen_width, screen_height, map_choices):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_choices = map_choices  # list of (key, display_name)
        self.selected_map_key = map_choices[0][0] if map_choices else "arena1"

        self.title_font = pygame.font.Font(None, 75)
        self.label_font = pygame.font.Font(None, 34)
        self.input_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 45)
        self.status_font = pygame.font.Font(None, 28)

        self.status_message = ""
        self.status_color = (220, 50, 50)

        # Name Input
        center_x = screen_width // 2
        self.name_input = TextInput(
            center_x - 180,
            230,
            360,
            50,
            self.input_font,
            placeholder="Enter nickname...",
            initial_text="Player 1",
            max_length=12
        )

        # Map Buttons (Horizontal row)
        self.map_buttons = []
        map_btn_width = 160
        map_btn_height = 50
        gap = 15
        total_width = len(map_choices) * map_btn_width + (len(map_choices) - 1) * gap
        start_x = center_x - total_width // 2
        map_y = 350

        for i, (key, display_name) in enumerate(map_choices):
            btn = Button(
                start_x + i * (map_btn_width + gap),
                map_y,
                map_btn_width,
                map_btn_height,
                display_name,
                pygame.font.Font(None, 32)
            )
            self.map_buttons.append((key, btn))

        # Action Buttons
        action_btn_width = 340
        action_btn_height = 70
        self.create_button = Button(
            center_x - action_btn_width // 2,
            460,
            action_btn_width,
            action_btn_height,
            "CREATE LOBBY",
            self.button_font
        )
        self.create_button.normal_color = (120, 200, 130)
        self.create_button.hover_color = (150, 225, 160)

        self.back_button = Button(
            center_x - action_btn_width // 2,
            550,
            action_btn_width,
            action_btn_height,
            "BACK",
            self.button_font
        )

    def set_status(self, message, is_error=True):
        self.status_message = message
        self.status_color = (220, 60, 60) if is_error else (60, 180, 80)

    def handle_event(self, event):
        self.name_input.handle_event(event)

        for key, btn in self.map_buttons:
            if btn.is_clicked(event):
                self.selected_map_key = key

        if self.create_button.is_clicked(event):
            name = self.name_input.text.strip()
            if not name:
                self.set_status("Please enter a nickname")
                return None
            return ("create", name, self.selected_map_key)

        if self.back_button.is_clicked(event):
            return ("back", None, None)

        return None

    def draw(self, screen):
        screen.fill((130, 130, 130))

        # Title Panel
        title_panel = pygame.Rect(
            145,
            15,
            self.screen_width - 290,
            140
        )
        pygame.draw.rect(screen, (195, 195, 195), title_panel)

        title_surf = self.title_font.render("CREATE LOBBY", True, (20, 20, 20))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 85))
        screen.blit(title_surf, title_rect)

        # Nickname Label
        center_x = self.screen_width // 2
        name_label = self.label_font.render("YOUR NICKNAME:", True, (30, 30, 35))
        screen.blit(name_label, (center_x - 180, 195))

        self.name_input.draw(screen)

        # Map Selection Label
        map_label = self.label_font.render("SELECT ARENA:", True, (30, 30, 35))
        screen.blit(map_label, (center_x - 180, 310))

        for key, btn in self.map_buttons:
            # Highlight selected map
            if key == self.selected_map_key:
                pygame.draw.rect(
                    screen,
                    (70, 140, 240),
                    btn.rect.inflate(6, 6),
                    3
                )
            btn.draw(screen)

        # Status Message
        if self.status_message:
            status_surf = self.status_font.render(self.status_message, True, self.status_color)
            status_rect = status_surf.get_rect(center=(center_x, 430))
            screen.blit(status_surf, status_rect)

        self.create_button.draw(screen)
        self.back_button.draw(screen)
