"""Exploration renderer for the dice-results celebration popup.

The clown's floating die settles on a roll N (10..25 pagodas) or a special
GHOST outcome, and a festive popup announces it. This script draws the locked
Ribbon Banner direction at its TRUE on-screen size (the popup is ~264 design px
wide on the 360 canvas), composited over the appropriate sky swatch, with a
small actual-size inset per cell so real small-screen legibility is judged
honestly — no flattering zoom-only cells.

Round 3 bakes the production hero: the Ribbon Banner (lime body, big cream
number, "PAGODAS" on a plum plate, gold star toppers, plum keyline halo) WITH
the plum/lime/gold confetti pop-in on by default. Confetti is held strictly
OUTSIDE the banner outline so nothing crosses the keyline or the star toppers.
The GHOST sibling is the same silhouette re-skinned to a lifted navy body and
is proven on a night biome swatch, not just day.

Run (headless):
    python tools/render_dice_celebration.py
Writes docs/dice_results/round_3.png.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import hud  # vendored bold TTF + cache

# Real canvas width — the popup is centred on a 360-wide portrait canvas.
W = 360
# Day-sky keyframe (game/biome.py): bright cyan top → pale bottom.
SKY_TOP = (40, 110, 200)
SKY_BOT = (170, 220, 245)
# Night keyframe (game/biome.py NIGHT): deep blue top → cool mid.
NIGHT_TOP = (5, 8, 30)
NIGHT_BOT = (35, 55, 115)

# Hero clown "Plum & Lime" palette (from the brief).
PLUM = (96, 44, 150)
PLUM_DK = (66, 28, 110)
LIME = (132, 218, 116)
GOLD = (250, 205, 72)
CREAM = (255, 248, 224)
# GHOST sibling re-skin: same silhouette, lifted navy body so the number plate
# keeps depth but the body holds its own value against a near-black night sky.
NAVY = (50, 34, 96)
NAVY_LT = (74, 52, 122)


def sky_tile(w, h, top=SKY_TOP, bot=SKY_BOT, lo=0.35, hi=0.80):
    """A representative sky background. The popup sits high (cy~152) where the
    gradient is still bright on day; we sample a mid-band of the full-screen
    gradient rather than the very top. Pass the night keyframe for the GHOST
    proof shot."""
    s = pygame.Surface((w, h))
    for y in range(h):
        t = lo + (hi - lo) * (y / max(1, h - 1))
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (w, y))
    return s


def _num_block(canvas, c, ncy, roll, ss, size=88, num_col=CREAM, edge_col=PLUM,
               shadow_a=110, edge_w=5):
    """The hero number — vendored bold font with a soft drop shadow + thick
    plum outline ring. The outline is stroked as a fine-step ring at a modest
    offset and the cream fill is re-stamped LAST, so the digit counters (the
    holes in 2/8/0) stay open instead of clogging with edge ink at true 264px.
    edge_w is ~1px thicker than round 2 to read as a deliberate frame."""
    nf = hud._font(int(size * ss), True)
    num = nf.render(str(roll), True, num_col)
    edge = nf.render(str(roll), True, edge_col)
    shadow = nf.render(str(roll), True, (0, 0, 0))
    shadow.set_alpha(shadow_a)
    canvas.blit(shadow, shadow.get_rect(center=(c + 3 * ss, ncy + 5 * ss)))
    o = edge_w * ss
    # Fine angular step keeps the stroke even (no scalloped gaps) while a single
    # ring radius avoids stacking offset glyphs across the counters.
    for ang in range(0, 360, 15):
        ox = math.cos(math.radians(ang)) * o
        oy = math.sin(math.radians(ang)) * o
        canvas.blit(edge, edge.get_rect(center=(c + ox, ncy + oy)))
    # Re-stamp the cream fill on top so the counters read open, not inked-in.
    nb = num.get_rect(center=(c, ncy))
    canvas.blit(num, nb)
    return nb


def _label_plate(canvas, c, cy, txt, ss, plate_col, text_col, edge_col,
                 size=27, track=True, pad_x=18, pad_y=7, plate_alpha=255):
    """Seat the label on a rounded plate so it never drops out against the sky,
    with the same cream/outline lettering as the number for one read."""
    lf = hud._font(int(size * ss), True)
    spaced = " ".join(txt) if track else txt
    lab = lf.render(spaced, True, text_col)
    pw = lab.get_width() + int(pad_x * 2 * ss)
    ph = lab.get_height() + int(pad_y * 2 * ss)
    plate = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pc = plate_col + (plate_alpha,) if len(plate_col) == 3 else plate_col
    pygame.draw.rect(plate, pc, plate.get_rect(), border_radius=int(ph * 0.5))
    pygame.draw.rect(plate, GOLD + (180,), plate.get_rect(),
                     width=max(1, 2 * ss), border_radius=int(ph * 0.5))
    pr = plate.get_rect(center=(c, cy))
    canvas.blit(plate, pr)
    # Thin outline under the lettering for crisp edges on the plate.
    edge = lf.render(spaced, True, edge_col)
    for ox, oy in ((-ss, 0), (ss, 0), (0, -ss), (0, ss)):
        canvas.blit(edge, edge.get_rect(center=(c + ox, cy + oy)))
    canvas.blit(lab, lab.get_rect(center=(c, cy)))
    return pr


def _star(canvas, cx, cy, r, fill, edge, ss, points=5):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / points
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(canvas, edge, pts)
    inner = [(cx + (px - cx) * 0.82, cy + (py - cy) * 0.82) for px, py in pts]
    pygame.draw.polygon(canvas, fill, inner)


def _banner_geom(c, ss):
    """Banner placard bounds, shared so the confetti layer can keep clear of the
    silhouette (tails + star toppers + keyline halo) by computing the same box
    the body draws."""
    HD = 264 * ss
    bw, bh = int(HD * 0.74), int(HD * 0.50)
    bx, by = c - bw // 2, c - bh // 2
    return bx, by, bw, bh


def _confetti_layer(canvas, c, ss, keepout, spread=0.50, n=24):
    """Recoloured (plum/lime/gold) pop-in confetti burst FX — diamonds, dots and
    short streamers radiating out around the frame so the ease-out-back scale
    gets its juice. Every particle is rejected if it falls inside `keepout`
    (the banner silhouette + star toppers), so nothing crosses the keyline or a
    star — the burst reads as a halo OUTSIDE the banner, not litter on top."""
    HD = canvas.get_width()
    pal = [GOLD, LIME, PLUM, CREAM, GOLD, LIME]

    def clear(px, py, margin):
        # margin grows the keep-out so a streamer's whole stroke (not just its
        # endpoints) stays off the banner.
        return not keepout(px, py, margin)

    # Short streamer curls, only those whose every sample clears the banner.
    for i in range(12):
        a = i * math.tau / 12 + 0.30
        r0 = HD * 0.34
        r1 = HD * spread + (i % 3) * 7 * ss
        col = pal[i % len(pal)]
        pts = []
        ok = True
        for t in range(6):
            tt = t / 5
            r = r0 + (r1 - r0) * tt
            aa = a + math.sin(tt * 3.0 + i) * 0.16
            px = c + math.cos(aa) * r
            py = c + math.sin(aa) * r * 0.92
            if not clear(px, py, 7 * ss):
                ok = False
                break
            pts.append((px, py))
        if ok and len(pts) > 1:
            pygame.draw.lines(canvas, col, False, pts, max(2, 3 * ss))
    # Diamonds + dots scattered along the burst front.
    for i in range(n):
        a = i * math.tau / n + 0.5
        dist = HD * 0.34 + (i * 37 % 110) / 110 * HD * 0.15
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist * 0.92
        if not clear(px, py, 6 * ss):
            continue
        col = pal[i % len(pal)]
        if i % 2 == 0:
            sz = (5 + i % 3 * 2) * ss
            d = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.polygon(d, col + (235,), [(sz // 2, 0), (sz, sz // 2),
                                                  (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 47) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), 3 * ss + i % 2 * ss)


def _banner_body(canvas, c, ss, body_col, frame_col, tail_col, gloss_a=39,
                 outer_rim=None):
    """Shared ribbon-banner silhouette: flared plum ribbon tails behind a
    rounded placard with a rolled plum frame, a soft gold inner keyline, a glossy
    top sheen, and gold star toppers. The normal roll and the GHOST sibling are
    two skins of THIS one shape — only the body/tail colours differ.

    gloss_a is dimmed from round 2 so the top bevel highlight is no longer the
    brightest value on the popup — the cream NUMBER owns the focal peak.

    outer_rim (RGB or None): an extra hairline drawn OUTSIDE the plum frame. The
    GHOST passes GOLD here so the silhouette holds against a near-black night sky
    where plum-on-navy alone has almost no edge contrast."""
    HD = canvas.get_width()
    bw, bh = int(HD * 0.74), int(HD * 0.50)
    bx, by = c - bw // 2, c - bh // 2

    tail_w = int(HD * 0.19)
    for sgn in (-1, 1):
        x0 = c + sgn * (bw // 2 - 4 * ss)
        pts = [
            (x0, by + int(bh * 0.18)),
            (x0 + sgn * tail_w, by + int(bh * 0.05)),
            (x0 + sgn * tail_w * 0.7, by + bh // 2),
            (x0 + sgn * tail_w, by + int(bh * 0.95)),
            (x0, by + int(bh * 0.82)),
        ]
        pygame.draw.polygon(canvas, tail_col, pts)

    rad = int(20 * ss)
    halo_w = 8 * ss
    # Optional outer rim (GHOST): a gold hairline just beyond the plum frame.
    if outer_rim is not None:
        pygame.draw.rect(canvas, outer_rim,
                         (bx - halo_w - 3 * ss, by - halo_w - 3 * ss,
                          bw + 2 * (halo_w + 3 * ss), bh + 2 * (halo_w + 3 * ss)),
                         border_radius=rad + halo_w + 3 * ss)
    # Plum keyline halo + rolled frame: a hard plum boundary that kills the
    # body/sky edge vibration.
    pygame.draw.rect(canvas, frame_col,
                     (bx - halo_w, by - halo_w, bw + 2 * halo_w, bh + 2 * halo_w),
                     border_radius=rad + halo_w)
    pygame.draw.rect(canvas, body_col, (bx, by, bw, bh), border_radius=rad)
    pygame.draw.rect(canvas, GOLD, (bx + 6 * ss, by + 6 * ss, bw - 12 * ss, bh - 12 * ss),
                     width=2 * ss, border_radius=rad - 4 * ss)
    gloss = pygame.Surface((bw - 12 * ss, bh // 3), pygame.SRCALPHA)
    gloss.fill((255, 255, 255, gloss_a))
    canvas.blit(gloss, (bx + 6 * ss, by + 6 * ss))
    for sx in (bx + int(bw * 0.14), bx + int(bw * 0.86)):
        _star(canvas, sx, by - 1 * ss, 11 * ss, GOLD, frame_col, ss)
    return bx, by, bw, bh


def _banner_keepout(c, ss, star_extra=0):
    """A predicate (px, py, margin) -> True if a point sits ON the banner
    silhouette: the placard + its gold-rim halo, the flared tails, and the two
    gold star toppers. Confetti uses this to stay strictly OUTSIDE the outline."""
    HD = 264 * ss
    bw, bh = int(HD * 0.74), int(HD * 0.50)
    bx, by = c - bw // 2, c - bh // 2
    halo = 8 * ss + 3 * ss  # placard + gold rim
    tail_w = int(HD * 0.19)
    star_cx = (bx + int(bw * 0.14), bx + int(bw * 0.86))
    star_cy = by - 1 * ss
    star_r = 11 * ss + star_extra

    def inside(px, py, margin):
        # Placard box (with halo + margin).
        if (bx - halo - margin <= px <= bx + bw + halo + margin and
                by - halo - margin <= py <= by + bh + halo + margin):
            return True
        # Flared tails: a band reaching out from each side at the placard's
        # vertical mid-zone.
        for sgn in (-1, 1):
            tx0 = c + sgn * (bw // 2 - 4 * ss)
            lo = min(tx0, tx0 + sgn * tail_w)
            hivx = max(tx0, tx0 + sgn * tail_w)
            if (lo - margin <= px <= hivx + margin and
                    by - margin <= py <= by + bh + margin):
                return True
        # Star toppers.
        for scx in star_cx:
            if math.hypot(px - scx, py - star_cy) <= star_r + margin:
                return True
        return False

    return inside


# ── PRODUCTION HERO: Ribbon Banner + baked confetti (normal roll) ─────────────
def var_ribbon_hero(roll, ss, confetti=True):
    """The locked production hero. Lime body, big cream number with a thickened
    plum outline and open counters, "PAGODAS" on a plum plate riding the lower
    frame, gold star toppers, plum keyline halo, dimmed top bevel. Confetti pops
    in OUTSIDE the banner outline by default; pass confetti=False for the static
    base/fallback frame."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    if confetti:
        _confetti_layer(canvas, c, ss, _banner_keepout(c, ss))
    bx, by, bw, bh = _banner_body(canvas, c, ss, LIME, PLUM, PLUM_DK)
    _num_block(canvas, c, c - int(10 * ss), roll, ss, size=96)
    _label_plate(canvas, c, by + bh + int(2 * ss), "PAGODAS", ss, PLUM, CREAM, PLUM_DK)
    return canvas, D


