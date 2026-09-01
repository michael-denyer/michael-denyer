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
    "wall": "#f4dfb8",
    "wainscot": "#d3a66f",
    "wainscot_trim": "#9d6f43",
    "floor": "#8c5432",
    "plank": "#67381f",
    "window_frame": "#56351f",
    "sky_top": "#6fb0db",
    "sky_bottom": "#bce8f7",
    "city": "#456985",
    "city_window": "#f5d16b",
    "shelf": "#73462b",
    "shelf_bracket": "#4e2f1d",
    "sign_board": "#71442a",
    "sign_trim": "#e2aa43",
    "sign_text": "#fff4d6",
    "chalk_board": "#163744",
    "chalk_text": "#fff1cf",
    "counter": "#5f3824",
    "counter_top": "#85502f",
    "counter_panel": "#432719",
    "door": "#75472b",
    "door_glass": "#c4ddf0",
    "rug": "#16536b",
    "rug_trim": "#f0b94a",
    "rug_pattern": "#0e394b",
    "shadow": "#2e1b11",
    "shadow_opacity": "0.18",
    "bowl": "#d94e4e",
    "bowl_inner": "#a92e3b",
    "kibble": "#d69a4a",
    "lamp_shade": "#d8524e",
    "lamp_glow_opacity": "0",
    "beam_opacity": "0.16",
    "stars_opacity": "0",
    "moon_opacity": "0",
    "cloud_opacity": "0.9",
    "eye_glow_opacity": "0",
    "firefly_opacity": "0",
    "text": "#3d2417",
    "room_dim_opacity": "0",
}

NIGHT = {
    **DAY,
    "wall": "#ccb99a",
    "wainscot": "#96744f",
    "wainscot_trim": "#624a31",
    "floor": "#633b26",
    "plank": "#432719",
    "window_frame": "#3e2a1d",
    "shelf": "#603a24",
    "shelf_bracket": "#3f2618",
    "sign_board": "#52311f",
    "sign_trim": "#d7a23f",
    "sign_text": "#fff0ce",
    "chalk_board": "#102b38",
    "chalk_text": "#fff0ce",
    "counter": "#4b2b1c",
    "counter_top": "#734329",
    "counter_panel": "#321d14",
    "door": "#583621",
    "rug": "#0f4359",
    "rug_trim": "#e7ad42",
    "rug_pattern": "#082d3e",
    "shadow_opacity": "0.34",
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
    "text": "#fff0d1",
    "room_dim_opacity": "0.03",
}
