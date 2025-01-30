import time
import threading
import RPi.GPIO as GPIO

from blinds.stepper_motor import StepperMotor
from blinds.motors_manager import MotorsManager
from blinds.websocket_server import WebSocketServer
from blinds.adafruit_mqtt import AdafruitIOMqttClient


# main classes
motors_manager: MotorsManager | None = None
websocket_server: WebSocketServer | None = None
adafruit_mqtt_client: AdafruitIOMqttClient | None = None

# threads
send_motors_position_thread: threading.Thread | None = None
websocket_thread: threading.Thread | None = None
adafruit_mqtt_thread: threading.Thread | None = None

def main() -> None:
    global websocket_server
    global motors_manager
    global send_motors_position_thread
    global websocket_thread
    global adafruit_mqtt_thread
    GPIO.setmode(GPIO.BCM)

    # motors settings
    motors = [StepperMotor(5, 6, 13, 19, 0), StepperMotor(23, 24, 25, 8, 1)]
    motors_manager = MotorsManager(motors)
    websocket_server = WebSocketServer(motors_manager)
    adafruit_mqtt_client = AdafruitIOMqttClient(websocket_server)

    send_motors_position_thread = threading.Thread(target=websocket_server.send_motors_position)
    websocket_thread = threading.Thread(target=websocket_server.start_server)
    adafruit_mqtt_thread = threading.Thread(target=adafruit_mqtt_client.run)

    # start sending motors position thread    
    send_motors_position_thread.start()
    websocket_thread.start()
    adafruit_mqtt_thread.start()

    # move motors
    while True:
        motors_manager.move_motors()
        time.sleep(0.001)


def cleanup() -> None:
    if motors_manager:
        print('Stopping motors...')
        motors_manager.stop_motors()

    if adafruit_mqtt_thread and adafruit_mqtt_client:
        print('Stopping mqtt...')
        adafruit_mqtt_client.stop()
        adafruit_mqtt_thread.join()

    if websocket_server and websocket_thread:
        print('Stopping ws server...')
        websocket_server.stop_server()
    
        if send_motors_position_thread:
            print('Stopping motors position thread...')
            send_motors_position_thread.join()

        websocket_thread.join()

    print('Cleaning up GPIO')
    GPIO.cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        cleanup()
