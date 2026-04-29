#!/usr/bin/env python3
"""
Post-process pygbag's generated build/web/index.html to inject:
  - Skybit dark-purple night-sky loading overlay
  - window.skyPlay() Web Audio synthesis (matches game/audio.py exactly)
"""
import os
import re
from pathlib import Path

src = Path("build/web/index.html")
if not src.exists():
    raise SystemExit("build/web/index.html not found — run pygbag first")

html = src.read_text(encoding="utf-8")

_SB_URL = os.environ.get("SUPABASE_URL", "")
_SB_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
# Build-time HMAC secret used by game/security/crypto.py + the JS bridge to
# sign score-submit envelopes. Rotates on every Netlify deploy. Generated
# fresh if not provided so local builds still work.
_SB_HMAC = os.environ.get("SKYBIT_HMAC_KEY") or os.urandom(24).hex()

# ── 1. Dark body + canvas background (CSS) ───────────────────────────────────
html = html.replace("background-color:powderblue", "background-color:#0d0820")
# Inline style on <canvas> if present
html = re.sub(
    r'(<canvas\b[^>]*style=["\'])([^"\']*)',
    lambda m: m.group(1) + "background:#0d0820;" + m.group(2),
    html,
)

# ── 2. Patch embedded Python progress-bar colors ──────────────────────────────
# pygbag embeds custom_site() Python code as a comment inside a <script> tag.
# Use regex so spaces inside tuples don't break the match.
html = html.replace('"#7f7f7f"', '"#0d0820"')                        # bg: gray → dark purple
html = re.sub(r'\(\s*0\s*,\s*255\s*,\s*0\s*\)', '(240,192,64)', html)   # bar: green → gold
html = re.sub(r'\(\s*10\s*,\s*10\s*,\s*10\s*\)', '(20,12,48)', html)    # track: near-black → deep purple
html = re.sub(r',\s*True\s*,\s*"blue"\)', ', True, (240,192,64))', html)  # text: blue → gold
# Some pygbag versions name the bg color differently
html = html.replace('"powderblue"', '"#0d0820"')
html = html.replace("'powderblue'", "'#0d0820'")

