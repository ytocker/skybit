"""tl3 price concept: CHAIN-STEEL — round 1.

A brushed-steel keystone hang-tag that reads as a physical price fob riveted to
the card: a spot-UV gloss band across the crown, a brass-bore steel grommet, and
a short run of interlocking chain links climbing off the top of the clear zone.
The price is a champagne numeral struck into the mid-body where the trapezoid is
widest so it never crowds the tapered base. LOCKED desaturates the whole fob
(colder steel, grey chain, grey numeral) instead of recolouring one element, so
"can't afford" reads at a glance without a separate badge.

The concept is delivered by monkey-patching sc.price_chip so the real
sc.draw_card composites the fob in the top-left zone of the 2x author buffer;
everything below the `sc.price_chip = my_price_chip` line is the review sheet.

Output: docs/store_price_tl3/chain_steel/round_1.png
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color, WHITE, NEAR_BLACK
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


# Shared coin_ring helper (byte-identical family unifier) — kept so every tl3
# concept carries the same coin token even when a given fob doesn't stamp one.
def coin_ring(surf, cx, cy):
    r = sc.m(5)
    s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
    cc = (r+1, r+1)
    pygame.draw.circle(s, (156, 116, 58), cc, r)
    pygame.draw.circle(s, (48, 28, 10), cc, r, 1)
    pygame.draw.circle(s, (0, 0, 0, 0), cc, sc.m(3)+1)
    surf.blit(s, (cx-r-1, cy-r-1))


# Shared grommet helper (3-layer, brass variant) — the family baseline; the
# steel concept below is a recolour of this same 3-layer build so the eyelet
# geometry stays identical across fobs.
def draw_grommet_brass(surf, cx, cy):
    r1, r2, r3 = sc.m(4)+1, sc.m(3), sc.m(2)
    pygame.draw.circle(surf, (184, 146, 74), (cx, cy), r1)
    pygame.draw.arc(surf, (240, 210, 100),
                    (cx-r1, cy-r1, r1*2, r1*2), math.pi*0.5, math.pi*1.5, 2)
    pygame.draw.arc(surf, (80, 50, 10),
                    (cx-r1, cy-r1, r1*2, r1*2), -math.pi*0.5, math.pi*0.5, 2)
    pygame.draw.circle(surf, (40, 30, 18), (cx, cy), r2)
    pygame.draw.circle(surf, (0, 0, 0, 0), (cx, cy), r3)


def draw_grommet_steel(surf, cx, cy):
    """Steel recolour of the brass baseline: cool body, an up-left bright arc + a
    lower-right shadow arc for a machined-eyelet read, over a dark brass bore that
    punches a real transparent hole so the fob looks physically pierced."""
    r1, r2, r3 = sc.m(4)+1, sc.m(3), sc.m(2)
    pygame.draw.circle(surf, (150, 158, 166), (cx, cy), r1)
    pygame.draw.arc(surf, (190, 198, 204),
                    (cx-r1, cy-r1, r1*2, r1*2), math.pi*0.5, math.pi*1.5, 2)
    pygame.draw.arc(surf, (60, 68, 76),
                    (cx-r1, cy-r1, r1*2, r1*2), -math.pi*0.5, math.pi*0.5, 2)
    pygame.draw.circle(surf, (40, 30, 18), (cx, cy), r2)
    pygame.draw.circle(surf, (0, 0, 0, 0), (cx, cy), r3)


def draw_chain_link(surf, cx, cy, vertical, col, outline):
    """One oval link as a thick ring (front/back halves fall out of the stroke
    naturally); alternating orientation up the run reads as an interlocked chain
    without needing rotated blits."""
    if vertical:
        rx, ry = sc.m(2)+1, sc.m(4)
    else:
        rx, ry = sc.m(4), sc.m(2)+1
    rect = pygame.Rect(cx-rx, cy-ry, rx*2, ry*2)
    pygame.draw.ellipse(surf, col, rect, sc.m(2))
    pygame.draw.ellipse(surf, outline, rect, 1)


def draw_price(surf, cx, cy, text, price_col):
    """Champagne numeral struck into the widest mid-body band. Auto-shrinks to
    stay inside the taper, with a 1px dark keyline so it holds against steel."""
    size = 16.0
    f = sc.font(size)
    while sc._glyph_base(text, f, 0).get_width() > sc.m(26) and size > 8:
        size -= 0.5
        f = sc.font(size)
    sc.plain_text(surf, text, f, (cx, cy), price_col, shadow_a=0,
                  weight=sc.m(0.8), keyline=(40, 44, 50), kw=1)


# Keystone trapezoid, chamfered top corners (3dp @ 45 deg). Face-local, dp.
FACE_POLY = [(4, 0), (76, 0), (78.6, 3.0), (69, 74), (11, 74), (1.4, 3.0)]
FACE_W, FACE_H = 80, 74
# Offset placing the polygon centroid near (50, 54) in the 2x author buffer so
# the fob seats in the card's top-left zone, clear of the dome + crest gem.
OX, OY = 10, 17


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    if affordable:
        stops = [(0.0, (198, 204, 210)), (0.5, (150, 158, 166)), (1.0, (118, 126, 134))]
        uv_light = (210, 218, 226)
        hairline = (210, 190, 150)
        edge_bright, edge_dark = (226, 232, 238), (88, 94, 102)
        chain_col, chain_out = (160, 168, 176), (96, 104, 112)
        price_col = (242, 224, 178)
        grommet = draw_grommet_steel
    else:
        stops = [(0.0, (150, 156, 162)), (0.5, (112, 118, 124)), (1.0, (84, 90, 96))]
        uv_light = (168, 174, 180)
        hairline = (130, 138, 144)
        edge_bright, edge_dark = (200, 206, 212), (70, 76, 82)
        chain_col, chain_out = (110, 116, 122), (78, 84, 90)
        price_col = (150, 150, 150)
        grommet = draw_grommet_steel

    # ── face: brushed-steel gradient + spot-UV crown + bevel, masked to shape ──
    face = sc.vgrad_stops(FACE_W, FACE_H, 0, stops, 255, 1.0).copy()
    # spot-UV gloss band over the top 20%: a lighter tone fading down in ~12
    # steps, capped by a champagne hairline where the coating edge sits.
    band = pygame.Surface((FACE_W, 15), pygame.SRCALPHA)
    for y in range(15):
        a = int(150 * (1 - y / 15))
        pygame.draw.line(band, (*uv_light, a), (0, y), (FACE_W - 1, y))
    face.blit(band, (0, 0))
    pygame.draw.line(face, hairline, (2, 15), (77, 15), 1)
    # bevel stripe: bright lit crown edge, dark base edge, 1dp inside the outline.
    pygame.draw.lines(face, edge_bright, False, [(3, 3), (5, 1), (75, 1), (77, 3)], 1)
    pygame.draw.line(face, edge_dark, (12, 72), (68, 72), 1)
    mask = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), FACE_POLY)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # cast a soft contact shadow so the fob sits ON the card, not painted flat.
    sh = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 90), FACE_POLY)
    surf.blit(sh, (OX + 1, OY + 2))
    surf.blit(face, (OX, OY))

    # ── chain climbing off the crown, then the grommet over its foot ──
    gx, gy = OX + 40, OY + 14
    for ly, vert in [(gy - 35, True), (gy - 25, False), (gy - 15, True), (gy - 5, False)]:
        draw_chain_link(surf, gx, ly, vert, chain_col, chain_out)
    grommet(surf, gx, gy)

    # ── price in the widest mid-body band ──
    draw_price(surf, OX + 40, OY + 56, text, price_col)
    return pygame.Rect(cx, cy, 0, 0)


sc.price_chip = my_price_chip


# ── render sheet ────────────────────────────────────────────────────────────
def render_card_1x(sid, variant):
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2*inset,
                       sc.CARD_H * sc.SS - 2*inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def zoom_left(card_1x):
    crop = card_1x.subsurface((0, 0, 80, 100))
    return pygame.transform.scale(crop, (160, 200))


BG = (8, 8, 20)
PAD = 20
GAP = 12
HDR_H = 40
LABEL_H = 20

CW, CH = sc.CARD_W, sc.CARD_H  # 162x100

cards = {
    "mummy_aff":   render_card_1x("skin_mummy",   sc.PRICE_VARIANT),
    "mummy_lck":   render_card_1x("skin_mummy",   "locked"),
    "kitsune_aff": render_card_1x("skin_kitsune", sc.PRICE_VARIANT),
    "kitsune_lck": render_card_1x("skin_kitsune", "locked"),
}

row1_h = CH
row2_h = 200
total_h = HDR_H + LABEL_H + row1_h + GAP + row2_h + PAD
total_w = PAD + 4*CW + 3*GAP + PAD
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("chain-steel · tl3 hang-tag · round 1", True, (255, 220, 80))
canvas.blit(ht, (total_w//2 - ht.get_width()//2, (HDR_H - ht.get_height())//2))

lf = hud_font(7)
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
card_list = [cards["mummy_aff"], cards["mummy_lck"], cards["kitsune_aff"], cards["kitsune_lck"]]

y1 = HDR_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD + i*(CW+GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HDR_H + (LABEL_H - lbl.get_height())//2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2×crop)"),
                                  ("mummy_lck", "mummy lck (2×crop)")]):
    x = PAD + i*(160+GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "docs/store_price_tl3/chain_steel/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
