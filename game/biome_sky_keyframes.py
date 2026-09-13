"""
Sky-only day/night keyframe tables for the biome sky designs.

Ported from the biome exploration's `biome_variants.py`, stripped to the
sky-relevant keys only — `sky_top`, `sky_mid`, `sky_bot`, `horizon`,
`star_alpha`. Every structural key (`mtn_*`, `struct_*`, `ground_*`,
`foliage_*`) and the ridge/signature/foliage params are intentionally
dropped: these designs contribute a sky color field + night-star sprinkle,
nothing else. The 10-stage day→night arc falls out of interpolating each
biome's keyframes against `phase` (0..1).

Reached through `game/sky_designs.py`. The first ten `BIOMES` entries are in
sheet order (matching the rows of
`docs/biome_redesign/round_7_all_skystars_daynight.png`); `alpine_haze` is a
later calm-lineage addition appended after them and is the current live sky.
"""
from game.biome_sky import BiomeSpec, SkyParams


# ── The 10 day-stage columns (predawn → night arc) ───────────────────────────
STAGES = [
    ("predawn", 0.8),
    ("dawn", 0.88),
    ("sunrise", 0.94),
    ("morning", 0.06),
    ("midday", 0.18),
    ("afternoon", 0.3),
    ("golden", 0.4),
    ("sunset", 0.5),
    ("dusk", 0.62),
    ("night", 0.7),
]


_DESERT_KF = [
    (0.06, dict(sky_top=(55, 125, 205), sky_mid=(150, 195, 225), sky_bot=(215, 230, 238), horizon=(250, 238, 210), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(60, 120, 210), sky_mid=(132, 182, 226), sky_bot=(202, 226, 240), horizon=(246, 236, 206), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(96, 124, 190), sky_mid=(236, 182, 122), sky_bot=(255, 206, 150), horizon=(255, 222, 150), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(110, 68, 122), sky_mid=(236, 110, 90), sky_bot=(255, 160, 92), horizon=(255, 192, 120), star_alpha=0)),  # sunset
    (0.62, dict(sky_top=(40, 35, 82), sky_mid=(92, 60, 122), sky_bot=(182, 112, 120), horizon=(240, 162, 132), star_alpha=40)),  # dusk
    (0.7, dict(sky_top=(10, 14, 40), sky_mid=(22, 32, 70), sky_bot=(46, 60, 100), horizon=(120, 122, 150), star_alpha=210)),  # night
    (0.8, dict(sky_top=(26, 30, 72), sky_mid=(52, 56, 112), sky_bot=(114, 92, 142), horizon=(202, 152, 162), star_alpha=110)),  # predawn
    (0.94, dict(sky_top=(70, 110, 180), sky_mid=(255, 166, 140), sky_bot=(255, 216, 166), horizon=(255, 236, 182), star_alpha=0)),  # sunrise
]

DESERT_MESA = BiomeSpec(
    name='Desert Mesa',
    note='Flat-topped sandstone buttes + eroded arch over rolling dunes; bone-dry warm palette.',
    keyframes=_DESERT_KF,
    sky=SkyParams(positions=(0.0, 0.28, 0.58, 0.84, 1.0), dither_amp=2.2, zenith_dark=0.11),
)

_ALPINE_KF = [
    (0.06, dict(sky_top=(78, 140, 210), sky_mid=(150, 196, 232), sky_bot=(210, 232, 244), horizon=(232, 240, 246), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(58, 128, 214), sky_mid=(138, 190, 232), sky_bot=(206, 230, 244), horizon=(228, 238, 246), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(110, 150, 206), sky_mid=(232, 200, 176), sky_bot=(255, 222, 188), horizon=(255, 226, 192), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(96, 96, 150), sky_mid=(228, 140, 132), sky_bot=(255, 178, 150), horizon=(255, 198, 168), star_alpha=20)),  # sunset
    (0.62, dict(sky_top=(40, 48, 96), sky_mid=(86, 86, 140), sky_bot=(150, 130, 158), horizon=(204, 168, 168), star_alpha=70)),  # dusk
    (0.7, dict(sky_top=(10, 16, 44), sky_mid=(22, 34, 72), sky_bot=(44, 60, 100), horizon=(110, 124, 158), star_alpha=215)),  # night
    (0.8, dict(sky_top=(26, 32, 78), sky_mid=(54, 60, 116), sky_bot=(112, 110, 154), horizon=(184, 162, 176), star_alpha=120)),  # predawn
    (0.94, dict(sky_top=(84, 142, 206), sky_mid=(248, 196, 184), sky_bot=(255, 220, 196), horizon=(255, 228, 202), star_alpha=0)),  # sunrise
]

