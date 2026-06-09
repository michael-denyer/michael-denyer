"""Assemble sprites into the full 1280x720 cafe scene."""

import html

from commit_cafe import sprites
from commit_cafe.choreography import plan_chase
from commit_cafe.palette import DAY, NIGHT, coat_for
from commit_cafe.state import CafeState, Pose, assign_poses

W, H = 1280, 720
FLOOR_Y = 580
CHASE_X1, CHASE_X2, CHASE_Y = 210, 620, 652

# Seat pools shared by poses; consumed in order, overflow goes to the floor line.
SLOT_GROUPS: dict[str, list[tuple[int, int]]] = {
    "shelf": [(950, 196), (1080, 196), (170, 640)],  # ALERT and SIT share these
    "loaf": [(1000, 470), (210, 400)],  # counter, then windowsill
    "sleep": [(500, 300), (600, 300), (180, 655)],
}
GROUP_FOR_POSE = {
    Pose.ALERT: "shelf",
    Pose.SIT: "shelf",
    Pose.LOAF: "loaf",
    Pose.SLEEP: "sleep",
}
OVERFLOW_Y = 660
OVERFLOW_X0, OVERFLOW_STEP = 1000, 115


def _phase(name: str) -> float:
    return (sum(name.encode()) % 100) / 100.0


def _sign(name: str, palette: dict[str, str]) -> str:
    return sprites.name_sign(
        name, palette["sign_board"], palette["sign_trim"], palette["sign_text"]
    )


def _place(state: CafeState, palette: dict[str, str]) -> tuple[str, str]:
    """Return (cats_layer, chase_layer). Chase layer uses absolute paths."""
    taken: dict[str, int] = {grp: 0 for grp in SLOT_GROUPS}
    overflow = 0
    cats_svg: list[str] = []
    chase_svg: list[str] = []
    glow = palette["eye_glow_opacity"]
    for cat, pose in zip(state.cats, assign_poses(state.cats), strict=True):
        coat, ph = coat_for(cat.name), _phase(cat.name)
        if pose is Pose.CHASE:
            chase = plan_chase(CHASE_X1, CHASE_X2, CHASE_Y)
            chase_svg.append(sprites.yarn_ball(cat.last_commit_hash, chase, palette))
            chase_svg.append(sprites.cat_chase(coat, chase, glow))
            chase_svg.append(
                f'<g transform="translate({(CHASE_X1 + CHASE_X2) // 2} {CHASE_Y + 26})">'
                f"{_sign(cat.name, palette)}</g>"
            )
            continue
        grp = GROUP_FOR_POSE[pose]
        slots = SLOT_GROUPS[grp]
        if taken[grp] < len(slots):
            x, y = slots[taken[grp]]
            taken[grp] += 1
        else:
            x, y = OVERFLOW_X0 + overflow * OVERFLOW_STEP, OVERFLOW_Y
            overflow += 1
        body = {
            Pose.ALERT: sprites.cat_alert,
            Pose.SIT: sprites.cat_sit,
            Pose.LOAF: sprites.cat_loaf,
            Pose.SLEEP: sprites.cat_sleep,
        }[pose](coat, ph, glow)
        cats_svg.append(f'<g transform="translate({x} {y})">{body}</g>')
        cats_svg.append(f'<g transform="translate({x} {y + 14})">{_sign(cat.name, palette)}</g>')
    return "".join(cats_svg), "".join(chase_svg)


def _room(palette: dict[str, str]) -> str:
    planks = "".join(
        f'<path d="M0 {FLOOR_Y + 24 + i * 28} H{W}" stroke="{palette["plank"]}" stroke-width="2"/>'
        for i in range(5)
    ) + "".join(
        f'<path d="M{(i * 173 + (i % 2) * 60) % W} {FLOOR_Y + 10 + (i % 5) * 27} v24" '
        f'stroke="{palette["plank"]}" stroke-width="2"/>'
        for i in range(14)
    )
    return (
        f'<rect width="{W}" height="{FLOOR_Y}" fill="{palette["wall"]}"/>'
        f'<rect y="{FLOOR_Y - 90}" width="{W}" height="90" fill="{palette["wainscot"]}"/>'
        f'<rect y="{FLOOR_Y - 90}" width="{W}" height="5" fill="{palette["wainscot_trim"]}"/>'
        f'<rect y="{FLOOR_Y}" width="{W}" height="{H - FLOOR_Y}" fill="{palette["floor"]}"/>'
        f"{planks}"
    )


