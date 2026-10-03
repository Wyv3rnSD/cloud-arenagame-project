from wall import Wall


class GameMap:

    def __init__(self, map_data):

        self.name = map_data.get(
            "name",
            "Unnamed Map"
        )

        # Spawn points, used for placing/respawning players.
        self.spawns = map_data.get(
            "spawns",
            [(0, 0)]
        )

        # Points where powerup crates are allowed to spawn.
        self.crate_spawns = map_data.get(
            "crate_spawns",
            []
        )

        # Walls
        self.walls = [
            Wall(*wall_rect)

            for wall_rect in map_data["walls"]
        ]


    # Draw
    def draw(
        self,
        screen,
        camera
    ):

        for wall in self.walls:

            wall.draw(
                screen,
                camera
            )
