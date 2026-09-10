"""MARROW-SKEWER clown-event bone column — matured round-2 render.

A single gold-cored marrow-spike runs the FULL pillar height as the honest
collision spine; loose vertebra discs (with wing-process side-nubs) and the
occasional small skull are threaded onto it like beads, with VISIBLE AIR
between them. The spike emerges past the last bead as a barbed bone-point aimed
INTO the gap.

Round-2 fairness fix (the whole ballgame): the spike is now a TRUE solid bone
shaft (~9px at 58px, ~1/6 of column width) — dark ink core, ivory body, gold
thin-accent inset, continuous top-left rim-sheen — so it reads as one UNBROKEN
lethal pole from cap to cap with zero sky breaks. Backward-raked thorn-barbs sit
in the middle of each long air-gap so the spine keeps a "do not enter this lane"
read between beads. The disc fill is dropped/cooled in value so the SHAFT is the
brightest sustained mass and wins the focal read; the end-cap barb stays the
single brightest accent. Bead pitch is tightened so no span reads as a doorway,
while air still beats bead for identity.

Identity rule (the art-director's distinctness fix): continuous thin-but-solid
spike + visible (tightened) air + discrete beads. NOT a fused bone-plate slab,
NOT a stacked stupa.

Bone-roster house style: warm-ivory bone, hard 1-2px ink keyline, dark-core ->
flat-fill -> top-left rim-sheen triad, gold thin-accent tracing (the spike core
is gold), faceted cyan/purple wisdom gems, supersample -> smoothscale, plus a
1px alpha-grown silhouette outline.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import math
import pygame

pygame.init()

# ── Bone-roster palette (locked batch2 house style) ──────────────────────────
INK     = (28, 22, 30)
BONE    = (228, 222, 206)
BONE_DK = (150, 144, 128)
BONE_CORE = (108, 102, 90)          # deepest under-shade for the dark-cored read
BONE_HI = (250, 247, 236)
# Cooler/bonier disc fills, pulled ~15-20% off the bright ivory so the SHAFT
# (which keeps the bright BONE/BONE_HI values) is the brightest sustained mass.
DISC      = (190, 188, 182)
DISC_HI   = (214, 213, 207)
DISC_CORE = (96, 96, 96)
GOLD    = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
GOLD_SHADOW = (110, 78, 22)
CYAN    = (120, 214, 222)
CYAN_HI = (224, 252, 252)
PURPLE  = (158, 120, 214)
PURPLE_HI = (224, 206, 250)

PW = 58                              # PIPE_W gameplay column width
OVERHANG = 7                         # wing-process nubs may spill past the column


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


# ── The threaded hardware: a gold-cored marrow spike ─────────────────────────

def marrow_spike(surf, cx, top_y, bot_y, ss):
    """The full-height central spike the beads are threaded on. Round 2 widens it
    to a TRUE solid bone shaft (~9px at 58px) so it reads as one unbroken lethal
    pole in every air-gap, not a thin decorative thread. Full bone treatment:
    ink keyline -> dark casing -> ivory body -> continuous top-left rim-sheen,
    with the gold marrow seam inset down the spine. Drawn FIRST so beads seat
    over it; the air gaps expose this solid shaft, which is the whole read."""
    hw = int(4.5 * ss)               # shaft half-width — true ~9px solid spine

    # Hard ink keyline so the shaft holds a crisp lethal silhouette in the gaps.
    pygame.draw.line(surf, INK, (cx, top_y), (cx, bot_y), hw * 2 + int(2.4 * ss))
    # Dark bone casing (the dark-cored read along the right/under edge).
    pygame.draw.line(surf, BONE_CORE, (cx, top_y), (cx, bot_y), hw * 2)
    # Ivory body — the SHAFT carries the bright sustained value, biased left so a
    # dark core line sits to the right (cylindrical bone read).
    pygame.draw.line(surf, BONE, (cx - int(0.6 * ss), top_y),
                     (cx - int(0.6 * ss), bot_y), int(hw * 1.5))
    # The molten gold marrow core inset down the spine (thin-accent, not the mass).
    pygame.draw.line(surf, GOLD_DK, (cx + int(0.4 * ss), top_y),
                     (cx + int(0.4 * ss), bot_y), max(2, int(2.4 * ss)))
    pygame.draw.line(surf, GOLD, (cx, top_y), (cx, bot_y), max(1, int(1.5 * ss)))
    # Continuous rim-sheen running the WHOLE left edge so the pole never breaks.
    pygame.draw.line(surf, BONE_HI, (cx - int(hw * 0.7), top_y),
                     (cx - int(hw * 0.7), bot_y), max(1, int(1.3 * ss)))


def shaft_barb(surf, cx, cy, ss, side):
    """A small backward-raked bone thorn on the shaft itself, planted in the
    middle of a long air-gap. Keeps the 'do not enter this lane' read between
    beads and re-asserts the spine as the solid thing. Rim-lit silhouette barb —
    a clean hook, not detail noise. Rakes AWAY from the nearest gap end so it
    reads as a fish-hook guarding the lane."""
    hw = int(4.5 * ss)
    root_x = cx + side * hw
    # The thorn sweeps out and back (rake) — a short triangular hook.
    tip = (root_x + side * int(10 * ss), cy - int(7 * ss))   # raked back/up
    barb = [(root_x, cy - int(5 * ss)),
            tip,
            (root_x, cy + int(2 * ss))]
    pygame.draw.polygon(surf, INK,
                        [(int(x), int(y)) for x, y in barb])
    inner = [(root_x + side * int(ss), cy - int(4 * ss)),
             (tip[0] - side * int(ss), tip[1] + int(ss)),
             (root_x + side * int(ss), cy + int(ss))]
    pygame.draw.polygon(surf, BONE,
                        [(int(x), int(y)) for x, y in inner])
    # Rim-lit leading edge so the thorn reads as a lit silhouette, not a smear.
    pygame.draw.line(surf, BONE_HI,
                     (int(root_x + side * int(ss)), int(cy - int(4 * ss))),
                     (int(tip[0] - side * int(ss)), int(tip[1] + int(ss))),
                     max(1, int(1.2 * ss)))


def _bone_triad_ellipse(surf, rect, ss):
    """A vertebra disc body in the dark-core -> flat-fill -> top-left rim-sheen
    triad. Round 2 uses the COOLER/dimmer disc palette so the disc reads bonier
    and steps back behind the bright shaft."""
    pygame.draw.ellipse(surf, INK, rect.inflate(int(2 * ss), int(2 * ss)))
    pygame.draw.ellipse(surf, DISC_CORE, rect)
    # Flat ivory fill lifted off the bottom so the lower lip stays dark-cored.
    fill = rect.inflate(-int(2 * ss), -int(2 * ss))
    fill.y -= int(ss)
    pygame.draw.ellipse(surf, DISC, fill)
    # Top-left rim sheen — kept subdued vs. the shaft sheen.
    sheen = pygame.Rect(rect.x + int(4 * ss), rect.y + int(2 * ss),
                        int(rect.w * 0.5), int(rect.h * 0.42))
    pygame.draw.ellipse(surf, DISC_HI, sheen)


def vertebra_bead(surf, cx, cy, ss, *, gem_col):
    """A loose vertebra DISC threaded on the spike: a flat centrum with a pair of
    wing-process side-nubs and a faceted wisdom-gem foramen at its core. Round 2
    narrows the centrum ~12% so the column silhouette stays spine-dominant and
    the lane edges read cleaner. The gap above/below it is bare solid spike."""
    half_w = int((PW * 0.5 + OVERHANG - 6) * ss)   # ~12% narrower; spills to nubs
    half_h = int(7.5 * ss)

    # Wing-process side-nubs FIRST (behind the centrum) — the transverse processes
    # that make a vertebra read as a vertebra, not a generic bead.
    for s in (-1, 1):
        wx = cx + s * (half_w - int(3 * ss))
        nub = pygame.Rect(0, 0, int(9 * ss), int(7 * ss))
        nub.center = (wx, cy)
        pygame.draw.ellipse(surf, INK, nub.inflate(int(2 * ss), int(2 * ss)))
        pygame.draw.ellipse(surf, _shade(DISC, -28), nub)
        pygame.draw.ellipse(surf, DISC, nub.inflate(-int(3 * ss), -int(3 * ss)))
        pygame.draw.circle(surf, DISC_HI,
                           (wx - int(2 * ss), cy - int(2 * ss)), max(1, int(1.4 * ss)))

    # The flat centrum disc.
    body = pygame.Rect(0, 0, half_w * 2 - int(8 * ss), half_h * 2)
    body.center = (cx, cy)
    _bone_triad_ellipse(surf, body, ss)

    # A faint pinch-line each side reads the disc as a stacked vertebral plate.
    for s in (-1, 1):
        px = cx + s * int(half_w * 0.46)
        pygame.draw.line(surf, _shade(DISC_CORE, 18),
                         (px, cy - int(4 * ss)), (px, cy + int(4 * ss)),
                         max(1, int(ss)))

    # The neural foramen at the core: a small faceted wisdom gem the spike pierces.
    _gem(surf, cx, cy, int(4.2 * ss), ss, col=gem_col)


def skull_bead(surf, cx, cy, ss, *, eye=CYAN):
    """A small SKULL threaded on the spike — the alternate bead on the coarse
    cadence so the string never reads as a uniform disc stack. Narrower than the
    discs (skulls are round, not winged). Uses the dimmer disc palette so it,
    too, steps back behind the bright shaft."""
    r = int(10 * ss)
    # Cranium triad (cooler disc values).
    pygame.draw.circle(surf, INK, (cx, cy), r + int(ss))
    pygame.draw.circle(surf, DISC_CORE, (cx, cy), r)
    pygame.draw.circle(surf, DISC, (cx, cy - int(ss)), r - int(1.5 * ss))
    pygame.draw.circle(surf, DISC_HI, (cx - r // 3, cy - r // 3), r // 3)

    # Eye sockets cored dark with a soul-light pin so the bead reads "alive".
    for s in (-1, 1):
        ex = cx + s * int(r * 0.46)
        ey = cy - int(r * 0.18)
        pygame.draw.circle(surf, INK, (ex, ey), int(r * 0.34))
        pygame.draw.circle(surf, eye, (ex, ey), max(1, int(r * 0.2)))
        pygame.draw.circle(surf, CYAN_HI, (ex - int(ss), ey - int(ss)),
                           max(1, int(r * 0.09)))
    # Small triangular nasal aperture.
    pygame.draw.polygon(surf, INK,
                        [(cx, cy + int(r * 0.12)),
                         (cx - int(r * 0.16), cy + int(r * 0.42)),
                         (cx + int(r * 0.16), cy + int(r * 0.42))])
    # The jaw teeth — short ink ticks so the skull reads at size.
    jy = cy + int(r * 0.5)
    pygame.draw.line(surf, _shade(DISC_CORE, 24),
                     (cx - int(r * 0.5), jy), (cx + int(r * 0.5), jy),
                     max(1, int(1.4 * ss)))
    for i in range(-2, 3):
        tx = cx + i * int(r * 0.26)
        pygame.draw.line(surf, INK, (tx, jy), (tx, jy + int(r * 0.34)),
                         max(1, int(ss)))


def _gem(surf, cx, cy, r, ss, *, col):
    """A faceted wisdom gem (cyan/purple) with the ink keyline + bright glint —
    the diamond cabochon the marrow spike threads through."""
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in pts])
    inner = [(cx, cy - r + ss), (cx + r - ss, cy),
             (cx, cy + r - ss), (cx - r + ss, cy)]
    pygame.draw.polygon(surf, _shade(col, -40), [(int(x), int(y)) for x, y in inner])
    # Lit left facet so the gem reads cut, not a flat lozenge.
    pygame.draw.polygon(surf, col,
                        [(int(cx), int(cy - r + ss)), (int(cx), int(cy + r - ss)),
                         (int(cx - r + ss), int(cy))])
    pygame.draw.circle(surf, CYAN_HI if col is CYAN else PURPLE_HI,
                       (int(cx - r * 0.3), int(cy - r * 0.3)), max(1, int(r * 0.3)))


def barbed_point(surf, cx, tip_y, base_y, ss):
    """The spike emerges past the last bead as a barbed bone-point aimed INTO the
    gap — the threading hardware is the cap and the SINGLE brightest accent. A
    tapered ivory blade with two rear-swept barbs and a thin gold marrow seam."""
    hw = int(7 * ss)
    # The barbs (rear-swept hooks) at the blade root.
    for s in (-1, 1):
        barb = [(cx + s * int(2 * ss), base_y - int(10 * ss)),
                (cx + s * int(13 * ss), base_y - int(2 * ss)),
                (cx + s * int(5 * ss), base_y + int(2 * ss))]
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in barb])
        pygame.draw.polygon(surf, BONE,
                            [(int(x - s * ss), int(y)) for x, y in barb])
        pygame.draw.polygon(surf, BONE_HI,
                            [(int(cx + s * int(2 * ss)), int(base_y - int(9 * ss))),
                             (int(cx + s * int(8 * ss)), int(base_y - int(3 * ss))),
                             (int(cx + s * int(4 * ss)), int(base_y))])
    # The blade body — a long tapered triangle from base to tip.
    blade = [(cx - hw, base_y), (cx + hw, base_y), (cx, tip_y)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in blade])
    pygame.draw.polygon(surf, BONE_CORE,
                        [(int(cx - hw + ss), int(base_y)),
                         (int(cx + hw - ss), int(base_y)), (int(cx), int(tip_y))])
    pygame.draw.polygon(surf, BONE,
                        [(int(cx - hw + int(2 * ss)), int(base_y - int(ss))),
                         (int(cx + hw - int(2 * ss)), int(base_y - int(ss))),
                         (int(cx), int(tip_y + int(2 * ss)))])
    # Lit left bevel reads the point as faceted, not flat — brightest in column.
    pygame.draw.polygon(surf, BONE_HI,
                        [(int(cx - hw + int(2 * ss)), int(base_y - int(ss))),
                         (int(cx - int(ss)), int(base_y - int(ss))),
                         (int(cx), int(tip_y + int(3 * ss)))])
    # The gold marrow seam runs out to (but not through) the very tip.
    pygame.draw.line(surf, GOLD_DK, (cx, base_y), (cx, tip_y + int(5 * ss)),
                     max(1, int(1.8 * ss)))
    pygame.draw.line(surf, GOLD, (cx, base_y), (cx, tip_y + int(7 * ss)),
                     max(1, int(ss)))


# ── Cadence: alternate disc / skull with tightened air gaps ───────────────────
# A coarse 3-step pattern so the bead identity alternates legibly. Round 2 tightens
# the pitch so no single span reads as a doorway; the shaft barb in each gap (below)
# guarantees fairness while air still beats bead for the threaded identity.
BEAD_PITCH = 34                      # 1x px between bead centres (tightened)
# Pattern read top->gap: disc, skull, disc  (repeats). Wing discs and round skulls
# alternate so the silhouette rhythm reads "threaded beads", never a solid stack.
CADENCE = ("disc", "skull", "disc")


def _bead_at(surf, cx, cy, idx, ss):
    kind = CADENCE[idx % len(CADENCE)]
    if kind == "skull":
        skull_bead(surf, cx, cy, ss, eye=CYAN)
    else:
        # Discs alternate gem colour on a slow beat for a little life.
        gem_col = PURPLE if (idx // 2) % 2 else CYAN
        vertebra_bead(surf, cx, cy, ss, gem_col=gem_col)


def render_column(H, ss, *, flip):
    """Render ONE half-column `H` px tall at supersample `ss`, beads threaded down
    the solid spike with the barbed point seated at the GAP end, and a shaft barb
    planted mid-air-gap between beads. `flip` mirrors so the point can aim up
    (bottom pillar) or down (top pillar)."""
    box_w = (PW + 2 * OVERHANG) * ss
    box_h = max(1, int(H)) * ss
    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    cx = box_w // 2

    # The solid spike spans the full height (it is the spine / collision edge). It
    # stops short of the gap end where the barbed point takes over.
    point_base = box_h - int(34 * ss)
    spike_top = -int(6 * ss)         # run off the far end so tiling is seamless
    marrow_spike(surf, cx, spike_top, point_base, ss)

    # Thread beads down the spike from the far end toward the gap, on the cadence.
    pitch = int(BEAD_PITCH * ss)
    # Nearest bead just above the point base; collect centres so barbs sit between.
    y = int(box_h - 34 * ss - 16 * ss)
    centres = []
    idx = 0
    while y > int(8 * ss):
        centres.append((y, idx))
        y -= pitch
        idx += 1

    # A shaft thorn-barb in the middle of each long air-gap between beads — the
    # gap fairness tell. Side alternates so the spine reads barbed both ways.
    for i in range(len(centres) - 1):
        y0, _ = centres[i]
        y1, _ = centres[i + 1]
        mid = (y0 + y1) // 2
        shaft_barb(surf, cx, mid, ss, side=1 if i % 2 == 0 else -1)
    # Also barb the gap above the topmost bead so the run-off span isn't bare.
    if centres:
        top_y0 = centres[-1][0]
        shaft_barb(surf, cx, top_y0 - pitch // 2, ss,
                   side=-1 if (len(centres) - 1) % 2 == 0 else 1)

    # Now seat the beads OVER the shaft + barbs.
    for cy, idx in centres:
        _bead_at(surf, cx, cy, idx, ss)

    # The barbed bone-point at the gap end — the threading hardware is the cap.
    barbed_point(surf, cx, box_h - int(2 * ss), point_base, ss)

    # Supersample down with a 1px alpha-grown silhouette outline (house finish).
    small = pygame.transform.smoothscale(surf, (PW + 2 * OVERHANG, max(1, int(H))))
    small = _grow_outline(small)
    if flip:
        small = pygame.transform.flip(small, False, True)
    return small


def _grow_outline(surf):
    """Grow a 1px ink silhouette outline by alpha-dilating the sprite — the
    roster's finishing pass so the bone reads crisp against any sky."""
    w, h = surf.get_size()
    mask = pygame.mask.from_surface(surf, 8)
    outline = pygame.Surface((w, h), pygame.SRCALPHA)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        shifted = pygame.Surface((w, h), pygame.SRCALPHA)
        shifted.blit(mask.to_surface(setcolor=(*INK, 255), unsetcolor=(0, 0, 0, 0)),
                     (ox, oy))
        outline.blit(shifted, (0, 0))
    outline.blit(surf, (0, 0))
    return outline


