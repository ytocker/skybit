"""
`black-eye` — the intermediate hurt skin: first life lost.

The lightest possible damage read. No dressings, no gauze, no torn plumage —
just a swollen bruise peeking out from under the left aviator lens. The shades
stay on, which is the whole character beat: he's hurt but pretending he's not.

The bruise straddles the head/body seam so it reads as a swollen cheek rather
than a floating sticker, and the lens is drawn on top so only the crescent
below it survives — a natural crop that keeps the aviators as the silhouette's
hero shape. The ramp is value-based (each ring darker than the red plumage
under it) rather than hue-based, so the mark still reads as a depression at 1x
and stays legible for colourblind players.
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

SCRATCH_HL = (245, 165, 150)

# Value ramp, outermost first. Every ring is darker than BODY (205,28,28) so
# the blob reads as swelling on luma alone.
BRUISE_OUT  = (175, 105, 150)
BRUISE_MID  = (148,  80, 128)
BRUISE_CORE = (120,  60, 110)
BRUISE_C    = (43, 30)


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


def _draw_bruise(surf):
    """Swollen bruise under the left lens.

    Drawn before the shades so the lens crops its top edge — the surviving
    crescent below the frame is what sells "swelling pushing out from under
    the glasses" instead of a decal pasted on the cheek. Centre sits on the
    head/body seam so the mass spills onto the shoulder like real puffiness.
    """
    _aaellipse(surf, BRUISE_OUT,  BRUISE_C, 5, 3)
    _aaellipse(surf, BRUISE_MID,  BRUISE_C, 4, 2)
    _aaellipse(surf, BRUISE_CORE, BRUISE_C, 2, 2)
    # Upper-left rim catch, matching the sprite's existing key light
    pygame.draw.line(surf, SCRATCH_HL, (40, 28), (42, 28), 2)


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


def _draw_tail(surf, damaged=False):
    d = pygame.draw
    BODY_SH = (130, 12, 12)
    for i, c in enumerate(((174, 38, 48), (190, 70, 30),
                           (210, 130, 40), (230, 195, 65))):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ]
        d.polygon(surf, c, _tail_feather(pts, damaged=(damaged and i == 1)))
    d.line(surf, BODY_SH, (4, 27), (18, 31), 1)
    d.line(surf, BODY_SH, (6, 33), (20, 35), 1)


def _build_frame(wing_angle_deg, hurt=True):
    """`hurt=False` rebuilds the untouched skin, for side-by-side comparison."""
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

    _aaellipse(surf, (155, 15, 20),   (48, 24), 12, 11)
    _aaellipse(surf, BODY,            (47, 22), 12, 11)
    if not hurt:
        # Healthy cheek blush — the bruise takes over this slot when hurt
        _aaellipse(surf, (200, 90, 90), (44, 24), 4, 3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    if hurt:
        _draw_bruise(surf)

    _draw_sunglasses(surf, 50, 20)

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


def _build_hurt_frame(wing_angle_deg):
    return _build_frame(wing_angle_deg, hurt=True)


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

    ramp = [np.array(c) for c in (BRUISE_OUT, BRUISE_MID, BRUISE_CORE,
                                  SCRATCH_HL)]
    bruise_mask = np.zeros(arr_hw.shape[:2], dtype=bool)
    for c in ramp:
        bruise_mask |= np.all(np.abs(arr_hw.astype(int) - c) < 14, axis=2)

    opaque = alpha_hw > 8
    luma_hw = (0.299 * arr_hw[:, :, 0] + 0.587 * arr_hw[:, :, 1]
               + 0.114 * arr_hw[:, :, 2])
    luma = float(luma_hw[opaque].mean())

    total_bruise = int(bruise_mask.sum())

    # The crescent that actually survives the lens crop, at 1x
    zone = np.zeros_like(opaque)
    zone[27:35, 38:51] = True
    visible = int((bruise_mask & zone).sum())

    # Seam spill: rows below the head ellipse's lower edge
    spill = int((bruise_mask & np.pad(np.ones((6, 13), dtype=bool),
                                      ((30, arr_hw.shape[0] - 36),
                                       (38, arr_hw.shape[1] - 51)))).sum())

    print(f"bruise_px={total_bruise}, visible_crescent={visible}, "
          f"seam_spill={spill}, luma={luma:.1f}")

    assert visible       >= 6,  f"bruise crescent too small: {visible}"
    assert total_bruise  >= 10, f"bruise too faint: {total_bruise}"
    assert total_bruise  <= 90, f"bruise oversized (reads as a mask): {total_bruise}"
    assert spill         >= 2,  f"bruise not crossing head/body seam: {spill}"
    # Floor sits just under the undressed sprite's own mean — this concept adds
    # no pale gauze to lift it, so the gauze-era floor of 95 doesn't apply.
    assert luma          >= 90, f"luma too dark: {luma:.1f}"

    # Nothing anywhere else: no dressings on the body
    body_zone = np.zeros_like(opaque)
    body_zone[20:50, 8:38] = True
    assert int((bruise_mask & body_zone).sum()) == 0, "damage leaked onto the body"

    print("All asserts passed.")

    del arr_hw, alpha_hw

    hurt   = [_add_outline(_build_frame(a, hurt=True))  for a in _HURT_ANGLES]
    normal = [_add_outline(_build_frame(a, hurt=False)) for a in _HURT_ANGLES]

    NIGHT, DAY = (8, 8, 20), (100, 160, 220)
    margin, gap = 20, 10
    row1  = _strip(hurt,   4, gap, NIGHT)
    row0  = _strip(normal, 2, gap, NIGHT)
    row2  = _strip(hurt,   2, gap, NIGHT)
    row3a = _strip(hurt,   1, gap, DAY)
    row3b = _strip(hurt,   1, gap, (5, 8, 30))

    label_h = 30
    pad3    = 12
    canvas_w = margin * 2 + max(row1.get_width(), row2.get_width())
    canvas_h = (margin + row1.get_height() + gap + 18 + row0.get_height() +
                gap + 18 + row2.get_height() + gap +
                row3a.get_height() + pad3 * 2 + label_h + margin + 10)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(NIGHT)

    try:
        font  = pygame.font.SysFont("dejavusans", 17)
        small = pygame.font.SysFont("dejavusans", 12)
    except Exception:
        font = small = pygame.font.Font(None, 17)

    canvas.blit(row1, (margin, margin))
    y = margin + row1.get_height() + gap

    canvas.blit(small.render("current skin (undamaged) — 2x", True, (170, 175, 200)),
                (margin, y))
    y += 18
    canvas.blit(row0, (margin, y))
    y += row0.get_height() + gap

    canvas.blit(small.render("black-eye — 2x", True, (170, 175, 200)), (margin, y))
    y += 18
    canvas.blit(row2, (margin, y))
    y += row2.get_height() + gap

    for i, (panel, bg) in enumerate(((row3a, DAY), (row3b, (5, 8, 30)))):
        px = margin + i * (panel.get_width() + pad3 * 2 + gap * 2)
        pygame.draw.rect(canvas, bg,
                         (px, y, panel.get_width() + pad3 * 2,
                          panel.get_height() + pad3 * 2))
        canvas.blit(panel, (px + pad3, y + pad3))
    y += row3a.get_height() + pad3 * 2

    canvas.blit(small.render("1x on day sky", True, (10, 20, 40)),
                (margin + pad3, y - pad3 + 1))
    canvas.blit(small.render("1x on night sky", True, (200, 205, 230)),
                (margin + row3a.get_width() + pad3 * 3 + gap * 2, y - pad3 + 1))
    lbl = font.render("black-eye — round 1   (4x / current 2x / hurt 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
