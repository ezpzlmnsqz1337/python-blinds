import logging
import threading
import time
from pathlib import Path

from blinds.stepper_motor import StepperMotor

logger = logging.getLogger(__name__)


class MotorsManager:
    def __init__(self, motors: list[StepperMotor]) -> None:
        self.motors = motors
        self.motor_threads: list[threading.Thread] = []
        self.config_lock = threading.Lock()
        self.stop_requested = False
        # disable motors
        for motor in self.motors:
            motor.disable()
        # load motor configuration
        for motor in self.motors:
            self.load_config(motor)

        # invert direction of first motor
        motors[0].invert_direction(True)

    def get_motor(self, index: int) -> StepperMotor:
        return self.motors[index]

    def get_motors(self) -> list[StepperMotor]:
        return self.motors

    def get_config_path(self, motor: StepperMotor) -> Path:
        return Path(__file__).parent / f"config_m{motor.id}"

    def load_config(self, motor: StepperMotor) -> None:
        config_path = self.get_config_path(motor)
        try:
            with self.config_lock:
                with open(config_path, "r", encoding="utf-8") as config_file:
                    position = int(config_file.readline().strip())
                    limit = int(config_file.readline().strip())
        except FileNotFoundError:
            logger.warning("Missing motor config for motor %s at %s", motor.id, config_path)
            position = 0
            limit = 0
        except ValueError:
            logger.warning("Invalid motor config for motor %s at %s", motor.id, config_path)
            position = 0
            limit = 0

        motor.set_position(position)
        motor.set_target_position(position)
        motor.set_limit(limit)

    def save_config(self, motor: StepperMotor) -> None:
        config_path = self.get_config_path(motor)
        temp_path = config_path.with_suffix(f"{config_path.suffix}.tmp")
        contents = f"{motor.get_position()}\n{motor.get_limit()}\n"

        with self.config_lock:
            with open(temp_path, "w", encoding="utf-8") as config_file:
                config_file.write(contents)
                config_file.flush()
            temp_path.replace(config_path)

    def stop_motor_threads(self) -> None:
        for m in self.motors:
            m.set_target_position(m.get_position())
            m.disable()
            # stops the threads
            self.stop_requested = True
        # join their threads
        for thread in self.motor_threads:
            thread.join()
        self.motor_threads.clear()
        self.stop_requested = False

    def move_motor(self, motor: StepperMotor) -> None:
        moving = False
        next_step_at = time.monotonic()
        while not self.stop_requested:
            is_moving = motor.move()
            if is_moving != moving:
                moving = not moving
                if not moving:
                    self.save_config(motor)

            if moving:
                next_step_at += motor.step_pause
                sleep_for = next_step_at - time.monotonic()
                if sleep_for > 0:
                    time.sleep(sleep_for)
                else:
                    next_step_at = time.monotonic()
            else:
                next_step_at = time.monotonic()
                time.sleep(motor.IDLE_STEP_DELAY)

    def start_motor_threads(self) -> None:
        self.stop_motor_threads()
        for m in self.motors:
            t = threading.Thread(target=self.move_motor, args=(m,))
            t.start()
            self.motor_threads.append(t)
