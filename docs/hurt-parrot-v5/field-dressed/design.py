"""
`field-dressed` — hurt-parrot concept exploration (standalone, not wired in).

Thesis: the wound emerges from under the dressing. A medic got to this bird,
then it went straight back out.

Where `bandaged-cheek` spread two small strips around the sprite, this one
commits to a single proper chest dressing — a taped pad with the red cross on
it — and lets one raked cut run out from beneath its lower hem and down across
the belly. That "runs out from under" relationship is the whole story: a pad
parked beside a wound is decoration, a pad the wound escapes from is treatment.
One pad, one wound, one cross: a second pad on the jaw pulled the eye off the
thesis cut and, at 1x, fused with the chest into a single shapeless band, so
the sprite spends its entire damage budget on one legible event.
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

# Tape, not gauze: a touch greyer and darker than the pad so the tabs read as a
# different material holding it on rather than as pad that spilled over the hem.
STITCH     = (180, 170, 160)
# Dressing set. Slightly warmer and duller than a near-white: field gauze that
# has been handled, with a dark hem so each pad keeps its own edge against the
# red plumage instead of blooming into it at 1x.
GAUZE      = (198, 190, 172)
HEM        = (120, 108,  95)
CROSS      = (190,  20,  35)
SCRATCH_D  = (100,  10,  10)
SCRATCH_HL = (245, 165, 150)
# Fallback core value for the stretches of rake that cross the wing or the body
# shadow. A luma-37 core on a luma-18 covert is a cut nobody can see; this reads
# as raw flesh against dark feather and keeps the line continuous.
SCRATCH_PALE = (180, 90, 80)
# Cracks read as light caught in the fracture — near-black on a black lens
# vanishes entirely; glass chips bright, and the bright line is also the only
# thing that survives the downscale.
CRACK      = (150, 175, 205)

# Chest pad, quad rather than rectangle so it follows the barrel of the breast.
# The right edge is held in to x=31 to keep it clear of the wing root, which
# swings across the upper body on the downstroke frames.
CHEST_PAD = [(20, 23), (30, 21), (31, 34), (21, 36)]
# Cross arms cropped well inside the pad: the mark needs a clear ring of gauze
# all the way round, and a cross that touches its own hem stops reading as a
# cross and starts reading as a torn patch.
CHEST_H   = ((23, 28), (27, 28))
CHEST_V   = ((25, 25), (25, 31))

# The upper rake is the thesis cut: its inboard end starts well inside the pad
# so six columns of it are swallowed by the gauze, then it surfaces below the
# bottom hem and runs thirteen clean columns out across the belly. Both rakes
# ride the belly ellipse (centre (28,38), rx 12, ry 6) rather than the breast —
# higher up they crossed the wing coverts and the body shadow, where a dark core
# on dark feather is invisible at any zoom.
UPPER_CUT = ((20, 33), (37, 43))
# Supporting mark only: shorter, parallel, and held four to six rows clear so a
# band of untouched plumage separates the two instead of them reading as one
# thick smear.
LOWER_CUT = ((22, 40), (32, 45))


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


def _lerp_pt(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t))


def _draw_ragged_cuts(surf):
    """Two raked claw-marks across the breast and flank. Each is a dark core
    with a pale lip one pixel up-and-left of it: the value pair is what makes a
    cut read as a torn ridge of feather rather than a flat stripe.

    The lip rides one to two rows above the core and is started part-way along
    rather than tracked off the geometric normal. A rounded unit normal on a
    shallow cut snaps to (0,1) and stacks the lip directly under the core, which
    reads as a fat two-tone line; the ragged partial lip reads as one edge of the
    tear catching light, and starting it late leaves the inboard end — the end
    that comes out from under the pad — as raw dark, which is where the eye
    should land.

    Both strokes are ground-aware. The dark-core/pale-lip pair only works on a
    light surface; where the rake crosses the wing or the body shadow the pair
    inverts into a pale line on dark and the lip is dropped altogether, because
    a highlight lip needs something darker underneath it to be a highlight of.
    The destination is sampled before anything is written, so the core does not
    become its own lip's ground."""
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


