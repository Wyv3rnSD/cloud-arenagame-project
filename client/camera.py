import pygame


class Camera:

    def __init__(
        self,
        screen_width,
        screen_height,
        world_width,
        world_height
    ):

        self.position = pygame.Vector2(
            0,
            0
        )

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.world_width = world_width
        self.world_height = world_height


    # Follow Player
    def update(
        self,
        target
    ):

        self.position.x = (
            target.position.x
            - self.screen_width / 2
        )

        self.position.y = (
            target.position.y
            - self.screen_height / 2
        )


        # Camera Boundaries
        self.position.x = max(
            0,
            min(
                self.position.x,
                self.world_width
                - self.screen_width
            )
        )

        self.position.y = max(
            0,
            min(
                self.position.y,
                self.world_height
                - self.screen_height
            )
        )


    # World to Screen
    def apply(
        self,
        world_position
    ):

        return (
            world_position
            - self.position
        )