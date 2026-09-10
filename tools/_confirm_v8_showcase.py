#!/usr/bin/env python3
"""
confirm_purchase_v8  ·  showcase assembly

6 panels: BEFORE (v5_integration current design) + 5 round_2 concepts.
Each panel: EPIC tier popup cropped from each 3-tier strip → scaled to 200×355.
Canvas: (8,8,20) BG · 200×355 panels · 12px gaps · 20px margins · 50px header · 28px footer.
"""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, m, SS, font,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image

# ── mandatory gloss_sweep patch ───────────────────────────────────────────────
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)

sc.gloss_sweep = _gloss_sweep_fixed

# ── palette used for BEFORE render (EPIC tier) ────────────────────────────────
EPIC_PAL = {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}
EPIC_PRICE = "1,400"
EPIC_SID   = "skin_prism"
EPIC_NAME  = "PRISM"
EPIC_WORD  = "EPIC"

# ── shared popup geometry ─────────────────────────────────────────────────────
POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
GEM_L_X, GEM_R_X, GEM_CY, GEM_R = 43, 217, 152, 14


# ── shared chrome (same as all r2 scripts) ────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))


def corner_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def name_text(big, name):
    nfs  = 45
    nfnt = font(nfs)
    mw   = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1
        nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def rarity_banner(big, tier_word, pal):
    cx, cy_log, w_log, h_log = CX, 247, 156, 23
    f   = font(h_log * 0.58)
    tw  = sc._glyph_base(tier_word, f, m(1.4)).get_width()
    w   = min(m(w_log), tw + m(16) * 2)
    h   = m(h_log)
    pt  = h // 2
    x0, y0 = m(cx) - w // 2, m(cy_log) - h // 2
    poly = [(0,h//2),(pt,0),(w-pt,0),(w,h//2),(w-pt,h),(pt,h)]
    top  = lerp_color(pal["gem"], WHITE, 0.1)
    bot  = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0,top),(0.5,pal["glow"]),(1.0,bot)], 255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255,255,255,255), poly)
    body.blit(pmask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0,0,0,120), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0+px, y0+py) for px, py in poly]
    pygame.draw.polygon(big, (4,5,16), abspoly, width=max(1, m(1.4)))
    plain_text(big, tier_word, f, (m(cx), m(cy_log)), (14,12,26),
               shadow_a=0, tracking=m(1.4), weight=m(0.7))


def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])


# ── BEFORE: faithful reproduction of _draw_confirm (affordable=True) ─────────
def before_shelf(big, price_str, pal):
    """Mirrors _draw_confirm shelf, chip, buttons, bottom gems exactly (affordable=True)."""
    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
    SHELF_RAD = m(CARD_RAD)
    BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
    BUY_CX = CX - (BTN_W + BTN_GAP) // 2   # = 75
    CAN_CX = CX + (BTN_W + BTN_GAP) // 2   # = 185
    CHIP_CY, CHIP_W, CHIP_H, CHIP_RAD = 402, 88, 26, 8
    BOT_GEM_CY = 402

    # shelf body (bottom rounded corners only)
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf = vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                        [(0.0,(34,36,72)),(0.5,(22,24,54)),(1.0,(12,14,36))], 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255,255,255,255), smask.get_rect(),
                     border_bottom_left_radius=SHELF_RAD,
                     border_bottom_right_radius=SHELF_RAD)
    shelf.blit(smask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115,106,140), (0,0), (shelf_rect.w-1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for _yy in range(m(6)):
        _a = int(120 * (1 - _yy / m(6)))
        pygame.draw.line(seat, (0,0,0,_a), (0,_yy), (shelf_rect.w-1, _yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # side-wall feathering between card edge and shelf edge
    wall_draw_h = m(CARD_TOP_Y + CARD_H - CARD_RAD - SHELF_Y)  # m(68)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        for col_fn, bx in [
            (lambda xx: (130,120,165, int(50*xx/max(1,wall_w-1))), m(CARD_X)),
            (lambda xx: (0,0,0, int(50*(1-xx/max(1,wall_w-1)))), m(SHELF_X+SHELF_W)),
        ]:
            _wall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
            for _xx in range(wall_w):
                pygame.draw.line(_wall, col_fn(_xx), (_xx,0), (_xx, wall_draw_h-1))
            big.blit(_wall, (bx, m(SHELF_Y)))

    # price chip (88×26, font 18, coin_r=m(11)) — mirrors _chip() in store.py
    cx_ = m(CX)
    cy_ = m(CHIP_CY)
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx_, cy_)
    crad = m(CHIP_RAD)
    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=80, dy=m(2))
    big.blit(vgrad_stops(chip.w, chip.h, crad,
                         [(0.0,(40,42,74)),(1.0,(26,28,54))], 255), chip.topleft)
    sc.top_sheen(big, chip, crad, m(9), peak=30)
    sc.bevel_rim(big, chip, crad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 200),
                 w=max(1, m(1.4)))
    num_font = font(18)
    coin_r   = m(11)
    gap      = m(4)
    num_w    = num_font.size(price_str)[0]
    total    = coin_r * 2 + gap + num_w
    left     = cx_ - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_r * 2 + gap + num_w // 2
    sc.coin_glyph(big, coin_cx, cy_, coin_r)
    plain_text(big, price_str, num_font, (num_cx, cy_ + m(1)), (236,240,232),
               shadow_a=0, weight=m(0.7))

    # BUY button (99×31, blue-purple) — mirrors _btn(rect, "BUY") in store.py
    brad = m(BTN_RAD)
    buy_r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy_r.center = (m(BUY_CX), m(BTN_CY))
    sc.drop_shadow(big, buy_r, brad, blur=m(3), alpha=100, dy=m(2))
    big.blit(vgrad_stops(buy_r.w, buy_r.h, brad,
                         [(0.0,(38,40,84)),(1.0,(22,24,56))], 255), buy_r.topleft)
    sc.top_sheen(big, buy_r, brad, m(12), peak=22)
    sc.bevel_rim(big, buy_r, brad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(2.0)))
    plain_text(big, "BUY", font(14), buy_r.center, (200,205,240),
               shadow_a=110, weight=m(0.8), keyline=(8,6,20), kw=m(0.9))

    # CANCEL button (99×31, dark blue) — mirrors _btn(rect, "CANCEL", is_cancel=True)
    can_r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can_r.center = (m(CAN_CX), m(BTN_CY))
    sc.drop_shadow(big, can_r, brad, blur=m(3), alpha=100, dy=m(2))
    big.blit(vgrad_stops(can_r.w, can_r.h, brad,
                         [(0.0,(26,28,64)),(1.0,(14,16,44))], 255), can_r.topleft)
    sc.top_sheen(big, can_r, brad, m(12), peak=14)
    sc.bevel_rim(big, can_r, brad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(2.2)))
    plain_text(big, "CANCEL", font(13), can_r.center, (150,155,200),
               shadow_a=110, weight=m(0.8), keyline=(8,6,20), kw=m(0.9))

    # bottom gems flanking chip
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        sc._alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        sc.facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def render_before():
    """Call the real _draw_confirm — pixel-perfect, no manual approximation."""
    from game.store import StoreScene as Store
    import game.store_catalog as _cat
    import game.store_data as _dat

    SID = "skin_prism"

    orig_balance = _dat.balance
    _dat.balance = lambda: 99999
    try:
        class _Stub:
            _confirm = SID
            _confirm_panel = None
            confirm_yes_rect = None
            confirm_no_rect = None
            @staticmethod
            def _disp_name(sid):
                try:
                    return _cat.name(sid)
                except Exception:
                    return sid.replace("skin_", "").upper()

        canvas = pygame.Surface((360, 640))
        canvas.fill((8, 8, 20))
        Store._draw_confirm(_Stub(), canvas)
        # popup sits at px=(360-260)//2=50, py=40
        return canvas.subsurface(pygame.Rect(50, 40, 260, 442)).copy()
    finally:
        _dat.balance = orig_balance