ALPINE_SNOWPEAK = BiomeSpec(
    name='Alpine Snowpeak',
    note='Tall jagged snow-capped granite over a dark conifer treeline; cold blue-white, crisp high-altitude air.',
    keyframes=_ALPINE_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.66, 0.88, 1.0), dither_amp=1.6, zenith_dark=0.16),
)

_VOLCANO_KF = [
    (0.06, dict(sky_top=(104, 96, 108), sky_mid=(168, 130, 110), sky_bot=(196, 156, 128), horizon=(210, 158, 118), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(114, 108, 124), sky_mid=(180, 144, 122), sky_bot=(206, 166, 136), horizon=(216, 162, 120), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(122, 86, 90), sky_mid=(214, 130, 86), sky_bot=(244, 162, 96), horizon=(252, 168, 92), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(86, 52, 70), sky_mid=(190, 78, 66), sky_bot=(230, 116, 64), horizon=(248, 138, 64), star_alpha=20)),  # sunset
    (0.62, dict(sky_top=(46, 28, 46), sky_mid=(108, 42, 50), sky_bot=(170, 74, 54), horizon=(214, 100, 50), star_alpha=70)),  # dusk
    (0.7, dict(sky_top=(16, 12, 24), sky_mid=(40, 18, 26), sky_bot=(78, 30, 28), horizon=(150, 56, 34), star_alpha=170)),  # night
    (0.8, dict(sky_top=(28, 22, 40), sky_mid=(64, 34, 44), sky_bot=(118, 56, 48), horizon=(176, 80, 46), star_alpha=110)),  # predawn
    (0.94, dict(sky_top=(110, 78, 86), sky_mid=(224, 124, 84), sky_bot=(248, 158, 96), horizon=(252, 162, 88), star_alpha=0)),  # sunrise
]

VOLCANIC_CALDERA = BiomeSpec(
    name='Volcanic Caldera',
    note='Caldera-rim ridges around a crater notch; ash-charcoal terrain, smoky ember sky, lava glow at night.',
    keyframes=_VOLCANO_KF,
    sky=SkyParams(positions=(0.0, 0.3, 0.6, 0.82, 1.0), dither_amp=2.6, zenith_dark=0.12),
)

_KARST_KF = [
    (0.06, dict(sky_top=(150, 186, 196), sky_mid=(196, 216, 218), sky_bot=(224, 234, 230), horizon=(232, 238, 230), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(128, 178, 196), sky_mid=(184, 212, 218), sky_bot=(218, 232, 230), horizon=(228, 236, 228), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(168, 184, 178), sky_mid=(236, 210, 168), sky_bot=(252, 226, 184), horizon=(252, 228, 184), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(140, 130, 152), sky_mid=(226, 158, 150), sky_bot=(248, 188, 158), horizon=(250, 198, 162), star_alpha=20)),  # sunset
    (0.62, dict(sky_top=(62, 70, 100), sky_mid=(112, 118, 142), sky_bot=(168, 158, 166), horizon=(208, 184, 176), star_alpha=70)),  # dusk
    (0.7, dict(sky_top=(12, 18, 42), sky_mid=(26, 38, 70), sky_bot=(52, 66, 96), horizon=(118, 126, 142), star_alpha=205)),  # night
    (0.8, dict(sky_top=(30, 38, 70), sky_mid=(60, 70, 104), sky_bot=(120, 120, 144), horizon=(190, 172, 172), star_alpha=110)),  # predawn
    (0.94, dict(sky_top=(140, 172, 188), sky_mid=(248, 196, 168), sky_bot=(254, 222, 184), horizon=(254, 224, 184), star_alpha=0)),  # sunrise
]

KARST_WATERTOWN = BiomeSpec(
    name='Karst Watertown',
    note='Misty vertical karst towers over a still-water inlet of stilt houses; soft jade/grey, humid and serene.',
    keyframes=_KARST_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.62, 0.84, 1.0), dither_amp=1.8, zenith_dark=0.07),
)

