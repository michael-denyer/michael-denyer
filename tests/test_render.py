from pathlib import Path

from defusedxml import ElementTree as ET

from commit_cafe.render import render

GOLDEN = Path(__file__).parent / "golden"


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


def test_alert_and_sit_cats_do_not_share_a_seat(busy_state):
    import re

    from commit_cafe.state import RepoCat

    # pyLocusZoom (2h) -> CHASE; code-review-graph (20h) -> ALERT;
    # numpy-mkl (48h) -> SIT (digest%2==0); jamma (50h) -> SIT (digest%2==0)
    state = busy_state.model_copy(
        update={
            "cats": [
                RepoCat(name="pyLocusZoom", stars=1, last_commit_hash="aaaaaaa",
                        last_commit_age_hours=2.0),
                RepoCat(name="code-review-graph", stars=1, last_commit_hash="bbbbbbb",
                        last_commit_age_hours=20.0),
                RepoCat(name="numpy-mkl", stars=1, last_commit_hash="ccccccc",
                        last_commit_age_hours=48.0),
                RepoCat(name="jamma", stars=1, last_commit_hash="ddddddd",
                        last_commit_age_hours=50.0),
            ]
        }
    )
    svg = render(state, "day")
    pattern = r'<g transform="translate\((\d+) (196|640|300|400|470|655|660)\)">'
    body_anchors = re.findall(pattern, svg)
    assert len(body_anchors) == len(set(body_anchors))


def test_sleep_overflow_goes_to_floor_line(busy_state):
    from commit_cafe.state import RepoCat

    sleepy = [
        RepoCat(name=f"old-repo-{i}", stars=1, last_commit_hash="abc1234",
                last_commit_age_hours=1000.0)
        for i in range(5)
    ]
    state = busy_state.model_copy(update={"cats": sleepy, "open_prs": []})
    svg = render(state, "day")
    assert "translate(1000 660)" in svg
    assert "translate(1115 660)" in svg


def test_golden_day(busy_state):
    assert render(busy_state, "day") == (GOLDEN / "cafe-day.svg").read_text()


def test_golden_night(busy_state):
    assert render(busy_state, "night") == (GOLDEN / "cafe-night.svg").read_text()
