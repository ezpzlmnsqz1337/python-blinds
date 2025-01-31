from blinds.stepper_motor import StepperMotor
from pathlib import Path
import time
class MotorsManager:
    def __init__(self, motors: list[StepperMotor]) -> None:
        self.motors = motors
        self.config_path = Path(__file__).parent / "config"
        # disable motors
        for m in self.motors:
            m.disable()
        # invert direction of first motor
        motors[0].invert_direction(True)
        # load motors cofiguration
        self.load_config()


    def get_motor(self, index: int) -> StepperMotor:
        return self.motors[index]
    
    def get_motors(self) -> list[StepperMotor]:
        return self.motors
  
    def load_config(self) -> None:
        with open(self.config_path, "r") as f:
            for m in self.motors:
                m.set_position(int(f.readline()))
                m.set_target_position(m.get_position())
                m.set_limit(int(f.readline()))


    def save_config(self) -> None:
        with open(self.config_path, "w") as f:
            for m in self.motors:
                f.write(f"{m.get_target_position()}\n")
                f.write(f"{m.get_limit()}\n")
    
    
    def move_motors(self) -> bool:
        moving = False
        m1_moving = self.motors[0].move()
        m2_moving = self.motors[1].move()
        step_pause = self.motors[0].step_pause
        if m1_moving or m2_moving:
            moving = True
        if m1_moving:
            step_pause = self.motors[0].step_pause
        if m2_moving:
            step_pause = self.motors[1].step_pause
        if m1_moving and m2_moving:
            step_pause = max(self.motors[0].step_pause, self.motors[1].step_pause)
        time.sleep(step_pause)
        return moving
    
    def stop_motors(self) -> None:
        for m in self.motors:
            m.disable()