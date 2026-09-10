"""Before / after — full store page (costume category, page 1, 8 cards).

Replicates the real store layout: 360 px wide, night-sky gradient,
2 columns × 4 rows, _GAP=8, base_x=14, _GRID_TOP=116.

BEFORE: v4 production cards (dome r=40, box=60, notched ribbon)
AFTER:  v5 locked cards    (dome r=56, box=84, item +5lx, lozenge ribbon)

Output: docs/store_card_v5_card_item/storepage_compare_r1.png
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font
from game import store_catalog

# ── store grid constants (mirrors game/store.py) ──────────────────────────────
W, H       = 360, 640
_CARD_W    = 162
_CARD_H    = 100
_GAP       = 8
_GRID_TOP  = 116
_BASE_X    = (W - (_CARD_W * 2 + _GAP)) // 2   # 14

# Night-sky gradient stops (from store.py _BG_STOPS)
_BG_STOPS  = ((8, 8, 24), (12, 12, 36), (18, 16, 48), (24, 20, 58))

# First page of the costume category
SIDS = store_catalog.ids_of_group("costume")[:8]

# ── background ────────────────────────────────────────────────────────────────
SS = sc.SS
_INSET = 6


def _make_bg():
    bg = pygame.Surface((W, H))
    n = len(_BG_STOPS)
    for y in range(H):
        f = y / (H - 1)
        seg = min(n - 2, int(f * (n - 1)))
        local = (f * (n - 1)) - seg
        pygame.draw.line(bg, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1], local),
                         (0, y), (W - 1, y))
    return bg


def _draw_header(surf):
    """Minimal COSTUMES label + divider — enough context without full HUD."""
    f = hud_font(14, True)
    lbl = f.render("COSTUMES", True, (210, 180, 100))
    surf.blit(lbl, ((W - lbl.get_width()) // 2, 88))
    pygame.draw.line(surf, (50, 46, 80), (14, 110), (W - 14, 110), 1)


# ── v4 original card renderer ─────────────────────────────────────────────────
def _ribbon_v4(surf, tier_word, cx, cy, max_w, pal):
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(12)
    w = min(max_w, tw + pad * 2)
    h = sc.m(15)
    notch = sc.m(5)
    x0, y0 = cx - w // 2, cy - h // 2
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, 0,
                          [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2),
            (w - notch, h), (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    surf.blit(sh, (x0, y0 + sc.m(2)))
    surf.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, sc.m(1.4)))
    sc.plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26),
                  shadow_a=0, tracking=sc.m(1.4), weight=sc.m(0.7))


def _draw_card_v4(surf, sid, rect):
    """Original v4 card draw — dome r=40, box=60, centred item, notched ribbon."""
    pal = sc.RARITY[sc._rarity(sid)]
    rad = sc.m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=sc.m(8), alpha=160, dy=sc.m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, sc.m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, sc.m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect,
                     width=max(1, sc.m(2)), border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, sc.m(2.0)))
    tray = rect.inflate(-sc.m(7), -sc.m(7))
    trad = rad - sc.m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(sc.m(2), sc.m(2)),
                     width=max(1, sc.m(1)), border_radius=trad + sc.m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray,
                     width=max(1, sc.m(1)), border_radius=trad)
    orig_r = sc.m(sc.R_DISC)
    cx, cy = rect.centerx, rect.y + sc.m(sc.CY_DISC)
    sc.soft_glow(surf, cx, cy, orig_r + sc.m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, orig_r, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    sc.blit_thumb(surf, sid, cx, cy, orig_r * 1.5)
    sc.cabochon_glass(surf, cx, cy, orig_r, tint=pal["gem"])
    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19),
                 sc.m(sc.GEM_R + 3), pal["gem"], pal["deep"], mystery=False)
    tier_word = sc._rarity(sid).upper()
    _ribbon_v4(surf, tier_word, cx, rect.y + sc.m(55), rect.w - sc.m(34), pal)
    sc._name_on(surf, sc._name(sid), cx, rect.y + sc.m(70), rect.w - sc.m(26))
    sc.state_chip(surf, sid, cx, rect.y + sc.m(88), False, False, sc.m(20),
                  variant=sc.PRICE_VARIANT)


def render_card_v4(sid):
    big = pygame.Surface((_CARD_W * SS, _CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       _CARD_W * SS - 2 * sc.m(_INSET),
                       _CARD_H * SS - 2 * sc.m(_INSET))
    _draw_card_v4(big, sid, rect)
    return pygame.transform.smoothscale(big, (_CARD_W, _CARD_H))


def render_card_v5(sid):
    big = pygame.Surface((_CARD_W * SS, _CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       _CARD_W * SS - 2 * sc.m(_INSET),
                       _CARD_H * SS - 2 * sc.m(_INSET))
    sc.draw_card(big, sid, rect, equipped=False, secret=False)
    return pygame.transform.smoothscale(big, (_CARD_W, _CARD_H))


# ── render one full store page ────────────────────────────────────────────────
def render_store_page(card_fn):
    surf = _make_bg()
    _draw_header(surf)
    for idx, sid in enumerate(SIDS):
        card = card_fn(sid)
        x = _BASE_X + (idx % 2) * (_CARD_W + _GAP)
        y = _GRID_TOP + (idx // 2) * (_CARD_H + _GAP)
        surf.blit(card, (x, y))
    return surf


# ── canvas: two store pages side by side, cropped to the grid area ────────────
CROP_TOP    = 80       # show a little above the COSTUMES label
CROP_BOTTOM = 548      # just below the last card row
PAGE_H      = CROP_BOTTOM - CROP_TOP   # 468

BG_CANVAS   = (4, 4, 12)
GAP_MID     = 24
MARGIN      = 28
HDR_H       = 52
LBL_H       = 30
FOOTER_H    = LBL_H + 10

canvas_w = MARGIN * 2 + W * 2 + GAP_MID
canvas_h = MARGIN + HDR_H + PAGE_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG_CANVAS)

hf   = hud_font(18, True)
htxt = hf.render("v5 store card  —  costumes  —  before / after  (8 cards, page 1)",
                  True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

page_y   = MARGIN + HDR_H
lbl_font = hud_font(13, True)
sub_font = hud_font(10, False)

PANELS = [
    (render_store_page(render_card_v4), "BEFORE",
     "dome r=40  box=60  notched ribbon"),
    (render_store_page(render_card_v5), "AFTER",
     "dome r=56  box=84  item up  lozenge"),
]

for col, (page_surf, title, subtitle) in enumerate(PANELS):
    x = MARGIN + col * (W + GAP_MID)
    # blit the cropped region of the store page
    canvas.blit(page_surf, (x, page_y),
                area=pygame.Rect(0, CROP_TOP, W, PAGE_H))

    # thin border around each panel
    border_col = (80, 76, 110) if col == 0 else (180, 150, 60)
    pygame.draw.rect(canvas, border_col,
                     (x - 1, page_y - 1, W + 2, PAGE_H + 2), 1)

    col_colour = (160, 156, 180) if col == 0 else (255, 230, 120)
    t1 = lbl_font.render(title, True, col_colour)
    t2 = sub_font.render(subtitle, True, (120, 116, 140))
    lbl_y = page_y + PAGE_H + 8
    canvas.blit(t1, (x + (W - t1.get_width()) // 2, lbl_y))
    canvas.blit(t2, (x + (W - t2.get_width()) // 2, lbl_y + t1.get_height() + 3))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_card_item", "storepage_compare_r1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