_AUTUMN_KF = [
    (0.06, dict(sky_top=(110, 160, 206), sky_mid=(190, 208, 214), sky_bot=(232, 224, 196), horizon=(248, 226, 186), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(92, 152, 210), sky_mid=(178, 204, 216), sky_bot=(226, 222, 198), horizon=(244, 224, 188), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(120, 148, 196), sky_mid=(244, 196, 132), sky_bot=(255, 214, 156), horizon=(255, 216, 148), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(112, 84, 122), sky_mid=(232, 120, 84), sky_bot=(255, 156, 92), horizon=(255, 178, 106), star_alpha=20)),  # sunset
    (0.62, dict(sky_top=(46, 40, 86), sky_mid=(104, 64, 118), sky_bot=(192, 116, 110), horizon=(238, 154, 116), star_alpha=70)),  # dusk
    (0.7, dict(sky_top=(12, 16, 44), sky_mid=(26, 30, 68), sky_bot=(52, 50, 86), horizon=(128, 100, 110), star_alpha=205)),  # night
    (0.8, dict(sky_top=(30, 34, 76), sky_mid=(60, 56, 108), sky_bot=(124, 96, 122), horizon=(206, 150, 138), star_alpha=110)),  # predawn
    (0.94, dict(sky_top=(104, 150, 200), sky_mid=(252, 192, 152), sky_bot=(255, 216, 174), horizon=(255, 222, 178), star_alpha=0)),  # sunrise
]

AUTUMN_HIGHLANDS = BiomeSpec(
    name='Autumn Highlands',
    note='Rolling forested hills under a fiery maple canopy; terrace wall + cairn way-marker, warm and cozy.',
    keyframes=_AUTUMN_KF,
    sky=SkyParams(positions=(0.0, 0.3, 0.6, 0.84, 1.0), dither_amp=2.2, zenith_dark=0.05),
)

_GORGE_KF = [
    (0.06, dict(sky_top=(150, 184, 188), sky_mid=(196, 216, 214), sky_bot=(222, 232, 226), horizon=(228, 234, 226), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(132, 178, 190), sky_mid=(188, 212, 214), sky_bot=(218, 230, 226), horizon=(224, 232, 224), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(166, 184, 178), sky_mid=(234, 210, 168), sky_bot=(250, 224, 182), horizon=(250, 226, 184), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(138, 128, 150), sky_mid=(224, 158, 148), sky_bot=(246, 188, 156), horizon=(248, 196, 160), star_alpha=20)),  # sunset
    (0.62, dict(sky_top=(56, 66, 100), sky_mid=(106, 116, 142), sky_bot=(164, 158, 166), horizon=(204, 184, 178), star_alpha=70)),  # dusk
    (0.7, dict(sky_top=(12, 18, 42), sky_mid=(26, 38, 68), sky_bot=(50, 64, 92), horizon=(116, 126, 140), star_alpha=205)),  # night
    (0.8, dict(sky_top=(30, 38, 70), sky_mid=(60, 70, 104), sky_bot=(118, 120, 144), horizon=(188, 172, 174), star_alpha=110)),  # predawn
    (0.94, dict(sky_top=(140, 172, 184), sky_mid=(248, 198, 168), sky_bot=(252, 222, 184), horizon=(252, 224, 186), star_alpha=0)),  # sunrise
]

MISTY_GORGE = BiomeSpec(
    name='Misty Gorge',
    note='Tall narrow Guilin karst towers receding into deep ink-wash mist; celadon/blue-grey monochrome, serene.',
    keyframes=_GORGE_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.62, 0.84, 1.0), dither_amp=1.6, zenith_dark=0.08),
)

