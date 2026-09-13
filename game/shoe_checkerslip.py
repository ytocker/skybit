"""CHECKER SLIP — laceless slip-on with a black/white checkerboard upper.

Drawn entirely from pygame primitives so it survives the full size range:
the SAME function is the ~104×62 product shot AND a ~15×10 sprite on the
bird's feet. Geometry is fractions of the (x, y, w, h) box so it scales
cleanly.

The check is deliberately resolution-aware rather than a fine grid: at hero
size it is a small count of LARGE blocks (4 cols × 2 rows) so the pattern
reads as a few honest squares, and below a width threshold it hard-snaps to a
single pure-black/pure-white alternating band (no mid-grays, no AA) so a tiny
foot sprite still says "checker shoe" instead of dissolving into mud.

It is a HOMAGE in the spirit of the game's KFC parody theme — a silhouette +
checkerboard colorway with stylized cues (padded collar top-line, elastic side
gore, white foxing tape over a warm gum sole), never an exact trademarked
mark. No text, no logo.
"""
import pygame


# Pure black/white check (no tints — tiny sizes need maximum contrast), a warm
# cream gum sole kept clearly distinct from the bright white foxing tape, and a
# darker collar value so the slip-on top-line reads even when the check is gone.
_CANVAS_W  = (248, 248, 246)   # white check / canvas
_CANVAS_D  = (20, 20, 24)      # black check
_GORE      = (236, 232, 224)   # plain elastic side-gore gusset (un-checkered)
_GORE_E    = (210, 204, 192)
_COLLAR_D  = (40, 34, 50)      # dark padded-collar top-line
_FOXING    = (252, 252, 250)   # bright white rubber foxing tape
_FOXING_E  = (214, 214, 210)
_GUM       = (214, 178, 120)   # warm gum tan outsole — distinct from the whites
_GUM_E     = (182, 144, 88)    # 1px darker gum edge / waffle line
_SEAM      = (208, 208, 204)   # quiet seam on white canvas

# Below this device width the fine check can't hold; we draw a hard-snapped
# pure black/white band instead of trying (and failing) to tile squares.
_TINY_W = 34


def _u(u, v, x, y, w, h, facing):
    """Map unit-box (u, v) in [0..1] to device pixels, mirroring about u=0.5
    when facing left so one core serves both feet / both store orientations."""
    if facing < 0:
        u = 1.0 - u
    return (int(round(x + u * w)), int(round(y + v * h)))


def _poly(surf, color, pts, x, y, w, h, facing):
    pygame.draw.polygon(surf, color, [_u(u, v, x, y, w, h, facing)
                                      for u, v in pts])


def _line(surf, color, a, b, x, y, w, h, facing, width):
    pygame.draw.line(surf, color, _u(*a, x, y, w, h, facing),
                     _u(*b, x, y, w, h, facing), max(1, int(round(width))))


# Upper silhouette (toe-right), shared by the fill and the checker clip mask so
# the pattern never spills past the canvas. Low, round slip-on profile.
_UPPER = [(0.05, 0.78), (0.05, 0.50), (0.10, 0.40), (0.22, 0.34),
          (0.40, 0.32), (0.60, 0.33), (0.78, 0.40), (0.91, 0.52),
          (0.95, 0.66), (0.95, 0.78)]

# Toe-end region that carries the check (kept clear of the collar + side gore).
# Four large columns span this band; the collar scoop and gore sit to its left.
_CHECK_U0, _CHECK_U1 = 0.40, 0.95
_CHECK_V0, _CHECK_V1 = 0.33, 0.78


