#!/usr/bin/env python3
"""
Post-process pygbag's generated build/web/index.html to inject:
  - Skybit dark-purple night-sky loading overlay
  - window.skyPlay() Web Audio synthesis (matches game/audio.py exactly)
"""
import os
import re
import sys
from pathlib import Path

src = Path("build/web/index.html")
if not src.exists():
    raise SystemExit("build/web/index.html not found — run pygbag first")

html = src.read_text(encoding="utf-8")

_SB_URL = os.environ.get("SUPABASE_URL", "")
_SB_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

# Track how many color/background replacements actually matched. Used by the
# post-write assertions below: a deploy where NONE of the loader colours
# were patched almost certainly means pygbag changed its template and the
# user will see the unthemed default progress bar (green rectangle, blue
# text) — which has been observed in production as a stuck-loading state.
_color_subs = 0

def _patch_re(pattern, replacement, html_in):
    global _color_subs
    new, n = re.subn(pattern, replacement, html_in)
    _color_subs += n
    return new

def _patch_str(needle, replacement, html_in):
    global _color_subs
    _color_subs += html_in.count(needle)
    return html_in.replace(needle, replacement)

# ── 1. Dark body + canvas background (CSS) ───────────────────────────────────
html = _patch_str("background-color:powderblue", "background-color:#0d0820", html)
# Inline style on <canvas> if present
html = re.sub(
    r'(<canvas\b[^>]*style=["\'])([^"\']*)',
    lambda m: m.group(1) + "background:#0d0820;" + m.group(2),
    html,
)

# ── 2. Patch embedded Python progress-bar colors ──────────────────────────────
# pygbag embeds custom_site() Python code as a comment inside a <script> tag.
# Use regex so spaces inside tuples don't break the match.
html = _patch_str('"#7f7f7f"', '"#0d0820"', html)                        # bg: gray → dark purple
html = _patch_re(r'\(\s*0\s*,\s*255\s*,\s*0\s*\)', '(240,192,64)', html)   # bar: green → gold
html = _patch_re(r'\(\s*10\s*,\s*10\s*,\s*10\s*\)', '(20,12,48)', html)    # track: near-black → deep purple
html = _patch_re(r',\s*True\s*,\s*"blue"\)', ', True, (240,192,64))', html)  # text: blue → gold
# Some pygbag versions name the bg color differently
html = _patch_str('"powderblue"', '"#0d0820"', html)
html = _patch_str("'powderblue'", "'#0d0820'", html)

# ── 2. Loading overlay HTML (injected right after <body>) ─────────────────────
OVERLAY = """
<div id="skybit-loading">
  <p class="skybit-title">SKYBIT</p>
  <p class="skybit-sub">Pocket Sky Flyer</p>
  <div id="skybit-btn" class="tap-btn">TAP &nbsp;&middot;&nbsp; CLICK &nbsp;&middot;&nbsp; SPACE</div>
  <div class="skybit-progress" aria-hidden="true">
    <div id="skybit-progress-fill" class="skybit-progress-fill"></div>
  </div>
  <p id="skybit-status" class="skybit-status"></p>
  <svg class="mountains" viewBox="0 0 1440 200" preserveAspectRatio="none"
       xmlns="http://www.w3.org/2000/svg">
    <path d="M0,200 L0,130 L60,70 L120,110 L200,40 L280,90 L360,20
             L440,75 L520,45 L600,100 L680,15 L760,80 L840,35 L920,95
             L1000,50 L1080,85 L1160,25 L1240,90 L1320,55 L1440,70 L1440,200 Z"
          fill="#0e1a0c" opacity="0.95"/>
    <path d="M0,200 L0,155 L80,125 L160,145 L240,108 L320,132 L400,95
             L480,128 L560,105 L640,135 L720,88 L800,120 L880,100 L960,130
             L1040,110 L1120,138 L1200,105 L1280,128 L1360,112 L1440,125 L1440,200 Z"
          fill="#0a1208" opacity="0.75"/>
  </svg>
</div>
"""
NAME_OVERLAY = """
<div id="name-overlay">
  <svg class="mountains" viewBox="0 0 1440 200" preserveAspectRatio="none"
       xmlns="http://www.w3.org/2000/svg">
    <path d="M0,200 L0,130 L60,70 L120,110 L200,40 L280,90 L360,20
             L440,75 L520,45 L600,100 L680,15 L760,80 L840,35 L920,95
             L1000,50 L1080,85 L1160,25 L1240,90 L1320,55 L1440,70 L1440,200 Z"
          fill="#0e1a0c" opacity="0.95"/>
    <path d="M0,200 L0,155 L80,125 L160,145 L240,108 L320,132 L400,95
             L480,128 L560,105 L640,135 L720,88 L800,120 L880,100 L960,130
             L1040,110 L1120,138 L1200,105 L1280,128 L1360,112 L1440,125 L1440,200 Z"
          fill="#0a1208" opacity="0.75"/>
  </svg>
  <svg class="ne-trophy" viewBox="0 0 60 72"
       xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M10 18 Q 3 18 3 26 Q 3 35 11 36" fill="none"
          stroke="#f0c040" stroke-width="3" stroke-linecap="round"/>
    <path d="M50 18 Q 57 18 57 26 Q 57 35 49 36" fill="none"
          stroke="#f0c040" stroke-width="3" stroke-linecap="round"/>
    <polygon points="9,14 51,14 47,42 13,42"
             fill="#f0c040" stroke="#8c5a08" stroke-width="1.2"/>
    <line x1="14" y1="16" x2="46" y2="16" stroke="#fff8c8" stroke-width="1.2"/>
    <rect x="27" y="42" width="6" height="11"
          fill="#f0c040" stroke="#8c5a08" stroke-width="1"/>
    <rect x="18" y="53" width="24" height="5"
          fill="#f0c040" stroke="#8c5a08" stroke-width="1"/>
    <rect x="14" y="58" width="32" height="5"
          fill="#f0c040" stroke="#8c5a08" stroke-width="1"/>
  </svg>
  <p class="ne-headline">You made it to the top 10!</p>
  <input id="name-input" type="text" inputmode="text"
         autocapitalize="characters" autocorrect="off" autocomplete="off"
         spellcheck="false" maxlength="10"
         placeholder="TYPE YOUR NAME…"/>
  <p id="name-counter">0 / 10</p>
  <button id="name-submit" class="ne-submit">SUBMIT</button>
  <button id="name-skip" class="ne-skip">SKIP</button>
</div>
"""
html = html.replace("<body>", "<body>\n" + OVERLAY + NAME_OVERLAY, 1)

