"""
`plucked-notch` — the intermediate hurt skin, told by subtraction.

Forked from `ace-headwrap`, then stripped of every dressing. Nothing is added
to the bird: something is taken from it. A bite-shaped notch is torn out of the
wing's trailing edge, and a single loose feather drifts in the wake above the
shoulder. That is the whole vocabulary — no gauze, no plasters, no cross.

The notch is authored in wing-local space and carried through the wing's own
rotation, so it is the only hurt cue in this family that ANIMATES: the tear
sweeps across the flap arc instead of sitting frozen on the body.

Two geometry facts drove the final placement, both measured rather than
assumed. First, the wing is blitted over the body and is almost entirely
enclosed by the body + head ellipses, so a punch-out confined to the wing
surface can never reach sky — it would only reveal red plumage and read as a
stain, not a hole. Second, the wing's trailing corner sits ~7 px inside the
body's lower-left contour. So the tear is cut through the *composite* along the
wing's trailing axis, deep enough to break the outer silhouette. The result is
a genuine dent in the bird's outline at 1x, which is the only scale that
decides whether a damage cue works.
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

BODY    = (205,  28,  28)
BODY_SH = (130,  12,  12)
WING_D  = ( 18,  42, 125)

# Bite geometry in the wing's own 50x50 space, so it rides the flap rotation.
# Circles rather than a polygon: a scallop reads as "torn out" where a straight
# chord would read as a cut edge of the wing itself.
BITE_LOBES = (((17, 38), 5.4), ((13, 43), 4.6))
# Inner rim arc — the part of the tear that stays on the bird and needs depth.
BITE_LIP = ((22, 33), (20, 38), (17, 43), (13, 48))

FEATHER_BOB = (0, 1, -1, 0)


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


def _wing_to_sprite(pt, angle_deg):
    """Map a wing-local point onto the sprite, matching the blit + rotation.

    pygame.transform.rotate turns counter-clockwise about the surface centre and
    the blit re-centres the grown rect on (34, 28), so the centre is the one
    fixed point and this is the exact inverse of what the renderer does.
    """
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    dx, dy = pt[0] - 25, pt[1] - 25
    return (34 + dx * ca + dy * sa, 28 - dx * sa + dy * ca)


def _build_wing(angle_deg):
    WING   = (30,  70, 180)
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

    # Trailing edge loses its feather bulk to the bite before anything else
    # sees the wing, so the tear survives even where the body sits behind it.
    for centre, r in BITE_LOBES:
        d.circle(w, (0, 0, 0, 0), centre, int(r), 0)
    d.lines(w, WING_D, False, BITE_LIP, 1)
    return pygame.transform.rotate(w, angle_deg)


def _punch_bite(surf, angle_deg):
    """Cut the notch through the finished sprite and line its inner rim.

    Done on the composite because the wing alone is enclosed by the body and
    head ellipses — a wing-only hole would show plumage, not sky, and the
    concept is subtractive: the silhouette has to actually lose material.
    """
    lobes = [(_wing_to_sprite(c, angle_deg), r) for c, r in BITE_LOBES]
    for (cx, cy), r in lobes:
        for x in range(max(0, int(cx - r - 1)), min(SPRITE_W, int(cx + r + 2))):
            for y in range(max(0, int(cy - r - 1)), min(SPRITE_H, int(cy + r + 2))):
                if math.hypot(x - cx, y - cy) <= r:
                    surf.set_at((x, y), (0, 0, 0, 0))

    # Rim shading rides just inside each lobe so the tear has thickness rather
    # than looking like a clean die-cut.
    for (cx, cy), r in lobes:
        for step in range(0, 360, 6):
            t = math.radians(step)
            x = int(round(cx + math.cos(t) * (r + 0.9)))
            y = int(round(cy + math.sin(t) * (r + 0.9)))
            if not (0 <= x < SPRITE_W and 0 <= y < SPRITE_H):
                continue
            if surf.get_at((x, y))[3] <= 8:
                continue
            if any(math.hypot(x - ox, y - oy) <= orr for (ox, oy), orr in lobes):
                continue
            surf.set_at((x, y), (*BODY_SH, surf.get_at((x, y))[3]))


def _draw_loose_feather(surf, frame_index):
    """One plucked feather trailing above the shoulder.

    Detached from the silhouette on purpose: an isolated shape in empty canvas
    is what sells "this came off" at 1x, where a feather touching the body
    would just thicken the outline. The per-frame bob keeps it alive without
    animating far enough to read as a second bird.
    """
    d = pygame.draw
    fy = 12 + FEATHER_BOB[frame_index % 4]
    d.polygon(surf, BODY, [(4, fy + 3), (6, fy), (11, fy + 1), (9, fy + 5)])
    d.line(surf, BODY_SH, (6, fy + 1), (10, fy + 3), 1)


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


def _draw_tail(surf):
    d = pygame.draw
    for i, c in enumerate(((174, 38, 48), (190, 70, 30),
                           (210, 130, 40), (230, 195, 65))):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ]
        d.polygon(surf, c, pts)
    d.line(surf, BODY_SH, (4, 27), (18, 31), 1)
    d.line(surf, BODY_SH, (6, 33), (20, 35), 1)


def _build_hurt_frame(wing_angle_deg, frame_index=0):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    CHEST   = (235,  80,  80)
    BELLY   = (215, 140,  45)
    BEAK    = (235, 168,   0)
    BEAK_LO = (205, 138,   0)
    BEAK_D  = (140,  92,   0)

    _draw_loose_feather(surf, frame_index)
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
    _aaellipse(surf, (200, 90, 90),   (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

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

    _punch_bite(surf, wing_angle_deg)

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

    # A healthy reference frame tells us how much silhouette the bite removed.
    def _intact(angle):
        s = _build_hurt_frame(angle)
        return s

    for i, ang in enumerate(_HURT_ANGLES):
        f = _add_outline(_build_hurt_frame(ang, i))
        alpha = pygame.surfarray.pixels_alpha(f).T.copy()
        # Bite zone in outlined-sprite space (2 px pad already applied)
        zone = alpha[34:56, 8:34]
        holes = int((zone <= 8).sum())
        print(f"angle {ang:>4}: bite-zone transparent px = {holes}")
        assert holes >= 20, f"notch closed up at angle {ang}: {holes}"

        del alpha

    f0 = _build_hurt_frame(10, 0)
    a0 = pygame.surfarray.pixels3d(f0).transpose(1, 0, 2).copy()
    al0 = pygame.surfarray.pixels_alpha(f0).T.copy()

    # No dressing palette may survive anywhere in the sprite
    for name, c in (("gauze", (198, 190, 172)), ("hem", (120, 108, 95)),
                    ("cross", (190, 20, 35)), ("stitch", (180, 170, 160))):
        n = int((np.all(np.abs(a0.astype(int) - np.array(c)) < 10, axis=2)
                 & (al0 > 8)).sum())
        print(f"{name} px = {n}")
        assert n == 0, f"dressing colour {name} leaked in: {n}"

    feather = int((al0[10:20, 2:14] > 8).sum())
    print(f"loose feather px = {feather}")
    assert feather >= 14, f"loose feather too small: {feather}"

    rim = int((np.all(np.abs(a0.astype(int) - np.array(BODY_SH)) < 10, axis=2)
               & (al0 > 8))[30:56, 8:34].sum())
    print(f"torn-rim px = {rim}")
    assert rim >= 12, f"tear rim too faint: {rim}"

    luma = float((0.299 * a0[:, :, 0] + 0.587 * a0[:, :, 1]
                  + 0.114 * a0[:, :, 2])[al0 > 8].mean())
    print(f"luma = {luma:.1f}")
    assert luma >= 90, f"luma too dark: {luma:.1f}"

    print("All asserts passed.")
    del a0, al0

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
    lbl = font.render("plucked-notch — round 1   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
