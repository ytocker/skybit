"""v5_card_item — 5 distinct concepts for a bigger item in the store card.

Thesis per variant (all keep the locked card shell: indigo body, gold bevel,
dark tray):

  A  expanded-dome   — glass dome scaled 20→26 r, item 30→46 logical px box
  B  open-spotlight  — dome glass removed; item 45 px in a pure radial glow
  C  portrait-column — left 42 % of card is a tall item panel, info right
  D  podium-stand    — item 52 px rises above a small hex base (no dome)
  E  wide-stage      — item 38 px in a full-width rounded-rect tray

Output: docs/store_card_v5_card_item/r1.png  — 6-panel comparison
(original + A–E) each at SS=2 card size (324×200 device px).
"""

import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from game import store_catalog
from game.hud import _font as hud_font
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
    _ribbon, _name_on, price_chip,
    gloss_sweep, bevel_rim,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Items used across all panels
SID_EPIC = "skin_mummy"   # EPIC (1100) — our hero comparison item


# =============================================================================
# Shared shell  (kept identical across every variant)
# =============================================================================

def _shell(big, rect):
    """Indigo card body, gold bevel, dark tray — the locked CONSTELLATION shell."""
    rad = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    # Inner tray
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)


def _gem(big, rect, pal):
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"], mystery=False)


def _info(big, sid, rect, pal, cy_ribbon, cy_name, cy_chip):
    """Ribbon + name + price chip at caller-specified Y positions."""
    cx = rect.centerx
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)
    tier = _rarity(sid).upper()
    _ribbon(big, tier, cx, rect.y + m(cy_ribbon), rect.w - m(34), pal)
    _name_on(big, name, cx, rect.y + m(cy_name), rect.w - m(26))
    price_chip(big, cx, rect.y + m(cy_chip), f"{price:,}", m(20),
               affordable=True)


# =============================================================================
# ORIGINAL (reference)
# =============================================================================

def draw_original(big, sid, rect):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    _shell(big, rect)
    cx, cy = rect.centerx, rect.y + m(30)
    soft_glow(big, cx, cy, m(23), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(20), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, m(20) * 1.5)      # box = 60 device px
    cabochon_glass(big, cx, cy, m(20), tint=pal["gem"])
    _gem(big, rect, pal)
    _info(big, sid, rect, pal, 55, 70, 88)


# =============================================================================
# A — Expanded Dome  (dome radius 20→26, item box 60→88 device px)
# =============================================================================

def draw_expanded_dome(big, sid, rect):
    """Same glass-dome anatomy; dome radius +30 %, item 47 % bigger box.
    Info band shifts down to keep clear of the larger disc."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    _shell(big, rect)
    R = 26
    cx, cy = rect.centerx, rect.y + m(33)
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 32, layers=9)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(big, sid, cx, cy, m(R) * 1.70)      # box ≈ 88 device px
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    _gem(big, rect, pal)
    _info(big, sid, rect, pal, 59, 73, 89)


# =============================================================================
# B — Open Spotlight  (no dome glass at all; item in radial glow)
# =============================================================================

def draw_open_spotlight(big, sid, rect):
    """Glass dome removed. Item stands in a pure radial glow spotlight —
    multi-layer additive halo, no physical ring, no glass overlay.
    Item box 90 device px (50 % bigger)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    _shell(big, rect)
    cx, cy = rect.centerx, rect.y + m(27)
    # Multi-ring glow (wider, no hard edge)
    for r, a in ((m(46), 14), (m(36), 22), (m(26), 30), (m(18), 38)):
        g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*pal["glow"], a), (r, r), r)
        big.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_ADD)
    # Item — no dome, no glass; just the lit sprite in open card space
    blit_thumb(big, sid, cx, cy, 90)               # box = 90 device px
    _gem(big, rect, pal)
    _info(big, sid, rect, pal, 57, 71, 87)


# =============================================================================
# C — Portrait Column  (left 42 % = tall item panel; right 58 % = info)
# =============================================================================

