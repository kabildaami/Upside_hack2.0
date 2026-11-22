"""Trusted clock and break decisions; MCP exposes same clock contract."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def current_time(tz: str = 'Africa/Tunis') -> dict:
    try: zone=ZoneInfo(tz)
    except (KeyError, ValueError): zone=ZoneInfo('Africa/Tunis'); tz='Africa/Tunis'
    now=datetime.now(zone)
    return {'iso':now.isoformat(timespec='seconds'),'date':now.date().isoformat(),
            'time':now.strftime('%H:%M:%S'),'timezone':tz,'weekday':now.strftime('%A')}


def break_due(active_seconds: int, threshold: int = 1800) -> bool:
    return active_seconds >= threshold
