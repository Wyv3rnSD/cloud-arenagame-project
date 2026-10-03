from . import arena1, arena2, arena3


# Registry of all available maps.
# Add a new map by creating maps/<name>.py with a MAP_DATA dict,
# then import it above and register it here.
MAPS = {
    "arena1": arena1.MAP_DATA,
    "arena2": arena2.MAP_DATA,
    "arena3": arena3.MAP_DATA,
}


def load_map(name):
    if name not in MAPS:
        raise ValueError(f"Unknown map: {name}")

    return MAPS[name]


def map_names():
    return list(MAPS.keys())


def map_choices():
    # List of (key, display_name) pairs, e.g. ("arena1", "Arena 1"),
    # in registry order - handy for building a map-select menu.
    return [
        (key, data.get("name", key))

        for key, data in MAPS.items()
    ]
