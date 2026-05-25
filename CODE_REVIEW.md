# Blinds Python Server Review

## Findings

### 1. Cleanup misses HTTP and MQTT shutdown paths

- Severity: High
- Files: `blinds/__main__.py`
- Details:
  - `main()` assigns `http_server` and `adafruit_mqtt_client` as locals instead of updating the module globals used by `cleanup()`.
  - `cleanup()` therefore skips `http_server.stop_server()` and `adafruit_mqtt_client.stop()`.
  - Because the MQTT thread is non-daemon and sits in a reconnect loop, shutdown or restart can hang instead of stopping cleanly.

### 2. Config writes are not atomic or synchronized

- Severity: High
- Files: `blinds/motors_manager.py`, `blinds/http_server.py`, `blinds/websocket_server.py`
- Details:
  - `save_config()` truncates and rewrites `config_m0` and `config_m1` directly.
  - That same method is called from motor worker threads, WebSocket handlers, and HTTP handlers.
  - There is no lock and no atomic replace, so overlapping writes or interruption during write can corrupt the config file.
  - `load_config()` assumes both lines are valid integers and will crash startup on partial or malformed files.

### 3. WebSocket command routing uses substring matching

- Severity: Medium
- Files: `blinds/websocket_server.py`
- Details:
  - Incoming messages are dispatched with checks like `if "up" in msg` instead of parsing the verb.
  - Command selection can therefore depend on the password or any other payload text.
  - Example: `setLimit:0:backup` contains `up` and can be misrouted to `go_up()`.

### 4. Bottom-limit calibration stores target instead of actual position

- Severity: Medium
- Files: `blinds/websocket_server.py`, `blinds/stepper_motor.py`, `ui/src/components/Window.vue`
- Details:
  - The UI presents `Set Limit` as storing the current bottom position.
  - The server currently persists `motor.get_target_position()` rather than the motor's actual position.
  - If the blind is still moving, misses steps, or stalls, the saved limit can be incorrect.

## Working Order

1. Fix cleanup shutdown wiring.
2. Make config persistence atomic and thread-safe.
3. Replace substring-based WebSocket dispatch with command parsing.
4. Fix calibration to use actual position.