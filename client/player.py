import pygame
import random


class Player:

    def __init__(self, x, y):

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)

        self.radius = 20

        # Movement
        # base_* values are the "normal" numbers; max_speed/acceleration
        # are recalculated from them each frame based on active status
        # effects (speed boost, slow, etc).
        self.base_acceleration = 0.45
        self.base_max_speed = 7

        self.acceleration = self.base_acceleration
        self.max_speed = self.base_max_speed

        self.friction = 0.985
        self.recoil_friction = 0.990

        self.max_recoil_speed = 20

        self.bounce = 0.85


        # Status Effects
        # Speed multiplier (< 1 slows, > 1 boosts).
        self.speed_multiplier = 1.0
        self.speed_effect_end_time = 0

        # Uncontrollable movement (unlucky crate).
        self.controls_scrambled = False
        self.controls_scrambled_end_time = 0

        # Frozen (near-total movement lock, from a freeze pellet hit).
        self.frozen_until = 0

        # Health
        self.max_health = 100
        self.health = 100

        # Shield
        self.max_shield = 50
        self.shield = 50

        self.shield_regen_delay = 7000
        self.shield_regen_rate = 10

        self.last_damage_time = 0

        self.player_id = None
        self.name = "Player"
        self.slot = 0

        # Hitbox
        self.rect = pygame.Rect(
            0,
            0,
            self.radius * 2,
            self.radius * 2
        )

        self.rect.center = self.position


    # Update
    def update(
        self,
        world_width,
        world_height,
        walls
    ):

        # Status Effects
        # Expires old effects and recalculates max_speed/acceleration.
        self.update_status_effects()

        movement = pygame.Vector2(0, 0)

        if self.is_frozen():

            # Frozen: no input accepted at all.
            # Existing velocity just bleeds off via friction below.
            pass


        elif self.controls_scrambled:

            # Unlucky crate: input is replaced with a random
            # direction each frame, so movement is uncontrollable.
            movement = pygame.Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            )


        else:

            keys = pygame.key.get_pressed()

            # Input
            if keys[pygame.K_w]:
                movement.y -= 1

            if keys[pygame.K_s]:
                movement.y += 1

            if keys[pygame.K_a]:
                movement.x -= 1

            if keys[pygame.K_d]:
                movement.x += 1


        # Acceleration
        if movement.length() > 0:

            movement = movement.normalize()

            movement_force = (
                movement * self.acceleration
            )

            current_speed = (
                self.velocity.length()
            )


            # Normal Movement
            if current_speed < self.max_speed:

                self.velocity += movement_force

                if (
                    self.velocity.length()
                    > self.max_speed
                ):

                    self.velocity.scale_to_length(
                        self.max_speed
                    )


            # High Speed Movement
            else:

                old_speed = (
                    self.velocity.length()
                )

                self.velocity += movement_force

                new_speed = (
                    self.velocity.length()
                )

                # WASD Can Change Direction
                # But Cannot Increase High Speed
                if new_speed > old_speed:

                    self.velocity.scale_to_length(
                        old_speed
                    )


        # X Movement
        self.position.x += self.velocity.x

        self.rect.centerx = round(
            self.position.x
        )

        self.handle_x_collisions(
            walls
        )


        # Y Movement
        self.position.y += self.velocity.y

        self.rect.centery = round(
            self.position.y
        )

        self.handle_y_collisions(
            walls
        )


        # World Boundaries

        # Left
        if self.position.x - self.radius < 0:

            self.position.x = self.radius

            self.rect.centerx = round(
                self.position.x
            )

            self.velocity.x *= -self.bounce


        # Right
        if self.position.x + self.radius > world_width:

            self.position.x = (
                world_width - self.radius
            )

            self.rect.centerx = round(
                self.position.x
            )

            self.velocity.x *= -self.bounce


        # Top
        if self.position.y - self.radius < 0:

            self.position.y = self.radius

            self.rect.centery = round(
                self.position.y
            )

            self.velocity.y *= -self.bounce


        # Bottom
        if self.position.y + self.radius > world_height:

            self.position.y = (
                world_height - self.radius
            )

            self.rect.centery = round(
                self.position.y
            )

            self.velocity.y *= -self.bounce


        # Friction
        if self.velocity.length() > self.max_speed:

            self.velocity *= (
                self.recoil_friction
            )

        else:

            self.velocity *= (
                self.friction
            )


        # Shield
        self.update_shield()


    # Damage
    def take_damage(self, damage):

        if damage <= 0:
            return

        self.last_damage_time = (
            pygame.time.get_ticks()
        )

        # Shield Damage
        if self.shield > 0:

            shield_damage = min(
                self.shield,
                damage
            )

            self.shield -= shield_damage
            damage -= shield_damage


        # Health Damage
        if damage > 0:

            self.health -= damage

            self.health = max(
                0,
                self.health
            )


    # Shield
    def update_shield(self):

        if self.shield >= self.max_shield:
            return

        current_time = (
            pygame.time.get_ticks()
        )

        if (
            current_time
            - self.last_damage_time
            < self.shield_regen_delay
        ):
            return

        regen_per_frame = (
            self.shield_regen_rate / 60
        )

        self.shield += regen_per_frame

        self.shield = min(
            self.shield,
            self.max_shield
        )


    # Status Effects
    def update_status_effects(self):

        current_time = pygame.time.get_ticks()

        # Speed Effect Expiry (boost or slow)
        if (
            self.speed_effect_end_time
            and current_time
            >= self.speed_effect_end_time
        ):

            self.speed_multiplier = 1.0
            self.speed_effect_end_time = 0


        # Scrambled Controls Expiry
        if (
            self.controls_scrambled
            and current_time
            >= self.controls_scrambled_end_time
        ):

            self.controls_scrambled = False


        # Recalculate Effective Movement Stats
        self.max_speed = (
            self.base_max_speed
            * self.speed_multiplier
        )

        self.acceleration = (
            self.base_acceleration
            * self.speed_multiplier
        )


    # Frozen?
    def is_frozen(self):

        return (
            pygame.time.get_ticks()
            < self.frozen_until
        )


    # Apply Freeze
    # (used by freeze pellets hitting a player)
    def apply_freeze(self, duration_ms):

        self.frozen_until = (
            pygame.time.get_ticks()
            + duration_ms
        )


    # Apply Speed Effect
    # multiplier > 1 boosts, < 1 slows. Overrides any
    # currently active speed effect.
    def apply_speed_effect(
        self,
        multiplier,
        duration_ms
    ):

        self.speed_multiplier = multiplier

        self.speed_effect_end_time = (
            pygame.time.get_ticks()
            + duration_ms
        )


    # Apply Scrambled Controls
    def apply_scramble(self, duration_ms):

        self.controls_scrambled = True

        self.controls_scrambled_end_time = (
            pygame.time.get_ticks()
            + duration_ms
        )


    # Apply Recoil
    def apply_recoil(
        self,
        direction,
        recoil_velocity
    ):

        self.velocity -= (
            direction
            * recoil_velocity
        )

        # Recoil Speed Limit
        if (
            self.velocity.length()
            > self.max_recoil_speed
        ):

            self.velocity.scale_to_length(
                self.max_recoil_speed
            )


    # X Collisions
    def handle_x_collisions(self, walls):

        for wall in walls:

            if self.rect.colliderect(
                wall.rect
            ):

                if self.velocity.x > 0:

                    self.rect.right = (
                        wall.rect.left
                    )

                    self.position.x = (
                        self.rect.centerx
                    )

                    self.velocity.x *= (
                        -self.bounce
                    )

                elif self.velocity.x < 0:

                    self.rect.left = (
                        wall.rect.right
                    )

                    self.position.x = (
                        self.rect.centerx
                    )

                    self.velocity.x *= (
                        -self.bounce
                    )


    # Y Collisions
    def handle_y_collisions(self, walls):

        for wall in walls:

            if self.rect.colliderect(
                wall.rect
            ):

                if self.velocity.y > 0:

                    self.rect.bottom = (
                        wall.rect.top
                    )

                    self.position.y = (
                        self.rect.centery
                    )

                    self.velocity.y *= (
                        -self.bounce
                    )

                elif self.velocity.y < 0:

                    self.rect.top = (
                        wall.rect.bottom
                    )

                    self.position.y = (
                        self.rect.centery
                    )

                    self.velocity.y *= (
                        -self.bounce
                    )


    # Aim
    def get_aim_direction(
        self,
        camera
    ):

        mouse_position = pygame.Vector2(
            pygame.mouse.get_pos()
        )

        player_screen_position = (
            camera.apply(
                self.position
            )
        )

        direction = (
            mouse_position
            - player_screen_position
        )

        if direction.length() > 0:

            direction = (
                direction.normalize()
            )

        return direction


    # Draw
    def draw(
        self,
        screen,
        camera
    ):

        screen_position = (
            camera.apply(
                self.position
            )
        )

        # Status-based Color
        if self.is_frozen():

            color = (150, 220, 255)


        elif self.controls_scrambled:

            color = (200, 80, 200)


        elif self.speed_multiplier > 1:

            color = (255, 200, 60)


        elif self.speed_multiplier < 1:

            color = (140, 140, 140)


        else:

            try:
                from config import SLOT_COLORS
                color = SLOT_COLORS[self.slot % len(SLOT_COLORS)]
            except Exception:
                color = (80, 170, 255)


        pygame.draw.circle(
            screen,
            color,
            (
                int(screen_position.x),
                int(screen_position.y)
            ),
            self.radius
        )

        pygame.draw.circle(
            screen,
            (30, 30, 35),
            (
                int(screen_position.x),
                int(screen_position.y)
            ),
            self.radius,
            2
        )