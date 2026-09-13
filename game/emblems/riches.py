"""
RICHES family — six engraved center glyphs for the GOLD wealth-ladder
achievements (v2 LOCKED spec). Procedural, single-colour engrave idiom shared
with ``game/achievement_icons.py``.

The ladder is read off ONE escalating cue: the CONTAINER that holds the money
grows rung by rung — none -> 3-stack -> drawstring pouch -> tall safe -> crowned
hoard -> the Midas hand turning a coin to gold. The ringed ``$`` dollar coin is
the constant thread woven through every rung (a single ``_coin`` helper, so the
glyph is pixel-identical wherever it appears), and Midas alone carries a
saturated gold gem-spark routed through ``_accent`` so it stays monochrome when
the medal is dormant. No numerals, no sub-5px detail; every shape is a bold
filled disc / polygon / thick line so the read survives at the 44px row size.
"""
from __future__ import annotations

import math
import pygame

# These mirror the host module's engrave hooks. The render harness wires the
# real functions in by importing ``game.achievement_icons`` and copying its
# ``_GLYPH_SH`` / ``_glyph_font`` / ``_accent`` onto this module before stamping,
# so the inset-shadow tone, font cache and dormant-desaturation stay identical to
# the rest of the medallion family rather than being re-implemented here.
_GLYPH_SH = (32, 18, 44)


def _glyph_font(px: int):
    # Replaced at import time by the host module's cached SysFont so the ``$``
    # matches every other coin glyph; this stand-in keeps the file importable
    # on its own.
    return pygame.font.SysFont(None, px, bold=True)


def _accent(lit_col, dormant_col=(170, 162, 150)):
    # Replaced at import time by the host's state-aware accent resolver.
    return lit_col


# ── the constant thread: the ringed ``$`` coin ───────────────────────────────
#
# Lifted verbatim from ``_glyph_coin`` so the dollar token is the SAME object on
# every rung. ``rscale`` shrinks it where several coins must share the box; the
# ring weight tracks the coin radius so a small spilled coin never goes hairline.

