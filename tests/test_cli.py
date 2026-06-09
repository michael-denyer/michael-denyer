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
