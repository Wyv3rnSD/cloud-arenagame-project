import math

import pygame


# Mystery box styling - deliberately the same for every crate,
# regardless of what's actually inside. The real type/label/color
# only get looked up (from powerups.POWERUP_TYPES) once the crate
# is picked up, in main.py's pickup-notice logic.
MYSTERY_COLOR = (90, 60, 130)
MYSTERY_LABEL = "?"


class Crate:

    def __init__(
        self,
        x,
        y,
        crate_type
    ):

        self.x = x
        self.y = y

        # What's actually inside - kept secret from the player
        # until pickup. Not used anywhere in this class's drawing.
        self.crate_type = crate_type

        self.size = 34

        self.rect = pygame.Rect(
            0,
            0,
            self.size,
            self.size
        )

        self.rect.center = (x, y)


    # Draw
    # A slow up/down bob, purely visual - driven off the game
    # clock so it needs no per-frame update() call of its own.
    def draw(
        self,
        screen,
        camera,
        font
    ):

        bob = math.sin(
            pygame.time.get_ticks()
            / 300
        ) * 5

        screen_center = camera.apply(
            pygame.Vector2(
                self.rect.centerx,
                self.rect.centery + bob
            )
        )

        crate_rect = pygame.Rect(
            0,
            0,
            self.size,
            self.size
        )

        crate_rect.center = (
            screen_center.x,
            screen_center.y
        )

        # Box (always the same mystery styling)
        pygame.draw.rect(
            screen,
            MYSTERY_COLOR,
            crate_rect,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (20, 20, 20),
            crate_rect,
            width=3,
            border_radius=6
        )

        # "?" Label
        label_surface = font.render(
            MYSTERY_LABEL,
            True,
            (230, 230, 230)
        )

        label_rect = (
            label_surface.get_rect(
                center=crate_rect.center
            )
        )

        screen.blit(
            label_surface,
            label_rect
        )
