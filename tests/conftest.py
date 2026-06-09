from datetime import UTC, datetime

import pytest

from commit_cafe.state import CafeState, PrInfo, RepoCat


@pytest.fixture
def busy_state() -> CafeState:
    return CafeState(
        username="michael-denyer",
        cats=[
            RepoCat(name="pyLocusZoom", stars=120, last_commit_hash="a3f9c21",
                    last_commit_age_hours=2.0),
            RepoCat(name="code-review-graph", stars=80, last_commit_hash="7be02dd",
                    last_commit_age_hours=20.0),
            RepoCat(name="maid", stars=60, last_commit_hash="f41c9a0",
                    last_commit_age_hours=72.0),
            RepoCat(name="memory-mcp", stars=30, last_commit_hash="03d77e1",
                    last_commit_age_hours=120.0),
            RepoCat(name="ministack", stars=12, last_commit_hash="c9821fb",
                    last_commit_age_hours=40 * 24.0),
        ],
        open_prs=[PrInfo(number=87, repo="maid"), PrInfo(number=91, repo="ministack")],
        streak_days=23,
        commits_today=4,
        total_stars=412,
        est_year=2015,
        top_languages=[("Python", 0.61), ("R", 0.18), ("SQL", 0.12), ("Shell", 0.09)],
        rendered_at=datetime(2026, 6, 9, 14, 30, tzinfo=UTC),
    )


@pytest.fixture
def quiet_state() -> CafeState:
    return CafeState(
        username="michael-denyer",
        cats=[
            RepoCat(name="pyLocusZoom", stars=120, last_commit_hash="a3f9c21",
                    last_commit_age_hours=30 * 24.0),
            RepoCat(name="maid", stars=60, last_commit_hash="f41c9a0",
                    last_commit_age_hours=60 * 24.0),
        ],
        open_prs=[],
        streak_days=0,
        commits_today=0,
        total_stars=412,
        est_year=2015,
        top_languages=[("Python", 1.0)],
        rendered_at=datetime(2026, 6, 9, 2, 0, tzinfo=UTC),
    )
