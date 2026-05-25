# python-blinds package

Python service for the blinds controller.

This package contains the Raspberry Pi motor control code, WebSocket server,
HTTP server, and Adafruit MQTT integration used by the project.

Development commands from the repository root:

```bash
uv build --project blinds
uv run --project blinds ruff check blinds
uv run --project blinds mypy --config-file blinds/pyproject.toml blinds
```