"""Round-1 exploration sheet for the POWER-UPS card-frame polish.

Five distinct, on-palette ways to make the explainer card frame read more
"finished" without clutter or hurting the icon/name/blurb legibility. Each
candidate is drawn as a REAL card at its true 162x124 size on the actual
dark gradient + star-field background, with the real TRIPLE icon, gold
"TRIPLE" name, and cream "Coins are worth 3x" blurb inside — then shown in
the sheet at ~2.7x zoom so the frame detail survives, plus a 1x inset of one
candidate to judge it at native size.

This file only RENDERS candidates; it does not touch game/powerup_help.py.
Run from repo root:  python tools/gen_powerups_frame_polish.py
"""
import os
import math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game.config import W, H
from game.draw import lerp_color, UI_CREAM, NEAR_BLACK
from game.hud import (
    _font, _draw_overlay_stars,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _GOLD_MUTED,
    _PANEL_DARK, _PANEL_LIGHTER, _ORANGE_BORDER,
)
import game.powerup_help as ph
from game.powerup_help import (
    _gradient_bg, _seeded_stars, _powerup_icon, _wrap, _PANEL_OS,
)

CARD_W, CARD_H, RADIUS, ALPHA = 162, 124, 14, 215


# ── candidate frame treatments ──────────────────────────────────────────────
# Every treatment composites at _PANEL_OS x and smoothscales down, matching
# the shipped _dark_panel so the rounded corners + rim stay crisp at 360 px.
# All geometry below is expressed in oversampled (os_) units.

def _base_body(ow, oh, orad):
    """Solid navy body — the shared starting point for the flat treatments."""
    pnl = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*_PANEL_DARK, ALPHA), (0, 0, ow, oh),
                     border_radius=orad)
    return pnl


