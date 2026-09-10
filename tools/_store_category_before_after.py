"""Before/after store category page — costume, page 1.

Shows 8 cards (skin_pirate → skin_wizard) in the real store grid layout
(2 col × 4 row, 360px wide panel) with the store background gradient,
comparing the original card design against the locked new design.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font

sd.load()

# ── store grid constants (from game/store.py) ─────────────────────────────────
STORE_W, STORE_H = 360, 640
CARD_W, CARD_H = 162, 100
GAP       = 8
GRID_TOP  = 116
BASE_X    = (STORE_W - (CARD_W * 2 + GAP)) // 2   # 14

SIDS = [
    "skin_pirate", "skin_cowboy", "skin_pharaoh", "skin_crown",
    "skin_tophat", "skin_ninja",  "skin_viking",  "skin_wizard",
]

# ── originals ─────────────────────────────────────────────────────────────────
_ORIG = dict(
    _INSET=sc._INSET, _DOME_R=sc._DOME_R, _BOX_PX=sc._BOX_PX,
    CY_DISC=sc.CY_DISC, _ITEM_DY=sc._ITEM_DY,
)
_orig_ribbon = sc._ribbon_lozenge
_orig_name   = sc._name_on
_orig_bevel  = sc.bevel_rim


# ── helpers ───────────────────────────────────────────────────────────────────

def _store_bg():
    """Replicate the store's 4-stop vertical gradient."""
    stops = [(8,8,24), (12,12,36), (18,16,48), (24,20,58)]
    surf = pygame.Surface((STORE_W, STORE_H))
    seg = STORE_H // (len(stops) - 1)
    for i in range(len(stops) - 1):
        c0, c1 = stops[i], stops[i+1]
        y0, y1 = i * seg, (i+1) * seg
        for y in range(y0, y1):
            t = (y - y0) / max(1, y1 - y0)
            c = tuple(int(c0[j] + (c1[j]-c0[j])*t) for j in range(3))
            pygame.draw.line(surf, c, (0,y), (STORE_W,y))
    return surf


def _before_ribbon(surf, tier_word, cx, cy, max_w, pal):
    """Old ribbon: h=m(10), position shifted back to m(55) baseline."""
    cy = cy - (sc.m(67) - sc.m(55))   # undo current m(67), restore m(55)
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(14)
    w = min(max_w, tw + pad * 2)
    h = sc.m(10)                       # old height
    pt = h // 2
    x0, y0 = cx - w // 2, cy - h // 2
    poly = [(0,h//2),(pt,0),(w-pt,0),(w,h//2),(w-pt,h),(pt,h)]
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, 0, [(0.0,top),(0.5,pal["glow"]),(1.0,bot)], 255, gamma=1.08)
    pmask = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255,255,255,255), poly)
    body.blit(pmask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0,0,0,120), poly)
    surf.blit(sh, (x0, y0+sc.m(2)))
    surf.blit(body, (x0, y0))
    abspoly = [(x0+px,y0+py) for px,py in poly]
    pygame.draw.polygon(surf, (4,5,16), abspoly, width=max(1,sc.m(1.4)))
    sc.plain_text(surf, tier_word, f, (cx,cy), (14,12,26),
                  shadow_a=0, tracking=sc.m(1.4), weight=sc.m(0.7))


def _before_name(surf, name, cx, cy, max_w):
    """Old name: position shifted back to m(72) baseline."""
    _orig_name(surf, name, cx, cy - (sc.m(78) - sc.m(72)), max_w)


def _before_bevel(surf, rect, radius, deep, bright, w):
    if rect.w > 200:
        w = max(1, sc.m(2.0))
    _orig_bevel(surf, rect, radius, deep, bright, w)


def render_grid(before=False):
    """Render the 8-card costume grid onto a store background surface."""
    if before:
        sc._INSET   = 6;  sc._DOME_R = 56; sc._BOX_PX = 84
        sc.CY_DISC  = 30; sc._ITEM_DY = 6
        sc._ribbon_lozenge = _before_ribbon
        sc._name_on        = _before_name
        sc.bevel_rim       = _before_bevel
    sc._card_cache.clear()

    panel = _store_bg()
    for idx, sid in enumerate(SIDS):
        x = BASE_X + (idx % 2) * (CARD_W + GAP)
        y = GRID_TOP + (idx // 2) * (CARD_H + GAP)
        card = sc.render_card(sid, equipped=False, owned=True)
        panel.blit(card, (x, y))

    if before:
        sc._INSET          = _ORIG["_INSET"]
        sc._DOME_R         = _ORIG["_DOME_R"]
        sc._BOX_PX         = _ORIG["_BOX_PX"]
        sc.CY_DISC         = _ORIG["CY_DISC"]
        sc._ITEM_DY        = _ORIG["_ITEM_DY"]
        sc._ribbon_lozenge = _orig_ribbon
        sc._name_on        = _orig_name
        sc.bevel_rim       = _orig_bevel
        sc._card_cache.clear()
    return panel


before_panel = render_grid(before=True)
after_panel  = render_grid(before=False)

# ── comparison sheet ──────────────────────────────────────────────────────────
PAD    = 20
GAP_SH = 24
HDR_H  = 52
LBL_H  = 28

sheet_w = PAD + STORE_W + GAP_SH + STORE_W + PAD
sheet_h = PAD + HDR_H + LBL_H + STORE_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

fh = hud_font(17, True)
fl = hud_font(12, True)

title = fh.render(
    "store category — costume page 1 — before vs after",
    True, (240, 224, 180))
sheet.blit(title, ((sheet_w - title.get_width()) // 2,
                   PAD + (HDR_H - title.get_height()) // 2))

y_panels = PAD + HDR_H + LBL_H
sheet.blit(before_panel, (PAD, y_panels))
sheet.blit(after_panel,  (PAD + STORE_W + GAP_SH, y_panels))

for i, (lbl, col) in enumerate([
        ("BEFORE  (original)", (170, 166, 190)),
        ("AFTER  (dome 62 · inset 4 · repositioned)", (255, 226, 120))]):
    x = PAD + i * (STORE_W + GAP_SH)
    t = fl.render(lbl, True, col)
    sheet.blit(t, (x + (STORE_W - t.get_width()) // 2,
                   PAD + HDR_H + (LBL_H - t.get_height()) // 2))

out = "docs/store_card_size/category_before_after.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
