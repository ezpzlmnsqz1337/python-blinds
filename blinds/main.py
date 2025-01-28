import RPi.GPIO as GPIO
import stepper
import time
import sys
import os
import threading

import asyncio
from websockets.asyncio.server import serve, broadcast, ServerConnection

USER_PASSWORD = ""
CONNECTIONS: set = set()


# web socket callbacks
def go_up(msg: str) -> None:
    print("go up")
    index = int(msg.split(":")[1])
    steps = int(msg.split(":")[2])
    motor = motors[index]
    motor.set_target_position(motor.get_target_position() - steps)
    broadcast(CONNECTIONS, f"motor:{index}:goto:{motor.get_target_position() - steps} ")
    save_config()


def go_down(msg: str) -> None:
    index = int(msg.split(":")[1])
    steps = int(msg.split(":")[2])
    motor = motors[index]
    motor.set_target_position(motor.get_target_position() + steps)
    broadcast(
        CONNECTIONS, f"motor:{index}:go to: {motor.get_target_position() + steps}"
    )
    save_config()


def stop(msg: str) -> None:
    index = int(msg.split(":")[1])
    motor = motors[index]
    motor.set_target_position(motor.get_position())
    motor.disable()
    broadcast(CONNECTIONS, f"motor:{index}, stop")
    save_config()


def close_blinds() -> None:
    for m in motors:
        m.set_target_position(m.get_limit())
        broadcast(CONNECTIONS, f"motors, close, limit: {m.get_limit()} ")
    save_config()


def open_blinds() -> None:
    for m in motors:
        m.set_target_position(0)
        broadcast(CONNECTIONS, f"motors: open, bottom limit: 0 ")
    save_config()


def close_blind(msg: str) -> None:
    index = int(msg.split(":")[1])
    motor = motors[index]
    motor.set_target_position(motor.get_limit())
    broadcast(CONNECTIONS, f"motor: {index}, close, limit: {motor.get_limit()} ")
    save_config()


def open_blind(msg: str) -> None:
    index = int(msg.split(":")[1])
    motor = motors[index]
    motor.set_target_position(0)
    broadcast(CONNECTIONS, f"motor: {index}, open, bottom limit: 0 ")
    save_config()


def set_top_position(msg: str) -> None:
    password = msg.split(":")[2]
    if password == USER_PASSWORD:
        index = int(msg.split(":")[1])
        motor = motors[index]
        motor.set_top_position()
        broadcast(
            CONNECTIONS, f"setTopPosition:motor:{index}:position:{motor.get_position()}"
        )
        save_config()


def set_limit(msg: str) -> None:
    password = msg.split(":")[2]
    if password == USER_PASSWORD:
        index = int(msg.split(":")[1])
        motor = motors[index]
        motor.set_limit(motor.get_target_position())
        broadcast(
            CONNECTIONS, f"setLimit:motor:{index}:position:{motor.get_position()}"
        )
        save_config()


def set_ignore_limits(msg: str) -> None:
    password = msg.split(":")[2]
    if password == USER_PASSWORD:
        ignore_limits = True if msg.split(":")[1] == "1" else False
        for m in motors:
            m.set_ignore_limits(ignore_limits)

        broadcast(CONNECTIONS, f"setIgnoreLimits:{ignore_limits}")


async def on_ws_message(websocket: ServerConnection) -> None:
    CONNECTIONS.add(websocket)
    print("Connections: ", CONNECTIONS)
    try:
        async for msg in websocket:
            print("Message: ", msg)
            if "up" in msg:
                go_up(msg)
            elif "down" in msg:
                go_down(msg)
            elif "stop" in msg:
                stop(msg)
            elif "closeBlind" in msg:
                close_blind(msg)
            elif "openBlind" in msg:
                open_blind(msg)
            elif "CLOSE" in msg:
                close_blinds()
            elif "OPEN" in msg:
                open_blinds()
            elif "setTopPosition" in msg:
                set_top_position(msg)
            elif "setLimit" in msg:
                set_limit(msg)
            elif "getBlindsPosition" in msg:
                print("getBlindsPosition")
            elif "setIgnoreLimits" in msg:
                set_ignore_limits(msg)
    finally:
        CONNECTIONS.remove(websocket)
        await websocket.wait_closed()


async def run_ws_server():
    async with serve(on_ws_message, "", 8082):
        await asyncio.get_running_loop().create_future()  # run forever


GPIO.setmode(GPIO.BCM)

# web socket clients
ws: list = []

# motors settings
motors = (stepper.MyStepper(5, 6, 13, 19, 0), stepper.MyStepper(23, 24, 25, 8, 1))


def move_motors() -> None:
    for m in motors:
        m.move()


def send_motors_position() -> None:
    while True:
        for i, m in enumerate(motors):
            ignore = 1 if m.get_ignore_limits() == True else 0
            broadcast(
                CONNECTIONS,
                f"blindsPosition:motor:{i}:position:{m.get_position()}:target:{m.get_target_position()}:limit:{m.get_limit()}:ignoreLimit:{ignore}",
            )
        time.sleep(1)


def load_config() -> None:
    with open("config", "r") as f:
        for m in motors:
            m.set_position(int(f.readline()))
            m.set_target_position(m.get_position())
            m.set_limit(int(f.readline()))


def save_config() -> None:
    with open("config", "w") as f:
        for m in motors:
            f.write(f"{m.get_target_position()}\n")
            f.write(f"{m.get_limit()}\n")


# threads
send_motors_position_thread = threading.Thread(target=send_motors_position)
websocket_thread = threading.Thread(target=lambda: asyncio.run(run_ws_server()))


def main() -> None:
    # disable motors
    for m in motors:
        m.disable()
    # load motors cofiguration
    load_config()
    # handle password for configuration over web page
    with open("pass", "r") as f:
        global USER_PASSWORD
        USER_PASSWORD = f.readline().rstrip("\n").rstrip("\r")

    # invert direction of first motor
    motors[0].invert_direction(True)

    # start sending motors position thread
    send_motors_position_thread.start()
    websocket_thread.start()

    # move motors
    while True:
        move_motors()
        time.sleep(0.001)


def cleanup() -> None:
    for m in motors:
        m.disable()
    send_motors_position_thread.join()
    websocket_thread.join()
    GPIO.cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        cleanup()
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
