"""Cat coat assignment and day/night scene palettes."""

import hashlib

from pydantic import BaseModel


class Coat(BaseModel, frozen=True):
    pattern: str
    body: str
    shade: str
    chest: str
    eye: str


_COATS = [
    Coat(pattern="ginger", body="#e8954f", shade="#c97636", chest="#f5d9b8", eye="#3f7a3a"),
    Coat(pattern="tuxedo", body="#3a3a41", shade="#26262c", chest="#f0ece2", eye="#c9a24a"),
    Coat(pattern="solid", body="#9a9aa8", shade="#7c7c8a", chest="#c8c8d4", eye="#4a7a9c"),
    Coat(pattern="tabby", body="#b98a5e", shade="#9c6f44", chest="#e8d9b8", eye="#3f7a3a"),
    Coat(pattern="calico", body="#f0ece2", shade="#d8d2c2", chest="#f0ece2", eye="#c9a24a"),
    Coat(pattern="socks", body="#5a4a42", shade="#46382f", chest="#e8d9b8", eye="#4a7a9c"),
]
_EYES = ["#3f7a3a", "#c9a24a", "#4a7a9c", "#8a5f9c"]


def _digest(name: str, salt: bytes = b"") -> int:
    return int.from_bytes(hashlib.sha1(name.encode() + salt).digest()[:4], "big")


def coat_for(name: str) -> Coat:
    base = _COATS[_digest(name) % len(_COATS)]
    return base.model_copy(update={"eye": _EYES[_digest(name, b"eye") % len(_EYES)]})


DAY = {
    "wall": "#e8d4b4",
    "wainscot": "#dcc49e",
    "wainscot_trim": "#c9a87e",
    "floor": "#a06b42",
    "plank": "#8a5732",
    "window_frame": "#6e4a2e",
    "sky_top": "#9cc4e4",
    "sky_bottom": "#c4ddf0",
    "city": "#7c95ad",
    "city_window": "#5f7991",
    "shelf": "#8a5f3c",
    "shelf_bracket": "#6e4a2e",
    "sign_board": "#8a5f3c",
    "sign_trim": "#6e4a2e",
    "sign_text": "#f5ead2",
    "chalk_board": "#33393a",
    "chalk_text": "#f5ead2",
    "counter": "#6e4a2e",
    "counter_top": "#8a5f3c",
    "door": "#8a5f3c",
    "door_glass": "#c4ddf0",
    "bowl": "#c75450",
    "bowl_inner": "#a83c38",
    "kibble": "#8a5f3c",
    "lamp_shade": "#c75450",
    "lamp_glow_opacity": "0",
    "beam_opacity": "0.16",
    "stars_opacity": "0",
    "moon_opacity": "0",
    "cloud_opacity": "0.9",
    "eye_glow_opacity": "0",
    "firefly_opacity": "0",
    "text": "#5a3f28",
    "room_dim_opacity": "0",
}

NIGHT = {
    **DAY,
    "wall": "#bda88c",
    "wainscot": "#a8916f",
    "wainscot_trim": "#8f7a5c",
    "floor": "#7c5232",
    "plank": "#684527",
    "sky_top": "#1b2540",
    "sky_bottom": "#2b3a5e",
    "city": "#1a2540",
    "city_window": "#ffd9a0",
    "door_glass": "#2b3a5e",
    "lamp_glow_opacity": "0.22",
    "beam_opacity": "0",
    "stars_opacity": "1",
    "moon_opacity": "1",
    "cloud_opacity": "0",
    "eye_glow_opacity": "0.5",
    "firefly_opacity": "1",
    "text": "#e8dcc8",
    "room_dim_opacity": "0.14",
}
