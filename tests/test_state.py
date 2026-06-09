from datetime import UTC, datetime

from commit_cafe.state import CafeState, Pose, PrInfo, RepoCat, assign_poses


def cat(name: str, age_hours: float, stars: int = 5) -> RepoCat:
    return RepoCat(
        name=name, stars=stars, last_commit_hash="a3f9c21", last_commit_age_hours=age_hours
    )


def test_most_recent_under_24h_chases():
    poses = assign_poses([cat("a", 2.0), cat("b", 10.0), cat("c", 400.0)])
    assert poses == [Pose.CHASE, Pose.ALERT, Pose.SLEEP]


def test_exactly_24h_is_not_chasing():
    poses = assign_poses([cat("a", 24.0)])
    assert poses[0] in (Pose.SIT, Pose.LOAF)


def test_under_14_days_sits_or_loafs():
    poses = assign_poses([cat("a", 25.0), cat("b", 13 * 24.0)])
    assert all(p in (Pose.SIT, Pose.LOAF) for p in poses)


def test_exactly_14_days_sleeps():
    assert assign_poses([cat("a", 14 * 24.0)]) == [Pose.SLEEP]


def test_sit_loaf_choice_is_deterministic_per_name():
    first = assign_poses([cat("pyLocusZoom", 48.0)])
    second = assign_poses([cat("pyLocusZoom", 48.0)])
    assert first == second


def test_cafe_state_roundtrips_json():
    state = CafeState(
        username="michael-denyer",
        cats=[cat("a", 2.0)],
        open_prs=[PrInfo(number=87, repo="maid")],
        streak_days=23,
        commits_today=4,
        total_stars=412,
        est_year=2015,
        top_languages=[("Python", 0.61), ("R", 0.2)],
        rendered_at=datetime(2026, 6, 9, 12, 0, tzinfo=UTC),
    )
    assert CafeState.model_validate_json(state.model_dump_json()) == state
