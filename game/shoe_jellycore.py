import pygame


# JELLYCORE — epic translucent gel runner. The read is a GUMMY shoe: a
# glossy jelly upper sitting on a see-through candy sole you can read the
# ground through. The hero cues are (1) the pink->cyan translucent outsole,
# (2) the wet specular gloss + inner gel bubbles on the upper, and (3) the
# soft inner bloom along the midsole. Because translucency is the whole
# point, the body is composited onto a per-pixel-alpha temp surface with
# alpha'd fills, then blit down; only the silhouette outline stays fully
# opaque so the shoe survives the 40px foot read instead of dissolving.
#
# All geometry is proportional (px/py over the 0..1 box) so the same call
# feeds the 104x58 product shot and the 17x11 worn foot. Strokes clamp to
# >=1px so the gloss/lace cues don't vanish on downscale.

_PINK    = (255, 143, 208)
_CYAN    = ( 96, 230, 255)
_LILAC   = (201, 168, 255)
_DEEP    = ( 58,  46,  85)
_WHITE   = (255, 255, 255)
# High-key opaque substrate laid down first so every translucent band
# composites over a bright base — translucency over light = candy, over
# dark = bruise. A pale lilac reads as frosted gel, not paper.
_BASE    = (244, 238, 252)


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile JELLYCORE sneaker into box (x,y,w,h)."""
    # A local SRCALPHA layer lets the sole/upper be genuinely translucent
    # (so whatever is behind the shoe bleeds through) while we keep the
    # outline crisp. Work in toe-right space then mirror via facing.
    iw, ih = max(1, int(round(w))), max(1, int(round(h)))
    pad = max(2, int(round(w * 0.06)))
    lay = pygame.Surface((iw + pad * 2, ih + pad * 2), pygame.SRCALPHA)

    def px(t):
        return pad + (t * iw if facing == 1 else (1.0 - t) * iw)

    def py(t):
        return pad + t * ih

    def poly(color, pts, alpha=255):
        col = (color[0], color[1], color[2], alpha) if len(color) == 3 else color
        pygame.draw.polygon(lay, col, [(px(a), py(b)) for a, b in pts])

    def aapoly(color, pts, alpha=255):
        col = (color[0], color[1], color[2], alpha) if len(color) == 3 else color
        pts = [(px(a), py(b)) for a, b in pts]
        pygame.draw.polygon(lay, col, pts)
        pygame.draw.aalines(lay, col, True, pts)

    def line(color, a, b, width, alpha=255):
        col = (color[0], color[1], color[2], alpha) if len(color) == 3 else color
        pygame.draw.line(lay, col, (px(a[0]), py(a[1])), (px(b[0]), py(b[1])),
                         max(1, int(round(width))))

    def bubble(cx, cy, r, alpha):
        # A trapped air/light pocket: lighter-than-surround fill, a bright
        # rim, and a hard white specular hotspot. Reads as a lit cavity, not
        # a dark pellet. Sub-3px bubbles are noise, so they're clamped out.
        rr = max(1, int(round(w * r)))
        if rr < 3:
            return
        c = (px(cx), py(cy))
        pygame.draw.circle(lay, (*_BASE, min(255, alpha + 40)), c, rr)
        pygame.draw.circle(lay, (*_WHITE, min(255, alpha)), c, rr,
                           max(1, int(rr * 0.28)))
        pygame.draw.circle(lay, (*_WHITE, 255),
                           (c[0] - rr * 0.32, c[1] - rr * 0.32),
                           max(1, int(rr * 0.4)))

    sole_top = 0.74

    # ── opaque high-key substrate — fill the whole silhouette with a near-
    # white pale lilac at full alpha BEFORE any translucent band. This is
    # the bright candy ground the gel sits on; without it the translucency
    # averages toward the dark outline and bruises. ──
    substrate = [
        (0.10, 0.46), (0.17, 0.30), (0.30, 0.23), (0.45, 0.24),
        (0.58, 0.30), (0.74, 0.40), (0.88, 0.52), (0.965, 0.86),
        (0.94, 0.97), (0.86, 0.995), (0.10, 0.995),
    ]
    poly(_BASE, substrate, alpha=255)

    # ── soft inner bloom — a wide low-alpha halo under the midsole so the
    # shoe reads as if it is glowing from inside before any solid colour. ──
    glow = pygame.Surface(lay.get_size(), pygame.SRCALPHA)
    gcx, gcy = px(0.42), py(0.80)
    grx, gry = int(iw * 0.62), int(ih * 0.40)
    for k in range(5, 0, -1):
        a = 18 + (5 - k) * 9  # peak ~45 at the core so the bloom truly blooms
        pygame.draw.ellipse(glow, (*_CYAN, a),
                            (gcx - grx * k / 5, gcy - gry * k / 5,
                             grx * 2 * k / 5, gry * 2 * k / 5))
    # A warm pink bloom node near the toe balances the cool cyan core so the
    # inside glow reads two-tone candy rather than a single cyan wash.
    pcx, pcy = px(0.78), py(0.82)
    prx, pry = int(iw * 0.34), int(ih * 0.30)
    for k in range(4, 0, -1):
        a = 16 + (4 - k) * 9
        pygame.draw.ellipse(glow, (*_PINK, a),
                            (pcx - prx * k / 4, pcy - pry * k / 4,
                             prx * 2 * k / 4, pry * 2 * k / 4))
    lay.blit(glow, (0, 0))

    # ── translucent candy outsole — pink (toe) -> lilac -> cyan (heel),
    # drawn as banded horizontal slabs so the gradient reads, all at low
    # alpha so the ground shows through. This is THE jelly tell. ──
    sole = [
        (0.05, 0.985), (0.12, sole_top), (0.88, sole_top),
        (0.965, 0.86), (0.94, 0.97), (0.86, 0.995), (0.10, 0.995),
    ]
    poly(_LILAC, sole, alpha=160)
    bands = 9
    for i in range(bands):
        t0 = i / bands
        t1 = (i + 1) / bands
        col = _lerp(_CYAN, _PINK, t0)  # heel(cyan,left) -> toe(pink,right)
        xa = 0.07 + t0 * 0.88
        xb = 0.07 + t1 * 0.88
        poly(col, [
            (xa, 0.985 - 0.02 * (1 - abs(t0 - 0.5) * 2)),
            (xa, sole_top + 0.02),
            (xb, sole_top + 0.02),
            (xb, 0.985 - 0.02 * (1 - abs(t1 - 0.5) * 2)),
        ], alpha=130)

    # Two GUARANTEED opaque candy bands inside the sole — one cyan at the
    # heel, one pink at the toe, at full alpha. When everything translucent
    # averages out at the 40px foot read, these keep the two-tone identity
    # alive so the foot stays candy, not the dark outline colour.
    poly(_CYAN, [
        (0.10, 0.90), (0.10, sole_top + 0.04), (0.30, sole_top + 0.04),
        (0.27, 0.90),
    ], alpha=255)
    poly(_PINK, [
        (0.70, 0.90), (0.72, sole_top + 0.04), (0.92, sole_top + 0.04),
        (0.93, 0.86), (0.90, 0.92),
    ], alpha=255)

    # Glossy meniscus highlight running along the top of the sole — the
    # wet line where the jelly upper meets the candy sole. Full white at
    # the seam is the cheapest, most legible "wet surface" jelly cue.
    line(_WHITE, (0.13, sole_top + 0.015), (0.86, sole_top + 0.015),
         max(1, h * 0.045), alpha=255)

    # Two big air pockets suspended IN the clear sole — light, not pellets.
    bubble(0.40, 0.87, 0.06, 150)
    bubble(0.68, 0.85, 0.05, 140)

    # ── glossy jelly upper — rounded wet body, semi-translucent so the
    # candy hue carries up into it but solid enough to hold the shoe shape. ─
    upper = [
        (0.10, sole_top + 0.01), (0.10, 0.46), (0.17, 0.30),
        (0.30, 0.23), (0.45, 0.24), (0.58, 0.30),
        (0.74, 0.40), (0.88, 0.52), (0.93, 0.66),
        (0.93, sole_top + 0.01),
    ]
    aapoly(_PINK, upper, alpha=190)
    # Lilac core tint low on the upper to bridge into the sole gradient.
    poly(_LILAC, [
        (0.10, sole_top + 0.01), (0.10, 0.52), (0.55, 0.46),
        (0.93, 0.64), (0.93, sole_top + 0.01),
    ], alpha=130)
    # Cyan cast at the heel so the upper echoes the sole's two-tone candy.
    poly(_CYAN, [
        (0.10, sole_top + 0.01), (0.10, 0.46), (0.26, 0.30),
        (0.30, 0.50), (0.20, sole_top + 0.01),
    ], alpha=130)
    # An opaque cyan heel slab so the upper carries the candy two-tone even
    # when the translucent washes average out at foot scale.
    poly(_CYAN, [
        (0.10, 0.62), (0.10, 0.46), (0.20, 0.38), (0.22, 0.60),
    ], alpha=255)

    # Inner gel bubbles trapped in the jelly upper — 3 light air pockets.
    bubble(0.34, 0.40, 0.055, 165)
    bubble(0.52, 0.50, 0.045, 150)
    bubble(0.68, 0.56, 0.04, 140)

    # ── wet specular gloss — a bright curved sweep over the toe shoulder so
    # the upper reads glassy/wet, plus a thin rim-light along the top edge. ─
    poly(_WHITE, [
        (0.45, 0.27), (0.62, 0.31), (0.74, 0.42),
        (0.66, 0.44), (0.56, 0.36), (0.45, 0.33),
    ], alpha=150)
    line(_WHITE, (0.18, 0.31), (0.43, 0.25), max(1, h * 0.04), alpha=170)

    # ── frosted semi-clear lace loops — two pale arches over the throat,
    # low-alpha so they read as frosted gel, not solid string. ──
    for cx, cy, rr in ((0.30, 0.34, 0.085), (0.44, 0.33, 0.085)):
        rad = max(1, int(round(w * rr)))
        c = (px(cx), py(cy))
        pygame.draw.circle(lay, (*_WHITE, 90), c, rad, max(1, int(round(w * 0.02))))
        pygame.draw.circle(lay, (*_WHITE, 150), c, rad, max(1, int(round(w * 0.01))))

    # ── crisp silhouette outline — fully opaque so the shape survives 40px
    # even though everything inside it is translucent. Combine the upper +
    # sole into one closed contour. ──
    contour = [
        (0.10, 0.46), (0.17, 0.30), (0.30, 0.23), (0.45, 0.24),
        (0.58, 0.30), (0.74, 0.40), (0.88, 0.52), (0.965, 0.86),
        (0.94, 0.97), (0.86, 0.995), (0.10, 0.995),
    ]
    pts = [(px(a), py(b)) for a, b in contour]
    pygame.draw.polygon(lay, (*_DEEP, 235), pts, max(1, int(round(w * 0.02))))
    pygame.draw.aalines(lay, (*_DEEP, 235), True, pts)

    surf.blit(lay, (x - pad, y - pad))
