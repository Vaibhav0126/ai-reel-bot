"""
When should today's Short go live?

Uploads are private with a scheduled `publishAt`, so there is always a review
window between "the bot uploaded it" and "the world can see it". The publish
time is picked for the target audience's timezone, not the machine's: the old
schedule posted at 1pm/7pm Japan time, which is 11pm/5am on the US east coast.

Pure functions only (no network), so they are unit-tested.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def next_publish_time(
    now_utc: datetime,
    tz_name: str = "America/New_York",
    hour: int = 12,
    min_lead_hours: float = 6.0,
) -> datetime:
    """Next `hour`:00 local time in `tz_name` that is at least `min_lead_hours` away.

    Returns an aware UTC datetime. DST is handled by zoneinfo, so 12:00 New York
    stays 12:00 New York all year.
    """
    if now_utc.tzinfo is None:
        raise ValueError("now_utc must be timezone-aware")
    if not 0 <= hour <= 23:
        raise ValueError(f"hour out of range: {hour}")

    tz = ZoneInfo(tz_name)
    local_now = now_utc.astimezone(tz)
    earliest = now_utc + timedelta(hours=min_lead_hours)

    for day_offset in range(0, 3):
        day = (local_now + timedelta(days=day_offset)).date()
        candidate = datetime(day.year, day.month, day.day, hour, 0, tzinfo=tz)
        if candidate.astimezone(timezone.utc) >= earliest:
            return candidate.astimezone(timezone.utc)
    raise RuntimeError("could not find a publish slot")  # unreachable for sane inputs


def to_rfc3339(dt: datetime) -> str:
    """Format for the YouTube Data API `status.publishAt` field."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
