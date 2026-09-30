import json
from pathlib import Path

import pytest
from defusedxml import ElementTree

from commit_cafe.banner import render_banner
from commit_cafe.cli import main


def test_cli_renders_both_variants_from_state(tmp_path):
    exit_code = main(
        ["render", "--state", "tests/fixtures/cafe_state_busy.json", "--out", str(tmp_path)]
    )
    assert exit_code == 0
    for mode in ("day", "night"):
        svg = (tmp_path / f"cafe-{mode}.svg").read_text()
        assert svg.startswith("<svg")


def test_cli_errors_without_inputs():
    assert main(["render"]) == 1


@pytest.mark.parametrize("total_stars", [0, 412, 12345])
def test_cli_banner_uses_total_stars_not_just_displayed_cats(tmp_path, total_stars):
    state = json.loads(Path("tests/fixtures/cafe_state_busy.json").read_text())
    state["total_stars"] = total_stars
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state))
    out = tmp_path / "out"

    assert (
        main(
            [
                "render",
                "--state",
                str(state_path),
                "--out",
                str(out),
                "--banner-templates",
                "images",
            ]
        )
        == 0
    )

    for mode in ("day", "night"):
        svg = (out / f"profile-banner-{mode}.svg").read_text()
        root = ElementTree.fromstring(svg)
        count = root.find(".//*[@id='total-stars']")
        assert count is not None
        assert count.text == f"{total_stars:,} repo stars"
        assert f"{total_stars:,} repo stars" in root.find("{http://www.w3.org/2000/svg}desc").text
        assert "<!--total-stars-->" not in svg
        assert (out / f"cafe-{mode}.svg").exists()


def test_banner_rejects_missing_star_marker():
    with pytest.raises(ValueError, match="missing the total-stars marker"):
        render_banner("<svg/>", 412)