def draw_portrait_column(big, sid, rect):
    """Card anatomy split left/right. Left column is a tall rounded-rect
    item stage; item box = 96 device px. Info (gem/ribbon/name/chip) stacked
    in right column. Vertical separator rendered as a dim keyline."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    _shell(big, rect)
    rad = m(CARD_RAD)

    col_w = int(rect.w * 0.42)        # device px width of item column
    sep_x = rect.x + col_w

    # ── Left item column — dark recessed panel ──
    panel = pygame.Rect(rect.x + m(3), rect.y + m(3),
                        col_w - m(3), rect.h - m(6))
    panel_rad = rad - m(3)
    col_surf = vgrad(panel.w, panel.h, panel_rad,
                     (8, 8, 22), (16, 14, 32), 200)
    big.blit(col_surf, panel.topleft)
    pygame.draw.rect(big, (30, 28, 48, 140), panel,
                     width=max(1, m(1)), border_radius=panel_rad)

    # Item centered in column, large
    cx_item = panel.centerx
    cy_item = panel.centery + m(2)
    soft_glow(big, cx_item, cy_item, m(30), pal["glow"], 28, layers=8)
    blit_thumb(big, sid, cx_item, cy_item, 96)     # box = 96 device px

    # Tier aura ring (instead of dome glass) — subtle, not heavy
    pygame.draw.circle(big, (*pal["gem"], 35), (cx_item, cy_item),
                       m(28), max(1, m(1)))

    # Vertical separator
    sv = pygame.Surface((max(1, m(1)), rect.h - m(8)), pygame.SRCALPHA)
    sv.fill((*CARD_RING_BRIGHT, 45))
    big.blit(sv, (sep_x, rect.y + m(4)))

    # ── Right column — gem / ribbon / name / chip ──
    info_cx = sep_x + (rect.right - sep_x) // 2
    info_w = rect.right - sep_x - m(6)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)
    tier = _rarity(sid).upper()

    facet_gem(big, rect.right - m(16), rect.y + m(16), m(GEM_R + 3),
              pal["gem"], pal["deep"])
    _ribbon(big, tier, info_cx, rect.y + m(42), info_w, pal)
    _name_on(big, name, info_cx, rect.y + m(58), info_w)
    price_chip(big, info_cx, rect.y + m(75), f"{price:,}", m(20),
               affordable=True)


# =============================================================================
# D — Podium Stand  (item 52 px; small hex plinth at its base; no dome)
# =============================================================================

def draw_podium_stand(big, sid, rect):
    """Dome replaced by a small circular plinth at item foot level.
    Item floats 52 px box above the plinth, not enclosed in glass.
    Reads as a museum-display pedestal."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    _shell(big, rect)

    cx = rect.centerx
    # Item center — high enough to leave room for info below
    cy_item = rect.y + m(30)
    # Plinth center — just below the item
    cy_plinth = rect.y + m(52)
    r_plinth = m(13)

    # Glow behind item
    soft_glow(big, cx, cy_item, m(32), pal["glow"], 28, layers=9)

    # Item — large, free-floating, no glass
    blit_thumb(big, sid, cx, cy_item, 104)          # box = 104 device px

    # Plinth disc — a small cabochon acting as a mount base
    cabochon(big, cx, cy_plinth, r_plinth, CABO_LO, CABO_HI,
             ring=pal["gem"], ring_a=70)
    cabochon_glass(big, cx, cy_plinth, r_plinth, tint=pal["gem"])

    # Small contact shadow between item and plinth
    shad = pygame.Surface((m(22), m(4)), pygame.SRCALPHA)
    pygame.draw.ellipse(shad, (0, 0, 0, 60), shad.get_rect())
    big.blit(shad, (cx - m(11), cy_plinth - m(2)))

    _gem(big, rect, pal)
    _info(big, sid, rect, pal, 61, 74, 89)


# =============================================================================
# E — Wide Stage  (item 76 px in full-width rounded-rect tray at card top)
# =============================================================================