def _grad_body(ow, oh, orad, top, bot):
    """Vertical-gradient body clipped to the rounded rect. Lighter navy at
    top fading to deeper navy gives the card soft volume without a shadow."""
    pnl = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(top, bot, t)
        pygame.draw.line(pnl, (*c, ALPHA), (0, yy), (ow - 1, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return pnl


def cand_gradient_sheen(surf, rect):
    """A — Soft Volume. Vertical body gradient (light navy -> deep navy) plus
    a faint top inner sheen, finished with the existing single 2 px rim. The
    most restrained: just gives the flat card gentle dimensionality."""
    os_ = _PANEL_OS
    ow, oh, orad = rect.width * os_, rect.height * os_, RADIUS * os_
    pnl = _grad_body(ow, oh, orad, _PANEL_LIGHTER, _PANEL_DARK)
    # Top inner sheen: a wide, very low-alpha pale band that fades downward,
    # reading as light catching the upper face of the card.
    sheen = pygame.Surface((ow, oh), pygame.SRCALPHA)
    band = int(oh * 0.42)
    for yy in range(band):
        a = int(26 * (1 - yy / band))
        pygame.draw.line(sheen, (*_GOLD_PALE, a),
                         (orad, yy), (ow - orad, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pnl.blit(sheen, (0, 0))
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 150), (0, 0, ow, oh),
                     width=2 * os_, border_radius=orad)
    surf.blit(pygame.transform.smoothscale(pnl, rect.size), rect.topleft)


def cand_engraved_bezel(surf, rect):
    """B — Engraved Bezel. The bright outer rim plus a second, thinner deep-gold
    inset rule a few px in, reading as a chiselled double-line frame. Body kept
    flat navy so the bezel does all the talking."""
    os_ = _PANEL_OS
    ow, oh, orad = rect.width * os_, rect.height * os_, RADIUS * os_
    pnl = _base_body(ow, oh, orad)
    # Outer bright rim.
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 150), (0, 0, ow, oh),
                     width=2 * os_, border_radius=orad)
    # Inset deep-gold rule — a few px inside, concentric rounded rect.
    inset = 5 * os_
    pygame.draw.rect(pnl, (*_GOLD_DEEP, 170),
                     (inset, inset, ow - 2 * inset, oh - 2 * inset),
                     width=max(1, os_), border_radius=max(1, orad - inset))
    # A whisper of pale on the inset's top edge sells the "engraved groove".
    pygame.draw.line(pnl, (*_GOLD_PALE, 70),
                     (inset + orad, inset - os_),
                     (ow - inset - orad, inset - os_), max(1, os_ // 2))
    surf.blit(pygame.transform.smoothscale(pnl, rect.size), rect.topleft)


def cand_metallic_emboss(surf, rect):
    """C — Raised Metal. Two-tone metallic rim (bright outer + deep-gold inner)
    over a subtle gradient body, plus a 1 px inner bevel: pale on top/left,
    dark on bottom/right, so the whole tile looks physically raised."""
    os_ = _PANEL_OS
    ow, oh, orad = rect.width * os_, rect.height * os_, RADIUS * os_
    pnl = _grad_body(ow, oh, orad, _PANEL_LIGHTER, _PANEL_DARK)
    # Inner bevel: light top+left, dark bottom+right (just inside the rim).
    b = 3 * os_
    bw = max(1, os_)
    # Top edge highlight.
    pygame.draw.line(pnl, (*_GOLD_PALE, 90),
                     (orad, b), (ow - orad, b), bw)
    # Left edge highlight.
    pygame.draw.line(pnl, (*_GOLD_PALE, 60),
                     (b, orad), (b, oh - orad), bw)
    # Bottom edge shadow.
    pygame.draw.line(pnl, (*NEAR_BLACK, 120),
                     (orad, oh - b), (ow - orad, oh - b), bw)
    # Right edge shadow.
    pygame.draw.line(pnl, (*NEAR_BLACK, 90),
                     (ow - b, orad), (ow - b, oh - orad), bw)
    # Two-tone metallic rim: deep-gold underlayer, bright on top.
    pygame.draw.rect(pnl, (*_GOLD_DEEP, 200), (0, 0, ow, oh),
                     width=3 * os_, border_radius=orad)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 200), (0, 0, ow, oh),
                     width=max(1, int(1.5 * os_)), border_radius=orad)
    surf.blit(pygame.transform.smoothscale(pnl, rect.size), rect.topleft)


def cand_corner_brackets(surf, rect):
    """D — Corner Brackets. Thin single rim kept understated, but each corner
    gets an L-shaped gold bracket (bright with a deep-gold shadow ply) — a
    jewelry-box / passport-frame finishing touch that draws the eye to the
    card's shape without adding any interior clutter."""
    os_ = _PANEL_OS
    ow, oh, orad = rect.width * os_, rect.height * os_, RADIUS * os_
    pnl = _base_body(ow, oh, orad)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 120), (0, 0, ow, oh),
                     width=max(1, int(1.5 * os_)), border_radius=orad)
    # Bracket geometry: legs start past the corner radius, run inward.
    leg = 18 * os_          # length of each bracket arm
    pad = orad - 1 * os_    # how far the bracket sits off the true corner
    tw = max(1, int(2.5 * os_))   # bracket thickness
    sh = max(1, os_)              # shadow ply offset

    def bracket(cx, cy, dx, dy):
        # Deep-gold shadow ply (offset toward card interior) first, then bright.
        for col, off in ((_GOLD_DEEP, sh), (_GOLD_BRIGHT, 0)):
            ax, ay = cx + off * dx, cy + off * dy
            pygame.draw.line(pnl, (*col, 230),
                             (ax, ay), (ax + leg * dx, ay), tw)
            pygame.draw.line(pnl, (*col, 230),
                             (ax, ay), (ax, ay + leg * dy), tw)
    bracket(pad, pad, 1, 1)                      # top-left
    bracket(ow - pad, pad, -1, 1)                # top-right
    bracket(pad, oh - pad, 1, -1)                # bottom-left
    bracket(ow - pad, oh - pad, -1, -1)          # bottom-right
    surf.blit(pygame.transform.smoothscale(pnl, rect.size), rect.topleft)


