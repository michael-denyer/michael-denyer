"""Data model for a cafe scene and the activity->pose rules."""

import hashlib
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

CHASE_MAX_HOURS = 24.0
AWAKE_MAX_HOURS = 14 * 24.0


class Pose(StrEnum):
    CHASE = "chase"
    ALERT = "alert"
    SIT = "sit"
    LOAF = "loaf"
    SLEEP = "sleep"


class RepoCat(BaseModel):
    name: str
    stars: int
    last_commit_hash: str
    last_commit_age_hours: float


class PrInfo(BaseModel):
    number: int
    repo: str


class CafeState(BaseModel):
    username: str
    cats: list[RepoCat]
    open_prs: list[PrInfo]
    streak_days: int
    commits_today: int
    total_stars: int
    est_year: int
    top_languages: list[tuple[str, float]]
    rendered_at: datetime


def _name_digest(name: str) -> int:
    return int.from_bytes(hashlib.sha1(name.encode()).digest()[:4], "big")


def assign_poses(cats: list[RepoCat]) -> list[Pose]:
    """Map commit recency to a pose per cat (cats arrive ordered by recency).

    The single most recent cat under 24h chases the yarn; other sub-24h cats
    sit alert watching it. Under 14 days they sit or loaf (picked
    deterministically from the repo name so the scene is stable between
    renders); anything older sleeps.
    """
    poses: list[Pose] = []
    chaser_taken = False
    for c in cats:
        if c.last_commit_age_hours < CHASE_MAX_HOURS:
            poses.append(Pose.ALERT if chaser_taken else Pose.CHASE)
            chaser_taken = True
        elif c.last_commit_age_hours < AWAKE_MAX_HOURS:
            poses.append(Pose.SIT if _name_digest(c.name) % 2 == 0 else Pose.LOAF)
        else:
            poses.append(Pose.SLEEP)
    return poses
