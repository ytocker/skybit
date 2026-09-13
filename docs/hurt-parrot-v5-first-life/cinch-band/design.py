"""
`cinch-band` — one gauze wrap, the minimum medical intervention.

The first-life-lost skin has to read as "hurt" from a single glance at 1x while
leaving room for the last-life skin to escalate on top of it. So this concept
spends its whole budget on one idea: a single band cinched around the belly.
No cross, no plasters, no wounds — those are the later tier's vocabulary, and
holding them back is what makes the escalation legible as a *count* rather than
a redesign.

The band sits at y 36-42, clear of the last-life chest pad footprint (y 21-36)
so the two tiers stack without repainting either. A 1 px back-contour sliver
above the left end sells the wrap as going around a 3D barrel instead of being
painted on the front. The knot is the only element allowed past the body
contour: at 1x the silhouette is all a player can parse, so the concept needs
exactly one new bump on it — a lumpy asymmetric lozenge with two short tails,
low and forward where the eye already tracks the bird's leading edge.
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
CONTOUR    = (165, 158, 142)
CONTACT_SH = ( 62,  40,  42)


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


def _draw_cinch_band(surf):
    """The single wrap. Drawn last so it sits over plumage, wing and belly sheen.

    Everything except the knot is clipped to the existing silhouette — a band
    that bulged past the body would read as a separate floating object at 1x.
    The knot is the deliberate exception and is stamped straight onto the
    surface so it survives into the blackout read.

    The wing sweeps down to y 44-49 over this whole footprint on all four flap
    frames, so there is no band placement that the wing never touches. Passing
    the band *behind* the wing would hide most of it on the down-flap frames and
    the skin would flicker between "hurt" and "fine", so the band goes on top
    and earns that read with a 1 px contact shadow along its lower hem.
    """
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw

    # Dips 1 px at centre so the band follows the belly barrel, not a flat tape
    front = [(16, 37), (28, 36), (40, 37), (40, 42), (28, 43), (16, 42)]
    d.lines(layer, CONTACT_SH, False, [(16, 43), (28, 44), (40, 43)], 1)
    d.polygon(layer, GAUZE, front)
    d.lines(layer, HEM, False, [(16, 37), (28, 36), (40, 37)], 1)
    d.lines(layer, HEM, False, [(16, 42), (28, 43), (40, 42)], 1)

    # Far side of the wrap, disappearing into the body shadow
    d.line(layer, CONTOUR, (16, 35), (22, 34), 1)

    for x in range(18, 39, 4):
        d.circle(layer, STITCH, (x, 36), 1)

    _stamp_clipped(surf, layer)

    # Bumpier than a rectangle so the new silhouette bump reads as tied cloth
    knot_pts = [(14, 39), (16, 37), (20, 38), (19, 42), (14, 42)]
    d.polygon(surf, GAUZE, knot_pts)
    d.polygon(surf, HEM,   knot_pts, 1)
    d.line(surf, GAUZE, (15, 42), (12, 45), 2)
    d.line(surf, HEM,   (15, 42), (12, 45), 1)
    d.line(surf, GAUZE, (17, 43), (16, 47), 2)
    d.line(surf, HEM,   (17, 43), (16, 47), 1)


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

    _draw_cinch_band(surf)

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

    GAUZE_A = np.array(GAUZE)

    # The band must survive every flap frame identically — a wing that ate part
    # of it on the down-frames would make the injury blink in and out
    counts = []
    for ang in _HURT_ANGLES:
        f = _build_hurt_frame(ang)
        a = pygame.surfarray.pixels3d(f).transpose(1, 0, 2)
        counts.append(int(np.all(np.abs(a - GAUZE_A) < 12, axis=2).sum()))
        del a
    print(f"gauze per frame = {counts}")
    assert max(counts) - min(counts) == 0, f"band flickers across frames: {counts}"

    frame = _build_hurt_frame(10)
    arr_hw = pygame.surfarray.pixels3d(frame).transpose(1, 0, 2)
    alpha_hw = pygame.surfarray.pixels_alpha(frame).T

    GAUZE_C = np.array(GAUZE)
    HEM_C   = np.array(HEM)

    gauze_mask = np.all(np.abs(arr_hw - GAUZE_C) < 12, axis=2)
    opaque = alpha_hw > 8
    opaque_count = int(opaque.sum())
    gauze_count = int(gauze_mask.sum())
    gauze_frac = gauze_count / max(opaque_count, 1)

    luma_hw = (0.299 * arr_hw[:, :, 0] + 0.587 * arr_hw[:, :, 1]
               + 0.114 * arr_hw[:, :, 2])
    luma = float(luma_hw[opaque].mean())

    band_zone = np.zeros_like(opaque)
    band_zone[34:49, 11:43] = True
    band_gauze = int(gauze_mask[band_zone].sum())

    # Silhouette break: gauze outside BOTH body ellipses in the knot footprint
    yy, xx = np.mgrid[0:SPRITE_H, 0:SPRITE_W]
    in_body = (((xx - 32) / 19.0) ** 2 + ((yy - 32) / 14.0) ** 2 <= 1.0) | \
              (((xx - 34) / 19.0) ** 2 + ((yy - 35) / 14.0) ** 2 <= 1.0)
    knot_zone = np.zeros_like(opaque)
    knot_zone[37:48, 12:21] = True
    knot_break = int((gauze_mask & knot_zone & ~in_body).sum())

    # No cross, no plasters: gauze outside the band footprint must stay near zero
    stray = gauze_count - band_gauze

    print(f"gauze={gauze_count} ({gauze_frac:.1%} of opaque), band_gauze={band_gauze}, "
          f"knot_break={knot_break}, stray={stray}, luma={luma:.1f}")

    assert band_gauze >= 30, f"band too faint: {band_gauze}"
    assert knot_break >= 4,  f"knot does not break silhouette: {knot_break}"
    assert stray == 0,       f"gauze outside the band footprint: {stray}"
    assert gauze_frac <= 0.12, f"single wrap should stay light: {gauze_frac:.1%}"
    assert luma >= 95, f"luma too dark: {luma:.1f}"

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
    lbl = font.render("cinch-band — round 1   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
