"""
Alpine Haze sunset/sunrise study, v4 — the Ember-Gold lineage, re-graded.

The live game ALREADY ships the "Ember Gold" evening (these exact keyframes are
the live OKLab `paint_sky` source, so this study sheet == what ships). The user
played it and asked for three fixes plus a set restructure. v4 keeps the loved
cool glacial-cyan DAY byte-for-byte and the whole `_compose`/`_retime` machinery,
and re-authors the evening to fix what shipped:

  FIX 1 — LUMINOUS golden onset. The live golden 0.40 top is a muted dark warm-
    brown and the top plunged to deep violet by 0.50, so leaving the bright frozen
    afternoon read as the zenith "snapping dark". v4 lifts golden 0.40 to a bright
    warm top (pale gold / warm-peach, clearly lighter than the old brown, never
    cyan — real golden hour scatters blue OUT, the zenith stays warm-pale), ADDS a
    0.35 INSERT bridge that eases the cyan afternoon top into that warm gold in
    BOTH value and hue through a warm-cyan / pale-gold (never a dark/grey/blue
    dip), and makes the top's descent into the deep-violet sunset GRADUAL across
    0.40→0.44→0.50→0.56 — golden stays bright/warm, only by sunset/dwell does the
    top reach deep violet. The warm low-band entry the user liked (orange horizon +
    warm sky_bot coming in low) is KEPT.

  FIX 2 — a NIGHT that reads as night. The live deep-night kept a warm bronze
    ember at the horizon, so the bottom never joined the dark. v4 takes the deep-
    night 0.72 horizon + sky_bot DOWN to a dark, cool-leaning value — an iris-dark
    dome, no orange ember at the deepest point — graded GRADUALLY: a warm ember may
    persist through dusk 0.62, fades at twilight 0.68, fully resolved to dark+cool
    by deep-night 0.72 (and 0.80 holds that dark). This is the BOTTOM band going
    dark+cool, NOT the whole sky going black — sky_top keeps the "dark but never
    black" lifted-indigo floor (~min (14,16,40), graded by tier) so the dome reads
    a cool dark indigo top AND a dark cool bottom with the star field still legible.
    Predawn/dawn warm-up (0.88/0.94) is unchanged in spirit.

  FIX 3 — smoother colour travel. No adjacent authored pair (0.35→0.40→0.44→0.50
    →0.56→0.62→0.68→0.72) jumps hue/value too far in one step; the gold→orange→plum
    handoff is routed through saturated coral/rose bridges in the mid so no vertical
    sample greys, and the 0.44/0.56 dwell frames carry the large gaps.

SET RESTRUCTURE — the user loves Ember Gold, so the set is WEIGHTED toward it:
  ~6 EMBER-GOLD-FAMILY evolutions — all clear relatives of the shipped anchor
    (warm gold→orange→plum over time), each a distinct but restrained move:
    1 Ember Gold (brighter-gold), 2 Amber Warm (amber), 3 Rose-Gold Glow (rose-
    gold), 4 Coral Ember (coral-warm), 5 Deep Plum Ember (deeper-plum), 6 Cool
    Plum Gold (a cooler, violet-leaning gold).
  ~4 BOLD departures — the adventurous end, free to travel further from the warm
    anchor: 7 Amethyst Nightfall (jewel/amethyst), 8 Indigo & Fire (indigo & fire),
    9 Aurora Teal-Magenta (teal↔magenta aurora), 10 Blood Scarlet (a hot scarlet→
    oxblood inferno — the genuinely-different fourth direction, the only pure-red
    evening in the set).
  Row 11 EMBER_GOLD_LIVE is the live "too dark" baseline, carried VERBATIM as the
    before/after reference — it is deliberately NOT fixed.

Provably-identical DAY spine: the cool-cyan day anchors (0.06 / 0.18 / 0.30) are
authored ONCE in `_ALPINE_HAZE_KF` and copied verbatim into every design — the
identity anchor, never moved or darkened. The new 0.35 is an INSERT that eases OFF
the day (it is not spine). Everything from golden onward is per-design.

Night is dark but NEVER black — a visible deep COOL colour cast up top + a dark
cool bottom + a legible star field, no warm ember at the deepest point. The deep-
night `sky_top` floor is held at a min of ~(14,16,40) and graded across three
brightness tiers — MOONLIT-BRIGHT (the cool bold rows: Amethyst, Indigo & Fire,
Aurora; sky_top ≈ (24–30,34–40,70–90), a lit indigo/teal dome where the ridgeline
reads crisp — held to the LOW end of the moonlit band because these rows' own
sunset tops are deep violet/indigo, so the night must stay clearly darker than the
sunset to still read as night), MID (the warm anchors Ember Gold, Amber Warm,
Rose-Gold, Coral Ember; ≈ (22–28,28–40,60–76)) and DEEP-but-cool (the deepest
rows: Deep Plum Ember, Cool Plum Gold, Blood Scarlet; ≈ (16–22,22–30,48–60), a
dark cool indigo cast, no warm ember). Each row keeps its own cool night flavour
(indigo / teal-navy / wine-but-cooled / mauve-navy / plum-indigo), just graded.
Each row's deep-night `sky_top` VALUE still reads clearly DARKER than that same
row's SUNSET so it is night, not a second sunset. This grade lives in the LOW
palette RGB on dusk/twilight/night/predawn (0.62/0.68/0.72/0.80), NOT in per-
design `SkyParams` — `zenith_dark` stays shared so the day is never darkened.

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through `tools/preview_sky_alpine_sunsets.py`. Pure-Pygame /
pygbag-safe (the keyframes are just colour tables; the OKLab bake lives in the
engine).
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# ── the shared frame (DAY frozen; sunset→night→sunrise authored per design) ───
# Phase clock matches the calm sets so the preview columns line up:
#   morning 0.06 · midday 0.18 · afternoon 0.30 · golden-onset 0.35 (INSERT) ·
#   golden 0.40 · sunset 0.50 · dusk 0.62 · twilight 0.68 · deep-night 0.72 ·
#   predawn 0.80 · dawn 0.88 · sunrise 0.94. `make_palette` wraps 0.94 -> 0.06 so
#   the night side is continuous.
#
# Only the three DAY frames (0.06/0.18/0.30) are SPINE — kept byte-for-byte on
# every variant; they are the loved cool glacial-cyan day and the identity
# anchor. Every other frame is VARY (golden 0.40, sunset 0.50, dusk 0.62,
# twilight 0.68, deep-night 0.72, predawn 0.80, dawn 0.88, sunrise 0.94), and
# designs may additionally INSERT dwell frames at 0.35 (golden-onset bridge that
# eases the cyan top into the warm gold) and 0.44/0.56/0.68 (sunset→night) and
# 0.86/0.90 (sunrise) to grade the slow travel. The spine's non-day frames below
# are only the fallback for rows that don't author them — every row authors its own.
_ALPINE_HAZE_KF = [
    (0.06, dict(sky_top=(86, 158, 186),  sky_mid=(150, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),   # SPINE morning  (FROZEN day)
    (0.18, dict(sky_top=(76, 168, 192),  sky_mid=(144, 198, 208), sky_bot=(196, 214, 212), horizon=(216, 220, 212), star_alpha=0)),   # SPINE midday   (FROZEN day)
    (0.30, dict(sky_top=(86, 160, 188),  sky_mid=(152, 192, 204), sky_bot=(198, 212, 208), horizon=(216, 218, 210), star_alpha=0)),   # SPINE afternoon(FROZEN day)
    (0.40, dict(sky_top=(88, 152, 178),  sky_mid=(156, 186, 196), sky_bot=(202, 208, 202), horizon=(220, 214, 204), star_alpha=0)),   # VARY golden
    (0.50, dict(sky_top=(74, 126, 160),  sky_mid=(146, 168, 184), sky_bot=(202, 200, 196), horizon=(230, 204, 184), star_alpha=12)),  # VARY sunset
    (0.62, dict(sky_top=(34, 76, 116),   sky_mid=(76, 126, 160),  sky_bot=(134, 172, 186), horizon=(190, 204, 200), star_alpha=80)),  # VARY dusk
    (0.68, dict(sky_top=(22, 52, 92),    sky_mid=(46, 96, 140),   sky_bot=(92, 150, 174),  horizon=(150, 188, 196), star_alpha=150)), # VARY twilight
    (0.72, dict(sky_top=(8, 28, 62),     sky_mid=(16, 64, 104),   sky_bot=(34, 104, 136),  horizon=(70, 144, 164),  star_alpha=210)), # VARY deep night
    (0.80, dict(sky_top=(12, 38, 78),    sky_mid=(26, 84, 124),   sky_bot=(54, 126, 156),  horizon=(108, 166, 186), star_alpha=130)), # VARY predawn
    (0.88, dict(sky_top=(76, 146, 176),  sky_mid=(140, 186, 200), sky_bot=(190, 210, 208), horizon=(214, 218, 210), star_alpha=20)),  # VARY dawn
    (0.94, dict(sky_top=(84, 156, 184),  sky_mid=(148, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),   # VARY sunrise
]

# Shared bake params for all rows — keeps the grade placement identical too.
# zenith_dark stays SHARED (0.14): night darkness lives in the LOW palette RGB
# on 0.62/0.68/0.72/0.80, never in per-design SkyParams (that would also darken
# the loved day).
_ALPINE_SKY = SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14)

# Fallback star_alpha for any INSERTED dwell frame a design doesn't author —
# interpolated from the slow-travel arc so star onset reads continuous:
#   golden-onset 0.35 (0, still day) → golden 0.40 (0) → sunset 0.50 (12) → 0.56
#   → dusk 0.62 (80) → twilight 0.68 (150) → night 0.72 (210).
_INSERT_STAR_ALPHA = {
    0.35: 0,    # golden-onset bridge — still full day, no stars yet
    0.44: 5,    # between golden 0.40 (0) and sunset 0.50 (12)
    0.56: 30,   # between sunset 0.50 (12) and dusk 0.62 (80)
    0.68: 150,  # twilight dwell — between dusk 0.62 (80) and night 0.72 (210)
    0.86: 48,   # between predawn 0.80 (130) and dawn 0.88 (20) -> closer to dawn
    0.90: 13,   # between dawn 0.88 (20) and sunrise 0.94 (0)
}

# Phases a design is ALLOWED to override. DAY (0.06/0.18/0.30) is the only spine;
# the whole golden-onset→sunset→night→sunrise arc is overridable so each row
# authors its own luminous golden onset and its own dark, cool, starry night.
_VARY_PHASES = {0.40, 0.50, 0.62, 0.68, 0.72, 0.80, 0.88, 0.94}
_INSERT_PHASES = {0.35, 0.44, 0.56, 0.68, 0.86, 0.90}


# ── night-balanced retiming (study) ──────────────────────────────────────────
# The cycle's keyframe phases were lopsided: a long day + a long evening descent,
# then only ~26 s of genuinely-dark night (the lone 0.72 anchor) before predawn
# 0.80 already lifted toward dawn. This remaps every frame's PHASE — colours are
# untouched — onto a timeline where the dark, starry night HOLDS about as long as
# the sunset arc, and inserts a flat repeat of the night frame so the sky sits
# dark instead of immediately climbing back. The new golden-onset 0.35 retimes to
# ~0.235 — between afternoon 0.30→0.20 and golden 0.40→0.27 — so the cyan→gold
# bridge sits in real time just before golden hour. Approx durations (×320 s):
#   day ~74 s · evening descent ~93 s · dark night hold ~96 s · dawn ~57 s.
# Applied in `_compose`, so all 11 rows shift identically; ported to the live
# game/biome keyframes only once a design is chosen.
_RETIME = [
    (0.06, 0.04), (0.18, 0.12), (0.30, 0.20),                                    # day (compressed)
    (0.35, 0.235), (0.40, 0.27), (0.50, 0.37), (0.62, 0.47), (0.68, 0.52), (0.72, 0.56),  # golden-onset bridge -> descent -> night
    (0.80, 0.86), (0.88, 0.92), (0.94, 0.97),                                    # predawn -> dawn -> sunrise
]
_NIGHT_HOLD_PHASE = 0.82   # flat repeat of the 0.72 night frame — holds the dark


def _retime(ph):
    """Piecewise-linear remap of an old keyframe phase onto the balanced timeline."""
    a = _RETIME
    if ph <= a[0][0]:
        return a[0][1]
    if ph >= a[-1][0]:
        (o0, n0), (o1, n1) = a[-2], a[-1]
        return n1 + (ph - o1) * (n1 - n0) / (o1 - o0)
    for (o0, n0), (o1, n1) in zip(a, a[1:]):
        if o0 <= ph <= o1:
            return n0 + (ph - o0) * (n1 - n0) / (o1 - o0)
    return ph



def _compose(overrides: dict) -> list:
    """Clone the frozen day + spine and apply a design's golden→sunset→night→sunrise.

    `overrides` maps phase -> dict(sky_top/mid/bot/horizon[, star_alpha]). For a
    VARY phase we replace the four RGB keys; an override MAY also carry its own
    `star_alpha` (so a design can make its night "full of stars" and time star
    emergence through dusk/twilight) — if absent we keep the spine's value. For
    an INSERT phase we add a new dwell frame; it likewise uses an authored
    `star_alpha` if given, else the interpolated `_INSERT_STAR_ALPHA` fallback.
    The three DAY anchors are never overridable and pass through verbatim —
    that is what guarantees the loved cool-cyan day is identical with zero
    hand-transcription."""
    by_phase = {ph: dict(d) for ph, d in _ALPINE_HAZE_KF}
    for ph, rgb in overrides.items():
        assert ph in _VARY_PHASES or ph in _INSERT_PHASES, f"phase {ph} is not overridable"
        frame = dict(rgb)
        if 'star_alpha' in rgb:
            # Design authored its own star alpha for this frame — honour it.
            frame['star_alpha'] = rgb['star_alpha']
        elif ph in by_phase:
            # VARY without an authored alpha: keep the spine's star_alpha.
            frame['star_alpha'] = by_phase[ph]['star_alpha']
        else:
            # INSERT without an authored alpha: interpolated fallback.
            frame['star_alpha'] = _INSERT_STAR_ALPHA[ph]
        by_phase[ph] = frame
    # Remap every frame onto the night-balanced timeline (colours unchanged) and
    # add the flat dark hold so the night sits dark rather than climbing at once.
    out = [(round(_retime(ph), 4), pal) for ph, pal in sorted(by_phase.items())]
    night = by_phase.get(0.72)
    if night is not None:
        out.append((_NIGHT_HOLD_PHASE, dict(night)))
    out.sort(key=lambda kv: kv[0])
    return out


def _spec(name, note, overrides):
    return BiomeSpec(name=name, note=note, keyframes=_compose(overrides), sky=_ALPINE_SKY)


# ── the 10 evening moods (frozen cool-cyan day under every one) ───────────────
# The set is weighted toward the loved Ember Gold anchor: ~6 EMBER-GOLD-FAMILY
# evolutions (rows 1–6, all warm gold→orange→plum relatives, each a restrained
# distinct move) + ~4 BOLD departures (rows 7–10, free to travel further).
#
# Authoring discipline shared by all rows (v4):
#   * DAY (0.06/0.18/0.30): the untouched cool glacial-cyan day — frozen,
#     byte-for-byte identical across every row. Never warmed, never darkened.
#   * GOLDEN ONSET (0.35 INSERT → golden 0.40): leaving the bright frozen
#     afternoon, the 0.35 bridge eases the cyan top into a LUMINOUS warm gold in
#     both value and hue — routed through a warm-cyan / pale-gold, NEVER a dark /
#     grey / blue dip. Golden 0.40 is BRIGHT and warm (pale gold / warm-peach top,
#     clearly lighter than the live muted brown), with the warm low-band entry
#     (orange horizon + warm sky_bot) the user liked. Golden hour scatters blue
#     OUT, so the zenith stays warm-pale, never cyan.
#   * SUNSET (golden 0.40 → sunset 0.50, with 0.44/0.56 dwell): the top's descent
#     into the deep-violet sunset is GRADUAL across 0.40→0.44→0.50→0.56 — golden
#     stays bright/warm, only by sunset/dwell does the top reach deep violet. The
#     anchor rows TRAVEL gold→orange→plum over time; the bold rows may travel
#     further (jewel-rose→violet, flame→indigo, tangerine→teal, scarlet→oxblood).
#     The gold↔purple handoff is ALWAYS bridged by a saturated coral/rose MID so
#     no vertical sample greys to taupe.
#   * DUSK → TWILIGHT → NIGHT (0.62 / 0.68 / 0.72, then predawn 0.80): a DESIGNED
#     slow darken AND a GRADUAL cool-down of the BOTTOM band — a warm ember may
#     persist at the horizon through dusk 0.62, FADES at twilight 0.68, and is
#     fully resolved to DARK + COOL by deep-night 0.72 (no orange ember at the
#     deepest point; 0.80 holds that dark). The TOP keeps the "dark but never
#     black" lifted-indigo floor (min ~(14,16,40), graded MOONLIT→MID→DEEP), so
#     the dome reads a cool dark indigo TOP and a dark cool BOTTOM — an iris-dark
#     dome, never a void, never a second sunset. star_alpha rises monotonically
#     and stars EMERGE through twilight (~80 dusk → ~150 twilight → deep night);
#     on the lit MOONLIT rows it is lowered at deep night (~170-185) so the field
#     stays crisp without washing out. Each row's deep-night sky_top VALUE is
#     clearly DARKER than that same row's SUNSET sky_top.
#   * SUNRISE (dawn 0.88 / sunrise 0.94): RICH, never pale, and a genuinely
#     DIFFERENT moment from that row's sunset (a clearer, fresher hue family).


# ── 6 EMBER-GOLD-FAMILY anchors (warm gold→orange→plum over time) ────────────

# 1. Ember Gold (brighter-gold) — the loved anchor, re-graded. [NIGHT TIER: MID]
#    The whole-sky hue TRAVELS over time: a luminous molten GOLD at golden hour →
#    burnt-orange + coral-red by sunset → plum-violet by the 0.56 dwell, then falls
#    to a dark COOL indigo night (the warm ember fades out by deep night). Sunrise:
#    a rich warm amber-rose dawn.
EMBER_GOLD = _spec(
    'Ember Gold',
    'ANCHOR [brighter-gold]: the loved Ember Gold, re-graded. GOLDEN ONSET: the cyan afternoon top eases (0.35) into a LUMINOUS pale-gold zenith — golden 0.40 reads bright molten GOLD, not the old muted brown. SUNSET travels gold→burnt-orange+coral→plum-violet, the top sinking to deep violet only by the 0.56 dwell. NIGHT: a DARK COOL indigo dome top AND a dark cool bottom — the warm horizon ember persists through dusk, fades by twilight, fully cool by deep night (no orange ember), star_alpha peaks ~224. SUNRISE: a rich warm amber-rose dawn.',
    {
        # GOLDEN ONSET — 0.35 bridges the frozen cyan afternoon top (86,160,188)
        # into golden's warm pale-gold via a warm-cyan / pale-gold (top stays
        # bright, only warms; the low band brings the warm horizon in early). 0.40
        # is now a LUMINOUS pale-gold zenith (not the live (124,96,70) brown), so
        # the descent into deep violet across 0.40→0.44→0.50→0.56 is gradual.
        0.35: dict(sky_top=(132, 157, 162), sky_mid=(214, 204, 180), sky_bot=(246, 214, 168), horizon=(255, 196, 120)),
        0.40: dict(sky_top=(168, 157, 137), sky_mid=(248, 198, 132), sky_bot=(255, 196, 96),  horizon=(255, 158, 56)),
        0.44: dict(sky_top=(168, 140, 150), sky_mid=(244, 168, 104), sky_bot=(255, 178, 70),  horizon=(252, 124, 44)),
        0.50: dict(sky_top=(110, 78, 132),  sky_mid=(234, 116, 96),  sky_bot=(252, 140, 56),  horizon=(238, 92, 34)),
        0.56: dict(sky_top=(82, 46, 124),   sky_mid=(212, 78, 116),  sky_bot=(232, 96, 72),   horizon=(220, 70, 50)),
        # DUSK→TWILIGHT→NIGHT [MID] — slow darken; the warm horizon ember holds
        # through dusk 0.62, FADES at twilight 0.68, fully cool by deep-night 0.72
        # (horizon/sky_bot taken DOWN to a dark cool indigo — no orange ember). The
        # top keeps its lifted indigo floor (deep-night sky_top (26,32,66)). 0.80
        # holds the dark.
        0.62: dict(sky_top=(35, 31, 73),   sky_mid=(104, 63, 84),   sky_bot=(146, 87, 68),   horizon=(176, 84, 45),  star_alpha=88),
        0.68: dict(sky_top=(28, 31, 68),   sky_mid=(57, 45, 75),    sky_bot=(84, 61, 75),    horizon=(110, 70, 68),   star_alpha=156),
        0.72: dict(sky_top=(23, 28, 57),   sky_mid=(31, 35, 61),    sky_bot=(42, 45, 68),    horizon=(56, 56, 75),    star_alpha=224),
        0.80: dict(sky_top=(24, 30, 59),   sky_mid=(33, 37, 63),    sky_bot=(44, 47, 70),    horizon=(59, 59, 78),    star_alpha=168),
        # SUNRISE — rich warm amber-rose; clearer/fresher than the dusk fire.
        0.88: dict(sky_top=(72, 110, 150), sky_mid=(220, 158, 134), sky_bot=(255, 178, 132), horizon=(255, 168, 110)),
        0.94: dict(sky_top=(82, 138, 172), sky_mid=(228, 178, 158), sky_bot=(255, 192, 150), horizon=(255, 182, 132)),
    },
)


# 2. Amber Warm — ANCHOR [amber-warm]. [NIGHT TIER: MID] Ember Gold pulled toward a
#    deeper AMBER-honey gold: golden reads warm amber → amber-orange by sunset →
#    warm-plum by the dwell, then a dark cool indigo night (amber ember fades out).
#    Sunrise: a warm honey-peach dawn.
AMBER_WARM = _spec(
    'Amber Warm',
    'ANCHOR [amber-warm]: Ember Gold deepened to a honey AMBER. GOLDEN ONSET eases the cyan top into a luminous warm amber zenith (0.40 bright amber-gold, never brown). SUNSET travels amber→amber-orange→warm-plum, the top reaching deep violet only by the 0.56 dwell. NIGHT: a dark cool indigo dome — the amber horizon ember persists through dusk, fades by twilight, fully cool by deep night, star_alpha peaks ~222. SUNRISE: a warm honey-peach dawn.',
    {
        # GOLDEN ONSET — same cyan→warm easing, but the warm end is a deeper HONEY
        # AMBER, pushed CLEARLY redder/deeper than Ember Gold's neutral pale gold so
        # the two separate at a glance in motion: the golden 0.40 horizon drives to a
        # deep amber-orange (~255,128,32) and the mid is a richer honey-amber (less
        # yellow). Still luminous at 0.40, gradual descent after.
        0.35: dict(sky_top=(138, 154, 154), sky_mid=(222, 192, 150), sky_bot=(252, 194, 124), horizon=(255, 166, 84)),
        0.40: dict(sky_top=(178, 154, 126), sky_mid=(250, 174, 92),  sky_bot=(255, 162, 60),  horizon=(255, 128, 32)),
        0.44: dict(sky_top=(166, 124, 130), sky_mid=(246, 144, 74),  sky_bot=(255, 146, 48),  horizon=(248, 100, 28)),
        # SUNSET mid is ORANGE-AMBER (warm tangerine), not coral — keeps Amber Warm
        # in the honey/amber family vs Ember Gold's brighter neutral fire.
        0.50: dict(sky_top=(106, 68, 116),  sky_mid=(240, 124, 56),  sky_bot=(250, 118, 40),  horizon=(232, 78, 28)),
        0.56: dict(sky_top=(78, 42, 112),   sky_mid=(216, 92, 70),   sky_bot=(228, 84, 52),   horizon=(214, 64, 38)),
        # DUSK→TWILIGHT→NIGHT [MID] — amber ember holds through dusk, fades at
        # twilight, dark+cool by deep night (horizon/bot cooled to indigo). Top
        # lifted floor (26,32,64). A touch warmer-amber than Ember Gold at dusk so
        # the two stay distinct, but the deep-night bottom is fully cool either way.
        0.62: dict(sky_top=(35, 30, 70),   sky_mid=(110, 61, 75),   sky_bot=(155, 87, 56),   horizon=(179, 80, 38),  star_alpha=88),
        0.68: dict(sky_top=(28, 30, 64),   sky_mid=(61, 44, 68),    sky_bot=(90, 59, 66),    horizon=(120, 70, 57),   star_alpha=156),
        0.72: dict(sky_top=(23, 28, 56),   sky_mid=(33, 35, 59),    sky_bot=(44, 45, 66),    horizon=(59, 57, 73),    star_alpha=222),
        0.80: dict(sky_top=(24, 30, 57),   sky_mid=(35, 37, 61),    sky_bot=(45, 47, 68),    horizon=(63, 61, 77),    star_alpha=166),
        # SUNRISE — warm honey-peach; fresher than the amber dusk.
        0.88: dict(sky_top=(74, 116, 152), sky_mid=(224, 162, 130), sky_bot=(255, 182, 128), horizon=(255, 164, 100)),
        0.94: dict(sky_top=(84, 140, 174), sky_mid=(232, 182, 154), sky_bot=(255, 194, 146), horizon=(255, 178, 124)),
    },
)


# 3. Rose-Gold Glow — ANCHOR [rose-gold-warm]. [NIGHT TIER: MID] Ember Gold warmed
#    toward ROSE-GOLD: golden reads pink-kissed gold → rose-coral by sunset →
#    rose-plum by the dwell, then a dark cool mauve-indigo night. Sunrise: a soft
#    blush-gold dawn.
ROSE_GOLD_GLOW = _spec(
    'Rose-Gold Glow',
    'ANCHOR [rose-gold-warm]: Ember Gold warmed with a pink kiss. GOLDEN ONSET eases the cyan top into a luminous rose-gold zenith (0.40 bright pink-gold). SUNSET travels rose-gold→rose-coral→rose-plum, the top deepening to violet only by the dwell. NIGHT: a dark cool mauve-indigo dome — the rose horizon glow persists through dusk, fades by twilight, fully cool by deep night, star_alpha peaks ~222. SUNRISE: a soft blush-gold dawn.',
    {
        # GOLDEN ONSET — the warm end carries a clear PINK kiss in the gold (rose-
        # gold), the mid pulled toward warm rose so the zenith reads rose-gold, not
        # plain gold. Luminous at 0.40, gradual descent.
        0.35: dict(sky_top=(142, 154, 158), sky_mid=(226, 192, 178), sky_bot=(252, 198, 160), horizon=(255, 176, 120)),
        0.40: dict(sky_top=(180, 153, 143), sky_mid=(252, 186, 142), sky_bot=(255, 176, 104), horizon=(255, 142, 72)),
        0.44: dict(sky_top=(172, 128, 146), sky_mid=(248, 158, 124), sky_bot=(255, 158, 84),  horizon=(250, 116, 58)),
        0.50: dict(sky_top=(112, 70, 124),  sky_mid=(238, 112, 110), sky_bot=(252, 130, 72),  horizon=(238, 92, 56)),
        0.56: dict(sky_top=(84, 44, 118),   sky_mid=(216, 82, 124),  sky_bot=(232, 96, 88),   horizon=(220, 76, 70)),
        # DUSK→TWILIGHT→NIGHT [MID] — rose horizon glow holds through dusk, fades
        # at twilight, dark+cool by deep night into a MAUVE-indigo (a touch more
        # blue-violet than Ember Gold so the rose-family flavour survives the cool-
        # down). Top lifted floor (26,32,68). No warm ember at the deepest point.
        0.62: dict(sky_top=(37, 31, 73),   sky_mid=(115, 61, 84),   sky_bot=(160, 85, 78),   horizon=(183, 80, 63),  star_alpha=88),
        0.68: dict(sky_top=(28, 31, 68),   sky_mid=(64, 44, 73),    sky_bot=(94, 59, 75),    horizon=(122, 70, 71),   star_alpha=156),
        0.72: dict(sky_top=(23, 28, 59),   sky_mid=(33, 35, 63),    sky_bot=(44, 45, 70),    horizon=(57, 56, 77),    star_alpha=222),
        0.80: dict(sky_top=(24, 30, 61),   sky_mid=(35, 37, 64),    sky_bot=(45, 47, 71),    horizon=(61, 59, 80),    star_alpha=166),
        # SUNRISE — soft blush-gold; the rose reborn lighter than the dusk.
        0.88: dict(sky_top=(76, 124, 158), sky_mid=(232, 164, 154), sky_bot=(255, 182, 148), horizon=(255, 162, 116)),
        0.94: dict(sky_top=(86, 146, 178), sky_mid=(240, 182, 174), sky_bot=(255, 194, 162), horizon=(255, 176, 138)),
    },
)


# 4. Coral Ember — ANCHOR [coral-warm]. [NIGHT TIER: MID] Ember Gold pulled toward
#    a warm CORAL reef glow: golden reads gold-coral → deep coral-red by sunset →
#    coral-plum by the dwell, then a dark cool plum-indigo night. Sunrise: a fresh
#    coral-cream dawn.
CORAL_EMBER = _spec(
    'Coral Ember',
    'ANCHOR [coral-warm]: Ember Gold pulled toward a warm coral reef glow. GOLDEN ONSET eases the cyan top into a luminous coral-gold zenith (0.40 bright gold-coral). SUNSET travels gold-coral→deep coral-red→coral-plum, the top deepening to violet only by the dwell. NIGHT: a dark cool plum-indigo dome — the coral horizon ember persists through dusk, fades by twilight, fully cool by deep night, star_alpha peaks ~222. SUNRISE: a fresh coral-cream dawn.',
    {
        # GOLDEN ONSET — the warm end is a hotter CORAL than Ember Gold's gold (the
        # horizon redder, the mid salmon-coral), but the zenith still eases off cyan
        # luminously at 0.40 before the gradual descent. Coral keeps real chroma.
        0.35: dict(sky_top=(141, 153, 157), sky_mid=(232, 188, 166), sky_bot=(255, 186, 144), horizon=(255, 164, 104)),
        0.40: dict(sky_top=(181, 150, 139), sky_mid=(254, 168, 126), sky_bot=(255, 158, 96),  horizon=(255, 122, 60)),
        0.44: dict(sky_top=(168, 122, 140), sky_mid=(250, 138, 100), sky_bot=(255, 138, 72),  horizon=(252, 96, 48)),
        # 0.50 coral-red nudged a hair HOTTER/oranger (more red+orange in the mid)
        # so the "reef" identity holds clear of Rose-Gold Glow's pinker coral.
        0.50: dict(sky_top=(108, 66, 116),  sky_mid=(244, 96, 80),   sky_bot=(252, 116, 60),  horizon=(246, 76, 44)),
        0.56: dict(sky_top=(80, 42, 112),   sky_mid=(222, 74, 98),   sky_bot=(232, 86, 70),   horizon=(226, 64, 54)),
        # DUSK→TWILIGHT→NIGHT [MID] — coral ember holds through dusk, fades at
        # twilight, dark+cool by deep night into a PLUM-indigo. Top lifted floor
        # (26,32,66). No orange/coral ember at the deepest point — bottom fully cool.
        0.62: dict(sky_top=(37, 30, 70),   sky_mid=(118, 59, 80),   sky_bot=(167, 84, 68),   horizon=(188, 78, 52),  star_alpha=88),
        0.68: dict(sky_top=(28, 30, 64),   sky_mid=(68, 42, 68),    sky_bot=(99, 57, 66),    horizon=(127, 68, 61),   star_alpha=156),
        0.72: dict(sky_top=(23, 28, 57),   sky_mid=(33, 35, 61),    sky_bot=(44, 45, 68),    horizon=(57, 56, 75),    star_alpha=222),
        0.80: dict(sky_top=(24, 30, 59),   sky_mid=(35, 37, 63),    sky_bot=(45, 47, 70),    horizon=(61, 59, 78),    star_alpha=166),
        # SUNRISE — fresh coral-cream; the reef glow reborn clear and lighter.
        0.88: dict(sky_top=(76, 124, 158), sky_mid=(244, 160, 144), sky_bot=(255, 178, 150), horizon=(255, 158, 120)),
        0.94: dict(sky_top=(86, 146, 176), sky_mid=(248, 180, 166), sky_bot=(255, 190, 164), horizon=(255, 170, 140)),
    },
)


# 5. Deep Plum Ember — ANCHOR [deeper-plum]. [NIGHT TIER: DEEP-BUT-COOL] Ember Gold
#    with a RICHER, EARLIER plum: golden still reads warm gold, but the violet floods
#    the top harder and earlier so the sunset is the most plum-saturated of the
#    anchors, then it falls to the deepest cool indigo of the warm family. Sunrise: a
#    warm plum-peach dawn.
DEEP_PLUM_EMBER = _spec(
    'Deep Plum Ember',
    'ANCHOR [deeper-plum]: Ember Gold with a richer, earlier plum top. GOLDEN ONSET still eases the cyan top into a luminous warm gold (0.40 bright), but the violet floods the top harder so the sunset is the most plum-saturated of the anchors. NIGHT: the deepest cool indigo of the warm family (DEEP tier) — the gold ember persists through dusk, fades by twilight, fully cool+dark by deep night, star_alpha peaks ~230. SUNRISE: a warm plum-peach dawn.',
    {
        # GOLDEN ONSET — identical luminous cyan→gold ease at 0.35/0.40 (the warm
        # entry the user liked is shared), but from 0.44 on the violet pushes into
        # the top EARLIER and DEEPER than Ember Gold, so the plum sunset is richer —
        # the differentiator. Still gradual (golden bright), just a steeper plum arc.
        0.35: dict(sky_top=(134, 157, 164), sky_mid=(214, 204, 180), sky_bot=(246, 214, 168), horizon=(255, 196, 120)),
        0.40: dict(sky_top=(171, 159, 139), sky_mid=(248, 196, 130), sky_bot=(255, 194, 94),  horizon=(255, 154, 54)),
        0.44: dict(sky_top=(146, 110, 150), sky_mid=(242, 156, 102), sky_bot=(255, 172, 66),  horizon=(250, 116, 42)),
        0.50: dict(sky_top=(96, 56, 138),   sky_mid=(228, 100, 104), sky_bot=(250, 132, 54),  horizon=(236, 84, 32)),
        0.56: dict(sky_top=(72, 38, 134),   sky_mid=(202, 70, 124),  sky_bot=(228, 88, 72),   horizon=(214, 64, 50)),
        # DUSK→TWILIGHT→NIGHT [DEEP-BUT-COOL] — the WARMER deep-plum twin (vs Cool
        # Plum Gold's slate-BLUE floor): the deep night is a warmer-VIOLET dome where
        # RED leads BLUE so it reads plum-warm, not slate. The gold ember holds
        # through dusk, fades at twilight, and the deep-night top sinks to a lifted-
        # but-low warm-violet (26,22,54) — still dark+cool (no warm horizon ember),
        # but the two deep-plum NIGHTS now differ in HUE, not a 2-point RGB delta.
        0.62: dict(sky_top=(37, 26, 56),   sky_mid=(108, 52, 75),   sky_bot=(148, 77, 63),   horizon=(177, 75, 42),  star_alpha=90),
        0.68: dict(sky_top=(30, 24, 50),   sky_mid=(61, 37, 61),    sky_bot=(85, 49, 63),    horizon=(110, 59, 59),   star_alpha=158),
        0.72: dict(sky_top=(23, 19, 47),   sky_mid=(33, 26, 49),    sky_bot=(42, 35, 56),    horizon=(56, 45, 64),    star_alpha=230),
        0.80: dict(sky_top=(24, 21, 49),   sky_mid=(35, 28, 50),    sky_bot=(44, 37, 57),    horizon=(59, 49, 68),    star_alpha=170),
        # SUNRISE — warm plum-peach; the plum reborn fresh over a peach horizon.
        0.88: dict(sky_top=(74, 118, 156), sky_mid=(206, 156, 162), sky_bot=(252, 174, 146), horizon=(255, 160, 116)),
        0.94: dict(sky_top=(84, 142, 176), sky_mid=(214, 176, 180), sky_bot=(255, 186, 160), horizon=(255, 172, 138)),
    },
)


# 6. Cool Plum Gold — ANCHOR [cooler-plum-leaning gold]. [NIGHT TIER: DEEP-BUT-COOL]
#    The COOLEST of the warm family: golden reads a cooler, lemon-leaning gold, the
#    sunset tips a blue-violet plum (cooler than Deep Plum Ember's warm plum), then a
#    deep cool slate-indigo night. Sunrise: a cool gold-and-rose dawn.
COOL_PLUM_GOLD = _spec(
    'Cool Plum Gold',
    'ANCHOR [cooler-plum-leaning gold]: the coolest of the warm family. GOLDEN ONSET eases the cyan top into a luminous COOL lemon-gold zenith (0.40 bright, a hair cooler than Ember Gold). SUNSET travels cool-gold→amber→a BLUE-VIOLET plum (cooler than Deep Plum Ember). NIGHT: a deep cool slate-indigo dome (DEEP tier) — the gold ember persists through dusk, fades by twilight, fully cool by deep night, star_alpha peaks ~228. SUNRISE: a cool gold-and-rose dawn.',
    {
        # GOLDEN ONSET — COMMITTED cool identity (vs Deep Plum Ember's warm twin):
        # the warm end is a genuinely GREEN-LEMON gold (green nudged up, red pulled
        # back) so the zenith reads a cool-leaning gold, not the warm gold of the
        # others. The 0.35 ease keeps the cyan→gold path clean; 0.40 still luminous.
        # The plum it travels to is a genuine BLUE-violet (blue added in the tops).
        0.35: dict(sky_top=(128, 161, 168), sky_mid=(204, 210, 184), sky_bot=(234, 220, 168), horizon=(244, 204, 126)),
        0.40: dict(sky_top=(158, 168, 142), sky_mid=(228, 210, 134), sky_bot=(244, 206, 98),  horizon=(246, 170, 66)),
        # 0.44 lifted off the dull warm-grey-mauve onto a cleaner COOL LILAC (it was
        # the dullest single cell in the set) — more blue, less red/green muddiness.
        0.44: dict(sky_top=(146, 144, 178), sky_mid=(224, 174, 118), sky_bot=(244, 182, 78),  horizon=(238, 130, 54)),
        # SUNSET plum is genuinely BLUE-VIOLET — blue pushed clearly above red in the
        # 0.50/0.56 tops so it reads cool against Deep Plum Ember's warm plum.
        0.50: dict(sky_top=(82, 64, 156),   sky_mid=(200, 110, 124), sky_bot=(238, 138, 64),  horizon=(228, 96, 46)),
        0.56: dict(sky_top=(58, 46, 150),   sky_mid=(168, 80, 146),  sky_bot=(214, 100, 92),  horizon=(204, 80, 64)),
        # DUSK→TWILIGHT→NIGHT [DEEP-BUT-COOL] — a true SLATE-BLUE floor: blue clearly
        # dominant over the violet-warm twin's red, the lemon-gold ember holding
        # through dusk then fading to a dark cool slate-blue by deep night (top
        # (16,24,62), blue dominant, bottom fully cool, no warm ember). The coolest,
        # bluest deep night of the warm family — distinct in HUE from Deep Plum's
        # warmer-violet floor, not by a 2-point RGB delta.
        0.62: dict(sky_top=(26, 28, 73),   sky_mid=(82, 54, 97),    sky_bot=(127, 77, 84),   horizon=(160, 77, 56),  star_alpha=90),
        0.68: dict(sky_top=(21, 26, 68),   sky_mid=(42, 40, 84),    sky_bot=(66, 52, 82),    horizon=(90, 63, 75),    star_alpha=158),
        0.72: dict(sky_top=(14, 21, 54),   sky_mid=(21, 28, 61),    sky_bot=(28, 37, 70),    horizon=(38, 47, 80),    star_alpha=228),
        0.80: dict(sky_top=(16, 23, 56),   sky_mid=(23, 30, 63),    sky_bot=(30, 38, 71),    horizon=(42, 50, 84),    star_alpha=168),
        # SUNRISE — cool lemon-gold over a soft rose horizon; cooler/fresher than
        # the dusk and a touch cooler in the mid than the warm-twin's peach dawn.
        0.88: dict(sky_top=(80, 134, 166), sky_mid=(206, 174, 168), sky_bot=(244, 190, 148), horizon=(252, 174, 120)),
        0.94: dict(sky_top=(90, 152, 182), sky_mid=(214, 190, 186), sky_bot=(250, 200, 162), horizon=(254, 184, 138)),
    },
)


# ── 4 BOLD departures (free to travel further from the warm anchor) ──────────

# 7. Amethyst Nightfall — BOLD [jewel / amethyst]. [NIGHT TIER: MOONLIT-BRIGHT] At
#    golden the warm onset blooms into a jewel sky — rose horizon → magenta mid →
#    amethyst-VIOLET top — that BOTH darkens AND climbs over time (the rose recedes,
#    the violet floods down), then falls to a lit moonlit-blue indigo night.
#    Sunrise: a rich rose-violet dawn.
AMETHYST_NIGHTFALL = _spec(
    'Amethyst Nightfall',
    'BOLD [jewel / amethyst]: the warm golden onset blooms into a banded jewel sky — rose H338 horizon → magenta mid → amethyst-VIOLET top — whose bands ALSO migrate (the rose recedes, the violet floods down). GOLDEN ONSET still eases the cyan top in luminous (0.35→0.40 warm-rose-gold) before the jewels arrive, so it is not a snap-to-violet. NIGHT: a LIT moonlit-blue indigo dome (the ridgeline reads crisp), star_alpha peaks ~185, bottom dark+cool. SUNRISE: a rich rose-violet dawn.',
    {
        # GOLDEN ONSET — even the bold rows obey FIX 1: 0.35/0.40 ease the cyan top
        # into a LUMINOUS warm rose-gold (bright, warm, not a dark violet snap),
        # then the jewel bands bloom across 0.44→0.50→0.56 as the rose recedes and
        # the amethyst-violet floods down — banded at every step yet travelling.
        0.35: dict(sky_top=(135, 145, 152), sky_mid=(228, 188, 184), sky_bot=(252, 188, 170), horizon=(255, 168, 132)),
        0.40: dict(sky_top=(158, 137, 156), sky_mid=(238, 150, 168), sky_bot=(252, 142, 150), horizon=(255, 130, 116)),
        0.44: dict(sky_top=(122, 84, 162),  sky_mid=(204, 96, 176),  sky_bot=(234, 96, 150),  horizon=(248, 96, 124)),
        0.50: dict(sky_top=(66, 46, 124),   sky_mid=(150, 64, 176),  sky_bot=(196, 60, 154),  horizon=(234, 64, 124)),
        0.56: dict(sky_top=(50, 36, 100),   sky_mid=(122, 54, 158),  sky_bot=(166, 56, 140),  horizon=(212, 54, 124)),
        # DUSK→TWILIGHT→NIGHT [MOONLIT-BRIGHT] — a true moonlit-BLUE indigo dome:
        # the deep-night sky_top is lifted to (30,40,90) so the ridgeline reads
        # crisply against a lit indigo sky, but held to the LOW end of the moonlit
        # band so its VALUE stays clearly DARKER than this row's deep-violet sunset
        # top (54,38,106) — night, not a second sunset. The magenta horizon glow
        # fades through twilight; by deep night the bottom is a cool indigo (no warm
        # ember). star_alpha (185) keeps cores crisp on the lit dome.
        0.62: dict(sky_top=(31, 37, 90),   sky_mid=(61, 45, 131),   sky_bot=(96, 52, 136),   horizon=(150, 50, 115),  star_alpha=82),
        0.68: dict(sky_top=(28, 35, 84),   sky_mid=(42, 40, 103),   sky_bot=(61, 49, 108),   horizon=(90, 54, 106),    star_alpha=132),
        0.72: dict(sky_top=(26, 35, 78),   sky_mid=(35, 38, 84),    sky_bot=(44, 45, 89),    horizon=(56, 52, 94),     star_alpha=185),
        0.80: dict(sky_top=(27, 36, 79),   sky_mid=(37, 40, 85),    sky_bot=(45, 47, 90),    horizon=(57, 54, 96),     star_alpha=120),
        # SUNRISE — rich rose-violet reborn; fresher, lighter, clearly distinct.
        0.88: dict(sky_top=(78, 132, 168), sky_mid=(190, 158, 210), sky_bot=(228, 168, 204), horizon=(248, 158, 184)),
        0.94: dict(sky_top=(86, 148, 178), sky_mid=(200, 178, 216), sky_bot=(234, 182, 210), horizon=(250, 172, 192)),
    },
)


# 8. Indigo & Fire — BOLD [indigo & fire]. [NIGHT TIER: MOONLIT-BRIGHT] The high-
#    contrast jewel: a fiery magenta-red horizon → hot purple-magenta mid → DEEP
#    INDIGO top, banded AND migrating (the flame recedes, the indigo floods down),
#    then a lit moonlit indigo night. Sunrise: a cool steel-blue & gold dawn.
INDIGO_FIRE = _spec(
    'Indigo & Fire',
    'BOLD [indigo & fire]: the high-contrast jewel — a magenta-RED H348 horizon, a hot purple-magenta mid bridge, a DEEP INDIGO H250 top, banded AND migrating (the flame recedes, the indigo floods down). GOLDEN ONSET still eases the cyan top in luminous (0.35→0.40 warm-coral-gold) so the indigo arrives gradually, not as a snap. NIGHT: a near-black-but-LIT moonlit indigo, star_alpha peaks ~170, bottom dark+cool. SUNRISE: a cool steel-blue and gold dawn.',
    {
        # GOLDEN ONSET — FIX 1 even here: 0.35/0.40 are a LUMINOUS warm coral-gold,
        # NOT an immediate indigo. The flame+indigo banding blooms across
        # 0.44→0.50→0.56 as the deep indigo floods down. To preserve the "fire", a
        # hotter MAGENTA-RED band is HELD one column lower — the 0.50 mid stays a hot
        # magenta-red (was a muddy purple-magenta where it met the indigo top) so the
        # flame punch survives until the indigo floods the mid at 0.56.
        0.35: dict(sky_top=(134, 144, 153), sky_mid=(226, 184, 176), sky_bot=(252, 178, 152), horizon=(255, 152, 110)),
        0.40: dict(sky_top=(155, 131, 163), sky_mid=(232, 140, 158), sky_bot=(248, 128, 136), horizon=(255, 116, 100)),
        0.44: dict(sky_top=(96, 72, 158),   sky_mid=(208, 72, 144),  sky_bot=(228, 70, 130),  horizon=(244, 80, 108)),
        0.50: dict(sky_top=(44, 38, 124),   sky_mid=(196, 56, 116),  sky_bot=(214, 54, 112),  horizon=(228, 56, 92)),
        0.56: dict(sky_top=(36, 30, 104),   sky_mid=(96, 44, 150),   sky_bot=(160, 48, 122),  horizon=(212, 52, 98)),
        # DUSK→TWILIGHT→NIGHT [MOONLIT-BRIGHT, DEEPER END] — a deep but clearly-LIT
        # indigo dome held to the DEEP end of the moonlit band (deep-night sky_top
        # (22,30,74), blue dominant) so the silhouette reads against a moonlit
        # indigo. The magenta flame fades through twilight; by deep night the bottom
        # is a cool indigo (no warm ember). Night sky_top VALUE stays clearly DARKER
        # than this row's already-dark deep-indigo sunset top (38,32,110).
        0.62: dict(sky_top=(28, 33, 85),   sky_mid=(50, 38, 104),   sky_bot=(101, 49, 101),  horizon=(167, 57, 87),  star_alpha=86),
        0.68: dict(sky_top=(24, 31, 77),   sky_mid=(38, 37, 90),    sky_bot=(64, 45, 90),    horizon=(104, 54, 87),   star_alpha=140),
        0.72: dict(sky_top=(19, 26, 64),   sky_mid=(30, 35, 77),    sky_bot=(40, 42, 78),    horizon=(56, 49, 80),    star_alpha=170),
        0.80: dict(sky_top=(20, 27, 64),   sky_mid=(31, 37, 78),    sky_bot=(42, 44, 80),    horizon=(57, 50, 82),    star_alpha=126),
        # SUNRISE — cool fresh steel-blue mid lifting to a thin gold horizon.
        0.88: dict(sky_top=(78, 142, 178), sky_mid=(160, 192, 216), sky_bot=(206, 204, 204), horizon=(252, 196, 138)),
        0.94: dict(sky_top=(86, 152, 184), sky_mid=(162, 196, 216), sky_bot=(212, 208, 206), horizon=(255, 202, 152)),
    },
)


# 9. Aurora Teal-Magenta — BOLD [aurora teal↔magenta]. [NIGHT TIER: MOONLIT-BRIGHT]
#    A banded aurora — tangerine-coral horizon → magenta-rose mid → indigo top with
#    a teal sliver — whose bands migrate (the warm end cools, the teal re-enters at
#    twilight), then a lit moonlit teal-navy night with one signature low teal glow.
#    Sunrise: a fresh cyan-peach dawn.
AURORA_TEAL_MAGENTA = _spec(
    'Aurora Teal-Magenta',
    'BOLD [aurora teal↔magenta]: a banded aurora — TANGERINE-coral H14 horizon, warm magenta-rose mid, indigo top, a thin TEAL sliver at the edge — whose bands migrate (the warm end cools upward, the teal re-blooms as the TWILIGHT accent). GOLDEN ONSET still eases the cyan top in luminous (0.35→0.40 warm-coral-gold) before the aurora. NIGHT: a LIT moonlit teal-navy with one signature low teal-green glow, star_alpha peaks ~185, bottom dark+cool. SUNRISE: a fresh cyan-and-peach dawn.',
    {
        # GOLDEN ONSET — FIX 1: 0.35/0.40 LUMINOUS warm coral-gold (not a cyan-blue
        # twilight). The aurora bands bloom across 0.44→0.50→0.56 — tangerine
        # horizon, magenta-rose mid, indigo top. The TEAL edge is now brought in
        # EARLIER and WIDER (a teal-green cast in the sky_top at 0.50/0.56, where it
        # used to stay pure indigo) so the aurora identity reads as teal↔magenta
        # BEFORE twilight, not only at it — magenta below, teal-green above.
        0.35: dict(sky_top=(135, 145, 154), sky_mid=(228, 186, 174), sky_bot=(252, 180, 150), horizon=(255, 154, 104)),
        0.40: dict(sky_top=(150, 137, 155), sky_mid=(238, 146, 158), sky_bot=(252, 138, 122), horizon=(255, 124, 78)),
        0.44: dict(sky_top=(80, 92, 148),   sky_mid=(228, 108, 158), sky_bot=(248, 102, 110), horizon=(255, 102, 70)),
        0.50: dict(sky_top=(38, 86, 124),   sky_mid=(216, 80, 150),  sky_bot=(248, 80, 96),   horizon=(250, 82, 58)),
        0.56: dict(sky_top=(30, 76, 108),   sky_mid=(190, 66, 140),  sky_bot=(228, 66, 96),   horizon=(226, 66, 62)),
        # DUSK→TWILIGHT→NIGHT [MOONLIT-BRIGHT, COOLER] — a lit TEAL-NAVY dome held
        # to the DEEP end of the moonlit band (deep-night sky_top (24,34,70), blue
        # dominant with green nudged over the pure-indigo bold rows). The magenta
        # cools out, TEAL re-enters as the unmistakable twilight (0.68) accent, and
        # the night keeps ONE signature low cool teal-green glow at the horizon
        # (46,108,90) — its separator from rows 7/8, held exactly (this is a COOL
        # teal glow, not a warm ember, so it satisfies FIX 2's dark-cool bottom).
        # Night sky_top VALUE stays clearly DARKER than this row's sunset top.
        0.62: dict(sky_top=(26, 35, 84),   sky_mid=(94, 50, 106),   sky_bot=(157, 63, 101),  horizon=(186, 68, 84),   star_alpha=84),
        0.68: dict(sky_top=(24, 35, 75),   sky_mid=(33, 70, 94),    sky_bot=(61, 101, 111),  horizon=(56, 131, 124),  star_alpha=134),
        0.72: dict(sky_top=(21, 30, 61),   sky_mid=(30, 44, 70),    sky_bot=(38, 54, 70),    horizon=(40, 94, 78),    star_alpha=185),
        0.80: dict(sky_top=(22, 30, 61),   sky_mid=(31, 45, 71),    sky_bot=(40, 56, 71),    horizon=(42, 96, 80),    star_alpha=120),
        # SUNRISE — fresh cyan-and-peach; cool, calm, plainly a different moment.
        0.88: dict(sky_top=(72, 150, 190), sky_mid=(120, 194, 212), sky_bot=(190, 198, 200), horizon=(236, 174, 152)),
        0.94: dict(sky_top=(80, 158, 196), sky_mid=(124, 198, 214), sky_bot=(196, 202, 202), horizon=(240, 180, 158)),
    },
)


# 10. Blood Scarlet — BOLD [pure-red inferno]. [NIGHT TIER: DEEP-BUT-COOL] The only
#     pure-red evening of the set: golden reads blood-ORANGE, sunset migrates to hot
#     SCARLET, the 0.56 dwell tips crimson-oxblood — an orange→scarlet over-time
#     journey, hotter and redder than any anchor — then it falls to a deep cool
#     oxblood-indigo night (the scarlet ember fully cooled out). Sunrise: a fresh
#     peach-rose dawn.
BLOOD_SCARLET = _spec(
    'Blood Scarlet',
    'BOLD [pure-red inferno]: the only pure-red evening — golden 0.40 reads blood-ORANGE, sunset 0.50 migrates to hot SCARLET, the 0.56 dwell tips CRIMSON-oxblood, hotter than any anchor. GOLDEN ONSET still eases the cyan top in luminous (0.35→0.40 warm) so the fire arrives gradually. NIGHT: a deep COOL oxblood-indigo (DEEP tier) — the scarlet horizon ember persists through dusk, fades by twilight, fully cool by deep night (no warm ember), star_alpha peaks ~230. SUNRISE: a fresh peach-rose dawn.',
    {
        # GOLDEN ONSET — FIX 1: 0.35/0.40 ease the cyan top into a luminous warm
        # orange-gold (NOT the live dark-violet snap), then the fire intensifies
        # across 0.44→0.50→0.56 as the horizon drives to scarlet and the top deepens
        # to an oxblood-violet. The hot rose-red mid is the saturated bridge keeping
        # the warm→violet column from greying. The over-time hue PATH is the identity.
        0.35: dict(sky_top=(134, 146, 153), sky_mid=(228, 186, 168), sky_bot=(255, 184, 142), horizon=(255, 150, 92)),
        0.40: dict(sky_top=(162, 133, 146), sky_mid=(244, 142, 116), sky_bot=(252, 130, 78),  horizon=(255, 110, 56)),
        0.44: dict(sky_top=(108, 70, 130),  sky_mid=(232, 96, 100),  sky_bot=(248, 104, 56),  horizon=(248, 84, 40)),
        0.50: dict(sky_top=(64, 40, 110),   sky_mid=(216, 56, 84),   sky_bot=(240, 78, 44),   horizon=(232, 56, 34)),
        0.56: dict(sky_top=(50, 30, 92),    sky_mid=(192, 48, 84),   sky_bot=(218, 66, 46),   horizon=(206, 48, 38)),
        # DUSK→TWILIGHT→NIGHT [DEEP-BUT-COOL] — the scarlet ember holds through
        # dusk, fades at twilight, dark+COOL by deep night into an OXBLOOD-INDIGO
        # (deep-night sky_top (20,24,54), bottom fully cool — no warm ember at the
        # deepest point, the key FIX-2 change from the warm-bottom Ember-Gold-LIVE).
        # The oxblood survives only as the dome cast up top, not as a horizon glow.
        0.62: dict(sky_top=(31, 24, 56),   sky_mid=(104, 45, 63),   sky_bot=(144, 57, 49),   horizon=(165, 52, 38),  star_alpha=90),
        0.68: dict(sky_top=(24, 24, 52),   sky_mid=(56, 33, 56),    sky_bot=(84, 45, 59),    horizon=(110, 54, 57),   star_alpha=158),
        0.72: dict(sky_top=(17, 21, 47),   sky_mid=(26, 26, 50),    sky_bot=(35, 35, 57),    horizon=(47, 45, 66),    star_alpha=230),
        0.80: dict(sky_top=(19, 23, 49),   sky_mid=(28, 28, 52),    sky_bot=(37, 37, 59),    horizon=(50, 49, 70),    star_alpha=170),
        # SUNRISE — fresh peach over a rose horizon; clearer than the blood dusk.
        0.88: dict(sky_top=(72, 116, 156), sky_mid=(232, 158, 140), sky_bot=(255, 168, 132), horizon=(255, 146, 112)),
        0.94: dict(sky_top=(82, 142, 176), sky_mid=(240, 176, 158), sky_bot=(255, 182, 146), horizon=(255, 160, 130)),
    },
)


# 11. Ember Gold (LIVE · current — too dark) — the EXACT current-committed Ember
#     Gold override table, verbatim, with the BLACK-night keyframes that ship today
#     (deep-night 0.72 sky_top=(12,12,30) — essentially black; horizon a warm
#     bronze ember (96,64,48)). Carried as the before/after baseline so the user
#     can see, side-by-side, the void+warm-ember night they are complaining about
#     against the lifted, dark-cool nights of rows 1–10. It has NO 0.35 onset
#     bridge, so its golden-hour snap shows too. Deliberately NOT fixed.
EMBER_GOLD_LIVE = _spec(
    'Ember Gold (LIVE · current — too dark)',
    'BEFORE/AFTER REFERENCE: the exact LIVE Ember Gold that ships today — golden 0.40 top is a muted dark brown (124,96,70) that snaps to deep violet by 0.50 (the "zenith snapping dark" the user flagged), and the deep-night 0.72 sky_top is (12,12,30), essentially BLACK, with a warm bronze horizon ember (96,64,48) that never joins the night. Carried verbatim as the baseline against the luminous golden onset + lifted, dark-cool nights of rows 1–10. Deliberately NOT fixed.',
    {
        0.40: dict(sky_top=(124, 96, 70),   sky_mid=(244, 174, 78),  sky_bot=(255, 192, 64),  horizon=(255, 150, 36)),
        0.44: dict(sky_top=(104, 70, 96),   sky_mid=(238, 138, 86),  sky_bot=(255, 168, 54),  horizon=(252, 110, 32)),
        0.50: dict(sky_top=(82, 48, 116),   sky_mid=(232, 94, 90),   sky_bot=(252, 134, 50),  horizon=(238, 80, 30)),
        0.56: dict(sky_top=(78, 40, 124),   sky_mid=(210, 72, 116),  sky_bot=(230, 92, 70),   horizon=(218, 66, 48)),
        0.62: dict(sky_top=(38, 28, 70),   sky_mid=(126, 70, 90),   sky_bot=(184, 108, 64),  horizon=(210, 96, 44),  star_alpha=88),
        0.68: dict(sky_top=(26, 20, 54),   sky_mid=(78, 48, 72),    sky_bot=(124, 78, 64),   horizon=(160, 88, 50),  star_alpha=156),
        0.72: dict(sky_top=(12, 12, 30),   sky_mid=(30, 26, 48),    sky_bot=(56, 46, 56),    horizon=(96, 64, 48),   star_alpha=236),
        0.80: dict(sky_top=(16, 16, 38),   sky_mid=(36, 34, 58),    sky_bot=(64, 56, 64),    horizon=(102, 76, 58),  star_alpha=168),
        0.88: dict(sky_top=(72, 110, 150), sky_mid=(220, 158, 134), sky_bot=(255, 178, 132), horizon=(255, 168, 110)),
        0.94: dict(sky_top=(82, 138, 172), sky_mid=(228, 178, 158), sky_bot=(255, 192, 150), horizon=(255, 182, 132)),
    },
)


# Sheet order: 6 Ember-Gold-FAMILY anchors, then 4 BOLD departures, then the LIVE
# (current, too-dark) Ember Gold as the before/after reference row last.
CONCEPTS = [
    ('ember_gold', EMBER_GOLD),
    ('amber_warm', AMBER_WARM),
    ('rose_gold_glow', ROSE_GOLD_GLOW),
    ('coral_ember', CORAL_EMBER),
    ('deep_plum_ember', DEEP_PLUM_EMBER),
    ('cool_plum_gold', COOL_PLUM_GOLD),
    ('amethyst_nightfall', AMETHYST_NIGHTFALL),
    ('indigo_fire', INDIGO_FIRE),
    ('aurora_teal_magenta', AURORA_TEAL_MAGENTA),
    ('blood_scarlet', BLOOD_SCARLET),
    ('ember_gold_live', EMBER_GOLD_LIVE),
]
