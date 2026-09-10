#!/usr/bin/env python3
"""Run from CI with SUPABASE_URL / SUPABASE_ANON_KEY in env. Performs the
exact same GET the deployed JS does and writes a markdown diagnostic to
stdout. The CI workflow then posts that to a tracking issue so the
result is readable without leaking the anon key in raw form.

Three checks:
  1. Server-to-server fetch (bypasses CORS) — does the data exist + are
     creds valid?
  2. Browser-style CORS preflight (OPTIONS with Origin header) — is the
     deployed origin allowed by Supabase?
  3. Deployed HTML inspection — did the build substitute __SB_URL__ /
     __SB_KEY__ into the live page?

Run locally too: `SUPABASE_URL=... SUPABASE_ANON_KEY=... python tools/diagnose_supabase.py`.
"""
from __future__ import annotations

import json
import os
import re
import sys
from urllib import error, request


DEPLOYED_URL = os.environ.get(
    "DEPLOYED_URL", "https://ytocker.github.io/skybit/"
)


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


def _origin(url: str) -> str:
    return _host(url).rstrip("/")


def check_direct(sb_url: str, sb_key: str) -> int:
    print("### 1. Direct fetch (server-to-server, bypasses CORS)\n")
    target = sb_url.rstrip("/") + "/rest/v1/scores?select=name,score&order=score.desc&limit=200"
    req = request.Request(
        target,
        headers={
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=15) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"- **HTTP error: {e.code} {e.reason}**")
        print("\n```\n" + body[:600] + "\n```")
        return 0
    except Exception as e:
        print(f"- **Network error:** `{type(e).__name__}: {e}`")
        return 0
    try:
        rows = json.loads(body)
    except Exception:
        rows = None
    if isinstance(rows, list):
        print(f"- HTTP **{status}** — rows returned: **{len(rows)}**")
        if rows:
            sample = rows[0]
            nm = str(sample.get("name", ""))[:10]
            sc = sample.get("score", "?")
            print(f"- top row: `name={nm!r}, score={sc}`")
        return len(rows)
    print(f"- HTTP {status}, body not JSON")
    print("\n```\n" + body[:400] + "\n```")
    return 0


def check_cors(sb_url: str, sb_key: str, origin: str) -> None:
    print(f"\n### 2. CORS preflight as if from `{origin}`\n")
    target = sb_url.rstrip("/") + "/rest/v1/scores?select=name,score&limit=1"
    # OPTIONS preflight that the browser would issue before our GET.
    # The browser preflight is triggered because we send custom headers
    # (apikey, Authorization).
    req = request.Request(
        target,
        method="OPTIONS",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "apikey,authorization",
        },
    )
    try:
        with request.urlopen(req, timeout=15) as resp:
            status = resp.status
            allow_origin = resp.headers.get("Access-Control-Allow-Origin", "(none)")
            allow_headers = resp.headers.get("Access-Control-Allow-Headers", "(none)")
            allow_methods = resp.headers.get("Access-Control-Allow-Methods", "(none)")
    except error.HTTPError as e:
        print(f"- preflight HTTP **{e.code} {e.reason}**")
        return
    except Exception as e:
        print(f"- preflight network error: `{type(e).__name__}: {e}`")
        return
    print(f"- preflight HTTP **{status}**")
    print(f"- `Access-Control-Allow-Origin: {allow_origin}`")
    print(f"- `Access-Control-Allow-Headers: {allow_headers[:120]}`")
    print(f"- `Access-Control-Allow-Methods: {allow_methods[:120]}`")
    if allow_origin == "*" or origin in allow_origin:
        print(f"- ✅ origin `{origin}` is allowed.")
    else:
        print(f"- ❌ origin `{origin}` is NOT allowed by Supabase CORS — this is the bug.")

    # Also follow with a real GET that includes the Origin header. The
    # response Access-Control-Allow-Origin should still match.
    get_req = request.Request(
        target,
        headers={
            "Origin": origin,
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
        },
    )
    try:
        with request.urlopen(get_req, timeout=15) as resp:
            ao = resp.headers.get("Access-Control-Allow-Origin", "(none)")
            print(f"- actual GET with Origin → status {resp.status}, "
                  f"Access-Control-Allow-Origin: `{ao}`")
    except error.HTTPError as e:
        ao = e.headers.get("Access-Control-Allow-Origin", "(none)")
        print(f"- actual GET with Origin → status {e.code}, "
              f"Access-Control-Allow-Origin: `{ao}`")
    except Exception as e:
        print(f"- actual GET error: `{type(e).__name__}: {e}`")


