"""Render the music loop to a WAV for offline listen.

Dumps the exact same loop the native backend would generate, without
needing an audio device. Pure stdlib."""
import sys, pathlib, math, time, wave, struct
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

SAMPLE_RATE = 22050

def shape_val(shape, phase):
    x = math.sin(2 * math.pi * phase)
    if shape == "sine":     return x
    if shape == "square":   return 1.0 if x > 0 else -1.0
    if shape == "triangle":
        p = phase - math.floor(phase); return 4 * abs(p - 0.5) - 1
    return x

def env_val(i, n, a_s, r_s):
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
        buf[i] = int(shape_val(shape, phase) * env_val(i, n, a, r) * vol * 32767)
    return buf

def kick(dur, vol):
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

# Mirrors game/audio.py constants.
CHORDS = (
    (60, (0, 4, 7, 11)),      # Cmaj7
    (57, (0, 3, 7, 10, 14)),  # Am9
    (53, (0, 4, 7, 11)),      # Fmaj7
    (55, (0, 5, 7, 10)),      # G7sus4
)
SECTIONS = (
    (True, True, False, False, False),
    (True, True, True,  False, False),
    (True, True, True,  True,  True ),
    (True, True, True,  False, False),
)
ARP_PATTERNS = (
    (0, 1, 2, 3, 2, 1, 0, 1),
    (0, 2, 1, 3, 2, 0, 3, 1),
    (0, 2, 3, 2, 1, 3, 2, 0),
    (0, 2, 1, 3, 0, 2, 1, 3),
)
LEAD_DEGS = (0, 7, 11, 14, 7, 11, 0, 7)
BPM = 78; BEAT = 60.0 / BPM; BAR = BEAT * 4
BARS_TOTAL = 16; BARS_PER_SECTION = 4

t0 = time.time()
total = BARS_TOTAL * BAR
n = int(total * SAMPLE_RATE)
mix = [0] * n
for bar in range(BARS_TOTAL):
    sec = SECTIONS[(bar // BARS_PER_SECTION) % len(SECTIONS)]
    sub_on, pad_on, arp_on, kick_on, lead_on = sec
    root, offs = CHORDS[bar % len(CHORDS)]
    bar_start = bar * BAR
    i0 = int(bar_start * SAMPLE_RATE)
    if sub_on:
        acc(mix, voice(BAR * 0.95, midi_hz(root - 12), "sine", 0.19, a=0.35, r=0.35), i0)
    if pad_on:
        for off in offs:
            for det in (-5, +5):
                acc(mix, voice(BAR * 0.98, midi_hz(root + off), "triangle",
                               0.045, detune=det, a=0.45, r=0.55), i0)
    if arp_on:
        pat = ARP_PATTERNS[(bar // BARS_PER_SECTION) % len(ARP_PATTERNS)]
        dur_n = BEAT * 0.45
        for i in range(8):
            idx = pat[i] % len(offs)
            note = root + offs[idx] + 12
            t = bar_start + i * (BEAT / 2)
            acc(mix, voice(dur_n, midi_hz(note), "sine", 0.075, a=0.006, r=0.12),
                int(t * SAMPLE_RATE))
    if kick_on:
        k = kick(0.12, 0.45)
        for beat in (0, 2):
            acc(mix, k, int((bar_start + beat * BEAT) * SAMPLE_RATE))
    if lead_on:
        base = (bar % 4) * 2
        for i in range(2):
            deg = LEAD_DEGS[(base + i) % len(LEAD_DEGS)]
            t = bar_start + i * (BAR / 2)
            for det in (-4, +4):
                acc(mix, voice(BAR * 0.48, midi_hz(root + deg + 12), "sine",
                               0.085, detune=det, a=0.06, r=0.45),
                    int(t * SAMPLE_RATE))

for i in range(n):
    s = mix[i]
    if s > 32767: s = 32767
    elif s < -32768: s = -32768
    mix[i] = s
t1 = time.time()
print(f"generated {total:.1f}s in {t1 - t0:.2f}s")

out = pathlib.Path("/home/user/Claude_test/docs/music_preview.wav")
w = wave.open(str(out), 'wb')
w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
w.writeframes(b''.join(struct.pack('<h', s) for s in mix))
w.close()
print("wrote", out, f"({out.stat().st_size/1024:.0f} KB)")
