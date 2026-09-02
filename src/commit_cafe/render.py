"""Assemble sprites into the full 1280x720 cafe scene."""

import html
import math

from commit_cafe import sprites
from commit_cafe.choreography import plan_chase
from commit_cafe.palette import DAY, NIGHT, coats_for
from commit_cafe.state import CafeState, Pose, assign_poses

W, H = 1280, 720
FLOOR_Y = 580
RUG_X, RUG_Y = 310, 544
CHASE_X1, CHASE_X2, CHASE_Y = 380, 820, 626
CHASE_SIGN_Y = 674
STREAK_X, STREAK_Y = 1100, 678

# Every stationary cat gets its own display zone. Keeping placement independent
# of pose prevents long repository labels from competing for the same wall area.
STATIONARY_SLOTS = [
    (930, 210),
    (1145, 210),
    (540, 330),
    (210, 420),
    (1030, 470),
]


def _star_scale(stars: int) -> float:
    """Bigger-starred repos render as slightly bigger cats, capped at 1.05–1.3x."""
    return min(1.3, max(1.05, 1.14 + 0.05 * (math.log10(stars + 1) - 1)))


def _phase(name: str) -> float:
    return (sum(name.encode()) % 100) / 100.0


def _sign(name: str, palette: dict[str, str]) -> str:
    board = palette["chalk_board"] if _phase(name) >= 0.5 else palette["sign_board"]
    return sprites.name_sign(name, board, palette["rug_trim"], palette["sign_text"])


def _place(state: CafeState, palette: dict[str, str]) -> tuple[str, str]:
    """Return (cats_layer, chase_layer). Chase layer uses absolute paths."""
    stationary_index = 0
    cats_svg: list[str] = []
    chase_svg: list[str] = []
    glow = palette["eye_glow_opacity"]
    coats = coats_for([cat.name for cat in state.cats])
    for cat, pose, coat in zip(state.cats, assign_poses(state.cats), coats, strict=True):
        ph = _phase(cat.name)
        if pose is Pose.CHASE:
            chase = plan_chase(CHASE_X1, CHASE_X2, CHASE_Y)
            chase_svg.append(sprites.yarn_ball(cat.last_commit_hash, chase, palette))
            chase_svg.append(sprites.cat_chase(coat, chase, glow, scale=_star_scale(cat.stars)))
            chase_svg.append(
                f'<g transform="translate({(CHASE_X1 + CHASE_X2) // 2} {CHASE_SIGN_Y})">'
                f"{_sign(cat.name, palette)}</g>"
            )
            continue
        x, y = STATIONARY_SLOTS[stationary_index]
        stationary_index += 1
        pose_fn = {
            Pose.ALERT: sprites.cat_alert,
            Pose.SIT: sprites.cat_sit,
            Pose.LOAF: sprites.cat_loaf,
            Pose.SLEEP: sprites.cat_sleep,
        }[pose]
        if state.streak_days == 0:
            pose_fn = sprites.cat_alert
        shadow_width = 38 if pose in (Pose.LOAF, Pose.SLEEP) else 31
        body = sprites.cat_shadow(palette, shadow_width) + pose_fn(coat, ph, glow)
        scale = _star_scale(cat.stars)
        sign_y = y + 18
        cats_svg.append(f'<g transform="translate({x} {y}) scale({scale:.3f})">{body}</g>')
        cats_svg.append(f'<g transform="translate({x} {sign_y})">{_sign(cat.name, palette)}</g>')
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
    panels = "".join(
        f'<rect x="{x}" y="507" width="138" height="55" rx="3" fill="none" '
        f'stroke="{palette["wainscot_trim"]}" stroke-width="3" opacity="0.7"/>'
        for x in range(18, W, 158)
    )
    return (
        f'<rect width="{W}" height="{FLOOR_Y}" fill="url(#wall-gradient)"/>'
        f'<rect y="{FLOOR_Y - 90}" width="{W}" height="90" fill="{palette["wainscot"]}"/>'
        f'<rect y="{FLOOR_Y - 90}" width="{W}" height="5" fill="{palette["wainscot_trim"]}"/>'
        f"{panels}"
        f'<rect y="{FLOOR_Y - 7}" width="{W}" height="7" fill="{palette["wainscot_trim"]}"/>'
        f'<rect y="{FLOOR_Y}" width="{W}" height="{H - FLOOR_Y}" fill="url(#floor-gradient)"/>'
        f"{planks}"
    )


def _scene_defs(palette: dict[str, str]) -> str:
    return (
        "<defs>"
        '<linearGradient id="wall-gradient" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{palette["wall"]}"/>'
        f'<stop offset="1" stop-color="{palette["wainscot"]}" stop-opacity="0.78"/>'
        "</linearGradient>"
        '<linearGradient id="floor-gradient" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{palette["floor"]}"/>'
        f'<stop offset="1" stop-color="{palette["plank"]}"/>'
        "</linearGradient>"
        '<linearGradient id="chalk-gradient" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{palette["chalk_board"]}"/>'
        '<stop offset="1" stop-color="#071f2b"/>'
        "</linearGradient>"
        '<linearGradient id="rug-gradient" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{palette["rug"]}"/>'
        f'<stop offset="1" stop-color="{palette["rug_pattern"]}"/>'
        "</linearGradient>"
        '<filter id="soft-shadow" x="-30%" y="-30%" width="160%" height="180%">'
        '<feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#21140d" '
        'flood-opacity="0.28"/>'
        "</filter>"
        '<filter id="small-shadow" x="-20%" y="-30%" width="140%" height="170%">'
        '<feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#21140d" '
        'flood-opacity="0.32"/>'
        "</filter>"
        "</defs>"
    )