# ── GHOST sibling re-skin — same banner, lifted navy body + gold rim ──────────
def var_ghost_sibling(roll, ss):
    """GHOST as a SIBLING of the hero, not a new shape: the exact ribbon-banner
    silhouette re-skinned to a lifted navy/plum body, a friendly ghost mascot
    peeking centred above the panel, "GHOST!" on the same plum plate. A GOLD
    outer rim is added so the silhouette holds against night, where the navy
    body and plum frame have almost no value separation from the sky."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Ghost mascot centred above, peeking from behind the panel top edge.
    gr = int(HD * 0.115)
    gx = c
    gy = c - int(HD * 0.30)
    gw, gh = gr * 3, int(gr * 3.4)
    ghost = pygame.Surface((gw, gh), pygame.SRCALPHA)
    pygame.draw.circle(ghost, (240, 250, 255, 240), (gw // 2, gr), gr)
    pygame.draw.rect(ghost, (240, 250, 255, 240),
                     (gw // 2 - gr, gr, gr * 2, int(gr * 1.5)))
    for k in range(4):  # scalloped hem
        pygame.draw.circle(ghost, (240, 250, 255, 240),
                           (gw // 2 - gr + int(gr * (0.45 + k * 0.55)), int(gr * 2.45)),
                           int(gr * 0.32))
    # Soft body shade for volume.
    sh = pygame.Surface((gw, gh), pygame.SRCALPHA)
    pygame.draw.circle(sh, (150, 170, 210, 70), (int(gw * 0.62), int(gr * 1.2)),
                       int(gr * 0.8))
    ghost.blit(sh, (0, 0))
    for ex in (-1, 1):
        pygame.draw.circle(ghost, NAVY, (gw // 2 + ex * gr // 2, gr), gr // 4)
    # Rosy cheeks for friendliness.
    for ex in (-1, 1):
        pygame.draw.circle(ghost, (255, 170, 190, 150),
                           (gw // 2 + ex * int(gr * 0.78), int(gr * 1.35)), int(gr * 0.18))
    canvas.blit(ghost, ghost.get_rect(center=(gx, gy)))

    bx, by, bw, bh = _banner_body(canvas, c, ss, NAVY, PLUM, NAVY_LT, outer_rim=GOLD)
    _num_block(canvas, c, c - int(10 * ss), roll, ss, size=96, edge_col=PLUM)
    _label_plate(canvas, c, by + bh + int(2 * ss), "GHOST!", ss, PLUM, CREAM, PLUM_DK)
    return canvas, D


# ── 5th cell: respec'd RARE high-roll Medallion (bigger number disc) ──────────
def var_medallion_rare(roll, ss):
    """Explicitly NOT the everyday celebration — a separate RARE / high-roll
    frame. Respec'd from round 2 with a LARGER number disc (the cream field and
    the number both grow) so the rolled N stays the hero even on the busy gold
    bezel. Clean symmetric 2-sprig laurel, "PAGODAS" on a cream/plum band."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Tighter, warmer framed plum field (ring, not a flat bruise).
    field = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(field, PLUM + (235,), (c, c), int(HD * 0.42))
    pygame.draw.circle(field, GOLD + (210,), (c, c), int(HD * 0.42), max(2, 3 * ss))
    pygame.draw.circle(field, PLUM_DK + (235,), (c, c), int(HD * 0.365))
    canvas.blit(field, (0, 0))

    # Festive flecks over the field (reads "roll", not "award").
    for i in range(16):
        a = i * math.tau / 16 + 0.4
        dist = HD * 0.365 + (i % 3) * 6 * ss
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist
        col = [GOLD, LIME, CREAM][i % 3]
        if i % 2 == 0:
            sz = (5 + i % 2 * 2) * ss
            d = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.polygon(d, col + (235,),
                                [(sz // 2, 0), (sz, sz // 2), (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 51) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), 3 * ss)

    # LARGER disc so the number reads as the hero on this rare frame.
    R = int(HD * 0.315)
    for i in range(44):  # fluted bezel
        a = i * math.tau / 44
        rr = R + (6 * ss if i % 2 == 0 else 2 * ss)
        pygame.draw.line(canvas, (200, 150, 30),
                         (c + math.cos(a) * (R - 2 * ss), c + math.sin(a) * (R - 2 * ss)),
                         (c + math.cos(a) * rr, c + math.sin(a) * rr), max(2, 3 * ss))
    pygame.draw.circle(canvas, (180, 132, 28), (c, c), R)
    pygame.draw.circle(canvas, GOLD, (c, c), R - 5 * ss)
    # Bigger cream inner field so the number sits on cream, not gold.
    pygame.draw.circle(canvas, (255, 244, 212), (c, c), int(R * 0.74))
    pygame.draw.circle(canvas, PLUM, (c, c), int(R * 0.74), max(2, 2 * ss))
    # Clipped top-left specular crescent.
    hl = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, 90), (c - int(R * 0.32), c - int(R * 0.32)),
                       int(R * 0.55))
    mask = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), R - 8 * ss)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(hl, (0, 0))

    def sprig(sgn):
        base_a = math.pi * 0.5 + sgn * 0.62
        stem = []
        for t in range(7):
            tt = t / 6
            ar = base_a - sgn * tt * 0.62
            rr = (R - 9 * ss) + tt * 14 * ss
            stem.append((c + math.cos(ar) * rr, c + math.sin(ar) * rr))
        pygame.draw.lines(canvas, (70, 150, 60), False, stem, max(2, 3 * ss))
        for k, (sx, sy) in enumerate(stem):
            if k == 0:
                continue
            la = math.atan2(sy - stem[k - 1][1], sx - stem[k - 1][0])
            for side in (-1, 1):
                lw, lh = int(13 * ss), int(7 * ss)
                leaf = pygame.Surface((lw, lh), pygame.SRCALPHA)
                pygame.draw.ellipse(leaf, LIME, leaf.get_rect())
                pygame.draw.ellipse(leaf, (70, 150, 60), leaf.get_rect(), max(1, ss))
                leaf = pygame.transform.rotate(leaf, -math.degrees(la) + side * 42)
                canvas.blit(leaf, leaf.get_rect(center=(int(sx), int(sy))))
    sprig(-1)
    sprig(1)
    pygame.draw.circle(canvas, GOLD, (c, c + R + int(2 * ss)), int(6 * ss))
    pygame.draw.circle(canvas, PLUM, (c, c + R + int(2 * ss)), int(6 * ss), max(1, 2 * ss))

    # Bigger number to match the bigger disc.
    _num_block(canvas, c, c - int(12 * ss), roll, ss, size=92,
               num_col=PLUM, edge_col=CREAM, edge_w=4)
    _label_plate(canvas, c, c + int(R * 0.74) + int(14 * ss), "PAGODAS", ss,
                 CREAM, PLUM, PLUM, size=22)
    return canvas, D