_SNOW_KF = [
    (0.06, dict(sky_top=(150, 168, 188), sky_mid=(196, 208, 220), sky_bot=(220, 228, 234), horizon=(226, 230, 232), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(134, 162, 188), sky_mid=(188, 204, 218), sky_bot=(214, 224, 232), horizon=(222, 228, 230), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(160, 168, 186), sky_mid=(232, 212, 184), sky_bot=(250, 228, 198), horizon=(250, 228, 196), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(126, 118, 150), sky_mid=(220, 156, 152), sky_bot=(244, 188, 166), horizon=(246, 196, 170), star_alpha=20)),  # sunset
    (0.62, dict(sky_top=(46, 54, 96), sky_mid=(92, 96, 138), sky_bot=(152, 144, 162), horizon=(200, 178, 176), star_alpha=70)),  # dusk
    (0.7, dict(sky_top=(10, 16, 42), sky_mid=(22, 32, 66), sky_bot=(44, 58, 92), horizon=(108, 122, 152), star_alpha=210)),  # night
    (0.8, dict(sky_top=(28, 34, 76), sky_mid=(56, 62, 114), sky_bot=(114, 114, 152), horizon=(184, 166, 174), star_alpha=110)),  # predawn
    (0.94, dict(sky_top=(150, 172, 192), sky_mid=(246, 204, 188), sky_bot=(250, 224, 200), horizon=(250, 226, 202), star_alpha=0)),  # sunrise
]

SNOW_TEMPLE = BiomeSpec(
    name='Snow Temple',
    note='Snow-capped ink peaks over an austere whitewashed temple; near-monochrome grey + white, one warm lantern.',
    keyframes=_SNOW_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.66, 0.88, 1.0), dither_amp=1.4, zenith_dark=0.15),
)

_MAPLE_KF = [
    (0.06, dict(sky_top=(132, 162, 188), sky_mid=(196, 206, 206), sky_bot=(228, 222, 204), horizon=(238, 222, 196), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(114, 156, 192), sky_mid=(186, 202, 206), sky_bot=(222, 220, 204), horizon=(234, 220, 196), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(146, 152, 184), sky_mid=(240, 196, 144), sky_bot=(252, 214, 162), horizon=(252, 214, 156), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(116, 88, 128), sky_mid=(230, 122, 88), sky_bot=(250, 156, 96), horizon=(252, 176, 108), star_alpha=20)),  # sunset
    (0.62, dict(sky_top=(48, 42, 88), sky_mid=(106, 66, 118), sky_bot=(190, 116, 110), horizon=(236, 152, 116), star_alpha=70)),  # dusk
    (0.7, dict(sky_top=(12, 16, 44), sky_mid=(26, 30, 66), sky_bot=(50, 48, 84), horizon=(122, 96, 108), star_alpha=205)),  # night
    (0.8, dict(sky_top=(30, 34, 76), sky_mid=(60, 56, 106), sky_bot=(122, 96, 120), horizon=(202, 148, 134), star_alpha=110)),  # predawn
    (0.94, dict(sky_top=(126, 156, 188), sky_mid=(250, 196, 154), sky_bot=(252, 216, 174), horizon=(252, 220, 176), star_alpha=0)),  # sunrise
]

MAPLE_MONASTERY = BiomeSpec(
    name='Maple Monastery',
    note='Hillside monastery (terrace + stupa + red lantern) under fiery maple ink; warm autumn architecture in mist.',
    keyframes=_MAPLE_KF,
    sky=SkyParams(positions=(0.0, 0.3, 0.6, 0.84, 1.0), dither_amp=1.8, zenith_dark=0.07),
)

_CLOUDSEA_KF = [
    (0.06, dict(sky_top=(96, 150, 206), sky_mid=(168, 200, 228), sky_bot=(212, 228, 238), horizon=(228, 234, 240), star_alpha=0)),  # morning
    (0.18, dict(sky_top=(74, 142, 212), sky_mid=(154, 196, 230), sky_bot=(206, 226, 240), horizon=(224, 232, 240), star_alpha=0)),  # midday
    (0.4, dict(sky_top=(120, 152, 200), sky_mid=(240, 200, 156), sky_bot=(252, 220, 178), horizon=(252, 222, 176), star_alpha=0)),  # golden
    (0.5, dict(sky_top=(106, 92, 144), sky_mid=(226, 142, 116), sky_bot=(248, 178, 134), horizon=(250, 190, 144), star_alpha=20)),  # sunset
    (0.62, dict(sky_top=(48, 56, 102), sky_mid=(96, 104, 144), sky_bot=(160, 156, 172), horizon=(202, 182, 178), star_alpha=70)),  # dusk
    (0.7, dict(sky_top=(10, 16, 44), sky_mid=(22, 34, 70), sky_bot=(46, 60, 96), horizon=(112, 126, 150), star_alpha=210)),  # night
    (0.8, dict(sky_top=(28, 36, 78), sky_mid=(56, 66, 114), sky_bot=(116, 120, 152), horizon=(186, 172, 178), star_alpha=110)),  # predawn
    (0.94, dict(sky_top=(110, 156, 204), sky_mid=(250, 200, 168), sky_bot=(252, 222, 186), horizon=(252, 224, 188), star_alpha=0)),  # sunrise
]

