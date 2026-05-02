#!/usr/bin/env python3
"""Run from CI with SUPABASE_URL / SUPABASE_ANON_KEY in env. Performs the
exact same GET the deployed JS does and writes a markdown diagnostic to
stdout. The CI workflow then posts that to a tracking issue so the
result is readable without leaking the anon key in raw form.

Run locally too: `SUPABASE_URL=... SUPABASE_ANON_KEY=... python tools/diagnose_supabase.py`.
"""
from __future__ import annotations

import json
import os
import sys
from urllib import error, request


def _mask(s: str, head: int = 8, tail: int = 4) -> str:
    if not s:
        return "(empty)"
    if len(s) <= head + tail + 3:
        return "***"
    return s[:head] + "…" + s[-tail:] + f" (len={len(s)})"


def _host(url: str) -> str:
    if not url:
        return "(empty)"
    try:
        from urllib.parse import urlparse
        p = urlparse(url)
        return f"{p.scheme}://{p.netloc}"
    except Exception:
        return "(unparsable)"


def main() -> int:
    sb_url = os.environ.get("SUPABASE_URL", "").strip()
    sb_key = os.environ.get("SUPABASE_ANON_KEY", "").strip()

    print("## Supabase leaderboard diagnostic\n")
    print(f"- url host: `{_host(sb_url)}`")
    print(f"- url present: {bool(sb_url)}; key present: {bool(sb_key)} (key fingerprint: `{_mask(sb_key)}`)")

    if not sb_url or not sb_key:
        print("\n**Verdict:** SUPABASE_URL or SUPABASE_ANON_KEY missing in this CI context.")
        print("Likely cause: secrets are environment-scoped, not repository-scoped.")
        return 0

    target = sb_url.rstrip("/") + "/rest/v1/scores?select=name,score&order=score.desc&limit=200"
    req = request.Request(
        target,
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Accept": "application/json",
        },
    )

    print(f"- GET `{target.replace(sb_url, _host(sb_url))}`")
    try:
        with request.urlopen(req, timeout=15) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"- **HTTP error: {e.code} {e.reason}**")
        print("\n```\n" + body[:800] + "\n```")
        if e.code == 401:
            print("\n**Verdict:** anon key is wrong/rotated, OR RLS is denying read for `anon` role.")
        elif e.code == 404:
            print("\n**Verdict:** project URL is wrong, OR the `scores` table doesn't exist in this project.")
        else:
            print(f"\n**Verdict:** server returned HTTP {e.code}.")
        return 0
    except Exception as e:
        print(f"- **Network error:** `{type(e).__name__}: {e}`")
        return 0

    print(f"- HTTP status: **{status}**, body length: {len(body)} bytes")

    try:
        rows = json.loads(body)
    except Exception:
        print("\nBody was not valid JSON:")
        print("\n```\n" + body[:800] + "\n```")
        return 0

    if not isinstance(rows, list):
        print(f"\nUnexpected JSON shape: `{type(rows).__name__}`")
        print("\n```json\n" + json.dumps(rows)[:800] + "\n```")
        return 0

    print(f"- rows returned: **{len(rows)}**")
    if rows:
        sample = rows[0]
        # Names are public anyway (rendered in the in-game leaderboard).
        # Truncate for safety.
        nm = str(sample.get("name", ""))[:10]
        sc = sample.get("score", "?")
        print(f"- top row: `name={nm!r}, score={sc}`")
        print("\n**Verdict:** ✅ leaderboard is reachable from CI — fetch is fine, "
              "any deployed-site emptiness is on the JS side or the deployed HTML "
              "is missing the substituted secret.")
    else:
        print("\n**Verdict:** ⚠️ HTTP 200 OK with **0 rows**.")
        print("\nClassic Supabase signature for one of these (in order of likelihood):")
        print("1. RLS enabled on `scores` with no SELECT policy permitting `anon` "
              "(or a restrictive policy that evaluates false).")
        print("2. The `anon` role lacks `GRANT SELECT ON public.scores`.")
        print("3. The table is genuinely empty in this project (no scores have been "
              "submitted to it yet — this is plausible if `SUPABASE_URL` points to "
              "a different project than the one Netlify wrote to).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
