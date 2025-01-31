import RPi.GPIO as GPIO

class StepperMotor:
    def __init__(self, pin0: int, pin1: int, pin2: int, pin3: int, id: int) -> None:
        self.pin0 = pin0
        self.pin1 = pin1
        self.pin2 = pin2
        self.pin3 = pin3

        GPIO.setup(self.pin0, GPIO.OUT)
        GPIO.setup(self.pin1, GPIO.OUT)
        GPIO.setup(self.pin2, GPIO.OUT)
        GPIO.setup(self.pin3, GPIO.OUT)

        self.id = id

        self.position = 0
        self.target = 0

        self.limit = 0
        self.invert_dir = False
        self.disabled = True
        self.ignore_limits = False

        self.step_map = (self.step1,
                        self.step2,
                        self.step3,
                        self.step4,
                        self.step5,
                        self.step6,
                        self.step7,
                        self.step8,
                        )
        self.current_step = 0
        self.elapsed_steps = 0
        self.step_pause = 0.002

    def invert_direction(self, invert: bool) -> None:
        self.invert_dir = invert

    def set_position(self, new_position: int) -> None:
        self.position = new_position

    def get_position(self) -> int:
        return self.position

    def set_limit_to_current_position(self) -> None:
        self.limit = self.position

    def set_limit(self, limit: int) -> None:
        self.limit = limit

    def get_limit(self) -> int:
        return self.limit

    def set_top_position(self) -> None:
        self.position = 0
        self.target = 0

    def set_target_position(self, target_position: int) -> None:
        self.target = target_position
        self.disabled = False

    def get_target_position(self) -> int:
        return self.target

    def set_ignore_limits(self, ignore: bool) -> None:
        self.ignore_limits = ignore

    def get_ignore_limits(self) -> bool:
        return self.ignore_limits

    def move(self) -> bool:
        if not self.ignore_limits:
            if self.target > self.limit:
                self.target = self.limit
            elif self.target <= 0:
                self.target = 0

        if self.position == self.target:
            if not self.disabled:
                self.disable()
            return False
        elif self.position < self.target:
            if self.invert_dir:
                self.step_CCW()
            else:
                self.step_CW()
        elif self.position > self.target:
            if self.invert_dir:
                self.step_CW()
            else:
                self.step_CCW()
        
        if self.elapsed_steps != 0 and self.elapsed_steps % 200 == 0:
            if self.step_pause - 0.0001 > 0.0004:
                self.step_pause -= 0.0001
        return True

    def disable(self) -> None:
        GPIO.output(self.pin0, GPIO.LOW)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)
        GPIO.output(self.pin3, GPIO.LOW)
        self.disabled = True
        self.elapsed_steps = 0
        self.step_pause = 0.002

    def step_CW(self):
        self.current_step = (self.current_step + 1) % len(self.step_map)
        self.step_map[self.current_step]()
        self.position += -1 if self.invert_dir else 1
        self.elapsed_steps += 1

    def step_CCW(self):
        self.current_step = self.current_step - \
            1 if self.current_step > 0 else (len(self.step_map) - 1)
        self.step_map[self.current_step]()
        self.position += 1 if self.invert_dir else -1
        self.elapsed_steps += 1

    def step1(self):
        GPIO.output(self.pin0, GPIO.HIGH)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)
        GPIO.output(self.pin3, GPIO.LOW)

    def step2(self):
        GPIO.output(self.pin0, GPIO.HIGH)
        GPIO.output(self.pin1, GPIO.HIGH)
        GPIO.output(self.pin2, GPIO.LOW)
        GPIO.output(self.pin3, GPIO.LOW)

    def step3(self):
        GPIO.output(self.pin0, GPIO.LOW)
        GPIO.output(self.pin1, GPIO.HIGH)
        GPIO.output(self.pin2, GPIO.LOW)
        GPIO.output(self.pin3, GPIO.LOW)

    def step4(self):
        GPIO.output(self.pin0, GPIO.LOW)
        GPIO.output(self.pin1, GPIO.HIGH)
        GPIO.output(self.pin2, GPIO.HIGH)
        GPIO.output(self.pin3, GPIO.LOW)

    def step5(self):
        GPIO.output(self.pin0, GPIO.LOW)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.HIGH)
        GPIO.output(self.pin3, GPIO.LOW)

    def step6(self):
        GPIO.output(self.pin0, GPIO.LOW)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.HIGH)
        GPIO.output(self.pin3, GPIO.HIGH)

    def step7(self):
        GPIO.output(self.pin0, GPIO.LOW)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)
        GPIO.output(self.pin3, GPIO.HIGH)

    def step8(self):
        GPIO.output(self.pin0, GPIO.HIGH)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)
        GPIO.output(self.pin3, GPIO.HIGH)

