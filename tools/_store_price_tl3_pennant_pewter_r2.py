"""Round-2 render sheet for the tl3 PENNANT-PEWTER hang-tag price treatment.

Revises r1 per art-director critique:
- Outer silhouette stroke replaced with per-segment line draws so the
  2px polygon miter at the reflex lower-corner vertices can't spike outside
  the silhouette; each segment now terminates cleanly at its endpoints.
- Affordable bottom gradient stop deepened to (168,144,80) — the warm bronze
  shows more strongly and the pewter→bronze sweep reads as active / buyable.
- Locked fill flattened to a single uniform cold-slate (128,132,138) with no
  metal-banding rows and no bronze stop; the face is dead and clearly disabled.
- Stitched-notch ticks at the apex removed; the V-tip is a clean sharp point.
- Coin ring raised 2 face-px to y=32, ruling line to y=44, price to y=52 —
  the champagne numeral now has balanced pewter framing above and below.

Review-only tooling — never imported by the game.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def coin_ring(surf, cx, cy):
    # The tl3 family unifier: a small bronze washer with a punched transparent
    # bore, drawn byte-identical across every tl3 tag so the family reads as one.
    r = sc.m(5)
    s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    cc = (r + 1, r + 1)
    pygame.draw.circle(s, (156, 116, 58), cc, r)
    pygame.draw.circle(s, (48, 28, 10), cc, r, 1)
    pygame.draw.circle(s, (0, 0, 0, 0), cc, sc.m(3) + 1)
    surf.blit(s, (cx - r - 1, cy - r - 1))


# ── pennant geometry (face-local px, drawn on the SS=2 author buffer) ─────────
# PAD=4 keeps the 2px outer stroke and the grommet entirely inside the surface
# boundary; the face centroid sits at padded-surface centre so a single
# center=(50,50) blit seats the tag in the card's top-left corner.
FACE_W = 76
RECT_H = 58
APEX_Y = 80
PAD = 4

# Outer silhouette: 45° chamfers at the two top corners, V-apex at the bottom.
_POLY = [(8, 0), (68, 0), (76, 8), (76, 58), (38, 80), (0, 58), (0, 8)]
# Inner deboss ring inset 4px from the outer poly.
_INNER = [(12, 4), (64, 4), (72, 12), (72, 54), (38, 74), (4, 54), (4, 12)]

# Affordable: cool pewter top → steel mid → deepened warm-bronze base, so the
# tag reads as precious woven metal rather than painted plastic.
# Locked: both stops identical so lerp_stops always returns the same cold slate;
# no warmth, no depth — dead.
_STOPS_AFF = [(0.0, (158, 164, 170)), (0.5, (122, 128, 136)), (1.0, (168, 144, 80))]
_STOPS_LCK = [(0.0, (128, 132, 138)), (1.0, (128, 132, 138))]


def _fl(x, y):
    """Face-local (spec) coords -> padded-surface coords."""
    return (x + PAD, y + PAD)


def _pennant_fill(stops, metal_banding=True):
    """Vertical gradient masked to the pennant silhouette.  The ±4-luminance
    metal-weave toggle is skipped for the locked variant so the face reads as
    flat dead slate rather than an active textile."""
    grad = pygame.Surface((FACE_W, APEX_Y), pygame.SRCALPHA)
    for y in range(APEX_Y):
        r, g, b = sc.lerp_stops(stops, y / (APEX_Y - 1))
        if metal_banding:
            band = 4 if (y // 2) % 2 == 0 else -4
            col = (max(0, min(255, r + band)), max(0, min(255, g + band)),
                   max(0, min(255, b + band)))
        else:
            col = (r, g, b)
        pygame.draw.line(grad, col, (0, y), (FACE_W - 1, y))
    mask = pygame.Surface((FACE_W, APEX_Y), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), _POLY)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return grad


def _price_face(face, text, price_col, key_col):
    """Champagne (or grey) numerals centred at y≈52 face-local — high enough
    that the pewter body frames the price on all sides with equal breathing room,
    rather than crowding it against the V-junction."""
    sz = 11.0
    f = sc.font(sz)
    while sc._glyph_base(text, f, 0).get_width() > 62 and sz > 7:
        sz -= 0.5
        f = sc.font(sz)
    sc.plain_text(face, text, f, _fl(38, 52), color=price_col, shadow_a=0,
                  weight=sc.m(0.8), keyline=key_col, kw=max(1, sc.m(0.6)))


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """PENNANT-PEWTER hang-tag: a straight-hanging V-pointed felt pennant on a
    cool pewter/steel-bronze face, relocated to the card's top-left corner. The
    whole tag re-tints for affordability; the bronze coin ring + steel grommet
    are shared tl3 furniture."""
    affordable = (variant != "locked")
    text = _abbr(text)

    if affordable:
        stops = _STOPS_AFF
        stroke_col = (70, 44, 10)        # deep bronze silhouette edge
        inner_col = (186, 190, 196)      # bright steel deboss highlight
        price_col = (244, 222, 174)      # champagne numerals
        key_col = (56, 52, 46)           # dark bronze keyline under price
    else:
        stops = _STOPS_LCK
        stroke_col = (96, 100, 106)      # cold slate edge
        inner_col = (150, 154, 158)      # barely-there deboss — keeps the shape
        price_col = (150, 150, 150)      # grey numerals
        key_col = (40, 44, 50)           # dark slate keyline

    face = pygame.Surface((FACE_W + PAD * 2, APEX_Y + PAD * 2), pygame.SRCALPHA)

    # Felt body — banding disabled for locked so its face reads as lifeless flat slate.
    face.blit(_pennant_fill(stops, metal_banding=affordable), (PAD, PAD))

    # Outer silhouette as individual line segments; a polygon outline would miter
    # at the reflex lower-corner vertices and push bronze pixels outside the shape.
    pts = [_fl(*p) for p in _POLY]
    for i in range(len(pts)):
        pygame.draw.line(face, stroke_col, pts[i], pts[(i + 1) % len(pts)], 2)

    # Inner debossed ring — 1px bright line just inside the outer stroke.
    pygame.draw.polygon(face, inner_col, [_fl(*p) for p in _INNER], 1)

    # Steel grommet: outer ring, lit UL arc, shaded LR arc, dark bore, punched void.
    gx, gy = _fl(38, 14)
    pygame.draw.circle(face, (188, 192, 196), (gx, gy), 12)
    pygame.draw.circle(face, (150, 158, 166), (gx, gy), 9)
    grect = (gx - 9, gy - 9, 18, 18)
    pygame.draw.arc(face, (190, 200, 208), grect,
                    math.radians(80), math.radians(200), 2)
    pygame.draw.arc(face, (60, 68, 76), grect,
                    math.radians(260), math.radians(380), 2)
    pygame.draw.circle(face, (40, 30, 18), (gx, gy), sc.m(3))
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), sc.m(2))

    # Short straight cord — the pennant hangs without drape.
    pygame.draw.line(face, (150, 158, 166), _fl(38, 5), _fl(38, 2), 2)
    pygame.draw.line(face, (200, 206, 212), _fl(39, 5), _fl(39, 2), 1)

    # Bronze coin ring at y=32 (raised 2px from r1's y=34) for breathing room.
    coin_ring(face, *_fl(38, 32))
    # Ruling line moved to y=44 to maintain proportional separation from both
    # the coin ring above and the price below.
    pygame.draw.line(face, (96, 100, 106), _fl(6, 44), _fl(70, 44), 1)
    # Price at y=52 — clean pewter framing on all four sides.
    _price_face(face, text, price_col, key_col)

    # Apex left as a clean sharp V — stitched-notch ticks were too fine to resolve
    # at 1× and merged into visual noise at the tip.

    surf.blit(face, face.get_rect(center=(50, 50)))
    return face.get_rect(center=(50, 50))


sc.price_chip = my_price_chip


# ── render sheet ──────────────────────────────────────────────────────────────
def render_card_1x(sid, variant):
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def zoom_left(card_1x):
    crop = card_1x.subsurface((0, 0, 80, 100))
    return pygame.transform.scale(crop, (160, 200))


BG = (8, 8, 20)
PAD_S = 20
GAP = 12
HDR_H = 40
LABEL_H = 20
CW, CH = sc.CARD_W, sc.CARD_H

cards = {
    "mummy_aff":   render_card_1x("skin_mummy",   sc.PRICE_VARIANT),
    "mummy_lck":   render_card_1x("skin_mummy",   "locked"),
    "kitsune_aff": render_card_1x("skin_kitsune", sc.PRICE_VARIANT),
    "kitsune_lck": render_card_1x("skin_kitsune", "locked"),
}

row1_h = CH
row2_h = 200
total_w = PAD_S + 4 * CW + 3 * GAP + PAD_S
total_h = HDR_H + LABEL_H + row1_h + GAP + row2_h + PAD_S
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("pennant-pewter · tl3 hang-tag · round 2", True, (255, 220, 80))
canvas.blit(ht, (total_w // 2 - ht.get_width() // 2, (HDR_H - ht.get_height()) // 2))

lf = hud_font(7)
card_list = [cards["mummy_aff"], cards["mummy_lck"],
             cards["kitsune_aff"], cards["kitsune_lck"]]
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
y1 = HDR_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD_S + i * (CW + GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HDR_H + (LABEL_H - lbl.get_height()) // 2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2×crop)"),
                                  ("mummy_lck", "mummy lck (2×crop)")]):
    x = PAD_S + i * (160 + GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "/home/user/skybit/docs/store_price_tl3/pennant_pewter/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")

# ── sanity ────────────────────────────────────────────────────────────────────
aff = cards["mummy_aff"]
lck = cards["mummy_lck"]

# Sample near the bottom of the pennant rect (y≈34 card-local) where the warm
# bronze base stop dominates the affordable gradient but locked is flat cold slate.
# The two variants must differ there by more than a trivial rounding difference.
pa = aff.get_at((20, 34))
pl = lck.get_at((20, 34))
print("aff(20,34)=", tuple(pa), " lck(20,34)=", tuple(pl))
diff = abs(int(pa[0]) - int(pl[0])) + abs(int(pa[1]) - int(pl[1])) + abs(int(pa[2]) - int(pl[2]))
assert diff > 20, f"affordable/locked too similar at (20,34): diff={diff}"
print("sanity OK — pennant-pewter r2 renders, states clearly differ")