def _draw_chest_dressing(surf):
    """The main dressing: a taped pad square on the breast, carrying the one red
    cross on the sprite. Drawn after the rake so the upper cut disappears under
    its lower hem and surfaces again below — the pad has to be over the wound,
    not next to it, or the two stop being one event."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw

    # Hem pushed one pixel outboard of the pad instead of inset into it. An inset
    # outline ate a third of the gauze field, which at 1x left a dark-rimmed grey
    # chip rather than a pad; run outside, the pad keeps its full white mass and
    # still gets the dark edge that stops it blooming into the red plumage.
    cx = sum(p[0] for p in CHEST_PAD) / len(CHEST_PAD)
    cy = sum(p[1] for p in CHEST_PAD) / len(CHEST_PAD)
    grown = []
    for px, py in CHEST_PAD:
        vx, vy = px - cx, py - cy
        L = max(1e-3, math.hypot(vx, vy))
        grown.append((px + vx / L * 1.6, py + vy / L * 1.6))
    d.polygon(layer, HEM,   grown)
    d.polygon(layer, GAUZE, CHEST_PAD)

    # The one piece of universal shorthand in the sprite, and the first thing a
    # player parses.
    d.line(layer, CROSS, CHEST_H[0], CHEST_H[1], 2)
    d.line(layer, CROSS, CHEST_V[0], CHEST_V[1], 2)

    # Tape tabs straddling the hem. They are what keep the pad from reading as a
    # white sticker: something visibly holds it on, and it runs onto plumage.
    d.line(layer, STITCH, (18, 26), (21, 26), 1)
    d.line(layer, STITCH, (18, 32), (21, 32), 1)
    d.line(layer, STITCH, (29, 23), (32, 23), 1)
    d.line(layer, STITCH, (29, 31), (32, 31), 1)

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


def _draw_tail(surf):
    d = pygame.draw
    BODY_SH = (130, 12, 12)
    # Innermost feather pulled a few points off the cross red. At the old value
    # the deepest tail red and the medical cross were the same colour, so the
    # sprite carried a second red mark that competed with the one that matters.
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
    # Chest and belly carry the form modelling — hurt is told by the damage
    # marks, not by draining the light out of the plumage.
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

    # Raked over the coverts rather than under them. Below the wing the cut all
    # but vanished on the upstroke frames, and a claw that opened the breast
    # would have opened the coverts on the way through anyway. It still goes
    # down before every dressing — each pad has to sit on the wound it treats.
    _draw_ragged_cuts(surf)

    # Head hangs 1 px lower than the healthy build — small in absolute terms,
    # but it breaks the proud upward line of the original silhouette.
    _aaellipse(surf, (155, 15, 20),   (48, 24), 12, 11)
    _aaellipse(surf, BODY,            (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90),   (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _draw_sunglasses(surf, 50, 20)
    _draw_cracked_lens(surf)
    _draw_chest_dressing(surf)

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
    arr_hw = pygame.surfarray.pixels3d(frame).transpose(1, 0, 2)  # H×W×3
    alpha_hw = pygame.surfarray.pixels_alpha(frame).T             # H×W

    GAUZE_C = np.array(GAUZE)
    CROSS_C = np.array(CROSS)
    SCRATCH_D_C = np.array(SCRATCH_D)
    SCRATCH_HL_C = np.array(SCRATCH_HL)

    gauze_count = int(np.all(np.abs(arr_hw - GAUZE_C) < 12, axis=2).sum())
    cross_count = int(np.all(np.abs(arr_hw - CROSS_C) < 12, axis=2).sum())

    opaque = alpha_hw > 8
    luma_hw = (0.299 * arr_hw[:, :, 0] + 0.587 * arr_hw[:, :, 1]
               + 0.114 * arr_hw[:, :, 2])
    luma = float(luma_hw[opaque].mean())

    # Wound ink that survived onto a readable ground. The pale fallback core is
    # deliberately excluded: it proves the line stayed continuous over the wing,
    # but only the dark/highlight pair on light plumage is the wound read.
    wound_mask = np.all(np.abs(arr_hw - SCRATCH_D_C) < 20, axis=2) | \
                 np.all(np.abs(arr_hw - SCRATCH_HL_C) < 20, axis=2)
    wound_pixels = int(wound_mask.sum())

    opaque_count = int(opaque.sum())
    gauze_frac = gauze_count / max(opaque_count, 1)

    print(f"gauze={gauze_count} ({gauze_frac:.1%} of opaque), "
          f"cross={cross_count}, wound_px={wound_pixels}, luma={luma:.1f}")

    assert gauze_count   >= 95,   f"gauze too low: {gauze_count}"
    assert gauze_count   <= 200,  f"gauze overload (mummy): {gauze_count}"
    assert gauze_frac    <= 0.15, f"gauze fraction too high (>{15}%): {gauze_frac:.1%}"
    assert cross_count   >= 10,   f"cross too faint: {cross_count}"
    assert cross_count   <= 25,   f"two-cross bleed: {cross_count}"
    assert wound_pixels  >= 20,   f"wound too faint: {wound_pixels}"
    assert luma          >= 95,   f"luma too dark: {luma:.1f}"

    # One pad only. Gauze appearing low and outboard means a jaw dressing crept
    # back in and the sprite is carrying two damage sites again.
    jaw_zone = np.zeros_like(opaque)
    jaw_zone[30:, 33:] = True
    gauze_in_jaw = int(np.all(np.abs(arr_hw - GAUZE_C) < 12, axis=2)[jaw_zone].sum())
    assert gauze_in_jaw <= 30, f"jaw pad crept back: {gauze_in_jaw} gauze px in jaw zone"

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
    lbl = font.render("field-dressed — round 2   (4x / 2x / 1x day + night)",
                      True, (225, 225, 245))
    canvas.blit(lbl, (margin, canvas_h - margin - lbl.get_height() + 4))

    out_path = os.path.join(OUT_DIR, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {canvas_w}x{canvas_h} -> {out_path}")
