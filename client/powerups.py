import random


# Powerup Types
# Each entry: key -> (weight, display_name, color)
# Weights don't need to add to any particular total - random.choices
# normalizes them. Split as: 60% good crates (evenly among 5 types,
# 12% each), 40% unlucky crates (evenly among 2 types, 20% each) -
# i.e. a 2/5 chance of drawing an unlucky crate overall.
POWERUP_TYPES = {
    "ammo": (
        12,
        "AMMO",
        (255, 220, 100)
    ),

    "shield": (
        12,
        "SHIELD",
        (60, 140, 255)
    ),

    "health": (
        12,
        "HEALTH",
        (60, 200, 80)
    ),

    "speed": (
        12,
        "SPEED BOOST",
        (255, 200, 60)
    ),

    "freeze_ammo": (
        12,
        "FREEZE ROUNDS",
        (150, 220, 255)
    ),

    "unlucky_slow": (
        20,
        "??? (SLOWED)",
        (140, 140, 140)
    ),

    "unlucky_scramble": (
        20,
        "??? (SCRAMBLED)",
        (200, 80, 200)
    ),
}


# Roll a random powerup type, weighted per POWERUP_TYPES.
def roll_powerup_type():

    keys = list(POWERUP_TYPES.keys())

    weights = [
        POWERUP_TYPES[key][0]

        for key in keys
    ]

    return random.choices(
        keys,
        weights=weights,
        k=1
    )[0]


# Apply a powerup's effect to the player/shotgun that picked it up.
def apply_powerup(
    player,
    shotgun,
    powerup_type
):

    # Ammo Refill
    if powerup_type == "ammo":

        shotgun.reserve_ammo = min(
            shotgun.reserve_ammo + 20,
            80
        )


    # Shield Refill
    elif powerup_type == "shield":

        player.shield = min(
            player.shield + 30,
            player.max_shield
        )


    # Health Refill
    elif powerup_type == "health":

        player.health = min(
            player.health + 40,
            player.max_health
        )


    # Speed Boost
    elif powerup_type == "speed":

        player.apply_speed_effect(
            1.6,
            6000
        )


    # Freeze Rounds
    elif powerup_type == "freeze_ammo":

        shotgun.freeze_shots_remaining += 2


    # Unlucky - Slowed
    elif powerup_type == "unlucky_slow":

        player.apply_speed_effect(
            0.5,
            5000
        )


    # Unlucky - Scrambled Controls
    elif powerup_type == "unlucky_scramble":

        player.apply_scramble(
            4000
        )