def _furniture(state: CafeState, palette: dict[str, str]) -> str:
    def shelf(x: int, y: int, w: int) -> str:
        return (
            f'<rect x="{x}" y="{y}" width="{w}" height="13" fill="{palette["shelf"]}"/>'
            f'<rect x="{x + 10}" y="{y + 13}" width="12" height="26" '
            f'fill="{palette["shelf_bracket"]}"/>'
            f'<rect x="{x + w - 22}" y="{y + 13}" width="12" height="26" '
            f'fill="{palette["shelf_bracket"]}"/>'
        )

    counter = (
        f'<rect x="900" y="470" width="340" height="18" fill="{palette["counter_top"]}"/>'
        f'<rect x="912" y="488" width="316" height="{FLOOR_Y - 488 + 60}" '
        f'fill="{palette["counter"]}"/>'
        f'<rect x="1158" y="442" width="30" height="26" fill="#f5f0e4"/>'
        f'<path d="M1190 445 a8 8 0 0 1 0 16" stroke="#f5f0e4" stroke-width="3" '
        f'fill="none"/>'
        f'<g transform="translate(1173 436)">{sprites.steam()}</g>'
    )
    return (
        shelf(880, 196, 330)
        + shelf(420, 300, 240)
        + counter
        + f'<g transform="translate(1040 330)">'
        f"{sprites.bookshelf(state.top_languages, palette)}</g>"
        + f'<g transform="translate(1140 162)">{sprites.plant(0.3)}</g>'
        + f'<g transform="translate(480 0)">{sprites.lamp(palette)}</g>'
        + f'<g transform="translate(1100 0)">{sprites.lamp(palette)}</g>'
        + f'<g transform="translate(460 160)">'
        f"{sprites.wall_clock(state.rendered_at.hour, state.rendered_at.minute, palette)}"
        f"</g>"
    )


def render(state: CafeState, mode: str) -> str:
    palette = DAY if mode == "day" else NIGHT
    cats_layer, chase_layer = _place(state, palette)
    chalk_lines = [
        f"{state.commits_today} commits today · {state.total_stars} stars",
        f"est. {state.est_year} · rendered {state.rendered_at.strftime('%Y-%m-%d %H:%M')} UTC",
    ]
    pr = state.open_prs[0].number if state.open_prs else None
    more = max(0, len(state.open_prs) - 1)
    layers = [
        _room(palette),
        f'<g transform="translate(60 120)">{sprites.window(palette)}</g>',
        f'<g transform="translate(74 134)">{sprites.dust_motes(palette)}</g>',
        f'<g transform="translate(90 150)">{sprites.fireflies(palette)}</g>',
        f'<g transform="translate(700 18)">{sprites.chalkboard(chalk_lines, palette)}</g>',
        _furniture(state, palette),
        f'<g transform="translate(765 {FLOOR_Y})">{sprites.dog_at_door(pr, more, palette)}</g>',
        cats_layer,
        chase_layer,
        f'<g transform="translate(130 666)">{sprites.bowl(state.streak_days, palette)}</g>',
        f'<rect width="{W}" height="{H}" fill="#1b2540" opacity="{palette["room_dim_opacity"]}"/>',
    ]
    body = "".join(layers)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img">'
        f"<title>The Commit Cafe</title>"
        f"<desc>GitHub activity for {html.escape(state.username)} as an animated cat cafe: "
        f"repos are cats, poses follow commit recency, an open PR waits at the door "
        f"as a dog, and the contribution streak fills the food bowl.</desc>"
        f"{body}</svg>"
    )
