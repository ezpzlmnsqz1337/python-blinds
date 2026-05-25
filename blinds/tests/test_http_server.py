import threading
import time
from pathlib import Path
from typing import Any, cast
from urllib.request import urlopen

from blinds.http_server import HttpServer


class FakeMotor:
    def __init__(self) -> None:
        self.position = 10
        self.target = 10
        self.limit = 40
        self.disabled = False

    def get_position(self) -> int:
        return self.position

    def get_target_position(self) -> int:
        return self.target

    def set_target_position(self, target: int) -> None:
        self.target = target

    def disable(self) -> None:
        self.disabled = True

    def get_limit(self) -> int:
        return self.limit


class FakeMotorsManager:
    def __init__(self) -> None:
        self.motor = FakeMotor()
        self.saved = 0

    def get_motors(self) -> list[FakeMotor]:
        return [self.motor]

    def save_config(self, motor: FakeMotor) -> None:
        self.saved += 1


def start_server(server: HttpServer) -> tuple[threading.Thread, int]:
    thread = threading.Thread(target=server.start_server, daemon=True)
    thread.start()

    for _ in range(100):
        if server._server is not None:
            return thread, server._server.server_port
        time.sleep(0.01)

    raise AssertionError("HTTP server did not start")


def test_http_server_serves_ui_and_history_fallback(tmp_path: Path) -> None:
    ui_root = tmp_path / "ui"
    ui_root.mkdir()
    (ui_root / "index.html").write_text("<html>rolety</html>", encoding="utf-8")
    (ui_root / "app.js").write_text("console.log('ok')", encoding="utf-8")

    server = HttpServer(cast(Any, FakeMotorsManager()), port=0, ui_root=ui_root)
    thread, port = start_server(server)

    try:
        root_response = urlopen(f"http://127.0.0.1:{port}/")
        root_body = root_response.read().decode()
        route_response = urlopen(f"http://127.0.0.1:{port}/settings")
        route_body = route_response.read().decode()
        asset_response = urlopen(f"http://127.0.0.1:{port}/app.js")
        asset_body = asset_response.read().decode()
    finally:
        server.stop_server()
        thread.join(timeout=2)

    assert root_body == "<html>rolety</html>"
    assert route_body == "<html>rolety</html>"
    assert asset_body == "console.log('ok')"


def test_http_server_open_endpoint_sets_targets() -> None:
    manager = FakeMotorsManager()
    server = HttpServer(cast(Any, manager), port=0)
    thread, port = start_server(server)

    try:
        response = urlopen(f"http://127.0.0.1:{port}/open")
        body = response.read().decode()
    finally:
        server.stop_server()
        thread.join(timeout=2)

    assert body == "opening"
    assert manager.motor.target == 0
    assert manager.saved == 1