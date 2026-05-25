from blinds.gpio_backend import get_gpio_backend


class StepperMotor:
    START_STEP_DELAY = 0.0032
    MIN_STEP_DELAY = 0.0006
    STEP_DELAY_DELTA = 0.00006
    ACCELERATION_STEP_WINDOW = 20
    IDLE_STEP_DELAY = 0.01

    def __init__(self, pin0: int, pin1: int, pin2: int, pin3: int, id: int) -> None:
        self.gpio = get_gpio_backend()
        self.pin0 = pin0
        self.pin1 = pin1
        self.pin2 = pin2
        self.pin3 = pin3

        self.gpio.setup_output(self.pin0)
        self.gpio.setup_output(self.pin1)
        self.gpio.setup_output(self.pin2)
        self.gpio.setup_output(self.pin3)

        self.id = id

        self.position = 0
        self.target = 0

        self.limit = 0
        self.invert_dir = False
        self.disabled = True
        self.ignore_limits = False

        self.step_map = (
            self.step1,
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
        self.speed_level = 0
        self.max_speed_level = int(
            (self.START_STEP_DELAY - self.MIN_STEP_DELAY) / self.STEP_DELAY_DELTA
        )
        self.step_pause = self.START_STEP_DELAY

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

        self.update_speed_profile()

        if self.position < self.target:
            if self.invert_dir:
                self.step_CCW()
            else:
                self.step_CW()
        elif self.position > self.target:
            if self.invert_dir:
                self.step_CW()
            else:
                self.step_CCW()
        return True

    def update_speed_profile(self) -> None:
        if (
            self.elapsed_steps > 0
            and self.elapsed_steps % self.ACCELERATION_STEP_WINDOW == 0
            and self.speed_level < self.max_speed_level
        ):
            self.speed_level += 1

        self.step_pause = max(
            self.MIN_STEP_DELAY,
            self.START_STEP_DELAY - (self.speed_level * self.STEP_DELAY_DELTA),
        )

    def disable(self) -> None:
        self.gpio.write(self.pin0, self.gpio.LOW)
        self.gpio.write(self.pin1, self.gpio.LOW)
        self.gpio.write(self.pin2, self.gpio.LOW)
        self.gpio.write(self.pin3, self.gpio.LOW)
        self.disabled = True
        self.speed_level = 0
        self.elapsed_steps = 0
        self.step_pause = self.START_STEP_DELAY

    def step_CW(self) -> None:
        self.current_step = (self.current_step + 1) % len(self.step_map)
        self.step_map[self.current_step]()
        self.position += -1 if self.invert_dir else 1
        self.elapsed_steps += 1

    def step_CCW(self) -> None:
        self.current_step = (
            self.current_step - 1 if self.current_step > 0 else (len(self.step_map) - 1)
        )
        self.step_map[self.current_step]()
        self.position += 1 if self.invert_dir else -1
        self.elapsed_steps += 1

    def step1(self) -> None:
        self.gpio.write(self.pin0, self.gpio.HIGH)
        self.gpio.write(self.pin1, self.gpio.LOW)
        self.gpio.write(self.pin2, self.gpio.LOW)
        self.gpio.write(self.pin3, self.gpio.LOW)

    def step2(self) -> None:
        self.gpio.write(self.pin0, self.gpio.HIGH)
        self.gpio.write(self.pin1, self.gpio.HIGH)
        self.gpio.write(self.pin2, self.gpio.LOW)
        self.gpio.write(self.pin3, self.gpio.LOW)

    def step3(self) -> None:
        self.gpio.write(self.pin0, self.gpio.LOW)
        self.gpio.write(self.pin1, self.gpio.HIGH)
        self.gpio.write(self.pin2, self.gpio.LOW)
        self.gpio.write(self.pin3, self.gpio.LOW)

    def step4(self) -> None:
        self.gpio.write(self.pin0, self.gpio.LOW)
        self.gpio.write(self.pin1, self.gpio.HIGH)
        self.gpio.write(self.pin2, self.gpio.HIGH)
        self.gpio.write(self.pin3, self.gpio.LOW)

    def step5(self) -> None:
        self.gpio.write(self.pin0, self.gpio.LOW)
        self.gpio.write(self.pin1, self.gpio.LOW)
        self.gpio.write(self.pin2, self.gpio.HIGH)
        self.gpio.write(self.pin3, self.gpio.LOW)

    def step6(self) -> None:
        self.gpio.write(self.pin0, self.gpio.LOW)
        self.gpio.write(self.pin1, self.gpio.LOW)
        self.gpio.write(self.pin2, self.gpio.HIGH)
        self.gpio.write(self.pin3, self.gpio.HIGH)

    def step7(self) -> None:
        self.gpio.write(self.pin0, self.gpio.LOW)
        self.gpio.write(self.pin1, self.gpio.LOW)
        self.gpio.write(self.pin2, self.gpio.LOW)
        self.gpio.write(self.pin3, self.gpio.HIGH)

    def step8(self) -> None:
        self.gpio.write(self.pin0, self.gpio.HIGH)
        self.gpio.write(self.pin1, self.gpio.LOW)
        self.gpio.write(self.pin2, self.gpio.LOW)
        self.gpio.write(self.pin3, self.gpio.HIGH)
