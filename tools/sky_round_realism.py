"""
Realism round: 10 full-day sky concepts grounded in how a REAL sky behaves.

The single governing principle — authored into every keyframe below — is:

    Warmth lives LOW; cool lives HIGH; darkness falls from the top down.

So each design's day->night->dawn SEQUENCE reads believably by getting three
things right at once: (a) the colour ORDER, (b) the vertical POSITION of colour
at each instant, and (c) the phase TIMING/proportions. The chromatic arc is the
same one a clear-air sky actually walks:

  * DAY      — deepest, most-saturated blue at the zenith, paling to a lighter,
               hazier near-white (sometimes faintly warm) at the horizon. The
               LONGEST phase, held by near-identical anchors at 0.05/0.16/0.27.
  * GOLDEN   — a warm gold wash CONCENTRATED LOW near the sun; sky_top stays
               blue but begins to warm. Soft, short.
  * SUNSET   — the drama as a thin LOW band: intense yellow->orange->red hugging
               the horizon, climbing through orange->peach->pink in bot/mid,
               while sky_top STAYS COOL and starts to darken. NARROW + LOW so it
               never floods the whole dome (the #1 realism failure to avoid).
  * BLUE HR  — the Belt of Venus: a pink/salmon mid band riding ~10-20 deg up
               (a sky_mid PINKER than the stops both above AND below it) over a
               dark blue-grey Earth-shadow band rising from the horizon (sky_bot
               darker/bluer than that pink mid). Deep saturated cool blue dome;
               first stars.
  * TWILIGHT — deep blue darkening to indigo/navy; the last glow sinks; stars
               ramp to full.
  * NIGHT    — very dark desaturated navy/indigo, NEVER pure black (every channel
               held above a ~(12,14,32) airglow floor), stars at max. HELD — the
               longest dark phase, near-identical anchors at 0.66 and 0.80.
  * DAWN     — the whole sequence in reverse (Belt/Earth-shadow now on the other
               side), read a touch quicker than dusk, resolving back to the day.

The vividness is craft, not saturation slammers: warm horizon vs cool zenith at
the SAME instant gives the OKLab bake a real arc to travel so the midband stays
saturated instead of slumping to grey. `positions` keeps the warm sunset band
low and narrow and places the Belt-of-Venus pink at mid height.

The shared realistic clock (phase linear in gameplay time over the 320 s cycle):
  DAY 0.00-0.30 (30%) · GOLDEN 0.30-0.36 (6%) · SUNSET 0.36-0.43 (7%) ·
  BELT/BLUE-HOUR 0.43-0.52 (9%) · NAUTICAL->ASTRO 0.52-0.60 (8%) ·
  NIGHT 0.60-0.82 (22%, held) · DAWN 0.82-0.95 (13%) · SUNRISE 0.95-1.00 (5%).
`make_palette` wraps the last anchor -> the first through 1.0, so the night/dawn
seam stays continuous.

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through the two `tools/preview_sky_round_realism*.py` sheets.
Pure-Pygame / pygbag-safe (the keyframes are just colour tables; the OKLab bake
lives in the engine).
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# Every design shares the SAME phase anchors so all 10 walk one realistic clock;
# only the colours and `SkyParams` differ. Anchors, in cycle order:
#   day      0.05 / 0.16 / 0.27   (held — longest phase)
#   golden   0.33
#   sunset   0.39
#   belt     0.47                 (Belt of Venus / blue hour)
#   twilight 0.55                 (nautical -> astronomical)
#   night    0.66 / 0.80          (held — longest dark phase)
#   dawn     0.88
#   sunrise  0.96
# `make_palette` wraps 0.96 -> 0.05 through 1.0, so the dark side is continuous.


# ── 1. Cobalt Alpine — clear thin-air cobalt day, classic textbook twilight ────
# The reference design: a deep cobalt zenith over a pale hazy horizon, the most
# "correct" walk through golden/sunset/belt — every other design is a deviation
# from this baseline.
_ALPINE_KF = [
    (0.05, dict(sky_top=(28, 84, 192), sky_mid=(74, 142, 224), sky_bot=(158, 200, 238), horizon=(214, 232, 244), star_alpha=0)),
    (0.16, dict(sky_top=(24, 80, 196), sky_mid=(70, 140, 226), sky_bot=(154, 200, 240), horizon=(216, 234, 246), star_alpha=0)),
    (0.27, dict(sky_top=(30, 84, 190), sky_mid=(78, 144, 222), sky_bot=(162, 202, 236), horizon=(220, 234, 242), star_alpha=0)),
    (0.33, dict(sky_top=(36, 86, 184), sky_mid=(102, 144, 206), sky_bot=(228, 198, 162), horizon=(255, 206, 124), star_alpha=0)),
    (0.39, dict(sky_top=(40, 70, 150), sky_mid=(154, 124, 158), sky_bot=(255, 158, 102), horizon=(252, 138, 70), star_alpha=10)),
    (0.47, dict(sky_top=(28, 46, 116), sky_mid=(150, 110, 154), sky_bot=(70, 88, 138), horizon=(228, 150, 120), star_alpha=60)),
    (0.55, dict(sky_top=(16, 28, 84), sky_mid=(34, 54, 116), sky_bot=(48, 74, 132), horizon=(96, 110, 158), star_alpha=140)),
    (0.66, dict(sky_top=(13, 16, 52), sky_mid=(16, 26, 70), sky_bot=(22, 38, 88), horizon=(34, 58, 110), star_alpha=235)),
    (0.80, dict(sky_top=(13, 16, 50), sky_mid=(16, 26, 68), sky_bot=(22, 38, 86), horizon=(34, 56, 108), star_alpha=235)),
    (0.88, dict(sky_top=(24, 40, 108), sky_mid=(110, 96, 150), sky_bot=(70, 92, 144), horizon=(238, 156, 122), star_alpha=70)),
    (0.96, dict(sky_top=(30, 80, 182), sky_mid=(86, 148, 220), sky_bot=(178, 208, 236), horizon=(248, 222, 174), star_alpha=10)),
]

COBALT_ALPINE = BiomeSpec(
    name='Cobalt Alpine',
    note='Clear thin-air cobalt day paling to a hazy horizon; the textbook walk — low gold, a narrow red sunset band, a clean Belt of Venus over Earth-shadow blue, deep navy night.',
    keyframes=_ALPINE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.60, 0.86, 1.0), dither_amp=2.0, zenith_dark=0.12),
)


# ── 2. Desert Warm-Pale — bleached warm-blue day, dust-amber low sunset ────────
# A hot dry sky: the day blue is paler and the horizon carries a warm dust haze,
# so noon already reads sun-baked. The sunset goes deep amber-red, low, with a
# strong Earth-shadow at the belt.
_DESERT_KF = [
    (0.05, dict(sky_top=(58, 122, 196), sky_mid=(140, 180, 210), sky_bot=(228, 222, 202), horizon=(252, 230, 184), star_alpha=0)),
    (0.16, dict(sky_top=(54, 118, 200), sky_mid=(136, 178, 212), sky_bot=(226, 222, 200), horizon=(253, 228, 180), star_alpha=0)),
    (0.27, dict(sky_top=(60, 122, 194), sky_mid=(144, 182, 210), sky_bot=(230, 222, 198), horizon=(254, 226, 176), star_alpha=0)),
    (0.33, dict(sky_top=(66, 118, 184), sky_mid=(150, 168, 198), sky_bot=(244, 212, 168), horizon=(255, 206, 120), star_alpha=0)),
    (0.39, dict(sky_top=(62, 86, 148), sky_mid=(178, 134, 138), sky_bot=(255, 158, 96), horizon=(238, 96, 58), star_alpha=10)),
    (0.47, dict(sky_top=(40, 52, 112), sky_mid=(170, 116, 132), sky_bot=(78, 78, 116), horizon=(222, 134, 96), star_alpha=60)),
    (0.55, dict(sky_top=(22, 30, 78), sky_mid=(48, 52, 102), sky_bot=(62, 66, 110), horizon=(120, 100, 122), star_alpha=140)),
    (0.66, dict(sky_top=(12, 16, 50), sky_mid=(18, 24, 66), sky_bot=(24, 34, 82), horizon=(36, 46, 100), star_alpha=235)),
    (0.80, dict(sky_top=(12, 16, 48), sky_mid=(18, 24, 64), sky_bot=(24, 34, 80), horizon=(36, 44, 98), star_alpha=235)),
    (0.88, dict(sky_top=(28, 38, 100), sky_mid=(128, 96, 134), sky_bot=(78, 80, 116), horizon=(232, 138, 96), star_alpha=70)),
    (0.96, dict(sky_top=(56, 114, 188), sky_mid=(136, 174, 214), sky_bot=(226, 218, 196), horizon=(255, 216, 158), star_alpha=10)),
]

DESERT_WARM_PALE = BiomeSpec(
    name='Desert Warm-Pale',
    note='Bleached warm-blue day over a dust-hazed horizon, sun-baked at noon; a deep amber-red low sunset and a strong slate Earth-shadow at the belt.',
    keyframes=_DESERT_KF,
    sky=SkyParams(positions=(0.0, 0.28, 0.58, 0.84, 1.0), dither_amp=2.6, zenith_dark=0.10),
)


# ── 3. Tropical Aqua — turquoise-edged day, coral-reef sunset, teal blue-hour ──
# Maritime humid air: a saturated cyan zenith over a turquoise-aqua horizon, the
# sunset coral over the warm sea, the night a deep teal-navy.
_AQUA_KF = [
    (0.05, dict(sky_top=(30, 130, 206), sky_mid=(96, 188, 222), sky_bot=(168, 224, 222), horizon=(212, 240, 226), star_alpha=0)),
    (0.16, dict(sky_top=(26, 132, 210), sky_mid=(92, 190, 224), sky_bot=(164, 226, 224), horizon=(210, 240, 224), star_alpha=0)),
    (0.27, dict(sky_top=(32, 130, 204), sky_mid=(100, 188, 220), sky_bot=(172, 224, 220), horizon=(216, 238, 222), star_alpha=0)),
    (0.33, dict(sky_top=(42, 130, 196), sky_mid=(110, 188, 206), sky_bot=(232, 216, 170), horizon=(255, 218, 134), star_alpha=0)),
    (0.39, dict(sky_top=(44, 96, 168), sky_mid=(168, 142, 156), sky_bot=(255, 160, 110), horizon=(255, 110, 86), star_alpha=10)),
    (0.47, dict(sky_top=(26, 52, 120), sky_mid=(224, 144, 158), sky_bot=(40, 64, 120), horizon=(226, 148, 116), star_alpha=60)),
    (0.55, dict(sky_top=(14, 36, 92), sky_mid=(26, 70, 116), sky_bot=(36, 88, 124), horizon=(78, 124, 144), star_alpha=140)),
    (0.66, dict(sky_top=(13, 18, 56), sky_mid=(14, 32, 76), sky_bot=(18, 50, 92), horizon=(30, 76, 110), star_alpha=235)),
    (0.80, dict(sky_top=(13, 18, 54), sky_mid=(14, 32, 74), sky_bot=(18, 50, 90), horizon=(30, 74, 108), star_alpha=235)),
    (0.88, dict(sky_top=(20, 50, 116), sky_mid=(120, 104, 146), sky_bot=(50, 100, 134), horizon=(232, 150, 116), star_alpha=70)),
    (0.96, dict(sky_top=(28, 124, 200), sky_mid=(78, 188, 216), sky_bot=(150, 226, 210), horizon=(248, 222, 170), star_alpha=10)),
]

TROPICAL_AQUA = BiomeSpec(
    name='Tropical Aqua',
    note='Saturated cyan zenith over a turquoise-aqua horizon by day, a coral-reef sunset hugging the sea and a teal-navy blue-hour sinking to deep teal night.',
    keyframes=_AQUA_KF,
    sky=SkyParams(positions=(0.0, 0.40, 0.72, 0.90, 1.0), dither_amp=2.4, zenith_dark=0.10),
)


# ── 4. Hazy Smoke — milky warm day, smoke-red ember sunset, brown-violet night ─
# Wildfire-haze air: the day is a low-contrast milky warm blue-grey, the sun a
# muted red disc, the sunset a smouldering ember-orange that the haze spreads a
# touch wider and lower; the night a warm brown-violet, never neutral.
_SMOKE_KF = [
    (0.05, dict(sky_top=(96, 134, 178), sky_mid=(162, 178, 188), sky_bot=(216, 206, 184), horizon=(238, 218, 178), star_alpha=0)),
    (0.16, dict(sky_top=(90, 130, 182), sky_mid=(158, 176, 188), sky_bot=(216, 204, 180), horizon=(240, 216, 172), star_alpha=0)),
    (0.27, dict(sky_top=(98, 132, 176), sky_mid=(166, 178, 186), sky_bot=(220, 204, 176), horizon=(242, 214, 166), star_alpha=0)),
    (0.33, dict(sky_top=(84, 108, 158), sky_mid=(170, 158, 158), sky_bot=(234, 190, 144), horizon=(252, 180, 112), star_alpha=0)),
    (0.39, dict(sky_top=(60, 68, 128), sky_mid=(168, 120, 130), sky_bot=(238, 142, 96), horizon=(232, 104, 70), star_alpha=10)),
    (0.47, dict(sky_top=(40, 42, 100), sky_mid=(192, 124, 138), sky_bot=(50, 50, 92), horizon=(206, 128, 104), star_alpha=60)),
    (0.55, dict(sky_top=(26, 26, 72), sky_mid=(50, 44, 92), sky_bot=(58, 50, 96), horizon=(112, 80, 100), star_alpha=140)),
    (0.66, dict(sky_top=(16, 14, 40), sky_mid=(30, 22, 50), sky_bot=(44, 32, 58), horizon=(68, 46, 64), star_alpha=230)),
    (0.80, dict(sky_top=(16, 14, 40), sky_mid=(30, 22, 50), sky_bot=(44, 32, 58), horizon=(68, 44, 62), star_alpha=230)),
    (0.88, dict(sky_top=(36, 32, 78), sky_mid=(128, 88, 104), sky_bot=(96, 70, 90), horizon=(214, 122, 84), star_alpha=70)),
    (0.96, dict(sky_top=(94, 128, 172), sky_mid=(168, 174, 182), sky_bot=(224, 200, 172), horizon=(250, 196, 138), star_alpha=10)),
]

HAZY_SMOKE = BiomeSpec(
    name='Hazy Smoke',
    note='Low-contrast milky warm day under wildfire haze, a muted red sun and a smouldering ember sunset the smoke spreads low, sinking to a warm brown-violet night.',
    keyframes=_SMOKE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=3.0, zenith_dark=0.08),
)


# ── 5. Storm Front — bruised steel day, violet squall, magenta-edged sunset ────
# A dramatic weather sky: a steel blue-grey day shot through with a bruised
# violet, the sunset firing magenta-pink under a slate deck; high chroma at low
# value so it stays dramatic, never washed grey. Night a deep bruise-indigo.
_STORM_KF = [
    (0.05, dict(sky_top=(46, 42, 96), sky_mid=(86, 92, 138), sky_bot=(140, 150, 174), horizon=(176, 182, 192), star_alpha=0)),
    (0.16, dict(sky_top=(42, 38, 100), sky_mid=(82, 90, 140), sky_bot=(138, 150, 176), horizon=(178, 184, 192), star_alpha=0)),
    (0.27, dict(sky_top=(48, 42, 94), sky_mid=(90, 94, 138), sky_bot=(144, 152, 172), horizon=(182, 184, 190), star_alpha=0)),
    (0.33, dict(sky_top=(44, 40, 100), sky_mid=(110, 116, 128), sky_bot=(196, 200, 138), horizon=(220, 218, 120), star_alpha=0)),
    (0.39, dict(sky_top=(46, 36, 110), sky_mid=(146, 96, 138), sky_bot=(228, 130, 116), horizon=(240, 150, 86), star_alpha=10)),
    (0.47, dict(sky_top=(34, 30, 96), sky_mid=(170, 98, 152), sky_bot=(60, 52, 110), horizon=(214, 118, 122), star_alpha=60)),
    (0.55, dict(sky_top=(24, 24, 76), sky_mid=(58, 44, 102), sky_bot=(70, 56, 108), horizon=(122, 90, 124), star_alpha=140)),
    (0.66, dict(sky_top=(14, 14, 48), sky_mid=(26, 22, 66), sky_bot=(36, 30, 78), horizon=(58, 46, 96), star_alpha=230)),
    (0.80, dict(sky_top=(14, 14, 46), sky_mid=(26, 22, 64), sky_bot=(36, 30, 76), horizon=(58, 44, 94), star_alpha=230)),
    (0.88, dict(sky_top=(30, 28, 92), sky_mid=(128, 84, 138), sky_bot=(80, 66, 116), horizon=(224, 128, 112), star_alpha=70)),
    (0.96, dict(sky_top=(46, 68, 134), sky_mid=(104, 126, 166), sky_bot=(186, 192, 202), horizon=(248, 200, 152), star_alpha=10)),
]

STORM_FRONT = BiomeSpec(
    name='Storm Front',
    note='A pre-storm sky: a bruised slate-violet deck pressing down from the top, a sickly pale yellow-green light-leak at golden hour, then a magenta-pink sunset below the squall; high chroma at low value, never washed, to a bruise-indigo night.',
    keyframes=_STORM_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.84, 1.0), dither_amp=2.6, zenith_dark=0.12),
)


# ── 6. Pastel Rose — soft periwinkle day, blush-peach sunset, lilac dawn world ─
# A gentle premium pastel sky: a soft periwinkle day with a faintly warm horizon,
# a blush-peach sunset that never goes harsh, the Belt of Venus reading clearly
# as a rose band over a dusty-blue shadow; a deep but lilac-tinted night.
_ROSE_KF = [
    (0.05, dict(sky_top=(78, 112, 200), sky_mid=(138, 168, 226), sky_bot=(204, 212, 234), horizon=(238, 220, 220), star_alpha=0)),
    (0.16, dict(sky_top=(72, 108, 204), sky_mid=(134, 166, 228), sky_bot=(202, 212, 234), horizon=(240, 220, 218), star_alpha=0)),
    (0.27, dict(sky_top=(80, 112, 198), sky_mid=(142, 170, 224), sky_bot=(208, 214, 232), horizon=(242, 218, 214), star_alpha=0)),
    (0.33, dict(sky_top=(108, 126, 204), sky_mid=(180, 174, 214), sky_bot=(244, 206, 198), horizon=(255, 204, 168), star_alpha=0)),
    (0.39, dict(sky_top=(96, 100, 178), sky_mid=(196, 148, 172), sky_bot=(255, 178, 150), horizon=(255, 142, 130), star_alpha=10)),
    (0.47, dict(sky_top=(62, 64, 138), sky_mid=(206, 138, 170), sky_bot=(96, 96, 146), horizon=(238, 168, 156), star_alpha=60)),
    (0.55, dict(sky_top=(34, 34, 92), sky_mid=(78, 64, 124), sky_bot=(88, 78, 128), horizon=(146, 116, 144), star_alpha=140)),
    (0.66, dict(sky_top=(16, 14, 60), sky_mid=(30, 26, 80), sky_bot=(42, 34, 92), horizon=(72, 56, 106), star_alpha=225)),
    (0.80, dict(sky_top=(16, 14, 58), sky_mid=(30, 26, 78), sky_bot=(42, 34, 90), horizon=(72, 54, 104), star_alpha=225)),
    (0.88, dict(sky_top=(40, 40, 104), sky_mid=(168, 116, 154), sky_bot=(98, 96, 146), horizon=(244, 168, 154), star_alpha=70)),
    (0.96, dict(sky_top=(90, 126, 208), sky_mid=(164, 182, 226), sky_bot=(232, 214, 222), horizon=(255, 210, 184), star_alpha=10)),
]

PASTEL_ROSE = BiomeSpec(
    name='Pastel Rose',
    note='Soft periwinkle day with a faintly warm horizon, a gentle blush-peach sunset and a clear rose Belt of Venus over dusty-blue shadow, to a deep lilac-tinted night.',
    keyframes=_ROSE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.56, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.08),
)


# ── 7. Jewel Sunset — sapphire day, high-contrast gold->scarlet->magenta dusk ──
# The premium showpiece: a rich sapphire day, then the most saturated evening of
# the set — a thin scarlet-gold blaze at the sun climbing to magenta-pink, the
# Belt of Venus a vivid salmon over a deep indigo shadow. Night royal indigo.
_JEWEL_KF = [
    (0.05, dict(sky_top=(26, 70, 184), sky_mid=(58, 128, 224), sky_bot=(140, 196, 240), horizon=(204, 230, 244), star_alpha=0)),
    (0.16, dict(sky_top=(22, 66, 188), sky_mid=(52, 126, 226), sky_bot=(134, 196, 242), horizon=(206, 230, 246), star_alpha=0)),
    (0.27, dict(sky_top=(28, 70, 182), sky_mid=(62, 130, 222), sky_bot=(146, 198, 238), horizon=(210, 230, 242), star_alpha=0)),
    (0.33, dict(sky_top=(34, 70, 172), sky_mid=(108, 128, 204), sky_bot=(238, 200, 156), horizon=(255, 212, 110), star_alpha=0)),
    (0.39, dict(sky_top=(46, 52, 138), sky_mid=(176, 100, 150), sky_bot=(255, 144, 92), horizon=(255, 86, 56), star_alpha=10)),
    (0.47, dict(sky_top=(28, 36, 112), sky_mid=(208, 104, 156), sky_bot=(48, 54, 116), horizon=(236, 126, 108), star_alpha=60)),
    (0.55, dict(sky_top=(18, 22, 82), sky_mid=(56, 40, 114), sky_bot=(60, 52, 118), horizon=(120, 80, 134), star_alpha=140)),
    (0.66, dict(sky_top=(13, 14, 50), sky_mid=(22, 20, 70), sky_bot=(30, 30, 84), horizon=(52, 44, 104), star_alpha=235)),
    (0.80, dict(sky_top=(13, 14, 48), sky_mid=(22, 20, 68), sky_bot=(30, 30, 82), horizon=(52, 42, 102), star_alpha=235)),
    (0.88, dict(sky_top=(26, 30, 100), sky_mid=(168, 92, 146), sky_bot=(60, 62, 126), horizon=(244, 120, 96), star_alpha=70)),
    (0.96, dict(sky_top=(26, 66, 180), sky_mid=(74, 132, 222), sky_bot=(170, 208, 238), horizon=(255, 206, 150), star_alpha=10)),
]

JEWEL_SUNSET = BiomeSpec(
    name='Jewel Sunset',
    note='Rich sapphire day and the most saturated evening of the set: a thin scarlet-gold blaze climbing to magenta-pink, a vivid salmon Belt of Venus over deep indigo shadow, royal-indigo night.',
    keyframes=_JEWEL_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.86, 1.0), dither_amp=2.0, zenith_dark=0.14),
)


# ── 8. Slate Monochrome — cool near-monochrome day, restrained amber-grey dusk ──
# The quiet, sophisticated end: a cool desaturated blue-grey day, a single low
# whisper of warm amber at sunset against an otherwise grey-blue dome, a faint
# dusty-rose belt. Reads premium-minimal; night a deep cool slate-navy.
_SLATE_KF = [
    (0.05, dict(sky_top=(74, 102, 146), sky_mid=(128, 156, 184), sky_bot=(188, 204, 216), horizon=(216, 226, 230), star_alpha=0)),
    (0.16, dict(sky_top=(70, 98, 148), sky_mid=(124, 154, 186), sky_bot=(186, 204, 216), horizon=(218, 226, 230), star_alpha=0)),
    (0.27, dict(sky_top=(76, 102, 144), sky_mid=(132, 158, 184), sky_bot=(192, 206, 214), horizon=(220, 226, 228), star_alpha=0)),
    (0.33, dict(sky_top=(62, 82, 132), sky_mid=(124, 144, 174), sky_bot=(196, 196, 192), horizon=(228, 206, 172), star_alpha=0)),
    (0.39, dict(sky_top=(44, 58, 110), sky_mid=(96, 110, 144), sky_bot=(150, 150, 156), horizon=(224, 158, 116), star_alpha=10)),
    (0.47, dict(sky_top=(30, 42, 92), sky_mid=(96, 124, 146), sky_bot=(40, 56, 98), horizon=(120, 120, 130), star_alpha=60)),
    (0.55, dict(sky_top=(24, 32, 74), sky_mid=(46, 56, 96), sky_bot=(56, 66, 102), horizon=(98, 102, 124), star_alpha=140)),
    (0.66, dict(sky_top=(20, 26, 60), sky_mid=(32, 40, 78), sky_bot=(40, 52, 92), horizon=(58, 68, 104), star_alpha=225)),
    (0.80, dict(sky_top=(20, 26, 58), sky_mid=(32, 40, 76), sky_bot=(40, 52, 90), horizon=(58, 66, 102), star_alpha=225)),
    (0.88, dict(sky_top=(28, 36, 90), sky_mid=(108, 102, 124), sky_bot=(60, 70, 106), horizon=(204, 152, 128), star_alpha=70)),
    (0.96, dict(sky_top=(72, 100, 144), sky_mid=(136, 160, 184), sky_bot=(198, 208, 214), horizon=(238, 208, 168), star_alpha=10)),
]

SLATE_MONOCHROME = BiomeSpec(
    name='Slate Monochrome',
    note='Cool-steel near-monochrome day on a clear day->night value ramp, a single thin warm ember held to the horizon at sunset and a faint cool-cyan belt over slate shadow; premium-minimal, sinking to a deep cool slate-navy night.',
    keyframes=_SLATE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.84, 1.0), dither_amp=2.2, zenith_dark=0.10),
)


# ── 9. Aurora Boreal — cold cyan day, peach belt, green aurora over indigo night ─
# A high-latitude sky: a cold pale-cyan day, an honest low peach sunset, then the
# night lifts a green-teal aurora glow from the horizon up through the dome over
# a star-thick indigo — the airglow floor tipped green, never neutral.
_AURORA_KF = [
    (0.05, dict(sky_top=(38, 116, 198), sky_mid=(96, 188, 224), sky_bot=(160, 226, 226), horizon=(206, 240, 230), star_alpha=0)),
    (0.16, dict(sky_top=(32, 118, 204), sky_mid=(90, 192, 226), sky_bot=(156, 228, 228), horizon=(208, 240, 230), star_alpha=0)),
    (0.27, dict(sky_top=(40, 116, 196), sky_mid=(100, 190, 222), sky_bot=(166, 226, 224), horizon=(212, 238, 226), star_alpha=0)),
    (0.33, dict(sky_top=(50, 110, 184), sky_mid=(124, 174, 204), sky_bot=(224, 214, 184), horizon=(255, 216, 148), star_alpha=0)),
    (0.39, dict(sky_top=(48, 84, 152), sky_mid=(158, 134, 156), sky_bot=(250, 166, 122), horizon=(248, 120, 82), star_alpha=10)),
    (0.47, dict(sky_top=(26, 54, 122), sky_mid=(160, 118, 144), sky_bot=(48, 92, 122), horizon=(224, 144, 112), star_alpha=60)),
    (0.55, dict(sky_top=(14, 34, 88), sky_mid=(22, 56, 102), sky_bot=(30, 78, 108), horizon=(58, 120, 124), star_alpha=150)),
    (0.66, dict(sky_top=(13, 18, 54), sky_mid=(15, 38, 74), sky_bot=(26, 108, 98), horizon=(58, 168, 120), star_alpha=240)),
    (0.80, dict(sky_top=(13, 18, 52), sky_mid=(15, 38, 72), sky_bot=(26, 106, 96), horizon=(56, 164, 118), star_alpha=240)),
    (0.88, dict(sky_top=(22, 48, 110), sky_mid=(80, 132, 158), sky_bot=(52, 116, 126), horizon=(232, 150, 110), star_alpha=70)),
    (0.96, dict(sky_top=(36, 112, 194), sky_mid=(104, 186, 222), sky_bot=(172, 226, 222), horizon=(252, 220, 162), star_alpha=10)),
]

AURORA_BOREAL = BiomeSpec(
    name='Aurora Boreal',
    note='Cold pale-cyan polar day and an honest low peach sunset, then a green-teal aurora rising from the horizon through a star-thick indigo night; the airglow floor tips green, never neutral.',
    keyframes=_AURORA_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.12),
)


# ── 10. Deep Ocean Blue-Hour — abyssal ultramarine day, lives in the blue hour ─
# The deepest, coolest design: a profound ultramarine day, a brief restrained
# warm horizon at sunset that the cool dome quickly swallows, a long luxurious
# blue hour and an abyssal star-glittered navy night. Premium and immersive.
_OCEAN_KF = [
    (0.05, dict(sky_top=(18, 64, 162), sky_mid=(48, 120, 210), sky_bot=(120, 184, 234), horizon=(186, 220, 240), star_alpha=0)),
    (0.16, dict(sky_top=(14, 60, 168), sky_mid=(42, 118, 214), sky_bot=(114, 184, 236), horizon=(184, 222, 240), star_alpha=0)),
    (0.27, dict(sky_top=(20, 64, 160), sky_mid=(52, 122, 208), sky_bot=(126, 186, 232), horizon=(192, 222, 236), star_alpha=0)),
    (0.33, dict(sky_top=(26, 62, 150), sky_mid=(80, 116, 188), sky_bot=(200, 196, 200), horizon=(252, 214, 160), star_alpha=0)),
    (0.39, dict(sky_top=(28, 50, 128), sky_mid=(118, 110, 162), sky_bot=(232, 168, 128), horizon=(248, 138, 92), star_alpha=10)),
    (0.47, dict(sky_top=(20, 38, 110), sky_mid=(206, 134, 156), sky_bot=(32, 52, 112), horizon=(212, 140, 116), star_alpha=60)),
    (0.55, dict(sky_top=(12, 28, 84), sky_mid=(24, 52, 116), sky_bot=(34, 70, 126), horizon=(72, 110, 152), star_alpha=150)),
    (0.66, dict(sky_top=(13, 14, 50), sky_mid=(13, 26, 74), sky_bot=(16, 44, 96), horizon=(28, 70, 120), star_alpha=240)),
    (0.80, dict(sky_top=(13, 14, 48), sky_mid=(13, 26, 72), sky_bot=(16, 44, 94), horizon=(28, 68, 118), star_alpha=240)),
    (0.88, dict(sky_top=(18, 42, 110), sky_mid=(104, 100, 150), sky_bot=(46, 82, 138), horizon=(220, 146, 116), star_alpha=70)),
    (0.96, dict(sky_top=(18, 60, 158), sky_mid=(62, 124, 208), sky_bot=(140, 192, 234), horizon=(250, 216, 158), star_alpha=10)),
]

DEEP_OCEAN_BLUE_HOUR = BiomeSpec(
    name='Deep Ocean Blue-Hour',
    note='Profound abyssal ultramarine day that lives in the blue hour: a brief restrained warm horizon the cool dome swallows fast, a long luxurious blue hour and a star-glittered navy night.',
    keyframes=_OCEAN_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.84, 1.0), dither_amp=1.8, zenith_dark=0.16),
)


# Ordered (id, spec) list — the 10 realism rows in sheet order.
CONCEPTS = [
    ('cobalt_alpine', COBALT_ALPINE),
    ('desert_warm_pale', DESERT_WARM_PALE),
    ('tropical_aqua', TROPICAL_AQUA),
    ('hazy_smoke', HAZY_SMOKE),
    ('storm_front', STORM_FRONT),
    ('pastel_rose', PASTEL_ROSE),
    ('jewel_sunset', JEWEL_SUNSET),
    ('slate_monochrome', SLATE_MONOCHROME),
    ('aurora_boreal', AURORA_BOREAL),
    ('deep_ocean_blue_hour', DEEP_OCEAN_BLUE_HOUR),
]
