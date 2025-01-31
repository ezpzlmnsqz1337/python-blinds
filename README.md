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
