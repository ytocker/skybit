"""Render the music loop to a WAV for offline listen. Uses stdlib only — no
audio device needed."""
import os, sys, pathlib, math, time
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

# Bypass pygame mixer entirely; borrow the generator math from audio.py
SAMPLE_RATE = 22050

def shape_val(shape, phase):
    x = math.sin(2 * math.pi * phase)
    if shape == "sine":     return x
    if shape == "square":   return 1.0 if x > 0 else -1.0
    if shape == "triangle":
        p = phase - math.floor(phase); return 4 * abs(p - 0.5) - 1
    return x

def env_val(i, n, a_s=0.008, r_s=0.12):
    a = max(1, int(a_s * SAMPLE_RATE)); r = max(1, int(r_s * SAMPLE_RATE))
    if i < a: return i / a
    if i > n - r: return max(0.0, (n - i) / r)
    return 1.0

def midi_hz(m): return 440.0 * (2.0 ** ((m - 69) / 12.0))

def voice(dur, freq, shape, vol, detune=0.0, a=0.02, r=0.10):
    n = int(dur * SAMPLE_RATE); f = freq * (2.0 ** (detune / 1200.0))
    phase = 0.0; buf = [0] * n
    for i in range(n):
        phase += f / SAMPLE_RATE
        e = env_val(i, n, a, r)
        buf[i] = int(shape_val(shape, phase) * e * vol * 32767)
    return buf

def kick(dur, vol=0.95):
    n = int(dur * SAMPLE_RATE); phase = 0.0; buf = [0] * n
    for i in range(n):
        t = i / max(1, n)
        f = 60.0 * math.exp(-3.0 * t) + 40.0
        phase += f / SAMPLE_RATE
        amp = math.exp(-6.0 * t) * vol
        buf[i] = int(math.sin(2 * math.pi * phase) * amp * 32767)
    return buf

def acc(tgt, src, start):
    m = min(len(src), len(tgt) - start)
    for i in range(m): tgt[start + i] += src[i]

CHORDS = ((54, (0, 3, 7)), (50, (0, 4, 7)), (57, (0, 4, 7)), (52, (0, 4, 7)))
LEAD = (0, 3, 7, 5, 3, 7, 5, 2)
BPM = 110; BAR = 60.0 / BPM * 4; BEAT = 60.0 / BPM
bars_per_chord = 2
total_sec = bars_per_chord * len(CHORDS) * BAR
n = int(total_sec * SAMPLE_RATE)
mix = [0] * n
t0 = time.time()
k = kick(0.09, 0.95)
for bar in range(bars_per_chord * len(CHORDS)):
    for beat in range(4):
        acc(mix, k, int((bar * BAR + beat * BEAT) * SAMPLE_RATE))
for ci, (root, triad) in enumerate(CHORDS):
    slot = ci * bars_per_chord * BAR
    dur = bars_per_chord * BAR
    for bar in range(bars_per_chord):
        for beat in range(4):
            note = root - 24 + (7 if beat in (1, 3) else 0)
            start = int((slot + bar * BAR + beat * BEAT) * SAMPLE_RATE)
            acc(mix, voice(BEAT * 0.92, midi_hz(note), "square", 0.18, a=0.005, r=0.04), start)
    for off in triad:
        note = root + off
        start = int(slot * SAMPLE_RATE)
        acc(mix, voice(dur, midi_hz(note), "triangle", 0.060, detune=-3, a=0.12, r=0.18), start)
        acc(mix, voice(dur, midi_hz(note), "triangle", 0.060, detune=+3, a=0.12, r=0.18), start)
    note_dur = BEAT * 0.55
    ms = (0, 2, 3, 5, 7, 8, 10, 12)
    for rep in range(bars_per_chord):
        for i, deg in enumerate(LEAD):
            note = root + 12 + ms[deg]
            t = slot + rep * BAR + i * (BAR / len(LEAD))
            start = int(t * SAMPLE_RATE)
            for det in (-6, +6):
                acc(mix, voice(note_dur, midi_hz(note), "sine", 0.12, detune=det, a=0.008, r=0.10), start)
for i in range(n):
    s = mix[i]
    if s > 32767: s = 32767
    elif s < -32768: s = -32768
    mix[i] = s
t1 = time.time()
print(f"generated {total_sec:.1f}s in {t1 - t0:.2f}s")

import wave, struct
out = pathlib.Path("/home/user/Claude_test/docs/music_preview.wav")
w = wave.open(str(out), 'wb')
w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
w.writeframes(b''.join(struct.pack('<h', s) for s in mix))
w.close()
print("wrote", out, f"({out.stat().st_size/1024:.0f} KB)")
