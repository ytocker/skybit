"""Round-2 render for the `wax-cream` store-card price tag (tier-line 3).

Changes from r1 (per art-director critique):
- Wax seal is ABSENT on locked cards entirely; locked = cool grey parchment +
  coin_ring + price only. Storytelling fix: the seal is the "affordability
  stamp", so it vanishes when the item is out of reach.
- coin_ring decoupled upward to (36, 56) face-local so it no longer collides
  with the seal center. Seal relocated to lower-right corner (54, 70) at a
  smaller radius (~sc.m(3)), with a 1px darker halo so it reads as a pressed
  impression in the corner zone.
- NOTCH pushed 10→14dp so the 45° corner clips register visually (~7px at
  1×). Existing mahogany diagonal stroke now spans the full cut.
- Locked price darkened to (96,88,80) — still clearly muted but legible on
  cool cream.

Review sheet only — nothing here is wired into the live store draw path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color
from game.hud import _font as hud_font

sd.load()

FACE_W = 72
FACE_H = 80
TILT = 6
NOTCH = 14                           # was 10; larger clips register at 1×


def _abbr(text):
    """Prices climb into the thousands; collapse long numbers to `1.2k` style
    so they stay readable at 1× on the narrow tag face."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def coin_ring(surf, cx, cy):
    """Bronze rivet ring whose bore is punched clear so the parchment (and
    price) reads through it — the tag's decorative family unifier."""
    r = sc.m(5)
    s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    cc = (r + 1, r + 1)
    pygame.draw.circle(s, (156, 116, 58), cc, r)
    pygame.draw.circle(s, (48, 28, 10), cc, r, 1)
    pygame.draw.circle(s, (0, 0, 0, 0), cc, sc.m(3) + 1)
    surf.blit(s, (cx - r - 1, cy - r - 1))


def _silhouette_mask():
    """White silhouette of the notched-corner portrait: bottom corners rounded,
    top corners sliced at 45° per NOTCH=14. Used to clip fill and edge stroke
    so nothing pokes past the tag's real outline."""
    mask = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, FACE_W, FACE_H),
                     border_bottom_left_radius=sc.m(5),
                     border_bottom_right_radius=sc.m(5))
    # carve the 45° clips at both top corners
    pygame.draw.polygon(mask, (0, 0, 0, 0), [(0, 0), (NOTCH, 0), (0, NOTCH)])
    pygame.draw.polygon(mask, (0, 0, 0, 0),
                        [(FACE_W - NOTCH, 0), (FACE_W, 0), (FACE_W, NOTCH)])
    return mask


def _cream_fill(top, bot, mask):
    """Warm parchment gradient with a 3-row +4/0/−4 luminance ripple so the
    stock reads as pressed paper, clipped into the silhouette."""
    grad = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    band = {0: 4, 1: 0, 2: -4}
    for y in range(FACE_H):
        t = y / max(1, FACE_H - 1)
        base = lerp_color(top, bot, t)
        d = band[y % 3]
        col = tuple(max(0, min(255, c + d)) for c in base)
        pygame.draw.line(grad, (*col, 255), (0, y), (FACE_W - 1, y))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return grad


def _edge_stroke(face, mask, color):
    """2px mahogany rim on the notched-corner silhouette: a rounded-bottom rect
    outline plus explicit lines along the two 45° cut edges so the wider NOTCH
    registers as a deliberate design rather than a clipping artefact."""
    edge = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.rect(edge, color, (0, 0, FACE_W, FACE_H), width=2,
                     border_bottom_left_radius=sc.m(5),
                     border_bottom_right_radius=sc.m(5))
    # explicit diagonal rim so the cut reads clearly even at 1×
    pygame.draw.line(edge, color, (NOTCH, 0), (0, NOTCH), 2)
    pygame.draw.line(edge, color, (FACE_W - NOTCH, 0), (FACE_W, NOTCH), 2)
    edge.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    face.blit(edge, (0, 0))


