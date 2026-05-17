import time
import logging
import sys
import threading
import RPi.GPIO as GPIO

from blinds.stepper_motor import StepperMotor
from blinds.motors_manager import MotorsManager
from blinds.websocket_server import WebSocketServer
from blinds.adafruit_mqtt import AdafruitIOMqttClient
from blinds.http_server import HttpServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# main classes
motors_manager: MotorsManager | None = None
websocket_server: WebSocketServer | None = None
adafruit_mqtt_client: AdafruitIOMqttClient | None = None
http_server: HttpServer | None = None

# threads
websocket_thread: threading.Thread | None = None
adafruit_mqtt_thread: threading.Thread | None = None
http_thread: threading.Thread | None = None

stop_requested = False


def main() -> None:
    global websocket_server
    global motors_manager
    global websocket_thread
    global adafruit_mqtt_thread
    
    logger.info("Starting Python Blinds Service...")
    GPIO.setmode(GPIO.BCM)

    # motors settings
    motors = [StepperMotor(5, 6, 13, 19, 0), StepperMotor(23, 24, 25, 8, 1)]
    motors_manager = MotorsManager(motors)
    websocket_server = WebSocketServer(motors_manager)
    http_server = HttpServer(motors_manager)
    adafruit_mqtt_client = AdafruitIOMqttClient(websocket_server)

    websocket_thread = threading.Thread(target=websocket_server.start_server)
    adafruit_mqtt_thread = threading.Thread(target=adafruit_mqtt_client.run)
    http_thread = threading.Thread(target=http_server.start_server, daemon=True)

    # start sending motors position thread
    logger.info("Starting WebSocket server thread...")
    websocket_thread.start()
    logger.info("Starting Adafruit MQTT thread...")
    adafruit_mqtt_thread.start()
    logger.info("Starting HTTP server thread...")
    http_thread.start()
    logger.info("Starting motor threads...")
    motors_manager.start_motor_threads()

    # move motors
    while not stop_requested:
        websocket_server.send_motors_position()
        time.sleep(1)
    
    logger.info("Main thread stopped")


def cleanup() -> None:
    logger.info("Cleaning up...")
    if motors_manager:
        logger.info("Stopping motor threads...")
        motors_manager.stop_motor_threads()

    if http_server:
        logger.info("Stopping HTTP server...")
        http_server.stop_server()

    if adafruit_mqtt_thread and adafruit_mqtt_client:
        logger.info("Stopping MQTT client...")
        adafruit_mqtt_client.stop()
        adafruit_mqtt_thread.join()

    if websocket_server and websocket_thread:
        logger.info("Stopping WebSocket server...")
        websocket_server.stop_server()
        websocket_thread.join()

    logger.info("Cleaning up GPIO")
    GPIO.cleanup()
    logger.info("Cleanup complete")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        stop_requested = True
    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        stop_requested = True
    finally:
        cleanup()
