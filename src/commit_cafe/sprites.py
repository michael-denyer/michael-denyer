"""Parametric SVG sprite builders. Every public function returns a <g> string.

Sprites draw around a local origin (ground-contact point, x-centered) and are
positioned by the renderer via translate. All animation is SMIL.
"""

import html
import math

from commit_cafe.palette import Coat

EAR_INNER = "#d98a8a"
NOSE = "#d98a8a"
LINE = "#2c2620"


def g(content: str, transform: str = "") -> str:
    attr = f' transform="{transform}"' if transform else ""
    return f"<g{attr}>{content}</g>"


def swish(cx: float, cy: float, dur: float, amp: float, phase: float) -> str:
    """Rotate-about-point tail swish with eased keyframes."""
    return (
        f'<animateTransform attributeName="transform" type="rotate" '
        f'values="0 {cx} {cy};{amp} {cx} {cy};0 {cx} {cy};{-amp * 0.6} {cx} {cy};0 {cx} {cy}" '
        f'keyTimes="0;0.3;0.55;0.8;1" calcMode="spline" '
        f'keySplines="0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1" '
        f'dur="{dur}s" begin="{-phase * dur:.4f}s" repeatCount="indefinite"/>'
    )


def breathe(content: str, cx: float, cy: float, dur: float, amp: float, phase: float) -> str:
    """Wrap content so it scales gently about (cx, cy)."""
    anim = (
        f'<animateTransform attributeName="transform" type="scale" '
        f'values="1 1;1 {1 + amp};1 1" keyTimes="0;0.5;1" calcMode="spline" '
        f'keySplines="0.4 0 0.6 1;0.4 0 0.6 1" '
        f'dur="{dur}s" begin="{-phase * dur:.4f}s" repeatCount="indefinite"/>'
    )
    return (
        f'<g transform="translate({cx} {cy})"><g>{anim}'
        f'<g transform="translate({-cx} {-cy})">{content}</g></g></g>'
    )


def _blink(open_eyes: str, closed_eyes: str, dur: float, phase: float) -> str:
    begin = f"{-phase * dur:.4f}s"
    show_open = (
        f'<animate attributeName="opacity" values="1;1;0;0;1" '
        f'keyTimes="0;0.92;0.93;0.97;0.98" dur="{dur}s" begin="{begin}" '
        f'repeatCount="indefinite"/>'
    )
    show_closed = (
        f'<animate attributeName="opacity" values="0;0;1;1;0" '
        f'keyTimes="0;0.92;0.93;0.97;0.98" dur="{dur}s" begin="{begin}" '
        f'repeatCount="indefinite"/>'
    )
    return (
        f'<g opacity="1">{show_open}{open_eyes}</g>'
        f'<g opacity="0">{show_closed}{closed_eyes}</g>'
    )


def _ear(x: float, y: float, s: float, color: str, tilt: float, flick_phase: float = -1) -> str:
    flick = ""
    if flick_phase >= 0:
        flick = (
            f'<animateTransform attributeName="transform" type="rotate" '
            f'values="0 {x} {y};0 {x} {y};-9 {x} {y};0 {x} {y};0 {x} {y}" '
            f'keyTimes="0;0.55;0.6;0.65;1" dur="9s" begin="{-flick_phase * 9:.4f}s" '
            f'repeatCount="indefinite"/>'
        )
    return g(
        f"{flick}"
        f'<path d="M{x} {y} L{x + s * tilt} {y - s * 1.3} L{x + s} {y} Z" fill="{color}"/>'
        f'<path d="M{x + s * 0.25} {y - s * 0.1} L{x + s * 0.5 * (1 + tilt * 0.6)} '
        f'{y - s * 0.75} L{x + s * 0.75} {y - s * 0.1} Z" fill="{EAR_INNER}"/>'
    )


