"""
Round-12 exploration: 10 RESTRAINED, UX-flattering sky concepts for Skybit.

The journey: the live sky read grey/melancholic -> round-11 answered with 10
*vivid* concepts -> the user found those too vivid. This is the third target:
a cool, restrained, harmonious backdrop that RECEDES, so the game's warm, busy
foreground (scarlet bird, gold coins, tan pillars, warm power-up bursts) pops
and long runs stay easy on the eye. NOT a swing back to grey.

The register is the Alto's Odyssey / Monument Valley / GRIS / Sky: Children of
the Light family — recessive pastel/jewel gradients that keep foreground
silhouettes readable. Every concept is authored to ALL of these rules:

  * Cool-biased, MODERATE chroma. Hue families bias blue/teal/slate/lavender/
    dawn rose-grey/pale amber — clean pastels or hazy jewel tones, never neon.
  * Muted != grey. Each row's hue identity stays DECISIVE even at low chroma;
    no phase is allowed to collapse to neutral charcoal/beige.
  * Value-managed for the HUD: the top ~10% band is kept a touch deeper /
    stronger-hued (zenith_dark + a deepened sky_top stop) so white+gold HUD
    text reads; the upper sky is never near-white.
  * Calm bird zone (upper-mid): low-contrast, no warm saturated red/orange and
    no saturated green up there (the bird owns scarlet, foliage owns green).
    Warm accents are allowed ONLY low / at the horizon, kept subtle.
  * Alive nights: deep indigo/teal/violet + stars — saturated-dark, never grey.
  * Distinctiveness via hue family + time-of-day; each a tight analogous palette
    with at most one quiet complementary horizon accent. No two rows alike.

Palette truth was grounded in blue-hour / high-altitude-haze / overcast /
pre-dawn photography and the recessive game-sky references (see task notes):
blue-hour descent #87c7de->#1d51a6->#0d0548, cloud-blue haze #A2B6B9.

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through `tools/preview_sky_concepts_calm.py`. Pure-Pygame /
pygbag-safe (the keyframes are just color tables; the OKLab bake lives in the
engine). Authored as a NEW module so the round-11 vivid set stays intact.
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# All concepts share the SAME phase clock as round 11 so the columns line up:
#   morning 0.06 · midday 0.18 · afternoon 0.30 · golden 0.40 · sunset 0.50 ·
#   dusk 0.62 · night 0.72 · predawn 0.80 · dawn 0.88 · sunrise 0.94
# `make_palette` wraps 0.94 -> 0.06 through 1.0, so the night side is continuous.
#
# Authoring discipline for the calm target, applied to every row:
#   - Day phases (0.06-0.40): keep the upper-mid (sky_top/sky_mid) cool and
#     close in value; let the horizon carry the one warm/hue accent, kept low.
#   - Sunset (0.50): a SINGLE quiet warm step at the horizon only — no full-sky
#     fire. The zenith stays cool.
#   - Dusk/predawn (0.62/0.80): blue-hour — cool, deepening, the most "Alto".
#   - Night (0.72): saturated-dark jewel tone + stars.


# ── 1. Dawn Rose-Grey — hazy rose-mauve morning, slate noon, blue-hour night ──
# A muted rose-grey that stays decisively warm-neutral-cool without tipping to
# beige: a smoky slate-blue zenith over a soft dusty-rose horizon by day, the
# warmth held LOW so the bird zone is cool. Pre-dawn is its signature — a true
# muted rose-grey blue-hour.
# Sunrise/sunset signature: a dusty rose-MAUVE bloom (violet-biased pink, NOT
# amber) that climbs from the horizon into sky_bot and washes the mid mauve, the
# slate zenith holding cool above it so no warmth reaches the top band. A faint
# mauve creeps into the cold-grey predawn shoulder so the moment has a runway.
# Held wide via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_ROSEGREY_KF = [
    (0.06, dict(sky_top=(96, 110, 140), sky_mid=(150, 156, 174), sky_bot=(206, 190, 192), horizon=(224, 196, 188), star_alpha=0)),
    (0.18, dict(sky_top=(104, 122, 152), sky_mid=(158, 168, 186), sky_bot=(208, 200, 200), horizon=(222, 204, 196), star_alpha=0)),
    (0.30, dict(sky_top=(100, 116, 148), sky_mid=(152, 162, 182), sky_bot=(204, 194, 196), horizon=(220, 196, 190), star_alpha=0)),
    (0.40, dict(sky_top=(110, 106, 146), sky_mid=(180, 138, 168), sky_bot=(222, 150, 172), horizon=(236, 138, 158), star_alpha=0)),
    (0.44, dict(sky_top=(104, 96, 142), sky_mid=(184, 126, 162), sky_bot=(228, 136, 166), horizon=(236, 122, 150), star_alpha=0)),
    (0.50, dict(sky_top=(96, 86, 138), sky_mid=(180, 112, 154), sky_bot=(226, 120, 158), horizon=(230, 106, 138), star_alpha=10)),
    (0.56, dict(sky_top=(82, 74, 128), sky_mid=(162, 100, 146), sky_bot=(212, 114, 150), horizon=(220, 104, 134), star_alpha=24)),
    (0.62, dict(sky_top=(58, 56, 106), sky_mid=(114, 92, 144), sky_bot=(172, 112, 148), horizon=(204, 114, 138), star_alpha=70)),
    (0.72, dict(sky_top=(26, 28, 56), sky_mid=(48, 48, 84), sky_bot=(78, 72, 110), horizon=(120, 100, 130), star_alpha=190)),
    (0.80, dict(sky_top=(40, 38, 80), sky_mid=(90, 68, 120), sky_bot=(146, 96, 142), horizon=(196, 110, 142), star_alpha=110)),
    (0.84, dict(sky_top=(58, 52, 102), sky_mid=(130, 92, 146), sky_bot=(198, 120, 152), horizon=(228, 116, 142), star_alpha=56)),
    (0.88, dict(sky_top=(80, 76, 126), sky_mid=(166, 118, 160), sky_bot=(224, 138, 162), horizon=(236, 124, 148), star_alpha=24)),
    (0.90, dict(sky_top=(90, 92, 138), sky_mid=(170, 136, 170), sky_bot=(224, 156, 174), horizon=(232, 144, 158), star_alpha=12)),
    (0.94, dict(sky_top=(96, 110, 142), sky_mid=(158, 158, 180), sky_bot=(210, 188, 194), horizon=(228, 188, 184), star_alpha=0)),
]

DAWN_ROSE_GREY = BiomeSpec(
    name='Dawn Rose-Grey',
    note='Smoky slate-blue zenith over a soft dusty rose-mauve horizon — muted, violet-biased rose-grey that never tips to amber or beige — sinking to a true blue-hour night.',
    keyframes=_ROSEGREY_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 2. Powder Morning — clean powder-blue clear day, gentle cool dusk, navy ───
# The classic "clear blue morning" but pastel and recessive: a deepened
# cornflower zenith opening to a powder-blue mid and a barely-warm pale horizon.
# The most universally-readable backdrop — calm, cool, foreground-first.
# Sunrise/sunset signature: a soft peach bloom raised ~40% taller so it fills the
# lower-mid frame (no thin horizon band), rising into the powder-blue mid as
# periwinkle — warm-below / cool-above as a clean pastel dawn. The dawn shoulder
# (predawn/dawn) is pre-warmed so the morning has a runway. Zenith stays cool.
# Widened via 0.44/0.56 and 0.84/0.90.
_POWDER_KF = [
    (0.06, dict(sky_top=(136, 166, 204), sky_mid=(196, 214, 232), sky_bot=(224, 232, 242), horizon=(236, 236, 240), star_alpha=0)),
    (0.18, dict(sky_top=(140, 170, 208), sky_mid=(198, 218, 234), sky_bot=(226, 234, 242), horizon=(238, 238, 240), star_alpha=0)),
    (0.30, dict(sky_top=(140, 168, 204), sky_mid=(200, 216, 230), sky_bot=(226, 232, 240), horizon=(238, 236, 238), star_alpha=0)),
    (0.40, dict(sky_top=(134, 154, 196), sky_mid=(228, 192, 198), sky_bot=(252, 208, 192), horizon=(255, 198, 170), star_alpha=0)),
    (0.44, dict(sky_top=(128, 146, 192), sky_mid=(232, 184, 192), sky_bot=(254, 200, 182), horizon=(255, 188, 156), star_alpha=0)),
    (0.50, dict(sky_top=(118, 134, 186), sky_mid=(228, 172, 186), sky_bot=(254, 192, 174), horizon=(255, 178, 144), star_alpha=10)),
    (0.56, dict(sky_top=(96, 112, 172), sky_mid=(204, 150, 170), sky_bot=(250, 176, 158), horizon=(255, 170, 134), star_alpha=26)),
    (0.62, dict(sky_top=(50, 74, 134), sky_mid=(138, 122, 154), sky_bot=(220, 168, 158), horizon=(248, 172, 138), star_alpha=80)),
    (0.72, dict(sky_top=(14, 24, 62), sky_mid=(24, 50, 102), sky_bot=(40, 82, 132), horizon=(72, 120, 158), star_alpha=210)),
    (0.80, dict(sky_top=(22, 36, 84), sky_mid=(70, 78, 124), sky_bot=(154, 130, 158), horizon=(216, 168, 164), star_alpha=130)),
    (0.84, dict(sky_top=(40, 56, 110), sky_mid=(142, 120, 162), sky_bot=(230, 174, 180), horizon=(255, 184, 154), star_alpha=58)),
    (0.88, dict(sky_top=(88, 116, 176), sky_mid=(204, 180, 202), sky_bot=(250, 200, 188), horizon=(255, 190, 160), star_alpha=24)),
    (0.90, dict(sky_top=(106, 138, 192), sky_mid=(206, 192, 214), sky_bot=(246, 210, 202), horizon=(252, 204, 180), star_alpha=12)),
    (0.94, dict(sky_top=(122, 160, 204), sky_mid=(174, 202, 228), sky_bot=(222, 222, 224), horizon=(248, 214, 202), star_alpha=0)),
]

POWDER_MORNING = BiomeSpec(
    name='Powder Morning',
    note='The lightest, airiest porcelain-periwinkle clear day — high-value low-chroma blue clearly above Slate, a hair warm — easing to a gentle cool dusk and a deep navy night.',
    keyframes=_POWDER_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.24),
)


# ── 3. Pale Amber Haze — warm-neutral hazy afternoon, cool zenith, indigo night ─
# The one row that owns a warm daytime read, kept UX-safe: the warmth lives only
# in the LOWER half (pale amber/sand horizon), the zenith stays a cool dusty
# blue, so the bird zone never goes warm. Hazy, sun-through-dust afternoon.
# Sunrise/sunset signature: this row's natural strength — a rich honey-amber that
# floods sky_bot and warms the mid to gold, the cool dusty-blue zenith above. The
# most full-bodied bloom of the set. Widened via 0.44/0.56 and 0.84/0.90.
_AMBER_KF = [
    (0.06, dict(sky_top=(110, 144, 180), sky_mid=(170, 190, 200), sky_bot=(224, 214, 188), horizon=(238, 220, 178), star_alpha=0)),
    (0.18, dict(sky_top=(110, 142, 184), sky_mid=(160, 178, 200), sky_bot=(228, 216, 184), horizon=(244, 220, 172), star_alpha=0)),
    (0.30, dict(sky_top=(112, 138, 178), sky_mid=(160, 174, 196), sky_bot=(230, 212, 176), horizon=(246, 216, 162), star_alpha=0)),
    (0.40, dict(sky_top=(116, 134, 174), sky_mid=(196, 182, 168), sky_bot=(248, 198, 130), horizon=(252, 184, 104), star_alpha=0)),
    (0.44, dict(sky_top=(112, 124, 168), sky_mid=(202, 174, 154), sky_bot=(250, 188, 116), horizon=(254, 172, 90), star_alpha=0)),
    (0.50, dict(sky_top=(102, 108, 158), sky_mid=(200, 162, 142), sky_bot=(250, 178, 108), horizon=(252, 160, 80), star_alpha=10)),
    (0.56, dict(sky_top=(82, 86, 134), sky_mid=(178, 142, 124), sky_bot=(238, 166, 106), horizon=(244, 150, 80), star_alpha=26)),
    (0.62, dict(sky_top=(56, 60, 104), sky_mid=(128, 102, 110), sky_bot=(204, 152, 116), horizon=(234, 162, 110), star_alpha=78)),
    (0.72, dict(sky_top=(20, 22, 52), sky_mid=(44, 42, 72), sky_bot=(88, 76, 88), horizon=(146, 116, 100), star_alpha=195)),
    (0.80, dict(sky_top=(34, 32, 66), sky_mid=(80, 64, 88), sky_bot=(158, 116, 96), horizon=(224, 162, 110), star_alpha=115)),
    (0.84, dict(sky_top=(56, 54, 98), sky_mid=(130, 104, 116), sky_bot=(210, 156, 112), horizon=(246, 170, 104), star_alpha=58)),
    (0.88, dict(sky_top=(86, 98, 146), sky_mid=(182, 164, 156), sky_bot=(238, 194, 136), horizon=(248, 186, 120), star_alpha=24)),
    (0.90, dict(sky_top=(100, 124, 164), sky_mid=(188, 180, 174), sky_bot=(234, 202, 156), horizon=(244, 200, 148), star_alpha=12)),
    (0.94, dict(sky_top=(108, 142, 180), sky_mid=(180, 190, 192), sky_bot=(228, 214, 182), horizon=(240, 218, 174), star_alpha=0)),
]

PALE_AMBER_HAZE = BiomeSpec(
    name='Pale Amber Haze',
    note='Sun-through-dust afternoon — cool dusty-blue zenith over a pale amber/sand horizon, the warmth held low — cooling to a deep indigo night.',
    keyframes=_AMBER_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.62, 0.84, 1.0), dither_amp=2.4, zenith_dark=0.08),
)


# ── 4. Misty Teal — soft sea-mist teal day, muted aqua dusk, deep teal night ──
# A cool teal that stays clearly teal (not foliage-green, not plain blue):
# desaturated sea-mist by day, the horizon a touch paler. Owns the teal hue at
# moderate chroma, with a saturated-dark teal night.
# Sunrise/sunset signature: a coral/salmon afterglow — teal's complementary —
# anchored to the BOTTOM ~45% (sky_bot/horizon) so the teal reclaims the top
# third and the scarlet bird keeps its silhouette against cool sky; the mid only
# half-warms. The warm/cool meeting line makes the pop read. Held wide via
# 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_TEAL_KF = [
    (0.06, dict(sky_top=(132, 148, 158), sky_mid=(176, 190, 196), sky_bot=(202, 216, 218), horizon=(216, 224, 222), star_alpha=0)),
    (0.18, dict(sky_top=(134, 152, 164), sky_mid=(178, 194, 200), sky_bot=(204, 218, 220), horizon=(218, 226, 224), star_alpha=0)),
    (0.30, dict(sky_top=(134, 150, 160), sky_mid=(178, 192, 198), sky_bot=(204, 216, 216), horizon=(218, 224, 222), star_alpha=0)),
    (0.40, dict(sky_top=(122, 140, 158), sky_mid=(168, 184, 194), sky_bot=(220, 196, 188), horizon=(248, 178, 144), star_alpha=0)),
    (0.44, dict(sky_top=(110, 130, 156), sky_mid=(150, 176, 192), sky_bot=(228, 184, 172), horizon=(252, 162, 124), star_alpha=0)),
    (0.50, dict(sky_top=(94, 116, 152), sky_mid=(138, 164, 188), sky_bot=(232, 172, 158), horizon=(250, 150, 112), star_alpha=12)),
    (0.56, dict(sky_top=(72, 100, 140), sky_mid=(116, 144, 178), sky_bot=(218, 162, 150), horizon=(242, 144, 114), star_alpha=28)),
    (0.62, dict(sky_top=(48, 74, 108), sky_mid=(82, 122, 152), sky_bot=(166, 154, 162), horizon=(222, 156, 138), star_alpha=80)),
    (0.72, dict(sky_top=(8, 26, 56), sky_mid=(16, 58, 94), sky_bot=(28, 96, 124), horizon=(58, 132, 146), star_alpha=205)),
    (0.80, dict(sky_top=(12, 34, 66), sky_mid=(26, 78, 114), sky_bot=(76, 124, 144), horizon=(196, 138, 128), star_alpha=120)),
    (0.84, dict(sky_top=(30, 56, 92), sky_mid=(62, 106, 142), sky_bot=(164, 150, 158), horizon=(242, 148, 116), star_alpha=64)),
    (0.88, dict(sky_top=(78, 116, 146), sky_mid=(140, 166, 188), sky_bot=(216, 182, 172), horizon=(250, 162, 128), star_alpha=22)),
    (0.90, dict(sky_top=(96, 130, 154), sky_mid=(150, 180, 194), sky_bot=(218, 198, 190), horizon=(246, 180, 150), star_alpha=12)),
    (0.94, dict(sky_top=(116, 144, 160), sky_mid=(162, 190, 200), sky_bot=(210, 206, 200), horizon=(240, 192, 180), star_alpha=0)),
]

MISTY_TEAL = BiomeSpec(
    name='Misty Teal',
    note='Whisper of blue-teal sea-mist — low-chroma, hue pushed past cyan to blue-teal so it reads as recessive backdrop not foliage — coral/salmon afterglow at the edges, saturated-dark teal night.',
    keyframes=_TEAL_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 5. Slate Blue-Hour — the pure Alto blue-hour, deep slate all cycle ────────
# The most recessive concept: a perpetual cool slate-blue that only shifts value
# across the day. Day and night stay maximum-recede — backdrop as pure negative
# space for the foreground.
# Sunrise/sunset signature: a warm ember-orange horizon that blooms UP through
# sky_bot and flushes the mid amber-bronze, the deep slate zenith pressing cool
# above it so the ember reads as a glowing event inside the blue hour. Held wide
# via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_SLATE_KF = [
    (0.06, dict(sky_top=(72, 96, 138), sky_mid=(120, 146, 178), sky_bot=(176, 196, 214), horizon=(204, 216, 224), star_alpha=0)),
    (0.18, dict(sky_top=(78, 104, 148), sky_mid=(126, 154, 186), sky_bot=(182, 202, 218), horizon=(210, 220, 226), star_alpha=0)),
    (0.30, dict(sky_top=(74, 100, 144), sky_mid=(122, 150, 182), sky_bot=(178, 198, 214), horizon=(206, 216, 222), star_alpha=0)),
    (0.40, dict(sky_top=(66, 84, 130), sky_mid=(122, 134, 166), sky_bot=(206, 178, 168), horizon=(244, 168, 116), star_alpha=0)),
    (0.44, dict(sky_top=(60, 76, 124), sky_mid=(126, 124, 158), sky_bot=(220, 168, 148), horizon=(250, 154, 98), star_alpha=0)),
    (0.50, dict(sky_top=(54, 66, 116), sky_mid=(124, 114, 150), sky_bot=(228, 158, 134), horizon=(250, 142, 86), star_alpha=12)),
    (0.56, dict(sky_top=(44, 56, 104), sky_mid=(112, 96, 134), sky_bot=(218, 144, 118), horizon=(246, 130, 80), star_alpha=30)),
    (0.62, dict(sky_top=(36, 50, 92), sky_mid=(92, 84, 120), sky_bot=(192, 138, 122), horizon=(234, 138, 88), star_alpha=85)),
    (0.72, dict(sky_top=(10, 18, 50), sky_mid=(20, 40, 84), sky_bot=(36, 70, 114), horizon=(66, 106, 146), star_alpha=215)),
    (0.80, dict(sky_top=(16, 28, 66), sky_mid=(38, 60, 102), sky_bot=(110, 104, 138), horizon=(208, 138, 112), star_alpha=135)),
    (0.84, dict(sky_top=(30, 44, 88), sky_mid=(86, 90, 134), sky_bot=(196, 146, 138), horizon=(248, 142, 92), star_alpha=70)),
    (0.88, dict(sky_top=(50, 72, 122), sky_mid=(120, 124, 160), sky_bot=(212, 164, 150), horizon=(250, 154, 100), star_alpha=22)),
    (0.90, dict(sky_top=(60, 86, 132), sky_mid=(122, 138, 172), sky_bot=(204, 182, 178), horizon=(242, 172, 132), star_alpha=12)),
    (0.94, dict(sky_top=(70, 96, 138), sky_mid=(118, 146, 180), sky_bot=(180, 196, 210), horizon=(218, 206, 200), star_alpha=0)),
]

SLATE_BLUE_HOUR = BiomeSpec(
    name='Slate Blue-Hour',
    note='Pure recessive Alto blue-hour — a perpetual cool slate-blue that shifts only in value, with a warm ember-orange that blooms up from the horizon at sunrise/sunset. Maximum recede otherwise.',
    keyframes=_SLATE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14),
)


# ── 6. Lavender Dusk — muted lilac-violet day, dove-grey-violet dusk, plum night ─
# A restrained lavender that holds its violet identity at low chroma: a soft
# grey-violet zenith over a paler lilac mid, kept calm and cool by day.
# Plum-saturated night. Distinct from Rose-Grey by leaning cooler/bluer-violet.
# Sunrise/sunset signature: the lilac intensifies and floods up into a vivid
# magenta/pink bloom through sky_bot and the mid; the grey-violet zenith is held
# a notch cooler/darker than the bloom (top-band value/chroma pulled back) so the
# HUD reads, the gorgeous lower bloom kept intact. Dusk settles toward calm before
# night. Held wide via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise).
_LAVENDER_KF = [
    (0.06, dict(sky_top=(110, 110, 168), sky_mid=(162, 158, 198), sky_bot=(204, 196, 218), horizon=(218, 200, 210), star_alpha=0)),
    (0.18, dict(sky_top=(116, 116, 176), sky_mid=(168, 164, 204), sky_bot=(208, 200, 222), horizon=(220, 204, 214), star_alpha=0)),
    (0.30, dict(sky_top=(112, 112, 172), sky_mid=(164, 160, 200), sky_bot=(206, 196, 218), horizon=(216, 198, 210), star_alpha=0)),
    (0.40, dict(sky_top=(98, 92, 152), sky_mid=(182, 148, 192), sky_bot=(232, 168, 198), horizon=(246, 158, 178), star_alpha=0)),
    (0.44, dict(sky_top=(92, 82, 148), sky_mid=(190, 138, 190), sky_bot=(240, 154, 192), horizon=(250, 146, 174), star_alpha=0)),
    (0.50, dict(sky_top=(84, 72, 142), sky_mid=(188, 124, 182), sky_bot=(242, 142, 184), horizon=(250, 138, 168), star_alpha=12)),
    (0.56, dict(sky_top=(72, 60, 130), sky_mid=(166, 110, 170), sky_bot=(224, 134, 178), horizon=(240, 134, 166), star_alpha=30)),
    (0.62, dict(sky_top=(54, 46, 102), sky_mid=(108, 82, 144), sky_bot=(172, 120, 162), horizon=(208, 138, 162), star_alpha=78)),
    (0.72, dict(sky_top=(24, 18, 58), sky_mid=(50, 38, 90), sky_bot=(86, 64, 118), horizon=(128, 96, 138), star_alpha=200)),
    (0.80, dict(sky_top=(36, 28, 74), sky_mid=(82, 52, 116), sky_bot=(146, 90, 150), horizon=(208, 130, 168), star_alpha=115)),
    (0.84, dict(sky_top=(54, 40, 100), sky_mid=(126, 84, 154), sky_bot=(206, 124, 172), horizon=(244, 138, 168), star_alpha=62)),
    (0.88, dict(sky_top=(96, 84, 152), sky_mid=(172, 134, 188), sky_bot=(228, 162, 192), horizon=(248, 156, 176), star_alpha=20)),
    (0.90, dict(sky_top=(104, 98, 160), sky_mid=(170, 150, 194), sky_bot=(220, 178, 202), horizon=(242, 170, 184), star_alpha=12)),
    (0.94, dict(sky_top=(110, 112, 170), sky_mid=(162, 160, 200), sky_bot=(208, 196, 218), horizon=(228, 196, 204), star_alpha=0)),
]

LAVENDER_DUSK = BiomeSpec(
    name='Lavender Dusk',
    note='Muted lilac-violet day holding its hue at low chroma — soft grey-violet zenith — flaring to a vivid magenta/pink bloom at sunrise/sunset, deepening to a plum-saturated night.',
    keyframes=_LAVENDER_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 7. Starlit Navy — deep cool navy day, ultramarine dusk, galaxy night ──────
# The deepest, coolest, most night-leaning row — a permanently dusk-blue sky
# that stays gorgeous and saturated-dark, carrying a faint starfield even by
# day. Owns the "deep starlit navy" win, kept restrained: rich but never neon.
# Sunrise/sunset signature: a deep ultramarine flushed with a saturated
# magenta/indigo glow low — the warmth stays NIGHT-LEANING (no bright high-value
# bloom that would kill the starfield), a jewel ember rising into the mid against
# the navy zenith. Held wide via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise),
# stars dimming but never gone.
_NAVY_KF = [
    (0.06, dict(sky_top=(24, 42, 96), sky_mid=(38, 70, 126), sky_bot=(62, 102, 150), horizon=(94, 134, 170), star_alpha=40)),
    (0.18, dict(sky_top=(22, 46, 102), sky_mid=(36, 76, 134), sky_bot=(60, 108, 156), horizon=(92, 140, 176), star_alpha=32)),
    (0.30, dict(sky_top=(26, 44, 100), sky_mid=(40, 72, 128), sky_bot=(64, 104, 152), horizon=(96, 136, 170), star_alpha=30)),
    (0.40, dict(sky_top=(28, 40, 98), sky_mid=(62, 58, 130), sky_bot=(132, 78, 154), horizon=(188, 92, 150), star_alpha=30)),
    (0.44, dict(sky_top=(28, 36, 98), sky_mid=(74, 54, 132), sky_bot=(156, 72, 152), horizon=(214, 86, 144), star_alpha=34)),
    (0.50, dict(sky_top=(28, 34, 96), sky_mid=(82, 50, 130), sky_bot=(170, 68, 148), horizon=(226, 80, 138), star_alpha=42)),
    (0.56, dict(sky_top=(24, 30, 90), sky_mid=(70, 48, 128), sky_bot=(154, 68, 148), horizon=(208, 84, 144), star_alpha=64)),
    (0.62, dict(sky_top=(20, 30, 80), sky_mid=(46, 56, 120), sky_bot=(104, 88, 154), horizon=(168, 114, 170), star_alpha=120)),
    (0.72, dict(sky_top=(6, 10, 44), sky_mid=(12, 28, 80), sky_bot=(24, 58, 116), horizon=(50, 100, 150), star_alpha=240)),
    (0.80, dict(sky_top=(8, 16, 56), sky_mid=(26, 42, 104), sky_bot=(74, 68, 144), horizon=(168, 94, 162), star_alpha=160)),
    (0.84, dict(sky_top=(16, 24, 74), sky_mid=(52, 48, 120), sky_bot=(132, 68, 150), horizon=(210, 86, 144), star_alpha=92)),
    (0.88, dict(sky_top=(26, 38, 96), sky_mid=(64, 58, 128), sky_bot=(136, 82, 154), horizon=(198, 98, 150), star_alpha=58)),
    (0.90, dict(sky_top=(26, 42, 98), sky_mid=(54, 64, 128), sky_bot=(106, 94, 154), horizon=(168, 114, 162), star_alpha=46)),
    (0.94, dict(sky_top=(24, 42, 96), sky_mid=(38, 70, 126), sky_bot=(62, 102, 150), horizon=(108, 130, 168), star_alpha=42)),
]

STARLIT_NAVY = BiomeSpec(
    name='Starlit Navy',
    note='Deep cool navy by day that never goes near-white — a saturated magenta/indigo dusk flush kept night-leaning, the band\'s densest galaxy night — rich, recessive, never neon.',
    keyframes=_NAVY_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.80, 1.0), dither_amp=1.6, zenith_dark=0.18),
)


# ── 8. Alpine Haze — cool high-altitude haze day, periwinkle dusk, deep blue night ─
# The thin-air high-altitude register grounded in cloud-blue #A2B6B9: a deep
# clean cobalt zenith fading to a hazy cool-grey-blue horizon (the haze line of
# distant peaks). Crisp and airy by day, with a clean cool-blue night.
# Sunrise/sunset signature: a CLEAN hand-off, not a muddy seam — glacial cyan
# owns the TOP, a true apricot/peach alpenglow band (warm, less coral, to part it
# from Misty Teal) sits LOW and luminous in sky_bot/horizon, with a soft neutral
# pale-warm transition through the mid (no cyan/apricot collision line). Held wide
# via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_ALPINE_KF = [
    (0.06, dict(sky_top=(86, 158, 186), sky_mid=(150, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),
    (0.18, dict(sky_top=(76, 168, 192), sky_mid=(144, 198, 208), sky_bot=(196, 214, 212), horizon=(216, 220, 212), star_alpha=0)),
    (0.30, dict(sky_top=(86, 160, 188), sky_mid=(152, 192, 204), sky_bot=(198, 212, 208), horizon=(216, 218, 210), star_alpha=0)),
    (0.40, dict(sky_top=(82, 158, 188), sky_mid=(196, 206, 196), sky_bot=(252, 216, 176), horizon=(255, 200, 150), star_alpha=0)),
    (0.44, dict(sky_top=(70, 150, 186), sky_mid=(204, 202, 188), sky_bot=(255, 210, 166), horizon=(255, 192, 138), star_alpha=0)),
    (0.50, dict(sky_top=(58, 138, 180), sky_mid=(208, 198, 182), sky_bot=(255, 204, 158), horizon=(255, 186, 130), star_alpha=12)),
    (0.56, dict(sky_top=(46, 116, 164), sky_mid=(190, 184, 174), sky_bot=(252, 198, 156), horizon=(255, 182, 128), star_alpha=28)),
    (0.62, dict(sky_top=(34, 82, 124), sky_mid=(126, 146, 162), sky_bot=(220, 184, 162), horizon=(244, 184, 142), star_alpha=80)),
    (0.72, dict(sky_top=(8, 28, 62), sky_mid=(16, 64, 104), sky_bot=(34, 104, 136), horizon=(70, 144, 164), star_alpha=210)),
    (0.80, dict(sky_top=(12, 38, 78), sky_mid=(40, 92, 126), sky_bot=(146, 150, 148), horizon=(232, 178, 144), star_alpha=130)),
    (0.84, dict(sky_top=(28, 74, 118), sky_mid=(108, 142, 162), sky_bot=(220, 188, 160), horizon=(255, 188, 132), star_alpha=66)),
    (0.88, dict(sky_top=(72, 148, 182), sky_mid=(192, 200, 190), sky_bot=(252, 208, 170), horizon=(255, 196, 142), star_alpha=20)),
    (0.90, dict(sky_top=(80, 154, 184), sky_mid=(196, 204, 192), sky_bot=(248, 212, 180), horizon=(255, 202, 156), star_alpha=12)),
    (0.94, dict(sky_top=(84, 156, 184), sky_mid=(150, 190, 198), sky_bot=(212, 206, 192), horizon=(246, 202, 168), star_alpha=0)),
]

ALPINE_HAZE = BiomeSpec(
    name='Alpine Haze',
    note='Thin high-altitude air — glacial cyan zenith over a pale cloud-grey haze line by day — a clean alpenglow hand-off at sunrise/sunset: cyan up top, a true apricot/peach band low, a soft neutral transition between, clean cool-cyan night.',
    keyframes=_ALPINE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14),
)


# ── 9. Cool Eucalyptus — pale sage-cyan day, kept COOL (not foliage), slate night ─
# The sage/eucalyptus direction steered firmly COOL so it never competes with
# foliage green: a hazy desaturated sage-cyan (clearly blue-green, not leaf
# green) zenith over a paler dust-sage horizon by day. Soft, dry, herbal.
# Sunrise/sunset signature: the dust-sage lifts in CHROMA and warms toward a
# luminous GOLD-GREEN mid (not olive/grey) and a bright warm-gold horizon — a
# glowing ground-bloom, the cool grey-blue zenith holding above so the warmth
# stays off the bird zone. Held wide via 0.44/0.56 (sunset) and 0.84/0.90.
_EUCALYPTUS_KF = [
    (0.06, dict(sky_top=(104, 128, 162), sky_mid=(160, 180, 196), sky_bot=(202, 214, 200), horizon=(216, 220, 192), star_alpha=0)),
    (0.18, dict(sky_top=(106, 132, 168), sky_mid=(164, 184, 200), sky_bot=(204, 216, 200), horizon=(218, 222, 192), star_alpha=0)),
    (0.30, dict(sky_top=(108, 130, 164), sky_mid=(166, 182, 196), sky_bot=(206, 214, 196), horizon=(218, 218, 188), star_alpha=0)),
    (0.40, dict(sky_top=(104, 124, 156), sky_mid=(196, 196, 142), sky_bot=(246, 218, 124), horizon=(255, 206, 94), star_alpha=0)),
    (0.44, dict(sky_top=(98, 116, 152), sky_mid=(204, 194, 128), sky_bot=(252, 212, 106), horizon=(255, 196, 78), star_alpha=0)),
    (0.50, dict(sky_top=(88, 104, 144), sky_mid=(204, 188, 120), sky_bot=(255, 206, 96), horizon=(255, 188, 68), star_alpha=12)),
    (0.56, dict(sky_top=(70, 88, 128), sky_mid=(178, 172, 118), sky_bot=(244, 196, 98), horizon=(250, 180, 70), star_alpha=28)),
    (0.62, dict(sky_top=(46, 66, 102), sky_mid=(110, 128, 122), sky_bot=(204, 188, 122), horizon=(234, 192, 110), star_alpha=78)),
    (0.72, dict(sky_top=(12, 26, 52), sky_mid=(24, 58, 80), sky_bot=(48, 102, 100), horizon=(92, 146, 126), star_alpha=200)),
    (0.80, dict(sky_top=(18, 34, 62), sky_mid=(44, 80, 90), sky_bot=(126, 138, 96), horizon=(224, 178, 102), star_alpha=118)),
    (0.84, dict(sky_top=(36, 54, 88), sky_mid=(100, 122, 118), sky_bot=(206, 178, 116), horizon=(255, 186, 86), star_alpha=64)),
    (0.88, dict(sky_top=(88, 114, 148), sky_mid=(180, 186, 150), sky_bot=(240, 212, 128), horizon=(255, 198, 90), star_alpha=20)),
    (0.90, dict(sky_top=(96, 122, 156), sky_mid=(178, 190, 162), sky_bot=(234, 216, 142), horizon=(252, 206, 110), star_alpha=12)),
    (0.94, dict(sky_top=(102, 126, 160), sky_mid=(158, 180, 196), sky_bot=(204, 214, 196), horizon=(224, 214, 184), star_alpha=0)),
]

COOL_EUCALYPTUS = BiomeSpec(
    name='Cool Eucalyptus',
    note='Grey-blue slate zenith with the eucalyptus sage confined to a low dust-sage horizon band — cool up high by day, warming through gold-green to a low apricot bloom at sunrise/sunset — to a deep slate-teal night.',
    keyframes=_EUCALYPTUS_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.2, zenith_dark=0.10),
)


# ── 10. Pearl Overcast — soft pearl-grey-blue day with low warmth, blue-grey night ─
# The "overcast pearl with warmth" brief, kept off neutral grey by a decisive
# cool-blue cast in the zenith/mid and a barely-warm cream wash low by day. The
# softest, most diffuse, lowest-contrast backdrop — overcast but luminous.
# Night is a saturated blue-grey, not black.
# Sunrise/sunset signature: an internal soft VALUE gradient — a warm peach-grey
# GLOW that rises bright from the horizon and diffuses upward, felt as luminance
# (sun behind cloud) not just a hue tint; soft and diffuse, no hard band, the
# cooler pearl zenith holding above. Held wide via 0.44/0.56 and 0.84/0.90.
_PEARL_KF = [
    (0.06, dict(sky_top=(140, 142, 170), sky_mid=(190, 192, 208), sky_bot=(218, 218, 222), horizon=(230, 224, 216), star_alpha=0)),
    (0.18, dict(sky_top=(144, 146, 176), sky_mid=(192, 196, 212), sky_bot=(220, 220, 224), horizon=(232, 226, 218), star_alpha=0)),
    (0.30, dict(sky_top=(142, 144, 174), sky_mid=(190, 194, 210), sky_bot=(218, 218, 222), horizon=(230, 224, 214), star_alpha=0)),
    (0.40, dict(sky_top=(150, 146, 172), sky_mid=(216, 200, 194), sky_bot=(252, 224, 202), horizon=(255, 218, 186), star_alpha=0)),
    (0.44, dict(sky_top=(148, 142, 170), sky_mid=(222, 198, 190), sky_bot=(255, 222, 196), horizon=(255, 214, 180), star_alpha=0)),
    (0.50, dict(sky_top=(140, 134, 166), sky_mid=(224, 194, 188), sky_bot=(255, 222, 194), horizon=(255, 212, 176), star_alpha=12)),
    (0.56, dict(sky_top=(116, 110, 150), sky_mid=(206, 180, 182), sky_bot=(254, 216, 190), horizon=(255, 208, 174), star_alpha=28)),
    (0.62, dict(sky_top=(70, 70, 114), sky_mid=(144, 132, 154), sky_bot=(224, 198, 188), horizon=(248, 204, 180), star_alpha=72)),
    (0.72, dict(sky_top=(28, 26, 58), sky_mid=(50, 54, 92), sky_bot=(86, 96, 126), horizon=(132, 142, 160), star_alpha=185)),
    (0.80, dict(sky_top=(38, 38, 76), sky_mid=(84, 78, 110), sky_bot=(170, 144, 150), horizon=(232, 192, 176), star_alpha=108)),
    (0.84, dict(sky_top=(58, 56, 100), sky_mid=(136, 122, 146), sky_bot=(228, 192, 184), horizon=(255, 202, 170), star_alpha=58)),
    (0.88, dict(sky_top=(128, 124, 162), sky_mid=(202, 188, 198), sky_bot=(250, 222, 206), horizon=(255, 216, 184), star_alpha=18)),
    (0.90, dict(sky_top=(140, 138, 170), sky_mid=(204, 196, 206), sky_bot=(246, 226, 214), horizon=(255, 216, 192), star_alpha=10)),
    (0.94, dict(sky_top=(140, 142, 172), sky_mid=(192, 190, 204), sky_bot=(222, 216, 216), horizon=(244, 210, 192), star_alpha=0)),
]

PEARL_OVERCAST = BiomeSpec(
    name='Pearl Overcast',
    note='Softest diffuse backdrop — pearl-grey-blue held cool by a decisive blue cast — lifting to a luminous warm peach-grey glow at sunrise/sunset, overcast but luminous, blue-grey night, never charcoal.',
    keyframes=_PEARL_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.62, 0.84, 1.0), dither_amp=2.4, zenith_dark=0.15),
)


# Ordered (id, spec) list — the 10 concept rows in sheet order.
CONCEPTS = [
    ('dawn_rose_grey', DAWN_ROSE_GREY),
    ('powder_morning', POWDER_MORNING),
    ('pale_amber_haze', PALE_AMBER_HAZE),
    ('misty_teal', MISTY_TEAL),
    ('slate_blue_hour', SLATE_BLUE_HOUR),
    ('lavender_dusk', LAVENDER_DUSK),
    ('starlit_navy', STARLIT_NAVY),
    ('alpine_haze', ALPINE_HAZE),
    ('cool_eucalyptus', COOL_EUCALYPTUS),
    ('pearl_overcast', PEARL_OVERCAST),
]
