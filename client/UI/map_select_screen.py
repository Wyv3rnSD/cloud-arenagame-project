import pygame

from UI.button import Button


class MapSelectScreen:

    def __init__(
        self,
        screen_width,
        screen_height,
        map_choices
    ):

        self.screen_width = (
            screen_width
        )

        self.screen_height = (
            screen_height
        )

        # map_choices: list of (key, display_name) tuples
        self.map_choices = map_choices


        # Fonts
        self.title_font = (
            pygame.font.Font(
                None,
                80
            )
        )

        self.button_font = (
            pygame.font.Font(
                None,
                50
            )
        )


        # Map Buttons
        button_width = 330
        button_height = 90
        button_gap = 25

        button_x = (
            screen_width // 2
            - button_width // 2
        )

        first_button_y = 250

        self.map_buttons = []

        for index, (key, display_name) in enumerate(
            self.map_choices
        ):

            button_y = (
                first_button_y
                + index
                * (button_height + button_gap)
            )

            button = Button(
                button_x,
                button_y,
                button_width,
                button_height,
                display_name,
                self.button_font
            )

            self.map_buttons.append(
                (key, button)
            )


        # Back Button
        last_button_y = (
            first_button_y
            + len(self.map_choices)
            * (button_height + button_gap)
            + 15
        )

        self.back_button = Button(
            button_x,
            last_button_y,
            button_width,
            button_height,
            "BACK",
            self.button_font
        )


    # Events
    def handle_event(self, event):

        for key, button in self.map_buttons:

            if button.is_clicked(event):

                return key


        if self.back_button.is_clicked(
            event
        ):

            return "back"


        return None


    # Draw
    def draw(self, screen):

        # Background
        screen.fill(
            (130, 130, 130)
        )


        # Title Panel
        title_panel = pygame.Rect(
            145,
            15,
            self.screen_width - 290,
            150
        )

        pygame.draw.rect(
            screen,
            (195, 195, 195),
            title_panel
        )


        # Title
        title_surface = (
            self.title_font.render(
                "SELECT MAP",
                True,
                (20, 20, 20)
            )
        )

        title_rect = (
            title_surface.get_rect(
                center=(
                    self.screen_width // 2,
                    90
                )
            )
        )

        screen.blit(
            title_surface,
            title_rect
        )


        # Map Buttons
        for key, button in self.map_buttons:

            button.draw(screen)


        # Back Button
        self.back_button.draw(screen)
