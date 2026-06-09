from defusedxml import ElementTree as ET

from commit_cafe.render import render


def test_renders_valid_svg_both_modes(busy_state):
    for mode in ("day", "night"):
        root = ET.fromstring(render(busy_state, mode))
        assert root.tag.endswith("svg")


def test_no_scripts_or_external_refs(busy_state):
    svg = render(busy_state, "day")
    assert "<script" not in svg
    assert "http://" not in svg.replace("http://www.w3.org/", "")
    assert "https://" not in svg


def test_every_cat_gets_a_sign(busy_state):
    svg = render(busy_state, "day")
    for cat in busy_state.cats:
        assert cat.name in svg


def test_chaser_yarn_carries_hash(busy_state):
    assert "a3f9c21" in render(busy_state, "day")


def test_pr_dog_present_when_open_prs(busy_state, quiet_state):
    assert "PR #87" in render(busy_state, "day")
    assert "+1 waiting" in render(busy_state, "day")
    assert "deliveries welcome" in render(quiet_state, "day")


def test_quiet_state_has_no_yarn_chase(quiet_state):
    assert "animateMotion" not in render(quiet_state, "day")


def test_empty_bowl_when_streak_broken(quiet_state):
    assert "bowl empty" in render(quiet_state, "day")


def test_under_250kb(busy_state):
    for mode in ("day", "night"):
        assert len(render(busy_state, mode).encode()) < 250_000
