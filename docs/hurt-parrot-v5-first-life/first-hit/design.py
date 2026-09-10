"""
`first-hit` — first life lost: ace-headwrap stripped back to its minimum.

Identical to the last-life (ace-headwrap) skin except:
  - Head bandage REMOVED (head untouched, no knock yet)
  - Chest dressing + red cross REMOVED
  - Ragged claw-gash cuts REMOVED
  - Cracked lens: one crack line only (centre-to-lower-right)

What stays: the three adhesive plasters on the lower body, and the
sunglasses with a single hairline crack. The three bandaids already
exist on the body from a previous rough encounter — they read as
"the player has taken damage before" without screaming "critical".
The one crack tells the eye something happened to the shades without
the full spiderweb that signals last-life desperation.

The reduction is what makes the escalation legible: last-life adds the
head bandage, the chest pad, the wounds, and the full cracked-lens
spiderweb on top of exactly this intermediate state.
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

STITCH       = (180, 170, 160)
GAUZE        = (198, 190, 172)
HEM          = (120, 108,  95)
CRACK        = (150, 175, 205)

# Three bandaids — same footprints as ace-headwrap, no change
BANDAID_L = (12, 40, 24, 46)
BANDAID_R = (33, 37, 44, 43)
BANDAID_3 = (38, 33, 47, 38)


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
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            px = layer.get_at((x, y))
            if px[3] > 8 and surf.get_at((x, y))[3] > 8:
                surf.set_at((x, y), (px[0], px[1], px[2], surf.get_at((x, y))[3]))


def _draw_bandaid(surf, x0, y0, x1, y1, tab_left=True):
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
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
    x0, y0, x1, y1 = BANDAID_L
    _draw_bandaid(surf, x0, y0, x1, y1, tab_left=True)
    x0, y0, x1, y1 = BANDAID_R
    _draw_bandaid(surf, x0, y0, x1, y1, tab_left=False)
    x0, y0, x1, y1 = BANDAID_3
    _draw_bandaid(surf, x0, y0, x1, y1, tab_left=False)


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


def _draw_single_crack(surf):
    """One hairline crack on the left lens — centre to lower-right rim only."""
    pygame.draw.line(surf, CRACK, (45, 21), (47, 26), 1)


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

    _draw_bandaids(surf)

    _aaellipse(surf, (155, 15, 20),   (48, 24), 12, 11)
    _aaellipse(surf, BODY,            (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90),   (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _draw_sunglasses(surf, 50, 20)
    _draw_single_crack(surf)

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
    s = pygame.Surface((int(w), int(fh * scale)))
    s.fill(bg)
    for i, f in enumerate(frames):
        s.blit(pygame.transform.scale(f, (int(fw * scale), int(fh * scale))),
               (i * (int(fw * scale) + gap), 0))
    return s


if __name__ == "__main__":
    import numpy as np

    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    frame  = _build_hurt_frame(10)
    arr    = pygame.surfarray.pixels3d(frame).transpose(1, 0, 2).copy()
    alpha  = pygame.surfarray.pixels_alpha(frame).T.copy()
    opaque = alpha > 8

    GAUZE_C = np.array(GAUZE)
    CRACK_C = np.array(CRACK)

    gauze_px  = int(np.all(np.abs(arr - GAUZE_C) < 12, axis=2).sum())
    crack_px  = int(np.all(np.abs(arr - CRACK_C) < 20, axis=2).sum())
    luma      = float((0.299 * arr[:,:,0] + 0.587 * arr[:,:,1]
                       + 0.114 * arr[:,:,2])[opaque].mean())

    print(f"gauze={gauze_px}  crack={crack_px}  luma={luma:.1f}")

    assert gauze_px  >= 30,   f"bandaids too faint: {gauze_px}"
    assert gauze_px  <= 120,  f"gauze overload: {gauze_px}"
    assert crack_px  >= 2,    f"crack missing: {crack_px}"
    assert crack_px  <= 12,   f"too many cracks: {crack_px}"
    assert luma      >= 95,   f"luma too dark: {luma:.1f}"

    # Verify no headwrap pixels in crown zone
    crown_zone       = np.zeros_like(opaque)
    crown_zone[11:20, 38:59] = True
    crown_gauze = int(np.all(np.abs(arr - GAUZE_C) < 12, axis=2)[crown_zone].sum())
    print(f"crown_gauze={crown_gauze}  (must be 0 — no headwrap)")
    assert crown_gauze == 0, f"headwrap crept in: {crown_gauze}"

    print("All asserts passed.")
    del arr, alpha

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    NIGHT, DAY = (8, 8, 20), (100, 160, 220)
    margin, gap = 20, 10
    row1  = _strip(frames, 4, gap, NIGHT)
    row2  = _strip(frames, 2, gap, NIGHT)
    row3a = _strip(frames, 1, gap, DAY)
    row3b = _strip(frames, 1, gap, (5, 8, 30))

    label_h, pad3 = 30, 12
    canvas_w = margin * 2 + max(row1.get_width(), row2.get_width())
    canvas_h = (margin + row1.get_height() + gap + row2.get_height() + gap
                + row3a.get_height() + pad3 * 2 + label_h + margin)
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
    lbl = font.render("first-hit — round 1   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
