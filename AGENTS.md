# Python Blinds — Project Overview

## Hardware

- **Raspberry Pi Zero 2W** — controller, hostname `pizero2`, user `mazelpico`
- **2× stepper motor 28BYJ-48** with ULN2003 driver boards
  - Motor 0: balcony door blind (direction inverted in software)
  - Motor 1: window blind next to the balcony door
- Motors powered at **12V** (5V was insufficient torque)
- GPIO pin assignments defined in `blinds/__main__.py`:
  - Motor 0: pins 5, 6, 13, 19
  - Motor 1: pins 23, 24, 25, 8

## Software Architecture

```
blinds/          Python package — motor control + WebSocket + HTTP server
ui/              Vue.js — web UI for manual control and calibration
```

### `blinds/` (Python)

Runs as a systemd service from `blinds/.venv/bin/python -m blinds`. The virtualenv is provisioned from the `uv` project in `blinds/`.

**Python workflow:**
- Use `uv` for all Python work in this repo.
- Treat `blinds/` as the only Python project.
- Prefer `cd blinds && uv sync` to install dependencies.
- Prefer `uv run --project blinds ...` for Python commands, scripts, formatting, and checks.
- Prefer `uv add ...` / `uv remove ...` when changing Python dependencies instead of editing lock state by hand.
- On the Pi, `deploy.sh` bootstraps `uv` if needed and refreshes `blinds/.venv`.

| File | Purpose |
|---|---|
| `__main__.py` | Entry point. Wires up motors, WebSocket server, HTTP server, Adafruit MQTT client. Broadcasts motor positions every second to all connected WebSocket clients. |
| `stepper_motor.py` | Low-level stepper motor driver. Tracks position, target, limit, step sequence. Enforces 0–limit bounds unless `ignore_limits` is set. |
| `motors_manager.py` | Manages both motors. Runs each motor in its own thread. Persists position/limit to `config_m0` / `config_m1` on every move completion. |
| `websocket_server.py` | asyncio WebSocket server on **port 8082**. Handles all control messages from UI clients. |
| `http_server.py` | Minimal HTTP server on **port 3000**. Serves the built UI from `ui/dist/` and exposes `/open` and `/close` for Home Assistant. Toggle logic lives here: if motors moving → stop all; otherwise open/close all. No new dependencies (stdlib `http.server`). |
| `adafruit_mqtt.py` | MQTT client connecting to Adafruit IO. Listens to a feed; reacts to `OPEN` / `CLOSE` string values (Google Assistant integration, to be replaced with Home Assistant voice). |

**WebSocket message protocol** (sent by UI clients):

| Message | Action |
|---|---|
| `up:<index>:<steps>` | Move motor up by steps |
| `down:<index>:<steps>` | Move motor down by steps |
| `stop:<index>` | Stop single motor at current position |
| `openBlind:<index>` | Open single blind (target → 0) |
| `closeBlind:<index>` | Close single blind (target → limit) |
| `OPEN` | Open all blinds |
| `CLOSE` | Close all blinds |
| `setTopPosition:<index>:<password>` | Set current position as 0 (top) |
| `setLimit:<index>:<password>` | Set current target as bottom limit |
| `setIgnoreLimits:<0|1>:<password>` | Bypass limit enforcement |

**Position broadcast** (sent to all clients every second):
```
blindsPosition:motor:<i>:position:<pos>:target:<target>:limit:<limit>:ignoreLimit:<0|1>
```

**Motor position persistence:**
- Saved to `config_m0` / `config_m1` (one position per line, one limit per line)
- Loaded on startup so blinds remember where they are after power loss

**Calibration** (must be done via web UI):
1. Manually move blind to fully open (top) position
2. "Set Top Position" → resets position counter to 0
3. Move to fully closed position
4. "Set Limit" → saves current step count as the bottom limit

Re-calibration is occasionally needed due to occasional step loss.

### `ui/` (Vue.js)

Web interface for manual control and calibration. Served by the Python HTTP server on port 3000 and connects directly to the WebSocket server on port 8082.

## Deployment

```bash
./deploy.sh
```

- SSH target: `mazelpico@pizero2` (credentials in `ssh-credentials`)
- Builds are expected to already be compiled (`ui/dist/`)
- Copies Python files, built UI assets, and the Python service file to the Pi
- Copies `blinds/pyproject.toml` and `blinds/uv.lock` to the Pi, bootstraps `uv` if missing, and runs `uv sync --project blinds --locked --no-dev`
- Installs the Python service to `/lib/systemd/system/`, reloads daemon, and restarts it

**Useful commands on the Pi:**
```bash
sudo systemctl status python-blinds.service
sudo systemctl restart python-blinds.service
sudo journalctl -u python-blinds.service -f
```

## Home Assistant Integration

**Current:** IKEA BILRESA 2-button switch wired via HA REST commands:
```yaml
rest_command:
  blinds_open:
    url: http://192.168.0.21:3000/open
  blinds_close:
    url: http://192.168.0.21:3000/close
```
Button up → `/open`, button down → `/close`. Press while moving → stops all motors.

The toggle logic runs inside the Python blinds service (`http_server.py`), which has direct access to motor state — no WebSocket round-trip or broadcast wait needed.

**Automations (example):**
```yaml
automation:
  - alias: Blinds up button
    trigger:
      - platform: device
        # ... BILRESA up button trigger
    action:
      - service: rest_command.blinds_open

  - alias: Blinds down button
    trigger:
      - platform: device
        # ... BILRESA down button trigger
    action:
      - service: rest_command.blinds_close
```

**Legacy (to be replaced):** Google Assistant via Adafruit IO MQTT feed — publishes `OPEN`/`CLOSE` to the feed, polled every second by the Pi.

**Planned:** Replace Adafruit/Google Assistant with native Home Assistant voice control.
