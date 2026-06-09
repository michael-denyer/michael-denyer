from datetime import UTC, datetime, timedelta

import pytest

import commit_cafe.collect as collect
from commit_cafe.collect import _streak, fetch_state

NOW = datetime(2026, 6, 9, 14, 0, tzinfo=UTC)


def day(offset: int, count: int) -> dict:
    return {"date": (NOW.date() - timedelta(days=offset)).isoformat(), "contributionCount": count}


def test_streak_counts_consecutive_days():
    days = [day(3, 1), day(2, 2), day(1, 1), day(0, 4)]
    assert _streak(days, NOW.date()) == (4, 4)


def test_streak_zero_today_does_not_break_yesterdays_run():
    days = [day(2, 1), day(1, 1), day(0, 0)]
    assert _streak(days, NOW.date()) == (2, 0)


def test_streak_gap_resets():
    days = [day(3, 5), day(2, 0), day(1, 1), day(0, 1)]
    assert _streak(days, NOW.date()) == (2, 1)


@pytest.fixture
def fake_api(monkeypatch):
    def fake_get(path, token, params=None):
        if path == "/users/u/repos":
            return [
                {"name": "active", "fork": False, "private": False, "stargazers_count": 10},
                {"name": "a-fork", "fork": True, "private": False, "stargazers_count": 99},
                {"name": "old", "fork": False, "private": False, "stargazers_count": 5},
            ]
        if path.startswith("/repos/u/") and path.endswith("/commits"):
            return [
                {
                    "sha": "a3f9c21deadbeef",
                    "commit": {"committer": {"date": "2026-06-09T12:00:00Z"}},
                }
            ]
        if path.startswith("/repos/u/") and path.endswith("/languages"):
            return {"Python": 800, "R": 200}
        if path == "/search/issues":
            return {
                "items": [
                    {
                        "number": 87,
                        "repository_url": "https://api.github.com/repos/u/maid",
                        "created_at": "2026-06-01T00:00:00Z",
                    }
                ]
            }
        if path == "/users/u":
            return {"created_at": "2015-03-01T00:00:00Z"}
        raise AssertionError(f"unexpected path {path}")

    def fake_graphql(query, variables, token):
        # fetch_state computes the streak against the real clock, so these
        # calendar days must be anchored to the real today, not the fixed NOW
        real_today = datetime.now(UTC).date()

        def real_day(offset: int, count: int) -> dict:
            return {
                "date": (real_today - timedelta(days=offset)).isoformat(),
                "contributionCount": count,
            }

        return {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "weeks": [{"contributionDays": [real_day(1, 2), real_day(0, 3)]}]
                        }
                    }
                }
            }
        }

    monkeypatch.setattr(collect, "_get", fake_get)
    monkeypatch.setattr(collect, "_graphql", fake_graphql)


def test_fetch_state_assembles_cafe_state(fake_api):
    state = fetch_state("u", "tok")
    assert [c.name for c in state.cats] == ["active", "old"]  # fork excluded
    assert state.cats[0].last_commit_hash == "a3f9c21"
    assert state.open_prs[0].number == 87
    assert state.open_prs[0].repo == "maid"
    assert state.total_stars == 15  # forks excluded from star count too
    assert state.est_year == 2015
    assert state.top_languages[0][0] == "Python"
    assert 0.79 < state.top_languages[0][1] < 0.81
    assert state.streak_days == 2
    assert state.commits_today == 3