CLOUD_SEA_PEAKS = BiomeSpec(
    name='Cloud Sea Peaks',
    note='Karst spike peaks poking through a dense horizontal sea of clouds; cool dawn palette, the cloud-sea is the hero.',
    keyframes=_CLOUDSEA_KF,
    sky=SkyParams(positions=(0.0, 0.3, 0.58, 0.8, 1.0), dither_amp=1.8, zenith_dark=0.12),
)

_MOONCLIFF_KF = [
    (0.06, dict(sky_top=(58, 80, 120), sky_mid=(96, 124, 158), sky_bot=(146, 168, 188), horizon=(176, 188, 196), star_alpha=40)),  # morning
    (0.18, dict(sky_top=(64, 88, 132), sky_mid=(106, 134, 168), sky_bot=(156, 178, 196), horizon=(184, 196, 202), star_alpha=30)),  # midday
    (0.4, dict(sky_top=(66, 78, 122), sky_mid=(150, 138, 150), sky_bot=(200, 184, 174), horizon=(214, 196, 178), star_alpha=20)),  # golden
    (0.5, dict(sky_top=(58, 52, 102), sky_mid=(150, 100, 124), sky_bot=(208, 148, 134), horizon=(222, 162, 138), star_alpha=60)),  # sunset
    (0.62, dict(sky_top=(28, 32, 78), sky_mid=(56, 60, 108), sky_bot=(104, 104, 142), horizon=(168, 156, 168), star_alpha=130)),  # dusk
    (0.7, dict(sky_top=(8, 12, 38), sky_mid=(18, 26, 60), sky_bot=(38, 50, 84), horizon=(96, 110, 138), star_alpha=220)),  # night
    (0.8, dict(sky_top=(20, 26, 64), sky_mid=(42, 50, 96), sky_bot=(92, 100, 138), horizon=(160, 156, 172), star_alpha=150)),  # predawn
    (0.94, dict(sky_top=(60, 92, 138), sky_mid=(170, 160, 168), sky_bot=(216, 198, 184), horizon=(224, 204, 186), star_alpha=30)),  # sunrise
]

MOONLIT_PINE_CLIFF = BiomeSpec(
    name='Moonlit Pine Cliff',
    note='Dramatic dark cliff silhouette under a big moon; deep indigo ink that stays nocturnal all cycle, pine + ravens.',
    keyframes=_MOONCLIFF_KF,
    sky=SkyParams(positions=(0.0, 0.3, 0.6, 0.82, 1.0), dither_amp=1.6, zenith_dark=0.16),
)

