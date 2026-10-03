# Arena 2 - a symmetric cross of cover through the middle,
# with four boxed-in corner rooms (open on the inward side).

MAP_DATA = {
    "name": "Arena 2",

    "walls": [
        # Central cross
        (1400, 200, 200, 1600),
        (200, 900, 2600, 200),

        # Top-left corner room
        (350, 350, 500, 50),
        (350, 350, 50, 400),

        # Top-right corner room
        (2150, 350, 500, 50),
        (2600, 350, 50, 400),

        # Bottom-left corner room
        (350, 1600, 500, 50),
        (350, 1250, 50, 400),

        # Bottom-right corner room
        (2150, 1600, 500, 50),
        (2600, 1250, 50, 400),
    ],

    "spawns": [
        (150, 150),
        (2850, 150),
        (150, 1850),
        (2850, 1850),
    ],

    # Inside each corner room, clear of the cross and outer walls.
    "crate_spawns": [
        (600, 550),
        (2400, 550),
        (600, 1450),
        (2400, 1450),
    ],
}
