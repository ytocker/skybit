"""Treasure Box — once-per-cycle finale pickup, icon exploration round 2.

The Treasure Box triggers once per biome day/night cycle (~175 pillars),
opens a 5-pillar gap filled by a long coin rush, sits in the middle of
that gap, and on pickup grants +100 coins with a fireworks-style coin
explosion. The icon must read "treasure / chest / overflowing loot" at
a glance and feel like THE most special pickup the player ever sees.

Each candidate is a self-contained procedural draw: supersampled at SS
then smoothscaled down, matching the lottery/umbrella icon family
(3-5 colour palette, thick ink outline, gentle baked float-bob).

The pickup is explicitly LARGER than the regular power-ups — target
~56x46 px so the chest silhouette has room to breathe. Each cell shows
the chest at TRUE pickup size on the left half (with the canonical bob)
and a 3x zoom on the right half, on a dawn/sunrise sky swatch with a
faint sparkle / coin-shimmer ambience (the cycle ends near SUNRISE).

Round 2 converged on the royal-crown lead (B5). The pop-art halftone
collided with the umbrella's teal/cream and lost "treasure" semantics,
so it was dropped for a "Glowing rune" chest that adds an ancient-magic
flavour distinct from B3's jewelled fantasy direction.

  B1  Classic wooden + lid jewel  — silhouette pick, lifted past starter.
  B2  Overflowing gold            — darker body so the gold pile pops.
  B3  Magical jewelled            — large faceted ruby breaks lid top.
  B4  Glowing rune                — dark wood + amber sigil + seam glow.
  B5  Royal crown (lead)          — crown spike + 2 gold studs + sparkles.

Output: docs/treasure_box/round_2.png   (doc-only; not shipped)
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

# ---------------------------------------------------------------------------
# Footprint + palette
# ---------------------------------------------------------------------------
# Treasure Box is the rarest pickup — user explicitly asked for a LARGER
# footprint than the usual ~48 px power-ups. 56x46 keeps a comfortable
# chest aspect ratio (wider than tall) while still fitting the in-world
# spawn lane.
PICKUP_W = 56
PICKUP_H = 46
SS = 7                                   # supersample (matches umbrella sheet)

# Canonical float-bob phase so every candidate sits like a real pickup.
BOB_PULSE = 1.15

# Shared ink + neutrals — matches the lottery/umbrella icon family so the
# Treasure Box looks like it belongs to the same toy-store-arcade set.
INK        = (22, 18, 34)
INK_SOFT   = (46, 40, 64)
CREAM      = (250, 244, 222)

# Wood (B1 base). B2's wood is darkened (~15%) below so the gold pile pops
# off the body instead of collapsing into one amber mass at 1x.
WOOD_HI    = (174, 116,  62)
WOOD_MID   = (138,  82,  40)
WOOD_LO    = ( 96,  54,  24)
WOOD_GRAIN = ( 72,  40,  18)

# B2 darker wood — WOOD_MID and WOOD_LO reduced ~15% per channel so the
# spilling gold reads as a distinct silhouette over the chest body.
WOOD_HI_B2 = (148,  99,  53)
WOOD_MID_B2 = (117,  70,  34)
WOOD_LO_B2 = ( 82,  46,  20)
IRON_HI    = (118, 124, 138)
IRON_MID   = ( 82,  86,  98)
IRON_LO    = ( 54,  56,  68)

# Gold (locks, coins, rim, filigree).
GOLD_HI    = (255, 232, 124)
GOLD_MID   = (240, 196,  72)
GOLD_LO    = (188, 138,  28)
GOLD_INK   = (110,  72,  10)

# B3 magical body — deep mystic purple/blue gradient with cool ink.
MAGIC_HI   = ( 96,  74, 180)
MAGIC_MID  = ( 58,  44, 132)
MAGIC_LO   = ( 30,  20,  82)
MAGIC_HALO = (180, 168, 240)
GEM_RED_HI = (255, 130, 142)
GEM_RED    = (220,  56,  74)
GEM_RED_LO = (152,  28,  46)

# B4 glowing-rune palette — deeper wood than B1 so the amber sigil + seam
# under-glow read as "ancient magical artefact" rather than starter chest.
RUNE_WOOD_HI = (110,  68,  40)
RUNE_WOOD_MID = ( 76,  44,  26)
RUNE_WOOD_LO = ( 46,  26,  16)
RUNE_GRAIN   = ( 28,  16,  10)
RUNE_GLOW_HI = (255, 214, 132)            # bright sigil core
RUNE_GLOW_MID = (242, 158,  62)
RUNE_GLOW_LO = (188,  96,  28)
RUNE_HALO    = (255, 184,  96)            # seam under-glow + halo wash

# B5 royal — deeper kingly red velvet body with heavy gold edging + jewels.
ROYAL_HI   = (200,  64,  72)
ROYAL_MID  = (152,  36,  52)
ROYAL_LO   = ( 96,  18,  32)
JEWEL_RED  = (236,  72,  86)
JEWEL_BLU  = ( 96, 152, 240)
JEWEL_GRN  = ( 96, 200, 132)
JEWEL_PUR  = (180, 122, 232)

# Dawn / sunrise sky swatch (cycle ends near SUNRISE phase).
SKY_TOP    = (252, 198, 142)              # warm peach
SKY_MID    = (250, 168, 158)              # soft coral
SKY_BOT    = (148, 152, 196)              # cool dawn underbelly
HORIZON_GL = (255, 226, 178)              # sun-glow band


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ---------------------------------------------------------------------------
# Shared chest-body helpers — supersampled draws into a px-square surface.
# All accept (big, cx, cy, w, h, ink_w). cx/cy is the CHEST'S geometric
# centre in SS-space; w/h is the chest body footprint in SS-space.
# ---------------------------------------------------------------------------
def _vgrad_rect(surf, rect, top_col, bot_col, radius=0):
    """Vertical gradient inside `rect`, optionally rounded."""
    tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
    h_ = rect.height
    for y in range(h_):
        t = y / max(1, h_ - 1)
        pygame.draw.line(tmp, _lerp(top_col, bot_col, t),
                         (0, y), (rect.width, y))
    if radius:
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         mask.get_rect(), border_radius=radius)
        tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tmp, rect.topleft)


def _wood_grain(big, rect, ink_w):
    """A couple of horizontal grain ticks across the lid/body for a hand-
    drawn wooden feel — kept faint so the silhouette still leads."""
    n = 3
    for i in range(1, n + 1):
        y = rect.top + int(rect.height * (i / (n + 1)))
        x0 = rect.left + int(rect.width * 0.10)
        x1 = rect.right - int(rect.width * 0.10)
        pygame.draw.line(big, WOOD_GRAIN, (x0, y), (x1, y),
                         max(1, ink_w // 2))


def _curved_lid(big, lid_rect, ink_w, top_col, mid_col, lo_col,
                grain=True, sheen=True):
    """A curved (half-ellipse-topped) lid filling lid_rect's footprint.
    The arc rises above lid_rect.top by ~35% of lid_rect.height so the
    chest reads as 'pirate chest' rather than 'flat box'."""
    arc_h = int(lid_rect.height * 0.65)
    cx = lid_rect.centerx
    # Build a polygon following the arc top + the flat bottom edge.
    pts = []
    n = 18
    top_y = lid_rect.top - arc_h
    half_w = lid_rect.width // 2
    for i in range(n + 1):
        t = i / n
        ang = math.pi * (1 - t)               # left -> right across the arc
        ax = cx + math.cos(ang) * half_w
        ay = lid_rect.top - math.sin(ang) * arc_h
        pts.append((ax, ay))
    pts.append((lid_rect.right, lid_rect.bottom))
    pts.append((lid_rect.left, lid_rect.bottom))
    # Solid base fill via the polygon, then a vertical gradient masked over it.
    pygame.draw.polygon(big, mid_col, pts)
    # Mask gradient to the polygon shape.
    grad_rect = pygame.Rect(lid_rect.left, top_y,
                            lid_rect.width, lid_rect.bottom - top_y)
    grad = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    for y in range(grad_rect.height):
        t = y / max(1, grad_rect.height - 1)
        pygame.draw.line(grad, _lerp(top_col, lo_col, t),
                         (0, y), (grad_rect.width, y))
    mask = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    local_pts = [(p[0] - grad_rect.left, p[1] - grad_rect.top) for p in pts]
    pygame.draw.polygon(mask, (255, 255, 255, 255), local_pts)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grad, grad_rect.topleft)
    if sheen:
        # A soft elliptical highlight near the apex sells the dome curvature.
        sh = pygame.Surface((lid_rect.width, arc_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (255, 248, 222, 90),
                             (int(lid_rect.width * 0.18),
                              int(arc_h * 0.20),
                              int(lid_rect.width * 0.42),
                              int(arc_h * 0.45)))
        big.blit(sh, (lid_rect.left, top_y))
    if grain:
        # Grain ticks following the arc — sample a few horizontal chords.
        for frac in (0.30, 0.55, 0.78):
            y = top_y + int(arc_h * 2 * frac)
            # Chord half-width at this height (ellipse arc).
            dy = (lid_rect.top - y) / max(1, arc_h)
            dy = max(-1.0, min(1.0, dy))
            hx = int(half_w * math.sqrt(max(0.0, 1.0 - dy * dy)))
            pygame.draw.line(big, WOOD_GRAIN,
                             (cx - hx + ink_w * 2, y),
                             (cx + hx - ink_w * 2, y),
                             max(1, ink_w // 2))
    pygame.draw.polygon(big, INK, pts, ink_w)
    return pts, top_y


def _chest_body(big, rect, ink_w, top_col, mid_col, lo_col, radius=None):
    """The lower wooden box — a slightly rounded rectangle with a vertical
    gradient. `rect` is the body footprint (lid sits on top of it)."""
    if radius is None:
        radius = max(2, int(rect.width * 0.06))
    _vgrad_rect(big, rect, top_col, mid_col, radius=radius)
    # A second darker wash at the bottom 30% for depth.
    foot = pygame.Rect(rect.left, rect.top + int(rect.height * 0.62),
                       rect.width, int(rect.height * 0.40))
    _vgrad_rect(big, foot, mid_col, lo_col, radius=radius)
    pygame.draw.rect(big, INK, rect, ink_w, border_radius=radius)


def _iron_band(big, rect, ink_w):
    """Horizontal iron banding — left/right band running across body."""
    _vgrad_rect(big, rect, IRON_HI, IRON_LO, radius=max(1, ink_w))
    pygame.draw.rect(big, INK, rect, ink_w, border_radius=max(1, ink_w))
    # Rivets at the band ends.
    rivet_r = max(2, int(rect.height * 0.30))
    for cx in (rect.left + rect.height // 2,
               rect.right - rect.height // 2):
        pygame.draw.circle(big, IRON_HI, (cx, rect.centery), rivet_r)
        pygame.draw.circle(big, INK, (cx, rect.centery), rivet_r, ink_w)


def _gold_lock(big, cx, cy, w, h, ink_w, keyhole=True):
    """Big gold lock plate sitting flush on the lid-body seam."""
    lock = pygame.Rect(0, 0, w, h)
    lock.center = (cx, cy)
    _vgrad_rect(big, lock, GOLD_HI, GOLD_LO, radius=max(2, w // 8))
    pygame.draw.rect(big, GOLD_INK, lock, ink_w, border_radius=max(2, w // 8))
    if keyhole:
        # Round keyhole + tail slot.
        khr = max(2, int(h * 0.18))
        pygame.draw.circle(big, INK, (cx, cy - h // 8), khr)
        pygame.draw.polygon(big, INK,
                            [(cx - khr // 2, cy - h // 8),
                             (cx + khr // 2, cy - h // 8),
                             (cx + khr // 3, cy + h // 4),
                             (cx - khr // 3, cy + h // 4)])


def _gold_coin(big, cx, cy, r, ink_w, glyph=True):
    """Stylised gold coin — circular face with rim + a $ glyph chord."""
    pygame.draw.circle(big, GOLD_LO, (cx, cy + max(1, r // 6)), r)
    pygame.draw.circle(big, GOLD_HI, (cx, cy), r)
    pygame.draw.circle(big, GOLD_MID, (cx, cy), max(1, int(r * 0.78)))
    pygame.draw.circle(big, GOLD_INK, (cx, cy), r, max(1, ink_w // 2))
    if glyph and r >= 4:
        # Simple S-curve as a money-glyph — readable at tiny coins.
        pygame.draw.line(big, GOLD_INK,
                         (cx - r // 3, cy - r // 3),
                         (cx + r // 3, cy - r // 3),
                         max(1, ink_w // 2))
        pygame.draw.line(big, GOLD_INK,
                         (cx - r // 3, cy + r // 3),
                         (cx + r // 3, cy + r // 3),
                         max(1, ink_w // 2))
        pygame.draw.line(big, GOLD_INK,
                         (cx, cy - r // 2),
                         (cx, cy + r // 2),
                         max(1, ink_w // 2))


def _gem(big, cx, cy, w, h, col_hi, col_mid, col_lo, ink_w):
    """Cut gem — a faceted hex-ish polygon with a top highlight."""
    pts = [
        (cx,              cy - h // 2),
        (cx + w // 2,     cy - h // 5),
        (cx + w // 3,     cy + h // 2),
        (cx - w // 3,     cy + h // 2),
        (cx - w // 2,     cy - h // 5),
    ]
    pygame.draw.polygon(big, col_mid, pts)
    # Top-facet highlight wedge.
    pygame.draw.polygon(big, col_hi,
                        [(cx, cy - h // 2),
                         (cx + w // 2, cy - h // 5),
                         (cx + w // 6, cy - h // 8),
                         (cx - w // 6, cy - h // 8),
                         (cx - w // 2, cy - h // 5)])
    # Bottom shadow wedge.
    pygame.draw.polygon(big, col_lo,
                        [(cx - w // 3, cy + h // 2),
                         (cx + w // 3, cy + h // 2),
                         (cx + w // 5, cy + h // 6),
                         (cx - w // 5, cy + h // 6)])
    pygame.draw.polygon(big, INK, pts, ink_w)
    # Pin-glint.
    pygame.draw.circle(big, (255, 255, 255),
                       (cx - w // 5, cy - h // 4),
                       max(1, ink_w))


# ---------------------------------------------------------------------------
# The five candidate icon draws. Each returns a (PICKUP_W, PICKUP_H)
# SRCALPHA surface (already smoothscaled to footprint).
# ---------------------------------------------------------------------------
def _finish(big):
    return pygame.transform.smoothscale(
        big, (big.get_width() // SS, big.get_height() // SS))


def _new_big():
    return pygame.Surface((PICKUP_W * SS, PICKUP_H * SS), pygame.SRCALPHA)


def _common_layout():
    """Shared chest geometry — body rect + lid rect in SS-space. The lid
    occupies the upper ~38% of the icon; the body fills the lower ~52%;
    a tiny gap is left at the very bottom for the foot shadow."""
    px_w = PICKUP_W * SS
    px_h = PICKUP_H * SS
    margin_x = int(px_w * 0.08)
    body_top = int(px_h * 0.38)
    body_bot = int(px_h * 0.92)
    lid_top  = int(px_h * 0.20)            # base of the curved lid arch
    body = pygame.Rect(margin_x, body_top,
                       px_w - 2 * margin_x, body_bot - body_top)
    lid  = pygame.Rect(margin_x, lid_top,
                       px_w - 2 * margin_x, body_top - lid_top)
    return body, lid


def icon_b1():
    """B1 — Classic wooden chest with a single amber lid-jewel above the
    keyhole. Curved iron-banded lid, two horizontal iron bands across the
    body, gold lock plate on the seam, faint wood grain. The lid-jewel
    lifts B1 out of "starter chest" territory without breaking silhouette."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body first so lid + lock sit on top.
    _chest_body(big, body, ink, WOOD_HI, WOOD_MID, WOOD_LO)
    # Two iron bands across the body (left + right).
    band_h = int(body.height * 0.18)
    bw = int(body.width * 0.10)
    left_band  = pygame.Rect(body.left + int(body.width * 0.08),
                             body.top + int(body.height * 0.10),
                             bw, body.height - int(body.height * 0.20))
    right_band = pygame.Rect(body.right - int(body.width * 0.08) - bw,
                             body.top + int(body.height * 0.10),
                             bw, body.height - int(body.height * 0.20))
    _iron_band(big, left_band, ink)
    _iron_band(big, right_band, ink)
    # Faint body grain ticks.
    _wood_grain(big, body, ink)

    # Curved lid.
    _curved_lid(big, lid, ink, WOOD_HI, WOOD_MID, WOOD_LO)
    # Iron strap across the lid centre, curved to follow the dome.
    strap_y = lid.top + int(lid.height * 0.10)
    pygame.draw.line(big, IRON_MID,
                     (lid.left + int(lid.width * 0.04), strap_y),
                     (lid.right - int(lid.width * 0.04), strap_y),
                     max(3, ink))
    pygame.draw.line(big, INK,
                     (lid.left + int(lid.width * 0.04), strap_y),
                     (lid.right - int(lid.width * 0.04), strap_y),
                     max(1, ink // 2))

    # Big gold lock plate sitting on the lid/body seam.
    lock_w = int(body.width * 0.30)
    lock_h = int(body.height * 0.55)
    _gold_lock(big, body.centerx, body.top + lock_h // 2 - int(body.height * 0.08),
               lock_w, lock_h, ink, keyhole=True)
    # Small lid clasp tab descending into the lock from above.
    clasp = pygame.Rect(0, 0, int(lock_w * 0.35), int(lock_h * 0.45))
    clasp.midbottom = (body.centerx, body.top + int(lock_h * 0.18))
    _vgrad_rect(big, clasp, GOLD_HI, GOLD_LO,
                radius=max(2, clasp.width // 6))
    pygame.draw.rect(big, GOLD_INK, clasp, max(1, ink // 2),
                     border_radius=max(2, clasp.width // 6))

    # Lid jewel — a small amber square gem sitting on the lid centre,
    # just above the lock clasp. Sized ~4x4 px at pickup scale, so at SS=7
    # the supersampled gem is roughly 28x28 px. Lifts B1 past "starter
    # chest" without touching the silhouette.
    jw = int(SS * 4)
    jh = int(SS * 4)
    jcx = lid.centerx
    jcy = lid.top + int(lid.height * 0.45)
    jrect = pygame.Rect(0, 0, jw, jh)
    jrect.center = (jcx, jcy)
    _vgrad_rect(big, jrect, GOLD_HI, GOLD_LO,
                radius=max(2, jw // 4))
    pygame.draw.rect(big, GOLD_INK, jrect, max(1, ink // 2),
                     border_radius=max(2, jw // 4))
    # 1-px near-white glint at the gem's top-left so it reads as faceted.
    pygame.draw.line(big, (255, 250, 220),
                     (jrect.left + jw // 6, jrect.top + jh // 5),
                     (jrect.left + jw // 2, jrect.top + jh // 5),
                     max(1, ink // 2))

    return _finish(big)


def icon_b2():
    """B2 — Overflowing gold chest. Half-open lid, generous pile of gold
    coins spilling forward over the front edge, plus ONE larger floating
    coin above the open lid. The wooden body is intentionally ~15% darker
    than B1 so the gold pile reads as a distinct shape at 1x instead of
    collapsing into a single amber blob with the lid + body."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body — darker wood so the gold pile silhouette pops cleanly.
    _chest_body(big, body, ink, WOOD_HI_B2, WOOD_MID_B2, WOOD_LO_B2)
    _wood_grain(big, body, ink)
    # Inside-of-box dark backdrop so spilled coins read against a void.
    inner = pygame.Rect(body.left + int(body.width * 0.10),
                        body.top + int(body.height * 0.04),
                        body.width - int(body.width * 0.20),
                        int(body.height * 0.40))
    _vgrad_rect(big, inner, (32, 22, 14), (12, 8, 4),
                radius=max(2, inner.width // 16))
    pygame.draw.rect(big, INK, inner,
                     max(1, ink // 2), border_radius=max(2, inner.width // 16))

    # Half-open curved lid, tilted back ~28deg, hinged at the back-top of
    # the body. Draw the lid into a small surf and rotate so the curl
    # reads as a flipped-open lid rather than a slid-aside slab.
    lid_w = lid.width
    lid_h = int(lid.height * 1.6)
    lid_surf = pygame.Surface((lid_w + 8, lid_h + 8), pygame.SRCALPHA)
    local_lid = pygame.Rect(4, lid_h - lid.height, lid_w, lid.height)
    _curved_lid(lid_surf, local_lid, ink, WOOD_HI_B2, WOOD_MID_B2, WOOD_LO_B2)
    rot = pygame.transform.rotate(lid_surf, 28)
    # Place hinge near the back-top corner of the body.
    hinge = (body.left + int(lid.width * 0.18),
             body.top - int(lid.height * 0.10))
    big.blit(rot, rot.get_rect(midbottom=hinge))

    # Coin pile spilling over the front edge — concentric coin clumps.
    pile_cy = body.top + int(body.height * 0.55)
    coin_r0 = int(body.height * 0.18)
    # Back row coins inside the box, partially behind the front lip.
    for (ox, oy, rs) in ((-0.28, -0.20, 1.0),
                         ( 0.08, -0.26, 1.0),
                         ( 0.32, -0.10, 0.9)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)),
                   ink)
    # Front-spill coins overlapping the body's front edge — these break
    # the silhouette of the box so the spill reads as motion, not a sticker.
    for (ox, oy, rs) in ((-0.36,  0.18, 1.05),
                         (-0.10,  0.30, 1.10),
                         ( 0.18,  0.32, 1.00),
                         ( 0.40,  0.20, 0.95),
                         (-0.22,  0.40, 0.90)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)),
                   ink)
    # ONE larger coin floating up above the open lid — captures the
    # "leaping out" beat. Single big coin reads cleanly at 1x where two
    # small coins were collapsing into dirt-speck noise.
    _gold_coin(big,
               body.centerx + int(body.width * 0.12),
               pile_cy + int(body.height * -0.92),
               max(4, int(coin_r0 * 1.10)),
               ink)

    return _finish(big)


def icon_b3():
    """B3 — Magical jewelled chest. Deep purple/blue body with cool ink,
    a single LARGE cut ruby inset in the lid centre, gold corner trim +
    clasp, and a faint pale halo glow behind it. Fantasy / mystical feel."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Halo aura first, well behind everything.
    halo_cx = body.centerx
    halo_cy = (lid.top + body.bottom) // 2
    halo = pygame.Surface((PICKUP_W * SS, PICKUP_H * SS), pygame.SRCALPHA)
    for k in range(6):
        t = k / 5
        rr = int(min(PICKUP_W, PICKUP_H) * SS * (0.58 - t * 0.08))
        a = int(80 * (1 - t))
        pygame.draw.circle(halo, (*MAGIC_HALO, a), (halo_cx, halo_cy), rr)
    big.blit(halo, (0, 0))

    # Body.
    _chest_body(big, body, ink, MAGIC_HI, MAGIC_MID, MAGIC_LO)
    # Gold corner trims — short L-brackets at the four body corners.
    tw = int(body.width * 0.13)
    th = int(body.height * 0.30)
    for cx, cy, sx, sy in (
        (body.left,  body.top,    +1, +1),
        (body.right, body.top,    -1, +1),
        (body.left,  body.bottom, +1, -1),
        (body.right, body.bottom, -1, -1),
    ):
        # Short horizontal arm.
        arm_h = pygame.Rect(0, 0, tw, max(2, ink + 1))
        arm_h.topleft = (cx if sx > 0 else cx - tw,
                         cy if sy > 0 else cy - max(2, ink + 1))
        _vgrad_rect(big, arm_h, GOLD_HI, GOLD_LO,
                    radius=max(1, arm_h.height // 2))
        # Short vertical arm.
        arm_v = pygame.Rect(0, 0, max(2, ink + 1), th)
        arm_v.topleft = (cx if sx > 0 else cx - max(2, ink + 1),
                         cy if sy > 0 else cy - th)
        _vgrad_rect(big, arm_v, GOLD_HI, GOLD_LO,
                    radius=max(1, arm_v.width // 2))

    # Curved lid in the same magic palette, with a brighter sheen so it
    # reads "polished obsidian" rather than dull stone.
    _curved_lid(big, lid, ink, MAGIC_HI, MAGIC_MID, MAGIC_LO,
                grain=False, sheen=True)

    # Single faceted ruby crowning the lid — sized ~6x4 px at the final
    # pickup so the gem is unambiguously visible at 1x (the round-1 gem
    # disappeared into a flat blob). The gem extends 1 px above the lid's
    # top silhouette so it breaks the chest outline and signals "crowned".
    gem_w = SS * 6
    gem_h = SS * 4
    # Find the lid arc's apex (top_y) so we can sit the gem on it.
    arc_h = int(lid.height * 0.65)
    apex_y = lid.top - arc_h
    gem_cy = apex_y + gem_h // 2 - SS         # the -SS lifts the gem 1 px
    _gem(big,
         lid.centerx,
         gem_cy,
         gem_w, gem_h,
         GEM_RED_HI, GEM_RED, GEM_RED_LO, ink)
    # 1-px near-white pin-highlight on the top facet so the gem reads as
    # a polished cut at 1x — distinguishes "ruby" from "red dot".
    pygame.draw.line(big, (255, 250, 230),
                     (lid.centerx - gem_w // 6, gem_cy - gem_h // 3),
                     (lid.centerx + gem_w // 6, gem_cy - gem_h // 3),
                     max(1, SS // 2))

    # Tiny gold clasp on the seam, framing the gem-line from below.
    clasp_w = int(body.width * 0.18)
    clasp_h = int(body.height * 0.18)
    clasp = pygame.Rect(0, 0, clasp_w, clasp_h)
    clasp.center = (body.centerx, body.top)
    _vgrad_rect(big, clasp, GOLD_HI, GOLD_LO,
                radius=max(1, clasp.height // 3))
    pygame.draw.rect(big, GOLD_INK, clasp, max(1, ink // 2),
                     border_radius=max(1, clasp.height // 3))

    # A couple of tiny sparkle pips around the ruby to sell the magic.
    for ang_deg in (-60, 30):
        ang = math.radians(ang_deg)
        sx = lid.centerx + int(math.cos(ang) * lid.width * 0.30)
        sy = (lid.top + int(lid.height * 0.18)) + int(math.sin(ang) * lid.height * 0.5)
        spk_r = max(2, int(SS * 0.7))
        pygame.draw.line(big, (255, 250, 220),
                         (sx - spk_r * 2, sy), (sx + spk_r * 2, sy),
                         max(1, ink // 2))
        pygame.draw.line(big, (255, 250, 220),
                         (sx, sy - spk_r * 2), (sx, sy + spk_r * 2),
                         max(1, ink // 2))

    return _finish(big)


def icon_b4():
    """B4 — Glowing rune chest. Replaces the halftone direction that
    collided with the umbrella's teal/cream and lost "treasure" semantics.
    Dark wood body (deeper than B1), a glowing amber sigil on the lid
    front (circled spiral — reads as an ancient magical mark), and a
    soft amber under-glow leaking from the lid/body seam. Distinct from
    B3 (jewelled fantasy) — this one feels "ancient magic artefact"."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body — deeper wood than B1 so the amber sigil + seam glow carry the
    # mystical read instead of fighting a bright body.
    _chest_body(big, body, ink, RUNE_WOOD_HI, RUNE_WOOD_MID, RUNE_WOOD_LO)

    # Faint dark wood grain on the body (using the rune-specific darker
    # grain colour so it doesn't muddy the under-glow band).
    n_grain = 3
    for i in range(1, n_grain + 1):
        gy = body.top + int(body.height * (i / (n_grain + 1)))
        x0 = body.left + int(body.width * 0.10)
        x1 = body.right - int(body.width * 0.10)
        pygame.draw.line(big, RUNE_GRAIN, (x0, gy), (x1, gy),
                         max(1, ink // 2))

    # Curved lid in the same dark wood, no sheen — the lid is meant to
    # feel matte so the rune itself is the only light source on the icon.
    pts, lid_top_y = _curved_lid(big, lid, ink,
                                  RUNE_WOOD_HI, RUNE_WOOD_MID, RUNE_WOOD_LO,
                                  grain=True, sheen=False)

    # Seam under-glow band — a horizontal soft amber wash leaking from the
    # lid/body seam. Drawn as a tall vertical alpha gradient centred on
    # the seam so the brightest pixels sit on the joint and fall off
    # above and below. Sells "something glowing inside is escaping".
    seam_y = body.top
    glow_h = int(body.height * 0.42)
    glow_w = body.width + ink * 2
    glow_surf = pygame.Surface((glow_w, glow_h * 2), pygame.SRCALPHA)
    for k in range(glow_h * 2):
        t = (k - glow_h) / glow_h
        a = int(150 * max(0.0, 1.0 - abs(t)))
        if a > 0:
            pygame.draw.line(glow_surf, (*RUNE_HALO, a),
                             (0, k), (glow_w, k))
    # Slight horizontal taper at the band edges so the glow doesn't bleed
    # past the chest silhouette — multiply a soft mask over the glow.
    edge_mask = pygame.Surface((glow_w, glow_h * 2), pygame.SRCALPHA)
    edge_mask.fill((255, 255, 255, 255))
    for ex in range(int(glow_w * 0.18)):
        a = int(255 * (ex / max(1, int(glow_w * 0.18))))
        pygame.draw.line(edge_mask, (255, 255, 255, a),
                         (ex, 0), (ex, glow_h * 2), 1)
        pygame.draw.line(edge_mask, (255, 255, 255, a),
                         (glow_w - 1 - ex, 0),
                         (glow_w - 1 - ex, glow_h * 2), 1)
    glow_surf.blit(edge_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(glow_surf, (body.left - ink, seam_y - glow_h),
             special_flags=pygame.BLEND_PREMULTIPLIED)

    # Bright 1-px seam line right on the joint so the eye locks onto where
    # the glow comes from. Pure bright core over the wood.
    pygame.draw.line(big, RUNE_GLOW_HI,
                     (body.left + ink, seam_y),
                     (body.right - ink, seam_y),
                     max(2, ink // 2))

    # Glowing rune sigil on the lid front — a circled spiral (the classic
    # "ancient magical mark" reading). Drawn as a soft outer halo behind
    # a crisp amber stroke so the rune itself reads as self-luminous.
    rune_cx = lid.centerx
    rune_cy = lid.top + int(lid.height * 0.40)
    rune_r  = int(lid.height * 0.55)

    # Outer halo behind the rune — a few stacked translucent discs.
    halo = pygame.Surface((rune_r * 6, rune_r * 6), pygame.SRCALPHA)
    hcx = halo.get_width() // 2
    hcy = halo.get_height() // 2
    for k in range(5):
        rr = int(rune_r * (1.7 - k * 0.18))
        a = 26 + k * 18
        pygame.draw.circle(halo, (*RUNE_HALO, a), (hcx, hcy), rr)
    big.blit(halo, halo.get_rect(center=(rune_cx, rune_cy)),
             special_flags=pygame.BLEND_PREMULTIPLIED)

    # Outer circle of the rune — bright amber ring.
    pygame.draw.circle(big, RUNE_GLOW_LO, (rune_cx, rune_cy),
                       rune_r, max(2, ink))
    pygame.draw.circle(big, RUNE_GLOW_MID, (rune_cx, rune_cy),
                       rune_r, max(1, ink - 1))

    # Inner spiral — a short Archimedean spiral built as a polyline. Two
    # turns is enough to read as "magical mark" at 1x without looking busy.
    spiral_pts = []
    turns = 1.75
    steps = 48
    for i in range(steps + 1):
        t = i / steps
        ang = turns * 2 * math.pi * t
        rr = rune_r * 0.72 * (1.0 - t)
        spiral_pts.append((rune_cx + math.cos(ang) * rr,
                           rune_cy + math.sin(ang) * rr))
    if len(spiral_pts) >= 2:
        pygame.draw.lines(big, RUNE_GLOW_HI, False, spiral_pts,
                          max(2, ink))
    # Bright pin-glint at the spiral's centre — sells "active glow".
    pygame.draw.circle(big, (255, 248, 220),
                       (rune_cx, rune_cy), max(2, int(SS * 0.9)))

    return _finish(big)


def icon_b5():
    """B5 — Royal crown chest (lead). Deep velvet-red body with heavy gold
    edging, a crown emblem whose centre spike breaks the top of the lid
    silhouette (the round-1 standout legibility win), TWO gold studs
    flanking the crown (the rainbow 4-jewel rim was rejected as noise at
    1x), a widened + extra-bright gold lock plate as the focal anchor,
    and a handful of static gold sparkle pixels orbiting the crown spike
    to signal "rarest pickup"."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body — deep red velvet with gold trim at top + bottom edges.
    _chest_body(big, body, ink, ROYAL_HI, ROYAL_MID, ROYAL_LO)
    # Gold trim band along the lid/body seam (top of body).
    top_trim = pygame.Rect(body.left, body.top - max(1, ink // 2),
                            body.width, max(3, int(body.height * 0.10)))
    _vgrad_rect(big, top_trim, GOLD_HI, GOLD_LO,
                radius=max(1, top_trim.height // 2))
    pygame.draw.rect(big, GOLD_INK, top_trim, max(1, ink // 2),
                     border_radius=max(1, top_trim.height // 2))
    # Gold trim band at the bottom (the chest's "shoe").
    bot_trim = pygame.Rect(body.left, body.bottom - int(body.height * 0.12),
                            body.width, int(body.height * 0.14))
    _vgrad_rect(big, bot_trim, GOLD_HI, GOLD_LO,
                radius=max(1, bot_trim.height // 2))
    pygame.draw.rect(big, GOLD_INK, bot_trim, max(1, ink // 2),
                     border_radius=max(1, bot_trim.height // 2))

    # Curved lid in the same red velvet.
    pts, lid_apex_y = _curved_lid(big, lid, ink,
                                   ROYAL_HI, ROYAL_MID, ROYAL_LO,
                                   grain=False, sheen=True)

    # Gold filigree corner brackets — short curved arms at lid corners.
    for (cx, cy, sx) in ((lid.left,  lid.top + int(lid.height * 0.10), +1),
                         (lid.right, lid.top + int(lid.height * 0.10), -1)):
        bx = cx + sx * int(lid.width * 0.10)
        by = cy + int(lid.height * 0.15)
        pygame.draw.arc(big, GOLD_MID,
                        pygame.Rect(min(cx, bx) - 2, min(cy, by) - 2,
                                    abs(bx - cx) + 4, abs(by - cy) + 4),
                        math.radians(0), math.radians(110),
                        max(2, ink - 1))

    # Gold lock plate — widened ~2 px and one value-step brighter than B1's
    # to anchor the eye at 1x. The lock is THE focal hierarchy peak; the
    # crown above it signals rarity, the lock seals "this is treasure".
    lock_w = int(body.width * 0.26) + SS * 2     # ~+2 px at pickup scale
    lock_h = int(body.height * 0.48)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.04)
    _gold_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink, keyhole=True)
    # Bright near-white 1-px highlight on the lock plate's top edge — a
    # one-step-brighter sheen so the plate visibly catches dawn light.
    pygame.draw.line(big, (255, 250, 230),
                     (lock_cx - lock_w // 2 + ink,
                      lock_cy - lock_h // 2 + max(1, ink // 2)),
                     (lock_cx + lock_w // 2 - ink,
                      lock_cy - lock_h // 2 + max(1, ink // 2)),
                     max(2, ink // 2))

    # Crown emblem with its centre spike breaking the lid silhouette.
    # Built so the central peak rises ABOVE the lid's arc apex — this is
    # the round-1 standout legibility win and the whole reason B5 leads.
    crown_w = int(lock_w * 1.15)
    crown_h = int(lock_h * 0.62)
    crown_cx = lock_cx
    # Sit the crown base just above the seam; the central spike will
    # extend above the lid arc apex by ~SS pixels (= ~1 px at pickup).
    crown_base_y = body.top - int(body.height * 0.06)
    spike_tip_y  = lid_apex_y - SS                 # 1 px above lid silhouette
    crown_cy = (crown_base_y + spike_tip_y) // 2
    # Three-peak silhouette; the middle peak is the tallest so it pierces
    # the lid top. Asymmetric heights would muddy the read — keep symmetric.
    cpts = [
        (crown_cx - crown_w // 2,    crown_base_y),
        (crown_cx - crown_w // 2,    crown_cy - crown_h // 6),
        (crown_cx - crown_w // 3,    crown_base_y - crown_h // 5),
        (crown_cx - crown_w // 5,    crown_cy - crown_h // 3),
        (crown_cx,                   spike_tip_y),
        (crown_cx + crown_w // 5,    crown_cy - crown_h // 3),
        (crown_cx + crown_w // 3,    crown_base_y - crown_h // 5),
        (crown_cx + crown_w // 2,    crown_cy - crown_h // 6),
        (crown_cx + crown_w // 2,    crown_base_y),
    ]
    pygame.draw.polygon(big, GOLD_HI, cpts)
    # Shadow band at the crown's base for solidity.
    pygame.draw.polygon(big, GOLD_LO,
                        [(crown_cx - crown_w // 2, crown_base_y - crown_h // 6),
                         (crown_cx + crown_w // 2, crown_base_y - crown_h // 6),
                         (crown_cx + crown_w // 2, crown_base_y),
                         (crown_cx - crown_w // 2, crown_base_y)])
    pygame.draw.polygon(big, GOLD_INK, cpts, max(1, ink - 1))

    # TWO gold studs flanking the crown — replaces the rejected 4-colour
    # rainbow rim. Two studs read as symmetric jewellery anchors at 1x
    # without becoming noise. Sit them just inside the crown's outer peaks.
    stud_r = max(2, int(SS * 0.9))
    for sx in (crown_cx - int(crown_w * 0.42),
               crown_cx + int(crown_w * 0.42)):
        sy = crown_base_y - crown_h // 6
        pygame.draw.circle(big, GOLD_HI, (sx, sy), stud_r + 1)
        pygame.draw.circle(big, GOLD_MID, (sx, sy), stud_r)
        pygame.draw.circle(big, GOLD_INK, (sx, sy), stud_r,
                           max(1, ink // 2))

    # Sparkle pixels orbiting the crown spike — static (not animated), four
    # tiny gold "+" twinkles at varied radii. Signals "rarest pickup" the
    # moment the icon appears, without inflating the silhouette.
    sparkle_specs = (
        (-0.55, -0.85, 1.0),
        ( 0.62, -0.78, 0.85),
        (-0.18, -1.15, 0.75),
        ( 0.30, -1.05, 0.65),
    )
    sparkle_cx = crown_cx
    sparkle_cy = spike_tip_y
    for (ox, oy, sc) in sparkle_specs:
        sx = sparkle_cx + int(crown_w * ox)
        sy = sparkle_cy + int(crown_h * oy)
        L = max(1, int(SS * 0.9 * sc))
        # Bright gold core dot.
        pygame.draw.circle(big, GOLD_HI, (sx, sy), max(1, int(L * 0.7)))
        # 4-arm "+" twinkle.
        pygame.draw.line(big, GOLD_HI, (sx - L, sy), (sx + L, sy),
                         max(1, ink // 3))
        pygame.draw.line(big, GOLD_HI, (sx, sy - L), (sx, sy + L),
                         max(1, ink // 3))

    return _finish(big)


CANDIDATES = [
    ("B1", "Classic wooden + lid jewel", icon_b1),
    ("B2", "Overflowing gold",           icon_b2),
    ("B3", "Magical jewelled",           icon_b3),
    ("B4", "Glowing rune",               icon_b4),
    ("B5", "Royal crown  (lead)",        icon_b5),
]


# ---------------------------------------------------------------------------
# Dawn / sunrise sky swatch with sparkle-coin shimmer (context backdrop).
# ---------------------------------------------------------------------------
def _dawn_sparkle_swatch(w, h, seed):
    """A 3-band dawn sky (peach top -> coral mid -> cool dawn bottom) with
    a warm horizon glow band near the foot and a sprinkle of faint
    cream/gold sparkles for coin-shimmer ambience. The cycle ends near
    SUNRISE, so this is the sky the player actually sees."""
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.55:
            col = _lerp(SKY_TOP, SKY_MID, t / 0.55)
        else:
            col = _lerp(SKY_MID, SKY_BOT, (t - 0.55) / 0.45)
        surf.fill(col, (0, y, w, 1))
    # Warm horizon-glow band sitting low — a faint band where the sun
    # peeks up. Adds dawn warmth without crowding the chest silhouette.
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    band_y = int(h * 0.74)
    band_h = int(h * 0.22)
    for k in range(band_h):
        t = k / max(1, band_h - 1)
        a = int(72 * (1 - abs(t - 0.5) * 2))
        if a > 0:
            pygame.draw.line(glow, (*HORIZON_GL, a),
                             (0, band_y + k), (w, band_y + k))
    surf.blit(glow, (0, 0))
    # A muted ground band so the cell feels grounded.
    pygame.draw.rect(surf, (84, 70, 86), (0, int(h * 0.92), w, h))

    rng = (seed * 2654435761) & 0xFFFFFFFF
    def rnd():
        nonlocal rng
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        return rng / 0x7FFFFFFF

    # Sparkles — small 4-point twinkles + tiny coin-dust pips. Faint so
    # the chest is unambiguously the subject.
    sparks = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(int(w * h / 1200)):
        x = int(rnd() * w)
        y = int(rnd() * h * 0.85)
        if rnd() < 0.5:
            r = 1 + int(rnd() * 1.6)
            a = 110 + int(rnd() * 90)
            pygame.draw.circle(sparks, (255, 244, 198, a), (x, y), r)
        else:
            # 4-point star sparkle.
            a = 90 + int(rnd() * 120)
            L = 2 + int(rnd() * 2)
            pygame.draw.line(sparks, (255, 248, 220, a),
                             (x - L, y), (x + L, y), 1)
            pygame.draw.line(sparks, (255, 248, 220, a),
                             (x, y - L), (x, y + L), 1)
    surf.blit(sparks, (0, 0))
    return surf


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "treasure_box")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")

    # Bake float-bob: shift each finished icon a couple px on its swatch.
    bob = int(round(math.sin(BOB_PULSE * 0.8) * 2))

    cell_w, cell_h = 320, 340
    cols = 5
    pad = 16
    header_h = 88
    footer_h = 34

    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * pad
    sheet_h = header_h + cell_h + footer_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 30))

    def font(sz, bold=False):
        return pygame.font.SysFont("Arial", sz, bold=bold)

    title = font(26, bold=True).render(
        "TREASURE BOX — once-per-cycle finale pickup; +100 coins; "
        "coin explosion on pickup  (round 2)", True,
        (240, 240, 246))
    sheet.blit(title, (pad, pad))
    sub = font(14).render(
        "round 2 — converged on royal-crown lead; halftone replaced with "
        "glowing rune.  Dawn/sunrise sky + sparkle backdrop per cell.",
        True, (170, 178, 192))
    sheet.blit(sub, (pad, pad + 32))
    sub2 = font(13).render(
        "Left = real pickup size (~56x46 px, float-bobbed);  "
        "right = 3x zoom.  5 directions: wooden / overflowing / "
        "jewelled / rune / royal-crown.",
        True, (200, 180, 150))
    sheet.blit(sub2, (pad, pad + 54))

    for col, (tag, name, fn) in enumerate(CANDIDATES):
        x = pad + col * (cell_w + pad)
        y = header_h + pad
        swatch = _dawn_sparkle_swatch(cell_w, cell_h, seed=col + 3)
        sheet.blit(swatch, (x, y))
        pygame.draw.rect(sheet, (60, 66, 84), (x, y, cell_w, cell_h), 1)

        icon = fn()

        # True pickup size on the upper-left of the cell.
        true_cx = x + cell_w // 4 - PICKUP_W // 2
        true_cy = y + cell_h // 2 - PICKUP_H // 2 + bob
        sheet.blit(icon, (true_cx, true_cy))
        # Footprint outline + caption marking the honest pickup size.
        pygame.draw.rect(sheet, (255, 255, 255),
                         (true_cx - 3, true_cy - bob - 3,
                          PICKUP_W + 6, PICKUP_H + 6), 1)
        lbl = font(12).render(f"real pickup ~{PICKUP_W}x{PICKUP_H} px",
                               True, (210, 220, 235))
        sheet.blit(lbl, (x + 10, y + cell_h - 24))

        # 3x zoom on the right half of the cell.
        zoom = pygame.transform.smoothscale(
            icon, (PICKUP_W * 3, PICKUP_H * 3))
        zx = x + cell_w - PICKUP_W * 3 - 18
        zy = y + cell_h // 2 - (PICKUP_H * 3) // 2
        sheet.blit(zoom, (zx, zy))
        zl = font(12).render("3x zoom", True, (210, 220, 235))
        sheet.blit(zl, (zx + PICKUP_W * 3 - 56, zy - 18))

        # Caption strip.
        cap = font(16, bold=True).render(f"{tag}  {name}", True,
                                         (245, 240, 230))
        sheet.blit(cap, (x + 8, header_h + pad + cell_h + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
