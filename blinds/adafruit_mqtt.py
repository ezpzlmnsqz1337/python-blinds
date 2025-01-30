#!/usr/bin/env python3

# Example of using the MQTT client class to subscribe to a feed and print out
# any changes made to the feed.  Edit the variables below to configure the key,
# username, and feed to subscribe to for changes.

# Import standard python modules.
import sys
import time
from io import TextIOWrapper
import paho.mqtt.client as mqtt
from pathlib import Path
from blinds.websocket_server import WebSocketServer

class AdafruitIOMqttClient:
    def __init__(self, websocket_server: WebSocketServer) -> None:
        self.websocket_server = websocket_server
        self.stop_requested = False

        with open(Path(__file__).parent / 'adaconfig', 'r') as f:
            self.adafruit_io_url = self.readLineFromFileAsBytes(f)
            self.adafruit_io_username = self.readLineFromFileAsBytes(f)
            self.adafruit_io_key = self.readLineFromFileAsBytes(f)
            self.adafruit_io_feedname = self.readLineFromFileAsBytes(f)

    def readLineFromFileAsBytes(self, file: TextIOWrapper):
        return file.readline().rstrip('\n').rstrip('\r')
    
    def connected(self, client: mqtt.Client, userdata, flags_dict, result):
        print('Connected to Adafruit IO!  Listening for {0} changes...'.format(self.adafruit_io_feedname))
        client.subscribe('{0}/feeds/{1}'.format(self.adafruit_io_username, self.adafruit_io_feedname), 0)

    def subscribed(self, client: mqtt.Client, userdata, mid, granted_qos):
        print('Subscribed to {0} with QoS {1}'.format(self.adafruit_io_feedname, granted_qos[0]))

    def disconnected(self, client: mqtt.Client, userdata, rc):
        print('Disconnected from Adafruit IO!')
        sys.exit(1)

    def message(self, client: mqtt.Client, userdata, message):
        print('Feed {0} received new value: {1}'.format(message.topic, message.payload.decode('utf-8')))
        msg = message.payload.decode('utf-8')
        if msg == 'OPEN':
            self.websocket_server.open_blinds()
        elif msg == 'CLOSE':
            self.websocket_server.close_blinds()

    def run(self):
        print(f"Started Adafruit IO: {self.adafruit_io_url}")
        client = mqtt.Client()
        client.tls_set_context()
        client.username_pw_set(self.adafruit_io_username, self.adafruit_io_key)

        client.on_connect    = self.connected
        client.on_disconnect = self.disconnected
        client.on_message    = self.message
        client.on_subscribe  = self.subscribed

        print(f"Connecting to Adafruit IO: {self.adafruit_io_url}")
        client.connect(self.adafruit_io_url, 8883, 60)
        
        client.loop_start()

        while not self.stop_requested:
            time.sleep(1)
            pass

        client.loop_stop()
    
    def stop(self):
        self.stop_requested = True