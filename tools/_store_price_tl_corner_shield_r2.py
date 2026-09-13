"""Round-2 render sheet for the `corner-shield` store-card price badge.

A heraldic escutcheon struck into the card's TOP-LEFT corner: a clean 5-vertex
shield (flat top, straight shoulders, single foot pointing inward toward the
card centre). The body is a dark enamel field so the coin-metal price numerals
read as POSITIVE relief; the RIM is the sole affordability channel — warm gold
when the wallet can pay, cool-steel when locked — so the tier hue on the crest
gem is never overloaded to mean two things at once. No coin glyph: the numerals
alone carry the price, and the shield IS the denomination mark.

Round-2 changes over round_1 (art-director notes):
  - Prices are abbreviated ("1,100" -> "1.1k") so they fit the ~32px usable
    width instead of overflowing.
  - The struck-crown glare is tamed (dimmer top highlight + dimmer gloss) so it
    no longer competes with the numerals.
  - The locked rim flips to genuine cool-steel (hue AND value), not just a dim
    gold, so the state read is unambiguous.
  - Enamel separates from the card's blue interior via a warm tint on the
    affordable body plus a 1px dark inner-shadow strip inside the rim.
  - Silhouette simplified to a 5-vertex escutcheon (the top chamfers were lost
    to smoothscale at 1x anyway).

Implemented as a monkey-patch of store_cards.price_chip. Review-only tooling —
never imported by the game.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

sys.path.insert(0, "/home/user/skybit")

import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font

sd.load()


# ── shield geometry (device px in the 2x author buffer) ───────────────────────
# 5-vertex escutcheon centred on (50,50): flat top at y=30, straight shoulders
# to the widest point at y=46, then a single foot at (50,72) aiming down toward
# the card centre. Chamfers dropped — they vanish under smoothscale at 1x.
BADGE_CX = sc.m(25)                  # = 50 in the 2x buffer
BADGE_CY = sc.m(25)                  # = 50
SHIELD = [(36, 30), (64, 30), (72, 46), (50, 72), (28, 46)]
# Numerals sit at the shield's own mass-centroid (y~45, the widest band) rather
# than the card-space centre (50,50): the foot tapers too narrow below y=50 to
# hold four glyphs, and 45 is where the escutcheon is actually widest.
NUM_CX = sum(p[0] for p in SHIELD) / len(SHIELD)
NUM_CY = sum(p[1] for p in SHIELD) / len(SHIELD)
# font(9) ink measures ~37px wide — it overspills this silhouette badly. font(7)
# keeps the abbreviated 4-char string fully inside the rim with clear margin.
NUM_FONT = 7

# Body enamel ramps. Affordable is warm-tinted (leans red over blue) so it reads
# as "warm enamel" against the card's cool-blue darkness; locked stays neutral.
BODY_AFFORD = [(0.0, (30, 21, 26)), (1.0, (24, 16, 22))]
BODY_LOCK = [(0.0, (14, 15, 28)), (1.0, (10, 11, 22))]

# 1px dark strip drawn just inside the rim so the enamel field is fenced off from
# the card interior even where their values are close.
INNER_SHADOW = (8, 6, 10)

# Rim = the affordability channel. Warm gold bevel over a dark bronze keyline
# when payable; genuine cool-steel bevel over a cool-slate keyline when locked —
# the state flip is legible by BOTH hue and value.
RIM_AFFORD_HI = (230, 200, 130, 220)
RIM_AFFORD_DK = (120, 88, 28, 235)
RIM_LOCK_HI = (150, 148, 158, 190)
RIM_LOCK_DK = (70, 72, 84, 205)

LOCK_NUM = (150, 132, 92)            # dim coin-metal for the unaffordable state


def _abbr(text):
    """Compact a price string to 4 chars max so it fits the shield's usable
    width. Thousands collapse to a "1.1k" form (or bare "3k" when the hundreds
    digit is zero); sub-1000 values pass through unchanged."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _inset_poly(poly, d):
    """Shrink a polygon toward its centroid by `d` device px — used to seat the
    inner-shadow strip just inside the rim."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        vx, vy = cx - x, cy - y
        n = (vx * vx + vy * vy) ** 0.5 or 1.0
        out.append((x + vx / n * d, y + vy / n * d))
    return out


def _body_fill(surf, poly, stops):
    """Pour the dark enamel ramp into the shield outline: a full-rect vertical
    gradient clipped to the polygon via BLEND_RGBA_MIN against a shield alpha
    mask, then a faint top sheen for a hint of struck curvature."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    minx, maxx = int(min(xs)), int(max(xs))
    lo, hi = int(min(ys)), int(max(ys))
    bw, bh = maxx - minx + 1, hi - lo + 1
    lpoly = [(x - minx, y - lo) for x, y in poly]

    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), lpoly)

    body = sc.vgrad_stops(bw, bh, 0, stops, 255, gamma=1.05)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # top inner sheen so the flat enamel field reads with slight crown curvature.
    sheen = pygame.Surface((bw, bh), pygame.SRCALPHA)
    sh_h = max(1, int(bh * 0.55))
    for y in range(sh_h):
        a = int(24 * (1 - y / sh_h) ** 1.6)
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (bw, y))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(sheen, (0, 0))
    surf.blit(body, (minx, lo))


