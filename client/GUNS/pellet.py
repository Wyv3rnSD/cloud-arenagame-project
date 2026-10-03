import pygame


class Pellet:

    def __init__(
        self,
        position,
        direction,
        velocity,
        damage,
        effect=None,
        owner_id=None
    ):

        self.position = pygame.Vector2(
            position
        )

        self.direction = pygame.Vector2(
            direction
        )

        self.velocity = velocity
        self.damage = damage

        # Optional special effect applied to whatever this
        # pellet hits, e.g. "freeze". None = a normal pellet.
        self.effect = effect
        self.owner_id = owner_id

        self.radius = 4
        self.active = True


    # Update
    def update(
        self,
        walls
    ):

        self.position += (
            self.direction
            * self.velocity
        )


        # Wall Collision
        for wall in walls:

            if wall.rect.collidepoint(
                self.position.x,
                self.position.y
            ):

                self.active = False
                break


    # Draw
    def draw(
        self,
        screen,
        camera
    ):

        if not self.active:
            return

        screen_position = camera.apply(
            self.position
        )

        if self.effect == "freeze":

            color = (150, 220, 255)


        else:

            color = (255, 220, 100)


        pygame.draw.circle(
            screen,
            color,
            (
                int(screen_position.x),
                int(screen_position.y)
            ),
            self.radius
        )