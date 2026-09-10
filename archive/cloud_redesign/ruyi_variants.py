"""Round-24 Ruyi-cloud explorations: 8 directions off the round-23 V2.

The round-23 Ruyi (祥云) variant landed SHIP-READY but read too packed in
field — three lobes + base ribbon + arc keylines compress a lot of ink
into a 72-px silhouette. These 8 candidates each pull on ONE knob of
that base: aspect ratio, lobe count, edge treatment, interior structure,
or palette consumption — to find a sparser / more atmospheric Ruyi that
still reads as auspicious-cloud at thumbnail scale.

Drop-in contract is identical to `cloud_variants.draw_cloud_*`:
    `draw_ruyi_<name>(surf, x, y, palette, scale=1.0)`

Shared edge/body tinting is imported from `cloud_variants` — there's
exactly one definitive night-cool branch in the project and it lives
there. Do NOT re-implement those helpers here.
"""
from __future__ import annotations

import math
import pygame

from cloud_variants import (
    _cloud_body_color,
    _ink_shadow_color,
    _lit_edge_color,
)


# ── shared helpers ──────────────────────────────────────────────────────────

def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_color(a, b, t):
    return (
        int(_lerp(a[0], b[0], t)),
        int(_lerp(a[1], b[1], t)),
        int(_lerp(a[2], b[2], t)),
    )


def _alpha_surf(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((max(2, int(w)), max(2, int(h))), pygame.SRCALPHA)


def _seeded_jit(x: float, y: float, idx: int, amp: int) -> int:
    # Deterministic per-spawn LCG step so silhouette jitter doesn't
    # reshuffle frame-to-frame. Matches the seeding pattern used by the
    # round-23 baseline so jitter "feels" the same across variants.
    seed = (int(x) * 0x9E3779B1) ^ (int(y) * 0x7F4A7C15)
    v = ((seed + idx * 2654435761) & 0xFFFF) / 0xFFFF
    return int((v - 0.5) * 2 * amp)


def _is_night(palette: dict) -> bool:
    # Single luminance test used to gate night-only branches like the
    # ghost-white halos on the Sovereign and Sumi-e variants. Threshold
    # matches `_cloud_body_color`'s 90 split point so the cloud cools
    # in sync with its night-branch body.
    top = palette['sky_top']
    return (top[0] * 299 + top[1] * 587 + top[2] * 114) / 1000 < 90


def _ruyi_lobe(s: pygame.Surface, cx: int, cy: int, r: int,
               body, edge, lit,
               body_a: int = 245, key_a: int = 160,
               lit_arc: bool = False) -> None:
    # One canonical ruyi lobe: filled circle + lower-left calligraphic
    # arc keyline (200°–340°) + inner-curl arc (20°–200°). Pulled out
    # of the round-23 inline code so all 8 variants paint the same lobe
    # vocabulary, only varying count / spacing / palette.
    pygame.draw.circle(s, (*body, body_a), (cx, cy), r)
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(cx - r, cy - r, r * 2, r * 2),
        math.radians(200), math.radians(340), 2)
    inner = max(3, r - 5)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(cx - inner, cy - inner, inner * 2, inner * 2),
        math.radians(20), math.radians(200), 2)
    if lit_arc and r >= 6:
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(cx - r + 2, cy - r + 2,
                        max(2, r * 2 - 4), max(2, r * 2 - 4)),
            math.radians(110), math.radians(220), 2)


