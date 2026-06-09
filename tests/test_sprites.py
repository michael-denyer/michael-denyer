from defusedxml import ElementTree as ET

from commit_cafe.palette import DAY, NIGHT, coat_for
from commit_cafe.sprites import (
    bookshelf,
    bowl,
    cat_alert,
    cat_loaf,
    cat_sit,
    cat_sleep,
    chalkboard,
    dog_at_door,
    dust_motes,
    fireflies,
    lamp,
    name_sign,
    plant,
    steam,
    wall_clock,
    window,
)


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


def test_props_are_valid_xml():
    for fragment in (
        dog_at_door(87, more_count=2, palette=DAY),
        dog_at_door(None, more_count=0, palette=DAY),
        bowl(23, palette=DAY),
        bowl(0, palette=DAY),
        chalkboard(["4 commits today", "412 stars", "est. 2015"], palette=DAY),
        bookshelf([("Python", 0.61), ("R", 0.2), ("SQL", 0.19)], palette=DAY),
        wall_clock(14, 30, palette=DAY),
        window(palette=DAY),
        window(palette=NIGHT),
        plant(),
        lamp(palette=NIGHT),
        steam(),
        dust_motes(palette=DAY),
        fireflies(palette=NIGHT),
    ):
        wrap(fragment)


def test_dog_shows_pr_number():
    assert "PR #87" in dog_at_door(87, more_count=0, palette=DAY)
    assert "+2 waiting" in dog_at_door(87, more_count=2, palette=DAY)
    assert "deliveries welcome" in dog_at_door(None, more_count=0, palette=DAY)


def test_bowl_kibble_scales():
    full = bowl(30, palette=DAY)
    empty = bowl(0, palette=DAY)
    assert full.count("<circle") > empty.count("<circle")
    assert "23" not in empty


def test_bookshelf_spine_count_matches_languages():
    svg = bookshelf([("Python", 0.5), ("R", 0.5)], palette=DAY)
    assert svg.count('class="spine"') == 2


def test_clock_hands_reflect_time():
    assert wall_clock(3, 0, palette=DAY) != wall_clock(9, 0, palette=DAY)