# ── 3. CSS + JS injected before </body> ──────────────────────────────────────
INJECTION = """
<style>
/* ── Canvas base (shows behind pygame loading bar) ─── */
canvas { background: #0d0820 !important; }
body   { background: #0d0820 !important; }

/* ── Loading overlay ─────────────────────────────────
   Hardened: every pygbag template version has at one point shipped a
   `<div id="status">` or canvas at a high z-index that ends up over
   the user-facing splash. Force the Skybit overlay to win every
   stacking-context fight by pinning to the maximum reachable z-index
   and !important-ing display so a sibling rule can't toggle it off. */
#skybit-loading {
    position: fixed !important;
    inset: 0 !important;
    z-index: 2147483647 !important;
    background: linear-gradient(180deg, #060115 0%, #12082a 45%, #0c1022 100%) !important;
    display: flex !important;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    user-select: none;
    overflow: hidden;
    visibility: visible !important;
    opacity: 1;
    -webkit-tap-highlight-color: transparent;
}
.skybit-title { visibility: visible !important; opacity: 1 !important; }

/* Twinkling stars (added by JS) */
.star {
    position: absolute;
    background: #ffffff;
    border-radius: 50%;
    pointer-events: none;
    animation: twinkle var(--dur, 2s) ease-in-out infinite;
    animation-delay: var(--delay, 0s);
}
@keyframes twinkle {
    0%, 100% { opacity: 0.12; transform: scale(1.0); }
    50%       { opacity: 0.95; transform: scale(1.4); }
}

/* "SKYBIT" title */
.skybit-title {
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(54px, 14vw, 90px);
    font-weight: 900;
    letter-spacing: 8px;
    color: #f0c040;
    margin: 0;
    text-shadow:
        -3px  0   0 #a82010,
         3px  0   0 #a82010,
         0   -3px 0 #a82010,
         0    3px 0 #a82010,
         0    9px 8px rgba(0, 0, 0, 0.85);
    animation: float-title 3.4s ease-in-out infinite;
    pointer-events: none;
}
@keyframes float-title {
    0%, 100% { transform: translateY(0px);   }
    50%       { transform: translateY(-14px); }
}

/* Subtitle */
.skybit-sub {
    font-family: Arial, sans-serif;
    font-size: clamp(10px, 2.6vw, 14px);
    font-weight: 700;
    letter-spacing: 9px;
    color: #d8b855;
    margin: 14px 0 56px;
    opacity: 0.82;
    text-transform: uppercase;
    pointer-events: none;
}

/* TAP TO PLAY button */
.tap-btn {
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(13px, 3.6vw, 18px);
    font-weight: 900;
    letter-spacing: 4px;
    color: #ffffff;
    background: linear-gradient(180deg, #c84018 0%, #7e1c02 100%);
    border: 2px solid #e86828;
    border-radius: 60px;
    padding: 16px 52px;
    box-shadow:
        0 5px 30px rgba(200, 64, 20, 0.65),
        inset 0 1px 0 rgba(255, 255, 255, 0.18);
    animation: pulse-btn 1.8s ease-in-out infinite;
    pointer-events: none;
    white-space: nowrap;
}
@keyframes pulse-btn {
    0%, 100% { opacity: 0.70; transform: scale(1.00); }
    50%       { opacity: 1.00; transform: scale(1.07); }
}

/* Smooth themed progress bar (replaces pygbag's chunky default).
   Width is animated via CSS transition so each JS update glides
   instead of snapping. Time-based ease-out keeps motion alive
   while WASM downloads, then jumps to 100% on real boot. */
.skybit-progress {
    position: relative;
    width: clamp(180px, 56vw, 340px);
    height: 4px;
    margin: 22px 0 0;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 2px;
    overflow: hidden;
    pointer-events: none;
}
.skybit-progress-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #b88a2e 0%, #f0c040 50%, #fff0b0 100%);
    border-radius: inherit;
    transition: width 0.55s cubic-bezier(0.22, 1, 0.36, 1);
    box-shadow: 0 0 10px rgba(240, 192, 64, 0.55);
}
.skybit-progress-fill.skybit-progress-stalled {
    background: linear-gradient(90deg, #6a3a1a 0%, #a85a2a 100%);
    box-shadow: 0 0 8px rgba(168, 90, 42, 0.45);
    animation: stall-shimmer 1.6s ease-in-out infinite;
}
@keyframes stall-shimmer {
    0%, 100% { opacity: 0.55; }
    50%       { opacity: 1.00; }
}

/* Pygbag's progress chrome lives behind our z-index:100 overlay so the
   user never sees it; no hide rule needed. (Earlier `display:none`
   broke other things by removing elements pygbag's runtime expected.) */

/* Loading watchdog status line (filled in by JS once stalled) */
.skybit-status {
    font-family: Arial, sans-serif;
    font-size: clamp(11px, 2.6vw, 13px);
    font-weight: 600;
    letter-spacing: 2px;
    color: #d8b855;
    opacity: 0.7;
    margin: 18px 0 0;
    min-height: 1em;
    pointer-events: none;
    text-transform: uppercase;
    text-align: center;
}

/* SVG mountain silhouette */
.mountains {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    pointer-events: none;
}

/* ── Name-entry overlay ─────────────────────────────────────── */
#name-overlay {
    position: fixed;
    inset: 0;
    z-index: 200;
    background: linear-gradient(180deg, #060115 0%, #12082a 50%, #0c1022 100%);
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    font-family: Arial, sans-serif;
    -webkit-tap-highlight-color: transparent;
}
.ne-trophy {
    width: clamp(56px, 14vw, 80px);
    height: auto;
    margin: 0 0 14px;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.6));
    pointer-events: none;
    position: relative;
    z-index: 1;
}
.ne-headline {
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(20px, 5.4vw, 28px);
    font-weight: 900;
    letter-spacing: 2px;
    color: #f0c040;
    margin: 0 0 24px;
    text-shadow:
        -2px  0   0 #a82010,
         2px  0   0 #a82010,
         0   -2px 0 #a82010,
         0    2px 0 #a82010,
         0    7px 10px rgba(0, 0, 0, 0.8);
    pointer-events: none;
    position: relative;
    z-index: 1;
    text-align: center;
}
.ne-sub {
    font-size: 12px;
    letter-spacing: 3px;
    color: #d8b855;
    opacity: 0.65;
    margin: 0 0 24px;
    pointer-events: none;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
}
#name-input {
    background: #0d0820;
    color: #f0c040;
    border: 2px solid #e86828;
    border-radius: 14px;
    padding: 16px 28px;
    font-size: clamp(20px, 5vw, 26px);
    font-weight: 700;
    letter-spacing: 4px;
    text-align: center;
    outline: none;
    width: min(78vw, 300px);
    box-sizing: border-box;
    transition: box-shadow 0.2s;
    position: relative;
    z-index: 1;
}
#name-input:focus {
    box-shadow: 0 0 0 3px rgba(240, 192, 64, 0.35);
}
#name-counter {
    font-size: 13px;
    color: #d8b855;
    opacity: 0.6;
    margin: 8px 0 24px;
    letter-spacing: 1px;
    pointer-events: none;
    position: relative;
    z-index: 1;
}
.ne-submit, .ne-skip {
    /* Identical buttons: same width, same opacity, no animation, sit on
       top of whatever's behind via z-index. */
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(13px, 3.6vw, 18px);
    font-weight: 900;
    letter-spacing: 4px;
    color: #ffffff;
    background: linear-gradient(180deg, #c84018 0%, #7e1c02 100%);
    border: 2px solid #e86828;
    border-radius: 60px;
    padding: 16px 24px;
    min-width: 220px;
    text-align: center;
    cursor: pointer;
    white-space: nowrap;
    position: relative;
    z-index: 2;
    opacity: 1;
}
.ne-skip {
    margin-top: 14px;
}
</style>

<script>
/* Boot diagnostics — surface whether the overlay HTML reached the DOM
   and whether the build-time secret substitution was successful. Both
   are silent failure modes today; this gives us visibility without
   needing the user to dump page source. */
(function () {
    function once() {
        try {
            var ov = document.getElementById('skybit-loading');
            console.log('[skybit/boot] overlay in DOM:', !!ov,
                ov ? '(z-index=' + getComputedStyle(ov).zIndex +
                ', display=' + getComputedStyle(ov).display + ')' : '');
        } catch (_) {}
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', once);
    } else {
        once();
    }
})();
</script>

<script>
/* ── Skybit bridge (closure-private; no global submit API) ──────────────
   Everything score-related funnels through window.__sk(action, ...args).
   The previous build exposed window.lbSubmitStart / lbFetchStart /
   skyLogPlayStart directly on window, which made the casual cheat
   "open the console and type lbSubmitStart('X', 999999)" a one-liner.
   The dispatcher below requires a structured payload (with a SHA-256
   chain hash that the JS side recomputes from the events list) and
   tracks consumed run UUIDs to block trivial replay. None of this
   stops a determined reader of the source — it raises the bar from
   "60-second one-liner" to "construct a self-consistent proof." */
(function () {
    var a = "__SB_URL__";
    var b = "__SB_KEY__";

    /* Surface the build-time substitution result before any fetch runs.
       Top-10 has been silently empty on deploys where the build env
       didn't carry the secrets — this prints exactly what landed in
       the HTML so it's obvious in DevTools whether the value reached
       the page. The anon key is intentionally truncated so we can
       confirm presence + length without leaking the whole token to
       a casual screenshot. */
    try {
        var urlOk = !!(a && a.indexOf('supabase') >= 0 && a.indexOf('__SB_') < 0);
        console.log('[skybit/lb] build-time substitution:',
            'url=', urlOk ? a : '(not substituted: "' + a + '")',
            'key=', (b && b.indexOf('__SB_') < 0)
                ? (b.slice(0, 12) + '… len=' + b.length)
                : '(not substituted)');
    } catch (_) {}

    /* Sanity ping: fire a minimal fetch on page load, independent of
       the game's bridge / Python timing, so we can see whether the
       Supabase REST path works at all from this origin. Result is
       logged but never used — the real fetch path goes through
       doFetch() below. Skipped silently if substitution failed. */
    try {
        if (a && b && a.indexOf('__SB_') < 0 && b.indexOf('__SB_') < 0) {
            setTimeout(function () {
                fetch(a + '/rest/v1/scores?select=name,score&order=score.desc&limit=1', {
                    headers: {'apikey': b, 'Authorization': 'Bearer ' + b}
                }).then(function (r) {
                    console.log('[skybit/lb] sanity-ping status:', r.status, r.statusText);
                    return r.ok ? r.json() : r.text();
                }).then(function (body) {
                    console.log('[skybit/lb] sanity-ping body:',
                        typeof body === 'string' ? body.slice(0, 300) : body);
                }).catch(function (e) {
                    console.error('[skybit/lb] sanity-ping network error:', e && e.message || e);
                });
            }, 500);
        }
    } catch (_) {}

    /* Internal result slots — never on window. Polled via __sk('*_done'). */
    var rSubmit = null;
    var rFetch  = null;
    var rLog    = null;
    /* Parallel error string for fetch_top10. Empty string = no error
       (fetch is fine and returned 0 rows OR a populated array). Non-
       empty = a specific failure mode the Python side can render to the
       canvas so the user sees something other than a silent empty list. */
    var rFetchError = '';

    /* Replay defense: each run_id can submit exactly once per page load.
       Combined with the per-page-load handshake this means a captured
       fetch can't be re-fired ten times from the console. */
    var usedIds = (typeof Set === 'function') ? new Set() : {has:function(k){return !!this[k];}, add:function(k){this[k]=1;}};

    function deviceId() {
        try {
            var id = window.localStorage.getItem('skybit_device_id');
            if (id) return id;
            if (window.crypto && window.crypto.randomUUID) {
                id = window.crypto.randomUUID();
            } else {
                id = ('xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx').replace(/[xy]/g, function (c) {
                    var r = Math.random() * 16 | 0;
                    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
                });
            }
            window.localStorage.setItem('skybit_device_id', id);
            return id;
        } catch (e) {
            return '00000000-0000-4000-8000-000000000000';
        }
    }

    /* Recompute the same chain hash that game/_proof.py builds. The
       struct format is ">qIB" + 8-byte ASCII kind, identical to the
       Python writer. Any drift here desynchronises legitimate runs. */
    function packEvent(t, ds, kind) {
        var ms = Math.round(Number(t) * 1000);
        var buf = new ArrayBuffer(21);
        var dv  = new DataView(buf);
        var hi = Math.floor(ms / 0x100000000);
        var lo = ms >>> 0;
        if (ms < 0) {
            /* Two's complement for negative ms; not expected in legit runs. */
            hi = (hi >>> 0); lo = (lo >>> 0);
        }
        dv.setUint32(0, hi, false);
        dv.setUint32(4, lo, false);
        dv.setUint32(8, (Number(ds) >>> 0), false);
        var k = String(kind);
        var kl = k.length;
        dv.setUint8(12, kl & 0xff);
        var bytes = new Uint8Array(buf, 13, 8);
        for (var i = 0; i < 8; i++) bytes[i] = (i < k.length) ? (k.charCodeAt(i) & 0x7f) : 0;
        return new Uint8Array(buf);
    }
    function concatU8(a8, b8) {
        var out = new Uint8Array(a8.length + b8.length);
        out.set(a8, 0); out.set(b8, a8.length);
        return out;
    }
    function toHex(u8) {
        var s = '';
        for (var i = 0; i < u8.length; i++) {
            var h = u8[i].toString(16);
            s += (h.length < 2 ? '0' : '') + h;
        }
        return s;
    }
    async function chainHex(events) {
        var c = new Uint8Array(32);  /* zero-seed, matches Python */
        for (var i = 0; i < events.length; i++) {
            var ev = events[i];
            var packed = packEvent(ev[0], ev[1], ev[2]);
            var input = concatU8(c, packed);
            var digest = await window.crypto.subtle.digest('SHA-256', input);
            c = new Uint8Array(digest);
        }
        return toHex(c);
    }

    async function doSubmit(rawPayload) {
        rSubmit = null;
        try {
            if (!a || !b) { rSubmit = false; return; }
            var payload;
            try { payload = (typeof rawPayload === 'string') ? JSON.parse(rawPayload) : rawPayload; }
            catch (e) { rSubmit = false; return; }
            if (!payload || typeof payload !== 'object') { rSubmit = false; return; }
            var rid = String(payload.run_id || '');
            if (!rid || usedIds.has(rid)) { rSubmit = false; return; }
            var events = payload.events;
            if (!events || !events.length) { rSubmit = false; return; }
            /* Recompute chain hash on the JS side. A casual paster who
               supplies a fake events list with a guessed hash fails here. */
            var localHex = await chainHex(events);
            if (localHex !== String(payload.chain_hex || '')) { rSubmit = false; return; }
            usedIds.add(rid);
            var r = await fetch(a + '/rest/v1/scores', {
                method: 'POST',
                headers: {
                    'apikey': b,
                    'Authorization': 'Bearer ' + b,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify({name: String(payload.name), score: Number(payload.score)})
            });
            rSubmit = r.ok;
        } catch (e) { rSubmit = false; }
    }

    async function doFetch() {
        rFetch = null;
        rFetchError = '';
        try {
            if (!a || !b) {
                console.error('[skybit/lb] Supabase URL or KEY is empty — leaderboard cannot fetch.', {hasUrl: !!a, hasKey: !!b});
                rFetchError = 'config missing';
                rFetch = []; return;
            }
            /* Pull a wider slice and apply the plausibility ceiling
               client-side so a row injected by direct curl with score
               999999 doesn't make it onto the visible top-10. */
            var url = a + '/rest/v1/scores?select=name,score&order=score.desc&limit=200';
            var r = await fetch(
                url,
                { headers: {'apikey': b, 'Authorization': 'Bearer ' + b} }
            );
            if (!r.ok) {
                var bodyText = '';
                try { bodyText = await r.text(); } catch (_) {}
                console.error('[skybit/lb] fetch not ok:', r.status, r.statusText, '-', bodyText.slice(0, 200));
                rFetchError = 'http ' + r.status;
                rFetch = []; return;
            }
            var rows = await r.json();
            var filtered = [];
            for (var i = 0; i < rows.length && filtered.length < 10; i++) {
                var row = rows[i];
                var nm = String(row && row.name || '').slice(0, 10);
                var sc = Number(row && row.score);
                if (!isFinite(sc)) continue;
                if (sc < 0 || sc > 10000) continue;
                filtered.push({name: nm, score: sc});
            }
            console.log('[skybit/lb] fetched', rows.length, 'rows;', filtered.length, 'after filter');
            /* 200 OK with zero rows is the classic RLS-without-policy
               signature on Supabase — surface it so the leaderboard
               scene can show "Top-10 unavailable" instead of an empty
               list (silent empty looked identical to "no scores yet"
               and made the regression invisible). */
            if (rows.length === 0) {
                rFetchError = 'rls or empty';
            }
            rFetch = filtered;
        } catch (e) {
            console.error('[skybit/lb] fetch threw:', e && e.message || e);
            rFetchError = 'network';
            rFetch = [];
        }
    }

    async function doLog(rawPayload) {
        rLog = null;
        try {
            if (!a || !b) { rLog = false; return; }
            var payload;
            try { payload = (typeof rawPayload === 'string') ? JSON.parse(rawPayload) : rawPayload; }
            catch (e) { rLog = false; return; }
            if (!payload || typeof payload !== 'object') { rLog = false; return; }
            var body = {
                score:       Number(payload.score),
                duration_s:  Number(payload.duration_s),
                coins:       Number(payload.coins),
                pillars:     Number(payload.pillars),
                near_misses: Number(payload.near_misses),
                powerups:    payload.powerups || {},
                device_id:   deviceId()
            };
            var r = await fetch(a + '/rest/v1/plays', {
                method: 'POST',
                headers: {
                    'apikey': b,
                    'Authorization': 'Bearer ' + b,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify(body)
            });
            rLog = r.ok;
        } catch (e) { rLog = false; }
    }

    /* Single dispatcher. Reject unknown actions silently — no help for
       attackers grepping for action strings in console errors. */
    function dispatch(action, payload) {
        switch (String(action || '')) {
            case 'submit':       doSubmit(payload); return null;
            case 'submit_done':  return rSubmit;
            case 'fetch':        doFetch(); return null;
            case 'fetch_done':   return rFetch;
            case 'fetch_error':  return rFetchError;
            case 'log':          doLog(payload); return null;
            case 'log_done':     return rLog;
            default:             return null;
        }
    }

    /* Lock the property so a console attacker can't replace the
       dispatcher with their own and have us call into it later. */
    Object.defineProperty(window, '__sk', {
        value: dispatch, writable: false, configurable: false, enumerable: false
    });

    window._pendingName = "__pending__";
    var _nameStarsAdded = false;

    /* Desktop keyboard fix:
       SDL/pygame attaches a keydown listener at the window level and calls
       preventDefault on every key. That swallows the browser's default
       text-typing behavior on the focused <input>, so the field stays empty
       no matter what the user types. We register our own keydown listener
       in CAPTURE phase on window — it runs before SDL's bubble listener
       and, while the overlay is visible, calls stopPropagation so SDL never
       sees (or preventDefaults) the event. The browser's default action
       (typing into the focused input) still happens because that's not a
       listener — it's the browser's intrinsic behavior, which is gated by
       preventDefault, not stopPropagation.

       Enter must be handled here too because the input's own keydown
       listener is in the propagation path we're cutting short. */
    window.addEventListener('keydown', function (e) {
        var ov = document.getElementById('name-overlay');
        if (!ov || ov.style.display !== 'flex') return;
        e.stopPropagation();
        if (e.key === 'Enter') {
            var inp = document.getElementById('name-input');
            var v = (inp && inp.value || '').trim();
            window._pendingName = v.length > 0 ? v : '__skip__';
            ov.style.display = 'none';
        }
        // Escape skip removed — there's a clickable SKIP button now.
    }, true);

    /* iOS Safari fix: the soft keyboard only appears if focus() runs
       inside a real user gesture. ``openNameEntry``'s setTimeout(focus)
       fires after the gesture has ended, so iOS players see the overlay
       but no keyboard, and tapping the input may not focus it either —
       pygbag's SDL canvas listeners can swallow the synthesised click
       before it reaches the field.

       Capture-phase pointerdown at the document runs before any SDL
       listener and before any preventDefault, so we can re-focus the
       input synchronously inside the player's tap. Gated on overlay
       visibility so it never fires during gameplay. */
    document.addEventListener('pointerdown', function (e) {
        var ov = document.getElementById('name-overlay');
        if (!ov || ov.style.display !== 'flex') return;
        var t = e.target;
        // Don't steal focus from the SUBMIT / SKIP buttons — they need
        // their own click handler to fire normally.
        if (t && (t.id === 'name-submit' || t.id === 'name-skip')) return;
        var inp = document.getElementById('name-input');
        if (inp) try { inp.focus(); } catch (_) {}
    }, true);

    window.openNameEntry = function () {
        var ov  = document.getElementById('name-overlay');
        var inp = document.getElementById('name-input');
        var ctr = document.getElementById('name-counter');

        /* Inject twinkling stars once (same pattern as loading screen) */
        if (!_nameStarsAdded) {
            _nameStarsAdded = true;
            for (var i = 0; i < 40; i++) {
                var s = document.createElement('div');
                s.className = 'star';
                var sz = (Math.random() * 2.2 + 0.6).toFixed(1);
                s.style.cssText =
                    'width:' + sz + 'px;height:' + sz + 'px;' +
                    'top:'   + (Math.random() * 90).toFixed(1)  + '%;' +
                    'left:'  + (Math.random() * 100).toFixed(1) + '%;' +
                    '--dur:'   + (Math.random() * 3 + 1.3).toFixed(1) + 's;' +
                    '--delay:' + (Math.random() * 4).toFixed(1) + 's;';
                ov.insertBefore(s, ov.firstChild);
            }
        }

        ov.style.display = 'flex';
        inp.value = '';
        if (ctr) ctr.textContent = '0 / 10';
        window._pendingName = '__pending__';

        /* Desktop / Android: programmatic focus brings up the keyboard
           (or readies the cursor) without further user action. iOS
           Safari blocks focus() outside a real user gesture, so this
           call is a no-op there — the document-level pointerdown
           listener installed below handles iOS by re-focusing the
           input synchronously inside the player's tap. */
        setTimeout(function () { try { inp.focus(); } catch (_) {} }, 80);

        inp.oninput = function () {
            if (ctr) ctr.textContent = inp.value.length + ' / 10';
        };

        function submit() {
            var v = inp.value.trim();
            window._pendingName = v.length > 0 ? v : '__skip__';
            ov.style.display = 'none';
        }
        document.getElementById('name-submit').onclick = submit;
        document.getElementById('name-skip').onclick = function () {
            window._pendingName = '__skip__';
            ov.style.display = 'none';
        };
        // Enter / Escape are handled by the global capture-phase listener
        // above, since SDL would otherwise eat the input's own keydown.
    };
}());
</script>

<script>
(function () {
    /* ── skyPlay: load + play CC0 OGG samples ─────────────────────────────
       Same files (game/assets/sounds/*.ogg) are loaded by the native
       backend via pygame.mixer. inject_theme.py copies the OGGs into
       build/web/sounds/ at build time so the browser can fetch them via
       a relative URL. AudioBuffers are decoded once and cached, then
       played via short-lived AudioBufferSourceNode + GainNode each call. */

    var _ctx = null;
    var _cache = {};      // name → AudioBuffer
    var _pending = {};    // name → Promise<AudioBuffer>

    function getCtx() {
        if (!_ctx) _ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (_ctx.state === 'suspended') _ctx.resume();
        return _ctx;
    }

    function loadSnd(name) {
        if (_cache[name]) return Promise.resolve(_cache[name]);
        if (_pending[name]) return _pending[name];
        var ac = getCtx();
        var p = fetch('sounds/' + name + '.ogg')
            .then(function (r) { return r.arrayBuffer(); })
            .then(function (b) { return ac.decodeAudioData(b); })
            .then(function (buf) { _cache[name] = buf; delete _pending[name]; return buf; })
            .catch(function (e) { delete _pending[name]; throw e; });
        _pending[name] = p;
        return p;
    }

    window.skyPlay = function (name, volume) {
        loadSnd(name).then(function (buf) {
            var ac = getCtx();
            var src = ac.createBufferSource();
            src.buffer = buf;
            var g = ac.createGain();
            g.gain.value = (volume === undefined ? 1.0 : volume);
            src.connect(g); g.connect(ac.destination);
            src.start();
        }).catch(function (e) {
            if (!window._skyLoggedFail) {
                window._skyLoggedFail = true;
                console.warn('skyPlay failed for ' + name + ':', e);
            }
        });
    };

    /* ── Animated stars ───────────────────────────────────────────────── */
    var ov = document.getElementById('skybit-loading');
    if (ov) {
        for (var i = 0; i < 75; i++) {
            var s = document.createElement('div');
            s.className = 'star';
            var sz = (Math.random() * 2.5 + 0.7).toFixed(1);
            s.style.cssText =
                'width:' + sz + 'px;height:' + sz + 'px;' +
                'top:'  + (Math.random() * 90).toFixed(1) + '%;' +
                'left:' + (Math.random() * 100).toFixed(1) + '%;' +
                '--dur:'   + (Math.random() * 3 + 1.3).toFixed(1) + 's;' +
                '--delay:' + (Math.random() * 4).toFixed(1) + 's;';
            ov.insertBefore(s, ov.firstChild);
        }
    }

    /* ── Loading overlay state machine ────────────────────────────────────
       In production, pygbag's WASM/asset bundle download sometimes stalls
       (stale browser cache, CDN hiccup, slow mobile connection). The user
       only sees Skybit's overlay over pygbag's own progress bar, so they
       can't tell anything is wrong. The original dismiss handler also
       removed its listeners on the very first tap, so a tap fired before
       window.MM existed silently no-op'd UME and left the user staring
       at a frozen canvas with no recovery.

       This state machine fixes both:
         1. Polls window.MM every 250 ms; only marks the overlay as ready
            once pygbag has actually booted.
         2. After 8 s without boot, shows a "Loading… Ns" status line so
            the user knows it's still trying.
         3. After 25 s, swaps the button to "TAP TO RELOAD" with a
            cache-busting hard reload (?_skb=<ts>) — the most common
            fix for users wedged on a stale-cache state.
         4. A tap before pygbag boots is harmless (button pulses, listeners
            stay attached), so the user can retry instead of losing the
            overlay.
         5. Resumes the SHARED AudioContext (the same one skyPlay uses)
            on every gesture, so the user's real touch unlocks audio for
            the actual game session — the throw-away `new A()` of the
            previous version wasted the gesture on an unused context. */
    if (ov) {
        var btn    = document.getElementById('skybit-btn');
        var status = document.getElementById('skybit-status');
        var fill   = document.getElementById('skybit-progress-fill');
        var BTN_READY  = 'TAP  ·  CLICK  ·  SPACE';
        var BTN_LOAD   = 'LOADING…';
        var BTN_RELOAD = 'TAP TO RELOAD';
        var STALL_MS   = 25000;
        var INFO_MS    =  8000;
        /* Asymptote target while WASM is still downloading. We never let
           the bar reach 100 % from time alone — only a real `window.MM`
           boot snaps it there. Time-constant chosen so the bar reaches
           ~63 % at 6 s, ~86 % at 12 s, ~95 % at 18 s. The CSS transition
           on .skybit-progress-fill smooths each sample into a glide. */
        var ASYMPTOTE  = 0.92;
        var TAU_MS     = 6000;
        var t0 = Date.now();
        var pygbagReady = false;
        var stalled = false;

        if (btn) btn.textContent = BTN_LOAD;

        function isReady() {
            try { return typeof window.MM !== 'undefined' && window.MM !== null; }
            catch (_) { return false; }
        }

        function setFill(pct) {
            if (!fill) return;
            if (pct < 0) pct = 0;
            if (pct > 100) pct = 100;
            fill.style.width = pct.toFixed(2) + '%';
        }

        var pollId = setInterval(function () {
            if (isReady() && !pygbagReady) {
                pygbagReady = true;
                stalled = false;
                if (btn) btn.textContent = BTN_READY;
                if (status) status.textContent = '';
                if (fill) fill.classList.remove('skybit-progress-stalled');
                setFill(100);
                return;
            }
            if (pygbagReady) return;
            var elapsed = Date.now() - t0;
            /* 1 - exp(-t/τ) climbs fast then asymptotes — the bar always
               looks alive even on slow networks, and the CSS transition
               glides between samples so updates never snap. */
            var pct = ASYMPTOTE * (1 - Math.exp(-elapsed / TAU_MS)) * 100;
            setFill(pct);
            if (elapsed >= STALL_MS && !stalled) {
                stalled = true;
                if (btn) btn.textContent = BTN_RELOAD;
                if (status) status.textContent = 'Loading is stuck. Tap to reload.';
                if (fill) fill.classList.add('skybit-progress-stalled');
            } else if (elapsed >= INFO_MS && status && !stalled) {
                status.textContent = 'Loading… ' + Math.floor(elapsed / 1000) + 's';
            }
        }, 250);

        function reloadBust() {
            clearInterval(pollId);
            try {
                var u = new URL(window.location.href);
                u.searchParams.set('_skb', String(Date.now()));
                window.location.replace(u.toString());
            } catch (_) {
                window.location.reload();
            }
        }

        function pulseBtn() {
            if (!btn) return;
            btn.style.transition = 'transform 120ms ease';
            btn.style.transform  = 'scale(0.93)';
            setTimeout(function () { btn.style.transform = ''; }, 130);
        }

        function dismiss() {
            /* Always unlock the shared audio context on any user gesture --
               this is the same _ctx that skyPlay() uses later. Doing it
               here (inside the click handler) is the only point at which
               iOS Safari permits AudioContext.resume(). */
            try { getCtx(); } catch (_) {}

            if (stalled) { reloadBust(); return; }
            if (!pygbagReady) { pulseBtn(); return; }

            clearInterval(pollId);
            /* Pygbag's interpreter waits for a real DOM click on the
               canvas before kicking off the asyncio loop; setting
               MM.UME alone is NOT enough on emscripten 0.9.x, the
               interpreter pins forever. So we dispatch a synthetic
               click below in addition to setting MM.UME.
               That synthetic click also ends up in pygame's event
               queue as MOUSEBUTTONDOWN, but the STATE_INTRO branch
               of game/scenes.py:_flap_input now gates on _cooldown_t
               (initialised to 0.6 s when async_run starts), so the
               leaked click is harmlessly dropped instead of skipping
               the cinematic. See game/scenes.py async_run init. */
            try { if (window.MM) window.MM.UME = true; } catch (_) {}
            var cv = document.getElementById('canvas');
            if (cv) {
                try { cv.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true})); } catch (_) {}
            }
            ov.removeEventListener('click',      dismiss);
            ov.removeEventListener('touchstart', dismiss);
            ov.removeEventListener('touchend',   dismiss);
            /* Stay visible (pointer-events stays auto so any further taps
               are captured by the overlay's now-listenerless DOM and
               cannot reach the canvas) until Python signals first frame
               is rendered. Without this wait, the overlay would fade off
               while pygbag's bare progress display was still visible
               underneath -- the "separate screen" the user reported. */
            if (btn) btn.textContent = 'STARTING…';
            if (status) status.textContent = '';

            function fade() {
                ov.style.transition = 'opacity 0.45s ease';
                ov.style.opacity = '0';
                setTimeout(function () { ov.style.display = 'none'; }, 480);
            }
            /* Poll at 60 fps for the Python-side ready flag (set by
               game/scenes.py async_run after the first display.flip).
               Hard cap at 12 s so a stuck boot still hands the page
               over to the user instead of pinning forever. */
            var holdT0 = Date.now();
            var holdId = setInterval(function () {
                if (window.skybitGameReady === true ||
                    Date.now() - holdT0 > 12000) {
                    clearInterval(holdId);
                    fade();
                }
            }, 16);
        }
        ov.addEventListener('click',      dismiss);
        ov.addEventListener('touchstart', dismiss);
        ov.addEventListener('touchend',   dismiss);
    }
}());
</script>
"""
html = html.replace("</body>", INJECTION + "</body>", 1)

