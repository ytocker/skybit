"""Orchestrator verification for the alpine night redesign (round check).

Two independent checks the design loop relies on:
  1. Integrity of the study overrides (day frozen, night darker-than-sunset but
     above the lifted floor, star_alpha monotone into night).
  2. Engine-path brightness: render the interpolated night palette through the
     REAL live path `game.draw.get_sky_surface_biome` (4 stops, NO zenith_dark)
     — not the preview's paint_sky — and sample the zenith band, so we know the
     lift survives in-engine and isn't a preview-only artifact.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((8, 8))

from tools.sky_alpine_sunsets import CONCEPTS, _ALPINE_HAZE_KF
from game import draw

W, H, GROUND_Y = 480, 720, 560
DAY_PHASES = (0.06, 0.18, 0.30)
FLOOR = (14, 16, 40)

# Raw override tables live behind the composed specs; re-pull them by reading the
# module objects' keyframes is lossy (already retimed), so re-derive the raw
# night/sunset frames from the source dicts via the spec's pre-retime intent:
# easiest is to read the 0.50 sunset and 0.72 night straight from each spec's
# composed keyframes by matching the retimed phases. Instead we inspect the
# module-level override dicts directly.
# Retimed phases: sunset 0.50 -> 0.37, deep-night 0.72 -> 0.56, dusk 0.62 -> 0.47,
# twilight 0.68 -> 0.52.
SUNSET_P, DUSK_P, TWI_P, NIGHT_P = 0.37, 0.47, 0.52, 0.56

print("=== 1. INTEGRITY (composed keyframes) ===")
fails = []
# Day frames identical across all composed specs
day_ref = None
for name, spec in CONCEPTS:
    kf = dict((round(p, 4), d) for p, d in spec.keyframes)
    # retimed day phases: 0.06->0.04, 0.18->0.12, 0.30->0.20
    day = {p: kf[p] for p in (0.04, 0.12, 0.20)}
    sig = tuple((p, day[p]['sky_top'], day[p]['sky_mid'], day[p]['sky_bot'], day[p]['horizon']) for p in (0.04, 0.12, 0.20))
    if day_ref is None:
        day_ref = sig
    elif sig != day_ref:
        fails.append(f"{name}: DAY frames differ from row1")

def val(rgb):  # perceived-ish luminance proxy
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

for label, spec in CONCEPTS:
    if 'live' in label.lower():
        continue  # the black reference is intentionally below the new floor
    kf = dict((round(p, 4), d) for p, d in spec.keyframes)
    sunset_top = kf[SUNSET_P]['sky_top']
    night_top = kf[NIGHT_P]['sky_top']
    # night darker than sunset (value)
    if not (val(night_top) < val(sunset_top)):
        fails.append(f"{label}: night sky_top {night_top} NOT darker than sunset {sunset_top}")
    # above floor (each channel >= floor)
    if night_top[0] < FLOOR[0] or night_top[1] < FLOOR[1] or night_top[2] < FLOOR[2]:
        fails.append(f"{label}: night sky_top {night_top} BELOW floor {FLOOR}")
    # star_alpha monotone non-decreasing dusk->twilight->night
    sa = [kf[DUSK_P]['star_alpha'], kf[TWI_P]['star_alpha'], kf[NIGHT_P]['star_alpha']]
    if not (sa[0] <= sa[1] <= sa[2]):
        fails.append(f"{label}: star_alpha not monotone into night: {sa}")
    print(f"  {label:22s} night_top={night_top} val={val(night_top):5.1f} (sunset val={val(sunset_top):5.1f}) star={sa}")

print("  -> " + ("ALL PASS" if not fails else f"{len(fails)} FAIL"))
for f in fails:
    print("   !", f)

print("\n=== 2. ENGINE-PATH zenith brightness (live draw.get_sky_surface_biome) ===")
# Sample the redesigned rows vs the LIVE black reference at the deep-night phase.
# Retimed deep-night sits ~0.56 (from 0.72) holding to 0.82; sample both.
def zenith_mean(spec, phase, band_frac=0.06):
    pal = spec.palette_for_phase(phase)
    draw._sky_b_cache.clear()
    surf = draw.get_sky_surface_biome(W, H, GROUND_Y, pal, int(phase * 240))
    band = max(1, int(GROUND_Y * band_frac))
    r = g = b = 0
    n = 0
    for y in range(band):
        for x in range(0, W, 8):
            c = surf.get_at((x, y))
            r += c[0]; g += c[1]; b += c[2]; n += 1
    return (r / n, g / n, b / n)

# A representative spread of rows plus the LIVE reference, derived from CONCEPTS
# so the table survives row renames across study revisions.
_live_name = next((s.name for cid, s in CONCEPTS if 'live' in cid.lower()), None)
samples = [s.name for cid, s in CONCEPTS if 'live' not in cid.lower()][:4]
if _live_name:
    samples.append(_live_name)
by_name = {s.name: s for _, s in CONCEPTS}
for ph in (0.58, 0.82):
    print(f"  -- phase {ph} --")
    for nm in samples:
        spec = by_name[nm]
        zr, zg, zb = zenith_mean(spec, ph)
        print(f"    {nm:42s} zenith RGB=({zr:5.1f},{zg:5.1f},{zb:5.1f}) val={val((zr,zg,zb)):5.1f}")

print("\n=== 3. ENGINE-PATH sunset-vs-night zenith DELTA (invariant: night clearly darker) ===")
# Sunset peak retimes 0.50->0.37; deep-night 0.72->0.56 holding to 0.82. Sample
# the live-rendered zenith at both and require night to sit clearly below sunset.
TARGET = 5.0
inv_fail = []
for short, spec in CONCEPTS:
    if 'live' in short.lower():
        continue
    sv = val(zenith_mean(spec, 0.37))
    nv = val(zenith_mean(spec, 0.58))
    delta = sv - nv
    flag = "" if delta >= TARGET else f"  <-- below +{TARGET:.0f} target"
    print(f"  {short:22s} sunset_zen={sv:5.1f}  night_zen={nv:5.1f}  delta={delta:+6.1f}{flag}")
    if delta < TARGET:
        inv_fail.append((short, delta))
print("  -> " + ("ALL deltas >= +%.0f" % TARGET if not inv_fail
                  else "PINCHED: " + ", ".join(f"{n}({d:+.1f})" for n, d in inv_fail)))

print("\nDONE")