# ── Review sheet ──────────────────────────────────────────────────────────────

def _sky(w, h, top, bot):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        s.fill((int(top[0] + (bot[0] - top[0]) * t),
                int(top[1] + (bot[1] - top[1]) * t),
                int(top[2] + (bot[2] - top[2]) * t)), (0, y, w, 1))
    return s


def _pair_on_sky(panel_w, panel_h, sky_top, sky_bot, gap_h, *, guides=False,
                 scale=1.0):
    """A top + bottom MARROW-SKEWER pair framing a gap, on a sky gradient — the
    barbed point of each half aims into the gap. Guides OFF by default (the white
    layout box masked the air-gap failure in round 1); the fairness must read on
    the bare sky alone. `scale` < 1 simulates motion/distance."""
    panel = _sky(panel_w, panel_h, sky_top, sky_bot)
    gap_top = (panel_h - gap_h) // 2
    gap_bot = gap_top + gap_h
    cx = panel_w // 2
    top = render_column(int(gap_top / scale), 4, flip=True)        # point aims DOWN
    bot = render_column(int((panel_h - gap_bot) / scale), 4, flip=False)  # aims UP
    if scale != 1.0:
        cw = max(1, int((PW + 2 * OVERHANG) * scale))
        top = pygame.transform.smoothscale(
            top, (cw, max(1, int(top.get_height() * scale))))
        bot = pygame.transform.smoothscale(
            bot, (cw, max(1, int(bot.get_height() * scale))))
        panel.blit(top, (cx - cw // 2, gap_top - top.get_height()))
        panel.blit(bot, (cx - cw // 2, gap_bot))
    else:
        cw = PW + 2 * OVERHANG
        panel.blit(top, (cx - cw // 2, 0))
        panel.blit(bot, (cx - cw // 2, gap_bot))
    if guides:
        pygame.draw.rect(panel, (255, 255, 255, 60),
                         (cx - PW // 2, 0, PW, panel_h), 1)
    return panel


def main():
    pygame.font.init()
    title_f = pygame.font.SysFont("dejavusans", 22, bold=True)
    head_f = pygame.font.SysFont("dejavusans", 15, bold=True)
    body_f = pygame.font.SysFont("dejavusans", 12)

    BG = (32, 34, 44)
    SHEET_W, SHEET_H = 980, 760
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(BG)
    sheet.blit(title_f.render("MARROW-SKEWER  —  clown-event bone column  —  round 2",
                              True, (255, 255, 255)), (20, 14))
    sheet.blit(body_f.render(
        "FAIRNESS FIX: the gold-cored spike is now a TRUE solid ~9px bone shaft — "
        "one unbroken lethal pole, no sky breaks.  Shaft thorn-barbs guard every "
        "air-gap; discs dimmed/cooled so the spine wins the focal read.",
        True, (206, 208, 218)), (20, 42))

    # The contract panels: true 58px, GUIDES OFF, on day + night sky.
    PANEL_W, PANEL_H = 230, 580
    GAP_H = 150
    day = _pair_on_sky(PANEL_W, PANEL_H, (150, 205, 235), (210, 235, 245), GAP_H)
    night = _pair_on_sky(PANEL_W, PANEL_H, (20, 26, 52), (40, 30, 64), GAP_H)
    sheet.blit(head_f.render("DAY  (true 58px, no guides)", True, (255, 255, 255)),
               (24, 64))
    sheet.blit(head_f.render("NIGHT  (true 58px, no guides)", True,
                             (255, 255, 255)), (268, 64))
    sheet.blit(day, (20, 86))
    sheet.blit(night, (264, 86))

    # The fairness contract callout (the only thing that matters per the critique).
    sheet.blit(body_f.render(
        "Contract: solid pole cap-to-cap on bare sky.  No white box.",
        True, (188, 230, 200)), (20, 86 + PANEL_H + 8))

    # 0.7x motion/distance panel — verify the pole still holds when scrolling.
    cx3 = 508
    sheet.blit(head_f.render("0.7x  (motion / distance)", True, (255, 255, 255)),
               (cx3, 64))
    motion = _pair_on_sky(PANEL_W, PANEL_H, (150, 205, 235), (210, 235, 245),
                          GAP_H, scale=0.7)
    sheet.blit(motion, (cx3, 86))
    sheet.blit(body_f.render("(shrunk to sim. scroll — pole must still read)",
                             True, (206, 208, 218)), (cx3, 86 + PANEL_H + 8))

    # Detail callout: a single isolated tile, magnified — show shaft + barb + bead.
    cx4 = 760
    sheet.blit(head_f.render("SHAFT + GAP-BARB (3x)", True, (255, 255, 255)),
               (cx4, 64))
    tile_h = 240
    tile = render_column(tile_h, 6, flip=False)
    big = pygame.transform.scale(
        tile, ((PW + 2 * OVERHANG) * 2, tile_h * 2))
    tile_panel = _sky(big.get_width() + 8, big.get_height() + 8,
                      (150, 205, 235), (200, 228, 244))
    tile_panel.blit(big, (4, 4))
    sheet.blit(tile_panel, (cx4, 86))
    sheet.blit(body_f.render("solid shaft + mid-gap thorn-barbs",
                             True, (206, 208, 218)), (cx4, 86 + big.get_height() + 12))

    sheet.blit(body_f.render(
        "Collision edge = the central SOLID spike.  Identity held: continuous "
        "thin-but-solid pole + visible (tightened) air + discrete beads — not a "
        "fused slab, not a stupa.",
        True, (188, 190, 200)), (20, 736))

    out = "/home/user/skybit/docs/clown_bone_columns/marrow-skewer/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
