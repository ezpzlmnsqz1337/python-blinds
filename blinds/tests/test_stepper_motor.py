from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

from blinds.stepper_motor import StepperMotor


def simulate_move(target: int) -> tuple[StepperMotor, list[int], list[float]]:
    motor = StepperMotor(5, 6, 13, 19, 0)
    motor.set_limit(target)
    motor.set_target_position(target)

    positions: list[int] = []
    delays: list[float] = []
    while motor.move():
        positions.append(motor.get_position())
        delays.append(motor.step_pause)

    return motor, positions, delays


def render_speed_profile_chart(positions: list[int], delays: list[float]) -> Path:
    output_path = Path(__file__).resolve().parent / "artifacts" / "stepper_speed_profile.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rates = [1 / delay for delay in delays]

    figure, axis = plt.subplots(figsize=(10, 4.5), dpi=150)
    axis.plot(positions, rates, color="#2563eb", linewidth=2.5)
    axis.set_title("28BYJ-48 12V acceleration profile")
    axis.set_xlabel("position (steps)")
    axis.set_ylabel("speed (steps/second)")
    axis.grid(True, color="#d1d5db", linewidth=0.8)
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)

    return output_path


def test_speed_profile_accelerates_slowly_without_deceleration() -> None:
    motor, positions, delays = simulate_move(800)
    rates = [1 / delay for delay in delays]

    assert positions[-1] == 800
    assert max(rates) == rates[-1]
    assert rates[0] == 1 / motor.START_STEP_DELAY
    assert rates[motor.ACCELERATION_STEP_WINDOW - 1] == rates[0]
    assert rates[motor.ACCELERATION_STEP_WINDOW] > rates[0]
    assert all(left <= right for left, right in zip(rates, rates[1:]))
    assert min(delays) >= motor.MIN_STEP_DELAY


def test_move_completion_resets_speed_profile() -> None:
    motor, _, _ = simulate_move(80)

    assert motor.disabled is True
    assert motor.speed_level == 0
    assert motor.step_pause == motor.START_STEP_DELAY


def test_speed_profile_chart_is_generated() -> None:
    _, positions, delays = simulate_move(800)

    output_path = render_speed_profile_chart(positions, delays)

    assert output_path.exists()
    assert output_path.stat().st_size > 0