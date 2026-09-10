"""tl3 price concept: CHAIN-STEEL — round 2.

Addresses all art-director notes from round 1:

1. TAPER DRAMATIC: FACE_POLY redrawn — top edge 76dp (chamfered 3dp corners),
   base 44dp, 32dp taper over 74dp height.  The keystone silhouette is now
   unmistakable.

2. CHAIN FIXED: 2 links with cooler-grey body (90,96,104) and 1px dark
   keyline (40,46,54) separating link from face and from each other.  Each
   link is a sc.m(3)×sc.m(4) oval ring, 30 % overlap for the interlocked
   read.  The fob is shifted 9dp lower (OY 17→26) so a 14px navy card-body
   zone sits above the face — links are dark on dark-navy, high contrast.

3. COIN_RING CALLED: coin_ring helper is now invoked below the price, centred
   in the face — the family unifier across all five tl3 concepts.

4. PRICE RAISED: price centre moved to y≈36dp face-local (up from y≈56dp in
   r1) so it lives in the widest mid-body band with clear headroom above.

5. PRICE CONTRAST IMPROVED: a darker inked plaque (68,74,82 @ α 215) is
   struck behind the numeral, and the dark keyline is widened to kw=sc.m(1)
   (=2px at 2× device) so the champagne glyph pops.

Kept from r1: brushed-steel gradient, spot-UV band, champagne hairline, steel
grommet with real transparent void, LOCKED desaturation logic.

Output: docs/store_price_tl3/chain_steel/round_2.png
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


# Family-unifier coin token — byte-identical across all tl3 fobs so every
# concept in the set carries the same donut stamp regardless of material.
def coin_ring(surf, cx, cy):
    r = sc.m(5)
    s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
    cc = (r+1, r+1)
    pygame.draw.circle(s, (156, 116, 58), cc, r)
    pygame.draw.circle(s, (48, 28, 10), cc, r, 1)
    pygame.draw.circle(s, (0, 0, 0, 0), cc, sc.m(3)+1)
    surf.blit(s, (cx-r-1, cy-r-1))


def draw_grommet_steel(surf, cx, cy):
    """Steel recolour of the brass baseline: cool body, up-left bright arc
    and lower-right shadow arc for a machined-eyelet read, dark bore that
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
    """One oval ring at sc.m(3)×sc.m(4) half-axes; alternating orientation
    on adjacent links creates the interlocked-chain read without rotated blits.
    The 1px dark keyline on both the outer and inner rim separates each link
    from the steel face and from its neighbour."""
    rx = sc.m(3) if vertical else sc.m(4)
    ry = sc.m(4) if vertical else sc.m(3)
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    # body ring, then keyline overpaints the ring's outer pixel so the link
    # has a hard dark edge against whatever background it lands on
    pygame.draw.ellipse(surf, col, rect, sc.m(2))
    pygame.draw.ellipse(surf, outline, rect, 1)


def draw_price(surf, cx, cy, text, price_col):
    """Champagne numeral on a darker inked plaque that gives the digit its
    own ground against the brushed-steel face.  A 2px device keyline
    (kw=sc.m(1) = 2px at 2× supersample) gives the stroke a hard printed
    edge so the glyph pops cleanly."""
    # Struck plaque: darker than the mid-body steel, pinned to the face
    pw, ph = sc.m(14), sc.m(6)
    plaque = pygame.Surface((pw * 2, ph * 2), pygame.SRCALPHA)
    pygame.draw.rect(plaque, (68, 74, 82, 215), (0, 0, pw * 2, ph * 2),
                     border_radius=sc.m(1))
    surf.blit(plaque, (cx - pw, cy - ph))
    size = 16.0
    f = sc.font(size)
    while sc._glyph_base(text, f, 0).get_width() > sc.m(26) and size > 8:
        size -= 0.5
        f = sc.font(size)
    sc.plain_text(surf, text, f, (cx, cy), price_col, shadow_a=0,
                  weight=sc.m(0.8), keyline=(28, 32, 40), kw=sc.m(1))