def _eyes_open(cx: float, cy: float, gap: float, r: float, coat: Coat, glow: str) -> str:
    glow_circles = (
        f'<circle cx="{cx - gap}" cy="{cy}" r="{r + 1.5}" fill="{coat.eye}" opacity="{glow}"/>'
        f'<circle cx="{cx + gap}" cy="{cy}" r="{r + 1.5}" fill="{coat.eye}" opacity="{glow}"/>'
    )
    return (
        glow_circles
        + f'<circle cx="{cx - gap}" cy="{cy}" r="{r}" fill="{LINE}"/>'
        + f'<circle cx="{cx + gap}" cy="{cy}" r="{r}" fill="{LINE}"/>'
    )


def _eyes_closed(cx: float, cy: float, gap: float, r: float) -> str:
    return (
        f'<path d="M{cx - gap - r} {cy} Q{cx - gap} {cy + r * 1.4} {cx - gap + r} {cy}" '
        f'stroke="{LINE}" stroke-width="2" fill="none" stroke-linecap="round"/>'
        f'<path d="M{cx + gap - r} {cy} Q{cx + gap} {cy + r * 1.4} {cx + gap + r} {cy}" '
        f'stroke="{LINE}" stroke-width="2" fill="none" stroke-linecap="round"/>'
    )


def _whiskers(x: float, y: float, direction: int) -> str:
    lines = "".join(
        f'<path d="M{x} {y + i * 2} L{x + 16 * direction} {y + i * 5 - 2}" '
        f'stroke="{LINE}" stroke-opacity="0.4" stroke-width="1"/>'
        for i in (-1, 0, 1)
    )
    return lines


def _pattern_overlay(coat: Coat, body_cx: float, body_cy: float, rx: float, ry: float) -> str:
    if coat.pattern == "tabby":
        return "".join(
            f'<path d="M{body_cx + dx} {body_cy - ry * 0.8} Q{body_cx + dx + 4} {body_cy} '
            f'{body_cx + dx} {body_cy + ry * 0.5}" stroke="{coat.shade}" '
            f'stroke-width="4" fill="none" stroke-linecap="round"/>'
            for dx in (-rx * 0.4, 0, rx * 0.4)
        )
    if coat.pattern == "calico":
        return (
            f'<ellipse cx="{body_cx - rx * 0.4}" cy="{body_cy - ry * 0.3}" rx="{rx * 0.35}" '
            f'ry="{ry * 0.4}" fill="#e8954f"/>'
            f'<ellipse cx="{body_cx + rx * 0.45}" cy="{body_cy + ry * 0.1}" rx="{rx * 0.3}" '
            f'ry="{ry * 0.35}" fill="#5a4a42"/>'
        )
    if coat.pattern in ("tuxedo", "socks"):
        return (
            f'<ellipse cx="{body_cx - rx * 0.35}" cy="{body_cy + ry * 0.85}" rx="7" ry="4" '
            f'fill="{coat.chest}"/>'
            f'<ellipse cx="{body_cx + rx * 0.35}" cy="{body_cy + ry * 0.85}" rx="7" ry="4" '
            f'fill="{coat.chest}"/>'
        )
    return ""


def cat_sit(coat: Coat, phase: float, eye_glow_opacity: str) -> str:
    body = (
        f'<path d="M24 -6 Q52 -10 46 -44" stroke="{coat.body}" stroke-width="9" '
        f'fill="none" stroke-linecap="round">{swish(24, -6, 6, 12, phase)}</path>'
        f'<ellipse cx="0" cy="-28" rx="27" ry="30" fill="{coat.body}"/>'
        f'<ellipse cx="0" cy="-16" rx="14" ry="12" fill="{coat.chest}"/>'
        f"{_pattern_overlay(coat, 0, -28, 27, 30)}"
        f'<ellipse cx="-12" cy="-2" rx="9" ry="6" fill="{coat.body}"/>'
        f'<ellipse cx="10" cy="-2" rx="9" ry="6" fill="{coat.body}"/>'
    )
    sit_blink = _blink(
        _eyes_open(0, -64, 8, 2.5, coat, eye_glow_opacity), _eyes_closed(0, -64, 8, 2.5), 5.2, phase
    )
    head = (
        f'<circle cx="0" cy="-62" r="19" fill="{coat.body}"/>'
        f"{_ear(-18, -74, 13, coat.body, 0.35, flick_phase=phase)}"
        f"{_ear(5, -74, 13, coat.body, 0.65)}"
        f"{sit_blink}"
        f'<circle cx="0" cy="-57" r="2" fill="{NOSE}"/>'
        f"{_whiskers(-12, -58, -1)}{_whiskers(12, -58, 1)}"
    )
    return g(body + head)


