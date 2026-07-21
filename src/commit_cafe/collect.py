"""Fetch GitHub activity and normalize it into a CafeState."""

import time
from datetime import UTC, date, datetime, timedelta
from typing import Any

import httpx
from loguru import logger

from commit_cafe.state import CafeState, PrInfo, RepoCat

API = "https://api.github.com"
ROSTER_SIZE = 5

TRANSIENT_GRAPHQL_ERRORS = {"RESOURCE_LIMITS_EXCEEDED"}
GRAPHQL_ATTEMPTS = 3
GRAPHQL_BACKOFF_SECONDS = 2.0

# An unbounded contributionsCollection spans a year, and resolving that many
# contributionDays costs more than the Actions GITHUB_TOKEN is allowed to spend:
# GitHub answers RESOURCE_LIMITS_EXCEEDED. Ask for a short window instead and
# walk further back only while the streak is still running.
CALENDAR_WINDOW_DAYS = 90
CALENDAR_WINDOWS = 5

CONTRIB_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


def _get(path: str, token: str, params: dict[str, Any] | None = None) -> Any:
    response = httpx.get(f"{API}{path}", headers=_headers(token), params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _post_graphql(query: str, variables: dict[str, Any], token: str) -> dict[str, Any]:
    response = httpx.post(
        f"{API}/graphql",
        headers=_headers(token),
        json={"query": query, "variables": variables},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def _is_transient(errors: list[dict[str, Any]] | None) -> bool:
    return bool(errors) and all(e.get("type") in TRANSIENT_GRAPHQL_ERRORS for e in errors)


def _graphql(query: str, variables: dict[str, Any], token: str) -> dict[str, Any]:
    """POST a GraphQL query, retrying GitHub's transient resource-limit errors.

    Args:
        query: GraphQL document.
        variables: Query variables.
        token: GitHub token.

    Returns:
        The decoded response payload.

    Raises:
        RuntimeError: The response still carries errors after the last attempt.
    """
    payload = _post_graphql(query, variables, token)
    for attempt in range(1, GRAPHQL_ATTEMPTS):
        if not _is_transient(payload.get("errors")):
            break
        logger.warning(
            "transient GraphQL error on attempt {}/{}, retrying: {}",
            attempt,
            GRAPHQL_ATTEMPTS,
            payload["errors"],
        )
        time.sleep(GRAPHQL_BACKOFF_SECONDS * attempt)
        payload = _post_graphql(query, variables, token)
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload


def _streak(days: list[dict[str, Any]], today: date) -> tuple[int, int]:
    """Compute current streak and today's commit count.

    A zero today doesn't break the streak yet — there's still time to commit.

    Args:
        days: List of dicts with "date" (ISO) and "contributionCount" keys.
        today: The reference date for "today".

    Returns:
        Tuple of (streak_days, commits_today).
    """
    by_date = {d["date"]: d["contributionCount"] for d in days}
    today_count = by_date.get(today.isoformat(), 0)
    streak = 0
    cursor = today if today_count > 0 else today.fromordinal(today.toordinal() - 1)
    while by_date.get(cursor.isoformat(), 0) > 0:
        streak += 1
        cursor = cursor.fromordinal(cursor.toordinal() - 1)
    return streak, today_count


def _calendar_window(username: str, token: str, start: date, end: date) -> list[dict[str, Any]]:
    payload = _graphql(
        CONTRIB_QUERY,
        {
            "login": username,
            "from": f"{start.isoformat()}T00:00:00Z",
            "to": f"{end.isoformat()}T23:59:59Z",
        },
        token,
    )
    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [day for week in weeks for day in week["contributionDays"]]


def _fetch_streak(username: str, token: str, today: date) -> tuple[int, int]:
    """Compute the contribution streak, reading the calendar a window at a time.

    Stops as soon as a fetched window opens on a day with no contributions: that
    zero proves the streak ended inside the days already in hand.

    Args:
        username: GitHub username.
        token: GitHub personal access token or OAuth token.
        today: The reference date for "today".

    Returns:
        Tuple of (streak_days, commits_today).
    """
    days: list[dict[str, Any]] = []
    end = today
    for _ in range(CALENDAR_WINDOWS):
        start = end - timedelta(days=CALENDAR_WINDOW_DAYS - 1)
        window = _calendar_window(username, token, start, end)
        days.extend(window)
        if min(window, key=lambda day: day["date"])["contributionCount"] == 0:
            break
        end = start - timedelta(days=1)
    return _streak(days, today)


def fetch_state(username: str, token: str) -> CafeState:
    """Fetch GitHub activity for a user and return a CafeState.

    Args:
        username: GitHub username.
        token: GitHub personal access token or OAuth token.

    Returns:
        Populated CafeState ready for rendering.
    """
    now = datetime.now(UTC)
    repos = _get(f"/users/{username}/repos", token, params={"sort": "pushed", "per_page": 100})
    public = [r for r in repos if not r["fork"] and not r["private"]]
    roster = public[:ROSTER_SIZE]

    cats: list[RepoCat] = []
    lang_totals: dict[str, int] = {}
    for repo in roster:
        commits = _get(f"/repos/{username}/{repo['name']}/commits", token, params={"per_page": 1})
        if not commits:
            raise RuntimeError(f"repo {repo['name']} has no commits; cannot place it in the cafe")
        committed = datetime.fromisoformat(
            commits[0]["commit"]["committer"]["date"].replace("Z", "+00:00")
        )
        cats.append(
            RepoCat(
                name=repo["name"],
                stars=repo["stargazers_count"],
                last_commit_hash=commits[0]["sha"][:7],
                last_commit_age_hours=(now - committed).total_seconds() / 3600,
            )
        )
        for lang, size in _get(f"/repos/{username}/{repo['name']}/languages", token).items():
            lang_totals[lang] = lang_totals.get(lang, 0) + size

    total = sum(lang_totals.values()) or 1
    top_languages = sorted(
        ((lang, size / total) for lang, size in lang_totals.items()),
        key=lambda pair: -pair[1],
    )[:5]

    search = _get(
        "/search/issues", token, params={"q": f"is:pr is:open user:{username}", "per_page": 30}
    )
    open_prs = [
        PrInfo(number=item["number"], repo=item["repository_url"].rsplit("/", 1)[-1])
        for item in sorted(search["items"], key=lambda item: item["created_at"])
    ]

    streak_days, commits_today = _fetch_streak(username, token, now.date())

    user = _get(f"/users/{username}", token)
    state = CafeState(
        username=username,
        cats=cats,
        open_prs=open_prs,
        streak_days=streak_days,
        commits_today=commits_today,
        total_stars=sum(r["stargazers_count"] for r in public),
        est_year=int(user["created_at"][:4]),
        top_languages=top_languages,
        rendered_at=now,
    )
    logger.info(
        "fetched cafe state: {} cats, {} open PRs, streak {}", len(cats), len(open_prs), streak_days
    )
    return state