# ── 2. Loading overlay HTML (injected right after <body>) ─────────────────────
OVERLAY = """
<div id="skybit-loading">
  <p class="skybit-title">SKYBIT</p>
  <p class="skybit-sub">Pocket Sky Flyer</p>
  <div class="tap-btn">TAP &nbsp;&middot;&nbsp; CLICK &nbsp;&middot;&nbsp; SPACE</div>
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
  <p class="ne-celebrate">YOU MADE THE TOP 10!</p>
  <p class="ne-title">WELCOME TO TOP 10!</p>
  <input id="name-input" maxlength="10" autocomplete="off" spellcheck="false"
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

/* ── Loading overlay ───────────────────────────────── */
#skybit-loading {
    position: fixed;
    inset: 0;
    z-index: 100;
    background: linear-gradient(180deg, #060115 0%, #12082a 45%, #0c1022 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    user-select: none;
    overflow: hidden;
    -webkit-tap-highlight-color: transparent;
}

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
.ne-celebrate {
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(16px, 4.4vw, 22px);
    font-weight: 900;
    letter-spacing: 3px;
    color: #ffd84a;
    margin: 0 0 18px;
    text-shadow:
        0 0 12px rgba(255, 216, 74, 0.55),
        0 2px 0 #a82010,
        0 4px 8px rgba(0, 0, 0, 0.7);
    animation: pulse-btn 1.8s ease-in-out infinite;
    pointer-events: none;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
}
.ne-title {
    font-family: Arial Black, Arial, sans-serif;
    font-size: clamp(28px, 7vw, 38px);
    font-weight: 900;
    letter-spacing: 5px;
    color: #f0c040;
    margin: 0 0 8px;
    text-shadow:
        -2px  0   0 #a82010,
         2px  0   0 #a82010,
         0   -2px 0 #a82010,
         0    2px 0 #a82010,
         0    7px 10px rgba(0, 0, 0, 0.8);
    animation: float-title 3.4s ease-in-out infinite;
    pointer-events: none;
    position: relative;
    z-index: 1;
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
/* ── Supabase leaderboard bridge ───────────────────────────────────────── */
(function () {
    var _SB_URL  = "__SB_URL__";
    var _SB_KEY  = "__SB_KEY__";
    var _SB_HMAC = "__SB_HMAC__";  /* HMAC-SHA256 secret, replaced at build time */

    /* Fire-and-poll pattern: Python polls window._lbSubmitDone / window._lbFetchResult
       instead of awaiting a JS Promise directly (which freezes Python's asyncio loop). */
    window._lbSubmitDone   = null;
    window._lbFetchResult  = null;
    window._skyLogPlayDone = null;
    window._skySecEventDone = null;

    /* HMAC-SHA256(text) → hex string. Uses SubtleCrypto. */
    async function _hmacHex(keyStr, text) {
        try {
            var enc = new TextEncoder();
            var key = await window.crypto.subtle.importKey(
                'raw', enc.encode(keyStr),
                {name: 'HMAC', hash: 'SHA-256'},
                false, ['sign']
            );
            var sig = await window.crypto.subtle.sign('HMAC', key, enc.encode(text));
            var bytes = new Uint8Array(sig);
            var hex = '';
            for (var i = 0; i < bytes.length; i++) {
                hex += bytes[i].toString(16).padStart(2, '0');
            }
            return hex;
        } catch (e) {
            return '';
        }
    }

    /* Anonymous device UUID — stable across reloads on the same browser via
       localStorage, regenerated on a fresh device or after the user clears
       site data. No PII, no IP. */
    function _skybitDeviceId() {
        try {
            var id = window.localStorage.getItem('skybit_device_id');
            if (id) return id;
            if (window.crypto && window.crypto.randomUUID) {
                id = window.crypto.randomUUID();
            } else {
                /* RFC4122 v4 fallback for older browsers */
                id = ('xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx').replace(/[xy]/g, function (c) {
                    var r = Math.random() * 16 | 0;
                    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
                });
            }
            window.localStorage.setItem('skybit_device_id', id);
            return id;
        } catch (e) {
            /* Private mode / disabled storage: still return a per-tab id */
            return '00000000-0000-4000-8000-000000000000';
        }
    }

    /* Legacy: kept for back-compat with any cached client. NEW: signed RPC. */
    window.lbSubmitStart = function (name, score) {
        var env = JSON.stringify({name: String(name), score: Number(score),
                                  duration: 0, pillars: 0, run_sig: '',
                                  chain_last: '', chain_count: 0,
                                  y_stddev_centi: 0, y_range_centi: 0});
        window.lbSubmitSignedStart(env);
    };

    /* Signed-RPC submit. Python builds the envelope; we add device_id +
       client_sig and POST to /rest/v1/rpc/submit_score which enforces
       plausibility, rate-limit, and the anti-cheat trajectory check. */
    window.lbSubmitSignedStart = function (envelopeJson) {
        window._lbSubmitDone = null;
        (async function () {
            if (!_SB_URL || !_SB_KEY) { window._lbSubmitDone = false; return; }
            try {
                var env = JSON.parse(String(envelopeJson));
                var device = _skybitDeviceId();
                /* HMAC over the canonical envelope so a tampered field
                   produces a sig the server's presence-check still
                   accepts but real verification (off-line analytics)
                   would reject. The presence check alone forces the
                   client to go through this signed bridge. */
                var canon = JSON.stringify({
                    n: String(env.name || ''),
                    s: Number(env.score || 0),
                    d: Number(env.duration || 0),
                    p: Number(env.pillars || 0),
                    rs: String(env.run_sig || ''),
                    cl: String(env.chain_last || ''),
                    cc: Number(env.chain_count || 0),
                    ys: Number(env.y_stddev_centi || 0),
                    yr: Number(env.y_range_centi || 0),
                    dev: device
                });
                var sig = await _hmacHex(_SB_HMAC, canon);
                var body = {
                    p_name:           String(env.name || ''),
                    p_score:          Number(env.score || 0),
                    p_device:         device,
                    p_duration:       Number(env.duration || 0),
                    p_run_sig:        String(env.run_sig || ''),
                    p_pillars:        Number(env.pillars || 0),
                    p_y_stddev_centi: Number(env.y_stddev_centi || 0),
                    p_y_range_centi:  Number(env.y_range_centi || 0),
                    p_chain_last:     String(env.chain_last || ''),
                    p_chain_count:    Number(env.chain_count || 0),
                    p_client_sig:     sig
                };
                var r = await fetch(_SB_URL + '/rest/v1/rpc/submit_score', {
                    method: 'POST',
                    headers: {
                        'apikey': _SB_KEY,
                        'Authorization': 'Bearer ' + _SB_KEY,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(body)
                });
                if (!r.ok) {
                    /* Try to surface the server-side rejection reason on
                       the JS console — invaluable for debugging. */
                    try { console.warn('submit_score rejected:', await r.text()); } catch (e) {}
                }
                window._lbSubmitDone = r.ok;
            } catch (e) { console.warn('lbSubmitSignedStart:', e); window._lbSubmitDone = false; }
        })();
    };

    window.lbFetchStart = function () {
        window._lbFetchResult = null;
        (async function () {
            if (!_SB_URL || !_SB_KEY) { window._lbFetchResult = []; return; }
            try {
                var r = await fetch(
                    _SB_URL + '/rest/v1/scores?select=name,score&order=score.desc&limit=10',
                    { headers: {'apikey': _SB_KEY, 'Authorization': 'Bearer ' + _SB_KEY} }
                );
                window._lbFetchResult = r.ok ? await r.json() : [];
            } catch (e) { console.warn('lbFetchStart:', e); window._lbFetchResult = []; }
        })();
    };

    /* Per-run telemetry. Python passes a JSON string; we parse it, merge
       in the device UUID, and POST to the public.log_play RPC which
       enforces plausibility caps. */
    window.skyLogPlayStart = function (payloadJson) {
        window._skyLogPlayDone = null;
        (async function () {
            if (!_SB_URL || !_SB_KEY) { window._skyLogPlayDone = false; return; }
            try {
                var p = JSON.parse(String(payloadJson));
                var body = {
                    p_device:      _skybitDeviceId(),
                    p_score:       Number(p.score || 0),
                    p_duration:    Number(p.duration_s || 0),
                    p_coins:       Number(p.coins || 0),
                    p_pillars:     Number(p.pillars || 0),
                    p_near_misses: Number(p.near_misses || 0),
                    p_powerups:    p.powerups || {},
                    p_run_sig:     String(p.run_sig || '')
                };
                var r = await fetch(_SB_URL + '/rest/v1/rpc/log_play', {
                    method: 'POST',
                    headers: {
                        'apikey': _SB_KEY,
                        'Authorization': 'Bearer ' + _SB_KEY,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(body)
                });
                window._skyLogPlayDone = r.ok;
            } catch (e) { console.warn('skyLogPlayStart:', e); window._skyLogPlayDone = false; }
        })();
    };

    /* Security-event flush. Python collects anomalies into a ring buffer
       (game/security/events.py) and POSTs them in a batch via this bridge.
       Best-effort; failures don't break the game. */
    window.skySecEventStart = function (payloadJson) {
        window._skySecEventDone = null;
        (async function () {
            if (!_SB_URL || !_SB_KEY) { window._skySecEventDone = false; return; }
            try {
                var arr = JSON.parse(String(payloadJson));
                var device = _skybitDeviceId();
                var rows = arr.map(function (e) {
                    return {device_id: device, name: String(e.name || ''),
                            detail: e.detail || {}, ts: new Date((e.ts || 0) * 1000).toISOString()};
                });
                var r = await fetch(_SB_URL + '/rest/v1/security_events', {
                    method: 'POST',
                    headers: {
                        'apikey': _SB_KEY,
                        'Authorization': 'Bearer ' + _SB_KEY,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify(rows)
                });
                window._skySecEventDone = r.ok;
            } catch (e) { console.warn('skySecEventStart:', e); window._skySecEventDone = false; }
        })();
    };

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
        setTimeout(function () { inp.focus(); }, 80);
        window._pendingName = '__pending__';

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

    /* ── Overlay dismiss (tap/click → audio + UME + fade) ────────────── */
    if (ov) {
        function dismiss() {
            /* Start / resume Web Audio context */
            try {
                var A = window.AudioContext || window.webkitAudioContext;
                if (A) { var tmp = new A(); tmp.resume(); }
            } catch (_) {}
            /* Signal pygbag media manager */
            if (window.MM) window.MM.UME = true;
            /* Forward gesture to canvas so pygbag event handlers fire */
            var cv = document.getElementById('canvas');
            if (cv) cv.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
            /* Fade out */
            ov.style.transition = 'opacity 0.45s ease';
            ov.style.opacity = '0';
            setTimeout(function () { ov.style.display = 'none'; }, 480);
            ov.removeEventListener('click',    dismiss);
            ov.removeEventListener('touchend', dismiss);
        }
        ov.addEventListener('click',    dismiss);
        ov.addEventListener('touchend', dismiss);
    }
}());
</script>
"""
html = html.replace("</body>", INJECTION + "</body>", 1)

