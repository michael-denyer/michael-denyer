from pathlib import Path

from defusedxml import ElementTree as ET

from commit_cafe.render import STATIONARY_SLOTS, render
from commit_cafe.state import CafeState, RepoCat

GOLDEN = Path(__file__).parent / "golden"


def _top_shelf_pair(busy_state: CafeState) -> CafeState:
    return busy_state.model_copy(
        update={
            "cats": [
                RepoCat(
                    name="michael-denyer",
                    stars=1,
                    last_commit_hash="aaaaaaa",
                    last_commit_age_hours=1000.0,
                ),
                RepoCat(
                    name="pyLocusZoom",
                    stars=1,
                    last_commit_hash="bbbbbbb",
                    last_commit_age_hours=1000.0,
                ),
            ],
            "open_prs": [],
        }
    )


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
    svg = render(busy_state, "day")
    assert 'data-commit="a3f9c21"' in svg
    assert ">a3f9c21<" not in svg


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


def test_stationary_cats_use_unique_display_zones(busy_state):
    # pyLocusZoom (2h) -> CHASE; code-review-graph (20h) -> ALERT;
    # numpy-mkl (48h) -> SIT (digest%2==0); jamma (50h) -> SIT (digest%2==0)
    state = busy_state.model_copy(
        update={
            "cats": [
                RepoCat(
                    name="pyLocusZoom",
                    stars=1,
                    last_commit_hash="aaaaaaa",
                    last_commit_age_hours=2.0,
                ),
                RepoCat(
                    name="code-review-graph",
                    stars=1,
                    last_commit_hash="bbbbbbb",
                    last_commit_age_hours=20.0,
                ),
                RepoCat(
                    name="numpy-mkl",
                    stars=1,
                    last_commit_hash="ccccccc",
                    last_commit_age_hours=48.0,
                ),
                RepoCat(
                    name="jamma", stars=1, last_commit_hash="ddddddd", last_commit_age_hours=50.0
                ),
            ]
        }
    )
    svg = render(state, "day")
    body_anchors = [
        (x, y) for x, y in STATIONARY_SLOTS if f'<g transform="translate({x} {y}) scale(' in svg
    ]
    assert len(body_anchors) == len(state.cats) - 1
    assert len(body_anchors) == len(set(body_anchors))


def test_five_stationary_cats_fill_display_zones(busy_state):
    sleepy = [
        RepoCat(
            name=f"old-repo-{i}", stars=1, last_commit_hash="abc1234", last_commit_age_hours=1000.0
        )
        for i in range(5)
    ]
    state = busy_state.model_copy(update={"cats": sleepy, "open_prs": []})
    svg = render(state, "day")
    for x, y in STATIONARY_SLOTS:
        assert f"translate({x} {y}) scale(" in svg


def test_visible_repositories_get_distinct_coats(busy_state):
    state = _top_shelf_pair(busy_state)
    root = ET.fromstring(render(state, "day"))
    coat_colors = []
    for x, y in STATIONARY_SLOTS[:2]:
        transform_prefix = f"translate({x} {y}) scale("
        cat_group = next(
            element
            for element in root.iter()
            if element.attrib.get("transform", "").startswith(transform_prefix)
        )
        coat_colors.append(
            {
                element.attrib["fill"]
                for element in cat_group.iter()
                if element.attrib.get("fill", "").startswith("#")
            }
        )

    assert coat_colors[0] != coat_colors[1]


def test_top_shelf_nameplates_do_not_overlap(busy_state):
    state = _top_shelf_pair(busy_state)
    root = ET.fromstring(render(state, "day"))

    boxes = []
    for name in ("michael-denyer", "pyLocusZoom"):
        sign_group = next(
            element
            for element in root.iter()
            if element.attrib.get("transform", "").startswith("translate(")
            and any(descendant.text == name for descendant in element.iter())
        )
        x, y = map(float, sign_group.attrib["transform"][10:-1].split())
        board = next(
            descendant for descendant in sign_group.iter() if descendant.tag.endswith("rect")
        )
        boxes.append(
            (
                x + float(board.attrib["x"]),
                y + float(board.attrib["y"]),
                float(board.attrib["width"]),
                float(board.attrib["height"]),
            )
        )

    left, right = boxes
    horizontal_overlap = left[0] < right[0] + right[2] and right[0] < left[0] + left[2]
    vertical_overlap = left[1] < right[1] + right[3] and right[1] < left[1] + left[3]
    assert not (horizontal_overlap and vertical_overlap)


def test_activity_stage_has_dedicated_floor_space(busy_state):
    svg = render(busy_state, "day")
    assert "translate(310 544)" in svg  # centered runway
    assert "translate(600 674)" in svg  # chase-repo label beneath the rug
    assert "translate(1100 678)" in svg  # streak bowl clear of the chase
    assert "LIVE ACTIVITY" in svg
    assert '<rect x="24" y="14" width="194" height="34"' in svg
    assert "translate(170 640)" not in svg
    assert "translate(180 655)" not in svg


def test_golden_day(busy_state):
    assert render(busy_state, "day") == (GOLDEN / "cafe-day.svg").read_text()


def test_golden_night(busy_state):
    assert render(busy_state, "night") == (GOLDEN / "cafe-night.svg").read_text()


def test_starrier_cats_render_bigger(busy_state):
    svg = render(busy_state, "day")
    assert "scale(1." in svg or "scale(0." in svg


def test_broken_streak_turns_every_head(quiet_state):
    svg = render(quiet_state, "day")
    assert ">z<" not in svg  # nobody sleeps through a broken streak


def test_chalkboard_summarizes_live_cafe_state(busy_state):
    svg = render(busy_state, "day")
    assert "5 repo cats in residence" in svg
    assert "4 commits today" in svg
    assert "23-day streak" not in svg
    assert "serving code since" not in svg


def test_chalkboard_does_not_duplicate_broken_streak(quiet_state):
    svg = render(quiet_state, "day")
    assert "0 commits today" in svg
    assert "streak needs a commit" not in svg