def cat_alert(coat: Coat, phase: float, eye_glow_opacity: str) -> str:
    """Sitting upright, eyes wide, tail twitching fast — watching the yarn."""
    body = (
        f'<path d="M24 -6 Q52 -10 46 -44" stroke="{coat.body}" stroke-width="9" '
        f'fill="none" stroke-linecap="round">{swish(24, -6, 2.4, 16, phase)}</path>'
        f'<ellipse cx="0" cy="-30" rx="25" ry="32" fill="{coat.body}"/>'
        f'<ellipse cx="0" cy="-17" rx="13" ry="12" fill="{coat.chest}"/>'
        f"{_pattern_overlay(coat, 0, -30, 25, 32)}"
        f'<ellipse cx="-12" cy="-2" rx="9" ry="6" fill="{coat.body}"/>'
        f'<ellipse cx="10" cy="-2" rx="9" ry="6" fill="{coat.body}"/>'
    )
    head = (
        f'<circle cx="0" cy="-66" r="19" fill="{coat.body}"/>'
        f"{_ear(-19, -79, 14, coat.body, 0.3)}"
        f"{_ear(5, -79, 14, coat.body, 0.7)}"
        f"{_eyes_open(0, -68, 8, 3.5, coat, eye_glow_opacity)}"
        f'<circle cx="0" cy="-60" r="2" fill="{NOSE}"/>'
        f"{_whiskers(-12, -61, -1)}{_whiskers(12, -61, 1)}"
    )
    return g(body + head)


def cat_loaf(coat: Coat, phase: float, eye_glow_opacity: str) -> str:
    body = (
        f'<ellipse cx="0" cy="-15" rx="32" ry="16" fill="{coat.body}"/>'
        f"{_pattern_overlay(coat, 0, -15, 32, 16)}"
        f'<path d="M28 -10 Q44 -14 42 -30" stroke="{coat.shade}" stroke-width="6" '
        f'fill="none" stroke-linecap="round">{swish(28, -10, 7, 10, phase)}</path>'
    )
    loaf_blink = _blink(
        _eyes_open(-24, -27, 7, 2.2, coat, eye_glow_opacity),
        _eyes_closed(-24, -27, 7, 2.2),
        6.4,
        phase,
    )
    head = (
        f'<circle cx="-24" cy="-26" r="16" fill="{coat.body}"/>'
        f"{_ear(-37, -37, 11, coat.body, 0.4, flick_phase=phase)}"
        f"{_ear(-20, -38, 11, coat.body, 0.6)}"
        f"{loaf_blink}"
        f'<circle cx="-24" cy="-21" r="1.8" fill="{NOSE}"/>'
    )
    return breathe(g(body + head), 0, -15, dur=4.0, amp=0.03, phase=phase)


