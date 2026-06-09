"""Parametric SVG sprite builders. Every public function returns a <g> string.

Sprites draw around a local origin (ground-contact point, x-centered) and are
positioned by the renderer via translate. All animation is SMIL.
"""

import html

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
