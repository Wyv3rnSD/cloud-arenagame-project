import argparse
import ctypes
import logging
import os
from pathlib import Path
import runpy
import socket
import sys
import threading
import time


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765
LOCAL_SERVER_URL = f"ws://{SERVER_HOST}:{SERVER_PORT}"


def bundled_root():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def server_script():
    return bundled_root() / "server" / "server.py"


def show_error(message):
    if os.name == "nt":
        ctypes.windll.user32.MessageBoxW(None, message, "Cloud Arena", 0x10)
    elif sys.stderr:
        print(message, file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(description="Launch Cloud Arena.")
    server_options = parser.add_mutually_exclusive_group()
    server_options.add_argument(
        "--server-url",
        help="Connect to a WebSocket server other than the configured default.",
    )
    server_options.add_argument(
        "--local-server",
        action="store_true",
        help="Start the bundled multiplayer server on this computer.",
    )
    return parser.parse_args()


def start_local_server(log_file):
    handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    def serve():
        os.environ["PORT"] = str(SERVER_PORT)
        try:
            runpy.run_path(str(server_script()), run_name="__main__")
        except Exception:
            root_logger.exception("Local multiplayer server stopped unexpectedly")

    server_thread = threading.Thread(
        target=serve,
        name="CloudArenaServer",
        daemon=True,
    )
    server_thread.start()

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if not server_thread.is_alive():
            break
        try:
            with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=0.25):
                return server_thread
        except OSError:
            time.sleep(0.1)

    log_tail = ""
    if log_file.exists():
        log_tail = log_file.read_text(encoding="utf-8", errors="replace")[-3000:]
    raise RuntimeError(
        f"The local multiplayer server could not start on port {SERVER_PORT}.\n\n"
        f"Server log: {log_file}\n\n{log_tail or 'No server output was recorded.'}"
    )


def run_game():
    client_dir = bundled_root() / "client"
    sys.path.insert(0, str(client_dir))
    import main


def main():
    args = parse_args()
    if args.local_server:
        os.environ["CLOUD_ARENA_SERVER_URL"] = LOCAL_SERVER_URL
        local_app_data = Path(
            os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
        )
        log_file = local_app_data / "CloudArena" / "server.log"
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            start_local_server(log_file)
        except (OSError, RuntimeError) as error:
            show_error(str(error))
            return 1
    elif args.server_url:
        os.environ["CLOUD_ARENA_SERVER_URL"] = args.server_url

    run_game()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
