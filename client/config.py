import os

# Network and Game Configuration

# Local testing: "ws://127.0.0.1:8765"
# Cloud (Render): "wss://cloud-arena-server.onrender.com"
DEFAULT_SERVER_URL = os.environ.get(
    "CLOUD_ARENA_SERVER_URL",
    "wss://cloud-arena-server.onrender.com",
)

# Slot colors for players 0-3
SLOT_COLORS = [
    (70, 150, 255),   # Slot 0 (Host): Blue
    (255, 120, 60),   # Slot 1: Orange
    (70, 215, 110),   # Slot 2: Green
    (210, 90, 230),   # Slot 3: Purple
]