def draw_wide_stage(big, sid, rect):
    """Item lives in a full-width rounded-rect stage spanning 87 % of card width.
    Stage height ≈ 40 logical px. Item box = 76 device px (27 % bigger).
    Compact info strip below.  Shape language: horizontal capsule vs original circle."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    _shell(big, rect)

    stage_h = m(40)
    stage_pad = m(6)
    stage = pygame.Rect(rect.x + stage_pad, rect.y + m(5),
                        rect.w - stage_pad * 2, stage_h)
    stage_rad = stage_h // 2

    # Stage body — dark well with tier aura gradient
    well = vgrad(stage.w, stage.h, stage_rad,
                 lerp_color(pal["glow"], (6, 6, 18), 0.82),
                 lerp_color(pal["deep"], (4, 4, 14), 0.70), 210)
    big.blit(well, stage.topleft)

    # Stage glow halo (additive, behind item)
    cx_s, cy_s = stage.centerx, stage.centery
    for r, a in ((m(28), 16), (m(20), 26), (m(14), 34)):
        g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*pal["glow"], a), (r, r), r)
        big.blit(g, (cx_s - r, cy_s - r), special_flags=pygame.BLEND_ADD)

    # Stage rim — gold keyline + inner gloss sweep
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 80), stage,
                     width=max(1, m(1)), border_radius=stage_rad)
    gloss_sweep(big, stage, stage_rad, peak=38)

    # Item centered in stage, larger than original dome would allow
    blit_thumb(big, sid, cx_s, cy_s, 76)           # box = 76 device px

    _gem(big, rect, pal)
    _info(big, sid, rect, pal, 58, 72, 88)


# =============================================================================
# Panel renderer + showcase assembler
# =============================================================================

VARIANTS = [
    ("ORIGINAL",        draw_original),
    ("A  expanded-dome", draw_expanded_dome),
    ("B  open-spotlight", draw_open_spotlight),
    ("C  portrait-column", draw_portrait_column),
    ("D  podium-stand",   draw_podium_stand),
    ("E  wide-stage",     draw_wide_stage),
]

PANEL_W = CARD_W * SS   # 324
PANEL_H = CARD_H * SS   # 200
BG       = (8, 8, 20)
GAP      = 10
MARGIN   = 20
HDR_H    = 44
ID_H     = 26
LBL_H    = 20
FOOTER_H = ID_H + LBL_H + 4

n         = len(VARIANTS)
canvas_w  = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
canvas_h  = MARGIN + HDR_H + PANEL_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

# Header
hf   = hud_font(18, True)
htxt = hf.render("v5 card item  —  bigger item: 5 concepts vs original", True,
                  (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

id_font  = hud_font(14, True)
lbl_font = hud_font(11, False)
panel_y  = MARGIN + HDR_H

for col, (label, draw_fn) in enumerate(VARIANTS):
    x = MARGIN + col * (PANEL_W + GAP)

    # Render the panel
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       PANEL_W - 2 * m(_INSET), PANEL_H - 2 * m(_INSET))
    draw_fn(big, SID_EPIC, rect)
    # Thin border on each panel
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    canvas.blit(big, (x, panel_y))

    # Gold index #
    num = "ORIGINAL" if col == 0 else f"#{col}"
    id_surf = id_font.render(num, True, (255, 230, 120) if col else (200, 200, 200))
    canvas.blit(id_surf,
                (x + (PANEL_W - id_surf.get_width()) // 2,
                 panel_y + PANEL_H + 4))

    # Concept label
    slug = label.split("  ")[-1] if "  " in label else label
    lbl_surf = lbl_font.render(slug, True, (178, 174, 198))
    if lbl_surf.get_width() > PANEL_W - 4:
        lbl_surf = hud_font(9, False).render(slug, True, (178, 174, 198))
    canvas.blit(lbl_surf,
                (x + (PANEL_W - lbl_surf.get_width()) // 2,
                 panel_y + PANEL_H + 4 + ID_H + 2))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_card_item", "r1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
