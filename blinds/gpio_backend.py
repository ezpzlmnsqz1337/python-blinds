import logging
from functools import lru_cache
from typing import Protocol

import RPi.GPIO as rpi_gpio  # pyright: ignore[reportMissingImports, reportMissingModuleSource, reportMissingTypeStubs]

logger = logging.getLogger(__name__)


class GPIOBackend(Protocol):
    HIGH: int
    LOW: int

    def setup_output(self, pin: int) -> None: ...

    def write(self, pin: int, value: int) -> None: ...

    def cleanup(self) -> None: ...


class RPiGPIOBackend:
    HIGH: int = rpi_gpio.HIGH
    LOW: int = rpi_gpio.LOW

    def __init__(self) -> None:
        rpi_gpio.setmode(rpi_gpio.BCM)
        logger.info("Using RPi.GPIO backend")

    def setup_output(self, pin: int) -> None:
        rpi_gpio.setup(pin, rpi_gpio.OUT)

    def write(self, pin: int, value: int) -> None:
        rpi_gpio.output(pin, bool(value))

    def cleanup(self) -> None:
        rpi_gpio.cleanup()


class PigpioBackend:
    def __init__(self) -> None:
        import pigpio  # type: ignore[import-untyped]  # pyright: ignore[reportMissingImports, reportMissingModuleSource, reportMissingTypeStubs]

        self._pigpio = pigpio
        self.HIGH = pigpio.HIGH
        self.LOW = pigpio.LOW
        self.client = pigpio.pi()
        if not self.client.connected:
            self.client.stop()
            raise RuntimeError("pigpio daemon is not available")
        logger.info("Using pigpio backend")

    def setup_output(self, pin: int) -> None:
        self.client.set_mode(pin, self._pigpio.OUTPUT)

    def write(self, pin: int, value: int) -> None:
        self.client.write(pin, value)

    def cleanup(self) -> None:
        self.client.stop()


@lru_cache(maxsize=1)
def get_gpio_backend() -> GPIOBackend:
    try:
        return PigpioBackend()
    except Exception as exc:
        logger.warning("pigpio unavailable, falling back to RPi.GPIO: %s", exc)
        return RPiGPIOBackend()