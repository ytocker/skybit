"""AIRMAIL — par-avion ENVELOPE parcel cosmetic.

The classic airmail envelope. A ~22px slab carried below Pip that rotates with
his bank, so the read must survive the rotozoom on DAY and NIGHT sky. The
IDENTITY is the red+blue dashed candy-stripe perimeter border — no other
envelope parcel has the candy edge.

The stripe is deliberately COARSE: a solid red/blue nib pins each of the four
corners (which also doubles as a rotation-stable anchor), and only a few fat
ticks march the straight runs between them — at the downscaled 22px size a fine
dash count collapses into red/blue confetti, so 3–4 discrete ticks per edge is
the most that survives. A single saturated red stamp (top-right, held a pixel
off the border) is the one separated red mass, so the wide white quiet zone
carries the read. A faint flap V keeps the body from being a blank card.

Drawn on a 44px work surface then smoothscaled to 22 so the stripe ticks and the
keyline antialias cleanly. A baked dark outline is drawn first (slightly
inflated) so the white body reads as a shape on bright day sky; a cool night
keyline rim rides just inside the body so the white slab also reads on dark sky
without a per-mode sprite. The body is kept off the surface edges so the in-game
rotozoom never clips the corners.
"""
import pygame

# DAY airmail palette + a NIGHT-friendly cool keyline so the white slab still
# reads against a dark sky without a per-mode sprite.
PAPER = (242, 239, 230)        # warm white body
PAPER_SHADE = (222, 218, 206)  # gentle lower-body shade for a hint of volume
RED = (210,  67,  58)          # airmail red
# Airmail blue is deepened so red-vs-blue holds a VALUE difference, not just hue
# — the candy edge has to survive grayscale, where a same-value red/blue pair
# collapses to one mushy ring.
BLUE = ( 39,  79, 140)
INK = ( 42,  46,  58)          # dark ink / stamp edge
OUTLINE = ( 30,  33,  44)      # dark, high-value: reads on bright day sky
KEYLINE = (221, 230, 240)      # cool rim — the NIGHT lifeline


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static airmail slab for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # Slab body. Kept off the surface edges so the gameplay rotozoom never clips
    # the corners; a touch wider than tall for a letter feel.
    BW, BH = 34, 26
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 3

    # Baked outline frame (drawn first, slightly inflated) — the dark silhouette
    # that survives on the bright day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Paper body: faint top-to-bottom shade for a slab-of-paper feel, not a flat
    # fill. The candy stripe + stamp carry the read, so the body stays quiet.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        c = (
            int(PAPER[0] + (PAPER_SHADE[0] - PAPER[0]) * t),
            int(PAPER[1] + (PAPER_SHADE[1] - PAPER[1]) * t),
            int(PAPER[2] + (PAPER_SHADE[2] - PAPER[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # Faint flap V on top — two ink strokes from the upper corners meeting at the
    # top-centre. Kept thin/low-contrast so it suggests the closed flap without
    # competing with the stripe border.
    apex = (cx, rect.y + BH // 2 - 1)
    pygame.draw.line(surf, INK, (rect.x + 2, rect.y + 2), apex, 1)
    pygame.draw.line(surf, INK, (rect.right - 3, rect.y + 2), apex, 1)

    # The IDENTITY: red+blue COARSE candy-stripe perimeter border. Four solid
    # corner nibs anchor the ring (and stay put under rotation); only a few fat
    # ticks march each straight run, because a fine dash count smears into
    # red/blue confetti at the 22px downscale. The starting tick colour
    # alternates per edge so the candy reads as red+blue, not a run of one.
    border = rect.inflate(-6, -6)
    NIB = 3                       # solid corner nib half-length (px on each arm)
    DASH = 3                      # fat tick width along the run
    GAP = 4                       # paper gap between ticks (coarse = survives)
    colors = (RED, BLUE)

    def _nib(corner, ax, ay, c0, c1):
        # Solid 2px L-bracket nib: a short red arm + blue arm meeting at a
        # corner, a discrete coloured anchor instead of merged dashes.
        x, y = corner
        pygame.draw.line(surf, c0, (x, y), (x + ax * NIB, y), 2)
        pygame.draw.line(surf, c1, (x, y), (x, y + ay * NIB), 2)

    def _march(start, end, first):
        # Lay fat ticks from `start` toward `end`, leaving the corners (the nibs)
        # clear. `first` picks the starting colour so adjacent edges alternate.
        x0, y0 = start
        x1, y1 = end
        dx, dy = x1 - x0, y1 - y0
        length = max(abs(dx), abs(dy))
        ux, uy = dx / length, dy / length
        run = length - 2 * (NIB + 1)
        pitch = DASH + GAP
        n = max(1, int(run // pitch))
        # Centre the tick run on the edge so it sits symmetric between the nibs.
        s0 = (NIB + 1) + (run - (n * DASH + (n - 1) * GAP)) / 2
        ci = first
        for k in range(n):
            d = s0 + k * pitch
            a = (x0 + ux * d, y0 + uy * d)
            b = (x0 + ux * (d + DASH), y0 + uy * (d + DASH))
            pygame.draw.line(surf, colors[ci % 2], a, b, 3)
            ci += 1

    tl = (border.x, border.y)
    tr = (border.right, border.y)
    brc = (border.right, border.bottom)
    bl = (border.x, border.bottom)
    _nib(tl,  1,  1, RED, BLUE)
    _nib(tr, -1,  1, BLUE, RED)
    _nib(brc, -1, -1, RED, BLUE)
    _nib(bl,  1, -1, BLUE, RED)
    _march(tl, tr, 0)             # top:    R B R B ...
    _march(tr, brc, 1)           # right:  B R B ...
    _march(brc, bl, 0)           # bottom: R B R ...
    _march(bl, tl, 1)            # left:   B R B ...

    # Single red postage stamp, top-right — held a pixel off the border so it
    # never touches it, and reduced to ONE solid saturated square with a 1px ink
    # edge: the single clearly-separated red mass. A 1px paper halo keeps it from
    # fusing with the candy edge.
    st = pygame.Rect(rect.right - 12, rect.y + 5, 6, 6)
    pygame.draw.rect(surf, PAPER, st.inflate(2, 2))
    pygame.draw.rect(surf, RED, st)
    pygame.draw.rect(surf, INK, st, 1)

    # Cool keyline rim INSIDE the outline — a glowing edge on night sky that
    # stays subtle on day, so the slab reads on both skies from one sprite.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