html = html.replace("__SB_URL__", _SB_URL)
html = html.replace("__SB_KEY__", _SB_KEY)

src.write_text(html, encoding="utf-8")

# ── 3. Post-write assertions ────────────────────────────────────────────────
# This script previously silently no-op'd when pygbag's template changed
# format: the .replace("<body>", ...) and re.sub(...) calls just didn't
# match, the file was written unchanged, and Netlify happily deployed an
# unthemed pygbag default that hung at a green loading bar. Fail the build
# loudly here so Netlify keeps the previous good deploy instead.
_problems = []
if "skybit-loading" not in html:
    _problems.append(
        "OVERLAY HTML (id=skybit-loading) was not injected — pygbag's HTML "
        "probably no longer contains a literal '<body>' tag. inject_theme.py "
        "needs updating to match pygbag's new template."
    )
if "pygbagReady" not in html:
    _problems.append(
        "Watchdog state machine (pygbagReady) was not injected — pygbag's "
        "HTML probably no longer contains a literal '</body>' tag."
    )
if _color_subs == 0:
    _problems.append(
        "None of the loading-bar color replacements matched — pygbag has "
        "almost certainly changed its loader template. Users will see the "
        "unthemed green/blue default progress bar."
    )
if "powderblue" in html:
    _problems.append(
        "'powderblue' still present in output — background-color "
        "replacements did not run as expected."
    )
