import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from blinds.motors_manager import MotorsManager

logger = logging.getLogger(__name__)


class HttpServer:
    """HTTP server exposing /open and /close for Home Assistant.

    Toggle logic (identical for both endpoints):
      - Motors moving  → stop all
      - Motors stopped → open (target 0) or close (target limit)
    """

    def __init__(self, motors_manager: MotorsManager, port: int = 8083) -> None:
        self.motors_manager = motors_manager
        self.port = port
        self._server: HTTPServer | None = None

    def _make_handler(self):
        mm = self.motors_manager

        class _Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                logger.debug("HTTP %s", format % args)

            def _send(self, status: int, body: str) -> None:
                encoded = body.encode()
                self.send_response(status)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

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

            def do_GET(self):
                if self.path not in ("/open", "/close"):
                    self._send(404, "not found")
                    return

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

        return _Handler

    def start_server(self) -> None:
        self._server = HTTPServer(("", self.port), self._make_handler())
        logger.info("HTTP server listening on port %d", self.port)
        self._server.serve_forever()

    def stop_server(self) -> None:
        if self._server:
            self._server.shutdown()
            logger.info("HTTP server stopped")