def _inner_shadow(surf, poly):
    """A 1px dark keyline set just inside the rim — fences the enamel field off
    from the card's blue interior even where their values run close."""
    inner = _inset_poly(poly, sc.m(2))
    pygame.draw.polygon(surf, INNER_SHADOW, inner, max(1, sc.m(1)))


def _gloss(surf, poly):
    """A soft top-left specular pool — an ellipse tucked under the flat top edge,
    additively blended and clipped to the shield. Kept low-alpha so it no longer
    blows a pure-white band that competes with the numerals."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    minx, maxx = int(min(xs)), int(max(xs))
    lo, hi = int(min(ys)), int(max(ys))
    bw, bh = maxx - minx + 1, hi - lo + 1
    lpoly = [(x - minx, y - lo) for x, y in poly]

    layer = pygame.Surface((bw, bh), pygame.SRCALPHA)
    er = pygame.Rect(0, 0, int(bw * 0.62), int(bh * 0.4))
    er.center = (int(bw * 0.4), int(bh * 0.28))
    pygame.draw.ellipse(layer, (255, 248, 224, 22), er)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), lpoly)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (minx, lo), special_flags=pygame.BLEND_ADD)


def _rim(surf, poly, hi, dk):
    """Trace the ~2px beveled metal rim. A dark contact keyline defines the
    silhouette; the colour bevel seats inside it, brightest along the top + left
    (lit) edges and dimming toward the bottom-right, with a gently struck crown
    on the flat top edge — the read that carries affordability."""
    ys = [p[1] for p in poly]
    miny, maxy = min(ys), max(ys)
    span = max(1, maxy - miny)

    # dark keyline first so the bright bevel sits within a defined edge.
    pygame.draw.polygon(surf, dk[:3], poly, max(1, sc.m(2)))

    hi3 = hi[:3]
    dk3 = dk[:3]
    w = max(1, sc.m(1.4))
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        t = ((a[1] + b[1]) / 2 - miny) / span
        col = lerp_color(hi3, dk3, max(0.0, min(1.0, t)))
        pygame.draw.line(surf, col, a, b, w)
    # gently struck top edge — dimmed from r1 so it no longer flares to pure 255.
    pygame.draw.line(surf, lerp_color(hi3, WHITE, 0.14), poly[0], poly[1],
                     max(1, sc.m(0.8)))


def _numerals(surf, cx, cy, text, afford):
    """Abbreviated price in coin-metal relief centred at the shield centroid — no coin
    glyph. A dark down-cast lifts the glyphs so they read struck-proud.
    Affordable pours the 4-stop sovereign gradient into the glyph mask; locked
    tints a dim coin-metal so the price stays legible but visibly out of reach."""
    text = _abbr(text)
    f = sc.font(NUM_FONT)
    mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.9))
    rr = mask.get_rect(center=(cx, cy))

    cast = mask.copy()
    cast.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    cast.set_alpha(160)
    surf.blit(cast, (rr.x, rr.y + sc.m(1)))

    img = mask.copy()
    if afford:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((*LOCK_NUM, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, rr)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Corner-shield replacement for the default bottom price chip. Ignores the
    handed-in bottom-chip anchor and strikes the escutcheon at the fixed top-left
    corner. Affordability is forced through the `variant` channel so the harness
    can render both states on one sheet."""
    affordable = (variant != "locked")
    poly = [(BADGE_CX - sc.m(25) + dx, BADGE_CY - sc.m(25) + dy)
            for dx, dy in SHIELD]

    _body_fill(surf, poly, BODY_AFFORD if affordable else BODY_LOCK)
    _inner_shadow(surf, poly)
    _gloss(surf, poly)
    if affordable:
        _rim(surf, poly, RIM_AFFORD_HI, RIM_AFFORD_DK)
    else:
        _rim(surf, poly, RIM_LOCK_HI, RIM_LOCK_DK)
    _numerals(surf, NUM_CX, NUM_CY, text, affordable)

    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return pygame.Rect(int(min(xs)), int(min(ys)),
                       int(max(xs) - min(xs)), int(max(ys) - min(ys)))


sc.price_chip = my_price_chip        # patch BEFORE any draw_card call


# =============================================================================
# Render sheet
# =============================================================================
def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def zoom_tl(card_1x, scale=4):
    """4x nearest-neighbour crop of the top-left badge area (x=0..64, y=0..64 in
    the 1x card) so every rim edge and numeral is legible for review."""
    src = pygame.Rect(0, 0, 64, 64)
    crop = pygame.Surface((src.w, src.h), pygame.SRCALPHA)
    crop.blit(card_1x.subsurface(src.clip(card_1x.get_rect())), (0, 0))
    return pygame.transform.scale(crop, (256, 256))