if _problems:
    print("✗ inject_theme.py post-write assertions failed:", file=sys.stderr)
    for p in _problems:
        print("  - " + p, file=sys.stderr)
    print(
        "Aborting non-zero so Netlify retains the previous good deploy.",
        file=sys.stderr,
    )
    raise SystemExit(1)

print("✓ Skybit theme injected into build/web/index.html")
print(f"  ({_color_subs} color replacements matched)")
if _SB_URL and _SB_KEY:
    print(f"✓ Supabase URL set: {_SB_URL[:40]}...")
elif _SB_URL or _SB_KEY:
    # Half-set is a misconfiguration -- fail the build so the deploy
    # owner notices, rather than shipping a leaderboard that 401s.
    missing = "SUPABASE_ANON_KEY" if _SB_URL else "SUPABASE_URL"
    print(
        f"✗ {missing} is missing while the other Supabase env var is set. "
        "Both must be configured as repository secrets for the leaderboard "
        "to work. Aborting.",
        file=sys.stderr,
    )
    raise SystemExit(1)
else:
    print(
        "⚠⚠⚠ SUPABASE_URL and SUPABASE_ANON_KEY are both missing.\n"
        "    The leaderboard will be EMPTY in the deployed site.\n"
        "    Set them as repository secrets at:\n"
        "      Settings → Secrets and variables → Actions → New repository secret\n"
        "    Build is continuing because some deploys (e.g. local previews) intentionally\n"
        "    skip the leaderboard, but production deploys MUST set these."
    )

# ── 4. Copy CC0 sound files to build/web/sounds/ for browser fetch ──────────
# Native pygame.mixer reads them straight from game/assets/sounds/. The
# browser can't reach into the bundled APK, so the JS skyPlay() block fetches
# them from this static path under the deployed site root.
import shutil
_SND_SRC = Path("game/assets/sounds")
_SND_DST = Path("build/web/sounds")
if _SND_SRC.exists():
    _SND_DST.mkdir(parents=True, exist_ok=True)
    n_copied = 0
    for ogg in _SND_SRC.glob("*.ogg"):
        shutil.copy(ogg, _SND_DST / ogg.name)
        n_copied += 1
    print(f"✓ Copied {n_copied} sound files → build/web/sounds/")
else:
    print(f"⚠ {_SND_SRC} not found — browser will play no sounds")
