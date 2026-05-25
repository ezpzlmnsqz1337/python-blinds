#!/usr/bin/env python3

# Example of using the MQTT client class to subscribe to a feed and print out
# any changes made to the feed.  Edit the variables below to configure the key,
# username, and feed to subscribe to for changes.

# Import standard python modules.
import logging
import ssl
import time
from io import TextIOWrapper
from pathlib import Path
from typing import Any

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

from blinds.websocket_server import WebSocketServer

logger = logging.getLogger(__name__)


class AdafruitIOMqttClient:
    def __init__(self, websocket_server: WebSocketServer) -> None:
        self.websocket_server = websocket_server
        self.stop_requested = False
        self.client = None
        self.reconnect_delay = 5  # seconds
        self.max_reconnect_delay = 300  # 5 minutes

        with open(Path(__file__).parent / "adaconfig", "r") as f:
            self.adafruit_io_url = self.readLineFromFileAsBytes(f)
            self.adafruit_io_username = self.readLineFromFileAsBytes(f)
            self.adafruit_io_key = self.readLineFromFileAsBytes(f)
            self.adafruit_io_feedname = self.readLineFromFileAsBytes(f)

    def readLineFromFileAsBytes(self, file: TextIOWrapper):
        return file.readline().rstrip("\n").rstrip("\r")

    def connected(self, client: mqtt.Client, userdata: Any, flags_dict: Any, result: int) -> None:
        if result == 0:
            logger.info(
                "Connected to Adafruit IO!  Listening for %s changes...",
                self.adafruit_io_feedname,
            )
            self.reconnect_delay = 5
            client.subscribe(
                "{0}/feeds/{1}".format(
                    self.adafruit_io_username, self.adafruit_io_feedname
                ),
                0,
            )
        else:
            logger.error("Failed to connect to Adafruit IO, result code: %d", result)

    def subscribed(self, client: mqtt.Client, userdata: Any, mid: int, granted_qos: Any) -> None:
        logger.info(
            "Subscribed to %s with QoS %d",
            self.adafruit_io_feedname,
            granted_qos[0],
        )

    def disconnected(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        if rc != 0:
            logger.warning(
                "Unexpectedly disconnected from Adafruit IO! Return code: %d. "
                "Will attempt to reconnect...",
                rc,
            )
        else:
            logger.info("Disconnected from Adafruit IO (clean disconnect)")

    def message(self, client: mqtt.Client, userdata: Any, message: MQTTMessage) -> None:
        try:
            msg = message.payload.decode("utf-8")
            logger.info(
                "Feed %s received new value: %s",
                message.topic,
                msg,
            )
            if msg == "OPEN":
                self.websocket_server.open_blinds()
            elif msg == "CLOSE":
                self.websocket_server.close_blinds()
        except Exception as e:
            logger.error("Error processing message: %s", e, exc_info=True)

    def run(self):
        logger.info("Started Adafruit IO MQTT client: %s", self.adafruit_io_url)
        self.client = mqtt.Client()
        ssl_context = ssl.create_default_context()
        self.client.tls_set_context(ssl_context)  # type: ignore
        self.client.username_pw_set(self.adafruit_io_username, self.adafruit_io_key)

        self.client.on_connect = self.connected
        self.client.on_disconnect = self.disconnected
        self.client.on_message = self.message
        self.client.on_subscribe = self.subscribed

        # Enable automatic reconnection
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)

        while not self.stop_requested:
            try:
                logger.info("Connecting to Adafruit IO: %s", self.adafruit_io_url)
                self.client.connect(self.adafruit_io_url, 8883, 60)
                self.client.loop_forever()  # Blocks and handles reconnection automatically

                # If we get here, connection was lost and loop_forever returned
                if not self.stop_requested:
                    logger.warning(
                        "Connection lost. Reconnecting in %s seconds...",
                        self.reconnect_delay,
                    )
                    time.sleep(self.reconnect_delay)
                    # Exponential backoff
                    self.reconnect_delay = min(
                        self.reconnect_delay * 2,
                        self.max_reconnect_delay,
                    )
            except Exception as e:
                if not self.stop_requested:
                    logger.error(
                        "Error connecting to Adafruit IO: %s. Retrying in %s seconds...",
                        e,
                        self.reconnect_delay,
                        exc_info=True,
                    )
                    time.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(
                        self.reconnect_delay * 2,
                        self.max_reconnect_delay,
                    )

        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

    def stop(self):
        logger.info("Stopping Adafruit MQTT client...")
        self.stop_requested = True
        if self.client:
            self.client.disconnect()
