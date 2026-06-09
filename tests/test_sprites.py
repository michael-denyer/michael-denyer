from defusedxml import ElementTree as ET

from commit_cafe.palette import coat_for
from commit_cafe.sprites import cat_alert, cat_loaf, cat_sit, cat_sleep, name_sign


def wrap(fragment: str) -> object:
    return ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{fragment}</svg>')


COAT = coat_for("pyLocusZoom")


def test_stationary_cats_are_valid_xml():
    for fn in (cat_sit, cat_loaf, cat_sleep, cat_alert):
        wrap(fn(COAT, phase=0.3, eye_glow_opacity="0"))


def test_cats_animate():
    svg = cat_sit(COAT, phase=0.0, eye_glow_opacity="0")
    assert "animateTransform" in svg


def test_sleeping_cat_has_zzz():
    svg = cat_sleep(COAT, phase=0.0, eye_glow_opacity="0")
    assert svg.count(">z<") == 3


def test_name_sign_contains_text():
    sign = name_sign("pyLocusZoom", board="#8a5f3c", trim="#6e4a2e", text_color="#fff")
    assert "pyLocusZoom" in sign


def test_name_sign_escapes_markup():
    svg = name_sign("a&b<c", board="#8a5f3c", trim="#6e4a2e", text_color="#fff")
    wrap(svg)
    assert "a&amp;b&lt;c" in svg


def test_phase_staggers_animation_timing():
    a = cat_sit(COAT, phase=0.0, eye_glow_opacity="0")
    b = cat_sit(COAT, phase=0.5, eye_glow_opacity="0")
    assert a != b