def _string_lights(palette: dict[str, str]) -> str:
    bulbs = []
    for x, y, color in (
        (58, 31, "#ef6b66"),
        (118, 39, palette["rug_trim"]),
        (180, 43, "#6fc6b5"),
        (244, 40, "#ef6b66"),
        (306, 32, palette["rug_trim"]),
        (972, 32, "#6fc6b5"),
        (1036, 40, "#ef6b66"),
        (1100, 43, palette["rug_trim"]),
        (1162, 39, "#6fc6b5"),
        (1222, 31, "#ef6b66"),
    ):
        bulbs.append(
            f'<circle cx="{x}" cy="{y}" r="5" fill="{color}" filter="url(#small-shadow)"/>'
        )
    return (
        f'<path d="M20 20 Q190 66 350 20 M930 20 Q1090 66 1260 20" '
        f'stroke="{palette["window_frame"]}" stroke-width="3" fill="none"/>' + "".join(bulbs)
    )


def _window_sign(palette: dict[str, str]) -> str:
    return (
        f'<rect x="0" y="0" width="92" height="42" rx="10" '
        f'fill="{palette["chalk_board"]}" stroke="{palette["rug_trim"]}" stroke-width="3" '
        f'filter="url(#small-shadow)"/>'
        f'<circle cx="15" cy="21" r="5" fill="#6fc6b5"/>'
        f'<text x="55" y="28" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="18" font-weight="800" letter-spacing="1.5" '
        f'fill="{palette["chalk_text"]}">OPEN</text>'
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
        f'<rect x="908" y="486" width="324" height="158" rx="5" '
        f'fill="{palette["shadow"]}" opacity="{palette["shadow_opacity"]}"/>'
        f'<rect x="900" y="470" width="340" height="18" fill="{palette["counter_top"]}"/>'
        f'<rect x="912" y="488" width="316" height="{FLOOR_Y - 488 + 60}" '
        f'fill="{palette["counter"]}"/>'
        f'<rect x="930" y="508" width="128" height="112" rx="4" fill="none" '
        f'stroke="{palette["counter_panel"]}" stroke-width="5"/>'
        f'<rect x="1082" y="508" width="128" height="112" rx="4" fill="none" '
        f'stroke="{palette["counter_panel"]}" stroke-width="5"/>'
        f'<g transform="translate(1070 564)">{sprites.counter_badge(palette)}</g>'
        f'<rect x="1158" y="442" width="30" height="26" fill="#f5f0e4"/>'
        f'<path d="M1190 445 a8 8 0 0 1 0 16" stroke="#f5f0e4" stroke-width="3" '
        f'fill="none"/>'
        f'<g transform="translate(1173 436)">{sprites.steam()}</g>'
    )
    return (
        shelf(820, 210, 425)
        + shelf(420, 330, 240)
        + counter
        + f'<g transform="translate(1020 330)">'
        f"{sprites.bookshelf(state.top_languages[:4], palette)}</g>"
        + f'<g transform="translate(330 0)">{sprites.lamp(palette)}</g>'
        + f'<g transform="translate(1100 0)">{sprites.lamp(palette)}</g>'
        + f'<g transform="translate(375 245)">'
        f"{sprites.wall_clock(state.rendered_at.hour, state.rendered_at.minute, palette)}"
        f"</g>"
    )


def render(state: CafeState, mode: str) -> str:
    palette = DAY if mode == "day" else NIGHT
    cats_layer, chase_layer = _place(state, palette)
    repo_label = "repo cat" if len(state.cats) == 1 else "repo cats"
    commit_label = "commit" if state.commits_today == 1 else "commits"
    chalk_lines = [
        f"{len(state.cats)} {repo_label} in residence · {state.total_stars} stars",
        f"{state.commits_today} {commit_label} today",
    ]
    pr = state.open_prs[0].number if state.open_prs else None
    more = max(0, len(state.open_prs) - 1)
    layers = [
        _scene_defs(palette),
        _room(palette),
        _string_lights(palette),
        f'<g transform="translate(60 120)">{sprites.window(palette)}</g>',
        f'<g transform="translate(74 134)">{sprites.dust_motes(palette)}</g>',
        f'<g transform="translate(90 150)">{sprites.fireflies(palette)}</g>',
        f'<g transform="translate(92 164)">{_window_sign(palette)}</g>',
        f'<g transform="translate(620 12)">{sprites.chalkboard(chalk_lines, palette)}</g>',
        _furniture(state, palette),
        f'<g transform="translate(765 {FLOOR_Y})">{sprites.dog_at_door(pr, more, palette)}</g>',
        f'<g transform="translate({RUG_X} {RUG_Y})">{sprites.rug(palette)}</g>',
        f'<g transform="translate({RUG_X} {RUG_Y})">{sprites.activity_stage(palette)}</g>',
        cats_layer,
        chase_layer,
        (
            f'<g transform="translate({STREAK_X} {STREAK_Y})">'
            f"{sprites.bowl(state.streak_days, palette)}</g>"
        ),
        f'<rect width="{W}" height="{H}" fill="#1b2540" opacity="{palette["room_dim_opacity"]}"/>',
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="none" '
        f'stroke="{palette["window_frame"]}" stroke-width="4" opacity="0.45"/>',
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
