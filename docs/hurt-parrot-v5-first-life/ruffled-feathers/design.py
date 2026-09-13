"""
`ruffled-feathers` — the intermediate hurt state, first life lost.

Nothing is dressed, bound or patched. Two crest feathers have been knocked
loose off the nape and stand up at odd, unmatched angles — the universal
cartoon tell for "took a knock" without implying a wound. Read comes purely
from silhouette: the spikes sit outboard of the left lens against open sky,
where the outline dilate gives them a hard edge on any backdrop, so the
scruffy notch survives at 1x where a colour-only mark would vanish. The
shades stay pristine and the plumage keeps full saturation, because this
parrot is annoyed, not injured — the visual budget for real damage belongs
to the last-life skin.
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

BODY_RED = (205, 28, 28)
BODY_SH  = (130, 12, 12)

# Longer spike, steeper (~225deg off head centre); base pair is buried well
# inside the skull ellipse so the outline dilate can never orphan it.
SPIKE_LONG    = [(36, 12), (42, 21), (39, 22)]
SPIKE_LONG_SH = [(36, 12), (39, 22), (40, 18)]
# Shorter spike, near-horizontal (~198deg). The angle gap and the length gap
# both matter: matched twins read as a decorative crest, not as damage.
SPIKE_SHORT    = [(31, 18), (39, 22), (38, 19)]
SPIKE_SHORT_SH = [(31, 18), (39, 22), (38, 20)]


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


def _draw_nape_spikes(surf):
    """Two kicked-up crest feathers, drawn before the skull so the head ellipse
    covers their roots and they appear to grow out from under the contour."""
    d = pygame.draw
    d.polygon(surf, BODY_RED, SPIKE_LONG)
    d.polygon(surf, BODY_SH,  SPIKE_LONG_SH)
    d.polygon(surf, BODY_RED, SPIKE_SHORT)
    d.polygon(surf, BODY_SH,  SPIKE_SHORT_SH)


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


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = BODY_RED
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

    _draw_nape_spikes(surf)

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


def _spike_pixels(frame):
    """Count red plumage pixels in the nape zone that fall outside every base
    ellipse — i.e. genuinely new silhouette contributed by the spikes."""
    import numpy as np
    arr = pygame.surfarray.pixels3d(frame).transpose(1, 0, 2).copy()
    alpha = pygame.surfarray.pixels_alpha(frame).T.copy()

    ys, xs = np.mgrid[0:SPRITE_H, 0:SPRITE_W]
    inside = (((xs - 47) / 12.0) ** 2 + ((ys - 22) / 11.0) ** 2 <= 1.0)
    inside |= (((xs - 48) / 12.0) ** 2 + ((ys - 24) / 11.0) ** 2 <= 1.0)
    inside |= (((xs - 32) / 19.0) ** 2 + ((ys - 32) / 14.0) ** 2 <= 1.0)
    inside |= (((xs - 34) / 19.0) ** 2 + ((ys - 35) / 14.0) ** 2 <= 1.0)

    zone = np.zeros_like(inside)
    zone[10:23, 30:43] = True

    red = (np.all(np.abs(arr - np.array(BODY_RED)) < 14, axis=2) |
           np.all(np.abs(arr - np.array(BODY_SH)) < 14, axis=2))
    return int((red & (alpha > 8) & zone & ~inside).sum())


if __name__ == "__main__":
    import numpy as np

    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    for a in _HURT_ANGLES:
        f = _build_frame(a)
        n = _spike_pixels(f)
        print(f"angle {a:>4}: spike_px={n}")
        assert n >= 8, f"spikes lost at wing angle {a}: {n} px"

    frame = _build_frame(10)
    arr_hw = pygame.surfarray.pixels3d(frame).transpose(1, 0, 2).copy()
    alpha_hw = pygame.surfarray.pixels_alpha(frame).T.copy()
    opaque = alpha_hw > 8
    luma_hw = (0.299 * arr_hw[:, :, 0] + 0.587 * arr_hw[:, :, 1]
               + 0.114 * arr_hw[:, :, 2])
    print(f"luma={float(luma_hw[opaque].mean()):.1f}")

    # No dressings on this tier, so the floor is the base skin's own plumage
    # luma — any drop below it would mean something is dimming the bird.
    assert float(luma_hw[opaque].mean()) >= 90

    # Lenses stay perfect: no crack colour, full black lens area intact.
    lens = int((np.all(np.abs(arr_hw - np.array(SHADE_BLACK)) < 14, axis=2)
                & opaque).sum())
    print(f"lens_px={lens}")
    assert lens >= 60, f"lenses eroded: {lens}"

    print("All asserts passed.")

    raw    = [_build_frame(a) for a in _HURT_ANGLES]
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
    lbl = font.render("ruffled-feathers — round 1   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