def _coin(surf, cx, cy, r, col, rscale=0.66, ring=None):
    rr = max(4, int(r * rscale))
    if ring is None:
        ring = max(3, int(r * rscale / 8 * 12) // 12) if False else max(2, rr // 4)
    pygame.draw.circle(surf, col, (cx, cy), rr, ring)
    f = _glyph_font(int(rr * 1.7))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _crownlet(surf, cx, cy, r, col, w=None):
    # The shared L4 rank crownlet — a 3-point engraved coronet seated on top of
    # a motif. Faint cherry-on-top per spec; the container growth is the real
    # read, so this stays small.
    w = w or max(2, r // 12)
    half = r * 0.46
    base_y = cy
    pts = [
        (cx - half, base_y),
        (cx - half, base_y - r * 0.20),
        (cx - half * 0.5, base_y - r * 0.02),
        (cx, base_y - r * 0.34),
        (cx + half * 0.5, base_y - r * 0.02),
        (cx + half, base_y - r * 0.20),
        (cx + half, base_y),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _pips(surf, cx, cy, r, col, n):
    # L1/L2 rank dots tucked under a motif — faint optional accent only.
    pr = max(2, r // 12)
    span = pr * 3 * (n - 1)
    for i in range(n):
        x = cx - span // 2 + i * pr * 3
        pygame.draw.circle(surf, col, (int(x), int(cy)), pr)


# ── rung 1: coin_25_run — Pocket Change ──────────────────────────────────────

def _glyph_coin_25_run(surf, cx, cy, r, col):
    # ONE clean ``$`` coin with a single small notch-dot at its foot — the lone-
    # coin bottom rung. No second coin, so it never competes with the 3-stack of
    # the next rung at row size; just one unmistakable ringed ``$``.
    _coin(surf, cx, cy - int(r * 0.06), r, col, rscale=0.72)
    # one tiny notch-dot tucked lower-right (a single chip of loose change)
    nx, ny = cx + int(r * 0.60), cy + int(r * 0.58)
    nr = max(4, int(r * 0.17))
    pygame.draw.circle(surf, _GLYPH_SH, (nx + 1, ny + 1), nr)
    pygame.draw.circle(surf, col, (nx, ny), nr)
    pygame.draw.circle(surf, _GLYPH_SH, (nx, ny), nr, max(1, nr // 3))


# ── rung 2: coin_100_run — Coin Run ──────────────────────────────────────────

def _glyph_coin_100_run(surf, cx, cy, r, col):
    # A fanned RUN of 3 ``$`` coins — three discs fanned diagonally with wide
    # lateral offset and a deep inset-shadow gap rimming each, so the COUNT (3)
    # never fuses into a blob at row size. The front (lower-right, nearest) coin
    # carries a BOLD face-on ringed ``$`` — both the count and the dollar thread
    # survive the 44px shrink. Container = a stack/run of coins. L1 pip.
    cr = int(r * 0.42)               # each coin's radius
    gap = max(2, int(r * 0.07))      # dark separation halo between coins
    # back coins first (up-left, faint), front coin last (down-right, the ``$``)
    centres = [
        (cx - int(r * 0.50), cy - int(r * 0.30)),   # back
        (cx - int(r * 0.10), cy + int(r * 0.02)),   # middle
        (cx + int(r * 0.40), cy + int(r * 0.36)),   # front, face-on ``$``
    ]
    for i, (px, py) in enumerate(centres):
        # wide dark halo cuts a clean gap to the coin behind/beside it
        pygame.draw.circle(surf, _GLYPH_SH, (px, py), cr + gap)
        if i < 2:
            # back coins read edge-on: solid disc + a hollow ring score
            pygame.draw.circle(surf, col, (px, py), cr)
            pygame.draw.circle(surf, _GLYPH_SH, (px, py), max(2, cr - cr // 3))
            pygame.draw.circle(surf, col, (px, py), max(3, cr - cr // 2))
    tx, ty = centres[-1]
    _coin(surf, tx, ty, r, col, rscale=0.42)
    _pips(surf, cx, cy + int(r * 0.86), r, col, 1)


# ── rung 3: coins_500_life — Coin Collector ──────────────────────────────────

def _glyph_coins_500_life(surf, cx, cy, r, col):
    # A drawstring COIN POUCH with a ``$`` on its belly and two coins spilling
    # at its foot. Container = a sack. L2 wreath ticks.
    # sack body — a round-bottomed bag, narrowing to a tied neck
    by = cy + int(r * 0.10)
    bw = int(r * 0.78)
    bh = int(r * 0.74)
    body = [
        (cx - int(bw * 0.42), by - int(bh * 0.30)),   # neck left
        (cx - bw, by + int(bh * 0.30)),               # bulge left
        (cx - int(bw * 0.66), by + bh),               # base left
        (cx + int(bw * 0.66), by + bh),               # base right
        (cx + bw, by + int(bh * 0.30)),               # bulge right
        (cx + int(bw * 0.42), by - int(bh * 0.30)),   # neck right
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in body])
    # cinched neck — a narrow band above the bulge
    neck = pygame.Rect(cx - int(bw * 0.46), by - int(bh * 0.52),
                       int(bw * 0.92), max(4, int(bh * 0.24)))
    pygame.draw.rect(surf, col, neck, border_radius=max(2, r // 12))
    # drawstring tie ears flaring up off the neck
    for sgn in (-1, 1):
        ex = cx + sgn * int(bw * 0.40)
        pygame.draw.line(surf, col, (cx + sgn * int(bw * 0.18), by - int(bh * 0.44)),
                         (ex, by - int(bh * 0.78)), max(3, r // 9))
    # the ``$`` token engraved into the sack's belly (inset, so it reads sunk)
    f = _glyph_font(int(r * 0.78))
    g = f.render("$", True, _GLYPH_SH)
    surf.blit(g, g.get_rect(center=(cx, by + int(bh * 0.42))))
    # two coins spilling at the foot, lower-right
    for dx, dy, sc in ((0.74, 0.86, 0.26), (0.96, 0.66, 0.20)):
        nx, ny = cx + int(r * dx), cy + int(r * dy)
        nr = max(4, int(r * sc))
        pygame.draw.circle(surf, _GLYPH_SH, (nx + 1, ny + 1), nr)
        pygame.draw.circle(surf, col, (nx, ny), nr)
        pygame.draw.circle(surf, _GLYPH_SH, (nx, ny), nr, max(1, nr // 3))


# ── rung 4: coins_5000_life — Coin Vault ─────────────────────────────────────

def _glyph_coins_5000_life(surf, cx, cy, r, col):
    # A TALL SAFE drawn portrait/upright — clearly taller than wide — with a
    # thick bezel door-PORTHOLE (a heavy ringed circular door) and a small dial
    # nub. The TALL aspect + bezel ring separate it from the WIDE-LOW chest.
    bw = int(r * 1.08)       # body width
    bh = int(r * 1.48)       # body height — TALL, clearly > wide
    bx = cx - bw // 2
    bty = cy - int(bh * 0.50)
    body = pygame.Rect(bx, bty, bw, bh)
    pygame.draw.rect(surf, col, body, border_radius=max(3, r // 7))
    # short stubby feet so it stands like a strongbox, not a lid
    fh = max(3, int(r * 0.16))
    for sgn in (-1, 1):
        fx = cx + sgn * int(bw * 0.30)
        pygame.draw.rect(surf, col, (fx - max(2, r // 12), bty + bh,
                                     max(4, r // 6), fh))
    # heavy bezel door-PORTHOLE: a thick ring filling most of the body, drawn
    # in the inset tone so the door reads recessed into the safe face
    dcy = cy + int(r * 0.02)
    dr = int(min(bw, bh) * 0.42)
    pygame.draw.circle(surf, _GLYPH_SH, (cx, dcy), dr)
    pygame.draw.circle(surf, col, (cx, dcy), dr, max(4, r // 7))   # thick bezel
    pygame.draw.circle(surf, _GLYPH_SH, (cx, dcy), max(3, dr // 2))  # inner well
    # combination dial nub at the door's centre + a couple of spoke handles
    pygame.draw.circle(surf, col, (cx, dcy), max(3, int(dr * 0.30)))
    for a in (math.radians(35), math.radians(215)):
        hx = cx + int(math.cos(a) * dr * 0.62)
        hy = dcy + int(math.sin(a) * dr * 0.62)
        pygame.draw.line(surf, col, (cx, dcy), (hx, hy), max(3, r // 11))
    # ``$`` token stamped on the safe's top band so the dollar thread persists
    f = _glyph_font(int(r * 0.42))
    g = f.render("$", True, _GLYPH_SH)
    surf.blit(g, g.get_rect(center=(cx, bty + int(bh * 0.14))))


# ── rung 5: coin_tycoon — Coin Tycoon ────────────────────────────────────────

def _glyph_coin_tycoon(surf, cx, cy, r, col):
    # A treasure HOARD that visibly OUT-SCALES the pouch and vault: a broad,
    # tall heaped mound of bullion topped by a face-on ``$`` coin and crowned by
    # the L4 coronet, with loose coins spilling PAST the mound's base outline on
    # both flanks — the money is overflowing its own pile. Container = an open
    # hoard with no walls (the wealth literally can't be contained).
    base_y = cy + int(r * 0.78)
    # the mound silhouette — a wide, tall heap of bullion (out-scales the others)
    mound = [
        (cx - int(r * 1.06), base_y),
        (cx - int(r * 0.60), base_y - int(r * 0.66)),
        (cx + int(r * 0.60), base_y - int(r * 0.66)),
        (cx + int(r * 1.06), base_y),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in mound])
    # coins heaped up the mound's shoulders, the lowest pair SPILLING past the
    # base outline so the hoard clearly overflows
    for sgn in (-1, 1):
        for fx, fy, sc in ((0.74, 0.34, 0.24), (0.46, 0.56, 0.24),
                           (0.92, -0.10, 0.22)):   # last one spills below base_y
            nx = cx + sgn * int(r * fx)
            ny = base_y - int(r * fy)
            nr = max(4, int(r * sc))
            pygame.draw.circle(surf, _GLYPH_SH, (nx + 1, ny + 1), nr)
            pygame.draw.circle(surf, col, (nx, ny), nr)
            pygame.draw.circle(surf, _GLYPH_SH, (nx, ny), nr, max(1, nr // 3))
    # the crowning face-on ``$`` coin riding clear above the heap (the constant
    # thread) — a dark backing disc lifts it off the mound so it never merges
    coy = base_y - int(r * 0.92)
    pygame.draw.circle(surf, _GLYPH_SH, (cx, coy), int(r * 0.42) + 2)
    _coin(surf, cx, coy, r, col, rscale=0.42)
    # L4 crownlet seated above the hoard — the wealth is royal now
    _crownlet(surf, cx, coy - int(r * 0.50), r, col)


# ── rung 6: midas — Midas Touch ──────────────────────────────────────────────

def _glyph_midas(surf, cx, cy, r, col):
    # An open PALM (three fat WIDELY-SPACED finger-stubs + a thumb, no knuckle
    # detail) reaching up to a RADIANT ``$`` coin that hangs LOW, nearly touching
    # the fingertips, with the unlock-only GOLD gem-spark exactly at that contact
    # point. The HAND is exclusive to Midas — the apex of the wealth ladder: the
    # touch that turns the coin to gold. The reach-and-touch gesture must survive
    # row size, so the fingers fan with big dark gaps and the coin sits close.
    # the open palm — a rounded heel low in the box
    pw = int(r * 0.80)        # palm half-width
    py = cy + int(r * 0.78)   # palm base line
    fy_top = py - int(r * 0.26)
    palm = [
        (cx - pw, fy_top),
        (cx - int(pw * 0.74), py),                   # heel left
        (cx, py + int(r * 0.18)),                    # rounded heel bottom
        (cx + int(pw * 0.74), py),                   # heel right
        (cx + pw, fy_top),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in palm])
    # three fat finger-stubs fanned WIDE off the heel, each carved out by a broad
    # dark slot so the trio reads as separate fingers — not a paddle — at 44px
    finger_w = max(6, int(r * 0.24))
    flen = int(r * 0.42)
    for fx in (-0.62, 0.0, 0.62):
        x = cx + int(pw * fx)
        pygame.draw.rect(surf, _GLYPH_SH,
                         (x - finger_w // 2 - 3, fy_top - flen,
                          finger_w + 6, flen + 5),
                         border_radius=finger_w // 2 + 3)
        pygame.draw.rect(surf, col, (x - finger_w // 2, fy_top - flen,
                                     finger_w, flen + max(2, r // 12)),
                         border_radius=finger_w // 2)
    # thumb angled out off the right heel (open-hand gesture)
    thumb_w = max(6, int(r * 0.22))
    pygame.draw.line(surf, col, (cx + int(pw * 0.74), py - int(r * 0.04)),
                     (cx + int(pw * 1.08), fy_top - int(r * 0.16)), thumb_w)
    # radiant ``$`` coin dropped LOW so it nearly touches the middle fingertip,
    # the constant thread, ringed by short emanating rays
    cor = int(r * 0.36)
    coy = fy_top - flen - cor - int(r * 0.04)
    for i in range(8):
        a = i * math.pi / 4
        x1 = cx + int(math.cos(a) * cor * 1.28)
        y1 = coy + int(math.sin(a) * cor * 1.28)
        x2 = cx + int(math.cos(a) * cor * 1.70)
        y2 = coy + int(math.sin(a) * cor * 1.70)
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), max(2, r // 11))
    _coin(surf, cx, coy, r, col, rscale=0.36)
    # single GOLD four-point gem-spark at the fingertip-to-coin contact — the
    # only saturated accent in the family, desaturating to bronze when dormant
    gx = cx
    gy = fy_top - flen - int(r * 0.02)
    gold = _accent((255, 214, 92))
    sp = max(4, int(r * 0.22))
    pygame.draw.polygon(surf, _GLYPH_SH, [
        (gx, gy - sp - 1), (gx + sp // 2 + 1, gy), (gx, gy + sp + 1),
        (gx - sp // 2 - 1, gy)])
    pygame.draw.polygon(surf, gold, [
        (gx, gy - sp), (gx + sp * 2 // 5, gy),
        (gx, gy + sp), (gx - sp * 2 // 5, gy)])
    pygame.draw.polygon(surf, gold, [
        (gx - sp, gy), (gx, gy - sp * 2 // 5),
        (gx + sp, gy), (gx, gy + sp * 2 // 5)])


GLYPHS = {
    "coin_25_run": _glyph_coin_25_run,
    "coin_100_run": _glyph_coin_100_run,
    "coins_500_life": _glyph_coins_500_life,
    "coins_5000_life": _glyph_coins_5000_life,
    "coin_tycoon": _glyph_coin_tycoon,
    "midas": _glyph_midas,
}
