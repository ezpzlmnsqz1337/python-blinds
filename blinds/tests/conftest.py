import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class FakeGPIO(types.ModuleType):
    BCM = 11
    OUT = 0
    HIGH = 1
    LOW = 0

    def __init__(self) -> None:
        super().__init__("RPi.GPIO")

    def setmode(self, mode: int) -> None:
        return None

    def setup(self, channel: int, direction: int) -> None:
        return None

    def output(self, channel: int, value: int) -> None:
        return None

    def cleanup(self) -> None:
        return None


class FakePigpioClient:
    connected = True

    def set_mode(self, pin: int, mode: int) -> None:
        return None

    def write(self, pin: int, value: int) -> None:
        return None

    def stop(self) -> None:
        return None


class FakePigpio(types.ModuleType):
    OUTPUT = 1
    HIGH = 1
    LOW = 0

    def __init__(self) -> None:
        super().__init__("pigpio")

    def pi(self) -> FakePigpioClient:
        return FakePigpioClient()


fake_gpio = FakeGPIO()
fake_pigpio = FakePigpio()
rpi_module = types.ModuleType("RPi")
setattr(rpi_module, "GPIO", fake_gpio)

sys.modules.setdefault("RPi", rpi_module)
sys.modules.setdefault("RPi.GPIO", fake_gpio)
sys.modules.setdefault("pigpio", fake_pigpio)