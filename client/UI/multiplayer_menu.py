import pygame
from UI.button import Button


class MultiplayerMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.title_font = pygame.font.Font(None, 80)
        self.button_font = pygame.font.Font(None, 50)

        button_width = 380
        button_height = 80
        button_x = screen_width // 2 - button_width // 2
        button_gap = 25
        first_button_y = 260

        self.create_button = Button(
            button_x,
            first_button_y,
            button_width,
            button_height,
            "CREATE LOBBY",
            self.button_font
        )

        self.join_button = Button(
            button_x,
            first_button_y + (button_height + button_gap),
            button_width,
            button_height,
            "JOIN LOBBY",
            self.button_font
        )

        self.back_button = Button(
            button_x,
            first_button_y + 2 * (button_height + button_gap) + 15,
            button_width,
            button_height,
            "BACK",
            self.button_font
        )

    def handle_event(self, event):
        if self.create_button.is_clicked(event):
            return "create"
        if self.join_button.is_clicked(event):
            return "join"
        if self.back_button.is_clicked(event):
            return "back"
        return None

    def draw(self, screen):
        screen.fill((130, 130, 130))

        # Title Panel
        title_panel = pygame.Rect(
            145,
            15,
            self.screen_width - 290,
            160
        )
        pygame.draw.rect(screen, (195, 195, 195), title_panel)

        title_surface = self.title_font.render(
            "MULTIPLAYER",
            True,
            (20, 20, 20)
        )
        title_rect = title_surface.get_rect(
            center=(self.screen_width // 2, 95)
        )
        screen.blit(title_surface, title_rect)

        self.create_button.draw(screen)
        self.join_button.draw(screen)
        self.back_button.draw(screen)
