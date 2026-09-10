"""
`cinch-harness` — field-dressed-plus plus a dark improvised tape strap.

The medic had no more gauze, so he cinched the wound shut with whatever tape
was left. The injury reads by value inversion rather than by more white: a
near-black olive strap cuts diagonally across the red plumage, so the eye finds
it instantly without adding another pale mass to an already-bandaged bird. The
brass buckle rhymes with the aviator frame so the addition looks native to the
character rather than bolted on.
"""
import math
import os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

SPRITE_W, SPRITE_H = 64, 60
_HURT_ANGLES = (10, -5, -20, -35)

SHADE_BLACK = (15, 15, 25)
SHADE_GLINT = (255, 255, 255)
SHADE_TINT  = (35, 55, 90)
SHADE_FRAME = (220, 175, 40)

STITCH     = (180, 170, 160)
GAUZE      = (198, 190, 172)
HEM        = (120, 108,  95)
CROSS      = (190,  20,  35)
SCRATCH_D  = (100,  10,  10)
SCRATCH_HL = (245, 165, 150)
SCRATCH_PALE = (180, 90, 80)
CRACK      = (150, 175, 205)

# Improvised tape. Deliberately far darker than anything else on the body so it
# reads by contrast against red plumage instead of competing with the gauze.
TAPE       = ( 38,  42,  30)
TAPE_HI    = ( 98, 104,  78)   # raised to luma≈96 so it reads as cloth sheen not shadow

CINCH_A    = (35, 28)   # upper end on red plumage, 2 px from body edge
CINCH_B    = (22, 40)   # lower end, 2 px in from left silhouette
BUCKLE_C   = (28, 34)

CHEST_PAD = [(20, 23), (30, 21), (31, 34), (21, 36)]
CHEST_H   = ((23, 28), (27, 28))
CHEST_V   = ((25, 25), (25, 31))

UPPER_CUT = ((20, 33), (37, 43))
LOWER_CUT = ((22, 40), (32, 45))

# Small adhesive plasters. Neither carries a cross.
BANDAID_L = (12, 40, 24, 46)   # left flank below cuts — 12×6 px
BANDAID_R = (33, 37, 44, 43)   # right lower body — 11×6 px
BANDAID_3 = (38, 33, 47, 38)   # upper-right body, just below head/body seam — 9×5 px


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    pygame.draw.ellipse(surf, color, (cx - rx, cy - ry, rx * 2, ry * 2))


def _add_outline(src, outline_color=(20, 12, 18, 220)):
    pad = 2
    w, h = src.get_size()
    mask = pygame.mask.from_surface(src, threshold=8)
    sil  = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    out  = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _build_wing(angle_deg):
    WING   = (30,  70, 180)
    WING_D = (18,  42, 125)
    TIP    = (50, 200,  95)
    STRIPE = (210, 175,  50)
    HL     = (130, 175, 240)
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0,0,0,100), [(24,26),(46,14),(50,30),(34,44),(18,40)])
    d.polygon(w, WING,        [(24,24),(44,13),(48,28),(32,42),(18,36)])
    d.polygon(w, WING_D,      [(24,24),(32,42),(18,36)])
    d.polygon(w, TIP,         [(44,13),(50,18),(48,28)])
    d.polygon(w, STRIPE,      [(42,18),(48,22),(46,28),(40,24)])
    d.line(w, WING_D,         (26,25),(42,18), 2)
    d.line(w, WING_D,         (28,30),(44,25), 2)
    d.line(w, WING_D,         (30,34),(46,32), 2)
    d.line(w, HL,             (25,25),(41,15), 1)
    d.polygon(w, (0,0,0,0),   [(41,11),(53,17),(47,25),(43,16)])
    return pygame.transform.rotate(w, angle_deg)


def _stamp_clipped(surf, layer):
    """Composite a layer only where the silhouette already has pixels."""
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            px = layer.get_at((x, y))
            if px[3] > 8 and surf.get_at((x, y))[3] > 8:
                surf.set_at((x, y), (px[0], px[1], px[2], surf.get_at((x, y))[3]))


