import pygame
import random

from GUNS.pellet import Pellet


class Shotgun:

    def __init__(self):

        # Shotgun Parameters
        self.pellet_velocity = 15
        self.pellet_quantity = 10
        self.pellet_spread = 30
        self.random_offset = 4
        self.recoil_velocity = 12
        self.pellet_damage = 8

        # Fire Rate
        self.shot_delay = 850
        self.last_shot_time = -self.shot_delay

        # Ammo
        self.ammo_capacity = 8
        self.ammo = 8
        self.reserve_ammo = 40

        # Reload
        self.full_reload_time = 3000

        self.shell_reload_time = (
            self.full_reload_time
            / self.ammo_capacity
        )

        self.reloading = False
        self.last_shell_time = 0

        # Freeze Ammo
        # When > 0, the next shot fires freeze pellets instead of
        # normal ones and this is decremented by one. Granted by
        # the freeze-bullets powerup crate.
        self.freeze_shots_remaining = 0


    # Shoot
    def shoot(
        self,
        player,
        camera,
        pellets
    ):

        current_time = pygame.time.get_ticks()

        # Can't Shoot While Reloading
        if self.reloading:
            return

        # Shot Delay
        if (
            current_time - self.last_shot_time
            < self.shot_delay
        ):
            return

        # Empty
        if self.ammo <= 0:

            self.start_reload()
            return

        aim_direction = (
            player.get_aim_direction(
                camera
            )
        )

        if aim_direction.length() == 0:
            return


        # Spread
        if self.pellet_quantity == 1:

            base_angles = [0]

        else:

            step = (
                self.pellet_spread
                / (self.pellet_quantity - 1)
            )

            base_angles = [
                -self.pellet_spread / 2
                + step * i

                for i in range(
                    self.pellet_quantity
                )
            ]


        # Freeze Ammo
        is_freeze_shot = (
            self.freeze_shots_remaining > 0
        )

        pellet_effect = (
            "freeze"
            if is_freeze_shot
            else None
        )


        # Pellets
        spawned_pellets = []
        owner = getattr(player, "player_id", None)

        for base_angle in base_angles:

            random_angle = random.uniform(
                -self.random_offset,
                self.random_offset
            )

            final_angle = (
                base_angle
                + random_angle
            )

            pellet_direction = (
                aim_direction.rotate(
                    final_angle
                )
            )

            pellet = Pellet(
                player.position.copy(),
                pellet_direction,
                self.pellet_velocity,
                self.pellet_damage,
                pellet_effect,
                owner_id=owner
            )

            pellets.append(
                pellet
            )
            spawned_pellets.append(
                pellet
            )


        # Use Freeze Shot
        if is_freeze_shot:

            self.freeze_shots_remaining -= 1


        # Recoil
        player.apply_recoil(
            aim_direction,
            self.recoil_velocity
        )


        # Use Shell
        self.ammo -= 1

        self.last_shot_time = (
            current_time
        )


        # Auto Reload
        if (
            self.ammo == 0
            and self.reserve_ammo > 0
        ):

            self.start_reload()

        return spawned_pellets


    # Start Reload
    def start_reload(self):

        if self.reloading:
            return

        if self.ammo >= self.ammo_capacity:
            return

        if self.reserve_ammo <= 0:
            return

        self.reloading = True

        self.last_shell_time = (
            pygame.time.get_ticks()
        )


    # Update
    def update(self):

        if not self.reloading:
            return

        current_time = pygame.time.get_ticks()

        if (
            current_time - self.last_shell_time
            >= self.shell_reload_time
        ):

            self.ammo += 1
            self.reserve_ammo -= 1

            self.last_shell_time = (
                current_time
            )


            # Stop Reloading
            if (
                self.ammo >= self.ammo_capacity
                or self.reserve_ammo <= 0
            ):

                self.reloading = False