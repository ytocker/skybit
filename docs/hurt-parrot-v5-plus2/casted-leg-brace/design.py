"""
`casted-leg-brace` — field-dressed-plus, but the right leg is splinted.

Thesis: a rigid splint rail and peg-foot break the sprite's outline below the
body — the injury you can see in silhouette alone. Everything above the hips is
unchanged from field-dressed-plus (one chest pad, one cross, three plasters);
the read at 1x comes from the asymmetric leg, not from more gauze.

Round 2: plaster-white cast sleeve (reads against both day and night sky),
wider 7px cuff separated from dark rail by value, left leg extended with foot
and animated to emphasise the brace's rigidity by contrast.
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

# Plaster-white cast: luma≈231, reads 1.9:1 vs day-sky, ~10:1 vs night
CAST_WHITE = (236, 231, 218)

CHEST_PAD = [(20, 23), (30, 21), (31, 34), (21, 36)]
CHEST_H   = ((23, 28), (27, 28))
CHEST_V   = ((25, 25), (25, 31))

UPPER_CUT = ((20, 33), (37, 43))
LOWER_CUT = ((22, 40), (32, 45))

# Small adhesive plasters. Neither carries a cross.
BANDAID_L = (12, 40, 24, 46)   # left flank below cuts — 12×6 px
BANDAID_R = (33, 37, 44, 43)   # right lower body — 11×6 px
BANDAID_3 = (38, 33, 47, 38)   # upper-right body, just below head/body seam — 9×5 px

# Left leg x offsets per frame — good leg sways ±1px while brace is frozen
_LEFT_LEG_X = [28, 29, 28, 27]


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


def _draw_cast_brace(surf):
    """Splinted right leg. Drawn straight onto the sprite — not through
    `_stamp_clipped` — because the rail and foot plate live OUTSIDE the body
    silhouette, so the injury survives at 1x where on-body gauze detail collapses.

    Two-value design: plaster-white sleeve (soft cast wrapping) over a dark HEM
    rail (rigid peg) so the sleeve reads as padding and the rail reads as rigid.
    Wider 7px cuff distinguishes cast bulk from the 3px rail below.
    """
    d = pygame.draw

    sleeve_x, sleeve_y = 32, 44
    # Plaster-white: luma≈231 reads against both day (149) and night (9) sky
    d.rect(surf, CAST_WHITE, (sleeve_x, sleeve_y, 7, 6))
    d.rect(surf, HEM,        (sleeve_x, sleeve_y, 7, 6), 1)
    # Two diagonal HEM straps across the cast face — diagonals survive downsampling
    d.line(surf, HEM, (sleeve_x + 1, sleeve_y + 1), (sleeve_x + 5, sleeve_y + 3), 1)
    d.line(surf, HEM, (sleeve_x + 1, sleeve_y + 3), (sleeve_x + 5, sleeve_y + 5), 1)

    rail_x, rail_y = 34, 50
    d.rect(surf, HEM, (rail_x, rail_y, 3, 7))
    d.line(surf, (80, 68, 55), (rail_x, rail_y), (rail_x, rail_y + 6), 1)
    d.rect(surf, HEM, (rail_x - 1, rail_y + 7, 5, 2))
    d.line(surf, (180, 155, 120), (rail_x - 1, rail_y + 7), (rail_x + 3, rail_y + 7), 1)


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


def _build_hurt_frame(wing_angle_deg, frame_idx=0):
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

    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    d.polygon(surf, BEAK,    upper)
    d.polygon(surf, BEAK_D,  upper, 1)
    d.polygon(surf, BEAK_LO, lower)
    d.polygon(surf, BEAK_D,  lower, 1)
    d.line(surf, (255, 220, 100), (55, 22), (59, 24), 1)

    # Left (good) leg — extended foot makes the asymmetry legible;
    # lateral sway per frame contrasts with the frozen brace
    lx = _LEFT_LEG_X[frame_idx % 4]
    d.line(surf, BEAK_D, (lx, 45), (lx - 2, 52), 2)
    d.line(surf, BEAK_D, (lx - 2, 52), (lx - 4, 53), 2)  # toe kink

    # Right leg replaced by cast-brace — brace is identical in all 4 frames
    _draw_cast_brace(surf)

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

    frame = _build_hurt_frame(10, 0)
    arr_hw = pygame.surfarray.pixels3d(frame).transpose(1, 0, 2)
    alpha_hw = pygame.surfarray.pixels_alpha(frame).T

    GAUZE_C      = np.array(GAUZE)
    HEM_C        = np.array(HEM)
    CAST_WHITE_C = np.array(CAST_WHITE)
    CROSS_C      = np.array(CROSS)
    SCRATCH_D_C  = np.array(SCRATCH_D)
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

    # Cast sleeve plaster-white pixels in the cuff region
    sleeve_region = arr_hw[44:50, 32:39, :]
    sleeve_white  = int(np.all(np.abs(sleeve_region - CAST_WHITE_C) < 12, axis=2).sum())

    # Brace rail must reach below body — sample rows 50-57 for HEM colour
    brace_region = arr_hw[50:58, 32:38, :]
    brace_count  = int(np.all(np.abs(brace_region - HEM_C) < 20, axis=2).sum())

    print(f"gauze={gauze_count} ({gauze_frac:.1%} of opaque), "
          f"cross={cross_count}, wound_px={wound_pixels}, "
          f"brace={brace_count}, sleeve_white={sleeve_white}, luma={luma:.1f}")

    # Three bandaids + chest pad + cast sleeve; ceiling holds the mummy line
    assert gauze_count   >= 150,  f"gauze too low: {gauze_count}"
    assert gauze_count   <= 320,  f"gauze overload (mummy): {gauze_count}"
    assert gauze_frac    <= 0.22, f"gauze fraction too high: {gauze_frac:.1%}"
    assert cross_count   >= 10,   f"cross too faint: {cross_count}"
    assert cross_count   <= 25,   f"two-cross bleed: {cross_count}"
    assert wound_pixels  >= 20,   f"wound too faint: {wound_pixels}"
    assert luma          >= 95,   f"luma too dark: {luma:.1f}"
    assert brace_count   >= 10,   f"brace peg too faint or not reaching row 50+: {brace_count}"
    assert sleeve_white  >= 6,    f"cast sleeve too pale or missing: {sleeve_white}"

    jaw_zone = np.zeros_like(opaque)
    jaw_zone[30:, 33:] = True
    gauze_in_jaw = int(np.all(np.abs(arr_hw - GAUZE_C) < 12, axis=2)[jaw_zone].sum())
    assert gauze_in_jaw <= 150, f"jaw pad crept back: {gauze_in_jaw} gauze px in jaw zone"

    print("All asserts passed.")

    del arr_hw, alpha_hw, brace_region, sleeve_region

    raw    = [_build_hurt_frame(a, i) for i, a in enumerate(_HURT_ANGLES)]
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
    lbl = font.render("casted-leg-brace — round 2   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