def _draw_price(face, text, center, fill_col, key_col):
    """Solid numerals poured into the bold glyph mask, wrapped in a 1px
    parchment keyline so they lift off the cream stock in either state."""
    for fs in (13, 12, 11, 10):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        if mask.get_width() <= 58:
            break
    r = mask.get_rect(center=center)
    kl = mask.copy()
    kl.fill((*key_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = max(1, sc.m(0.6))
    for ang in range(0, 360, 45):
        dx = int(round(p * math.cos(math.radians(ang))))
        dy = int(round(p * math.sin(math.radians(ang))))
        face.blit(kl, (r.x + dx, r.y + dy))
    img = mask.copy()
    fill = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
    fill.fill((*fill_col, 255))
    img.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


def _twine(face, grommet, corner, cord, hi):
    """Cotton twine drape from the grommet up to the card corner: a gentle
    quadratic-bezier arc drawn as a 2px cord with a 1px parallel twist highlight.
    Drawn before the grommet so it appears to dive into the hole."""
    ctrl = (grommet[0] - 8, grommet[1] - 8)
    steps = 14
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * grommet[0] + 2*(1-t)*t * ctrl[0] + t*t * corner[0]
        y = (1-t)**2 * grommet[1] + 2*(1-t)*t * ctrl[1] + t*t * corner[1]
        pts.append((x, y))
    pygame.draw.lines(face, cord, False, pts, 2)
    hp = [(x - 1, y - 1) for x, y in pts]
    pygame.draw.lines(face, hi, False, hp, 1)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the wax-cream tag at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant; the wax seal appears ONLY on
    affordable cards — locked cards carry coin_ring + price but NO seal."""
    affordable = (variant != "locked")
    text = _abbr(text)

    grommet  = (36, 14)
    patch_c  = (36, 14)
    coin_c   = (36, 56)          # raised from 64 → clear of seal below
    seal_c   = (54, 70)          # lower-right corner; absent on locked
    price_c  = (36, 38)

    if affordable:
        cream_top, cream_bot = (248, 240, 222), (232, 218, 190)
        price_fill = (48, 28, 10)
        patch_col  = (208, 184, 148)
        seal_fill  = (122, 30, 38)
        seal_halo  = (86, 18, 26)
        cord, cord_hi = (176, 150, 104), (220, 196, 154)
    else:
        cream_top, cream_bot = (232, 226, 214), (214, 206, 190)
        price_fill = (96, 88, 80)   # was (150,140,124) — legible on cool cream
        patch_col  = (190, 180, 166)
        cord, cord_hi = (168, 160, 146), (206, 200, 188)
    price_key = (210, 192, 158)

    mask = _silhouette_mask()
    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    face.blit(_cream_fill(cream_top, cream_bot, mask), (0, 0))

    _edge_stroke(face, mask, (60, 28, 8))

    # 1px debossed inner border pressed in from the mahogany rim
    pygame.draw.rect(face, (196, 178, 142), (5, 5, FACE_W - 10, FACE_H - 10),
                     width=1, border_radius=sc.m(3))

    # reinforcement washer, twine, then grommet so cord tucks under the eyelet
    pygame.draw.circle(face, patch_col, patch_c, 14)
    _twine(face, grommet, (10, 2), cord, cord_hi)

    gr = sc.m(4)
    pygame.draw.circle(face, (174, 134, 44), grommet, gr)
    pygame.draw.arc(face, (60, 38, 8),
                    (grommet[0] - gr, grommet[1] - gr, gr * 2, gr * 2),
                    math.radians(-80), math.radians(70), max(1, sc.m(1)))
    pygame.draw.circle(face, (40, 28, 10), grommet, sc.m(3))
    pygame.draw.circle(face, (0, 0, 0, 0), grommet, sc.m(2))

    _draw_price(face, text, price_c, price_fill, price_key)

    # coin_ring — present on both states, clear of seal (which is corner-right)
    coin_ring(face, *coin_c)

    # wax seal — ONLY on affordable; absent entirely on locked
    if affordable:
        seal_r = sc.m(3)           # smaller corner accent, was sc.m(4)+1
        pygame.draw.circle(face, seal_fill, seal_c, seal_r)
        # 1px darker halo so the pressed impression reads against the stock
        pygame.draw.circle(face, seal_halo, seal_c, seal_r + 1, 1)

    rot = pygame.transform.rotozoom(face, TILT, 1.0)
    surf.blit(rot, rot.get_rect(center=(50, 52)))


sc.price_chip = my_price_chip


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


# ── pixel verification ────────────────────────────────────────────────────────
_va = render_card_1x("skin_mummy", sc.PRICE_VARIANT)
_vl = render_card_1x("skin_mummy", "locked")
_bg = (8, 8, 20)

tag_px = _va.get_at((12, 10))[:3]
assert any(abs(tag_px[i] - _bg[i]) > 40 for i in range(3)), \
    f"no tag at (12,10): {tag_px}"

pa, pl = _va.get_at((20, 25))[:3], _vl.get_at((20, 25))[:3]
assert pa != pl, f"states identical at (20,25): {pa}"

# confirm burgundy seal is present on affordable (lower-right tag zone)
seal_hit = None
for px in range(22, 50):
    for py in range(30, 55):
        c = _va.get_at((px, py))[:3]
        if c[0] > 90 and c[0] - c[1] > 40 and c[0] - c[2] > 40:
            seal_hit = ((px, py), c)
            break
    if seal_hit:
        break
assert seal_hit, "burgundy wax seal not found on affordable card"

# confirm seal pixel is ABSENT (not burgundy) on locked card at same location
lck_at_seal = _vl.get_at(seal_hit[0])[:3]
c = lck_at_seal
is_burgundy_locked = c[0] > 90 and c[0] - c[1] > 40 and c[0] - c[2] > 40
assert not is_burgundy_locked, \
    f"seal colour still appears on locked at {seal_hit[0]}: {lck_at_seal}"

print(f"tag(12,10):{tag_px}  aff(20,25):{pa} lck:{pl}  "
      f"seal{seal_hit[0]}:{seal_hit[1]}  lck_at_seal:{lck_at_seal}")

# ── render sheet ──────────────────────────────────────────────────────────────
BG     = (8, 8, 20)
PAD    = 20
GAP    = 12
HDR_H  = 40
CW, CH = sc.CARD_W, sc.CARD_H

cards = {
    "mummy_aff":   render_card_1x("skin_mummy",   sc.PRICE_VARIANT),
    "mummy_lck":   render_card_1x("skin_mummy",   "locked"),
    "kitsune_aff": render_card_1x("skin_kitsune", sc.PRICE_VARIANT),
    "kitsune_lck": render_card_1x("skin_kitsune", "locked"),
}

LABEL_H = 20
row1_h  = CH
row2_h  = 200
total_w = PAD + 4 * CW + 3 * GAP + PAD
total_h = HDR_H + LABEL_H + row1_h + GAP + row2_h + PAD
canvas  = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("wax-cream · tl3 hang-tag · round 2", True, (255, 220, 80))
canvas.blit(ht, (total_w // 2 - ht.get_width() // 2,
                 (HDR_H - ht.get_height()) // 2))

lf = hud_font(7)
card_list = [cards["mummy_aff"], cards["mummy_lck"],
             cards["kitsune_aff"], cards["kitsune_lck"]]
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
y1 = HDR_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD + i * (CW + GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HDR_H + (LABEL_H - lbl.get_height()) // 2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2×crop)"),
                                   ("mummy_lck", "mummy lck (2×crop)")]):
    x = PAD + i * (160 + GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "docs/store_price_tl3/wax_cream/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