def _lerp_pt(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t))


def _draw_ragged_cuts(surf):
    """Two raked claw-marks — same as field-dressed, unchanged."""
    core_layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    lip_layer  = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    for (ax, ay), (bx, by) in (UPPER_CUT, LOWER_CUT):
        lip_a = _lerp_pt((ax - 1, ay - 2), (bx - 1, by - 2), 0.20)
        d.line(lip_layer, SCRATCH_HL, lip_a, (bx - 1, by - 2), 1)
        d.line(core_layer, SCRATCH_D, (ax, ay), (bx, by), 1)

    dark = set()
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            r, g, b, a = surf.get_at((x, y))
            if a > 8 and (0.299 * r + 0.587 * g + 0.114 * b) < 80:
                dark.add((x, y))

    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            base_a = surf.get_at((x, y))[3]
            if base_a <= 8:
                continue
            on_dark = (x, y) in dark
            if core_layer.get_at((x, y))[3] > 8:
                c = SCRATCH_PALE if on_dark else SCRATCH_D
                surf.set_at((x, y), (*c, base_a))
            elif lip_layer.get_at((x, y))[3] > 8 and not on_dark:
                surf.set_at((x, y), (*SCRATCH_HL, base_a))


def _draw_bandaid(surf, x0, y0, x1, y1, tab_left=True):
    """Small rectangular adhesive plaster. GAUZE fill, HEM outline, two STITCH
    tabs on one side — the tab side faces open plumage so they read against red.
    No cross: the chest pad owns the only red mark."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw

    # Tabs drawn before the pad so HEM always wins at the pad edge
    mid_y = (y0 + y1) // 2
    if tab_left:
        d.line(layer, STITCH, (x0 - 3, y0 + 1), (x0, y0 + 1), 1)
        d.line(layer, STITCH, (x0 - 3, y1 - 1), (x0, y1 - 1), 1)
    else:
        d.line(layer, STITCH, (x1, y0 + 1), (x1 + 3, y0 + 1), 1)
        d.line(layer, STITCH, (x1, y1 - 1), (x1 + 3, y1 - 1), 1)

    d.rect(layer, GAUZE, (x0, y0, x1 - x0, y1 - y0))
    d.rect(layer, HEM,   (x0, y0, x1 - x0, y1 - y0), 1)

    _stamp_clipped(surf, layer)


def _draw_bandaids(surf):
    """Two adhesive plasters on the lower body. Drawn after the cuts so each one
    sits visibly on top of plumage rather than disappearing into the wound ink."""
    x0, y0, x1, y1 = BANDAID_L
    _draw_bandaid(surf, x0, y0, x1, y1, tab_left=True)
    x0, y0, x1, y1 = BANDAID_R
    _draw_bandaid(surf, x0, y0, x1, y1, tab_left=False)
    x0, y0, x1, y1 = BANDAID_3
    _draw_bandaid(surf, x0, y0, x1, y1, tab_left=False)


def _draw_cinch_harness(surf):
    """Dark tape strap over the chest pad, with a HEM-framed brass buckle.

    Called AFTER _draw_chest_dressing so the strap cinches the pad visibly
    rather than disappearing under it. The wound gaps are preserved as a
    transparent break in the tape to keep the injury the dominant read.
    A short frayed tail exits lower-left beyond the silhouette.
    """
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw

    d.line(layer, TAPE,    CINCH_A, CINCH_B, 3)
    d.line(layer, TAPE_HI, (CINCH_A[0] - 1, CINCH_A[1] - 1),
                           (CINCH_B[0] - 1, CINCH_B[1] - 1), 1)

    # Buckle: HEM keyline outside the SHADE_FRAME fill
    bx, by = BUCKLE_C
    d.rect(layer, HEM,         (bx - 2, by - 2, 5, 5))
    d.rect(layer, SHADE_FRAME, (bx - 1, by - 1, 3, 3))
    layer.set_at((bx + 1, by - 1), SHADE_GLINT)

    # Punch wound pixels out: the strap reads as torn/improvised if the cut
    # breaks it rather than the clean tape erasing the damage.
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            if layer.get_at((x, y))[3] <= 8:
                continue
            r, g, b, a = surf.get_at((x, y))
            if a <= 8:
                continue
            for wc in (SCRATCH_D, SCRATCH_HL, SCRATCH_PALE):
                if abs(r - wc[0]) < 20 and abs(g - wc[1]) < 20 and abs(b - wc[2]) < 20:
                    layer.set_at((x, y), (0, 0, 0, 0))
                    break

    _stamp_clipped(surf, layer)

    # Frayed tail: 3-4 px drawn DIRECTLY to surf so the tail can exit the
    # silhouette (stamp_clipped would eat it — the tail is the point that the
    # strap is improvised and slightly too long).
    d = pygame.draw
    tx, ty = CINCH_B[0] - 1, CINCH_B[1] + 1
    d.line(surf, TAPE,    (tx, ty), (tx - 3, ty + 3), 1)
    d.line(surf, TAPE_HI, (tx, ty), (tx - 2, ty + 2), 1)


def _draw_chest_dressing(surf):
    """Main dressing — identical to field-dressed."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw

    cx = sum(p[0] for p in CHEST_PAD) / len(CHEST_PAD)
    cy = sum(p[1] for p in CHEST_PAD) / len(CHEST_PAD)
    grown = []
    for px, py in CHEST_PAD:
        vx, vy = px - cx, py - cy
        L = max(1e-3, math.hypot(vx, vy))
        grown.append((px + vx / L * 1.6, py + vy / L * 1.6))
    d.polygon(layer, HEM,   grown)
    d.polygon(layer, GAUZE, CHEST_PAD)

    d.line(layer, CROSS, CHEST_H[0], CHEST_H[1], 2)
    d.line(layer, CROSS, CHEST_V[0], CHEST_V[1], 2)

    d.line(layer, STITCH, (18, 26), (21, 26), 1)
    d.line(layer, STITCH, (18, 32), (21, 32), 1)
    d.line(layer, STITCH, (29, 23), (32, 23), 1)
    d.line(layer, STITCH, (29, 31), (32, 31), 1)

    _stamp_clipped(surf, layer)