def _checker_upper(surf, x, y, w, h, facing):
    """Fill the upper white, then stamp a deliberate LARGE-block check on it.

    Hero/mid: 4 columns × 2 rows of big squares across the toe band — a few
    honest blocks that stay legible at 48px. Tiny (< _TINY_W device px): the
    grid is abandoned for a hard 4×1 pure-black/white band so the check never
    degrades into gray noise."""
    poly = [_u(u, v, x, y, w, h, facing) for u, v in _UPPER]
    pygame.draw.polygon(surf, _CANVAS_W, poly)

    # Device-space bounds of the check band so we can clip squares to the upper.
    band = [_u(u, v, x, y, w, h, facing) for u, v in
            [(_CHECK_U0, _CHECK_V0), (_CHECK_U1, _CHECK_V0),
             (_CHECK_U1, _CHECK_V1), (_CHECK_U0, _CHECK_V1)]]
    bxs = [p[0] for p in band]
    bys = [p[1] for p in band]
    bx0, bx1 = min(bxs), max(bxs)
    by0, by1 = min(bys), max(bys)
    bw = max(1, bx1 - bx0)
    bh = max(1, by1 - by0)

    stencil = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(stencil, (255, 255, 255, 255),
                        [(px - bx0, py - by0) for px, py in poly])

    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    if w < _TINY_W:
        # Hard-snap: 4 equal columns alternating pure black/white. One honest
        # split that says "checker" with zero mid-gray and no AA at the edges.
        cols = 4
        for c in range(cols):
            if c % 2 == 0:
                continue
            cx0 = bx0 + (bw * c) // cols
            cx1 = bx0 + (bw * (c + 1)) // cols
            pygame.draw.rect(mask, _CANVAS_D, (cx0 - bx0, 0, cx1 - cx0, bh))
    else:
        # Large blocks: 4 columns across, 2 rows down — big enough to survive a
        # 48px render as a few clear squares rather than a muddy tile.
        cols, rows = 4, 2
        for r in range(rows):
            for c in range(cols):
                if (r + c) % 2 == 0:
                    continue
                cx0 = bx0 + (bw * c) // cols
                cx1 = bx0 + (bw * (c + 1)) // cols
                cy0 = (bh * r) // rows
                cy1 = (bh * (r + 1)) // rows
                pygame.draw.rect(mask, _CANVAS_D,
                                 (cx0 - bx0, cy0, cx1 - cx0, cy1 - cy0))

    mask.blit(stencil, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(mask, (bx0, by0))

    if w >= _TINY_W:
        # Quiet seam where the toe-cap canvas meets the vamp, on the white base.
        _line(surf, _SEAM, (0.66, 0.36), (0.90, 0.54), x, y, w, h, facing,
              max(1, w * 0.012))


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile CHECKER SLIP shoe into box (x, y, w, h).

    Toe points RIGHT when facing=1 (mirrored for -1). Laceless slip-on with
    three clean horizontal values bottom-up — warm gum sole, bright white
    foxing tape, checkerboard canvas — plus a dark padded-collar top-line and a
    plain elastic side gore that sell "slip-on" even when the check vanishes at
    foot size. No outer outline — the caller adds the house outline.
    """
    tiny = w < _TINY_W

    # ── warm gum outsole (trimmed ~15% vs a platform look) ────────────────
    # Lower top edge starts at 0.81 (was 0.78) so the sole stack reads slimmer.
    sole = [(0.03, 0.88), (0.09, 0.86), (0.93, 0.87), (0.98, 0.90),
            (0.95, 0.99), (0.05, 0.99), (0.01, 0.93)]
    _poly(surf, _GUM_E, sole, x, y, w, h, facing)
    sole_face = [(0.04, 0.885), (0.93, 0.885), (0.95, 0.935), (0.06, 0.945)]
    _poly(surf, _GUM, sole_face, x, y, w, h, facing)
    if not tiny:
        # A few vertical waffle ticks — skipped tiny where they'd be noise.
        for tu in (0.20, 0.40, 0.60, 0.80):
            _line(surf, _GUM_E, (tu, 0.905), (tu, 0.975), x, y, w, h, facing,
                  max(1, w * 0.01))

    # ── CUE 1 · bright white foxing tape over the gum ─────────────────────
    # A thin pure-white rubber band riding just above the warm gum, giving the
    # third clean horizontal value: check / white tape / gum.
    foxing = [(0.04, 0.81), (0.95, 0.81), (0.96, 0.885), (0.03, 0.885)]
    _poly(surf, _FOXING_E, foxing, x, y, w, h, facing)
    foxing_face = [(0.05, 0.815), (0.94, 0.815), (0.95, 0.87), (0.045, 0.87)]
    _poly(surf, _FOXING, foxing_face, x, y, w, h, facing)

    # ── plain elastic side gore (un-checkered) near the collar ────────────
    # The stretch gusset that lets a laceless shoe pull on; drawn BEFORE the
    # check so the toe-band stencil leaves it clear. A flat panel, no pattern,
    # so it stays legible as the "slip-on" tell even at 16px.
    gore = [(0.10, 0.42), (0.24, 0.37), (0.38, 0.40), (0.36, 0.62),
            (0.22, 0.70), (0.10, 0.66)]
    _poly(surf, _GORE_E, gore, x, y, w, h, facing)
    gore_face = [(0.12, 0.435), (0.24, 0.395), (0.355, 0.42), (0.335, 0.605),
                 (0.225, 0.665), (0.12, 0.635)]
    _poly(surf, _GORE, gore_face, x, y, w, h, facing)

    # ── checkerboard canvas upper (hero cue) ──────────────────────────────
    _checker_upper(surf, x, y, w, h, facing)

    # ── CUE 2 · dark padded-collar top-line with an instep notch ──────────
    # The signature top opening: a dark padded-collar arc along the throat that
    # dips into a small notch at the instep. This single dark line is the most
    # robust slip-on cue and is hand-drawn even at tiny size.
    if tiny:
        # One thin dark collar line hugging the top opening — kept high and
        # slim so it crowns the bump without eating the check band below it.
        _line(surf, _COLLAR_D, (0.16, 0.40), (0.40, 0.34), x, y, w, h, facing,
              max(1, h * 0.06))
        _line(surf, _COLLAR_D, (0.40, 0.34), (0.52, 0.40), x, y, w, h, facing,
              max(1, h * 0.06))
    else:
        # Padded collar arc: rear riser, dip to the instep notch, short return.
        collar = [(0.16, 0.46), (0.18, 0.38), (0.30, 0.345), (0.41, 0.345),
                  (0.48, 0.39), (0.45, 0.45), (0.40, 0.40), (0.30, 0.41),
                  (0.22, 0.46)]
        _poly(surf, _COLLAR_D, collar, x, y, w, h, facing)
        # Bright padded lip riding on top of the dark collar for a rounded edge.
        _line(surf, _GORE, (0.19, 0.385), (0.30, 0.355), x, y, w, h, facing,
              max(1, h * 0.035))
        _line(surf, _GORE, (0.30, 0.355), (0.41, 0.355), x, y, w, h, facing,
              max(1, h * 0.035))
        # Heel edge tint so the white canvas reads against any sky.
        _line(surf, _SEAM, (0.05, 0.50), (0.05, 0.78), x, y, w, h, facing,
              max(1, w * 0.01))
