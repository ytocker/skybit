"""8 wild-divergence cloud explorations — no shared silhouette family.

Each variant differs from every other on at least three of: silhouette
family, aspect ratio, edge treatment, palette use, internal structure.
The lineup deliberately spans a vertical hourglass pillar, a horizontal
feathered cirrus streak, a faceted paper polygon, a tilted spiral coil,
a dense satin-stitched silk pillow, a single calligraphic comma stroke,
a chevron flock V-formation, and a pictographic glyph riding on a soft
body wash — no two share the same bounding-box profile or edge logic.

Drop-in: every variant matches `draw_cloud_<name>(surf, x, y, palette,
scale=1.0)`. Palette helpers are imported from the shared cloud module
so the night-cool branch stays single-source — re-implementing it would
desync this set from the live `_cloud_body_color` whenever that file
re-tunes its luminance threshold.
"""
from __future__ import annotations

import math
import pygame

from cloud_variants import (
    _cloud_body_color,
    _ink_shadow_color,
    _lit_edge_color,
)
from ruyi_variants import (
    _is_night,
    _lerp,
    _lerp_color,
    _seeded_jit,
    _alpha_surf,
)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Yún Hanzi Glyph (雲) on a soft body wash
# Research:
#   https://en.wiktionary.org/wiki/%E4%BA%91
#   https://palmstone.com/i-love-the-bold-and-simple-strokes-of-many-of-the-ancient-forms-of-chinese-characters-clouds-%E4%BA%91-yun-are-evoked-with-just-three-lines-in-this-old-version-of-the-character-for-me-the-lower/
#
# Ancient seal-script 云 (yún, cloud) reduces to three coiled strokes —
# a top horizontal, a lower horizontal, and the hooked sub-stroke
# curling under. Rendered here as a calligraphic ornament sitting ON a
# soft cumulus body wash, so the eye reads cloud-first then catches the
# glyph as a brushpainted overlay rather than as standalone text.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_yun_glyph(surf, x, y, palette, scale=1.0):
    """Pictographic 云 character painted onto a soft cloud body wash."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(64 * scale)
    h = int(50 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    cx = pad + w // 2
    cy = pad + h // 2

    # Soft body wash — low-alpha cumulus pillow behind the glyph so the
    # calligraphy sits on something cloud-shaped rather than floating as
    # disembodied text. Three stacked elliptical dabs of decaying alpha
    # give the wash a feathered edge instead of a hard oval contour.
    wash = _lerp_color(body, lit, 0.05)
    for (offx, offy, rw, rh, a) in (
        (0, 2, int(w * 0.95), int(h * 0.72), 90),
        (-int(w * 0.18), -int(h * 0.06), int(w * 0.55), int(h * 0.58), 80),
        (int(w * 0.20), int(h * 0.08), int(w * 0.50), int(h * 0.50), 75),
    ):
        pygame.draw.ellipse(
            s, (*wash, a),
            pygame.Rect(cx + offx - rw // 2, cy + offy - rh // 2, rw, rh))

    # Stroke colour is the body tint pushed toward the ink-shadow so the
    # glyph reads as confident brush ink against the lighter wash —
    # opposite contrast direction from the wash makes the glyph pop.
    stroke = _lerp_color(body, edge, 0.55) if not night else \
        _lerp_color(body, lit, 0.35)
    contour = edge
    # Fattened brushstrokes ~2× the round-1 weight so the calligraphy
    # reads as ornament-on-cloud, not as a hairline ink doodle.
    stroke_w = max(5, int(round(7 * scale)))

    # Top horizontal — the heaven-stroke. Slight downward bow at right so
    # the stroke reads as a swept calligraphic horizontal rather than a
    # ruled line; the bow ALSO breaks alignment with the second stroke so
    # the two horizontals don't look like a clip-art equals sign.
    top_y = pad + int(h * 0.22)
    top_pts = (
        (pad + int(w * 0.14), top_y),
        (pad + int(w * 0.40), top_y - 1),
        (pad + int(w * 0.66), top_y + 1),
        (pad + int(w * 0.86), top_y + 4),
    )
    pygame.draw.lines(s, (*stroke, 245), False, top_pts, stroke_w)

    # Second horizontal — wider, with a leftward sweep into the curl. The
    # leftward sweep is what tells the eye the lower mass is one stroke
    # that continues into the hook, not two separate strokes.
    mid_y = pad + int(h * 0.48)
    mid_pts = (
        (pad + int(w * 0.08), mid_y + 2),
        (pad + int(w * 0.35), mid_y),
        (pad + int(w * 0.62), mid_y + 1),
        (pad + int(w * 0.90), mid_y + 5),
    )
    pygame.draw.lines(s, (*stroke, 248), False, mid_pts, stroke_w)

    # The defining hook curl — the sub-glyph 厶 evolved into 私; here it
    # reads as the cloud's coiling underbody. Painted as an arc that
    # completes a calligraphic ㄣ — left-flick into a rising curl. The
    # hook is what makes the glyph read as 云 / 雲 rather than two
    # parallel sticks.
    hook_cx = pad + int(w * 0.52)
    hook_cy = pad + int(h * 0.72)
    hook_r = int(h * 0.22)
    pygame.draw.arc(
        s, (*stroke, 245),
        pygame.Rect(hook_cx - hook_r, hook_cy - hook_r,
                    hook_r * 2, hook_r * 2),
        math.radians(40), math.radians(330), stroke_w)
    # Trailing flick — the brush lifts to the lower-right. Painted as a
    # short tapered line so the gesture reads as a confident stroke
    # release rather than a clipped arc end.
    flick_a = (hook_cx + int(hook_r * 0.88), hook_cy + int(hook_r * 0.50))
    flick_b = (hook_cx + int(hook_r * 1.30), hook_cy + int(hook_r * 1.15))
    pygame.draw.line(s, (*stroke, 235), flick_a, flick_b, max(3, stroke_w - 2))

    # A whisper of ink-shadow under each horizontal — gated to non-night
    # phases because deep-blue night turns the under-shadow into smudge.
    if not night:
        pygame.draw.lines(s, (*contour, 70), False,
                          [(px, py + 2) for px, py in top_pts], 1)
        pygame.draw.lines(s, (*contour, 70), False,
                          [(px, py + 2) for px, py in mid_pts], 1)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Vertical Sumeru Pillar
# Research:
#   https://en.wikipedia.org/wiki/Mount_Meru_(Buddhism)
#   https://www.hdasianart.com/blogs/news/mount-meru-in-buddhism-the-cosmic-axis-of-the-universe
#
# Mount Sumeru in Buddhist cosmology is hourglass-shaped — wide base,
# wide top, pinched waist. Rendered here as a vertical thunderhead
# pillar reading as a cosmic axis rather than a horizontal drift. The
# 44 × 80 footprint plus an exaggerated waist pinch locks it as the
# lineup's vertical anchor at thumbnail scale.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_sumeru_pillar(surf, x, y, palette, scale=1.0):
    """Hourglass thunderhead pillar — vertical Sumeru-axis cloud column."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(44 * scale)
    h = int(80 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    cx = pad + w // 2

    # Hourglass profile widened from the round-1 28 px and waist
    # exaggerated to ~18% of cap width — the deeper pinch keeps the
    # cosmic-axis read alive at the thumbnail scales the harness uses.
    bands = (
        # (y_frac, half_w_frac, alpha)
        (0.04, 1.00, 235),
        (0.16, 0.85, 240),
        (0.30, 0.55, 230),
        (0.46, 0.32, 215),
        (0.50, 0.20, 210),  # deepest waist pinch
        (0.54, 0.32, 215),
        (0.70, 0.55, 230),
        (0.84, 0.85, 235),
        (0.96, 1.00, 230),
    )
    for (yf, hwf, a) in bands:
        by = pad + int(h * yf)
        hw = max(2, int(w * 0.5 * hwf))
        # Slight vertical thickness per band so the column reads as a
        # stack of soft ink discs, not stripes — discs overlap so the
        # silhouette is continuous from cap to anvil.
        band_h = max(3, int(h * 0.14))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(cx - hw, by - band_h // 2, hw * 2, band_h))

    # Sunlit edge along the column's leading (left) flank — scattered
    # dabs rather than a ruled line so the rim reads as scattered light
    # catching each band's edge. Gated to non-night so the rim doesn't
    # blow out the moonlit-pillar read.
    if not night:
        for (yf, hwf, _a) in bands:
            by = pad + int(h * yf)
            hw = max(2, int(w * 0.5 * hwf))
            pygame.draw.circle(s, (*lit, 200),
                               (cx - hw + 1, by), max(1, int(scale * 1.4)))

    # Ink-shadow on the trailing (right) flank — symmetric counterweight
    # to the highlight so the pillar reads as round volume, not flat
    # paper.
    for (yf, hwf, _a) in bands:
        by = pad + int(h * yf)
        hw = max(2, int(w * 0.5 * hwf))
        pygame.draw.ellipse(
            s, (*edge, 65),
            pygame.Rect(cx + hw - 3, by - 2,
                        max(3, int(scale * 4)), max(3, int(scale * 5))))

    # A single calligraphic "axis" stroke down the pillar's centre — the
    # cosmic-axis read that distinguishes Sumeru from a generic cumulus
    # column. Thin, low alpha so it reads as an inner light line rather
    # than dividing the silhouette.
    axis_col = lit if night else _lerp_color(body, edge, 0.45)
    pygame.draw.line(s, (*axis_col, 110),
                     (cx, pad + 4), (cx, pad + h - 4),
                     max(1, int(scale)))

    surf.blit(s, (int(x - cx), int(y - (pad + h // 2))))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Cirrus Mare's-Tail Streak
# Research:
#   https://en.wikipedia.org/wiki/Cirrus_uncinus_cloud
#   https://earthsky.org/earth/mares-tails-cirrus-uncinus-clouds/
#
# Cirrus uncinus — the "horse's tail" cloud — appears as a thin curled
# hook trailing a long feathered streak. Sailors read it as the leading
# edge of a warm front. Rendered as a 110 × 28 horizontal wisp with a
# curled head on the leading side and ice-crystal fall-streaks raining
# from the spine. Brush-painted feel from a small seeded jitter on the
# hook arc; fall-streaks lifted at night so the streak still reads.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_mares_tail(surf, x, y, palette, scale=1.0):
    """Cirrus uncinus — hooked head dragging a feathered fall-streak."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    length = int(110 * scale)
    h = int(28 * scale)
    pad = 6
    s = _alpha_surf(length + pad * 2, h + pad * 2)
    cy = pad + h // 2

    # Spine — chain of overlapping thin ellipses tapering both width and
    # alpha from head to tail so the streak reads as continuously wisping
    # off rather than stepping down in discrete bands.
    n = 18
    for i in range(n):
        t = i / (n - 1)
        sx = pad + int(t * length)
        sy = cy - int(math.sin(t * math.pi * 0.6) * 3 * scale)
        sw = max(2, int(8 * scale * (1 - t * 0.85)))
        sh = max(1, int(3 * scale))
        a = int(_lerp(220, 50, t))
        pygame.draw.ellipse(s, (*body, a),
                            pygame.Rect(sx - sw // 2, sy - sh // 2, sw, sh))

    # Curled hook — the defining uncinus signature. Drawn as a sequence
    # of short arc segments with ~1 px seeded jitter at each segment
    # join so the curve carries brush-painted irregularity rather than a
    # protractor-perfect arc.
    hook_r = max(4, int(h * 0.45))
    hook_cx = pad + hook_r
    hook_cy = cy + 1
    arc_segments = 6
    arc_start = 40
    arc_end = 260
    arc_w = max(2, int(scale * 3))
    for seg in range(arc_segments):
        a0 = arc_start + (arc_end - arc_start) * seg / arc_segments
        a1 = arc_start + (arc_end - arc_start) * (seg + 1) / arc_segments
        jx = _seeded_jit(x, y, seg, 1)
        jy = _seeded_jit(x, y, seg + 17, 1)
        rect = pygame.Rect(hook_cx - hook_r + jx, hook_cy - hook_r + jy,
                           hook_r * 2, hook_r * 2)
        pygame.draw.arc(s, (*body, 230), rect,
                        math.radians(a0), math.radians(a1), arc_w)
    # Inner sunlit rim along the hook — single thinner arc unjittered so
    # the highlight stays crisp where the brush ink wobbles around it.
    pygame.draw.arc(
        s, (*lit, 180),
        pygame.Rect(hook_cx - hook_r + 1, hook_cy - hook_r + 1,
                    hook_r * 2 - 2, hook_r * 2 - 2),
        math.radians(50), math.radians(200), max(1, int(scale * 2)))

    # Fall-streak feathers — short downward diagonal slants raining from
    # the spine, simulating ice crystals sublimating into drier air. The
    # diagonal angle (not vertical) is what reads as wind shear; perfect
    # verticals would look like rain. Night phase lifts the alpha
    # baseline ~20% so the feathers still register against deep sky.
    rng_seed = (int(x) * 0x9E37) ^ (int(y) * 0x85EB)
    n_fall = 9
    night_lift = 1.20 if night else 1.0
    for k in range(n_fall):
        t = 0.15 + (k / (n_fall - 1)) * 0.75
        fx = pad + int(t * length)
        fy_top = cy + 1
        # Feather length tapers with position so the densest fall-streaks
        # cluster mid-streak — same way uncinus actually disperses.
        flen = max(3, int(h * 0.55 * (0.5 + 0.5 * math.sin(t * math.pi))))
        jit = ((rng_seed >> (k % 12)) & 0x7) - 3
        fy_bot = fy_top + flen
        fx_bot = fx + max(2, int(flen * 0.25)) + jit // 2
        a = int(min(255, _lerp(140, 40, t) * night_lift))
        pygame.draw.line(s, (*body, a),
                         (fx, fy_top), (fx_bot, fy_bot),
                         max(1, int(scale)))

    # Soft ink-shadow whisper under the head — the hook is the streak's
    # densest mass and benefits from a hint of depth so the silhouette
    # reads as 3D foreshortening rather than flat tape.
    pygame.draw.ellipse(
        s, (*edge, 45),
        pygame.Rect(pad + 1, cy + 1, hook_r * 2 + 2, max(3, int(h * 0.35))))

    surf.blit(s, (int(x - length // 2 - pad), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Chevron Flock Contrail
# Research:
#   https://en.wikipedia.org/wiki/Flock_(birds)
#   https://en.wikipedia.org/wiki/V_formation
#
# A V-formation of ink-chevrons reads as either a distant migrating
# flock or a high-altitude squadron contrail — both belong squarely in
# the sky vocabulary. The lead chevron is heaviest; trailing pairs
# alpha-fade by row so the formation has aerial perspective. A faint
# horizontal contrail wisp anchors the flock to the same altitude band,
# tying the marks to a single sky stratum rather than scattered points.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_chevron_flock(surf, x, y, palette, scale=1.0):
    """V-formation chevron flock with a thin underlying contrail wisp."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(96 * scale)
    h = int(34 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Underlying contrail wisp — thin alpha-tapered horizontal smear
    # passing through the flock's mid-line. Gives the chevrons a shared
    # altitude band so the formation reads as one flock at one height,
    # not as confetti scattered across z-depths.
    trail_col = _lerp_color(body, lit, 0.15)
    n_trail = 14
    for i in range(n_trail):
        t = i / (n_trail - 1)
        tx = pad + int(t * w)
        # Trail thins toward both ends so it reads as a passing draft
        # rather than a ruled bar.
        a = int(40 + 60 * math.sin(t * math.pi))
        rad = max(1, int(scale * (1.0 + 1.5 * math.sin(t * math.pi))))
        pygame.draw.circle(s, (*trail_col, a), (tx, cy + 3), rad)

    # Chevron ink colour — body pushed toward ink-shadow so each mark
    # reads as a confident brush V against the trail wisp.
    ink = _lerp_color(body, edge, 0.55) if not night else \
        _lerp_color(body, lit, 0.30)

    # Flock layout: lead bird at the left tip, 3 pair-rows trailing
    # right-and-out so the formation forms a sky-true V opening toward
    # the trailing edge. Row alpha decays so distant birds feel further.
    # 1 lead + 3 pairs = 7 chevrons total.
    flock = [
        # (rel_x, rel_y, size, alpha) — rel coords in the bounding box.
        (0.10, 0.50, 1.30, 245),  # lead
        (0.32, 0.34, 1.10, 225),  # row 1 upper
        (0.32, 0.66, 1.10, 225),  # row 1 lower
        (0.55, 0.22, 0.95, 200),  # row 2 upper
        (0.55, 0.78, 0.95, 200),  # row 2 lower
        (0.78, 0.12, 0.80, 170),  # row 3 upper
        (0.78, 0.88, 0.80, 170),  # row 3 lower
    ]

    def _chevron(px, py, sz, a):
        # Each chevron is two short lines meeting at an apex pointing
        # forward (left). The apex offset gives each bird a slight
        # forward bias so the formation visibly leans into its travel.
        arm = max(3, int(6 * sz * scale))
        thick = max(2, int(2.2 * sz * scale))
        apex = (px, py)
        upper_tip = (px + arm, py - max(2, int(arm * 0.55)))
        lower_tip = (px + arm, py + max(2, int(arm * 0.55)))
        pygame.draw.line(s, (*ink, a), apex, upper_tip, thick)
        pygame.draw.line(s, (*ink, a), apex, lower_tip, thick)

    for (rx, ry, sz, a) in flock:
        px = pad + int(rx * w)
        py = pad + int(ry * h)
        _chevron(px, py, sz, a)

    # Lit specular on the lead chevron's upper arm — sunset / dawn light
    # catching the lead bird so the formation has a directional accent
    # without overlighting every mark. Gated by phase so night uses a
    # cooler hint instead of warm sun-rim.
    lead_px = pad + int(0.10 * w)
    lead_py = pad + int(0.50 * h)
    arm = max(3, int(6 * 1.30 * scale))
    rim_col = lit if not night else _lerp_color(lit, body, 0.4)
    pygame.draw.line(
        s, (*rim_col, 200),
        (lead_px + 1, lead_py - 1),
        (lead_px + arm, lead_py - max(2, int(arm * 0.55)) + 1),
        max(1, int(scale)))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Origami Folded Crane-Cloud
# Research:
#   https://en.wikipedia.org/wiki/Origami
#   https://en.wikipedia.org/wiki/Orizuru
#
# Faceted paper-fold silhouette — flat polygon cloud with two plane
# tones (lit/shadow) split along a single crease keyline. The silhouette
# is pulled to a 5-vertex pillow profile so the cohort-family read says
# "cloud" first, with the faceted shading + crease announcing "folded
# paper" as the second beat.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_origami(surf, x, y, palette, scale=1.0):
    """Faceted paper-fold cloud — pillow silhouette with lit/shadow split."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(74 * scale)
    h = int(46 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    cx = pad + w // 2
    cy = pad + h // 2

    # Two faceted plane tones — lit (upper-left) and shadow (lower-
    # right) — so the polygon reads as a folded sheet catching light.
    face_lit = _lerp_color(body, lit, 0.40)
    face_shadow = _lerp_color(body, edge, 0.30)
    # Crease keyline brightens against deep-blue night so the fold
    # geometry doesn't dissolve into the shadow plane; day keeps the
    # original body-toward-edge crease so the keyline still reads as
    # one confident ink line against the lit facet.
    if night:
        crease = _lerp_color(edge, lit, 0.45)
    else:
        crease = _lerp_color(edge, body, 0.35)

    # Five-vertex pillow profile: the silhouette family says "cloud"
    # before the faceted shading announces "paper" as the second beat.
    # Apex sits left-of-centre so the crease angle isn't symmetric and
    # the fold reads as a deliberate paper crease rather than a tent.
    body_poly = [
        (pad + int(w * 0.06), pad + int(h * 0.62)),  # left wing
        (pad + int(w * 0.40), pad + int(h * 0.08)),  # apex / lit peak
        (pad + int(w * 0.78), pad + int(h * 0.24)),  # right shoulder
        (pad + int(w * 0.96), pad + int(h * 0.58)),  # right wing
        (pad + int(w * 0.50), pad + int(h * 0.92)),  # belly low
    ]
    pygame.draw.polygon(s, (*face_shadow, 240), body_poly)

    # Lit plane — upper-left half cut along the crease running from
    # left wing through the apex out to the right shoulder. The brighter
    # triangle sits where a top-left light source would actually catch
    # the folded paper.
    lit_poly = [
        (pad + int(w * 0.06), pad + int(h * 0.62)),
        (pad + int(w * 0.40), pad + int(h * 0.08)),
        (pad + int(w * 0.78), pad + int(h * 0.24)),
        (pad + int(w * 0.50), pad + int(h * 0.55)),
    ]
    pygame.draw.polygon(s, (*face_lit, 235), lit_poly)

    # Crease keyline — single ridge running from the belly up through
    # the apex out to the right shoulder. One clean fold is the signal
    # that the shape is paper, not a vapour blob.
    crease_pts = [
        (pad + int(w * 0.50), pad + int(h * 0.92)),
        (pad + int(w * 0.40), pad + int(h * 0.08)),
        (pad + int(w * 0.78), pad + int(h * 0.24)),
    ]
    pygame.draw.lines(s, (*crease, 220), False, crease_pts,
                      max(1, int(scale * 1.4)))

    # Full silhouette outline — 1-px keyline so the paper edge stays
    # crisp against busy backdrops. Night drops alpha so the line
    # doesn't read as overbright against deep blue.
    outline_a = 220 if not night else 170
    pygame.draw.lines(s, (*edge, outline_a), True, body_poly,
                      max(1, int(scale * 1.2)))

    # One sharp lit highlight at the apex — paper catches a sun specular
    # at fold vertices. Drawn as a tiny lit triangle so the highlight
    # has angular character matching the faceted geometry.
    apex = (pad + int(w * 0.40), pad + int(h * 0.08))
    hi_pts = [
        apex,
        (apex[0] - max(2, int(scale * 3)), apex[1] + max(3, int(scale * 4))),
        (apex[0] + max(2, int(scale * 3)), apex[1] + max(3, int(scale * 4))),
    ]
    pygame.draw.polygon(s, (*lit, 230), hi_pts)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 6 — Incense Smoke Volute (tilted)
# Research:
#   https://www.angelicalbalance.com/spirituality/incense-smoke-pattern-meaning/
#   https://monianlife.com/blogs/news/how-to-interpret-incense-smoke-patterns
#
# Rising incense smoke curls in a volute spiral that disperses upward —
# read in East Asian temple iconography as the link between the
# offering and the heavens. Rendered as a coil tilted ~10° off vertical
# so at thumbnail scale it doesn't collide with Sumeru's hourglass
# pillar; the lean also reads as a breeze deflecting the rising smoke.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_smoke_volute(surf, x, y, palette, scale=1.0):
    """Tilted incense-smoke spiral — coil leaning into a breeze."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(56 * scale)
    h = int(80 * scale)
    pad = 8
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    cx = pad + w // 2

    # Per-spawn lean jitter in the ±8° band around the original ~10°
    # baseline — stacked columns on screen would otherwise read as a
    # repeated manufacturing defect when they all tilt identically. Sign
    # of the jitter is also free to flip so half the columns lean right
    # and the bunch reads as a breeze, not a queue.
    base_deg = 10.0
    jitter_deg = _seeded_jit(x, y, 0, 8)
    lean_deg = base_deg + jitter_deg
    lean_amt = math.tan(math.radians(lean_deg))

    # Day-phase contrast bump — against the brightest cyan skies the
    # column wash blows out, so push the body away from the sky's tonal
    # neighbourhood. Gated by sky_top luminance so dusk/sunset and
    # night skies (which already hold the column legibly) stay
    # untouched.
    sky_top = palette['sky_top']
    sky_lum = (sky_top[0] * 299 + sky_top[1] * 587 + sky_top[2] * 114) / 1000
    bright_day = (not night) and sky_lum > 170
    contrast_body = _lerp_color(body, edge, 0.15) if bright_day else body
    alpha_boost = 1.15 if bright_day else 1.0

    # Primary spiral: vertical parametric coil with the column path
    # tilted by lean_amt. Each disc is a soft alpha dab so the path
    # itself becomes the silhouette rather than a fixed shape.
    n = 32
    for i in range(n):
        t = i / (n - 1)
        py = pad + int(h * (1.0 - t))
        if t < 0.3:
            r_amp = _lerp(0.10, 0.30, t / 0.3)
        elif t < 0.75:
            r_amp = _lerp(0.30, 0.50, (t - 0.3) / 0.45)
        else:
            r_amp = _lerp(0.50, 0.58, (t - 0.75) / 0.25)
        radius = w * 0.5 * r_amp
        theta = t * math.tau * 2.5
        col_x = cx + int((py - (pad + h // 2)) * -lean_amt)
        px = col_x + int(math.cos(theta) * radius)
        disc_r = max(2, int(scale * _lerp(4.5, 1.8, t)))
        a = min(255, int(_lerp(220, 50, t) * alpha_boost))
        pygame.draw.circle(s, (*contrast_body, a), (px, py), disc_r)

    # Secondary inner spiral — half the disc count of round 1 so the
    # inner coil hints at 3D depth without muddying the silhouette into
    # a stipple cloud. Opposite phase keeps it visibly distinct from
    # the primary.
    inner_n = 8
    for i in range(inner_n):
        t = i / (inner_n - 1)
        py = pad + int(h * (1.0 - t * 0.85))
        r_amp = _lerp(0.06, 0.28, t)
        radius = w * 0.5 * r_amp
        theta = t * math.tau * 2.0 + math.pi
        col_x = cx + int((py - (pad + h // 2)) * -lean_amt)
        px = col_x + int(math.cos(theta) * radius)
        disc_r = max(1, int(scale * _lerp(3, 1.2, t)))
        a = int(_lerp(160, 30, t))
        pygame.draw.circle(s, (*edge, a), (px, py), disc_r)

    # Glowing ember at the base — anchors the column with a single warm
    # dab. Night uses a cool-lit variant so the ember reads as moonlit
    # incense rather than flame.
    ember_col = lit if not night else _lerp_color(lit, body, 0.40)
    ember_x = cx + int(((pad + h - 4) - (pad + h // 2)) * -lean_amt)
    ember_y = pad + h - 4
    pygame.draw.circle(s, (*ember_col, 230), (ember_x, ember_y),
                       max(2, int(scale * 3)))
    pygame.draw.circle(s, (*ember_col, 80), (ember_x, ember_y),
                       max(3, int(scale * 5)))

    surf.blit(s, (int(x - cx), int(y - (pad + h // 2))))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 7 — Suzhou Embroidery Stitch
# Research:
#   https://www.suembroidery.com/chinese-silk-embroidery-blog/stitches-of-suzhou-embroidery
#   https://en.wikipedia.org/wiki/Chinese_embroidery
#
# Su xiu (苏绣) — Chinese silk embroidery — uses dense satin-stitch fill
# bound by couched-stitch outlines. Rendered as a cloud silhouette
# stitched onto the sky: filled body with visible parallel stitch
# hatching, perimeter bound by a chain of dot-stitches. Aspect relaxed
# to ~80 × 34 so this variant sits as the cohort's common cumulus body;
# wider hatch step kills the small-scale moire of round 1.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_embroidery(surf, x, y, palette, scale=1.0):
    """Couched-stitch cloud — silk-embroidered silhouette with dot perimeter."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(80 * scale)
    h = int(34 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Silk thread tone — body pushed slightly toward lit so the fill
    # reads as woven sheen.
    thread = _lerp_color(body, lit, 0.20)
    thread_shadow = _lerp_color(body, edge, 0.30)
    couch = _lerp_color(edge, body, 0.25)

    # Cloud silhouette as a parametric closed curve — stacked half-lobes
    # joined into a long pillow. Used both to fill and to anchor the
    # perimeter dots so stitches sit exactly on the boundary.
    n_perim = 28
    perim = []
    for k in range(n_perim):
        t = k / n_perim
        ang = t * math.tau
        # Wider horizontally with a cosine-modulated vertical falloff —
        # three soft humps on top, flatter bottom, so the silhouette
        # has cloud rhythm without becoming a perfect oval.
        rx = w * 0.45 * (1.0 + 0.08 * math.cos(ang * 3))
        ry = h * 0.45 * (1.0 + 0.15 * math.sin(ang * 2))
        if math.sin(ang) > 0:
            ry *= 1.10
        else:
            ry *= 0.75
        px = cx + int(math.cos(ang) * rx)
        py = cy - int(math.sin(ang) * ry)
        perim.append((px, py))

    pygame.draw.polygon(s, (*thread, 245), perim)

    # Horizontal satin-stitch hatching — wider hatch_step (3 px base)
    # so small-scale tiles don't read as moire interference. Hatch
    # alpha pulled ~30% lower from round 1 so the stitch lines whisper
    # the satin texture rather than printing as ledger ruling.
    hatch_step = max(3, int(scale * 3.2))
    hatch_alpha = 155
    for hy in range(pad + 2, pad + h - 1, hatch_step):
        # Estimate the silhouette's half-width at this y by inverting
        # the parametric used above. Lines outside the polygon end up
        # alpha-zero against transparent pixels so no explicit clip is
        # needed.
        rel_y = (cy - hy) / (h * 0.45)
        if abs(rel_y) >= 1.0:
            continue
        if rel_y > 0:
            v_scale = 1.10
        else:
            v_scale = 0.75
        adj = max(-1.0, min(1.0, rel_y / v_scale))
        ang = math.asin(adj)
        rx = w * 0.45 * (1.0 + 0.08 * math.cos(ang * 3))
        half_w = int(abs(math.cos(ang)) * rx) - 2
        if half_w <= 1:
            continue
        # Alternate hatch tone every other line so the satin sheen has
        # subtle ridge variation — actual satin shows this up close.
        col = thread if (hy // hatch_step) % 2 == 0 else thread_shadow
        pygame.draw.line(s, (*col, hatch_alpha),
                         (cx - half_w, hy), (cx + half_w, hy), 1)

    # Dusk + night skies push the cumulus toward a muddy purple because
    # every channel just attenuates uniformly. A cool rim — pulled from
    # the sky_top, desaturated toward a neutral blue-grey — gives the
    # perimeter a moonlit / twilight bias that reads as scattered cool
    # light rather than dye bleed. Trigger is either a strict night
    # luminance OR a magenta-biased dusk where blue<red and overall
    # luminance is sub-130.
    sky_top = palette['sky_top']
    sky_lum = (sky_top[0] * 299 + sky_top[1] * 587 + sky_top[2] * 114) / 1000
    dusk_bias = (sky_lum < 130) and (sky_top[2] < sky_top[0])
    cool_phase = night or dusk_bias
    # Desaturate toward blue-grey — mix sky_top with a neutral cool
    # anchor so the rim never picks up sunset magenta. Brightness held
    # low so the ring whispers rather than hard-outlining each dot.
    cool_rim = _lerp_color(sky_top, (170, 185, 205), 0.55)

    # Couched-stitch perimeter — dots evenly spaced along the boundary.
    dot_r = max(1, int(scale * 1.6))
    for (px, py) in perim:
        pygame.draw.circle(s, (*couch, 230), (px, py), dot_r)
        # Inner highlight only on day phases where the dots otherwise
        # blend with the lit body fill.
        if not night:
            pygame.draw.circle(s, (*lit, 200), (px - 1, py - 1),
                               max(1, dot_r - 1))
        # Cool rim — single-pixel ring just outside each perimeter dot
        # so the cumulus carries moonlight at its silhouette edge
        # without changing its bounding box.
        if cool_phase:
            pygame.draw.circle(s, (*cool_rim, 170), (px, py), dot_r + 1, 1)

    # One curved "running-stitch" accent inside the body — short arc of
    # 4 dots near the top, the silk-cloud's auspicious-detail nod kept
    # small so the perimeter dots stay the dominant edge treatment.
    inner_arc_r = max(4, int(h * 0.20))
    for k in range(4):
        t = k / 3
        ang = math.radians(_lerp(195, 345, t))
        ix = cx + int(math.cos(ang) * inner_arc_r * 1.3)
        iy = cy - int(h * 0.15) + int(math.sin(ang) * inner_arc_r * 0.7)
        pygame.draw.circle(s, (*couch, 200), (ix, iy), max(1, dot_r - 1))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 8 — Sumi-e Brushstroke Comma
# Research:
#   https://en.wikipedia.org/wiki/Ink_wash_painting
#   https://en.wikipedia.org/wiki/Flying_white
#
# Sumi-e ink-wash technique values the single confident stroke: brush
# loaded heavy at the head, dragged dry through the tail so the trailing
# end shows flying-white (kasure / 飛白) gaps where the bristles outrun
# the ink. Rendered as a calligraphic comma — wet-loaded head bulb,
# tapered curve, dry-brush flicker at the tail. Pure silhouette: no
# keyline, no inner facets, just the gesture of one stroke.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_sumie_comma(surf, x, y, palette, scale=1.0):
    """Single sumi-e comma stroke — wet head, dry-brush flying-white tail."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(96 * scale)
    h = int(38 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Ink colour for a sumi-e cloud — body pushed firmly toward the
    # ink-shadow so the stroke reads as wet ink against the sky; night
    # branch pulls the other direction so the cloud doesn't dissolve
    # into deep-blue.
    ink = _lerp_color(body, edge, 0.30) if not night else \
        _lerp_color(body, lit, 0.20)

    # Comma path — parametric curve from a head bulb at the left bowing
    # gently down and back up through a tapered tail. Painted as a chain
    # of overlapping ellipses: radius and alpha bell-curve down the
    # length so the head is dense and the tail wisps away.
    n = 26
    head_x = pad + int(w * 0.18)
    head_y = pad + int(h * 0.40)
    tail_x = pad + int(w * 0.92)
    tail_y = pad + int(h * 0.62)
    # Control point sets up the gentle downward-then-up bow.
    ctrl_x = pad + int(w * 0.55)
    ctrl_y = pad + int(h * 0.80)

    # Seeded RNG for the flying-white gap pattern so the brush flicker
    # is deterministic per-spawn rather than re-rolled each frame.
    rng_seed = (int(x) * 0x9E3779B1) ^ (int(y) * 0x7F4A7C15)

    for i in range(n):
        t = i / (n - 1)
        # Quadratic Bézier evaluation along the comma path.
        mt = 1.0 - t
        bx = mt * mt * head_x + 2 * mt * t * ctrl_x + t * t * tail_x
        by = mt * mt * head_y + 2 * mt * t * ctrl_y + t * t * tail_y
        # Width profile — fat head bulb (t≈0.05), shoulder swell (t≈0.25),
        # then steady taper to a near-zero tail. The shoulder swell is
        # what makes a comma comma-shaped instead of a teardrop.
        if t < 0.25:
            radius = _lerp(8.0, 9.5, t / 0.25)
        else:
            radius = _lerp(9.5, 1.2, (t - 0.25) / 0.75)
        radius *= scale
        # Alpha bell — wet head sits near full opacity, mid-stroke holds,
        # tail wisps off. Flying-white gaps puncture the tail half by
        # cutting alpha to near-zero on hash-selected steps.
        a_base = int(_lerp(245, 90, t))
        kasure = 0
        if t > 0.55:
            # Pseudo-random gap mask — selected steps drop alpha to 25
            # so the bristles read as separating out from the ink load.
            v = ((rng_seed + i * 0x85EBCA77) & 0xFF) / 0xFF
            if v < 0.42:
                kasure = -130
        a = max(20, a_base + kasure)
        pygame.draw.circle(s, (*ink, a), (int(bx), int(by)),
                           max(1, int(radius)))

    # Head bulb accent — one small wet-ink dab just inside the head
    # giving the stroke its loaded-brush weight. No keyline anywhere
    # on this variant; the bulb IS the silhouette's bold head, sized
    # to push past the body radii at t≈0 only.
    bulb_x = pad + int(w * 0.13)
    bulb_y = pad + int(h * 0.46)
    pygame.draw.circle(s, (*ink, 240), (bulb_x, bulb_y),
                       max(3, int(scale * 5.5)))

    # Single flying-white speckle ahead of the brush bristles — a few
    # widely-spaced specks past the tail end so the eye reads "brush
    # lifted with momentum" rather than "stroke ended at point". Speck
    # alpha kept low so they whisper rather than read as separate dots.
    for k in range(3):
        v = ((rng_seed + (k + 7) * 0x27D4EB2F) & 0xFFFF) / 0xFFFF
        sx = tail_x + int(_lerp(2, 10, v) * scale)
        sy = tail_y + ((k - 1) * max(1, int(scale * 2)))
        pygame.draw.circle(s, (*ink, 110),
                           (sx, sy), max(1, int(scale)))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ── registries ───────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_cloud_yun_glyph,
    2: draw_cloud_sumeru_pillar,
    3: draw_cloud_mares_tail,
    4: draw_cloud_chevron_flock,
    5: draw_cloud_origami,
    6: draw_cloud_smoke_volute,
    7: draw_cloud_embroidery,
    8: draw_cloud_sumie_comma,
}

VARIANT_NAMES = {
    1: "Yún Hanzi Glyph on Wash (雲)",
    2: "Sumeru Vertical Pillar",
    3: "Cirrus Mare's-Tail Streak",
    4: "Chevron Flock Contrail",
    5: "Origami Folded Pillow",
    6: "Incense Smoke Volute (tilted)",
    7: "Suzhou Embroidery Stitch",
    8: "Sumi-e Brushstroke Comma",
}

VARIANT_SOURCES = {
    1: "https://en.wiktionary.org/wiki/%E4%BA%91 (云 yun pictographic)",
    2: "https://en.wikipedia.org/wiki/Mount_Meru_(Buddhism)",
    3: "https://en.wikipedia.org/wiki/Cirrus_uncinus_cloud",
    4: "https://en.wikipedia.org/wiki/V_formation",
    5: "https://en.wikipedia.org/wiki/Orizuru",
    6: "https://www.angelicalbalance.com/spirituality/incense-smoke-pattern-meaning/",
    7: "https://www.suembroidery.com/chinese-silk-embroidery-blog/stitches-of-suzhou-embroidery",
    8: "https://en.wikipedia.org/wiki/Ink_wash_painting",
}