VARIANTS = [
    ("1  Ribbon — PRODUCTION HERO", "lime body, baked confetti, thick num outline", "day",
     lambda r, ss: var_ribbon_hero(r, ss, confetti=True), 22),
    ("2  Ribbon — STATIC BASE", "same frame, confetti OFF (fallback)", "day",
     lambda r, ss: var_ribbon_hero(r, ss, confetti=False), 17),
    ("3  GHOST sibling — DAY", "navy re-skin proven on pale day sky", "day",
     var_ghost_sibling, 10),
    ("4  GHOST sibling — NIGHT", "PROOF: navy body + gold rim on night biome", "night",
     var_ghost_sibling, 10),
    ("5  Medallion — RARE FRAME", "respec: bigger number disc (NOT everyday)", "day",
     var_medallion_rare, 23),
]


def main():
    SS = 4  # supersample for crisp downscale to true size
    TRUE = 264   # popup is 264 design px on the 360 canvas
    INSET = 116  # actual-size inset shows the popup at ~half real size again
    cols = 3
    rows = 2
    pad = 20
    head = 64
    tile_w = TRUE + INSET + 40
    tile_h = TRUE + 96
    sheet_w = cols * tile_w + (cols + 1) * pad
    sheet_h = head + rows * tile_h + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "Dice-Results Celebration — Round 3 (Ribbon Banner baked + GHOST night proof)",
        True, (255, 255, 255)), (pad, 12))
    sheet.blit(sub_f.render(
        "True 264px size on day/night sky + actual-size inset. Cells 1/2 = hero+base, "
        "3/4 = GHOST on day vs NIGHT, 5 = rare frame.",
        True, (200, 205, 215)), (pad, 40))

    label_f = hud._font(19, True)
    samp_f = hud._font(13, True)

    for idx, (name, desc, sky, fn, roll) in enumerate(VARIANTS):
        col = idx % cols
        row = idx // cols
        tx = pad + col * (tile_w + pad)
        ty = head + pad + row * (tile_h + pad)

        if sky == "night":
            tile = sky_tile(tile_w, tile_h, NIGHT_TOP, NIGHT_BOT, lo=0.10, hi=0.55)
            chip_top, chip_bot, chip_lo, chip_hi = NIGHT_TOP, NIGHT_BOT, 0.10, 0.55
        else:
            tile = sky_tile(tile_w, tile_h)
            chip_top, chip_bot, chip_lo, chip_hi = SKY_TOP, SKY_BOT, 0.35, 0.80
        canvas, D = fn(roll, SS)

        out = pygame.transform.smoothscale(canvas, (TRUE, TRUE))
        tile.blit(out, out.get_rect(center=(16 + TRUE // 2, 36 + TRUE // 2)))

        chip = sky_tile(INSET + 16, INSET + 16, chip_top, chip_bot, chip_lo, chip_hi)
        ins = pygame.transform.smoothscale(canvas, (INSET, INSET))
        chip.blit(ins, ins.get_rect(center=((INSET + 16) // 2, (INSET + 16) // 2)))
        pygame.draw.rect(chip, (255, 255, 255), chip.get_rect(), 2)
        cr = chip.get_rect()
        cr.bottomright = (tile_w - 8, tile_h - 34)
        tile.blit(chip, cr)
        ilab = samp_f.render("actual size", True, (255, 255, 255))
        ib = pygame.Surface((ilab.get_width() + 6, ilab.get_height() + 2),
                            pygame.SRCALPHA)
        ib.fill((20, 22, 28, 200))
        ib.blit(ilab, (3, 1))
        tile.blit(ib, (cr.left, cr.top - ib.get_height() - 1))

        strip = pygame.Surface((tile_w, 30), pygame.SRCALPHA)
        strip.fill((20, 22, 28, 205))
        tile.blit(strip, (0, 0))
        tag = (255, 210, 110) if "GHOST" in name else LIME
        tile.blit(label_f.render(name, True, tag), (8, 6))
        cap = pygame.Surface((tile_w, 24), pygame.SRCALPHA)
        cap.fill((20, 22, 28, 205))
        tile.blit(cap, (0, tile_h - 24))
        tile.blit(samp_f.render(f"{desc}  (roll {roll})", True, (220, 225, 235)),
                  (8, tile_h - 21))
        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