def check_deployed_html(deployed_url: str) -> None:
    print(f"\n### 3. Deployed HTML inspection (`{deployed_url}`)\n")
    try:
        req = request.Request(
            deployed_url,
            headers={"User-Agent": "skybit-diag/1.0", "Accept": "text/html"},
        )
        with request.urlopen(req, timeout=15) as resp:
            status = resp.status
            html = resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        print(f"- HTTP {e.code} fetching deployed HTML: cannot inspect substitution.")
        return
    except Exception as e:
        print(f"- network error: `{type(e).__name__}: {e}`")
        return
    print(f"- HTTP {status}, html length: {len(html)} bytes")

    # Look for the bridge-IIFE signature.
    sb_url_placeholder = "__SB_URL__" in html
    sb_key_placeholder = "__SB_KEY__" in html
    print(f"- `__SB_URL__` placeholder still in HTML: **{sb_url_placeholder}**")
    print(f"- `__SB_KEY__` placeholder still in HTML: **{sb_key_placeholder}**")

    # Try to locate the assigned values via the bridge.
    m_url = re.search(r'var\s+a\s*=\s*"([^"]*)"', html)
    m_key = re.search(r'var\s+b\s*=\s*"([^"]*)"', html)
    if m_url:
        v = m_url.group(1)
        looks_real = "supabase" in v and not v.startswith("__SB_")
        print(f"- bridge `var a` looks like a real URL: **{looks_real}** "
              f"(host=`{_host(v) if looks_real else v[:30]}`)")
    else:
        print("- bridge `var a` not found")
    if m_key:
        v = m_key.group(1)
        looks_real = bool(v) and not v.startswith("__SB_") and "." in v
        print(f"- bridge `var b` looks like a JWT: **{looks_real}** (len={len(v)})")
    else:
        print("- bridge `var b` not found")


def main() -> int:
    sb_url = os.environ.get("SUPABASE_URL", "").strip()
    sb_key = os.environ.get("SUPABASE_ANON_KEY", "").strip()

    print("## Supabase leaderboard diagnostic\n")
    print(f"- url host: `{_host(sb_url)}`")
    print(f"- url present: {bool(sb_url)}; key present: {bool(sb_key)} "
          f"(key fingerprint: `{_mask(sb_key)}`)")
    print(f"- deployed URL under test: `{DEPLOYED_URL}`\n")

    if not sb_url or not sb_key:
        print("\n**Verdict:** SUPABASE_URL or SUPABASE_ANON_KEY missing in this CI context.")
        print("Likely cause: secrets are environment-scoped, not repository-scoped.")
        return 0

    rows = check_direct(sb_url, sb_key)
    check_cors(sb_url, sb_key, _origin(DEPLOYED_URL))
    check_deployed_html(DEPLOYED_URL)

    print("\n### Verdict\n")
    if rows == 0:
        print("Database returned 0 rows — fix has to be on Supabase (RLS/grants/empty project).")
    else:
        print(f"Database has **{rows} rows** and is reachable from CI. "
              "If the deployed site shows empty top-10, the cause is one of:")
        print("- CORS preflight in section 2 was rejected for the deployed origin")
        print("- Section 3 shows `__SB_URL__` / `__SB_KEY__` still as placeholders "
              "(build didn't substitute the secrets into the deployed HTML)")
        print("- Section 3 shows real values but a JS exception in the bridge "
              "prevents the fetch firing (would need a browser-side console line "
              "to confirm)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