# ── Calm-lineage addition (round-12 UX exploration, not in the round_7 sheet) ─
# Alpine Haze — the cool high-altitude-haze DAY (glacial cyan-cool zenith into a
# pale cloud-grey horizon haze) that won the calm/UX study, now carrying the
# signed-off "Coral Ember" multi-hue evening: the day holds the loved cyan, then
# a luminous coral-gold golden hour eases in — a warm bridge at 0.235 keeps the
# cyan→gold onset gradual so the zenith never snaps dark — and travels gold-coral
# → deep coral-red → coral-plum, the top deepening to violet only by the dwell.
# It then darkens into a dark COOL plum-indigo star-rich night: the coral horizon
# ember persists through dusk, fades by twilight, and is fully cool by deep night
# so the WHOLE dome reads as night (never black), before a fresh coral-cream dawn
# lifts it back. Ported verbatim from the sunset study
# (`tools/sky_alpine_sunsets.py` row 'coral_ember') with its night-balanced
# retiming applied, so the live sky matches the signed-off figure. The three DAY
# anchors (0.04/0.12/0.20) are the original cyan day, byte-for-byte.
_ALPINE_HAZE_KF = [
    (0.04, dict(sky_top=(86, 158, 186), sky_mid=(150, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),
    (0.12, dict(sky_top=(76, 168, 192), sky_mid=(144, 198, 208), sky_bot=(196, 214, 212), horizon=(216, 220, 212), star_alpha=0)),
    (0.20, dict(sky_top=(86, 160, 188), sky_mid=(152, 192, 204), sky_bot=(198, 212, 208), horizon=(216, 218, 210), star_alpha=0)),
    (0.235, dict(sky_top=(141, 153, 157), sky_mid=(232, 188, 166), sky_bot=(255, 186, 144), horizon=(255, 164, 104), star_alpha=0)),
    (0.27, dict(sky_top=(181, 150, 139), sky_mid=(254, 168, 126), sky_bot=(255, 158, 96), horizon=(255, 122, 60), star_alpha=0)),
    (0.31, dict(sky_top=(168, 122, 140), sky_mid=(250, 138, 100), sky_bot=(255, 138, 72), horizon=(252, 96, 48), star_alpha=5)),
    (0.37, dict(sky_top=(108, 66, 116), sky_mid=(244, 96, 80), sky_bot=(252, 116, 60), horizon=(246, 76, 44), star_alpha=12)),
    (0.42, dict(sky_top=(80, 42, 112), sky_mid=(222, 74, 98), sky_bot=(228, 80, 104), horizon=(218, 72, 98), star_alpha=30)),
    (0.47, dict(sky_top=(37, 30, 70), sky_mid=(118, 59, 80), sky_bot=(162, 78, 106), horizon=(170, 82, 108), star_alpha=88)),
    (0.52, dict(sky_top=(28, 30, 64), sky_mid=(68, 42, 68), sky_bot=(90, 55, 90), horizon=(108, 66, 84), star_alpha=156)),
    (0.56, dict(sky_top=(23, 28, 57), sky_mid=(33, 35, 61), sky_bot=(44, 45, 68), horizon=(57, 56, 75), star_alpha=222)),
    (0.82, dict(sky_top=(23, 28, 57), sky_mid=(33, 35, 61), sky_bot=(44, 45, 68), horizon=(57, 56, 75), star_alpha=222)),
    (0.86, dict(sky_top=(24, 30, 59), sky_mid=(35, 37, 63), sky_bot=(45, 47, 70), horizon=(61, 59, 78), star_alpha=166)),
    (0.92, dict(sky_top=(76, 124, 158), sky_mid=(244, 160, 144), sky_bot=(255, 178, 150), horizon=(255, 158, 120), star_alpha=20)),
    (0.97, dict(sky_top=(86, 146, 176), sky_mid=(248, 180, 166), sky_bot=(255, 190, 164), horizon=(255, 170, 140), star_alpha=0)),
]

ALPINE_HAZE = BiomeSpec(
    name='Alpine Haze',
    note='Glacial cyan-cool high-altitude day melting into a Coral Ember evening — a luminous coral-gold golden hour that travels gold-coral to coral-red to coral-plum, then slowly darkens into a dark cool plum-indigo star-rich night, then a fresh coral-cream dawn. The warm cool->warm line sinks toward the horizon as the sun sets (and rises again at dawn). Crisp airy day, warm coral dusk, deep cool plum-indigo night that reads as night yet never goes black.',
    keyframes=_ALPINE_HAZE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14, descent_drop=0.20),
)


# id → spec. The first ten are in round_7 sheet order; alpine_haze is the
# calm-lineage addition appended after them.
BIOMES = {
    "desert_mesa": DESERT_MESA,
    "alpine_snowpeak": ALPINE_SNOWPEAK,
    "volcanic_caldera": VOLCANIC_CALDERA,
    "karst_watertown": KARST_WATERTOWN,
    "autumn_highlands": AUTUMN_HIGHLANDS,
    "misty_gorge": MISTY_GORGE,
    "snow_temple": SNOW_TEMPLE,
    "maple_monastery": MAPLE_MONASTERY,
    "cloud_sea_peaks": CLOUD_SEA_PEAKS,
    "moonlit_pine_cliff": MOONLIT_PINE_CLIFF,
    "alpine_haze": ALPINE_HAZE,
}

BIOME_NAMES = {k: v.name for k, v in BIOMES.items()}
BIOME_NOTES = {k: v.note for k, v in BIOMES.items()}

