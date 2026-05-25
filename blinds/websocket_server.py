import asyncio
from pathlib import Path

from websockets import exceptions
from websockets.asyncio.server import ServerConnection, broadcast, serve

from blinds.motors_manager import MotorsManager


class WebSocketServer:

    def __init__(self, motors_manager: MotorsManager) -> None:
        self.connections: set[ServerConnection] = set()
        self.motors_manager = motors_manager
        self.user_password = None
        self.stop_event = asyncio.Event()

        # handle password for configuration over web page
        with open(Path(__file__).parent / "pass", "r") as f:
            self.user_password = f.readline().rstrip("\n").rstrip("\r")

    # web socket callbacks
    def go_up(self, msg: str) -> None:
        print("go up")
        index = int(msg.split(":")[1])
        steps = int(msg.split(":")[2])

        motor = self.motors_manager.get_motor(index)
        target = motor.get_target_position() - steps
        motor.set_target_position(target)
        broadcast(self.connections, f"motor:{index}:goto:{target} ")
        self.motors_manager.save_config(motor)

    def go_down(self, msg: str) -> None:
        index = int(msg.split(":")[1])
        steps = int(msg.split(":")[2])
        motor = self.motors_manager.get_motor(index)
        target = motor.get_target_position() + steps
        motor.set_target_position(target)
        broadcast(self.connections, f"motor:{index}:go to: {target}")
        self.motors_manager.save_config(motor)

    def stop(self, msg: str) -> None:
        index = int(msg.split(":")[1])
        motor = self.motors_manager.get_motor(index)
        motor.set_target_position(motor.get_position())
        motor.disable()
        broadcast(self.connections, f"motor:{index}, stop")
        self.motors_manager.save_config(motor)

    def close_blinds(self) -> None:
        for m in self.motors_manager.get_motors():
            m.set_target_position(m.get_limit())
            broadcast(self.connections, f"motors, close, limit: {m.get_limit()} ")
            self.motors_manager.save_config(m)

    def open_blinds(self) -> None:
        for m in self.motors_manager.get_motors():
            m.set_target_position(0)
            broadcast(self.connections, "motors: open, bottom limit: 0 ")
            self.motors_manager.save_config(m)

    def close_blind(self, msg: str) -> None:
        index = int(msg.split(":")[1])
        motor = self.motors_manager.get_motor(index)
        motor.set_target_position(motor.get_limit())
        broadcast(
            self.connections, f"motor: {index}, close, limit: {motor.get_limit()} "
        )
        self.motors_manager.save_config(motor)

    def open_blind(self, msg: str) -> None:
        index = int(msg.split(":")[1])
        motor = self.motors_manager.get_motor(index)
        motor.set_target_position(0)
        broadcast(self.connections, f"motor: {index}, open, bottom limit: 0 ")
        self.motors_manager.save_config(motor)

    def set_top_position(self, msg: str) -> None:
        password = msg.split(":")[2]
        if password == self.user_password:
            index = int(msg.split(":")[1])
            motor = self.motors_manager.get_motor(index)
            motor.set_top_position()
            broadcast(
                self.connections,
                f"setTopPosition:motor:{index}:position:{motor.get_position()}",
            )
            self.motors_manager.save_config(motor)

    def set_limit(self, msg: str) -> None:
        password = msg.split(":")[2]
        if password == self.user_password:
            index = int(msg.split(":")[1])
            motor = self.motors_manager.get_motor(index)
            motor.set_limit(motor.get_position())
            broadcast(
                self.connections,
                f"setLimit:motor:{index}:position:{motor.get_position()}",
            )
            self.motors_manager.save_config(motor)

    def dispatch_message(self, msg: str) -> None:
        command = msg.split(":", 1)[0]

        if command == "up":
            self.go_up(msg)
        elif command == "down":
            self.go_down(msg)
        elif command == "stop":
            self.stop(msg)
        elif command == "closeBlind":
            self.close_blind(msg)
        elif command == "openBlind":
            self.open_blind(msg)
        elif command == "CLOSE":
            self.close_blinds()
        elif command == "OPEN":
            self.open_blinds()
        elif command == "setTopPosition":
            self.set_top_position(msg)
        elif command == "setLimit":
            self.set_limit(msg)
        elif command == "setIgnoreLimits":
            self.set_ignore_limits(msg)

    def set_ignore_limits(self, msg: str) -> None:
        password = msg.split(":")[2]
        if password == self.user_password:
            ignore_limits = True if msg.split(":")[1] == "1" else False
            for m in self.motors_manager.get_motors():
                m.set_ignore_limits(ignore_limits)

            broadcast(self.connections, f"setIgnoreLimits:{ignore_limits}")

    def send_motors_position(self) -> None:
        for i, m in enumerate(self.motors_manager.get_motors()):
            ignore = 1 if m.get_ignore_limits() else 0
            broadcast(
                self.connections,
                f"blindsPosition:motor:{i}:position:{m.get_position()}:target:{m.get_target_position()}:limit:{m.get_limit()}:ignoreLimit:{ignore}",
            )

    async def on_ws_message(self, websocket: ServerConnection) -> None:
        self.connections.add(websocket)
        print("connections: ", self.connections)
        try:
            async for msg in websocket:
                msg = str(msg)
                print("Message: ", msg)
                self.dispatch_message(msg)
        except exceptions.ConnectionClosedError:
            print("Client disconnected without sending a close frame.")
        finally:
            self.connections.remove(websocket)
            await websocket.wait_closed()

    async def run_ws_server(self):
        async with serve(self.on_ws_message, "", 8082):
            await self.stop_event.wait()

    def start_server(self):
        asyncio.run(self.run_ws_server())

    def stop_server(self):
        self.stop_event.set()
