# Arena 1 - the original layout (staggered cover pieces).
# Wall tuples are (x, y, width, height) in world coordinates.

MAP_DATA = {
    "name": "Arena 1",

    "walls": [
        (300, 300, 400, 50),
        (900, 500, 50, 400),
        (1300, 300, 500, 50),
        (1800, 700, 50, 500),
        (600, 1200, 600, 50),
        (1500, 1400, 500, 50),
    ],

    # Corner spawns, kept clear of walls.
    "spawns": [
        (150, 150),
        (2850, 150),
        (150, 1850),
        (2850, 1850),
    ],

    # Open spots (clear of walls) where powerup crates can appear.
    "crate_spawns": [
        (1500, 1000),
        (750, 750),
        (2350, 900),
        (1000, 1700),
        (2400, 1650),
        (400, 1600),
    ],
}
