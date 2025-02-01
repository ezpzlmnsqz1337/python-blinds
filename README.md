# python-blinds

A simple Python script to control a set of 2 blinds using Raspberry Pi and stepper motors.

## Features
- Control the blinds using a web interface via WebSockets
- MQTT integration with ADAFRUIT.IO to allow voice control via Google Home

## Requirements
- Raspberry Pi (tested on Raspberry Pi Zero 2)
- Stepper motors (tested on 28BYJ-48 + ULN2003 drivers)
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

# Installation
- to install python dependencies run `pip install -r requirements.txt` in the `blinds` directory
- to install UI dependencies run `npm install` in the `ui` directory (requires node 14)
- to build the UI run `npm run build` in the `ui` directory
- to install web server dependencies run `npm install` in the `webserver` directory (requires node 14)
- to build the webserver run `npm run build` in the `webserver` directory
- to upload everything to the device via SSH create file `ssh-credentials` in the root directory with the following content:
```bash
export USER=<your_username>
export DESTINATION=<ssh_destination>
```
- and run `./upload.sh` in the root directory