def _draw_sunglasses(surf, cx, cy):
    r_outer = 6
    left  = (cx - 4, cy + 2)
    right = (cx + 6, cy - 1)

    pygame.draw.circle(surf, SHADE_FRAME, left, r_outer + 1)
    pygame.draw.circle(surf, SHADE_FRAME, right, r_outer + 1)
    pygame.draw.circle(surf, SHADE_BLACK, left, r_outer)
    pygame.draw.circle(surf, SHADE_BLACK, right, r_outer)
    tint = pygame.Surface((r_outer * 2, r_outer), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0] - r_outer, left[1] - r_outer + 1))
    surf.blit(tint, (right[0] - r_outer, right[1] - r_outer + 1))
    pygame.draw.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    pygame.draw.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 1), 1)
    pygame.draw.line(surf, SHADE_FRAME, (left[0] + 6, 21), (right[0] - 6, 19), 2)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] - r_outer + 1, left[1] - r_outer + 2),
                     (right[0] + r_outer - 1, right[1] - r_outer + 2), 1)


def _draw_cracked_lens(surf):
    for end in ((41, 17), (50, 18), (47, 26)):
        pygame.draw.line(surf, CRACK, (45, 21), end, 1)
    pygame.draw.line(surf, CRACK, (43, 19), (47, 23), 1)


def _tail_feather(pts, damaged=False):
    if not damaged:
        return pts
    root = ((pts[1][0] + pts[2][0]) / 2.0, (pts[1][1] + pts[2][1]) / 2.0)
    a = math.radians(18)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for i, (x, y) in enumerate(pts):
        if i in (0, 3):
            dx, dy = root[0] - x, root[1] - y
            L = max(1e-3, math.hypot(dx, dy))
            x, y = x + dx / L * 8.0, y + dy / L * 8.0
        vx, vy = x - root[0], y - root[1]
        out.append((root[0] + vx * ca - vy * sa, root[1] + vx * sa + vy * ca))
    return out