def _ruyi_heart(s: pygame.Surface, cx: int, cy: int, r: int,
                body, edge, lit,
                body_a: int = 245, key_a: int = 170,
                lit_arc: bool = False) -> None:
    # Two mirrored half-lobes joined at the base — this is the silhouette
    # signature that says "Ruyi" rather than "circle". Cluster of: left
    # lobe + right lobe centred horizontally on cx, vertically tucked so
    # their bottoms meet just under cy, with a downward V-notch between
    # them. The notch is what reads as a heart, not a peanut, at thumb-
    # nail. Used wherever the AD called for "double-lobed heart DNA".
    off = max(2, int(r * 0.55))
    lr = max(3, int(r * 0.78))
    lcx_l = cx - off
    lcx_r = cx + off
    lcy = cy - max(1, int(r * 0.10))
    # Drop-shadow first (under both halves) so it doesn't double-bake
    # in the join seam.
    pygame.draw.circle(s, (*edge, 30), (cx + 1, cy + 3), r)
    # Twin half-lobes — drawn as full discs then welded by a small
    # bridging ellipse at the base so the silhouette reads as one
    # continuous heart rather than two stamped balls.
    pygame.draw.circle(s, (*body, body_a), (lcx_l, lcy), lr)
    pygame.draw.circle(s, (*body, body_a), (lcx_r, lcy), lr)
    bridge_w = off * 2 + 2
    bridge_h = max(3, int(r * 0.55))
    pygame.draw.ellipse(
        s, (*body, body_a),
        pygame.Rect(cx - bridge_w // 2, lcy, bridge_w, bridge_h))
    # V-notch on top centre — small triangle in transparent so the heart
    # cleavage is visible. Achieved by repainting the body's interior
    # gap with the surface's clear-pixel through BLEND_RGBA_MULT mask
    # would be heavier; here a single 1-px tip indent is enough at the
    # scales we render.
    notch_top = (cx, lcy - lr + 2)
    notch_l = (cx - max(1, lr // 4), lcy - lr // 2)
    notch_r = (cx + max(1, lr // 4), lcy - lr // 2)
    pygame.draw.polygon(s, (0, 0, 0, 0), [notch_top, notch_l, notch_r])
    # Calligraphic keyline arcs hugging each half-lobe's outer flank —
    # mirrored so the heart has two flanking curls, the classic Ruyi
    # double-spiral signature.
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(lcx_l - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(200), math.radians(350), 2)
    pygame.draw.arc(
        s, (*edge, key_a),
        pygame.Rect(lcx_r - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(190), math.radians(340), 2)
    inner = max(2, lr - 4)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(lcx_l - inner, lcy - inner, inner * 2, inner * 2),
        math.radians(40), math.radians(200), 2)
    pygame.draw.arc(
        s, (*edge, min(255, key_a + 20)),
        pygame.Rect(lcx_r - inner, lcy - inner, inner * 2, inner * 2),
        math.radians(340), math.radians(140), 2)
    if lit_arc and lr >= 5:
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(lcx_l - lr + 2, lcy - lr + 2,
                        max(2, lr * 2 - 4), max(2, lr * 2 - 4)),
            math.radians(120), math.radians(220), 2)
        pygame.draw.arc(
            s, (*lit, 200),
            pygame.Rect(lcx_r - lr + 2, lcy - lr + 2,
                        max(2, lr * 2 - 4), max(2, lr * 2 - 4)),
            math.radians(110), math.radians(210), 2)


def _wisp_dab(s: pygame.Surface, cx: int, cy: int, r: int,
              body, edge, seed: int, n: int = 3) -> None:
    # Ink-wash dry-brush dab — 3-4 small alpha-faded blobs in a short
    # diagonal stagger. Used to replace solid mini-lobes with flying-
    # white wisps so a constellation reads as "1 Ruyi + 2 wisps" rather
    # than "3 same-size circles". Borrowed from the Sumi-e variant's
    # kasure technique so the visual vocabulary stays in-key.
    for k in range(n):
        ox = ((seed >> (k * 3)) & 0x7) - 3
        oy = ((seed >> (k * 3 + 1)) & 0x3) - 1
        rr = max(1, int(r * (1.0 - k * 0.25)))
        a = max(60, 200 - k * 50)
        pygame.draw.circle(s, (*body, a), (cx + ox + k * 2, cy + oy), rr)
        if k == 0:
            pygame.draw.circle(s, (*edge, 110),
                               (cx + ox + k * 2, cy + oy), rr, 1)


def _ribbon_polygon(cx: int, cy: int, w: int, h: int) -> list[tuple[int, int]]:
    # Symmetric S-tapered ribbon outline — used as a trailing streamer
    # behind a head lobe. Cubic-ish poly approximated via 9 control
    # points so the silhouette has visible widening + tapering instead
    # of a flat strip.
    half_w = w // 2
    return [
        (cx - half_w,           cy + h // 6),
        (cx - half_w + w // 6,  cy - h // 4),
        (cx - w // 5,           cy - h // 3),
        (cx + w // 5,           cy + h // 4),
        (cx + half_w,           cy + h // 6),
        (cx + half_w - w // 8,  cy + h // 3),
        (cx + w // 6,           cy + h // 2),
        (cx - w // 4,           cy + h // 3),
        (cx - half_w + w // 8,  cy + h // 3),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Trailing Ribbon Streamer
# Research:
#   https://news.lenovo.com/pressroom/press-releases/lenovo-designed-olympic-torch-for-beijing-2008-olympic-games-unveiled/
#   https://www.yankodesign.com/2007/04/27/cloud-of-promise-2008-olympic-torch-by-lenovo/
#
# Beijing 2008 "Cloud of Promise" torch motif: one Ruyi lobe HEAD pulling
# a long horizontal silk-ribbon trail behind it. Direct sparser answer to
# "too packed" — most of the silhouette is empty trailing ribbon, the
# auspicious meaning lives in the single head lobe.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_streamer(surf, x, y, palette, scale=1.0):
    """Heart-headed Ruyi pulling a silk ribbon trail — Olympics 2008 motif."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    # Round-2: heart head anchored at LEADING (left) edge with the
    # ribbon trailing RIGHT so the silhouette reads as motion-into-
    # frame. Head radius matches the round-23 dominant-lobe so the
    # heart reads as a full Ruyi at thumbnail, not a comet punctuation.
    length = int(92 * scale)
    head_r = int(15 * scale)
    # Pad expands to fit the heart's twin lobes (each ~0.78 head_r off
    # centre) without clipping at the left edge of the surface.
    pad = int(head_r * 1.8) + 6
    s = _alpha_surf(length + pad * 2, head_r * 3 + 10)
    cx = pad + head_r + 4
    cy = s.get_height() // 2

    # Ribbon trail — taper from full head-height at the join down to
    # zero on the right tip. Drawn as a series of progressively thinner
    # horizontal ellipses with a gentle vertical sine so the ribbon
    # arcs subtly instead of flat-strip slicing the sky.
    n_ribbon = 12
    ribbon_start = cx + int(head_r * 1.4)
    ribbon_end = pad + length
    for i in range(n_ribbon):
        # t goes 1→0 from head to tail so thickness fades AWAY from the
        # head (head-side has mass, tail-tip wisps off).
        t = 1.0 - (i / (n_ribbon - 1))
        rx = ribbon_start + int((1 - t) * (ribbon_end - ribbon_start))
        # Sine swoop matches the Olympics torch's flowing band.
        ry = cy + int(math.sin((1 - t) * math.pi * 0.8 + 0.4) * 4 * scale)
        # Thickness ramped 0.85 → 1.05 per AD round-2: ribbon was too
        # thin to read against sky_top.
        thick = max(1, int(head_r * 1.05 * t))
        # Alpha bumped 70→110 min, 215→245 max — round-1 ribbon went
        # invisible past the head at SUNSET/DUSK.
        a = int(_lerp(110, 245, t))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(rx - thick, ry - thick // 2,
                        thick * 2, max(2, thick)))

    # Ink-shadow underline beneath the ribbon — single long thin
    # ellipse, no full-circumference keyline, so the trail reads as
    # silk in motion rather than a solid heraldic band. Gated off at
    # night per cross-cutting A (drop-shadow smudge halo on deep
    # blue): streamer's underline carries the silk read at day/golden
    # so we keep it on those phases.
    if not _is_night(palette):
        pygame.draw.ellipse(
            s, (*edge, 55),
            pygame.Rect(ribbon_start, cy + head_r // 3,
                        ribbon_end - ribbon_start, max(2, int(head_r * 0.5))))

    # Heart-shape head — two mirrored half-lobes joined at base. The
    # round-1 single `_ruyi_lobe` read as a comet; the heart is what
    # carries the unambiguous "Ruyi" silhouette signature.
    _ruyi_heart(s, cx, cy, head_r, body, edge, lit,
                body_a=245, key_a=180, lit_arc=True)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Single Sovereign Lobe
# Research:
#   https://en.wikipedia.org/wiki/Ruyi_(scepter)
#   https://www.pagodared.com/blog/2024/10/11/as-you-wish-the-ruyi-symbol-in-chinese-japanse-decorative-arts/
#
# Minimalist sacred-symbol read: ONE large lobe, sized just under the
# round-23 dominant lobe but standing alone with no companions. The
# ghost-white night halo + gold-rim sunset moves the sovereign lobe
# toward an icon — auspicious-cloud as a single calligraphic dot.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_sovereign(surf, x, y, palette, scale=1.0):
    """Single 35-px sovereign Ruyi lobe — minimalist icon-grade silhouette."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    r = int(18 * scale)
    # Sibling micro-lobe (45% radius) — bumped from 40% per AD round-2:
    # 40% was borderline on DUSK and didn't survive at 1× scale; 45%
    # clinches the Ruyi double-lobe read across all phases. Needs pad
    # to fit at 4-o'clock.
    sib_r = max(3, int(r * 0.45))
    pad = r + 10 + sib_r
    s = _alpha_surf(r * 2 + pad * 2, r * 2 + pad * 2)
    cx = pad + r
    cy = pad + r

    # Outer aura — pulled wider at night so the sovereign lobe reads as
    # a moon-lit auspicious sigil. Day-phase aura is thin and warm so
    # the icon doesn't bloom too softly against bright sky. Drop-shadow
    # gated at night per cross-cutting A (deep-blue smudge halo on the
    # night branch); the moon-aura takes over the rim read there.
    if night:
        for ring in range(3):
            ar = r + 3 + ring * 2
            pygame.draw.circle(s, (*lit, 30 - ring * 8), (cx, cy), ar)
    else:
        pygame.draw.circle(s, (*edge, 45), (cx + 1, cy + 2), r + 1)

    # Day-phase darkens the keyline edge 10% so the lobe's circumference
    # ink survives bright-blue sky — round-1 day branch washed the
    # silhouette into the cyan dome.
    if not night:
        edge_lobe = (
            max(0, int(edge[0] * 0.90)),
            max(0, int(edge[1] * 0.90)),
            max(0, int(edge[2] * 0.90)),
        )
    else:
        edge_lobe = edge

    # Canonical lobe with stronger keyline alpha — the sovereign read
    # wants a confident inked silhouette. body_a dropped 248→252 per AD
    # round-2 day-contrast note; NIGHT phase drops to 235 per AD round-3
    # because 252 looked chalky against the deep navy night column.
    sovereign_body_a = 235 if night else 252
    _ruyi_lobe(s, cx, cy, r, body, edge_lobe, lit,
               body_a=sovereign_body_a, key_a=190, lit_arc=True)

    # Sibling micro-lobe at the 4-o'clock position — clinches the Ruyi
    # double-lobed silhouette so the icon reads AS a Ruyi rather than a
    # generic moon disc, while keeping the sparseness the sovereign
    # variant exists for.
    sib_ang = math.radians(35)
    sib_cx = cx + int(math.cos(sib_ang) * (r + sib_r - 4))
    sib_cy = cy + int(math.sin(sib_ang) * (r + sib_r - 4))
    if not night:
        pygame.draw.circle(s, (*edge, 35), (sib_cx + 1, sib_cy + 2), sib_r + 1)
    pygame.draw.circle(s, (*body, 248), (sib_cx, sib_cy), sib_r)
    pygame.draw.arc(
        s, (*edge_lobe, 170),
        pygame.Rect(sib_cx - sib_r, sib_cy - sib_r, sib_r * 2, sib_r * 2),
        math.radians(200), math.radians(340), 2)

    # Inner ruyi tail-mark S-glyph — width 2→3 and amplitude widened
    # (lateral 0.35→0.50, vertical 0.95→1.15) per AD round-2 so the
    # ruyi handle reads at thumbnail. The S is what makes the sovereign
    # read as "ruyi symbol" rather than "round pebble".
    tail_top = (cx, cy + int(r * 0.30))
    tail_mid = (cx + int(r * 0.50), cy + int(r * 0.75))
    tail_bot = (cx - int(r * 0.15), cy + int(r * 1.15))
    pygame.draw.lines(s, (*edge, 210), False,
                      [tail_top, tail_mid, tail_bot], 3)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Loose Trinity Cluster
# Research:
#   https://www.chinese-showcase.com/blogs/chinese-symbols/auspicious-clouds-pattern-xiangyun-meaning-symbolism-spiritual-significance
#   https://www.dunhuang.ds.lib.uw.edu/mogao-cave-321-early-tang-dynasty/
#
# Three Ruyi lobes drifting as separate bodies in a loose constellation
# — explicitly NOT joined into one silhouette. Mogao Cave 321's Tang
# Buddhas riding on "auspicious clouds" shows discrete cloud forms
# floating apart; this candidate breaks the round-23 connected stack
# into three independent shapes that the eye groups as a phrase.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_trinity(surf, x, y, palette, scale=1.0):
    """One lead Ruyi heart + two trailing flying-white wisps."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    # Wider footprint than round-23 (96 vs 72) but emptier interior —
    # the lead heart anchors the right side and the two wisps drift
    # back to the left like flying-white ink dabs trailing the body.
    w = int(96 * scale)
    h = int(52 * scale)
    pad = 10
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Lead Ruyi heart — radius 1.6× the round-23 base (h*0.30 → h*0.34)
    # so it dominates and reads as the constellation's "subject". The
    # two wisp anchors sit at 0.7× radius equivalent — but they're drawn
    # as wisp dabs, not full lobes.
    base_r = int(h * 0.30)
    lead_r = max(6, int(base_r * 1.05))
    lead_cx = pad + int(w * 0.78)
    lead_cy = cy + int(h * 0.05)
    wisp_pts = (
        (pad + int(w * 0.20), cy - int(h * 0.18), max(3, int(base_r * 0.55))),
        (pad + int(w * 0.45), cy + int(h * 0.20), max(3, int(base_r * 0.60))),
    )
    # Per-lobe y jitter so the constellation looks hand-placed.
    wisp_pts = tuple(
        (lx, ly + _seeded_jit(x, y, i + 1, int(h * 0.04)), lr)
        for i, (lx, ly, lr) in enumerate(wisp_pts)
    )

    # Wisp dabs FIRST so the lead heart sits cleanly on top — flying-
    # white technique borrowed from the sumi-e variant so the trio
    # reads as "Ruyi + breath-trail" rather than "three same circles".
    for i, (lx, ly, lr) in enumerate(wisp_pts):
        seed = (int(x) * 17 + int(y) * 31 + i * 211) & 0x3FF
        _wisp_dab(s, lx, ly, lr, body, edge, seed, n=4)

    # Lead Ruyi heart — drop-shadow gated at night per cross-cutting A.
    if not night:
        pygame.draw.circle(s, (*edge, 38),
                           (lead_cx + 1, lead_cy + 3), lead_r + 2)
    _ruyi_heart(s, lead_cx, lead_cy, lead_r, body, edge, lit,
                body_a=246, key_a=170, lit_arc=True)

    # Mirrored arc-keyline on the leftmost wisp — gives the constellation
    # rotation (the AD called the round-1 lobes "stamped"). The arc spans
    # 160°→320° instead of the canonical 200°→340°, so it bends the
    # opposite way to the lead heart's flanking keylines.
    wx, wy, wr = wisp_pts[0]
    arc_r = max(3, wr + 2)
    pygame.draw.arc(
        s, (*edge, 150),
        pygame.Rect(wx - arc_r, wy - arc_r, arc_r * 2, arc_r * 2),
        math.radians(160), math.radians(320), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Sumi-e Ink Brush Ruyi
# Research:
#   https://www.asianbrushpainter.com/blogs/kb/the-use-of-ink
#   https://www.shimizuart.org/post/sumi-e-the-art-of-ink-wash-painting
#
# Pure ink-wash Ruyi: NO outline keyline, NO closed arc. The lobes are
# soft alpha-gradient blobs and the ruyi-coil suggestion comes from a
# single calligraphic dry-brush flying-white (kasure) line draped over
# the top. Most atmospheric of the eight — barely-there Ruyi.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_sumie(surf, x, y, palette, scale=1.0):
    """Wet-ink Ruyi blobs with one flying-white coil — no closed outline."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    w = int(80 * scale)
    h = int(40 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # 3 soft wet-ink blobs, each painted as stacked alpha discs so the
    # edge dissolves into the sky instead of stopping at a hard
    # circumference. No keyline — sumi-e Ruyi is read purely from
    # silhouette mass and the dry-brush gesture on top.
    blob_centres = (
        (pad + int(w * 0.28), cy + 2, int(h * 0.30)),
        (pad + int(w * 0.55), cy - 5, int(h * 0.34)),
        (pad + int(w * 0.80), cy + 1, int(h * 0.30)),
    )
    for (bx, by, br) in blob_centres:
        for ring in range(4):
            rr = br + ring * 2
            # Inner ring alpha bumped 200→230 per AD round-2: round-1
            # body washed out to grey at DAY / GOLDEN. The outer rings
            # still fade so the soft-edge sumi-e read survives.
            a = max(0, (230 if ring == 0 else 200) - ring * 55)
            pygame.draw.circle(s, (*body, a), (bx, by), rr)

    # Faint double-lobe heart silhouette suggestion under the dominant
    # central blob — a low-alpha bridging ellipse between the central
    # and right blobs so the silhouette mass implies the Ruyi heart
    # without re-introducing a closed keyline (per AD round-2 D).
    bx_c, by_c, br_c = blob_centres[1]
    bx_r, by_r, br_r = blob_centres[2]
    bridge_x = (bx_c + bx_r) // 2
    bridge_y = (by_c + by_r) // 2 + 2
    bridge_w = abs(bx_r - bx_c) + 4
    bridge_h = max(3, int(br_c * 0.75))
    pygame.draw.ellipse(
        s, (*body, 150),
        pygame.Rect(bridge_x - bridge_w // 2, bridge_y - bridge_h // 2,
                    bridge_w, bridge_h))

    # Flying-white coil drape — short broken segments tracing a flat
    # ruyi-curl. Each segment is a stubby ellipse with alpha randomly
    # punched out to suggest dry-brush bristle gaps. Matches the
    # kasure technique from the research source above.
    coil_pts = []
    for k in range(20):
        t = k / 19
        # Coil arcs over the central blob then dips into the right
        # blob — the Ruyi "S" gesture distilled to a single stroke.
        coil_x = pad + int(w * (0.18 + 0.65 * t))
        coil_y = cy - int(h * 0.18) + int(math.sin(t * math.pi * 1.2) * h * 0.16)
        coil_pts.append((coil_x, coil_y))
    # Edge alpha cap at 90 per AD round-2 — sunset's warm horizon
    # pushed the edge tint into bright yellow on round-1, breaking the
    # ink-wash read.
    edge_a_cap = 90
    for k, (px, py) in enumerate(coil_pts):
        seed = (int(x) ^ (int(y) << 1) ^ (k * 7919)) & 0xFF
        # Skip ~30% of dabs entirely so the line breaks irregularly —
        # this is what makes it read as flying-white, not a dotted ruler.
        if seed > 180:
            continue
        rr = max(1, int(scale * (1.5 + (seed & 3) * 0.4)))
        a = int(_lerp(110, 220, k / 19))
        a = min(a, edge_a_cap + 130)
        pygame.draw.circle(s, (*edge, min(a, 220)), (px, py), rr)

    # One soft warm rim where the central blob meets the dry-brush
    # coil — picks up sunset/golden light without re-introducing a
    # closed keyline. Alpha dropped 180→100 at night so the rim doesn't
    # read as fish-eyes against the deep-blue sky (AD round-2).
    bx, by, br = blob_centres[1]
    pygame.draw.arc(
        s, (*lit, 100 if night else 180),
        pygame.Rect(bx - br + 2, by - br - 1,
                    max(4, br * 2 - 4), max(4, br + 4)),
        math.radians(200), math.radians(340), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Goryeo Cloud-Crane Carve
# Research:
#   https://smarthistory.org/maebyeong-with-cloud-and-crane-design/
#   https://en.wikipedia.org/wiki/Snow_Ruyi_National_Ski_Jumping_Centre
#
# Round-1 jade-craquelure read as hair-noise speckle at thumbnail and
# the mossy green fought the sky. RE-ROLL: strip the concept to a SINGLE
# heavy cloud-shape body (double-lobe heart in profile) with one carved
# arc suggesting a crane's wing curving up over the top edge. Palette
# moves from mossy-jade to soft celadon-blue-grey that sits ON the sky
# rather than fighting it. Heavy 2 px outline keyline carries the
# silhouette at thumbnail — same Maebyeong cloud-crane lineage as
# round 1, stripped to silhouette-only.
# ─────────────────────────────────────────────────────────────────────────────

def _mix(a, b, t: float):
    # Local palette blend used by the celadon + eclipse variants below
    # so their colour-mix expressions match the AD's verbatim spec.
    return (
        int(a[0] * (1 - t) + b[0] * t),
        int(a[1] * (1 - t) + b[1] * t),
        int(a[2] * (1 - t) + b[2] * t),
    )


def draw_ruyi_celadon(surf, x, y, palette, scale=1.0):
    """Goryeo cloud-crane carve — heart silhouette with crane-wing arc."""
    body_base = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    stone_light = palette.get('stone_light', body_base)
    stone_dark = palette.get('stone_dark', edge)
    foliage_top = palette.get('foliage_top', body_base)
    sky_top = palette['sky_top']
    horizon = palette['horizon']

    # Soft celadon-blue-grey body — sits ON the sky band instead of
    # fighting it (round-1 jade was the failure mode). AD's verbatim
    # mix recipe.
    body_celadon = _mix(stone_light, sky_top, 0.55)
    # Wing-arc highlight ONLY — slightly green-shifted so the crane's
    # wing reads as the lit edge of a glaze ridge.
    wing_hi = _mix(foliage_top, horizon, 0.4)
    # Heavy keyline ink — survives thumbnail. Mix recipe per AD spec.
    keyline = _mix(stone_dark, horizon, 0.4)

    head_r = int(15 * scale)
    pad = int(head_r * 2) + 8
    s = _alpha_surf(pad * 2 + head_r * 3, pad * 2 + head_r * 3)
    cx = s.get_width() // 2
    cy = s.get_height() // 2

    # Drop-shadow gated at night per cross-cutting A.
    if not night:
        pygame.draw.circle(s, (*edge, 40), (cx + 2, cy + 3), head_r + 2)

    # Single heavy cloud-shape body — heart silhouette in profile.
    # Drawn via the canonical _ruyi_heart helper but tinted in celadon
    # blue-grey, with the keyline drawn afterwards as the heavy outline.
    _ruyi_heart(s, cx, cy, head_r, body_celadon, keyline, lit,
                body_a=240, key_a=210, lit_arc=False)

    # Heavy 2 px outline keyline tracing the heart silhouette so the
    # form survives at thumbnail. Round-1 had no continuous keyline; the
    # AD called the speckle-craquelure a hair-noise read. Here we draw
    # the silhouette outline as two arcs flanking the heart's twin
    # half-lobes (the canonical Ruyi double-curl) so the silhouette
    # reads even when the body alpha bleeds into a similar sky tone.
    off = max(2, int(head_r * 0.55))
    lr = max(3, int(head_r * 0.78))
    lcy = cy - max(1, int(head_r * 0.10))
    pygame.draw.arc(
        s, (*keyline, 230),
        pygame.Rect(cx - off - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(180), math.radians(360), 2)
    pygame.draw.arc(
        s, (*keyline, 230),
        pygame.Rect(cx + off - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(180), math.radians(360), 2)

    # Carved crane-wing arc curving up and over the top edge — the
    # single carved detail of the Maebyeong cloud-crane motif, stripped
    # to one stroke. Painted in the wing-arc highlight ONLY (AD spec).
    wing_r = int(head_r * 1.15)
    pygame.draw.arc(
        s, (*wing_hi, 220),
        pygame.Rect(cx - wing_r, lcy - lr - int(head_r * 0.55),
                    wing_r * 2, wing_r),
        math.radians(200), math.radians(340), 2)
    # Crane-wing tail flick — single short stroke at the wing's right
    # tip so the eye reads "wing folding over body" rather than "second
    # rim". Directional cue per cross-cutting D.
    wing_tip = (cx + wing_r - 2, lcy - lr - int(head_r * 0.05))
    wing_curl = (cx + wing_r + 3, lcy - lr + int(head_r * 0.25))
    pygame.draw.line(s, (*wing_hi, 200), wing_tip, wing_curl, 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 6 — Dragon-Coil Long-Form
# Research:
#   https://asia.si.edu/explore-art-culture/collections/search/edanmdm:fsg_S1991.142/
#   https://www.suembroidery.com/chinese-silk-embroidery-blog/chinese-silk-embroidery-patterns-and-symbolisms
#
# Chinese imperial dragon-cloud robe motif: elongated horizontal Ruyi-
# bodied silhouette suggesting a dragon's body coiling through the sky.
# 120 × 18 px aspect — by far the longest of the eight, and the
# strongest sparseness answer to "too packed" because the mass spreads
# horizontally across 3× the round-23 footprint.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_dragon(surf, x, y, palette, scale=1.0):
    """Long horizontal Ruyi-spine dragon-cloud — 120 × 18 px aspect."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    # Body length trimmed 120 → 102 (-15%) per AD round-3: at 1× the
    # 120 px form ate more sky than the spacing budget allows for a
    # 3-cloud parallax band. Head 0.95×h and tail 0.35×h ratios held
    # constant, sine period stays at π * 1.4 — only the horizontal
    # footprint shrinks.
    length = int(102 * scale)
    h = int(20 * scale)
    pad = 8
    s = _alpha_surf(length + pad * 2, h * 3 + pad * 2)
    cx = pad + length // 2
    cy = s.get_height() // 2

    # Sine period dropped 2.2π → 1.4π per AD round-2 — round-1 zig-zag
    # read as a pufferfish at NIGHT. Undulation now reads as a single
    # gentle dragon coil rather than two compressed peaks.
    sine_period = math.pi * 1.4

    # Spine — soft horizontal body painted as stacked low-alpha
    # ellipses with a gentle sinusoidal undulation, mimicking a dragon's
    # coil from imperial robe motifs. The spine is what carries the
    # "elongated Ruyi" read; the lobes punctuate.
    spine_n = 14
    for i in range(spine_n):
        t = i / (spine_n - 1)
        sx = pad + int(t * length)
        sy = cy + int(math.sin(t * sine_period) * h * 0.45)
        sw = max(4, int(h * 1.4 * (1 - abs(t - 0.5))))
        sh = max(2, h - 2)
        a = int(_lerp(160, 220, 1 - abs(t - 0.5) * 2))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(sx - sw // 2, sy - sh // 2, sw, sh))

    # Three Ruyi-lobe punctuation points along the spine: tail (left),
    # mid-coil, head (right). Head pushed to 0.95× h, tail dropped to
    # 0.35× h per AD round-2 — round-1 lobes were too uniform and the
    # dragon had no head/tail directionality. The eye now reads the
    # body as flowing left-to-right with the head at the right edge.
    spine_pts = (
        (pad + int(length * 0.10), cy + int(math.sin(0.10 * sine_period) * h * 0.45), int(h * 0.35)),
        (pad + int(length * 0.50), cy + int(math.sin(0.50 * sine_period) * h * 0.45), int(h * 0.55)),
        (pad + int(length * 0.88), cy + int(math.sin(0.88 * sine_period) * h * 0.45), int(h * 0.95)),
    )
    for i, (lx, ly, lr) in enumerate(spine_pts):
        _ruyi_lobe(s, lx, ly, lr, body, edge, lit,
                   body_a=240, key_a=150, lit_arc=(i == 2))

    # Curling tail-tip Ruyi inner-curl on the rightmost (head) lobe —
    # small spiral arc tracing 180°→20° outside the head lobe so the
    # dragon's flick reads as "tail of breath" coming off the leading
    # edge. AD round-2: directional cue at distance.
    hx, hy, hr = spine_pts[2]
    curl_r = max(3, int(hr * 0.55))
    curl_cx = hx + hr - 1
    curl_cy = hy - int(hr * 0.20)
    pygame.draw.arc(
        s, (*edge, 200),
        pygame.Rect(curl_cx - curl_r, curl_cy - curl_r,
                    curl_r * 2, curl_r * 2),
        math.radians(40), math.radians(280), 1)

    # Ink-shadow undertow — single very thin long ellipse beneath the
    # spine. Gated at night per cross-cutting A: deep-blue night sky
    # turns the dark undertow into a smudge halo. Day/golden keep the
    # shadow for body-depth read.
    if not night:
        pygame.draw.ellipse(
            s, (*edge, 50),
            pygame.Rect(pad + 4, cy + h // 2, length - 8, max(2, h // 3)))

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 7 — Tang Mandala Crest (denser contrast option)
# Research:
#   https://www.dunhuang.ds.lib.uw.edu/mogao-cave-321-early-tang-dynasty/
#   https://www.dunhuang.ds.lib.uw.edu/mogao-cave-420-sui-dynasty/
#
# Dunhuang Tang-dynasty caisson-ceiling cloud canopy: dense radial
# mandala of 5–7 lobes in concentric tiers, often painted as the
# "rotating canopy-like caisson" mentioned in Mogao Cave 420. This is
# the intentional denser-direction control: lets the user see that
# packing MORE into a Ruyi silhouette pushes it further into
# decorative-decal territory, validating the sparser candidates.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_mandala(surf, x, y, palette, scale=1.0):
    """Radial 6-lobe Tang caisson cloud — the denser contrast direction."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(78 * scale)
    h = int(56 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Inner tier — 1 large central lobe.
    centre_r = int(h * 0.22)
    pygame.draw.circle(s, (*edge, 50), (cx + 1, cy + 2), centre_r + 1)

    # Outer tier — 6 satellite lobes in a hexagonal mandala arrangement.
    # The radial layout is what gives the variant its Tang caisson read;
    # exactly six lobes matches the most common Mogao panel.
    outer_r = int(h * 0.16)
    ring_radius = int(h * 0.36)
    for k in range(6):
        ang = (k / 6) * math.tau - math.pi / 2
        ox = cx + int(math.cos(ang) * ring_radius)
        oy = cy + int(math.sin(ang) * ring_radius * 0.78)
        pygame.draw.circle(s, (*edge, 38), (ox + 1, oy + 2), outer_r + 1)
        _ruyi_lobe(s, ox, oy, outer_r, body, edge, lit,
                   body_a=235, key_a=145, lit_arc=False)

    # Centre lobe drawn LAST so it sits on top of the satellite-lobe
    # arc keylines that would otherwise overlap into the middle.
    _ruyi_lobe(s, cx, cy, centre_r, body, edge, lit,
               body_a=250, key_a=180, lit_arc=True)

    # Connecting ring keyline — single thin elliptical arc tying the
    # mandala together, painted at low alpha so it whispers rather than
    # rules the silhouette into a flat badge.
    pygame.draw.ellipse(
        s, (*edge, 90),
        pygame.Rect(cx - ring_radius - 4, cy - int(ring_radius * 0.78) - 3,
                    (ring_radius + 4) * 2, int(ring_radius * 0.78 * 2) + 6),
        1)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 8 — Ruyi Eclipse
# Research:
#   https://en.wikipedia.org/wiki/Snow_Ruyi_National_Ski_Jumping_Centre
#   https://www.olympics.com/en/news/beijing-2022-unveils-official-emblems
#
# Round-1 Art-Deco bands clipped invisible at thumbnail and the bare
# silhouette read as plain shaded circles. RE-ROLL: two Ruyi heart-lobes
# stacked vertically, one body, one shadow — the "eclipse" idea is a
# hard half-light / half-shadow contrast across ONE silhouette. The
# Beijing-2022 Snow-Ruyi lineage carries through the hard outline + the
# two-tone divide, not through horizontal bands. Geometric clarity by
# silhouette-shading only.
# ─────────────────────────────────────────────────────────────────────────────

def draw_ruyi_deco(surf, x, y, palette, scale=1.0):
    """Ruyi Eclipse — heart silhouette with hard half-light / half-shadow split."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)
    night = _is_night(palette)

    stone_dark = palette.get('stone_dark', edge)
    horizon = palette['horizon']
    sky_top = palette['sky_top']

    # Two-tone body palette per AD spec.
    body_lit = _cloud_body_color(palette)
    # Cool shadow — pulled toward stone_dark + horizon so the dark half
    # reads as a single graphic shadow, not a generic grey.
    body_shadow = _mix(stone_dark, horizon, 0.55)
    # Single hard 3 px outline keyline — heavy chevron-rim per AD spec.
    keyline = _mix(stone_dark, sky_top, 0.4)

    head_r = int(15 * scale)
    pad = int(head_r * 2) + 8
    s = _alpha_surf(pad * 2 + head_r * 3, pad * 2 + head_r * 3)
    cx = s.get_width() // 2
    cy = s.get_height() // 2

    # Drop-shadow gated at night per cross-cutting A.
    if not night:
        pygame.draw.circle(s, (*edge, 40), (cx + 2, cy + 3), head_r + 2)

    # Eclipse split — upper/left half of the heart is lit, lower/right
    # half is shadow. Implemented by drawing the heart fully in the lit
    # tone, then over-painting a half-disc shadow on the same heart's
    # twin-lobe layout. The split is the design's geometric clarity.
    _ruyi_heart(s, cx, cy, head_r, body_lit, keyline, lit,
                body_a=240, key_a=210, lit_arc=False)

    # Shadow overlay — paint the shadow tone onto the heart's right /
    # lower flank. Done by drawing two filled half-circles (right halves
    # of each twin lobe) at alpha 200, so the rest of the body shows
    # through as the lit half. This is the "eclipse" hard divide.
    off = max(2, int(head_r * 0.55))
    lr = max(3, int(head_r * 0.78))
    lcy = cy - max(1, int(head_r * 0.10))
    for half_cx, ang_a, ang_b in (
        (cx - off, math.radians(340), math.radians(160)),
        (cx + off, math.radians(340), math.radians(160)),
    ):
        # Filled right-half arc emulated by stacking thin pie-slice
        # lines from centre. Cheap and silhouette-clipped because the
        # heart body already exists under it.
        for k in range(lr):
            t = (k + 1) / (lr + 1)
            seg_r = int(lr * t)
            pygame.draw.arc(
                s, (*body_shadow, 200),
                pygame.Rect(half_cx - seg_r, lcy - seg_r,
                            seg_r * 2, seg_r * 2),
                ang_a, ang_b, 2)

    # Heavy 3 px outline keyline running the entire heart silhouette —
    # survives at all scales (AD spec). Two arcs flanking the twin
    # lobes so the keyline traces the canonical Ruyi double-curl
    # rather than a flat circle outline.
    pygame.draw.arc(
        s, (*keyline, 240),
        pygame.Rect(cx - off - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(180), math.radians(360), 3)
    pygame.draw.arc(
        s, (*keyline, 240),
        pygame.Rect(cx + off - lr, lcy - lr, lr * 2, lr * 2),
        math.radians(180), math.radians(360), 3)
    # Bottom V-curve of the heart — single arc joining the two lobes'
    # base curves so the silhouette reads as one continuous chevron.
    pygame.draw.arc(
        s, (*keyline, 240),
        pygame.Rect(cx - off - lr // 2, lcy - 2,
                    (off + lr // 2) * 2, lr + 4),
        math.radians(20), math.radians(160), 3)

    # Single warm rim accent along the lit half so the eclipse split
    # doesn't go flat-graphic. Directional cue per cross-cutting D —
    # the lit side of the eclipse always sits on the upper-left flank.
    pygame.draw.arc(
        s, (*lit, 200),
        pygame.Rect(cx - off - lr + 1, lcy - lr + 1,
                    lr * 2 - 2, lr * 2 - 2),
        math.radians(180), math.radians(280), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ── registries ───────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_ruyi_streamer,
    2: draw_ruyi_sovereign,
    3: draw_ruyi_trinity,
    4: draw_ruyi_sumie,
    5: draw_ruyi_celadon,
    6: draw_ruyi_dragon,
    7: draw_ruyi_mandala,
    8: draw_ruyi_deco,
}

VARIANT_NAMES = {
    1: "Trailing Ribbon Streamer",
    2: "Single Sovereign Lobe",
    3: "Loose Trinity Cluster",
    4: "Sumi-e Ink Brush Ruyi",
    5: "Goryeo Cloud-Crane Carve",
    6: "Dragon-Coil Long-Form",
    7: "Tang Mandala Crest",
    8: "Ruyi Eclipse",
}

VARIANT_SOURCES = {
    1: "yankodesign.com 2008 Olympic 'Cloud of Promise' torch",
    2: "wikipedia.org/wiki/Ruyi_(scepter) + pagodared.com ruyi/lingzhi",
    3: "dunhuang.ds.lib.uw.edu Mogao Cave 321 Early Tang clouds",
    4: "asianbrushpainter.com flying-white kasure ink technique",
    5: "smarthistory.org Goryeo maebyeong cloud-and-crane (silhouette-only)",
    6: "asia.si.edu palace hanging embroidered dragon-and-lotus",
    7: "dunhuang.ds.lib.uw.edu Mogao Cave 420 rotating caisson canopy",
    8: "wikipedia.org Snow Ruyi Zhangjiakou + Beijing 2022 emblem",
}
