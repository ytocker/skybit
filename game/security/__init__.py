"""Skybit security module.

Centralizes every security-relevant capability the game uses: input
sanitization, rate limiting, run integrity (HMAC chain + anti-cheat
trajectory stats), local-storage tamper detection, anomaly events,
and privacy controls.

The split is deliberate — keep the existing game files (leaderboard,
play_log, world, scenes) thin and have them call into here. That way
the threat surface is auditable in one folder.

Design constraints
------------------
* Must run BOTH natively (CPython 3.11+) AND in pygbag/Emscripten WASM.
  Avoid imports that pygbag chokes on; prefer stdlib hmac/hashlib.
* Must NEVER raise into the game loop. Every public entry point catches
  and degrades gracefully — better to silently emit a security_event
  than crash a player's run.
* Defense in depth: the same checks run client-side (UX, fast feedback)
  AND server-side (Supabase RPC, see supabase/schema.sql). Client-side
  is bypassable; server-side is the authority.
"""
SCHEMA_V = 1

from .crypto import sign, verify, get_build_secret           # noqa: F401
from .sanitize import sanitize_name, is_clean                # noqa: F401
from .ratelimit import (                                     # noqa: F401
    can_submit_score, record_submission, can_refresh_leaderboard,
    telemetry_dedup_key,
)
from .integrity import RunRecorder, SignedRun                # noqa: F401
from .events import emit, recent, SecurityEvent              # noqa: F401
from .privacy import (                                       # noqa: F401
    telemetry_enabled, set_telemetry, rotate_device_id,
    clear_all_local_data, gdpr_notice_shown, mark_gdpr_notice_shown,
)
