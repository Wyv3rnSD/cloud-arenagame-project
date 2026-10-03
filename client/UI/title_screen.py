import pygame
from UI.button import Button


class TitleScreen:

    def __init__(
        self,
        screen_width,
        screen_height
    ):

        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.title_font = pygame.font.Font(None, 110)
        self.button_font = pygame.font.Font(None, 50)

        # Buttons
        button_width = 360
        button_height = 75

        button_x = (
            screen_width // 2
            - button_width // 2
        )

        self.multiplayer_button = Button(
            button_x,
            330,
            button_width,
            button_height,
            "MULTIPLAYER",
            self.button_font
        )
        self.multiplayer_button.normal_color = (100, 160, 240)
        self.multiplayer_button.hover_color = (130, 185, 255)

        self.solo_button = Button(
            button_x,
            425,
            button_width,
            button_height,
            "SOLO PRACTICE",
            self.button_font
        )

        self.quit_button = Button(
            button_x,
            520,
            button_width,
            button_height,
            "QUIT",
            self.button_font
        )

    # Events
    def handle_event(self, event):

        if self.multiplayer_button.is_clicked(event):
            return "multiplayer"

        if self.solo_button.is_clicked(event):
            return "map_select"

        if self.quit_button.is_clicked(event):
            return "quit"

        return None

    # Draw
    def draw(self, screen):

        # Background
        screen.fill((130, 130, 130))

        # Title Panel
        title_panel = pygame.Rect(
            145,
            15,
            self.screen_width - 290,
            240
        )

        pygame.draw.rect(
            screen,
            (195, 195, 195),
            title_panel
        )

        # Title
        title_surface = self.title_font.render(
            "Cloud Arena",
            True,
            (20, 20, 20)
        )

        title_rect = title_surface.get_rect(
            center=(
                self.screen_width // 2,
                135
            )
        )

        screen.blit(
            title_surface,
            title_rect
        )

        # Buttons
        self.multiplayer_button.draw(screen)
        self.solo_button.draw(screen)
        self.quit_button.draw(screen)