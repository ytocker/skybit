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
  <p class="ne-title">ENTER YOUR NAME</p>
  <p class="ne-sub">up to 10 characters</p>
  <input id="name-input" maxlength="10" autocomplete="off" spellcheck="false"/>
  <p id="name-counter">0 / 10</p>
  <button id="name-submit" class="ne-submit">SUBMIT</button>
  <p id="name-skip" class="ne-skip">skip</p>
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
.ne-submit {
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
    cursor: pointer;
    white-space: nowrap;
    position: relative;
    z-index: 1;
}
.ne-skip {
    margin-top: 18px;
    color: rgba(200, 200, 220, 0.38);
    font-size: 12px;
    letter-spacing: 2px;
    cursor: pointer;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
}
</style>

<script>
/* ── Supabase leaderboard bridge ───────────────────────────────────────── */
(function () {
    var _SB_URL = "__SB_URL__";
    var _SB_KEY = "__SB_KEY__";

    /* Fire-and-poll pattern: Python polls window._lbSubmitDone / window._lbFetchResult
       instead of awaiting a JS Promise directly (which freezes Python's asyncio loop). */
    window._lbSubmitDone = null;
    window._lbFetchResult = null;

    window.lbSubmitStart = function (name, score) {
        window._lbSubmitDone = null;
        (async function () {
            if (!_SB_URL || !_SB_KEY) { window._lbSubmitDone = false; return; }
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
                window._lbSubmitDone = r.ok;
            } catch (e) { console.warn('lbSubmitStart:', e); window._lbSubmitDone = false; }
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
        } else if (e.key === 'Escape') {
            window._pendingName = '__skip__';
            ov.style.display = 'none';
        }
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
    /* ── skyPlay: Web Audio synthesis ─────────────────────────────────────
       Mirrors the procedural++ toolkit in game/audio.py — band-limited
       OscillatorNodes (sine/square/triangle), exponential gain envelope
       via setTargetAtTime, vibrato via a modulator OscillatorNode wired to
       the carrier's frequency, detune via osc.detune.value, and filtered
       noise via AudioBufferSourceNode + BiquadFilterNode. Each named sound
       composes one or more voice() / tone() / noise() calls so it matches
       the same multi-voice spec the Python backend renders.                */

    var _ctx = null;
    var _noiseBuf = null;            // shared 2-second white-noise buffer

    function getCtx() {
        if (!_ctx) _ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (_ctx.state === 'suspended') _ctx.resume();
        return _ctx;
    }
    function getNoiseBuf(ac) {
        if (_noiseBuf) return _noiseBuf;
        var n = ac.sampleRate * 2;
        _noiseBuf = ac.createBuffer(1, n, ac.sampleRate);
        var d = _noiseBuf.getChannelData(0);
        // Deterministic LCG so renders are reproducible across reloads
        var s = 0x12345678;
        for (var i = 0; i < n; i++) {
            s = (s * 1664525 + 1013904223) >>> 0;
            d[i] = (s / 0x80000000) - 1.0;
        }
        return _noiseBuf;
    }

    /* envType="exp"   → linear attack + exp decay (sustained / pad)
       envType="punch" → instant onset + brief overshoot + exp decay (pickup)
       envType="hann"  → raised-cosine (set as exp here; the audible difference
                         is small enough that "exp" with longer atk works).    */
    function applyEnv(g, vol, atk, dec, dur, t0, envType, punch) {
        var tau = Math.max(0.001, dec / 3);
        if (envType === 'punch') {
            var p = (punch === undefined ? 0.35 : punch);
            // Instant onset with overshoot, taper to vol over 12 ms, then decay.
            g.gain.setValueAtTime(vol * (1 + p), t0);
            g.gain.linearRampToValueAtTime(vol, t0 + 0.012);
            g.gain.setTargetAtTime(0, t0 + 0.012, tau);
        } else {
            g.gain.setValueAtTime(0, t0);
            g.gain.linearRampToValueAtTime(vol, t0 + atk);
            g.gain.setTargetAtTime(0, t0 + atk, tau);
        }
        g.gain.setValueAtTime(0, t0 + dur);
    }

    /* tone() — band-limited oscillator voice. Supports pitch sweep, vibrato,
       tremolo (AM), detune, and instant pitch-jump (jumpAt/jumpToF) for
       Mario-style two-note arpeggios.                                       */
    function tone(ac, opts) {
        var t0 = opts.start;
        var dur = opts.dur;
        var f0 = opts.f0, f1 = (opts.f1 === undefined ? f0 : opts.f1);
        var atk = (opts.atk === undefined ? 0.005 : opts.atk);
        var dec = (opts.dec === undefined ? dur * 0.5 : opts.dec);
        var envType = opts.env || 'exp';
        var osc = ac.createOscillator(), g = ac.createGain();
        osc.type = opts.type;
        if (opts.detune) osc.detune.value = opts.detune;
        osc.frequency.setValueAtTime(f0, t0);
        if (opts.jumpAt !== undefined && opts.jumpToF !== undefined) {
            // Sweep/hold f0 until the jump, then instant jump to f2.
            if (f0 !== f1) {
                osc.frequency.linearRampToValueAtTime(
                    f0 + (f1 - f0) * (opts.jumpAt / dur), t0 + opts.jumpAt);
            }
            osc.frequency.setValueAtTime(opts.jumpToF, t0 + opts.jumpAt);
        } else if (f0 !== f1) {
            osc.frequency.linearRampToValueAtTime(f1, t0 + dur);
        }
        osc.connect(g); g.connect(ac.destination);
        if (opts.vib && opts.vibDepth) {
            var lfo = ac.createOscillator(), lfoG = ac.createGain();
            lfo.type = 'sine';
            lfo.frequency.value = opts.vib;
            lfoG.gain.value = opts.vibDepth * 1200;  // fraction → cents
            lfo.connect(lfoG); lfoG.connect(osc.detune);
            lfo.start(t0); lfo.stop(t0 + dur);
        }
        if (opts.tremHz && opts.tremDepth) {
            var lfo2 = ac.createOscillator(), lfo2G = ac.createGain();
            lfo2.type = 'sine';
            lfo2.frequency.value = opts.tremHz;
            lfo2G.gain.value = opts.tremDepth * opts.vol;
            lfo2.connect(lfo2G); lfo2G.connect(g.gain);
            lfo2.start(t0); lfo2.stop(t0 + dur);
        }
        applyEnv(g, opts.vol, atk, dec, dur, t0, envType, opts.punch);
        osc.start(t0); osc.stop(t0 + dur + 0.02);
    }

    /* Filtered white-noise voice. lp/hp are cutoff frequencies in Hz.
       env="punch" gives the same snappy onset as tone().                    */
    function noise(ac, opts) {
        var t0 = opts.start;
        var dur = opts.dur;
        var atk = (opts.atk === undefined ? 0.001 : opts.atk);
        var dec = (opts.dec === undefined ? dur * 0.5 : opts.dec);
        var envType = opts.env || 'exp';
        var src = ac.createBufferSource();
        src.buffer = getNoiseBuf(ac);
        src.loop = true;
        // Pseudo-random offset so consecutive plays use different noise
        var off = Math.random() * src.buffer.duration;
        src.loopStart = 0;
        src.loopEnd = src.buffer.duration;
        var node = src;
        if (opts.lp) {
            var lpf = ac.createBiquadFilter();
            lpf.type = 'lowpass';
            lpf.frequency.value = opts.lp;
            lpf.Q.value = 0.5;
            node.connect(lpf); node = lpf;
        }
        if (opts.hp) {
            var hpf = ac.createBiquadFilter();
            hpf.type = 'highpass';
            hpf.frequency.value = opts.hp;
            hpf.Q.value = 0.5;
            node.connect(hpf); node = hpf;
        }
        var g = ac.createGain();
        node.connect(g); g.connect(ac.destination);
        applyEnv(g, opts.vol, atk, dec, dur, t0, envType, opts.punch);
        if (opts.amHz && opts.amDepth) {
            var lfo = ac.createOscillator(), lfoG = ac.createGain();
            lfo.type = 'sine';
            lfo.frequency.value = opts.amHz;
            lfoG.gain.value = opts.amDepth * opts.vol;
            lfo.connect(lfoG); lfoG.connect(g.gain);
            lfo.start(t0); lfo.stop(t0 + dur);
        }
        src.start(t0, off); src.stop(t0 + dur + 0.02);
    }

    /* Random pitch jitter helper for repeat-heavy sounds (flap, coin).
       Returns a multiplier within [1 - cents/1200, 1 + cents/1200].         */
    function jit(maxCents) {
        var c = (Math.random() * 2 - 1) * maxCents;
        return Math.pow(2, c / 1200);
    }

    window.skyPlay = function (name, volume) {
        try {
            var ac = getCtx(), t = ac.currentTime, v = volume || 0.5;
            // Musical anchors (matches game/audio.py _build_bank)
            var A4=440, C5=523.25, D5=587.33, E5=659.25, G5=783.99,
                A5=880, B5=987.77, C6=1046.50, E6=1318.51, G6=1567.98,
                A6=1760, C7=2093.00;

            if (name === 'flap') {
                // Per-call random pitch ±50 cents + new noise offset for organic feel
                var pm = jit(50);
                noise(ac, {start: t, dur: 0.055, vol: 0.40*v, lp: 1100,
                           env: 'punch', dec: 0.025, punch: 0.55});
                tone (ac, {start: t, dur: 0.090, f0: 170*pm, f1: 85*pm,
                           type: 'sine', vol: 0.32*v,
                           env: 'punch', dec: 0.045, punch: 0.55});
            }
            else if (name === 'coin') {
                // Mario perfect-4th arpeggio B5 → E6 with per-call ±25-cent jitter
                var pm = jit(25);
                tone(ac, {start: t, dur: 0.130, f0: B5*pm, type: 'sine',
                          vol: 0.62*v, env: 'punch', dec: 0.080, punch: 0.55,
                          jumpAt: 0.030, jumpToF: E6*pm});
                tone(ac, {start: t + 0.030, dur: 0.040, f0: E6*4*pm,
                          type: 'sine', vol: 0.16*v,
                          env: 'punch', dec: 0.012, punch: 0.45});
            }
            else if (name === 'coin_combo') {
                // Brighter arp E6 → A6
                tone(ac, {start: t, dur: 0.150, f0: E6, type: 'sine',
                          vol: 0.62*v, env: 'punch', dec: 0.090, punch: 0.55,
                          jumpAt: 0.034, jumpToF: A6});
                tone(ac, {start: t + 0.034, dur: 0.045, f0: A6*2,
                          type: 'sine', vol: 0.16*v,
                          env: 'punch', dec: 0.014, punch: 0.40});
            }
            else if (name === 'coin_triple') {
                // Three Mario arps ascending C-E-G, sparkle on the last
                var arp = function (s, d, f1, f2, vol) {
                    tone(ac, {start: s, dur: d, f0: f1, type: 'sine',
                              vol: vol*v, env: 'punch', dec: d*0.55, punch: 0.55,
                              jumpAt: 0.024, jumpToF: f2});
                };
                arp(t,         0.090, C5, G5,    0.55);
                arp(t + 0.090, 0.090, E5, B5,    0.58);
                arp(t + 0.180, 0.130, G5, D5*2,  0.62);
                tone(ac, {start: t + 0.205, dur: 0.045, f0: C7*2, type: 'sine',
                          vol: 0.18*v, env: 'punch', dec: 0.014, punch: 0.45});
            }
            else if (name === 'mushroom') {
                var ms = function (s, f) {
                    tone(ac, {start: s, dur: 0.075, f0: f, type: 'triangle',
                              vol: 0.50*v, env: 'punch', dec: 0.045, punch: 0.40});
                };
                ms(t,         C5); ms(t + 0.070, E5);
                ms(t + 0.140, G5); ms(t + 0.210, C6);
                // Sustained C-major triad
                [C5, E5, G5].forEach(function (f, i) {
                    [+2, -2].forEach(function (det) {
                        tone(ac, {start: t + 0.290, dur: 0.260, f0: f,
                                  type: 'triangle', vol: 0.55*v/3,
                                  atk: 0.006, dec: 0.20, detune: det});
                    });
                });
                tone(ac, {start: t + 0.300, dur: 0.060, f0: C7*2, type: 'sine',
                          vol: 0.16*v, env: 'punch', dec: 0.020, punch: 0.40});
            }
            else if (name === 'magnet') {
                tone(ac, {start: t, dur: 0.220, f0: A4, f1: A5,
                          type: 'triangle', vol: 0.45*v,
                          env: 'punch', dec: 0.150, punch: 0.40,
                          tremHz: 10, tremDepth: 0.18});
                tone(ac, {start: t + 0.110, dur: 0.060, f0: A6, type: 'sine',
                          vol: 0.18*v, env: 'punch', dec: 0.025, punch: 0.30});
            }
            else if (name === 'slowmo') {
                tone(ac, {start: t, dur: 0.300, f0: A5, f1: A4,
                          type: 'triangle', vol: 0.50*v, atk: 0.005, dec: 0.22});
                tone(ac, {start: t, dur: 0.380, f0: A4*0.5, type: 'sine',
                          vol: 0.22*v, atk: 0.040, dec: 0.30});
            }
            else if (name === 'thunder') {
                noise(ac, {start: t, dur: 0.700, vol: 0.55*v, lp: 110,
                           atk: 0.040, dec: 0.55, amHz: 3.2, amDepth: 0.40});
                tone (ac, {start: t, dur: 0.700, f0: 48, f1: 36, type: 'sine',
                           vol: 0.32*v, atk: 0.040, dec: 0.55});
            }
            else if (name === 'death') {
                noise(ac, {start: t, dur: 0.070, vol: 0.40*v, lp: 1200,
                           env: 'punch', dec: 0.040, punch: 0.50});
                tone (ac, {start: t, dur: 0.260, f0: 220, f1: 60,
                           type: 'sine', vol: 0.50*v,
                           env: 'punch', dec: 0.18, punch: 0.30});
                tone (ac, {start: t + 0.080, dur: 0.220, f0: 80, f1: 40,
                           type: 'sine', vol: 0.40*v, atk: 0.005, dec: 0.16});
            }
            else if (name === 'gameover') {
                var go = function (s, f) {
                    tone(ac, {start: s, dur: 0.130, f0: f, type: 'triangle',
                              vol: 0.45*v, env: 'punch', dec: 0.080, punch: 0.30});
                };
                // F4 = A4 - 3 semitones; D4 = A4 - 7 semitones
                var F4 = A4 * Math.pow(2, -3/12), D4 = A4 * Math.pow(2, -7/12);
                go(t, C5); go(t + 0.140, A4); go(t + 0.280, F4);
                [D4, F4, A4].forEach(function (f) {
                    [+2, -2].forEach(function (det) {
                        tone(ac, {start: t + 0.420, dur: 0.320, f0: f,
                                  type: 'triangle', vol: 0.50*v/3,
                                  atk: 0.006, dec: 0.24, detune: det});
                    });
                });
            }
            else if (name === 'poof') {
                noise(ac, {start: t, dur: 0.055, vol: 0.50*v, lp: 900,
                           env: 'punch', dec: 0.030, punch: 0.55});
                tone (ac, {start: t + 0.010, dur: 0.140, f0: 480, f1: 180,
                           type: 'triangle', vol: 0.46*v,
                           env: 'punch', dec: 0.090, punch: 0.35});
                tone (ac, {start: t + 0.020, dur: 0.120, f0: 110, f1: 60,
                           type: 'sine', vol: 0.30*v, atk: 0.003, dec: 0.080});
            }
            else if (name === 'ghost') {
                tone (ac, {start: t, dur: 0.380, f0: 700, f1: 900,
                           type: 'sine', vol: 0.34*v, atk: 0.050, dec: 0.30,
                           vib: 4.5, vibDepth: 0.045});
                noise(ac, {start: t, dur: 0.380, vol: 0.10*v, hp: 2500,
                           atk: 0.060, dec: 0.30});
            }
            else if (name === 'grow') {
                var arp = function (s, d, f1, f2, vol) {
                    tone(ac, {start: s, dur: d, f0: f1, type: 'sine',
                              vol: vol*v, env: 'punch', dec: d*0.55, punch: 0.55,
                              jumpAt: 0.024, jumpToF: f2});
                };
                arp(t,         0.080, C5, G5,    0.55);
                arp(t + 0.080, 0.080, E5, B5,    0.58);
                arp(t + 0.160, 0.090, G5, D5*2,  0.60);
                [C6, E6, G6].forEach(function (f) {
                    [+2, -2].forEach(function (det) {
                        tone(ac, {start: t + 0.260, dur: 0.260, f0: f,
                                  type: 'triangle', vol: 0.50*v/3,
                                  atk: 0.006, dec: 0.20, detune: det});
                    });
                });
                tone(ac, {start: t + 0.275, dur: 0.055, f0: C7*2, type: 'sine',
                          vol: 0.18*v, env: 'punch', dec: 0.020, punch: 0.40});
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
"""
html = html.replace("</body>", INJECTION + "</body>", 1)

html = html.replace("__SB_URL__", _SB_URL)
html = html.replace("__SB_KEY__", _SB_KEY)

src.write_text(html, encoding="utf-8")
print("✓ Skybit theme injected into build/web/index.html")
if _SB_URL:
    print(f"✓ Supabase URL set: {_SB_URL[:40]}...")
else:
    print("⚠ SUPABASE_URL not set — leaderboard will be disabled")