def _label(surf, text, cx, y, size=13, col=(232, 226, 208)):
    f = hud_font(size, True)
    img = f.render(text, True, col)
    surf.blit(img, img.get_rect(center=(cx, y)))


def build_sheet():
    BG = (8, 8, 20)
    PAD = 20
    GAP = 12
    HEADER_H = 40
    LABEL_H = 20

    row1 = [
        ("skin_mummy", True, "MUMMY  EPIC  affordable"),
        ("skin_mummy", False, "MUMMY  EPIC  locked"),
        ("skin_kitsune", True, "KITSUNE  LEGEND.  affordable"),
        ("skin_kitsune", False, "KITSUNE  LEGEND.  locked"),
    ]
    cards1 = [(render_card_1x(sid, aff), lab) for sid, aff, lab in row1]

    zoom_afford = zoom_tl(cards1[0][0])
    zoom_lock = zoom_tl(cards1[1][0])
    row2 = [(zoom_afford, "4x  badge  affordable"),
            (zoom_lock, "4x  badge  locked")]

    r1_cell_w = sc.CARD_W
    r1_h = sc.CARD_H
    r2_cell_w = 256
    r2_h = 256

    row1_w = 4 * r1_cell_w + 3 * GAP
    row2_w = 2 * r2_cell_w + 1 * GAP
    content_w = max(row1_w, row2_w)
    sheet_w = content_w + 2 * PAD
    sheet_h = (HEADER_H + r1_h + LABEL_H + GAP + r2_h + LABEL_H + PAD)

    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill(BG)
    _label(sheet, "corner-shield  —  top-left price badge  —  round 2",
           sheet_w // 2, HEADER_H // 2 + 2, size=15, col=(246, 224, 150))

    # Row 1 — four full 1x cards.
    x = PAD + (content_w - row1_w) // 2
    y = HEADER_H
    for card, lab in cards1:
        sheet.blit(card, (x, y))
        _label(sheet, lab, x + r1_cell_w // 2, y + r1_h + LABEL_H // 2)
        x += r1_cell_w + GAP

    # Row 2 — 4x badge zoom crops.
    x = PAD + (content_w - row2_w) // 2
    y = HEADER_H + r1_h + LABEL_H + GAP
    for img, lab in row2:
        sheet.blit(img, (x, y))
        _label(sheet, lab, x + r2_cell_w // 2, y + r2_h + LABEL_H // 2)
        x += r2_cell_w + GAP

    return sheet


# =============================================================================
# Pixel verification
# =============================================================================
def verify():
    # _abbr must compact real thousands-prices and pass through short ones.
    assert _abbr("1,100") == "1.1k", _abbr("1,100")
    assert _abbr("3,500") == "3.5k", _abbr("3,500")
    assert _abbr("3,000") == "3k", _abbr("3,000")
    assert _abbr("450") == "450", _abbr("450")
    assert all(len(_abbr(t)) <= 4 for t in ("1,100", "3,500", "9,900", "3,000"))

    aff = render_card_1x("skin_mummy", True)
    lock = render_card_1x("skin_mummy", False)
    # (25,22) in the 1x card is the numeral centroid (shield centre ~50,45 in the
    # 2x buffer). Sample it to confirm the price is present + the two states
    # differ; sample a guaranteed body pixel beside it for the enamel field.
    ca = tuple(aff.get_at((25, 22)))
    cl = tuple(lock.get_at((25, 22)))
    ba = tuple(aff.get_at((25, 30)))     # enamel field below the numeral (foot)
    bl = tuple(lock.get_at((25, 30)))
    print("numeral centre @ (25,22) afford:", ca, "locked:", cl)
    print("enamel body @ (25,30) afford:", ba, "locked:", bl)

    assert ca[3] > 200, f"badge centre not opaque: {ca}"
    assert not (ca[0] > 230 and ca[1] > 220), f"centre reads bright card gold: {ca}"
    assert ca != cl, f"afford and locked identical at centre: {ca} vs {cl}"

    assert ba[3] > 200 and max(ba[:3]) < 70, f"enamel body not dark: {ba}"
    assert bl[3] > 200 and max(bl[:3]) < 70, f"locked enamel not dark: {bl}"
    assert ba != bl, f"afford and locked enamel identical: {ba} vs {bl}"
    # warm-vs-cool enamel: affordable leans warm (R >= B), locked leans cool.
    assert ba[0] >= ba[2], f"affordable enamel not warm: {ba}"
    print("verify OK")


if __name__ == "__main__":
    verify()
    sheet = build_sheet()
    out = "/home/user/skybit/docs/store_price_tl_badges/corner-shield/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    w, h = sheet.get_size()
    print(f"saved {w}x{h} -> {out}")