def cand_inset_vignette(surf, rect):
    """E — Framed Mat. An engraved double rule (bright outer rim + deep-gold
    inset) framing a darkened interior mat — a soft inner vignette pushes the
    edges down and lifts the icon/text off a slightly brighter centre, like a
    matted print in a gilt frame."""
    os_ = _PANEL_OS
    ow, oh, orad = rect.width * os_, rect.height * os_, RADIUS * os_
    pnl = _base_body(ow, oh, orad)
    # Inner vignette: dark ring near the edges fading to clear at centre.
    vig = pygame.Surface((ow, oh), pygame.SRCALPHA)
    cx, cy = ow / 2, oh / 2
    maxd = math.hypot(cx, cy)
    step = 2 * os_
    for r in range(int(maxd), 0, -step):
        t = r / maxd
        # Only the outer ~35% darkens; centre stays clear.
        a = int(110 * max(0.0, (t - 0.62) / 0.38)) if t > 0.62 else 0
        if a:
            pygame.draw.circle(vig, (0, 0, 0, a), (int(cx), int(cy)), r)
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    vig.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pnl.blit(vig, (0, 0))
    # Engraved double rule on top of the matted body.
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 150), (0, 0, ow, oh),
                     width=2 * os_, border_radius=orad)
    inset = 6 * os_
    pygame.draw.rect(pnl, (*_GOLD_DEEP, 160),
                     (inset, inset, ow - 2 * inset, oh - 2 * inset),
                     width=max(1, os_), border_radius=max(1, orad - inset))
    surf.blit(pygame.transform.smoothscale(pnl, rect.size), rect.topleft)


CANDIDATES = [
    ("A  SOFT VOLUME",     "body gradient + top sheen, single rim",
     cand_gradient_sheen),
    ("B  ENGRAVED BEZEL",  "bright rim + deep-gold inset rule",
     cand_engraved_bezel),
    ("C  RAISED METAL",    "two-tone rim + 1px inner bevel + gradient",
     cand_metallic_emboss),
    ("D  CORNER BRACKETS", "L brackets w/ deep-gold shadow ply",
     cand_corner_brackets),
    ("E  FRAMED MAT",      "double rule + soft inner vignette",
     cand_inset_vignette),
]


# ── card content (real icon + name + blurb), drawn into a tile ──────────────
def render_card(frame_fn):
    """One real 162x124 card on the actual gradient + stars bg, with the live
    TRIPLE icon, gold name, and cream blurb — the exact layout from
    PowerUpHelpScene so we judge the frame in true context."""
    surf = pygame.Surface((CARD_W + 24, CARD_H + 24))
    bg = pygame.Surface((W, H))
    _gradient_bg(bg)
    _draw_overlay_stars(bg, _seeded_stars(), 0.9)
    # Sample a slice of the real screen background behind the card position so
    # the gradient + a few stars sit under the frame, exactly as in-game.
    src = pygame.Rect(99, 120, CARD_W + 24, CARD_H + 24)
    surf.blit(bg.subsurface(src), (0, 0))

    card = pygame.Rect(12, 12, CARD_W, CARD_H)
    frame_fn(surf, card)

    _powerup_icon(surf, "triple", card.centerx, card.y + 32, 48)
    nimg = _font(14, True).render("TRIPLE", True, _GOLD_BRIGHT)
    surf.blit(nimg, nimg.get_rect(center=(card.centerx, card.y + 66)))
    f = _font(12, True)
    for li, line in enumerate(_wrap(f, "Coins are worth 3x", CARD_W - 16)[:3]):
        img = f.render(line, True, UI_CREAM)
        surf.blit(img, img.get_rect(center=(card.centerx, card.y + 84 + li * 14)))
    return surf, card


