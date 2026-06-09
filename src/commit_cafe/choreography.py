"""Pure geometry/timing for the yarn chase, kept out of the SVG layer."""

from pydantic import BaseModel

KITTEN_INSET = 60.0
KITTEN_LAG_S = -0.6
CHASE_DUR_S = 12.0


class Chase(BaseModel, frozen=True):
    dur_s: float
    ball_path: str
    kitten_path: str
    kitten_begin_s: float
    flip_key_times: str


def plan_chase(x_start: float, x_end: float, floor_y: float) -> Chase:
    """The ball bounces wall-to-wall; the kitten runs a shorter inset path so
    it reads as trailing, begins slightly behind, and flips facing at the
    midpoint turn (flip handled by the sprite via discrete opacity swaps)."""
    kx1, kx2 = x_start + KITTEN_INSET, x_end - KITTEN_INSET
    return Chase(
        dur_s=CHASE_DUR_S,
        ball_path=f"M {x_start:.0f} {floor_y:.0f} H {x_end:.0f} H {x_start:.0f}",
        kitten_path=f"M {kx1:.0f} {floor_y + 8:.0f} H {kx2:.0f} H {kx1:.0f}",
        kitten_begin_s=KITTEN_LAG_S,
        flip_key_times="0;0.5;0.5;1",
    )
