// Synthesized SFX using Web Audio API. No files.
// Call unlock() on the first user gesture to satisfy autoplay policies.

let ctx = null;
let master = null;
let muted = false;

function ensure() {
    if (ctx) return ctx;
    const AC = window.AudioContext || window.webkitAudioContext;
    ctx = new AC();
    master = ctx.createGain();
    master.gain.value = 0.28;
    master.connect(ctx.destination);
    return ctx;
}

export function unlock() {
    ensure();
    if (ctx.state === 'suspended') ctx.resume();
}

export function setMuted(m) { muted = !!m; if (master) master.gain.value = muted ? 0 : 0.28; }
export function isMuted() { return muted; }

function tone({ freq = 440, freq2 = null, dur = 0.08, type = 'square', vol = 0.3, attack = 0.002, decay = 0.06, when = 0 }) {
    ensure();
    const t0 = ctx.currentTime + when;
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t0);
    if (freq2 != null) osc.frequency.exponentialRampToValueAtTime(Math.max(20, freq2), t0 + dur);
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(vol, t0 + attack);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + attack + decay);
    osc.connect(g).connect(master);
    osc.start(t0);
    osc.stop(t0 + attack + decay + 0.02);
}

function noise({ dur = 0.1, vol = 0.2, hp = 800 }) {
    ensure();
    const t0 = ctx.currentTime;
    const len = Math.floor(ctx.sampleRate * dur);
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < len; i++) ch[i] = (Math.random() * 2 - 1) * (1 - i / len);
    const src = ctx.createBufferSource();
    src.buffer = buf;
    const g = ctx.createGain();
    g.gain.setValueAtTime(vol, t0);
    g.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    const f = ctx.createBiquadFilter();
    f.type = 'highpass';
    f.frequency.value = hp;
    src.connect(f).connect(g).connect(master);
    src.start(t0);
    src.stop(t0 + dur + 0.02);
}

export const sfx = {
    flap() { tone({ freq: 520, freq2: 760, dur: 0.07, type: 'triangle', vol: 0.18, decay: 0.07 }); },
    coin() {
        tone({ freq: 988, dur: 0.05, type: 'square', vol: 0.18, decay: 0.05 });
        tone({ freq: 1319, dur: 0.09, type: 'square', vol: 0.18, decay: 0.09, when: 0.05 });
    },
    combo(n) {
        const base = 880 + Math.min(6, n) * 60;
        tone({ freq: base, dur: 0.05, type: 'square', vol: 0.16 });
        tone({ freq: base * 1.5, dur: 0.08, type: 'square', vol: 0.14, when: 0.04 });
    },
    mushroom() {
        tone({ freq: 440, freq2: 880, dur: 0.12, type: 'square', vol: 0.18 });
        tone({ freq: 660, freq2: 1320, dur: 0.16, type: 'triangle', vol: 0.2, when: 0.08 });
        tone({ freq: 880, freq2: 1760, dur: 0.22, type: 'square', vol: 0.16, when: 0.18 });
    },
    hit() {
        tone({ freq: 220, freq2: 60, dur: 0.25, type: 'sawtooth', vol: 0.22, decay: 0.25 });
        noise({ dur: 0.18, vol: 0.16, hp: 400 });
    },
    score() { tone({ freq: 660, dur: 0.06, type: 'square', vol: 0.14 }); },
    click() { tone({ freq: 880, dur: 0.04, type: 'square', vol: 0.12, decay: 0.04 }); },
};
