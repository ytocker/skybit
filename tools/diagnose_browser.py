#!/usr/bin/env python3
"""Headless-browser diagnostic for the deployed Skybit leaderboard.

Loads `https://ytocker.github.io/skybit/`, captures every console message
and uncaught exception, waits for pygbag to boot, then drives the JS
bridge directly:
  - window.openNameEntry / window.__sk presence
  - window.__sk("fetch") + poll fetch_done up to 15 s
  - the boot-time `[skybit/lb]` console lines we ship from inject_theme.py

Output is markdown for posting to issue #2.

Requires `playwright` and `playwright install chromium` (the workflow
takes care of both).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

DEPLOYED_URL = os.environ.get(
    "DEPLOYED_URL", "https://ytocker.github.io/skybit/"
)
# Pygbag waits on its UME (User-Media-Engagement) gate before starting
# the Python interpreter, so a headless visit alone never executes any
# Python. We satisfy the gate explicitly below, then wait long enough
# for `main.py` to import and the startup leaderboard probe to fire.
WAIT_BOOT_S = 45
BRIDGE_POLL_S = 15


async def main() -> int:
    from playwright.async_api import async_playwright

    print("## Skybit deployed-page browser diagnostic\n")
    print(f"- target: `{DEPLOYED_URL}`\n")

    console_lines: list[str] = []
    page_errors: list[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()

        page.on("console",     lambda m: console_lines.append(f"[{m.type}] {m.text}"))
        page.on("pageerror",   lambda e: page_errors.append(str(e)))

        await page.goto(DEPLOYED_URL, wait_until="domcontentloaded", timeout=30_000)

        # Wait briefly for the bridge IIFE + overlay to render.
        await page.wait_for_timeout(3_000)

        # Satisfy pygbag's UME gate so the Python interpreter actually
        # starts. Two paths, run both in case the overlay isn't ready:
        #   1. set window.MM.UME = true (the documented escape)
        #   2. dispatch a real click on the overlay to fire its
        #      dismiss handler, which also sets MM.UME and forwards a
        #      click to the canvas.
        try:
            await page.evaluate(
                """() => {
                    try { if (window.MM) window.MM.UME = true; } catch (_) {}
                    const ov = document.getElementById('skybit-loading');
                    if (ov) ov.click();
                    const cv = document.getElementById('canvas');
                    if (cv) cv.dispatchEvent(new MouseEvent('click', {bubbles:true,cancelable:true}));
                }"""
            )
        except Exception as e:
            print(f"- UME-unlock attempt threw: `{e}`")

        # Now wait for pygbag to finish loading + Python main.py to run
        # the App init + the startup leaderboard probe to log.
        await page.wait_for_timeout(WAIT_BOOT_S * 1000)

        # Inspect the bridge state.
        bridge_state = await page.evaluate(
            """() => ({
                hasOpenNameEntry: typeof window.openNameEntry === 'function',
                hasSk:            typeof window.__sk === 'function',
                hasMM:            typeof window.MM !== 'undefined',
                pygbagModName:    (typeof window.MM !== 'undefined' && window.MM && window.MM.name) || null,
            })"""
        )

        # If __sk is wired, fire a fetch and poll for fetch_done.
        fetch_outcome = "(skipped — __sk not present)"
        rows_returned: int | None = None
        if bridge_state.get("hasSk"):
            try:
                await page.evaluate("() => window.__sk('fetch')")
                # Poll fetch_done up to BRIDGE_POLL_S seconds.
                for _ in range(BRIDGE_POLL_S * 4):
                    v = await page.evaluate(
                        "() => { const r = window.__sk('fetch_done'); "
                        "return r === null ? null : (Array.isArray(r) ? "
                        "{ rows: r, len: r.length } : { weird: typeof r }); }"
                    )
                    if v is not None:
                        if "rows" in v:
                            rows_returned = v["len"]
                            fetch_outcome = f"fetch_done returned **{v['len']} rows**"
                            if v["len"]:
                                fetch_outcome += f" (first: `{json.dumps(v['rows'][0])[:80]}`)"
                        else:
                            fetch_outcome = f"fetch_done returned unexpected: `{v}`"
                        break
                    await page.wait_for_timeout(250)
                else:
                    fetch_outcome = (
                        f"fetch_done stayed null for the whole {BRIDGE_POLL_S} s "
                        "poll window — doFetch() never assigned a value"
                    )
            except Exception as e:
                fetch_outcome = f"raised `{type(e).__name__}: {e}`"

        # Also read the fetch_error string the dispatcher exposes.
        fetch_error = ""
        if bridge_state.get("hasSk"):
            try:
                fetch_error = await page.evaluate(
                    "() => { try { return String(window.__sk('fetch_error') || ''); } "
                    "catch (_) { return ''; } }"
                )
            except Exception:
                pass

        await browser.close()

    print("### Bridge state\n")
    for k, v in bridge_state.items():
        print(f"- `{k}`: **{v}**")

    print(f"\n### __sk('fetch') outcome\n\n- {fetch_outcome}")
    if fetch_error:
        print(f"- `__sk('fetch_error')` = `{fetch_error}`")

    print("\n### Console messages (captured)\n")
    if console_lines:
        for line in console_lines:
            print(f"- `{line[:300]}`")
    else:
        print("- (none — page never logged anything; bridge IIFE may not have run)")

    print("\n### Page errors (uncaught JS exceptions)\n")
    if page_errors:
        for err in page_errors:
            print(f"```\n{err[:600]}\n```")
    else:
        print("- (none)")

    print("\n### Verdict\n")
    if not bridge_state.get("hasOpenNameEntry"):
        print("❌ `window.openNameEntry` is not defined — the bridge IIFE either "
              "didn't run or threw before assignment. The page-errors section above "
              "should show why. **This breaks the Python `_resolve()` handshake**, "
              "so `fetch_top10()` returns `[]` without ever calling __sk.")
    elif not bridge_state.get("hasSk"):
        print("❌ `window.__sk` not defined despite openNameEntry. Inconsistent "
              "IIFE state — investigate ordering.")
    elif rows_returned is None:
        print("❌ `__sk('fetch')` ran but `fetch_done` never returned a value. "
              "doFetch() is throwing or never resolving.")
    elif rows_returned == 0:
        print("⚠️ Bridge works, but the browser-side fetch returned 0 rows — "
              "in stark contrast to the server-side CI fetch which returned 15. "
              "This points to either a CORS regression specific to certain headers, "
              "or a stale service-worker cached response.")
    else:
        print(f"✅ Browser-side fetch via the bridge returned **{rows_returned} rows**. "
              "The leaderboard *should* render. If the live game still shows empty, "
              "the bug is between `fetch_top10()`'s return and the scene render — "
              "likely a Python-side state issue.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
