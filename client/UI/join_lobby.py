import pygame
from UI.button import Button
from UI.text_input import TextInput


class JoinLobbyScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.title_font = pygame.font.Font(None, 75)
        self.label_font = pygame.font.Font(None, 34)
        self.input_font = pygame.font.Font(None, 40)
        self.code_font = pygame.font.Font(None, 52)
        self.button_font = pygame.font.Font(None, 45)
        self.status_font = pygame.font.Font(None, 28)

        self.status_message = ""
        self.status_color = (220, 60, 60)

        center_x = screen_width // 2

        # Name Input
        self.name_input = TextInput(
            center_x - 180,
            230,
            360,
            50,
            self.input_font,
            placeholder="Enter nickname...",
            initial_text="Player 2",
            max_length=12
        )

        # Room Code Input (4 uppercase characters, prominent)
        self.code_input = TextInput(
            center_x - 180,
            345,
            360,
            58,
            self.code_font,
            placeholder="CODE",
            initial_text="",
            max_length=5,
            uppercase=True
        )

        # Action Buttons
        action_btn_width = 340
        action_btn_height = 70
        self.join_button = Button(
            center_x - action_btn_width // 2,
            460,
            action_btn_width,
            action_btn_height,
            "JOIN LOBBY",
            self.button_font
        )
        self.join_button.normal_color = (100, 160, 240)
        self.join_button.hover_color = (130, 185, 255)

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
        code_result = self.code_input.handle_event(event)

        # If user hits Enter on code input, trigger join
        if code_result == "submit" or self.join_button.is_clicked(event):
            name = self.name_input.text.strip()
            code = self.code_input.text.strip().upper()

            if not name:
                self.set_status("Please enter a nickname")
                return None
            if len(code) < 4:
                self.set_status("Please enter the full 4-letter room code")
                return None

            return ("join", code, name)

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

        title_surf = self.title_font.render("JOIN LOBBY", True, (20, 20, 20))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 85))
        screen.blit(title_surf, title_rect)

        center_x = self.screen_width // 2

        # Nickname Label
        name_label = self.label_font.render("YOUR NICKNAME:", True, (30, 30, 35))
        screen.blit(name_label, (center_x - 180, 195))
        self.name_input.draw(screen)

        # Code Label
        code_label = self.label_font.render("ROOM CODE (4 LETTERS):", True, (30, 30, 35))
        screen.blit(code_label, (center_x - 180, 310))
        self.code_input.draw(screen)

        # Status Message
        if self.status_message:
            status_surf = self.status_font.render(self.status_message, True, self.status_color)
            status_rect = status_surf.get_rect(center=(center_x, 430))
            screen.blit(status_surf, status_rect)

        self.join_button.draw(screen)
        self.back_button.draw(screen)