def _draw_tail(surf):
    d = pygame.draw
    BODY_SH = (130, 12, 12)
    for i, c in enumerate(((174, 38, 48), (190, 70, 30),
                           (210, 130, 40), (230, 195, 65))):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ]
        d.polygon(surf, c, _tail_feather(pts, damaged=(i == 1)))
    d.line(surf, BODY_SH, (4, 27), (18, 31), 1)
    d.line(surf, BODY_SH, (6, 33), (20, 35), 1)


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = (205,  28,  28)
    BODY_SH = (130,  12,  12)
    CHEST   = (235,  80,  80)
    BELLY   = (215, 140,  45)
    BEAK    = (235, 168,   0)
    BEAK_LO = (205, 138,   0)
    BEAK_D  = (140,  92,   0)

    _draw_tail(surf)

    _aaellipse(surf, BODY_SH, (34, 35), 19, 14)
    _aaellipse(surf, BODY,    (32, 32), 19, 14)
    _aaellipse(surf, CHEST,   (30, 29), 13,  8)
    _aaellipse(surf, BELLY,   (28, 38), 12,  6)

    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (205, 150, 150, 120), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _draw_ragged_cuts(surf)
    _draw_bandaids(surf)

    _aaellipse(surf, (155, 15, 20),   (48, 24), 12, 11)
    _aaellipse(surf, BODY,            (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90),   (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _draw_sunglasses(surf, 50, 20)
    _draw_cracked_lens(surf)
    _draw_chest_dressing(surf)
    _draw_cinch_harness(surf)   # after chest pad so strap visibly cinches it

    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    d.polygon(surf, BEAK,    upper)
    d.polygon(surf, BEAK_D,  upper, 1)
    d.polygon(surf, BEAK_LO, lower)
    d.polygon(surf, BEAK_D,  lower, 1)
    d.line(surf, (255, 220, 100), (55, 22), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    return surf


def _strip(frames, scale, gap, bg):
    fw, fh = frames[0].get_size()
    w = len(frames) * fw * scale + (len(frames) - 1) * gap
    s = pygame.Surface((w, fh * scale))
    s.fill(bg)
    for i, f in enumerate(frames):
        s.blit(pygame.transform.scale(f, (fw * scale, fh * scale)),
               (i * (fw * scale + gap), 0))
    return s


if __name__ == "__main__":
    import numpy as np

    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    frame = _build_hurt_frame(10)
    arr_hw = pygame.surfarray.pixels3d(frame).transpose(1, 0, 2)
    alpha_hw = pygame.surfarray.pixels_alpha(frame).T

    GAUZE_C     = np.array(GAUZE)
    CROSS_C     = np.array(CROSS)
    SCRATCH_D_C = np.array(SCRATCH_D)
    SCRATCH_HL_C = np.array(SCRATCH_HL)

    gauze_count = int(np.all(np.abs(arr_hw - GAUZE_C) < 12, axis=2).sum())
    cross_count = int(np.all(np.abs(arr_hw - CROSS_C) < 12, axis=2).sum())

    opaque = alpha_hw > 8
    luma_hw = (0.299 * arr_hw[:, :, 0] + 0.587 * arr_hw[:, :, 1]
               + 0.114 * arr_hw[:, :, 2])
    luma = float(luma_hw[opaque].mean())

    wound_mask = np.all(np.abs(arr_hw - SCRATCH_D_C) < 20, axis=2) | \
                 np.all(np.abs(arr_hw - SCRATCH_HL_C) < 20, axis=2)
    wound_pixels = int(wound_mask.sum())

    opaque_count = int(opaque.sum())
    gauze_frac = gauze_count / max(opaque_count, 1)

    print(f"gauze={gauze_count} ({gauze_frac:.1%} of opaque), "
          f"cross={cross_count}, wound_px={wound_pixels}, luma={luma:.1f}")

    # Three bandaids + chest pad; ceiling raised to allow the extra gauze
    assert gauze_count   >= 150,  f"gauze too low: {gauze_count}"
    assert gauze_count   <= 320,  f"gauze overload (mummy): {gauze_count}"
    assert gauze_frac    <= 0.22, f"gauze fraction too high: {gauze_frac:.1%}"
    assert cross_count   >= 10,   f"cross too faint: {cross_count}"
    assert cross_count   <= 25,   f"two-cross bleed: {cross_count}"
    assert wound_pixels  >= 20,   f"wound too faint: {wound_pixels}"
    # Relaxed 2 points from field-dressed-plus: the tape strap is intentionally
    # the darkest thing on the bird, so it pulls the body mean down on purpose.
    assert luma          >= 93,   f"luma too dark: {luma:.1f}"

    tape_pixels = int(np.all(np.abs(arr_hw - np.array(TAPE)) < 20, axis=2).sum())
    print(f"tape={tape_pixels}")
    assert tape_pixels >= 20, f"strap too faint or draw-order hidden: {tape_pixels}"

    # Buckle must show at least 6 SHADE_FRAME pixels in the 5×5 around BUCKLE_C
    bx, by = BUCKLE_C
    buckle_zone = arr_hw[max(0,by-2):by+3, max(0,bx-2):bx+3, :]
    SHADE_FRAME_C = np.array(SHADE_FRAME)
    buckle_px = int(np.all(np.abs(buckle_zone - SHADE_FRAME_C) < 15, axis=2).sum())
    print(f"buckle={buckle_px}")
    assert buckle_px >= 6, f"buckle too faint: {buckle_px}"

    jaw_zone = np.zeros_like(opaque)
    jaw_zone[30:, 33:] = True
    gauze_in_jaw = int(np.all(np.abs(arr_hw - GAUZE_C) < 12, axis=2)[jaw_zone].sum())
    assert gauze_in_jaw <= 150, f"jaw pad crept back: {gauze_in_jaw} gauze px in jaw zone"

    print("All asserts passed.")

    del arr_hw, alpha_hw

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    NIGHT, DAY = (8, 8, 20), (100, 160, 220)
    margin, gap = 20, 10
    row1  = _strip(frames, 4, gap, NIGHT)
    row2  = _strip(frames, 2, gap, NIGHT)
    row3a = _strip(frames, 1, gap, DAY)
    row3b = _strip(frames, 1, gap, (5, 8, 30))

    label_h = 30
    pad3    = 12
    canvas_w = margin * 2 + max(row1.get_width(), row2.get_width())
    canvas_h = (margin + row1.get_height() + gap + row2.get_height() + gap +
                row3a.get_height() + pad3 * 2 + label_h + margin)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(NIGHT)

    canvas.blit(row1, (margin, margin))
    y = margin + row1.get_height() + gap
    canvas.blit(row2, (margin, y))
    y += row2.get_height() + gap

    for i, (panel, bg) in enumerate(((row3a, DAY), (row3b, (5, 8, 30)))):
        px = margin + i * (panel.get_width() + pad3 * 2 + gap * 2)
        pygame.draw.rect(canvas, bg,
                         (px, y, panel.get_width() + pad3 * 2,
                          panel.get_height() + pad3 * 2))
        canvas.blit(panel, (px + pad3, y + pad3))
    y += row3a.get_height() + pad3 * 2

    try:
        font  = pygame.font.SysFont("dejavusans", 17)
        small = pygame.font.SysFont("dejavusans", 12)
    except Exception:
        font = small = pygame.font.Font(None, 17)
    canvas.blit(small.render("1x on day sky", True, (10, 20, 40)),
                (margin + pad3, y - pad3 + 1))
    canvas.blit(small.render("1x on night sky", True, (200, 205, 230)),
                (margin + row3a.get_width() + pad3 * 3 + gap * 2, y - pad3 + 1))
    lbl = font.render("cinch-harness — round 2   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