def cat_sleep(coat: Coat, phase: float, eye_glow_opacity: str) -> str:
    del eye_glow_opacity  # sleeping cats keep their eyes shut
    body = (
        f'<ellipse cx="0" cy="-14" rx="36" ry="17" fill="{coat.body}"/>'
        f"{_pattern_overlay(coat, 0, -14, 36, 17)}"
        f'<path d="M30 -6 Q10 4 -22 -4" stroke="{coat.shade}" stroke-width="7" '
        f'fill="none" stroke-linecap="round"/>'
        f'<circle cx="-26" cy="-20" r="15" fill="{coat.body}"/>'
        f"{_ear(-38, -30, 10, coat.body, 0.4)}"
        f"{_ear(-22, -31, 10, coat.body, 0.6)}"
        f"{_eyes_closed(-26, -20, 5, 2)}"
    )
    zs = "".join(
        f'<text x="-20" y="-44" font-family="Georgia, serif" font-size="{13 + i * 4}" '
        f'fill="{LINE}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.7;0" keyTimes="0;0.3;1" dur="4s" '
        f'begin="{i * 1.3 - phase * 4:.4f}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;6 -26" '
        f'dur="4s" begin="{i * 1.3 - phase * 4:.4f}s" repeatCount="indefinite"/>z</text>'
        for i in range(3)
    )
    return g(breathe(body, 0, -14, dur=4.4, amp=0.05, phase=phase) + zs)


def name_sign(text: str, board: str, trim: str, text_color: str) -> str:
    width = 10 * len(text) + 22
    return g(
        f'<rect x="{-width / 2}" y="0" width="{width}" height="26" fill="{board}" rx="3"/>'
        f'<rect x="{-width / 2}" y="22" width="{width}" height="4" fill="{trim}" rx="2"/>'
        f'<text x="0" y="18" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="14" font-weight="500" fill="{text_color}">{html.escape(text)}</text>'
    )


DOG_BODY = "#b98a5e"
DOG_SHADE = "#9c6f44"


def dog_at_door(pr_number: int | None, more_count: int, palette: dict[str, str]) -> str:
    """Door with glass pane; a bouncing dog appears when a PR is open.

    Origin: door bottom-center on the floor line.
    """
    door = (
        f'<rect x="-65" y="-310" width="130" height="310" fill="{palette["door"]}"/>'
        f'<rect x="-57" y="-302" width="114" height="294" fill="{palette["shelf"]}"/>'
        f'<rect x="-47" y="-288" width="94" height="130" fill="{palette["door_glass"]}"/>'
        f'<circle cx="41" cy="-120" r="6" fill="#c9a24a"/>'
    )
    if pr_number is None:
        sign_text = "deliveries welcome"
        dog = ""
        extra = ""
    else:
        sign_text = f"PR #{pr_number} · let me in?"
        bounce = (
            '<animateTransform attributeName="transform" type="translate" '
            'values="0 0;0 -14;0 0" keyTimes="0;0.5;1" calcMode="spline" '
            'keySplines="0.3 0 0.4 1;0.6 0 0.7 1" dur="0.9s" repeatCount="indefinite"/>'
        )
        wag = (
            '<animateTransform attributeName="transform" type="rotate" '
            'values="-20 18 -178;20 18 -178;-20 18 -178" dur="0.45s" repeatCount="indefinite"/>'
        )
        dog = (
            f"<g>{bounce}"
            f'<path d="M18 -178 L34 -192" stroke="{DOG_SHADE}" stroke-width="6" '
            f'stroke-linecap="round">{wag}</path>'
            f'<circle cx="0" cy="-198" r="26" fill="{DOG_BODY}"/>'
            f'<ellipse cx="-23" cy="-198" rx="9" ry="20" fill="{DOG_BODY}" '
            f'transform="rotate(20 -23 -198)"/>'
            f'<ellipse cx="23" cy="-198" rx="9" ry="20" fill="{DOG_BODY}" '
            f'transform="rotate(-20 23 -198)"/>'
            f'<ellipse cx="0" cy="-188" rx="13" ry="10" fill="#e8d9b8"/>'
            f'<circle cx="0" cy="-192" r="4" fill="{LINE}"/>'
            f'<circle cx="-9" cy="-204" r="2.6" fill="{LINE}"/>'
            f'<circle cx="9" cy="-204" r="2.6" fill="{LINE}"/>'
            f'<rect x="-3" y="-184" width="7" height="10" rx="3" fill="{EAR_INNER}"/>'
            f"</g>"
            f'<circle cx="-23" cy="-168" r="7" fill="{DOG_SHADE}"/>'
            f'<circle cx="23" cy="-168" r="7" fill="{DOG_SHADE}"/>'
        )
        extra = (
            f'<text x="0" y="-322" text-anchor="middle" font-family="Georgia, serif" '
            f'font-size="13" fill="{palette["text"]}">+{more_count} waiting</text>'
            if more_count > 0
            else ""
        )
    hang = (
        f'<path d="M-25 -332 V-344 M25 -332 V-344" stroke="{palette["sign_trim"]}" '
        f'stroke-width="2"/>'
    )
    sign = g(name_sign(sign_text, palette["sign_board"], palette["sign_trim"],
                       palette["sign_text"]), transform="translate(0 -358)")
    return g(door + dog + hang + sign + extra)


