"""v5_card_item_ribbon r1 — 5 shorter rarity ribbon options on the CONSTELLATION card.

Design #2 locked: box_px=84 (item + dome both at +40 %).

Panels:
  CURRENT  production notched-hex ribbon  h=m(15) = 30 dev
  A        pill / capsule                 h=m(10) = 20 dev  — rounded stadium
  B        lozenge / pointed ends         h=m(10) = 20 dev  — outward heraldic points
  C        flat bar                       h=m( 8) = 16 dev  — sharp-cornered strip
  D        italic / parallelogram         h=m(10) = 20 dev  — sheared lean-right
  E        arch / dome-top                h=m(11) = 22 dev  — rounded top, flat bottom

Output: docs/store_card_v5_card_item/ribbon_r1.png
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

BOX_PX = 84     # design #2 locked
SID    = "skin_mummy"

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
SS = sc.SS
_INSET = 6
PANEL_W = CARD_W * SS   # 324
PANEL_H = CARD_H * SS   # 200


# ── 5 distinct ribbon builders ─────────────────────────────────────────────────

def _ribbon_pill(surf, tier_word, cx, cy, max_w, pal):
    """Rounded capsule — stadium silhouette, no notch, fully soft ends."""
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(10)
    w = min(max_w, tw + pad * 2)
    h = sc.m(10)
    x0, y0 = cx - w // 2, cy - h // 2
    rad = h // 2
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, rad,
                          [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.08)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), (0, 0, w, h), border_radius=rad)
    surf.blit(sh, (x0, y0 + sc.m(2)))
    surf.blit(body, (x0, y0))
    pygame.draw.rect(surf, (4, 5, 16), (x0, y0, w, h),
                     border_radius=rad, width=max(1, sc.m(1.4)))
    sc.plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26),
                  shadow_a=0, tracking=sc.m(1.4), weight=sc.m(0.7))


def _ribbon_lozenge(surf, tier_word, cx, cy, max_w, pal):
    """Lozenge — outward pointed left/right ends; heraldic diamond silhouette."""
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(14)
    w = min(max_w, tw + pad * 2)
    h = sc.m(10)
    pt = h // 2          # lateral point depth
    x0, y0 = cx - w // 2, cy - h // 2
    poly = [(0, h // 2), (pt, 0), (w - pt, 0),
            (w, h // 2), (w - pt, h), (pt, h)]
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, 0,
                          [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.08)
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


def _ribbon_flat(surf, tier_word, cx, cy, max_w, pal):
    """Flat bar — thin sharp-cornered rectangle; minimal industrial strip."""
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(8)
    w = min(max_w, tw + pad * 2)
    h = sc.m(8)
    x0, y0 = cx - w // 2, cy - h // 2
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, 0,
                          [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.08)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    sh.fill((0, 0, 0, 80))
    surf.blit(sh, (x0, y0 + sc.m(1)))
    surf.blit(body, (x0, y0))
    pygame.draw.rect(surf, (4, 5, 16), (x0, y0, w, h), width=max(1, sc.m(1.2)))
    sc.plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26),
                  shadow_a=0, tracking=sc.m(1.4), weight=sc.m(0.7))


def _ribbon_italic(surf, tier_word, cx, cy, max_w, pal):
    """Parallelogram — sheared-right; directional italic silhouette."""
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(10)
    w = min(max_w, tw + pad * 2)
    h = sc.m(10)
    lean = h // 2        # top-edge offset relative to bottom edge
    sw = w + lean        # wider surface to hold the lean
    x0 = cx - sw // 2
    y0 = cy - h // 2
    poly = [(0, h), (w, h), (w + lean, 0), (lean, 0)]
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(sw, h, 0,
                          [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.08)
    pmask = pygame.Surface((sw, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((sw, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    surf.blit(sh, (x0, y0 + sc.m(2)))
    surf.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, sc.m(1.4)))
    sc.plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26),
                  shadow_a=0, tracking=sc.m(1.4), weight=sc.m(0.7))


def _ribbon_arch(surf, tier_word, cx, cy, max_w, pal):
    """Arch — top corners rounded, bottom corners sharp; archway / tombstone."""
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(10)
    w = min(max_w, tw + pad * 2)
    h = sc.m(11)
    x0, y0 = cx - w // 2, cy - h // 2
    rad = h // 2
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, 0,
                          [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.08)
    arch_mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(arch_mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_top_left_radius=rad, border_top_right_radius=rad,
                     border_bottom_left_radius=0, border_bottom_right_radius=0)
    body.blit(arch_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), (0, 0, w, h),
                     border_top_left_radius=rad, border_top_right_radius=rad,
                     border_bottom_left_radius=0, border_bottom_right_radius=0)
    surf.blit(sh, (x0, y0 + sc.m(2)))
    surf.blit(body, (x0, y0))
    pygame.draw.rect(surf, (4, 5, 16), (x0, y0, w, h),
                     border_top_left_radius=rad, border_top_right_radius=rad,
                     border_bottom_left_radius=0, border_bottom_right_radius=0,
                     width=max(1, sc.m(1.4)))
    sc.plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26),
                  shadow_a=0, tracking=sc.m(1.4), weight=sc.m(0.7))


# ── card draw with swappable ribbon ───────────────────────────────────────────

def draw_sized_card(surf, sid, rect, box_px, ribbon_fn=None):
    """CONSTELLATION card with scaled dome/item.  Pass ribbon_fn to override
    the production _ribbon; None uses the production ribbon unchanged."""
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

    dome_r = int(box_px / 1.5)
    cx = rect.centerx
    cy = max(rect.y + dome_r + sc.m(2), rect.y + sc.m(sc.CY_DISC))

    sc.soft_glow(surf, cx, cy, dome_r + sc.m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, dome_r, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    sc.blit_thumb(surf, sid, cx, cy, box_px)
    sc.cabochon_glass(surf, cx, cy, dome_r, tint=pal["gem"])

    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19),
                 sc.m(sc.GEM_R + 3), pal["gem"], pal["deep"], mystery=False)

    name = sc._name(sid)
    tier_word = sc._rarity(sid).upper()
    draw_ribbon = ribbon_fn if ribbon_fn is not None else sc._ribbon
    draw_ribbon(surf, tier_word, cx, rect.y + sc.m(55), rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))
    sc.state_chip(surf, sid, cx, rect.y + sc.m(88), False, False, sc.m(20),
                  variant=sc.PRICE_VARIANT)


def render_panel(ribbon_fn):
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET),
                       PANEL_H - 2 * sc.m(_INSET))
    draw_sized_card(big, SID, rect, BOX_PX, ribbon_fn=ribbon_fn)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


# ── canvas ────────────────────────────────────────────────────────────────────
PANELS = [
    (None,           "CURRENT",  "notched-hex  h=30"),
    (_ribbon_pill,   "A — pill",  "capsule      h=20"),
    (_ribbon_lozenge,"B — lozenge","pointed ends h=20"),
    (_ribbon_flat,   "C — flat",  "bar strip    h=16"),
    (_ribbon_italic, "D — italic","parallelogram h=20"),
    (_ribbon_arch,   "E — arch",  "dome-top     h=22"),
]

BG       = (8, 8, 20)
GAP      = 10
MARGIN   = 20
HDR_H    = 44
LBL_H    = 36
FOOTER_H = LBL_H + 8

n        = len(PANELS)
canvas_w = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
canvas_h = MARGIN + HDR_H + PANEL_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf   = hud_font(18, True)
htxt = hf.render(
    f"v5 card ribbon r1  —  {SID}  (EPIC)  —  box=84  —  ribbon options",
    True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_font  = hud_font(12, False)
lbl_font2 = hud_font(10, False)
panel_y   = MARGIN + HDR_H

for col, (ribbon_fn, title, subtitle) in enumerate(PANELS):
    x = MARGIN + col * (PANEL_W + GAP)
    panel = render_panel(ribbon_fn)
    canvas.blit(panel, (x, panel_y))

    col_colour = (255, 230, 120) if col == 0 else (178, 174, 198)
    t1 = lbl_font.render(title, True, col_colour)
    t2 = lbl_font2.render(subtitle, True, (130, 126, 150))
    lbl_y = panel_y + PANEL_H + 6
    canvas.blit(t1, (x + (PANEL_W - t1.get_width()) // 2, lbl_y))
    canvas.blit(t2, (x + (PANEL_W - t2.get_width()) // 2, lbl_y + t1.get_height() + 2))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_card_item", "ribbon_r1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
