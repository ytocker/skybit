#!/usr/bin/env python3
"""ticket-stub · confirm_purchase_v8 · card-frame-v1 · round_2

The popup reads as a tall admit-one boarding pass. A horizontal PERFORATION
line at y=330 splits it into an UPPER TICKET BODY (hero + event name + Zone A
face value, printed as gold foil directly on the indigo ticket stock) and a
LOWER COUNTERFOIL TEAROFF (buttons + Zone B rarity ribbon) tinted markedly
darker with a diagonal hatch. A physical tear STEP (dark line + gold lip) and a
row of lit-lipped punched holes at the tear line — plus larger edge notches that
bite into the gold rim — make the top ticket / bottom stub read as punched-
through, not a dashed line on a card. This is the set's silhouette differentiator.
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (m, SS, font, vgrad_stops, bevel_rim, top_sheen,
                              coin_glyph, facet_gem, _alpha_aura,
                              plain_text, lerp_color, CABO_LO, CABO_HI, CARD_T,
                              CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
                              PRICE_RIM_BRIGHT)
from PIL import Image, ImageDraw

# mandatory gloss_sweep patch — BLEND_ADD amount must follow the curve so a
# near-black body isn't blown white.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0: continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

TIERS = [
    ("RARE",      "skin_wizard",    "720", {"gem": (108, 188, 252), "glow": (60, 140, 220), "deep": (20, 60, 130)}),
    ("EPIC",      "skin_prism",     "720", {"gem": (194, 122, 248), "glow": (140, 60, 220), "deep": (70, 20, 160)}),
    ("LEGENDARY", "skin_astronaut", "720", {"gem": (255, 202, 104), "glow": (220, 150, 40), "deep": (140, 80, 10)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}

POP_W, POP_H = 260, 442; CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
CARD_BOT_Y = CARD_TOP_Y + CARD_H                       # 426
DISC_CY, DISC_R = 135, 53
PERF_Y = 330                                           # tear line — top of counterfoil
STRIPE_Y, STRIPE_H, STRIPE_W = 130, 8, 236
Y_NAME = 213
ZA_CY = 247
DETAIL_CY = 268
HOLE_CX, HOLE_R = 35, 8                                 # coin/seat punch, now on tear line
ZB_CY = 402
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2; CAN_CX = CX + (BTN_W + BTN_GAP) // 2

# Ticket stock: indigo card body value between the two indigo counterfoil tints.
BODY_STOPS = [(0.0, (18, 20, 56)), (0.5, (12, 14, 40)), (1.0, (16, 18, 52))]
# Counterfoil "stub" runs MUCH darker than the body so the tear reads as two
# separate pieces of stock, not one card with a dashed line.
FOIL_STOPS = [(0.0, (10, 11, 30)), (1.0, (6, 7, 20))]
PUNCH = (8, 8, 20)                                        # reads as punched-through
LIP_GOLD = (200, 170, 110, 190)                          # lit lip on the dark body
LIP_COOL = (70, 74, 110)                                 # lit lip against the gold rim
NAME_COL = (230, 220, 190)                               # warm cream / gold ink

# Ticket-face value ramp: same amber as the price chip but with a LIFTED foot so
# the numeral bottom doesn't mush into the dark indigo stock.
TICKET_PRICE_STOPS = [(0.00, (236, 176, 72)), (0.45, (204, 132, 42)),
                      (1.00, (175, 120, 45))]


def _num_outline(surf, base, color, center, off):
    """Ring-stamp a tinted copy of the numeral mask at `off` on 8 compass points
    so the glyph gains an even keyline of that colour."""
    kl = base.copy()
    kl.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = kl.get_rect(center=center)
    for ang in range(0, 360, 45):
        dx = int(round(off * math.cos(math.radians(ang))))
        dy = int(round(off * math.sin(math.radians(ang))))
        surf.blit(kl, (r.x + dx, r.y + dy))


def _lit_ring(big, center, r, color):
    """A 1px lit lip just OUTSIDE a punch core so the hole reads as punched
    THROUGH the stock (a bright edge catching light on the torn paper wall).
    Drawn via an alpha surface so the ring composites rather than replacing the
    body's own alpha."""
    d = r * 2 + m(3)
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, color, (d // 2, d // 2), r + max(1, m(1)), width=max(1, m(1)))
    big.blit(s, (center[0] - d // 2, center[1] - d // 2))


def _hline_alpha(big, x0, x1, y, color):
    """Alpha-composited 1px horizontal rule — used for the gold tear lip."""
    w = max(1, x1 - x0)
    s = pygame.Surface((w, max(1, m(1))), pygame.SRCALPHA)
    s.fill(color)
    big.blit(s, (x0, y))


# ── ticket stock: body + counterfoil + gold-foil border ─────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H)); rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, BODY_STOPS, 255, gamma=1.1), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=52)

    # counterfoil tearoff — a much darker indigo panel filling the body BELOW the
    # tear line, masked to the body's rounded bottom corners so the stub sits
    # inside the stock. A diagonal hatch (raised alpha so it survives at 1×)
    # differentiates it from the upper body.
    cfh = m(CARD_BOT_Y - PERF_Y)
    cf = vgrad_stops(m(CARD_W), cfh, 0, FOIL_STOPS, 255).copy()
    hatch = pygame.Surface((m(CARD_W), cfh), pygame.SRCALPHA)
    step = m(CARD_W) // 9
    for i in range(-2, 12):
        x0 = i * step
        pygame.draw.line(hatch, (80, 80, 120, 45), (x0, 0), (x0 - cfh, cfh), max(1, m(1)))
    cf.blit(hatch, (0, 0))
    cmask = pygame.Surface((m(CARD_W), cfh), pygame.SRCALPHA)
    pygame.draw.rect(cmask, (255, 255, 255, 255), cmask.get_rect(),
                     border_bottom_left_radius=rad, border_bottom_right_radius=rad)
    cf.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(cf, (m(CARD_X), m(PERF_Y)))

    # gold-foil ticket border ON TOP of both zones so it frames the whole pass.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, m(4)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))


def perforation(big):
    """The tear geometry: a physical STEP at the fold (dark shadow line + a lit
    gold lip just below it) so the eye reads a raised paper edge, then a tight
    row of lit-lipped punched holes, then two larger edge notches biting INTO the
    gold rim. Lit lips are what make R1's invisible holes finally read."""
    y = m(PERF_Y)

    # physical tear step — a dark contact shadow above the fold, a warm gold lip
    # catching light just below it. This step is the "top ticket / bottom stub"
    # cue that the dashed holes alone couldn't carry.
    pygame.draw.line(big, (0, 0, 10), (m(13), y - m(1)), (m(247), y - m(1)), max(1, m(1)))
    _hline_alpha(big, m(13), m(247), y + m(1), (180, 150, 80, 140))

    # punched holes along the fold — dark core THEN a dimmed-gold lit lip. Skip
    # any that would collide with the coin/seat punch at HOLE_CX.
    x = m(12)
    while x <= m(248):
        if abs(x - m(HOLE_CX)) > m(9):
            pygame.draw.circle(big, PUNCH, (x, y), m(4))
            _lit_ring(big, (x, y), m(4), LIP_GOLD)
        x += m(11)

    # edge notches — larger, and set ON the card edges so they bite into the gold
    # frame; a cool lit lip contrasts the notch against the warm rim. Clearest
    # tear cue in the whole silhouette.
    for nx in (m(CARD_X), m(CARD_X + CARD_W)):
        pygame.draw.circle(big, PUNCH, (nx, y), m(7))
        _lit_ring(big, (nx, y), m(7), LIP_COOL)


def class_stripe(big, pal):
    """A thin class/section band inside the ticket top, masked to the body so it
    stays within the rounded corners."""
    layer = pygame.Surface((m(CARD_W), m(CARD_H)), pygame.SRCALPHA)
    band = vgrad_stops(m(STRIPE_W), m(STRIPE_H), 0,
                       [(0.0, pal["gem"]), (1.0, pal["glow"])], 200)
    layer.blit(band, (m((CARD_W - STRIPE_W) // 2), m(STRIPE_Y - CARD_TOP_Y)))
    bmask = pygame.Surface((m(CARD_W), m(CARD_H)), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), bmask.get_rect(), border_radius=m(CARD_RAD))
    layer.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(layer, (m(CARD_X), m(CARD_TOP_Y)))


# ── hero item window ────────────────────────────────────────────────────────
def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try: sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception: pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    # registration print-ring: the gold ticket-window ring outside the bezel.
    pygame.draw.circle(big, CARD_RING_BRIGHT, (cx, cy), m(57), width=max(1, m(2)))


def name_text(big, name):
    plain_text(big, name, font(18), (m(CX), m(Y_NAME)), NAME_COL, shadow_a=150,
               weight=m(0.9), keyline=(8, 7, 18), kw=m(0.9))


# ── Zone A — gold-foil printed face value ───────────────────────────────────
def zone_a(big, tier_word, price_str, pal):
    """Coin + price float as gold-foil ink on the indigo stock — no container.
    Reads as the ticket's printed face value."""
    coin_cx, cy = m(CX - 36), m(ZA_CY)
    coin_glyph(big, coin_cx, cy, m(13))

    nf = font(22)
    base = sc._stamp_bold(sc._glyph_base(price_str, nf, 0), m(0.9))
    bw, bh = base.get_size()
    num_center = (coin_cx + m(13) + m(8) + bw // 2, cy)
    _num_outline(big, base, PRICE_RIM_BRIGHT, num_center, m(2.6))   # gold keyline
    _num_outline(big, base, (36, 22, 4), num_center, m(1.4))        # dark inner
    fill = vgrad_stops(bw, bh, 0, TICKET_PRICE_STOPS, 255)
    gold = base.copy()
    gold.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(gold, gold.get_rect(center=num_center))

    # tiny printed ticket line under the face value — warm cream, readable weight.
    df = sc._stamp_bold(sc._glyph_base("ADMIT ONE", font(9), m(1.4)), m(0.4))
    tint = df.copy(); tint.fill((230, 215, 190, 255), special_flags=pygame.BLEND_RGBA_MULT)
    tint.set_alpha(200)
    big.blit(tint, tint.get_rect(center=(num_center[0] - m(4), m(DETAIL_CY))))


# ── counterfoil detail + buttons + Zone B ───────────────────────────────────
def buttons(big):
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX), "BUY", [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
        (m(CAN_CX), "CANCEL", [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        top_sheen(big, r, br, m(12), peak=pk)
        bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def coin_hole(big):
    """A gold-ringed seat punch riding the tear line — a ticket-office detail
    that now belongs to the perforation family instead of floating in the stub."""
    c = (m(HOLE_CX), m(PERF_Y))
    pygame.draw.circle(big, PUNCH, c, m(HOLE_R))
    _lit_ring(big, c, m(HOLE_R), LIP_GOLD)


def zone_b(big, tier_word, pal, label_col=None):
    """Rarity ribbon centred in the de-crowded counterfoil. `label_col` overprints
    the tier word (LEGENDARY's cream on vermilion) since the shared ribbon bakes
    a dark-navy label that would fail contrast on the red stub."""
    sc._ribbon(big, tier_word, m(CX), m(ZB_CY), m(146), pal)
    if label_col is not None:
        plain_text(big, tier_word, font(8.5), (m(CX), m(ZB_CY)), label_col,
                   shadow_a=0, tracking=m(1.4), weight=m(0.7))


# ── render loop ─────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price_str, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    perforation(big)
    class_stripe(big, pal)
    hero_disc(big, sid, pal)
    name_text(big, NAMES[tier_word])
    zone_a(big, tier_word, price_str, pal)
    buttons(big)
    coin_hole(big)

    # LEGENDARY reads 1ST CLASS in wax-stamp vermilion — deliberately OFF the gold
    # family so the top-tier stub feels like a premium pass, not more gold. Cream
    # label + a red deep that won't bleed amber into the gold family.
    if tier_word == "LEGENDARY":
        zb_pal = dict(pal)
        zb_pal["gem"] = (205, 55, 40); zb_pal["glow"] = (170, 40, 30)
        zb_pal["deep"] = (110, 16, 16)
        zone_b(big, "1ST CLASS", zb_pal, label_col=(250, 240, 225))
    else:
        zone_b(big, tier_word, pal)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "ticket-stub · card-frame-v1 · round_2", fill=(232, 226, 208))
for i, (tw, sid, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP); strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/card-frame-v1/ticket-stub"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_2.png"
out.save(OUT); print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
