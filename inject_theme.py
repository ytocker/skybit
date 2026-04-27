#!/usr/bin/env python3
"""
Post-process pygbag's generated build/web/index.html to inject:
  - Skybit dark-purple night-sky loading overlay
  - window.skyPlay() Web Audio synthesis (matches game/audio.py exactly)
  - Supabase leaderboard JS bridge (lbSubmit / lbFetch / openNameEntry)
    Reads SUPABASE_URL and SUPABASE_ANON_KEY from environment at build time.
"""
import os
from pathlib import Path

_SB_URL = os.environ.get("SUPABASE_URL", "")
_SB_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

src = Path("build/web/index.html")
if not src.exists():
    raise SystemExit("build/web/index.html not found — run pygbag first")

html = src.read_text(encoding="utf-8")

# ── 1. Dark body background (CSS) ────────────────────────────────────────────
html = html.replace("background-color:powderblue", "background-color:#0d0820")

# ── 2. Patch embedded Python progress-bar colors ──────────────────────────────
# pygbag embeds custom_site() Python code as a comment inside a <script> tag.
# These targeted replacements recolor the pygame loading bar to match the theme.
html = html.replace('"#7f7f7f"', '"#0d0820"')       # body bg: gray → dark purple
html = html.replace('(0,255,0)', '(240,192,64)')     # bar fill: green → gold
html = html.replace('(10,10,10)', '(20,12,48)')      # bar track: near-black → deep purple
# "Ready to start!" text: blue → gold
html = html.replace(', True, "blue")', ', True, (240,192,64))')

# ── 2. Loading overlay HTML (injected right after <body>) ─────────────────────
OVERLAY = """
<div id="skybit-loading">
  <div class="title-glow"></div>
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
# Name-entry overlay — shown by window.openNameEntry(), hidden after submit/skip
NAME_OVERLAY = """
<div id="name-overlay" style="display:none;position:fixed;inset:0;z-index:200;
     background:rgba(8,3,26,.93);flex-direction:column;
     align-items:center;justify-content:center;font-family:Arial,sans-serif;">
  <p style="color:#f0c040;font-size:clamp(18px,5vw,26px);font-weight:900;
             letter-spacing:4px;margin:0 0 8px;text-shadow:0 2px 8px #000">ENTER YOUR NAME</p>
  <p style="color:#ddc870;font-size:13px;letter-spacing:2px;margin:0 0 28px;opacity:.7">
     max 16 characters</p>
  <input id="name-input" maxlength="16" autocomplete="off" spellcheck="false"
         style="background:#1a0f38;color:#f0c040;border:2px solid #f07030;
                border-radius:12px;padding:14px 24px;font-size:clamp(18px,5vw,24px);
                font-weight:700;letter-spacing:3px;text-align:center;
                outline:none;width:min(80vw,280px);box-sizing:border-box;"/>
  <button id="name-submit"
          style="margin-top:24px;background:linear-gradient(180deg,#cc4418,#881e04);
                 color:#fff;border:2px solid #e86828;border-radius:50px;
                 padding:13px 48px;font-size:17px;font-weight:900;
                 letter-spacing:3px;cursor:pointer;">SUBMIT</button>
  <p id="name-skip" style="margin-top:16px;color:rgba(200,200,220,.45);
     font-size:12px;letter-spacing:1px;cursor:pointer;">skip</p>
</div>
"""
html = html.replace("<body>", "<body>\n" + OVERLAY + NAME_OVERLAY, 1)

# ── 3. CSS + JS injected before </body> ──────────────────────────────────────
INJECTION = """
<style>
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

