# python-blinds

A simple Python script to control a set of 2 blinds using Raspberry Pi and stepper motors.

## Features
- Control the blinds using a web interface via WebSockets
- MQTT integration with ADAFRUIT.IO to allow voice control via Google Home (to be replaced with native Home Assistant voice control)
- HTTP endpoints for Home Assistant physical button integration

## Requirements
- Raspberry Pi (tested on Raspberry Pi Zero 2W)
- Stepper motors (tested on 28BYJ-48 + ULN2003 drivers)
- Motors powered at 12V
- need to add two files `pass` and `adaconfig` in blinds directory

### adaconfig file:
Contains the configuration for the adafruit.io MQTT server.
```
io.adafruit.com
<your_username>
<your_token>
<your_feed_name>
```

### pass file:
Contains sha256 hash of the password to be used to access settings in the web interface.
```
19e955dc99d019d6eee950c5538c1c48c7e7316453831c9e7a02be2b6c1edd07
```

## Installation
- to install python dependencies run `pip install -r requirements.txt` in the `blinds` directory
- to install UI dependencies run `npm install` in the `ui` directory (requires Node 14–16; vue-cli-service v4 breaks on Node 17+)
- to build the UI run `npm run build` in the `ui` directory
- to install web server dependencies run `npm install` in the `webserver` directory
- to build the webserver run `npm run build` in the `webserver` directory
- to upload everything to the device via SSH create file `ssh-credentials` in the root directory:
```bash
export USER=<your_username>
export DESTINATION=<ssh_destination>
```
- and run `./deploy.sh` in the root directory

## Home Assistant integration

Add to your HA `configuration.yaml`:
```yaml
rest_command:
  blinds_open:
    url: http://192.168.0.21:8083/open
  blinds_close:
    url: http://192.168.0.21:8083/close
```

Both endpoints implement toggle logic: if blinds are moving → stop; otherwise open/close.

## Services

Two systemd services run on the Pi:
- `python-blinds.service` — Python motor control + WebSocket server (port 8082) + HTTP server (port 8083)
- `python-blinds-webserver.service` — Node.js web UI server (port 3000)

```bash
sudo systemctl status python-blinds.service
sudo systemctl restart python-blinds.service
sudo journalctl -u python-blinds.service -f
```