# ── current shipped frame, for the reference column ─────────────────────────
def cand_current(surf, rect):
    os_ = _PANEL_OS
    ow, oh, orad = rect.width * os_, rect.height * os_, RADIUS * os_
    pnl = _base_body(ow, oh, orad)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 130), (0, 0, ow, oh),
                     width=2 * os_, border_radius=orad)
    surf.blit(pygame.transform.smoothscale(pnl, rect.size), rect.topleft)


# ── compose the review sheet ────────────────────────────────────────────────
ZOOM = 2.7
TILE_W = int((CARD_W + 24) * ZOOM)
TILE_H = int((CARD_H + 24) * ZOOM)
MARGIN, GAP = 30, 26
LABEL_H = 56
HEADER = 92

title_f = pygame.font.Font(None, 46)
sub_f = pygame.font.Font(None, 26)
lab_f = pygame.font.Font(None, 30)
desc_f = pygame.font.Font(None, 22)
small_f = pygame.font.Font(None, 24)

# 3 columns x 2 rows holds current + 5 candidates.
COLS, ROWS = 3, 2
sheet_w = MARGIN * 2 + COLS * TILE_W + (COLS - 1) * GAP
inset_block_h = (CARD_H + 24) + LABEL_H + 16     # 1x native inset row
sheet_h = (HEADER + ROWS * (TILE_H + LABEL_H) + (ROWS - 1) * GAP
           + GAP + inset_block_h + MARGIN)

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((20, 17, 34))

# Header.
t = title_f.render("POWER-UPS CARD FRAME — POLISH  (round 1)", True, (245, 235, 210))
sheet.blit(t, (MARGIN, 22))
s = sub_f.render("real 162x124 cards in context, shown at 2.7x  |  1x native inset below",
                 True, (168, 158, 188))
sheet.blit(s, (MARGIN, 58))

tiles = [("CURRENT", "rim only — 'too naked'", cand_current)] + CANDIDATES

for i, (label, desc, fn) in enumerate(tiles):
    col = i % COLS
    row = i // COLS
    x = MARGIN + col * (TILE_W + GAP)
    y = HEADER + row * (TILE_H + LABEL_H + GAP)
    card_surf, _ = render_card(fn)
    zoomed = pygame.transform.smoothscale(card_surf, (TILE_W, TILE_H))
    # Reference column gets a muted label so candidates stand out.
    is_ref = (i == 0)
    sheet.blit(zoomed, (x, y))
    pygame.draw.rect(sheet, (70, 60, 95), (x, y, TILE_W, TILE_H), 1)
    lcol = (150, 142, 168) if is_ref else (250, 222, 150)
    li = lab_f.render(label, True, lcol)
    sheet.blit(li, (x, y + TILE_H + 8))
    di = desc_f.render(desc, True, (160, 152, 180))
    sheet.blit(di, (x, y + TILE_H + 34))

# 1x native inset strip: the current card + candidate B (engraved bezel) and
# candidate C (raised metal) at TRUE size so legibility/scale is judgeable.
inset_y = HEADER + ROWS * (TILE_H + LABEL_H) + (ROWS - 1) * GAP + GAP
hd = small_f.render("AT TRUE 1x NATIVE SIZE (162x124):", True, (245, 235, 210))
sheet.blit(hd, (MARGIN, inset_y))
inset_y += 28
inset_specs = [
    ("CURRENT", cand_current),
    ("B BEZEL", cand_engraved_bezel),
    ("C METAL", cand_metallic_emboss),
    ("D BRACKETS", cand_corner_brackets),
]
ix = MARGIN
for label, fn in inset_specs:
    card_surf, _ = render_card(fn)
    sheet.blit(card_surf, (ix, inset_y))
    li = small_f.render(label, True, (210, 200, 226))
    sheet.blit(li, (ix, inset_y + card_surf.get_height() + 4))
    ix += card_surf.get_width() + GAP

OUT_DIR = os.path.join(_ROOT, "docs", "powerups_frame_polish")
os.makedirs(OUT_DIR, exist_ok=True)
out = os.path.join(OUT_DIR, "round_1.png")
pygame.image.save(sheet, out)
print("saved", out)
pygame.quit()
