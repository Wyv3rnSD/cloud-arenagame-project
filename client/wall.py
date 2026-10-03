import pygame


class Wall:

    def __init__(
        self,
        x,
        y,
        width,
        height
    ):

        self.rect = pygame.Rect(
            x,
            y,
            width,
            height
        )


    # Draw
    def draw(
        self,
        screen,
        camera
    ):

        screen_rect = pygame.Rect(
            self.rect.x
            - camera.position.x,

            self.rect.y
            - camera.position.y,

            self.rect.width,
            self.rect.height
        )

        pygame.draw.rect(
            screen,
            (100, 100, 110),
            screen_rect
        )