"""
Round-8 exploration: 10 brand-new, vivid sky concepts for Skybit.

These are FRESH BiomeSpecs authored from scratch — the old shan-shui biome
catalog is deliberately discarded here. The brief: skies that read *alive*
and *painterly* (heightened-but-true, Ghibli/Alto/GRIS territory), never the
grey-and-melancholic register the live Karst sky and half the old catalog
landed in, and never flat two-tone "PowerPoint" gradients or candy neon.

Each concept authors ~8-12 keyframes across the full 0..1 day cycle with rich
chroma and a believable day->night arc, plus a tuned `SkyParams`. The vividness
comes from craft, not saturation slammers:

  * Channel separation — a warm horizon riding against a cool zenith at the
    same instant — so the OKLab bake has a real arc to travel and the midband
    stays saturated instead of slumping to grey.
  * 5 non-uniform `positions` stops that compress most of the grade toward the
    horizon the way real air does (denser low, open up top).
  * `zenith_dark` tuned per concept to deepen the very top without muddying it.
  * Night skies kept ALIVE — saturated indigo/teal/violet with stars, never a
    neutral charcoal.

Palette truth was grounded in golden-hour / blue-hour / alpenglow / aurora /
monsoon photography and stylized-game sky references (see the task notes).

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through `tools/preview_sky_concepts.py`. Pure-Pygame / pygbag-
safe (the keyframes are just color tables; the OKLab bake lives in the engine).
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# Each keyframe table is keyed on the SAME phase anchors so all concepts share a
# common day->night clock; only the colors differ. Anchors, in cycle order:
#   morning 0.06 · midday 0.18 · afternoon 0.30 · golden 0.40 · sunset 0.50 ·
#   dusk 0.62 · night 0.72 · predawn 0.80 · dawn 0.88 · sunrise 0.94
# `make_palette` wraps 0.94 -> 0.06 through 1.0, so the night side is continuous.


# ── 1. Tropical Lagoon — turquoise day, teal blue-hour, warm reef sunset ───────
# Pushed the midday horizon off near-white into a richer reef-turquoise. Beside
# its cool blue neighbours (Cosmos/Emerald) the day horizon glow is tipped a few
# degrees toward aqua-green turquoise (hue ~170°) and the zenith given a faint
# warmth, so it reads unmistakably "lagoon" rather than generic blue sky.
_LAGOON_KF = [
    (0.06, dict(sky_top=(36, 148, 204), sky_mid=(50, 202, 222), sky_bot=(64, 230, 214), horizon=(76, 240, 214), star_alpha=0)),
    (0.18, dict(sky_top=(34, 156, 210), sky_mid=(44, 206, 224), sky_bot=(58, 232, 214), horizon=(72, 240, 212), star_alpha=0)),
    (0.30, dict(sky_top=(42, 160, 206), sky_mid=(64, 210, 222), sky_bot=(82, 234, 212), horizon=(102, 240, 210), star_alpha=0)),
    (0.40, dict(sky_top=(64, 158, 206), sky_mid=(132, 214, 206), sky_bot=(244, 218, 150), horizon=(255, 222, 138), star_alpha=0)),
    (0.50, dict(sky_top=(58, 110, 168), sky_mid=(180, 142, 150), sky_bot=(255, 158, 110), horizon=(255, 188, 120), star_alpha=10)),
    (0.62, dict(sky_top=(22, 58, 110), sky_mid=(40, 116, 142), sky_bot=(120, 156, 150), horizon=(232, 162, 120), star_alpha=70)),
    (0.72, dict(sky_top=(6, 22, 56), sky_mid=(12, 56, 92), sky_bot=(26, 92, 110), horizon=(72, 132, 134), star_alpha=210)),
    (0.80, dict(sky_top=(10, 30, 70), sky_mid=(20, 76, 116), sky_bot=(48, 128, 138), horizon=(150, 178, 156), star_alpha=120)),
    (0.88, dict(sky_top=(20, 96, 162), sky_mid=(70, 168, 196), sky_bot=(190, 214, 178), horizon=(255, 216, 168), star_alpha=20)),
    (0.94, dict(sky_top=(32, 140, 200), sky_mid=(94, 202, 216), sky_bot=(206, 240, 206), horizon=(255, 230, 186), star_alpha=0)),
]

TROPICAL_LAGOON = BiomeSpec(
    name='Tropical Lagoon',
    note='Electric reef turquoise by day melting to teal blue-hour and a warm coral sunset; saltwater-bright.',
    keyframes=_LAGOON_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.08),
)


# ── 2. Aurora Tundra — cold cyan day, green-violet curtains over indigo night ─
# Daytime (cols 4-7) was the palest, most neutral block on the sheet and drifted
# toward melancholic in motion. The day horizon band now carries a faint aurora
# green-teal shimmer (hue ~178°, sat lifted to ~0.32) so the row keeps its polar
# identity through the bright phases — the spectacular dusk/night is untouched.
_AURORA_KF = [
    (0.06, dict(sky_top=(34, 100, 176), sky_mid=(80, 182, 214), sky_bot=(124, 224, 218), horizon=(158, 240, 234), star_alpha=0)),
    (0.18, dict(sky_top=(28, 108, 188), sky_mid=(70, 190, 222), sky_bot=(112, 228, 220), horizon=(160, 240, 238), star_alpha=0)),
    (0.30, dict(sky_top=(36, 104, 182), sky_mid=(86, 186, 216), sky_bot=(130, 226, 216), horizon=(170, 238, 230), star_alpha=0)),
    (0.40, dict(sky_top=(58, 92, 158), sky_mid=(126, 170, 192), sky_bot=(210, 214, 202), horizon=(238, 226, 200), star_alpha=0)),
    (0.50, dict(sky_top=(46, 64, 132), sky_mid=(108, 110, 160), sky_bot=(204, 158, 160), horizon=(248, 188, 154), star_alpha=20)),
    (0.62, dict(sky_top=(18, 36, 92), sky_mid=(34, 92, 122), sky_bot=(72, 158, 142), horizon=(168, 184, 150), star_alpha=110)),
    (0.72, dict(sky_top=(6, 14, 48), sky_mid=(16, 60, 86), sky_bot=(34, 130, 118), horizon=(96, 176, 138), star_alpha=235)),
    (0.80, dict(sky_top=(10, 18, 56), sky_mid=(24, 70, 100), sky_bot=(58, 132, 134), horizon=(126, 168, 150), star_alpha=170)),
    (0.88, dict(sky_top=(22, 48, 108), sky_mid=(56, 116, 158), sky_bot=(128, 184, 196), horizon=(206, 218, 204), star_alpha=40)),
    (0.94, dict(sky_top=(30, 92, 166), sky_mid=(82, 172, 208), sky_bot=(140, 222, 212), horizon=(174, 238, 212), star_alpha=10)),
]

AURORA_TUNDRA = BiomeSpec(
    name='Aurora Tundra',
    note='Frozen cyan daylight giving way to green-violet aurora curtains over a deep indigo, star-thick night.',
    keyframes=_AURORA_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.80, 1.0), dither_amp=1.8, zenith_dark=0.14),
)


# ── 3. Mars Glow Desert — butterscotch dome, dusty-rose haze, blue solar dusk ─
# Lifted day chroma and a clean two-hue arc: a dusty-rose / mauve-violet zenith
# over a vivid burnt-orange→peach horizon, so it stops reading as one flat muddy
# tan. Brighter, more saturated terracotta through the day; the night horizon is
# pulled up to a saturated cobalt-dark instead of a neutral grey-blue.
_MARS_KF = [
    (0.06, dict(sky_top=(132, 60, 150), sky_mid=(214, 96, 108), sky_bot=(252, 138, 64), horizon=(255, 168, 84), star_alpha=0)),
    (0.18, dict(sky_top=(142, 60, 152), sky_mid=(226, 98, 100), sky_bot=(255, 138, 56), horizon=(255, 170, 76), star_alpha=0)),
    (0.30, dict(sky_top=(150, 54, 138), sky_mid=(236, 94, 84), sky_bot=(255, 134, 50), horizon=(255, 164, 66), star_alpha=0)),
    (0.40, dict(sky_top=(132, 44, 124), sky_mid=(230, 80, 74), sky_bot=(255, 122, 46), horizon=(255, 154, 56), star_alpha=0)),
    (0.50, dict(sky_top=(92, 40, 124), sky_mid=(184, 66, 100), sky_bot=(244, 116, 80), horizon=(132, 124, 196), star_alpha=20)),
    (0.62, dict(sky_top=(50, 30, 92), sky_mid=(116, 48, 84), sky_bot=(196, 84, 74), horizon=(80, 100, 190), star_alpha=90)),
    (0.72, dict(sky_top=(20, 12, 46), sky_mid=(56, 22, 52), sky_bot=(116, 42, 56), horizon=(34, 56, 150), star_alpha=215)),
    (0.80, dict(sky_top=(34, 16, 60), sky_mid=(90, 36, 64), sky_bot=(166, 64, 60), horizon=(58, 82, 178), star_alpha=120)),
    (0.88, dict(sky_top=(118, 50, 134), sky_mid=(212, 88, 92), sky_bot=(252, 134, 56), horizon=(244, 158, 92), star_alpha=20)),
    (0.94, dict(sky_top=(132, 58, 148), sky_mid=(216, 94, 102), sky_bot=(252, 136, 60), horizon=(255, 166, 80), star_alpha=0)),
]

MARS_GLOW_DESERT = BiomeSpec(
    name='Mars Glow Desert',
    note='Vivid terracotta iron-dust dome — dusty-rose / mauve-violet zenith over a burnt-orange→peach horizon — with a rare cobalt solar twilight and a saturated cobalt-indigo night.',
    keyframes=_MARS_KF,
    sky=SkyParams(positions=(0.0, 0.28, 0.56, 0.82, 1.0), dither_amp=2.6, zenith_dark=0.10),
)


# ── 4. Monsoon Storm Front — deep teal-indigo dome, luminous sickly-green squall ──
# Reworked to kill the grey-melancholic read: VALUE stays low but CHROMA runs
# HIGH. The zenith is a saturated indigo-violet bruise; the midband a deep teal-
# slate; and the lower third carries a LUMINOUS sickly-green / chartreuse storm-
# light band — the hot squall glow under a black cloud deck. Moody, never washed.
_MONSOON_KF = [
    (0.06, dict(sky_top=(40, 26, 104), sky_mid=(20, 86, 118), sky_bot=(46, 168, 130), horizon=(170, 232, 86), star_alpha=0)),
    (0.18, dict(sky_top=(38, 24, 112), sky_mid=(16, 92, 124), sky_bot=(40, 176, 134), horizon=(184, 240, 78), star_alpha=0)),
    (0.30, dict(sky_top=(42, 22, 102), sky_mid=(18, 84, 118), sky_bot=(44, 162, 128), horizon=(160, 224, 80), star_alpha=0)),
    (0.40, dict(sky_top=(54, 24, 100), sky_mid=(36, 70, 116), sky_bot=(70, 142, 124), horizon=(198, 216, 84), star_alpha=0)),
    (0.50, dict(sky_top=(70, 22, 104), sky_mid=(122, 44, 116), sky_bot=(196, 96, 100), horizon=(236, 168, 74), star_alpha=10)),
    (0.62, dict(sky_top=(40, 16, 88), sky_mid=(70, 32, 104), sky_bot=(96, 92, 110), horizon=(150, 184, 84), star_alpha=90)),
    (0.72, dict(sky_top=(12, 8, 48), sky_mid=(20, 30, 80), sky_bot=(26, 78, 92), horizon=(60, 156, 96), star_alpha=200)),
    (0.80, dict(sky_top=(18, 12, 60), sky_mid=(30, 42, 96), sky_bot=(38, 108, 108), horizon=(98, 190, 92), star_alpha=120)),
    (0.88, dict(sky_top=(40, 24, 104), sky_mid=(18, 86, 120), sky_bot=(44, 168, 130), horizon=(168, 230, 84), star_alpha=20)),
    (0.94, dict(sky_top=(40, 26, 106), sky_mid=(20, 88, 120), sky_bot=(46, 170, 130), horizon=(174, 234, 82), star_alpha=0)),
]

MONSOON_STORM_FRONT = BiomeSpec(
    name='Monsoon Storm Front',
    note='Low-value, HIGH-chroma: a saturated indigo-violet bruise zenith over deep teal-slate, lit by a luminous sickly-green chartreuse squall band at the horizon, bruising to violet-amber at sunset. Moody, never grey.',
    keyframes=_MONSOON_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.62, 0.84, 1.0), dither_amp=2.4, zenith_dark=0.12),
)


# ── 5. Cherry-Blossom Spring — periwinkle day, sakura-pink horizon, lilac dusk ─
# Anti-candy: deepened the zenith value and threaded a distinct cool PERIWINKLE
# band through the upper-mid. The daytime mid-field now carries a THIRD value
# step — a thin warm lilac→peach break at the sky_bot stop (~0.55 vertical) — so
# the grade has a painterly middle instead of a straight periwinkle→pink lerp;
# midday horizon saturation nudged up so the sakura reads richer at noon.
_SAKURA_KF = [
    (0.06, dict(sky_top=(64, 88, 198), sky_mid=(126, 148, 226), sky_bot=(232, 182, 194), horizon=(252, 132, 174), star_alpha=0)),
    (0.18, dict(sky_top=(54, 82, 202), sky_mid=(118, 142, 228), sky_bot=(230, 178, 192), horizon=(252, 124, 168), star_alpha=0)),
    (0.30, dict(sky_top=(66, 88, 200), sky_mid=(130, 148, 226), sky_bot=(234, 180, 190), horizon=(254, 126, 168), star_alpha=0)),
    (0.40, dict(sky_top=(90, 90, 196), sky_mid=(166, 146, 214), sky_bot=(238, 180, 200), horizon=(255, 168, 182), star_alpha=0)),
    (0.50, dict(sky_top=(112, 92, 176), sky_mid=(202, 142, 186), sky_bot=(252, 178, 184), horizon=(255, 192, 184), star_alpha=10)),
    (0.62, dict(sky_top=(54, 46, 122), sky_mid=(120, 86, 158), sky_bot=(200, 138, 172), horizon=(246, 174, 180), star_alpha=70)),
    (0.72, dict(sky_top=(14, 14, 56), sky_mid=(36, 28, 86), sky_bot=(76, 54, 112), horizon=(146, 100, 134), star_alpha=205)),
    (0.80, dict(sky_top=(26, 22, 80), sky_mid=(58, 44, 116), sky_bot=(118, 86, 148), horizon=(206, 150, 172), star_alpha=110)),
    (0.88, dict(sky_top=(74, 84, 188), sky_mid=(160, 150, 218), sky_bot=(244, 196, 208), horizon=(255, 200, 198), star_alpha=20)),
    (0.94, dict(sky_top=(72, 110, 206), sky_mid=(150, 172, 228), sky_bot=(244, 196, 204), horizon=(255, 196, 202), star_alpha=0)),
]

CHERRY_BLOSSOM_SPRING = BiomeSpec(
    name='Cherry-Blossom Spring',
    note='A deep periwinkle zenith threaded through lilac into a sakura-pink horizon — painterly value depth, never bubblegum — blooming to a lilac dusk.',
    keyframes=_SAKURA_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.56, 0.80, 1.0), dither_amp=1.8, zenith_dark=0.08),
)


# ── 6. Savanna Ember Dusk — gold-hazed day, ember-orange dusk, hot-coal night ─
# Carried a warm straw/amber undertone all the way through midday so the midband
# never slumps to neutral grey-green — the whole row now reads sun-baked, a hazy
# gold dome over a hot amber horizon even at noon.
_SAVANNA_KF = [
    (0.06, dict(sky_top=(58, 126, 198), sky_mid=(194, 184, 128), sky_bot=(248, 198, 96), horizon=(255, 184, 70), star_alpha=0)),
    (0.18, dict(sky_top=(50, 124, 204), sky_mid=(192, 182, 120), sky_bot=(248, 192, 88), horizon=(255, 178, 62), star_alpha=0)),
    (0.30, dict(sky_top=(72, 120, 192), sky_mid=(210, 178, 110), sky_bot=(252, 188, 80), horizon=(255, 172, 56), star_alpha=0)),
    (0.40, dict(sky_top=(132, 124, 158), sky_mid=(236, 174, 116), sky_bot=(255, 196, 110), horizon=(255, 192, 92), star_alpha=0)),
    (0.50, dict(sky_top=(120, 70, 96), sky_mid=(220, 110, 70), sky_bot=(255, 150, 66), horizon=(255, 174, 70), star_alpha=10)),
    (0.62, dict(sky_top=(56, 30, 60), sky_mid=(132, 56, 56), sky_bot=(208, 100, 50), horizon=(248, 140, 60), star_alpha=80)),
    (0.72, dict(sky_top=(18, 12, 32), sky_mid=(48, 22, 32), sky_bot=(98, 44, 38), horizon=(176, 82, 44), star_alpha=200)),
    (0.80, dict(sky_top=(30, 20, 44), sky_mid=(78, 38, 48), sky_bot=(146, 70, 50), horizon=(214, 112, 54), star_alpha=110)),
    (0.88, dict(sky_top=(96, 78, 118), sky_mid=(206, 138, 100), sky_bot=(252, 178, 100), horizon=(255, 188, 92), star_alpha=20)),
    (0.94, dict(sky_top=(90, 134, 188), sky_mid=(214, 178, 134), sky_bot=(252, 204, 132), horizon=(255, 204, 120), star_alpha=0)),
]

SAVANNA_EMBER_DUSK = BiomeSpec(
    name='Savanna Ember Dusk',
    note='Dust-gold afternoon blazing into an ember-orange dusk and a smouldering hot-coal night horizon.',
    keyframes=_SAVANNA_KF,
    sky=SkyParams(positions=(0.0, 0.28, 0.56, 0.82, 1.0), dither_amp=2.4, zenith_dark=0.08),
)


# ── 7. Oceanic Blue-Hour — deep cobalt day, ultramarine dusk, abyssal night ───
_OCEANIC_KF = [
    (0.06, dict(sky_top=(20, 70, 158), sky_mid=(64, 128, 204), sky_bot=(146, 192, 232), horizon=(202, 224, 240), star_alpha=0)),
    (0.18, dict(sky_top=(16, 76, 172), sky_mid=(56, 134, 212), sky_bot=(140, 196, 234), horizon=(196, 224, 240), star_alpha=0)),
    (0.30, dict(sky_top=(22, 72, 162), sky_mid=(70, 130, 204), sky_bot=(154, 196, 232), horizon=(214, 224, 232), star_alpha=0)),
    (0.40, dict(sky_top=(34, 64, 146), sky_mid=(98, 124, 182), sky_bot=(202, 196, 200), horizon=(252, 214, 168), star_alpha=0)),
    (0.50, dict(sky_top=(32, 44, 122), sky_mid=(86, 88, 156), sky_bot=(188, 152, 160), horizon=(252, 178, 134), star_alpha=20)),
    (0.62, dict(sky_top=(14, 24, 82), sky_mid=(28, 56, 122), sky_bot=(66, 108, 160), horizon=(150, 168, 184), star_alpha=120)),
    (0.72, dict(sky_top=(4, 10, 42), sky_mid=(10, 28, 78), sky_bot=(22, 58, 110), horizon=(56, 104, 146), star_alpha=235)),
    (0.80, dict(sky_top=(8, 16, 58), sky_mid=(18, 44, 100), sky_bot=(40, 88, 142), horizon=(96, 138, 168), star_alpha=160)),
    (0.88, dict(sky_top=(16, 52, 128), sky_mid=(48, 104, 176), sky_bot=(120, 172, 212), horizon=(200, 210, 220), star_alpha=30)),
    (0.94, dict(sky_top=(20, 68, 154), sky_mid=(62, 126, 202), sky_bot=(148, 196, 230), horizon=(214, 226, 234), star_alpha=0)),
]

OCEANIC_BLUE_HOUR = BiomeSpec(
    name='Oceanic Blue-Hour',
    note='Saturated cobalt-to-ultramarine sky that lives in the blue hour; deep, cool, oceanic, glittering at night.',
    keyframes=_OCEANIC_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.16),
)


# ── 8. Emerald Rainforest — jade-warm day, chartreuse haze, deep viridian night ─
# Cured the swamp midband: the deep jade zenith is pushed bluer/deeper and the
# horizon is steered off the muddy-yellow hue toward a LUMINOUS lime→aqua, so the
# midday read stays jungle-lush and electric instead of dishwater.
_RAINFOREST_KF = [
    (0.06, dict(sky_top=(20, 124, 152), sky_mid=(56, 198, 178), sky_bot=(120, 236, 168), horizon=(176, 248, 140), star_alpha=0)),
    (0.18, dict(sky_top=(16, 128, 160), sky_mid=(48, 202, 184), sky_bot=(110, 240, 168), horizon=(168, 250, 132), star_alpha=0)),
    (0.30, dict(sky_top=(18, 122, 150), sky_mid=(52, 198, 176), sky_bot=(118, 234, 158), horizon=(178, 244, 124), star_alpha=0)),
    (0.40, dict(sky_top=(28, 110, 134), sky_mid=(80, 184, 156), sky_bot=(156, 222, 140), horizon=(212, 236, 124), star_alpha=0)),
    (0.50, dict(sky_top=(52, 92, 120), sky_mid=(128, 158, 132), sky_bot=(208, 196, 134), horizon=(244, 210, 132), star_alpha=10)),
    (0.62, dict(sky_top=(22, 58, 74), sky_mid=(44, 116, 104), sky_bot=(96, 168, 120), horizon=(180, 200, 124), star_alpha=80)),
    (0.72, dict(sky_top=(4, 24, 38), sky_mid=(10, 58, 60), sky_bot=(20, 102, 86), horizon=(58, 150, 102), star_alpha=205)),
    (0.80, dict(sky_top=(8, 32, 50), sky_mid=(18, 80, 84), sky_bot=(40, 132, 108), horizon=(100, 176, 122), star_alpha=120)),
    (0.88, dict(sky_top=(34, 114, 140), sky_mid=(92, 188, 172), sky_bot=(168, 230, 178), horizon=(214, 244, 162), star_alpha=20)),
    (0.94, dict(sky_top=(48, 138, 160), sky_mid=(112, 204, 188), sky_bot=(184, 238, 178), horizon=(220, 248, 156), star_alpha=0)),
]

EMERALD_RAINFOREST = BiomeSpec(
    name='Emerald Rainforest',
    note='Humid deep-jade canopy light over a luminous lime→aqua horizon by day, sinking to a deep viridian, firefly-starred night.',
    keyframes=_RAINFOREST_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 9. High-Altitude Cosmos — deep indigo thin air, cyan-edged horizon, galactic night ─
# Split decisively COOL from Rose-Gold: indigo/blue-violet zenith over a
# cyan-edged horizon, never pink. This owns the "thin air / deep space" end —
# the darkest, bluest day of the band, with the strongest starfield.
_COSMOS_KF = [
    (0.06, dict(sky_top=(30, 34, 132), sky_mid=(46, 96, 196), sky_bot=(78, 178, 224), horizon=(120, 224, 230), star_alpha=44)),
    (0.18, dict(sky_top=(26, 32, 140), sky_mid=(40, 100, 204), sky_bot=(70, 184, 228), horizon=(108, 228, 232), star_alpha=34)),
    (0.30, dict(sky_top=(34, 34, 132), sky_mid=(50, 98, 196), sky_bot=(82, 178, 222), horizon=(126, 222, 226), star_alpha=30)),
    (0.40, dict(sky_top=(52, 36, 130), sky_mid=(88, 92, 184), sky_bot=(140, 168, 214), horizon=(196, 214, 220), star_alpha=24)),
    (0.50, dict(sky_top=(60, 30, 116), sky_mid=(120, 56, 152), sky_bot=(206, 116, 168), horizon=(248, 168, 150), star_alpha=36)),
    (0.62, dict(sky_top=(30, 18, 86), sky_mid=(62, 34, 116), sky_bot=(118, 70, 148), horizon=(150, 128, 188), star_alpha=140)),
    (0.72, dict(sky_top=(6, 6, 40), sky_mid=(18, 18, 78), sky_bot=(36, 44, 116), horizon=(58, 96, 158), star_alpha=255)),
    (0.80, dict(sky_top=(10, 10, 52), sky_mid=(28, 30, 100), sky_bot=(52, 70, 144), horizon=(86, 134, 182), star_alpha=190)),
    (0.88, dict(sky_top=(26, 26, 116), sky_mid=(56, 80, 176), sky_bot=(96, 158, 210), horizon=(160, 210, 224), star_alpha=64)),
    (0.94, dict(sky_top=(30, 32, 130), sky_mid=(44, 94, 196), sky_bot=(78, 176, 222), horizon=(124, 218, 228), star_alpha=44)),
]

HIGH_ALTITUDE_COSMOS = BiomeSpec(
    name='High-Altitude Cosmos',
    note='Thin near-space air: deep indigo/blue-violet zenith over a cyan-edged horizon, a magenta solar dusk, and the band\'s densest galactic-indigo night.',
    keyframes=_COSMOS_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.80, 1.0), dither_amp=1.6, zenith_dark=0.20),
)


# ── 10. Rose-Gold Salt Flat — soft lavender day, champagne-amber horizon, rose night ─
# Split decisively WARM from Cosmos: a soft lavender zenith pouring down into a
# genuinely champagne-AMBER horizon — rose-gold metal, not pink wash. The day
# zenith is deepened ~10% for more presence and the midday horizon glow warmed
# (hue ~28°, sat up) so the row carries real daytime energy instead of sitting
# lowest on the sheet — still a saturated mauve-rose night that won't drift grey.
_SALTFLAT_KF = [
    (0.06, dict(sky_top=(118, 106, 174), sky_mid=(218, 176, 164), sky_bot=(252, 202, 138), horizon=(255, 178, 106), star_alpha=0)),
    (0.18, dict(sky_top=(112, 102, 176), sky_mid=(216, 172, 158), sky_bot=(252, 196, 128), horizon=(255, 176, 100), star_alpha=0)),
    (0.30, dict(sky_top=(122, 106, 168), sky_mid=(226, 174, 154), sky_bot=(255, 194, 124), horizon=(255, 172, 96), star_alpha=0)),
    (0.40, dict(sky_top=(158, 128, 178), sky_mid=(244, 178, 152), sky_bot=(255, 200, 132), horizon=(255, 186, 108), star_alpha=0)),
    (0.50, dict(sky_top=(150, 100, 156), sky_mid=(244, 154, 138), sky_bot=(255, 184, 124), horizon=(255, 192, 124), star_alpha=10)),
    (0.62, dict(sky_top=(84, 52, 116), sky_mid=(176, 96, 124), sky_bot=(238, 150, 122), horizon=(255, 182, 132), star_alpha=70)),
    (0.72, dict(sky_top=(28, 16, 60), sky_mid=(70, 36, 80), sky_bot=(132, 66, 92), horizon=(204, 120, 110), star_alpha=205)),
    (0.80, dict(sky_top=(42, 26, 76), sky_mid=(102, 56, 102), sky_bot=(174, 100, 116), horizon=(244, 158, 132), star_alpha=115)),
    (0.88, dict(sky_top=(132, 110, 184), sky_mid=(224, 174, 178), sky_bot=(255, 200, 158), horizon=(255, 192, 130), star_alpha=20)),
    (0.94, dict(sky_top=(132, 118, 184), sky_mid=(222, 178, 166), sky_bot=(254, 204, 142), horizon=(255, 184, 108), star_alpha=0)),
]

ROSE_GOLD_SALT_FLAT = BiomeSpec(
    name='Rose-Gold Salt Flat',
    note='Soft lavender zenith pouring into a champagne-amber horizon — genuine rose-gold metal, not pink — warming to a peach sunset and a saturated mauve-rose night.',
    keyframes=_SALTFLAT_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=1.6, zenith_dark=0.07),
)


# Ordered (id, spec) list — the 10 concept rows in sheet order.
CONCEPTS = [
    ('tropical_lagoon', TROPICAL_LAGOON),
    ('aurora_tundra', AURORA_TUNDRA),
    ('mars_glow_desert', MARS_GLOW_DESERT),
    ('monsoon_storm_front', MONSOON_STORM_FRONT),
    ('cherry_blossom_spring', CHERRY_BLOSSOM_SPRING),
    ('savanna_ember_dusk', SAVANNA_EMBER_DUSK),
    ('oceanic_blue_hour', OCEANIC_BLUE_HOUR),
    ('emerald_rainforest', EMERALD_RAINFOREST),
    ('high_altitude_cosmos', HIGH_ALTITUDE_COSMOS),
    ('rose_gold_salt_flat', ROSE_GOLD_SALT_FLAT),
]
