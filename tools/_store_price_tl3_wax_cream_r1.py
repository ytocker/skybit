"""Round-1 render for the `wax-cream` store-card price tag (tier-line 3).

A heritage parchment swing-tag with a notched-corner portrait face, a matte
bronze grommet threaded on cotton twine, a debossed inner border, and — on
affordable cards — a pressed burgundy wax seal at the foot. The face is a warm
cream stock with faint horizontal paper banding so it reads as pressed card
rather than flat plastic; a mahogany edge and a reinforcement washer under the
grommet sell it as a physical tag hanging off the card's top-left corner.

Locked cards cool the whole stock to grey and swap the wax to a cold grey-mauve
so the tag still reads as the same object, just spent of colour.

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

# The tag face is authored directly in the 2x card buffer's device px (like the
# tl2 swing-tag), so FACE_W/FACE_H and every sc.m() feature share one scale.
FACE_W = 72
FACE_H = 80
TILT = 6                              # pygame +CCW => the tag leans visually -6deg
NOTCH = 10                           # 45deg corner clip at each top corner


def _abbr(text):
    """Prices climb into the thousands; a swing-tag face is narrow, so collapse
    long numbers to a compact `1.2k` style that still stays readable at 1x."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def coin_ring(surf, cx, cy):
    """A small bronze rivet ring whose bore is punched clear so the cream face
    (and price) reads through it — the tag's decorative fastener motif."""
    r = sc.m(5)
    s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    cc = (r + 1, r + 1)
    pygame.draw.circle(s, (156, 116, 58), cc, r)
    pygame.draw.circle(s, (48, 28, 10), cc, r, 1)
    pygame.draw.circle(s, (0, 0, 0, 0), cc, sc.m(3) + 1)
    surf.blit(s, (cx - r - 1, cy - r - 1))


def _silhouette_mask():
    """White silhouette of the notched-corner portrait: bottom corners rounded,
    top corners sliced at 45deg. Used to clip both the cream fill and the edge
    stroke so nothing pokes past the tag's real outline."""
    mask = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, FACE_W, FACE_H),
                     border_bottom_left_radius=sc.m(5),
                     border_bottom_right_radius=sc.m(5))
    # clip the two top corners to the 45deg notch
    pygame.draw.polygon(mask, (0, 0, 0, 0), [(0, 0), (NOTCH, 0), (0, NOTCH)])
    pygame.draw.polygon(mask, (0, 0, 0, 0),
                        [(FACE_W - NOTCH, 0), (FACE_W, 0), (FACE_W, NOTCH)])
    return mask


def _cream_fill(top, bot, mask):
    """Warm parchment gradient with a 3-row +4/0/-4 luminance ripple so the
    stock reads as pressed paper, then clipped into the silhouette."""
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
    """2px mahogany rim following the notched-corner silhouette: a rounded-bottom
    rect outline plus the two notch diagonals, all clipped to the mask so the
    square-corner overhang is trimmed back to the 45deg cut."""
    edge = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.rect(edge, color, (0, 0, FACE_W, FACE_H), width=2,
                     border_bottom_left_radius=sc.m(5),
                     border_bottom_right_radius=sc.m(5))
    pygame.draw.line(edge, color, (NOTCH, 0), (0, NOTCH), 2)
    pygame.draw.line(edge, color, (FACE_W - NOTCH, 0), (FACE_W, NOTCH), 2)
    edge.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    face.blit(edge, (0, 0))