# Dramatic keystone taper: top ~76dp (flat crown 70dp + 3dp chamfered
# corners = 76dp total), base 44dp — 32dp of taper over 74dp height.
FACE_POLY = [(5, 0), (75, 0), (78, 3), (62, 74), (18, 74), (2, 3)]
FACE_W, FACE_H = 80, 74
# OY=26 shifts the fob 9dp below r1 (was OY=17), opening a 14-px navy
# card-body zone above the face where both chain links sit at maximum
# dark-on-navy contrast without competing with the steel face at the top.
OX, OY = 10, 26


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    if affordable:
        stops = [(0.0, (198, 204, 210)), (0.5, (150, 158, 166)),
                 (1.0, (118, 126, 134))]
        uv_light  = (210, 218, 226)
        hairline  = (210, 190, 150)
        edge_bright, edge_dark = (226, 232, 238), (88, 94, 102)
        chain_col = (90, 96, 104)
        chain_out = (40, 46, 54)
        price_col = (242, 224, 178)
    else:
        stops = [(0.0, (150, 156, 162)), (0.5, (112, 118, 124)),
                 (1.0, (84, 90, 96))]
        uv_light  = (168, 174, 180)
        hairline  = (130, 138, 144)
        edge_bright, edge_dark = (200, 206, 212), (70, 76, 82)
        # LOCKED desaturates the whole fob — colder steel, grey chain,
        # grey numeral — so "can't afford" reads at a glance.
        chain_col = (86, 88, 94)
        chain_out = (36, 38, 44)
        price_col = (150, 150, 150)

    # ── face: brushed-steel gradient + spot-UV crown + bevel, masked to shape ──
    face = sc.vgrad_stops(FACE_W, FACE_H, 0, stops, 255, 1.0).copy()
    # spot-UV gloss band over the top ~20 %: lighter tone fading down in 15
    # steps, capped by a champagne hairline at the coating edge.
    band = pygame.Surface((FACE_W, 15), pygame.SRCALPHA)
    for y in range(15):
        a = int(150 * (1 - y / 15))
        pygame.draw.line(band, (*uv_light, a), (0, y), (FACE_W - 1, y))
    face.blit(band, (0, 0))
    # hairline x coords interpolated for the new taper at face-local y=15:
    # left≈5, right≈75 (was 2..77 for the old shallower trapezoid)
    pygame.draw.line(face, hairline, (5, 15), (75, 15), 1)
    # crown bevel bright: geometry tracks new FACE_POLY chamfer corners
    pygame.draw.lines(face, edge_bright, False, [(3, 3), (5, 1), (75, 1), (77, 3)], 1)
    # base bevel dark: new base runs x=18..62, so bevel sits at x=19..61
    pygame.draw.line(face, edge_dark, (19, 72), (61, 72), 1)
    mask = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), FACE_POLY)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # soft contact shadow so the fob reads as a physical object on the card
    sh = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 90), FACE_POLY)
    surf.blit(sh, (OX + 1, OY + 2))
    surf.blit(face, (OX, OY))

    # ── chain: 2 interlocked oval links above the steel grommet ──
    gx, gy = OX + 40, OY + 14          # grommet centre in surf pixel coords
    # 30 % overlap step: 70 % of one link height (2*sc.m(4)=16 px)
    step = int(sc.m(4) * 2 * 0.70)     # = 11 SS px
    # The vertical link (back) is drawn first so the horizontal link (front)
    # can thread through it visually at their overlap zone — correct chain
    # interlock without explicit clipping.
    cy_vert  = gy - sc.m(4) - sc.m(2)  # just above grommet top: gy - 12
    cy_horiz = cy_vert - step           # one step higher: gy - 23
    draw_chain_link(surf, gx, cy_vert,  True,  chain_col, chain_out)
    draw_chain_link(surf, gx, cy_horiz, False, chain_col, chain_out)
    draw_grommet_steel(surf, gx, gy)

    # ── price: raised to y≈36dp face-local, on inked plaque ──
    draw_price(surf, OX + 40, OY + 36, text, price_col)

    # ── coin_ring family token below price, centred in the face ──
    coin_ring(surf, OX + 40, OY + 58)

    return pygame.Rect(cx, cy, 0, 0)


sc.price_chip = my_price_chip


# ── render sheet ────────────────────────────────────────────────────────────
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
PAD = 20
GAP = 12
HDR_H = 40
LABEL_H = 20

CW, CH = sc.CARD_W, sc.CARD_H   # 162 x 100

cards = {
    "mummy_aff":   render_card_1x("skin_mummy",   sc.PRICE_VARIANT),
    "mummy_lck":   render_card_1x("skin_mummy",   "locked"),
    "kitsune_aff": render_card_1x("skin_kitsune", sc.PRICE_VARIANT),
    "kitsune_lck": render_card_1x("skin_kitsune", "locked"),
}

row1_h = CH
row2_h = 200
total_h = HDR_H + LABEL_H + row1_h + GAP + row2_h + PAD
total_w = PAD + 4 * CW + 3 * GAP + PAD
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("chain-steel · tl3 hang-tag · round 2", True, (255, 220, 80))
canvas.blit(ht, (total_w // 2 - ht.get_width() // 2,
                 (HDR_H - ht.get_height()) // 2))

lf = hud_font(7)
labels    = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
card_list = [cards["mummy_aff"], cards["mummy_lck"],
             cards["kitsune_aff"], cards["kitsune_lck"]]

y1 = HDR_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD + i * (CW + GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HDR_H + (LABEL_H - lbl.get_height()) // 2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2× crop)"),
                                   ("mummy_lck", "mummy lck (2× crop)")]):
    x = PAD + i * (160 + GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "docs/store_price_tl3/chain_steel/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
