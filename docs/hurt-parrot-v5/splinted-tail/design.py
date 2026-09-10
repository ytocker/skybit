"""
`splinted-tail` — hurt-parrot V5 concept: shifted jaw pad + splinted tail.

The jaw wrap moves 4 px left so its right edge clears the face ellipse.
A vertical gauze splint wraps the root of the snapped tail feather — the
dressing sits on the break rather than beside it, and its footprint keeps
body red on all four sides so the gauze stays high-contrast. A hem spine
down the long axis reads as the stick. Stitched tabs left and right; no
cross, the jaw pad owns the only red mark on the sprite.
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
# Tarnished rather than the healthy bird's bright gold — the frame took the same
# beating the lens did.
SHADE_FRAME = (220, 175, 40)

STITCH     = (180, 170, 160)
# Dressing set. Slightly warmer and duller than the old brow strip's near-white:
# field gauze that has been handled, with a dark hem so each strip keeps its own
# edge against the red plumage instead of blooming into it at 1x.
GAUZE      = (198, 190, 172)
HEM        = (120, 108,  95)
CROSS      = (190,  20,  35)
SCRATCH_D  = (100,  10,  10)
SCRATCH_HL = (230, 110,  90)
# Cracks read as light caught in the fracture. Round 1 drew them near-black on a
# black lens, which vanished entirely; glass chips bright, and the bright line is
# also the only thing that survives the downscale.
CRACK      = (150, 175, 205)

UPPER_CUT = ((14, 35), (28, 29))
LOWER_CUT = ((15, 40), (24, 35))


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
    # A chunk torn out of the primaries, punched as transparency rather than
    # painted dark so the break survives the outline pass and the 1x downscale.
    # Widened along the primaries edge: at 1x a 4px notch closes up, an 8px one
    # still reads as a bite taken out of the wing.
    d.polygon(w, (0,0,0,0),   [(41,11),(53,17),(47,25),(43,16)])
    return pygame.transform.rotate(w, angle_deg)


def _draw_scratches(surf):
    """Two raked claw-marks low across the breast. Each is a dark cut with a pale
    lip drawn one pixel off-normal: the value pair is what makes it read as a
    torn ridge of feather rather than a flat drawn-on stripe.

    Composited over the wing rather than under it, and clipped to whatever the
    silhouette already covers. Under the wing the rake all but disappeared on
    the upstroke frames — and a claw that opened the breast would have opened
    the coverts on the way through anyway, so carrying it across the wing is
    both the truthful read and the only one that holds for all four frames."""
    cuts = (UPPER_CUT, LOWER_CUT)
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (x0, y0), (x1, y1) in cuts:
        dx, dy = x1 - x0, y1 - y0
        L = max(1e-3, math.hypot(dx, dy))
        # Unit normal, rounded to whole pixels so the highlight stays a crisp
        # neighbour line instead of an antialiased smear.
        ox, oy = round(-dy / L), round(dx / L)
        pygame.draw.line(layer, SCRATCH_D, (x0, y0), (x1, y1), 1)
        pygame.draw.line(layer, SCRATCH_HL,
                         (x0 + ox, y0 + oy), (x1 + ox, y1 + oy), 1)
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            if layer.get_at((x, y))[3] > 8 and surf.get_at((x, y))[3] > 8:
                surf.set_at((x, y), layer.get_at((x, y)))


def _stamp_clipped(surf, layer):
    """Composite a layer only where the silhouette already has pixels, keeping
    the destination alpha. Dressings sit *on* the bird, so any part of a strip
    that runs off the body has to be discarded rather than widening the outline
    pass into a lumpy silhouette."""
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            px = layer.get_at((x, y))
            if px[3] > 8 and surf.get_at((x, y))[3] > 8:
                surf.set_at((x, y), (px[0], px[1], px[2], surf.get_at((x, y))[3]))


JAW_PAD  = [(31, 32), (44, 30), (46, 39), (33, 42)]
# Equal-armed 5x5 cross. A lopsided one stops reading as the medical glyph and
# starts reading as a smudge once it is down at 1x.
CROSS_H  = ((36, 36), (40, 36))
CROSS_V  = ((38, 34), (38, 38))
# Splint pad sits on the snapped feather's root rather than out on the clean fan:
# the dressing has to be where the break is. The 6x9 footprint also puts gauze
# against body red on every side, which is the highest-contrast ground available.
# Seven columns wide rather than six: at six, the hem ring plus the rigid spine
# leave too little clear gauze between them for the wrap to read as cloth rather
# than as a striped chip.
SPLINT_PAD = [(13, 25), (19, 25), (19, 33), (13, 33)]


def _draw_jaw_dressing(surf):
    """The main pad, wrapped under the jaw and across the chin. Its top edge is
    held at y>=31 so it clears the cracked-lens radials entirely — the shades own
    the upper head, the gauze owns the lower, and neither crops the other.
    Running it over the head/body seam is what sells it as a wrap tied around the
    jaw rather than a patch stuck on a cheek."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw

    d.polygon(layer, GAUZE, JAW_PAD)
    d.polygon(layer, HEM, JAW_PAD, 1)

    # Red cross — the one piece of universal shorthand in the sprite, and the
    # first thing a player parses.
    d.line(layer, CROSS, *CROSS_H, 2)
    d.line(layer, CROSS, *CROSS_V, 2)

    _stamp_clipped(surf, layer)


