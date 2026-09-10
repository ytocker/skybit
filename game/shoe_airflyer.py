import pygame


# AIR FLYER — an all-white chunky low-top basketball sneaker. The read is a
# tall clean off-white midsole stack capped by a slim grey outsole edge, with a
# single dark-grey check swoop that starts low+thin at the heel, dips to a belly
# at midfoot, then kicks up and tapers to a sharp point at the toe. A boxy heel
# collar and flat toe box give it the chunky basketball stance, not a loafer.
# All geometry is proportional so the same call serves the product shot and the
# tiny bird-foot size; below ~24px a single high-contrast dark stroke over a
# bright midsole bar guarantees the silhouette still reads.

_CREAM   = (244, 242, 235)   # off-white upper
_CREAM_D = (210, 207, 198)   # upper shadow / 1px edges
_MID     = (252, 251, 247)   # midsole, brighter than the upper so it pops
_MID_D   = (222, 219, 210)
# One value step darker than before so the hero swoop separates crisply from
# both the cream upper above and the bright white midsole below.
_GREY    = (118, 121, 132)   # the side swoop — the clear dark hero shape
_GREY_D  = (92, 95, 106)     # swoop trailing lip
_OUT     = (120, 122, 130)   # slim outsole lip under the white midsole
_SEAM    = (200, 197, 188)   # stitched toe-panel seam + air-pill outline
_PERF    = (196, 193, 184)   # toe perforation dots


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile AIR FLYER sneaker into box (x,y,w,h)."""
    # Work in facing=1 (toe right) space, then mirror coordinates so one body
    # of geometry serves both directions.
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    # Bottom ~22% of the box is the sole stack; the low-top upper stays inside.
    mid_top = 0.78   # top of the chunky midsole
    up_top  = 0.30   # crown of the boxy low-top upper

    # ── tiny-size branch: at bird-foot scale, detail dissolves into mush, so ──
    # force the read down to the two cues that matter — a bright white midsole
    # baseline bar and one full-width dark diagonal check. No laces/perf.
    if w < 24:
        # Cream upper block so the silhouette has a body above the sole.
        poly(_CREAM, [
            (0.06, 0.66), (0.06, 0.30), (0.60, 0.26),
            (0.92, 0.46), (0.96, 0.66),
        ])
        # One bold full-width dark check sweeping low heel → belly → sharp toe,
        # sitting just above the sole so the white bar stays visible below it.
        # Built thicker than the upper detail so it is unmistakably the hero.
        poly(_GREY, [
            (0.10, 0.58), (0.42, 0.76), (0.94, 0.36),
            (0.92, 0.55), (0.44, 0.68), (0.13, 0.50),
        ])
        # Bright midsole bar across the full footprint — the brightest baseline.
        poly(_MID, [
            (0.02, 1.00), (0.98, 1.00), (0.98, 0.78), (0.02, 0.82),
        ])
        return

    # ── slim grey outsole lip — a thin tread band on the ground line ───────────
    # Kept narrow so the white midsole above reads as the tall stacked AF1 sole.
    poly(_OUT, [
        (0.03, 1.00), (0.97, 1.00), (0.99, 0.945),
        (0.95, 0.925), (0.05, 0.925), (0.02, 0.965),
    ])

    # ── thick stacked white midsole — the bright base that grounds the shoe ────
    # Tall and clean (the AF1 sole is a slab), sitting on the slim grey lip.
    poly(_MID, [
        (0.02, 0.945), (0.04, mid_top), (0.16, 0.735),
        (0.84, 0.735), (0.96, mid_top), (0.985, 0.945),
        (0.95, 0.925), (0.05, 0.925),
    ])
    # Soft heel-side shadow on the midsole for a touch of volume.
    poly(_MID_D, [
        (0.02, 0.945), (0.04, mid_top), (0.07, mid_top),
        (0.05, 0.945),
    ])

    # ── stylized "air pill" embossed on the heel midsole ───────────────────────
    # A tiny grey-outlined oval (no text), an AF1 signature. Gated off below the
    # size where a 2px ring just turns to mud.
    if w >= 28:
        pcx, pcy = px(0.13), py(0.845)
        pw, ph = max(3, int(w * 0.085)), max(2, int(h * 0.075))
        pill = pygame.Rect(0, 0, pw, ph)
        pill.center = (int(pcx), int(pcy))
        pygame.draw.ellipse(surf, _SEAM, pill, max(1, int(w * 0.01)))

    # ── upper: a boxy cream low-top body — flat toe-box top + square heel ──────
    # The crown is flattened (vs a rounded loafer) so the stance reads basketball.
    poly(_CREAM, [
        (0.06, mid_top), (0.06, 0.42), (0.09, up_top),
        (0.34, 0.30), (0.58, 0.31), (0.74, 0.40),
        (0.88, 0.52), (0.93, 0.66), (0.94, mid_top),
    ])
    # Toe cap front edge + heel back edge get a 1px darker seam for definition.
    poly(_CREAM_D, [
        (0.90, 0.62), (0.94, mid_top), (0.905, mid_top), (0.875, 0.64),
    ])
    poly(_CREAM_D, [
        (0.06, mid_top), (0.06, 0.42), (0.085, 0.42), (0.085, mid_top),
    ])

    # ── the hero cue: one dark-grey check swoop, heel→toe ──────────────────────
    # Low + thin at the heel anchor, sweeping down to a belly at midfoot, then
    # kicking up and tapering to a sharp point toward the toe. Its baseline sits
    # above the midsole so a clean white band of sole shows below it. Built as
    # one filled stroke: outer (upper) curve out to the toe point, then the
    # inner (lower) curve back to the thick heel anchor.
    poly(_GREY, [
        # heel anchor (low + thin) → outer/upper edge dipping to a fuller belly
        (0.17, 0.715), (0.30, 0.705), (0.46, 0.69),
        (0.60, 0.635), (0.74, 0.555),
        (0.885, 0.455),                     # sharp up-kicked toe point
        # inner/lower edge sweeping back to the heel, lifting the baseline so a
        # clean white band of sole shows below the whole check
        (0.79, 0.575), (0.62, 0.675), (0.46, 0.725),
        (0.30, 0.735), (0.20, 0.745),
    ])
    # Thin darker lip along the swoop's trailing/lower edge for a 1px shadow.
    poly(_GREY_D, [
        (0.17, 0.715), (0.20, 0.745), (0.30, 0.735), (0.46, 0.725),
        (0.46, 0.74), (0.30, 0.75), (0.20, 0.762),
    ])

    # ── flat laces: short cream bars on a faint grey lace gap ──────────────────
    # A narrow throat shadow first, then bright bars that read when tiny.
    poly(_GREY, [
        (0.36, 0.40), (0.54, 0.385), (0.55, 0.46), (0.38, 0.50),
    ])
    bar_w = 0.045
    for i, (lx, ty) in enumerate(((0.385, 0.41), (0.435, 0.405), (0.485, 0.41))):
        poly(_CREAM, [
            (lx, ty), (lx + bar_w, ty - 0.01),
            (lx + bar_w, ty + 0.045), (lx, ty + 0.055),
        ])

    # ── square heel collar + small heel tab on the flat back ───────────────────
    # A taller, flatter back so the tab sits squarely on the collar (basketball
    # cut), instead of the rounded low loafer heel.
    poly(_CREAM, [
        (0.06, 0.42), (0.06, up_top), (0.16, 0.285),
        (0.18, 0.40), (0.10, 0.44),
    ])
    poly(_CREAM_D, [
        (0.06, 0.42), (0.06, up_top), (0.085, up_top), (0.085, 0.42),
    ])

    # ── stitched toe-panel seam — the AF1 toe cap, split from the vamp ─────────
    # A curved stitch line arcing from the swoop up over the toe box, plus a
    # small perforation cluster on the cap. Gated off below ~28px where a thin
    # curve and 1px dots dissolve into noise.
    if w >= 28:
        seam = [(px(a), py(b)) for a, b in (
            (0.71, 0.44), (0.76, 0.49), (0.79, 0.555),
            (0.805, 0.625), (0.805, 0.70),
        )]
        pygame.draw.lines(surf, _SEAM, False, seam, max(1, int(w * 0.012)))
        # Perforation cluster on the toe cap (ahead of the seam, toward the toe).
        r = max(1, int(w * 0.009))
        for dx, dy in ((0.845, 0.50), (0.88, 0.53), (0.845, 0.57),
                       (0.88, 0.485), (0.88, 0.575), (0.845, 0.62)):
            pygame.draw.circle(surf, _PERF, (int(px(dx)), int(py(dy))), r)