def bowl(streak_days: int, palette: dict[str, str]) -> str:
    kibble_count = min(14, max(1, streak_days * 14 // 30)) if streak_days > 0 else 0
    bits = "".join(
        f'<circle cx="{-24 + (i * 13) % 50}" cy="{-10 + (i * 7) % 9}" r="3.2" '
        f'fill="{palette["kibble"]}"/>'
        for i in range(kibble_count)
    )
    unit = "day" if streak_days == 1 else "days"
    label = f"{streak_days} {unit} of kibble" if streak_days > 0 else "bowl empty — commit!"
    return g(
        f'<ellipse cx="0" cy="0" rx="42" ry="16" fill="{palette["bowl"]}"/>'
        f'<ellipse cx="0" cy="-6" rx="36" ry="11" fill="{palette["bowl_inner"]}"/>'
        f"{bits}"
        f'<text x="0" y="6" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="13" font-weight="500" fill="{palette["sign_text"]}">STREAK</text>'
        f'<text x="0" y="30" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="14" fill="{palette["text"]}">{label}</text>'
    )


def chalkboard(lines: list[str], palette: dict[str, str]) -> str:
    title = (
        f'<text x="0" y="38" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="26" font-weight="500" fill="{palette["chalk_text"]}">THE COMMIT CAFE</text>'
    )
    rows = "".join(
        f'<text x="0" y="{62 + i * 18}" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="14" fill="{palette["chalk_text"]}">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    height = 70 + len(lines) * 18
    return g(
        f'<rect x="-160" y="0" width="320" height="{height}" fill="{palette["chalk_board"]}"/>'
        f'<rect x="-160" y="0" width="320" height="{height}" fill="none" '
        f'stroke="{palette["window_frame"]}" stroke-width="6"/>'
        + title
        + rows
    )


def bookshelf(languages: list[tuple[str, float]], palette: dict[str, str]) -> str:
    """Book spines sized by language share. Origin: shelf-board top-left."""
    spine_colors = ["#c75450", "#4e7a4a", "#4a7a9c", "#c9a24a", "#8a5f9c"]
    total_width = 170.0
    x = 6.0
    spines = []
    for i, (lang, share) in enumerate(languages[:5]):
        w = max(18.0, total_width * share)
        h = 52 - (i % 3) * 6
        color = spine_colors[i % len(spine_colors)]
        spines.append(
            f'<g class="spine"><rect x="{x:.1f}" y="{-h}" width="{w:.1f}" height="{h}" '
            f'fill="{color}" rx="2"/>'
            f'<text x="{x + w / 2:.1f}" y="{-h / 2 + 4:.0f}" text-anchor="middle" '
            f'font-family="Georgia, serif" font-size="11" fill="#f5ead2" '
            f'transform="rotate(-90 {x + w / 2:.1f} {-h / 2:.0f})">{html.escape(lang)}</text></g>'
        )
        x += w + 4
    board = (
        f'<rect x="0" y="0" width="{x + 2:.1f}" height="12" fill="{palette["shelf"]}"/>'
        f'<rect x="6" y="12" width="10" height="22" fill="{palette["shelf_bracket"]}"/>'
        f'<rect x="{x - 14:.1f}" y="12" width="10" height="22" '
        f'fill="{palette["shelf_bracket"]}"/>'
    )
    return g("".join(spines) + board)


def wall_clock(hour: int, minute: int, palette: dict[str, str]) -> str:
    hour_angle = (hour % 12 + minute / 60) * 30
    minute_angle = minute * 6
    hx = 14 * math.sin(math.radians(hour_angle))
    hy = -14 * math.cos(math.radians(hour_angle))
    mx = 20 * math.sin(math.radians(minute_angle))
    my = -20 * math.cos(math.radians(minute_angle))
    return g(
        f'<circle cx="0" cy="0" r="28" fill="{palette["sign_text"]}" '
        f'stroke="{palette["window_frame"]}" stroke-width="5"/>'
        f'<path d="M0 0 L{hx:.1f} {hy:.1f}" stroke="{LINE}" stroke-width="3" '
        f'stroke-linecap="round"/>'
        f'<path d="M0 0 L{mx:.1f} {my:.1f}" stroke="{LINE}" stroke-width="2" '
        f'stroke-linecap="round"/>'
        f'<circle cx="0" cy="0" r="2.5" fill="{LINE}"/>'
    )


def window(palette: dict[str, str]) -> str:
    """300x280 window. Origin: top-left of frame. Day shows clouds; night shows
    stars, moon, and flickering city windows — both variants are emitted and
    the palette's opacity switches select which is visible."""
    sky = (
        f'<rect x="14" y="14" width="272" height="126" fill="{palette["sky_top"]}"/>'
        f'<rect x="14" y="140" width="272" height="126" fill="{palette["sky_bottom"]}"/>'
    )
    clouds = (
        f'<g opacity="{palette["cloud_opacity"]}">'
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="-80 0;300 0" dur="34s" repeatCount="indefinite"/>'
        f'<ellipse cx="60" cy="60" rx="34" ry="12" fill="#f5f2ea"/>'
        f'<ellipse cx="84" cy="52" rx="22" ry="10" fill="#f5f2ea"/></g>'
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="320 0;-100 0" dur="52s" repeatCount="indefinite"/>'
        f'<ellipse cx="40" cy="110" rx="28" ry="10" fill="#efe9dd"/></g></g>'
    )
    stars = f'<g opacity="{palette["stars_opacity"]}">' + "".join(
        f'<circle cx="{30 + (i * 47) % 240}" cy="{28 + (i * 31) % 100}" r="1.4" fill="#dfe6ff">'
        f'<animate attributeName="opacity" values="0.3;1;0.3" dur="{2.4 + (i % 4) * 0.9:.1f}s" '
        f'begin="{-(i % 5) * 0.7:.4f}s" repeatCount="indefinite"/></circle>'
        for i in range(16)
    ) + (
        f'</g><circle cx="240" cy="62" r="24" fill="#f0e6cd" '
        f'opacity="{palette["moon_opacity"]}"/>'
    )
    city = (
        f'<g><rect x="30" y="186" width="50" height="80" fill="{palette["city"]}"/>'
        f'<rect x="100" y="166" width="40" height="100" fill="{palette["city"]}"/>'
        f'<rect x="160" y="196" width="60" height="70" fill="{palette["city"]}"/>'
        f'<rect x="236" y="176" width="40" height="90" fill="{palette["city"]}"/>'
        + "".join(
            f'<rect x="{38 + (i * 53) % 220}" y="{196 + (i * 23) % 56}" width="8" height="9" '
            f'fill="{palette["city_window"]}">'
            f'<animate attributeName="opacity" values="1;1;0.2;1" keyTimes="0;0.7;0.75;0.8" '
            f'calcMode="discrete" dur="{5 + i}s" repeatCount="indefinite"/></rect>'
            for i in range(6)
        )
        + "</g>"
    )
    frame = (
        f'<rect x="0" y="0" width="300" height="280" fill="none" '
        f'stroke="{palette["window_frame"]}" stroke-width="14"/>'
        f'<rect x="144" y="14" width="10" height="252" fill="{palette["window_frame"]}"/>'
        f'<rect x="14" y="132" width="272" height="10" fill="{palette["window_frame"]}"/>'
    )
    return g(sky + clouds + stars + city + frame)


def plant(swing_phase: float = 0.0) -> str:
    leaves = "".join(
        f'<ellipse cx="{[-22, -12, 0, 12, 22][i]}" cy="{[-26, -38, -44, -38, -26][i]}" '
        f'rx="7" ry="17" fill="#4e7a4a" '
        f'transform="rotate({[-40, -18, 0, 18, 40][i]} {[-22, -12, 0, 12, 22][i]} '
        f'{[-26, -38, -44, -38, -26][i]})"/>'
        for i in range(5)
    )
    sway = (
        f'<animateTransform attributeName="transform" type="rotate" '
        f'values="0 0 0;2.5 0 0;0 0 0;-2 0 0;0 0 0" dur="7s" '
        f'begin="{-swing_phase * 7:.4f}s" repeatCount="indefinite"/>'
    )
    pot = '<path d="M-24 0 L24 0 L16 -28 L-16 -28 Z" fill="#b3593e" transform="scale(1 -1)"/>'
    return g(f"<g>{sway}{leaves}</g>" + pot)


def lamp(palette: dict[str, str]) -> str:
    """Pendant lamp. Origin: ceiling attachment point."""
    return g(
        f'<path d="M0 0 V56" stroke="#5a4632" stroke-width="3"/>'
        f'<path d="M-26 92 L26 92 L14 58 L-14 58 Z" fill="{palette["lamp_shade"]}"/>'
        f'<circle cx="0" cy="94" r="7" fill="#ffd9a0"/>'
        f'<circle cx="0" cy="120" r="56" fill="#ffd9a0" '
        f'opacity="{palette["lamp_glow_opacity"]}"/>'
        f'<path d="M-26 92 L26 92 L78 360 L-78 360 Z" fill="#ffd9a0" '
        f'opacity="{palette["lamp_glow_opacity"]}"/>'
    )


def steam() -> str:
    puffs = "".join(
        f'<circle cx="{i * 3 - 3}" cy="0" r="{4 + i}" fill="#f5f2ea" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.5;0" dur="3.2s" begin="{i * 1.05:.4f}s" '
        f'repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;{4 - i * 4} -34" dur="3.2s" begin="{i * 1.05:.4f}s" '
        f'repeatCount="indefinite"/></circle>'
        for i in range(3)
    )
    return g(puffs)


def dust_motes(palette: dict[str, str]) -> str:
    """Floating dust in the window sunbeam (day only via beam_opacity)."""
    motes = "".join(
        f'<circle cx="{(i * 37) % 180}" cy="{(i * 53) % 240}" r="1.6" fill="#fff8e8">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;{8 - (i % 3) * 6} {18 + (i % 4) * 8};0 0" dur="{9 + i}s" '
        f'repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.2;0.8;0.2" dur="{7 + i}s" '
        f'repeatCount="indefinite"/></circle>'
        for i in range(8)
    )
    beam = (
        f'<path d="M0 0 L90 0 L260 460 L100 460 Z" fill="#fff3d6" '
        f'opacity="{palette["beam_opacity"]}"/>'
    )
    return g(beam + f'<g opacity="{palette["beam_opacity"]}">{motes}</g>')


def fireflies(palette: dict[str, str]) -> str:
    flies = "".join(
        f'<circle cx="{30 + i * 60}" cy="{20 + i * 30}" r="2.4" fill="#ffe9a0">'
        f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;0.15;0.4;1" '
        f'dur="{3.4 + i * 1.3:.1f}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;{14 - i * 10} {-12 + i * 8};0 0" dur="{8 + i * 2}s" '
        f'repeatCount="indefinite"/></circle>'
        for i in range(2)
    )
    return g(f'<g opacity="{palette["firefly_opacity"]}">{flies}</g>')