def _draw_tail_splint(surf):
    """Vertical gauze splint over the snapped-feather root. Landed on body-red
    ground (luma 81) for maximum GAUZE contrast. The HEM spine down the long
    axis reads as the stick under the dressing. Tabs drawn before the outline
    so the hem ring is never eaten."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw

    # Tabs first so the HEM outline overwrites any overlap
    for (x0, y0), (x1, y1) in (
        ((10, 27), (12, 27)),
        ((10, 31), (12, 31)),
        ((19, 27), (21, 27)),
        ((19, 31), (21, 31)),
    ):
        d.line(layer, STITCH, (x0, y0), (x1, y1), 1)

    d.polygon(layer, GAUZE, SPLINT_PAD)
    d.polygon(layer, HEM, SPLINT_PAD, 1)

    # Rigid spine: 1px HEM line down long axis, inset 1px from both hems
    d.line(layer, HEM, (16, 26), (16, 32), 1)

    _stamp_clipped(surf, layer)


def _draw_sunglasses(surf, cx, cy):
    """Aviator shades, knocked crooked. The left lens rides 2 px low and the brow
    bar tilts to match — "took one to the face" told entirely in geometry, no
    alpha tricks, no eyelid. Only the right lens keeps its glint: one dead
    cracked lens against one still catching the sun is the whole read."""
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
    """Star fracture in the low lens: three radials of uneven length plus a chord
    linking two of them. Uneven beats symmetric — four equal spokes read as a
    cartoon dead-eye X, while a lopsided star reads as impact."""
    for end in ((41, 17), (50, 18), (47, 26)):
        pygame.draw.line(surf, CRACK, (45, 21), end, 1)
    pygame.draw.line(surf, CRACK, (43, 19), (47, 23), 1)


def _tail_feather(pts, damaged=False):
    """Tail feathers run root-right, tip-left. A damaged one is snapped short
    and kicked off-axis so the fan's clean outline breaks — silhouette damage
    survives the 1x downscale where any painted-on detail would not."""
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


def _build_hurt_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = (205,  28,  28)
    BODY_SH = (130,  12,  12)
    # Chest and belly carry the form modelling. Round 1 crushed both toward the
    # base red, which flattened the bird into a dark silhouette; hurt is told by
    # the damage marks, not by draining the light out of the plumage.
    CHEST   = (235,  80,  80)
    BELLY   = (215, 140,  45)
    BEAK    = (235, 168,   0)
    BEAK_LO = (205, 138,   0)
    BEAK_D  = (140,  92,   0)

    for i, c in enumerate(((180, 25, 35), (190, 70, 30),
                           (210, 130, 40), (230, 195, 65))):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2),
        ]
        d.polygon(surf, c, _tail_feather(pts, damaged=(i == 1)))
    d.line(surf, BODY_SH, (4, 27), (18, 31), 1)
    d.line(surf, BODY_SH, (6, 33), (20, 35), 1)

    _aaellipse(surf, BODY_SH, (34, 35), 19, 14)
    _aaellipse(surf, BODY,    (32, 32), 19, 14)
    _aaellipse(surf, CHEST,   (30, 29), 13,  8)
    _aaellipse(surf, BELLY,   (28, 38), 12,  6)

    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (205, 150, 150, 120), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _draw_scratches(surf)

    # Head hangs 1 px lower than the healthy build — small in absolute terms,
    # but it breaks the proud upward line of the original silhouette.
    _aaellipse(surf, (155, 15, 20), (48, 24), 12, 11)
    _aaellipse(surf, BODY,          (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90), (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _draw_sunglasses(surf, 50, 20)
    _draw_cracked_lens(surf)
    _draw_tail_splint(surf)
    _draw_jaw_dressing(surf)

    # Beak parted only ~2 px, and the lower mandible tucked up under the upper.
    # Dropping it further left a spur hanging off the chin that made the bird
    # read as some other species entirely.
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


def _count_exact(frame, color):
    n = 0
    for x in range(SPRITE_W):
        for y in range(SPRITE_H):
            r, g, b, a = frame.get_at((x, y))
            if a > 8 and (r, g, b) == color:
                n += 1
    return n


def _cross_margin(frame):
    """Smallest number of clear gauze pixels between any cross pixel and whatever
    is not the pad — measured on the finished frame, so hem, clipping and the
    body edge all count against it."""
    def rgb(x, y):
        r, g, b, a = frame.get_at((x, y))
        return (r, g, b) if a > 8 else None

    worst = 99
    for x in range(SPRITE_W):
        for y in range(SPRITE_H):
            if rgb(x, y) != CROSS:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                run = 0
                sx, sy = x + dx, y + dy
                while 0 <= sx < SPRITE_W and 0 <= sy < SPRITE_H:
                    c = rgb(sx, sy)
                    if c == CROSS:
                        run = 0
                    elif c == GAUZE:
                        run += 1
                    else:
                        break
                    sx, sy = sx + dx, sy + dy
                worst = min(worst, run)
    return worst


def _mean_luma(frame):
    total, n = 0.0, 0
    for x in range(SPRITE_W):
        for y in range(SPRITE_H):
            r, g, b, a = frame.get_at((x, y))
            if a < 8:
                continue
            total += 0.299 * r + 0.587 * g + 0.114 * b
            n += 1
    return total / max(1, n)


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
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    raw    = [_build_hurt_frame(a) for a in _HURT_ANGLES]
    frames = [_add_outline(f) for f in raw]

    gauze_count = _count_exact(raw[0], GAUZE)
    cross_count = _count_exact(raw[0], CROSS)
    scratch_min = min(_count_exact(f, SCRATCH_D) + _count_exact(f, SCRATCH_HL)
                      for f in raw)
    luma = _mean_luma(raw[0])
    cross_margin = _cross_margin(raw[0])

    # Summed across the jaw pad and the tail splint: the threshold is about the
    # total amount of white on the bird, not about any one dressing.
    assert gauze_count >= 35, f"Bandage too faint: {gauze_count} gauze px (need >=35)"
    assert cross_count >= 10, f"Cross missing: {cross_count} cross px (need >=10)"
    assert scratch_min >= 25, (f"Scratches fade: min {scratch_min} px on worst "
                               f"frame (need >=25)")
    assert luma >= 95, f"Body too dark: mean luma {luma:.1f} (need >=95)"
    assert cross_margin >= 2, (f"Cross crowds the pad edge: {cross_margin} px "
                               f"gauze (need >=2)")

    # Splint must be legible as a second dressing, not a speck
    splint_gauze = sum(
        1 for x in range(10, 24) for y in range(23, 36)
        if raw[0].get_at((x, y))[3] > 8
        and (raw[0].get_at((x, y))[0], raw[0].get_at((x, y))[1], raw[0].get_at((x, y))[2]) == GAUZE
    )
    assert splint_gauze >= 28, f"Splint too faint: {splint_gauze} gauze px in splint region (need >=28)"

    NIGHT, DAY = (8, 8, 20), (100, 160, 220)
    margin, gap = 20, 10
    row1 = _strip(frames, 4, gap, NIGHT)
    row2 = _strip(frames, 2, gap, NIGHT)
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

    # Day and night side by side at shipping size: the whole point of the bright
    # crack and the white gauze is that they hold on both backgrounds.
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
    lbl = font.render("splinted-tail — round 2   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
    print(f"gauze={gauze_count}  cross={cross_count}  "
          f"scratch_min={scratch_min}  luma={luma:.1f}  "
          f"cross_margin={cross_margin}  splint_gauze={splint_gauze}")
