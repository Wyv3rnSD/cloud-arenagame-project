# Arena 3 - a scattered open field, more sightlines than the others,
# good for shotgun play at range instead of tight corners.

MAP_DATA = {
    "name": "Arena 3",

    "walls": [
        (500, 500, 150, 150),
        (2350, 500, 150, 150),
        (500, 1350, 150, 150),
        (2350, 1350, 150, 150),

        (1425, 950, 150, 150),

        (900, 300, 300, 50),
        (1800, 300, 300, 50),
        (900, 1650, 300, 50),
        (1800, 1650, 300, 50),

        (150, 950, 50, 300),
        (2800, 950, 50, 300),
    ],

    "spawns": [
        (150, 150),
        (2850, 150),
        (150, 1850),
        (2850, 1850),
        (1500, 150),
        (1500, 1850),
    ],

    # Open sightline spots, clear of the pillars and corner boxes.
    "crate_spawns": [
        (1500, 500),
        (1500, 1500),
        (900, 950),
        (2100, 950),
        (1500, 700),
    ],
}
