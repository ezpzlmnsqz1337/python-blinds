from blinds.stepper_motor import StepperMotor
from pathlib import Path
import threading
import time


class MotorsManager:
    def __init__(self, motors: list[StepperMotor]) -> None:
        self.motors = motors
        self.motor_threads: list[threading.Thread] = []
        self.stop_requested = False
        # disable motors
        [m.disable() for m in self.motors]
        # load motor configuration
        [self.load_config(m) for m in self.motors]

        # invert direction of first motor
        motors[0].invert_direction(True)

    def get_motor(self, index: int) -> StepperMotor:
        return self.motors[index]

    def get_motors(self) -> list[StepperMotor]:
        return self.motors

    def load_config(self, motor: StepperMotor) -> None:
        with open(Path(__file__).parent / f"config_m{motor.id}", "r") as f:
            motor.set_position(int(f.readline()))
            motor.set_target_position(motor.get_position())
            motor.set_limit(int(f.readline()))

    def save_config(self, motor: StepperMotor) -> None:
        with open(Path(__file__).parent / f"config_m{motor.id}", "w") as f:
            f.write(f"{motor.get_position()}\n")
            f.write(f"{motor.get_limit()}\n")

    def stop_motor_threads(self) -> None:
        for m in self.motors:
            m.set_target_position(m.get_position())
            m.disable()
            # stops the threads
            self.stop_requested = True
        # join their threads
        [t.join() for t in self.motor_threads]
        self.motor_threads.clear()
        self.stop_requested = False

    def move_motor(self, motor: StepperMotor) -> None:
        moving = False
        while not self.stop_requested:
            if motor.move() != moving:
                moving = not moving
                if not moving:
                    self.save_config(motor)
            time.sleep(motor.step_pause)

    def start_motor_threads(self) -> None:
        self.stop_motor_threads()
        for m in self.motors:
            t = threading.Thread(target=self.move_motor, args=(m,))
            t.start()
            self.motor_threads.append(t)