def _draw_price(face, text, center, fill_col, key_col):
    """Solid espresso numerals poured into the bold glyph mask, wrapped in a 1px
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
    ctrl = (grommet[0] - 8, grommet[1] - 8)      # bow the drape outward-left
    steps = 14
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * grommet[0] + 2 * (1 - t) * t * ctrl[0] + t * t * corner[0]
        y = (1 - t) ** 2 * grommet[1] + 2 * (1 - t) * t * ctrl[1] + t * t * corner[1]
        pts.append((x, y))
    pygame.draw.lines(face, cord, False, pts, 2)
    hp = [(x - 1, y - 1) for x, y in pts]
    pygame.draw.lines(face, hi, False, hp, 1)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the wax-cream tag at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant ("locked" for gated/too-expensive
    cards); any wallet-derived kwarg is absorbed so the sheet can force states."""
    affordable = (variant != "locked")
    text = _abbr(text)

    grommet = (36, 14)
    patch_c = (36, 14)
    coin_c = (36, 64)
    seal_c = (36, 68)
    price_c = (36, 38)

    if affordable:
        cream_top, cream_bot = (248, 240, 222), (232, 218, 190)
        price_fill = (48, 28, 10)
        patch_col = (208, 184, 148)
        seal_fill, seal_halo = (122, 30, 38), (86, 18, 26)
        cord, cord_hi = (176, 150, 104), (220, 196, 154)
    else:
        cream_top, cream_bot = (232, 226, 214), (214, 206, 190)
        price_fill = (150, 140, 124)
        patch_col = (190, 180, 166)
        seal_fill, seal_halo = (120, 104, 108), (92, 80, 84)
        cord, cord_hi = (168, 160, 146), (206, 200, 188)
    price_key = (210, 192, 158)

    mask = _silhouette_mask()
    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    face.blit(_cream_fill(cream_top, cream_bot, mask), (0, 0))

    _edge_stroke(face, mask, (60, 28, 8))

    # 1px debossed inner border, pressed in a touch from the mahogany rim.
    pygame.draw.rect(face, (196, 178, 142), (5, 5, FACE_W - 10, FACE_H - 10),
                     width=1, border_radius=sc.m(3))

    # reinforcement washer under the grommet, then the twine, then the grommet
    # so the cord tucks under the bronze eyelet.
    pygame.draw.circle(face, patch_col, patch_c, 14)
    _twine(face, grommet, (10, 2), cord, cord_hi)

    # matte heritage grommet: bronze body, a single lower-right shadow arc (no
    # upper-left sheen), a dark bore, and a punched-clear void.
    gr = sc.m(4)
    pygame.draw.circle(face, (174, 134, 44), grommet, gr)
    pygame.draw.arc(face, (60, 38, 8),
                    (grommet[0] - gr, grommet[1] - gr, gr * 2, gr * 2),
                    math.radians(-80), math.radians(70), max(1, sc.m(1)))
    pygame.draw.circle(face, (40, 28, 10), grommet, sc.m(3))
    pygame.draw.circle(face, (0, 0, 0, 0), grommet, sc.m(2))

    _draw_price(face, text, price_c, price_fill, price_key)

    coin_ring(face, *coin_c)

    # wax seal — burgundy when affordable, cold grey-mauve when locked. Halo ring
    # just outside so it reads pressed into the stock. No star geometry.
    seal_r = sc.m(4) + 1
    pygame.draw.circle(face, seal_fill, seal_c, seal_r)
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


# ── pixel verification (run BEFORE saving the sheet) ──────────────────────────
_va = render_card_1x("skin_mummy", sc.PRICE_VARIANT)
_vl = render_card_1x("skin_mummy", "locked")
_bg = (8, 8, 20)

tag_px = _va.get_at((12, 10))[:3]
assert any(abs(tag_px[i] - _bg[i]) > 40 for i in range(3)), \
    f"no tag at (12,10): {tag_px}"

pa, pl = _va.get_at((20, 25))[:3], _vl.get_at((20, 25))[:3]
assert pa != pl, f"states identical at (20,25): {pa}"

seal_hit = None
for px in range(18, 34):
    for py in range(36, 50):
        c = _va.get_at((px, py))[:3]
        if c[0] > 90 and c[0] - c[1] > 40 and c[0] - c[2] > 40:
            seal_hit = ((px, py), c)
            break
    if seal_hit:
        break
assert seal_hit, "burgundy wax seal not found on affordable card"
sc_lock = _vl.get_at(seal_hit[0][0:2])[:3] if False else None
print(f"tag(12,10):{tag_px}  aff(20,25):{pa} lck:{pl}  seal{seal_hit[0]}:{seal_hit[1]}")

# ── render sheet ──────────────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD = 20
GAP = 12
HDR_H = 40
CW, CH = sc.CARD_W, sc.CARD_H

cards = {
    "mummy_aff":   render_card_1x("skin_mummy",   sc.PRICE_VARIANT),
    "mummy_lck":   render_card_1x("skin_mummy",   "locked"),
    "kitsune_aff": render_card_1x("skin_kitsune", sc.PRICE_VARIANT),
    "kitsune_lck": render_card_1x("skin_kitsune", "locked"),
}

LABEL_H = 20
row1_h = CH
row2_h = 200
total_w = PAD + 4 * CW + 3 * GAP + PAD
total_h = HDR_H + LABEL_H + row1_h + GAP + row2_h + PAD
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("wax-cream · tl3 hang-tag · round 1", True, (255, 220, 80))
canvas.blit(ht, (total_w // 2 - ht.get_width() // 2, (HDR_H - ht.get_height()) // 2))

lf = hud_font(7)
card_list = [cards["mummy_aff"], cards["mummy_lck"], cards["kitsune_aff"], cards["kitsune_lck"]]
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
y1 = HDR_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD + i * (CW + GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HDR_H + (LABEL_H - lbl.get_height()) // 2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2×crop)"), ("mummy_lck", "mummy lck (2×crop)")]):
    x = PAD + i * (160 + GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "docs/store_price_tl3/wax_cream/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
