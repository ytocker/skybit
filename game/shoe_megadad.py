import pygame


# MEGA DAD — rare chunky "dad shoe" runner. The whole read is BULK: a bulbous
# triple-stacked foam midsole eats the bottom ~45% of the box (versus ~22% on a
# normal sneaker), so even at 16px the eye sees a fat wedge of sole carrying a
# squat colour-blocked upper. No glow, no fantasy — believable footwear that is
# simply enormous. Three stacked foam tiers separated by carved grooves give the
# "stack height" cue; a grey body with a teal toe overlay + orange mudguard reads
# as the colour-block; a reflective lace cage and a fat heel pull-loop are the
# two small cues clamped to >=1px so they survive the worn-foot shrink.
#
# All geometry is proportional in facing=1 (toe right) space; coordinates mirror
# for facing=-1 so one body of shapes serves both directions. Unlike the slim
# homages the upper is deliberately short and round-shouldered so the sole — not
# the upper — dominates the silhouette.

_OFFW   = (232, 230, 224)   # off-white foam (top midsole tier + highlights)
_OFFW_D = (205, 203, 196)   # foam shade between tiers
_GREY   = (185, 192, 196)   # cool grey upper body (mesh/suede)
_GREY_D = (150, 158, 163)   # upper shadow / panel seams
_TEAL   = ( 42, 166, 160)   # teal toe overlay pop
_TEAL_D = ( 28, 122, 118)   # teal shade
_ORANGE = (240, 121,  46)   # orange mudguard pop
_ORANGE_D = (196,  92,  30) # orange shade
_DARK   = ( 43,  46,  51)   # dark seams / outsole / pull-loop
_DARK_HI = (96, 102, 110)   # metallic sheen on the heel loop
_REFLECT = (244, 246, 240)  # near off-white reflective lace-cage straps


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile MEGA DAD sneaker into box (x,y,w,h)."""
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, (px(a[0]), py(a[1])),
                         (px(b[0]), py(b[1])), max(1, int(round(width))))

    # The foam stack owns the bottom ~45%; the upper is squeezed into the top
    # half so the silhouette reads sole-heavy. This split IS the dad-shoe cue.
    stack_top = 0.56

    # ── dark outsole on the ground line ────────────────────────────────────────
    poly(_DARK, [
        (0.05, 0.985), (0.13, 1.00), (0.90, 1.00),
        (0.98, 0.94), (0.95, 0.90), (0.08, 0.90), (0.03, 0.95),
    ])

    # ── bulbous triple-stacked foam midsole (the hero mass) ─────────────────────
    # One fat outer foam wall, rounded out at toe and heel so it bulges past the
    # upper. Drawn as a single big block first; carved grooves + a shade band
    # then split it into three readable tiers.
    poly(_OFFW, [
        (0.06, 0.93), (0.02, 0.82), (0.05, 0.70),
        (0.14, stack_top), (0.86, stack_top), (0.95, 0.68),
        (0.99, 0.80), (0.95, 0.92),
    ])

    # Carved grooves split the wall into THREE countable pillows. Each groove is
    # cut with the darkest seam colour (a near-value shade vanishes at icon scale)
    # and is ~0.06h wide, then capped with a 1px off-white highlight lip on its
    # UPPER edge so the tier above catches light and pops forward.
    groove_w = max(2, int(round(h * 0.06)))
    lip_w = max(1, int(round(h * 0.012)))
    for gy in (0.71, 0.82):
        pts = [(px(t), py(gy + 0.012 * (1 if i % 2 else -1)))
               for i, t in enumerate((0.07, 0.28, 0.50, 0.72, 0.93))]
        pygame.draw.lines(surf, _GREY_D, False, pts, groove_w)
        # Bright lip riding the top of each carved groove = the lit tier edge.
        lip = [(px(t), py(gy - 0.030 + 0.012 * (1 if i % 2 else -1)))
               for i, t in enumerate((0.07, 0.28, 0.50, 0.72, 0.93))]
        pygame.draw.lines(surf, _OFFW, False, lip, lip_w)

    # ── upper: cool-grey colour-blocked body (squat, round-shouldered) ──────────
    # Sits low and stubby on the foam. A dark collar notch carves a real ankle
    # opening into the top rather than leaving a featureless grey dome.
    poly(_GREY, [
        (0.12, stack_top), (0.13, 0.34), (0.22, 0.22),
        (0.40, 0.18), (0.58, 0.20), (0.66, 0.30),
        (0.74, 0.42), (0.88, 0.50), (0.88, stack_top),
    ])
    # Heel-counter shadow gives the rear upper depth.
    poly(_GREY_D, [
        (0.12, stack_top), (0.125, 0.40), (0.20, 0.26),
        (0.27, 0.30), (0.22, 0.44), (0.215, stack_top),
    ])
    # Dark ankle-opening notch scooped out of the collar so the upper reads as a
    # shoe you step into, not a solid grey blob.
    poly(_DARK, [
        (0.26, 0.215), (0.42, 0.185), (0.55, 0.205),
        (0.49, 0.275), (0.36, 0.285), (0.28, 0.26),
    ])

    # ── orange mudguard — dominant wrapping BLOCK, not a stripe ──────────────────
    # A tall orange mass (~0.15h) wrapping the foot/foam join along the whole
    # length and sweeping UP over the toe. This solid block is the 16px hero cue,
    # so it must read as a colour MASS rather than a thin band. Drawn before the
    # teal so the teal toe-cap still caps the very front on top of it.
    poly(_ORANGE, [
        (0.10, stack_top), (0.92, stack_top), (0.91, 0.44),
        (0.74, 0.41), (0.58, 0.47), (0.34, 0.49),
        (0.16, 0.51), (0.10, 0.54),
    ])
    # Lower shade keeps the block reading as 3D where it meets the foam.
    poly(_ORANGE_D, [
        (0.10, stack_top), (0.92, stack_top),
        (0.92, stack_top - 0.045), (0.10, stack_top - 0.025),
    ])

    # ── teal rounded toe-CAP at the very front (front colour pop) ───────────────
    # Pulled forward into a fat rounded block capping the toe so it reads as the
    # toe of the shoe, not a side panel set back on the flank. Sits on top of the
    # orange so the front of the shoe is unmistakably a capped toe.
    poly(_TEAL, [
        (0.76, 0.40), (0.87, 0.46), (0.905, 0.53),
        (0.895, 0.625), (0.72, 0.625), (0.70, 0.47),
    ])
    poly(_TEAL_D, [
        (0.86, 0.47), (0.905, 0.53), (0.895, 0.625),
        (0.84, 0.625),
    ])

    # ── lace cage: two FAT high-contrast reflective straps ──────────────────────
    # Two fat straps beat three thin same-value bars, which read as muddy noise at
    # 1x. Near off-white (_REFLECT) with a hard _DARK shadow under each so the
    # cage pops as reflective webbing and survives the worn-foot shrink.
    cage_w = max(2, int(round(h * 0.10)))
    # Dark throat gap first so the straps read as crossing a hole, not floating.
    poly(_DARK, [
        (0.34, 0.27), (0.56, 0.23), (0.60, 0.32),
        (0.40, 0.40),
    ])
    for tx0, ty0, tx1, ty1 in (
        (0.34, 0.36, 0.55, 0.32),
        (0.33, 0.49, 0.56, 0.44),
    ):
        line(_DARK, (tx0, ty0 + 0.035), (tx1, ty1 + 0.035), cage_w)
        line(_REFLECT, (tx0, ty0), (tx1, ty1), cage_w)

    # ── fat heel pull-loop standing PROUD of the back silhouette ────────────────
    # Pushed back past the heel edge (~0.04 vs the upper's 0.12 back wall) and up
    # over the collar so it clearly juts out as a graspable tab, not a flat flap
    # flush with the heel. A dark core inside the metallic arch reads as the hole.
    poly(_DARK_HI, [
        (0.07, 0.31), (0.02, 0.15), (0.08, 0.06),
        (0.22, 0.06), (0.29, 0.16), (0.25, 0.31),
        (0.20, 0.23), (0.14, 0.20), (0.10, 0.25),
    ])
    poly(_DARK, [
        (0.105, 0.255), (0.075, 0.155), (0.115, 0.105),
        (0.205, 0.105), (0.245, 0.165), (0.215, 0.245),
        (0.175, 0.195), (0.135, 0.195),
    ])
