import logging
import mimetypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Protocol, Sequence, cast
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class MotorLike(Protocol):
    def get_position(self) -> int: ...

    def get_target_position(self) -> int: ...

    def set_target_position(self, target: int) -> None: ...

    def disable(self) -> None: ...

    def get_limit(self) -> int: ...


class MotorsManagerLike(Protocol):
    def get_motors(self) -> Sequence[MotorLike]: ...

    def save_config(self, motor: object) -> None: ...


class HttpServer:
    """HTTP server exposing the built UI plus /open and /close for Home Assistant.

    Toggle logic (identical for both endpoints):
      - Motors moving  → stop all
      - Motors stopped → open (target 0) or close (target limit)
    """

    def __init__(
        self,
        motors_manager: object,
        port: int = 3000,
        ui_root: Path | None = None,
    ) -> None:
        self.motors_manager = motors_manager
        self.port = port
        self._server: HTTPServer | None = None
        self.ui_root = ui_root or (Path(__file__).resolve().parents[1] / "ui" / "dist")

    def _make_handler(self):
        mm = cast(MotorsManagerLike, self.motors_manager)
        ui_root = self.ui_root.resolve()

        class _Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                logger.debug("HTTP %s", format % args)

            def _send(self, status: int, body: str) -> None:
                self._send_bytes(status, body.encode(), "text/plain")

            def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _is_moving(self) -> bool:
                return any(
                    m.get_position() != m.get_target_position()
                    for m in mm.get_motors()
                )

            def _stop_all(self) -> None:
                for m in mm.get_motors():
                    m.set_target_position(m.get_position())
                    m.disable()
                    mm.save_config(m)

            def _serve_ui(self) -> None:
                requested_path = unquote(self.path.split("?", 1)[0])
                relative_path = requested_path.lstrip("/")
                candidate = (ui_root / relative_path).resolve()

                if not str(candidate).startswith(str(ui_root)):
                    self._send(404, "not found")
                    return

                if candidate.is_dir():
                    candidate = candidate / "index.html"

                if not candidate.exists() and "." not in Path(relative_path).name:
                    candidate = ui_root / "index.html"

                if not candidate.exists() or not candidate.is_file():
                    if not ui_root.exists():
                        self._send(503, "ui not built")
                    else:
                        self._send(404, "not found")
                    return

                content_type, _ = mimetypes.guess_type(candidate.name)
                self._send_bytes(
                    200,
                    candidate.read_bytes(),
                    content_type or "application/octet-stream",
                )

            def do_GET(self):
                if self.path in ("/open", "/close"):
                    if self._is_moving():
                        logger.info("HTTP %s: motors moving -> stopping", self.path)
                        self._stop_all()
                        self._send(200, "stopped")
                    elif self.path == "/open":
                        logger.info("HTTP /open: opening blinds")
                        for m in mm.get_motors():
                            m.set_target_position(0)
                            mm.save_config(m)
                        self._send(200, "opening")
                    else:
                        logger.info("HTTP /close: closing blinds")
                        for m in mm.get_motors():
                            m.set_target_position(m.get_limit())
                            mm.save_config(m)
                        self._send(200, "closing")
                else:
                    self._serve_ui()

        return _Handler

    def start_server(self) -> None:
        self._server = HTTPServer(("", self.port), self._make_handler())
        logger.info("HTTP server listening on port %d", self.port)
        self._server.serve_forever()

    def stop_server(self) -> None:
        if self._server:
            self._server.shutdown()
            logger.info("HTTP server stopped")
