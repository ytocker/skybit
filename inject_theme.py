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

    /* Build a fresh "warm bus" per-call: BiquadFilter LP + master gain
       feeding ac.destination. Voices route here instead of straight to
       destination so the entire mix is filtered + scaled together. */
    function warmBus(ac, lpHz, master) {
        var lp = ac.createBiquadFilter();
        lp.type = 'lowpass';
        lp.frequency.value = lpHz || 1800;
        lp.Q.value = 0.5;
        var mg = ac.createGain();
        mg.gain.value = master === undefined ? 0.55 : master;
        lp.connect(mg); mg.connect(opts.dest || ac.destination);
        return lp;  // voices connect their output here
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
        osc.connect(g); g.connect(opts.dest || ac.destination);
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
        node.connect(g); g.connect(opts.dest || ac.destination);
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

    /* Bell voice (2-op FM). The modulator's amplitude (the FM "index") is
       what gives bells their bright clangourous attack; it decays faster
       than the carrier's amplitude, leaving a pure sine ring afterwards.
       mod_ratio in 1.0-2.0 → kalimba/wood; 3-5 → glockenspiel/bell;
       6-9 → temple bell / gong (inharmonic, metallic).                     */
    function bell(ac, opts) {
        var t0 = opts.start;
        var dur = opts.dur;
        var f = opts.f;
        var modR = opts.modRatio || 3.5;
        var modI = (opts.modIndex === undefined) ? 2.0 : opts.modIndex;
        var modDec = (opts.modDec === undefined) ? 0.08 : opts.modDec;
        var dec = (opts.dec === undefined ? dur * 0.5 : opts.dec);
        var atk = (opts.atk === undefined ? 0.0 : opts.atk);
        var envType = opts.env || 'punch';
        var car = ac.createOscillator(), mod = ac.createOscillator();
        var modGain = ac.createGain();      // FM index (Hz of carrier deviation)
        var ampGain = ac.createGain();
        car.type = 'sine'; mod.type = 'sine';
        car.frequency.setValueAtTime(f, t0);
        // Optional pitch jump (Mario-style arpeggio applied to the bell)
        if (opts.jumpAt !== undefined && opts.jumpToF !== undefined) {
            car.frequency.setValueAtTime(opts.jumpToF, t0 + opts.jumpAt);
            mod.frequency.setValueAtTime(opts.jumpToF * modR, t0 + opts.jumpAt);
        }
        mod.frequency.setValueAtTime(f * modR, t0);
        // Initial mod depth in Hz, decays exponentially to ≈0 over ~3·modDec
        var startDepth = modI * f * modR;
        modGain.gain.setValueAtTime(startDepth, t0);
        modGain.gain.setTargetAtTime(0, t0, Math.max(0.001, modDec / 3));
        mod.connect(modGain); modGain.connect(car.frequency);
        car.connect(ampGain); ampGain.connect(opts.dest || ac.destination);
        applyEnv(ampGain, opts.vol, atk, dec, dur, t0, envType, opts.punch);
        car.start(t0); car.stop(t0 + dur + 0.02);
        mod.start(t0); mod.stop(t0 + dur + 0.02);
    }

    /* Karplus-Strong pluck. Web Audio doesn't expose a per-sample feedback
       loop, but a delay node fed into itself approximates it well enough.
       Used for the soft wood-mallet flap.                                   */
    function pluck(ac, opts) {
        var t0 = opts.start;
        var dur = opts.dur;
        var f = opts.f;
        var src = ac.createBufferSource();
        // Tiny noise burst as the "pluck excitation"
        var burstLen = Math.floor(ac.sampleRate / Math.max(20, f));
        var buf = ac.createBuffer(1, burstLen, ac.sampleRate);
        var d = buf.getChannelData(0);
        for (var i = 0; i < burstLen; i++) d[i] = (Math.random() * 2 - 1) * 0.6;
        src.buffer = buf;
        var dly = ac.createDelay(0.05);
        var fb = ac.createGain();
        var lpf = ac.createBiquadFilter();
        lpf.type = 'lowpass'; lpf.frequency.value = 4000; lpf.Q.value = 0.5;
        var ampGain = ac.createGain();
        dly.delayTime.value = 1 / Math.max(20, f);
        fb.gain.value = (opts.decay === undefined ? 0.96 : opts.decay);
        // Topology: src → dly → lpf → fb → dly  (loop) and dly → ampGain → out
        src.connect(dly);
        dly.connect(lpf); lpf.connect(fb); fb.connect(dly);
        dly.connect(ampGain); ampGain.connect(opts.dest || ac.destination);
        applyEnv(ampGain, opts.vol, 0.0, dur * 0.55, dur, t0, 'punch', 0.30);
        src.start(t0); src.stop(t0 + 0.005);
    }

    window.skyPlay = function (name, volume) {
        try {
            var ac = getCtx(), t = ac.currentTime, v = volume || 0.5;
            // Sky Garden palette: warm kalimba (mod_ratio=1.0), low-mid
            // register only, master LP at 1800Hz, master gain at 0.55,
            // no high sparkle pings.
            var bus = warmBus(ac, 1800, 0.55);
            var DST = bus;

            // Musical anchors — Sky Garden uses lower octaves
            var A3=220, C4=261.63, D4=293.66, E4=329.63, F4=349.23, G4=392,
                A4=440, B4=493.88, C5=523.25, E5=659.25, G5=783.99;

            // Warm kalimba helper (matches game/audio.py _kalimba)
            var kalimba = function (start, dur, f, vol, jumpAt, jumpToF, dec, punch) {
                bell(ac, {start: start, dur: dur, f: f, modRatio: 1.0,
                          modIndex: 1.6, modDec: 0.05, vol: vol,
                          env: 'punch', punch: (punch === undefined ? 0.30 : punch),
                          dec: (dec === undefined ? dur * 0.55 : dec),
                          jumpAt: jumpAt, jumpToF: jumpToF, dest: DST});
            };

            if (name === 'flap') {
                var pm = jit(30);
                pluck(ac, {start: t, dur: 0.080, f: 110 * pm, vol: 0.42*v,
                           decay: 0.96, dest: DST});
            }
            else if (name === 'coin') {
                // Single warm kalimba pluck C5 → G4 (perfect 4th DOWN, gentle)
                var pm = jit(30);
                kalimba(t, 0.260, C5 * pm, 0.50*v, 0.040, G4 * pm, 0.20, 0.30);
            }
            else if (name === 'coin_combo') {
                kalimba(t, 0.280, E5, 0.50*v, 0.044, B4, 0.22, 0.32);
            }
            else if (name === 'coin_triple') {
                kalimba(t,         0.180, C4, 0.45*v, undefined, undefined, 0.13, 0.30);
                kalimba(t + 0.090, 0.190, E4, 0.48*v, undefined, undefined, 0.14, 0.30);
                kalimba(t + 0.180, 0.260, G4, 0.52*v, undefined, undefined, 0.20, 0.32);
            }
            else if (name === 'mushroom') {
                kalimba(t,         0.140, C4, 0.45*v, undefined, undefined, 0.10, 0.28);
                kalimba(t + 0.080, 0.140, E4, 0.45*v, undefined, undefined, 0.10, 0.28);
                kalimba(t + 0.160, 0.140, G4, 0.45*v, undefined, undefined, 0.10, 0.28);
                kalimba(t + 0.240, 0.180, C5, 0.50*v, undefined, undefined, 0.13, 0.32);
                // Soft pad triad (sine)
                [{f:C4,vl:0.18}, {f:E4,vl:0.16}, {f:G4,vl:0.14}].forEach(function (n) {
                    tone(ac, {start: t + 0.340, dur: 0.420, f0: n.f,
                              type: 'sine', vol: n.vl*v,
                              atk: 0.040, dec: 0.32, dest: DST});
                });
            }
            else if (name === 'magnet') {
                kalimba(t, 0.300, A3, 0.48*v, 0.140, A4, 0.22, 0.30);
            }
            else if (name === 'slowmo') {
                kalimba(t, 0.420, E5, 0.45*v, 0.180, A3, 0.32, 0.28);
                tone(ac, {start: t, dur: 0.520, f0: A3*0.5, type: 'sine',
                          vol: 0.18*v, atk: 0.060, dec: 0.40, dest: DST});
            }
            else if (name === 'thunder') {
                noise(ac, {start: t, dur: 0.700, vol: 0.42*v, lp: 110,
                           atk: 0.040, dec: 0.55,
                           amHz: 3.2, amDepth: 0.40, dest: DST});
                tone (ac, {start: t, dur: 0.700, f0: 45, f1: 35, type: 'sine',
                           vol: 0.30*v, atk: 0.040, dec: 0.55, dest: DST});
            }
            else if (name === 'death') {
                pluck(ac, {start: t, dur: 0.180, f: 90, vol: 0.55*v,
                           decay: 0.96, dest: DST});
                tone (ac, {start: t, dur: 0.350, f0: 80, f1: 40, type: 'sine',
                           vol: 0.40*v, env: 'punch', dec: 0.22, punch: 0.35,
                           dest: DST});
                noise(ac, {start: t, dur: 0.050, vol: 0.18*v, lp: 600,
                           env: 'punch', dec: 0.030, punch: 0.40, dest: DST});
            }
            else if (name === 'gameover') {
                kalimba(t,         0.220, C5, 0.42*v, undefined, undefined, 0.16, 0.25);
                kalimba(t + 0.220, 0.220, A4, 0.42*v, undefined, undefined, 0.16, 0.25);
                kalimba(t + 0.440, 0.260, F4, 0.42*v, undefined, undefined, 0.18, 0.25);
                [{f:D4,vl:0.20}, {f:F4,vl:0.18}, {f:A4,vl:0.16}].forEach(function (n) {
                    tone(ac, {start: t + 0.580, dur: 0.440, f0: n.f,
                              type: 'sine', vol: n.vl*v,
                              atk: 0.060, dec: 0.34, dest: DST});
                });
            }
            else if (name === 'poof') {
                pluck(ac, {start: t, dur: 0.080, f: 180, vol: 0.50*v,
                           decay: 0.97, dest: DST});
                tone (ac, {start: t + 0.010, dur: 0.180, f0: 220, f1: 110,
                           type: 'sine', vol: 0.30*v,
                           env: 'punch', dec: 0.12, punch: 0.30, dest: DST});
            }
            else if (name === 'ghost') {
                tone(ac, {start: t, dur: 0.500, f0: 330, type: 'sine',
                          vol: 0.32*v, atk: 0.060, dec: 0.40,
                          vib: 4.0, vibDepth: 0.030, dest: DST});
                tone(ac, {start: t + 0.020, dur: 0.460, f0: 220, type: 'sine',
                          vol: 0.20*v, atk: 0.080, dec: 0.36, dest: DST});
            }
            else if (name === 'grow') {
                kalimba(t,         0.180, C4, 0.45*v, undefined, undefined, 0.13, 0.28);
                kalimba(t + 0.090, 0.190, E4, 0.48*v, undefined, undefined, 0.14, 0.28);
                kalimba(t + 0.180, 0.230, G4, 0.50*v, undefined, undefined, 0.17, 0.30);
                [{f:C4,vl:0.18}, {f:E4,vl:0.16}, {f:G4,vl:0.14}].forEach(function (n) {
                    tone(ac, {start: t + 0.330, dur: 0.460, f0: n.f,
                              type: 'sine', vol: n.vl*v,
                              atk: 0.050, dec: 0.36, dest: DST});
                });
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