/* Radial glow blob behind the title */
.title-glow {
    position: absolute;
    width: 320px;
    height: 180px;
    background: radial-gradient(ellipse at center,
        rgba(240,192,64,0.18) 0%,
        rgba(200,64,24,0.08) 45%,
        transparent 75%);
    pointer-events: none;
    animation: glow-pulse 3.4s ease-in-out infinite;
}
@keyframes glow-pulse {
    0%, 100% { opacity: 0.7; transform: scale(1.0); }
    50%       { opacity: 1.0; transform: scale(1.15); }
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
</style>

<script>
(function () {
    /* ── skyPlay: Web Audio synthesis ─────────────────────────────────────
       Matches game/audio.py browser backend parameters exactly.          */
    var _ctx = null;
    function getCtx() {
        if (!_ctx) _ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (_ctx.state === 'suspended') _ctx.resume();
        return _ctx;
    }
    function tone(ac, f0, f1, dur, type, vol, atk, rel, t0) {
        var osc = ac.createOscillator(), g = ac.createGain();
        osc.connect(g); g.connect(ac.destination);
        osc.type = type;
        osc.frequency.setValueAtTime(f0, t0);
        if (f0 !== f1) osc.frequency.linearRampToValueAtTime(f1, t0 + dur);
        g.gain.setValueAtTime(0, t0);
        g.gain.linearRampToValueAtTime(vol, t0 + atk);
        g.gain.setValueAtTime(vol, t0 + dur - rel);
        g.gain.linearRampToValueAtTime(0, t0 + dur);
        osc.start(t0); osc.stop(t0 + dur);
    }
    window.skyPlay = function (name, volume) {
        try {
            var ac = getCtx(), t = ac.currentTime, v = volume || 0.5;
            if      (name === 'flap')       { tone(ac,260,520,.07,'square',.25*v,.004,.05,t); }
            else if (name === 'coin')       { tone(ac,880,1320,.10,'sine',.40*v,.004,.08,t); }
            else if (name === 'coin_combo') { tone(ac,1175,1760,.13,'sine',.45*v,.003,.09,t); }
            else if (name === 'coin_triple') {
                tone(ac,880,880,.05,'sine',.35*v,.01,.02,t);
                tone(ac,1175,1175,.06,'sine',.40*v,.01,.02,t+.05);
                tone(ac,1568,1568,.08,'sine',.45*v,.01,.02,t+.11);
            }
            else if (name === 'mushroom') {
                tone(ac,523,523,.08,'triangle',.42*v,.01,.08,t);
                tone(ac,659,659,.08,'triangle',.42*v,.01,.08,t+.08);
                tone(ac,784,988,.14,'triangle',.50*v,.01,.08,t+.16);
            }
            else if (name === 'magnet') {
                tone(ac,220,660,.10,'triangle',.40*v,.01,.08,t);
                tone(ac,660,990,.12,'sine',.42*v,.01,.08,t+.10);
            }
            else if (name === 'slowmo') {
                tone(ac,880,660,.10,'triangle',.38*v,.01,.08,t);
                tone(ac,660,440,.10,'triangle',.40*v,.01,.08,t+.10);
                tone(ac,440,220,.18,'sine',.45*v,.01,.08,t+.20);
            }
            else if (name === 'thunder') {
                tone(ac,80,60,.20,'triangle',.38*v,.01,.08,t);
                tone(ac,60,50,.20,'triangle',.35*v,.01,.08,t+.20);
                tone(ac,50,40,.40,'sine',.32*v,.01,.08,t+.40);
            }
            else if (name === 'death')    { tone(ac,330,90,.32,'square',.45*v,.005,.18,t); }
            else if (name === 'gameover') {
                tone(ac,523,523,.12,'triangle',.35*v,.01,.08,t);
                tone(ac,440,440,.12,'triangle',.35*v,.01,.08,t+.12);
                tone(ac,349,349,.14,'triangle',.38*v,.01,.08,t+.24);
                tone(ac,262,262,.18,'triangle',.42*v,.01,.08,t+.38);
            }
        } catch (e) { console.warn('skyPlay error:', e); }
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

<script>
/* ── Supabase leaderboard bridge ──────────────────────────────────────────
   lbSubmit / lbFetch / openNameEntry are called from game/leaderboard.py.
   SUPABASE_URL and SUPABASE_ANON_KEY are baked in at build time.        */
(function () {
    var _SB_URL = """ + repr(_SB_URL) + """;
    var _SB_KEY = """ + repr(_SB_KEY) + """;

    window.lbSubmit = async function (name, score) {
        if (!_SB_URL || !_SB_KEY) return false;
        try {
            var r = await fetch(_SB_URL + '/rest/v1/scores', {
                method: 'POST',
                headers: {
                    'apikey': _SB_KEY,
                    'Authorization': 'Bearer ' + _SB_KEY,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify({name: String(name), score: Number(score)})
            });
            return r.ok;
        } catch (e) { console.warn('lbSubmit:', e); return false; }
    };

    window.lbFetch = async function () {
        if (!_SB_URL || !_SB_KEY) return [];
        try {
            var r = await fetch(
                _SB_URL + '/rest/v1/scores?select=name,score&order=score.desc&limit=10',
                { headers: {'apikey': _SB_KEY, 'Authorization': 'Bearer ' + _SB_KEY} }
            );
            return r.ok ? await r.json() : [];
        } catch (e) { console.warn('lbFetch:', e); return []; }
    };

    window._pendingName = '__pending__';

    window.openNameEntry = function () {
        var ov  = document.getElementById('name-overlay');
        var inp = document.getElementById('name-input');
        ov.style.display = 'flex';
        inp.value = '';
        setTimeout(function () { inp.focus(); }, 80);
        window._pendingName = '__pending__';

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
        inp.onkeydown = function (e) { if (e.key === 'Enter') submit(); };
    };
}());
</script>
"""
html = html.replace("</body>", INJECTION + "</body>", 1)

src.write_text(html, encoding="utf-8")
print("✓ Skybit theme injected into build/web/index.html")