html = html.replace("__SB_URL__", _SB_URL)
html = html.replace("__SB_KEY__", _SB_KEY)
html = html.replace("__SB_HMAC__", _SB_HMAC)

src.write_text(html, encoding="utf-8")
print("✓ Skybit theme injected into build/web/index.html")
if _SB_URL:
    print(f"✓ Supabase URL set: {_SB_URL[:40]}...")
else:
    print("⚠ SUPABASE_URL not set — leaderboard will be disabled")
if os.environ.get("SKYBIT_HMAC_KEY"):
    print(f"✓ Skybit HMAC key set from env (rotates per deploy)")
else:
    print("⚠ SKYBIT_HMAC_KEY not set — generated ephemeral build secret (set the env var on Netlify for stable rotation)")

# Mirror the HMAC into a Python module so game/security/crypto.py can
# read the same secret on the Python side. Written into the build's
# bundled game/ tree (pygbag packs game/security/_build_secret.py).
try:
    sec_dir = Path("game/security")
    if sec_dir.exists():
        (sec_dir / "_build_secret.py").write_text(
            f'# Auto-generated by inject_theme.py — do not edit by hand.\n'
            f'HMAC_KEY = {_SB_HMAC!r}\n',
            encoding="utf-8",
        )
        print("✓ game/security/_build_secret.py written")
except Exception as e:
    print(f"⚠ failed to write _build_secret.py: {e}")

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