# ── showcase assembly ─────────────────────────────────────────────────────────
PANEL_W, PANEL_H = 200, 355
GAP       = 12
MARGIN    = 20
HEADER_H  = 50
FOOTER_H  = 28

SLUGS = [
    "slot-marquee",
    "coin-rail-twin",
    "enamel-split-bar",
    "luggage-tag",
    "treasure-drawer",
]

# crop coords for EPIC tier popup from 2× 3-tier strip (EPIC is i=1)
# strip: MARGIN=20, HEAD=58, GAP=12, POP_W=260 in logical coords
# 2× strip: EPIC popup x=2*(20+1*(260+12))=584, y=2*58=116, w=520, h=884
_M, _H, _G, _PW, _PH = 20, 58, 12, 260, 442
EPIC_X2 = 2 * (_M + 1 * (_PW + _G))   # = 584
EPIC_Y2 = 2 * _H                       # = 116
EPIC_W2 = 2 * _PW                      # = 520
EPIC_H2 = 2 * _PH                      # = 884

CANVAS_W = MARGIN * 2 + PANEL_W * 6 + GAP * 5
CANVAS_H = HEADER_H + PANEL_H + FOOTER_H

# build BEFORE panel from pygame render
before_pg = render_before()
before_raw = pygame.image.tostring(before_pg, "RGB")
before_pil = Image.frombytes("RGB", (POP_W, POP_H), before_raw)
before_panel = before_pil.resize((PANEL_W, PANEL_H), Image.LANCZOS)

panels = [before_panel]
labels = ["BEFORE"]

for slug in SLUGS:
    strip_path = f"/home/user/skybit/docs/confirm_purchase_v8/{slug}/round_2.png"
    strip = Image.open(strip_path)
    epic_crop = strip.crop((EPIC_X2, EPIC_Y2, EPIC_X2 + EPIC_W2, EPIC_Y2 + EPIC_H2))
    panel = epic_crop.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    panels.append(panel)
    labels.append(slug)

# assemble canvas
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))

# draw panels and labels (using PIL for text)
from PIL import ImageDraw, ImageFont as PILFont

draw = ImageDraw.Draw(canvas)

# header text
draw.text((MARGIN, 14), "confirm_purchase_v8  ·  showcase  ·  BEFORE vs. 5 round-2 concepts",
          fill=(232, 226, 208))
draw.text((MARGIN, 32), "EPIC tier  ·  branch: v5_integration",
          fill=(140, 148, 168))

for i, (panel, slug) in enumerate(zip(panels, labels)):
    px = MARGIN + i * (PANEL_W + GAP)
    py = HEADER_H
    canvas.paste(panel, (px, py))

    # divider line between BEFORE and first concept
    if i == 1:
        div_x = px - GAP // 2
        draw.line([(div_x, py), (div_x, py + PANEL_H)], fill=(80, 76, 100), width=1)

    # slug label below panel
    label_y = HEADER_H + PANEL_H + 6
    draw.text((px + PANEL_W // 2, label_y), slug,
              fill=(180, 176, 210), anchor="mt")

OUT = "/home/user/skybit/docs/confirm_purchase_v8/showcase_v1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"saved {canvas.size[0]}×{canvas.size[1]}  →  {OUT}")
