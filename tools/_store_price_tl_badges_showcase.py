"""Phase 5 showcase: BEFORE (original price pill) + 5 concept badge crops from round_2.

Each concept panel is the x=0..64, y=0..64 badge zone from the round_2 render sheet's
first card (skin_mummy EPIC affordable), scaled to 200×200.
The BEFORE panel is rendered fresh with the unpatched price_chip.

Review-only tooling — never imported by the game.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

# ── BEFORE panel: unpatched original price_chip ───────────────────────────────
sd.wallet = 999_999   # ensure affordable state
_big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
_inset = sc.m(sc._INSET)
_rect = pygame.Rect(_inset, _inset,
                    sc.CARD_W * sc.SS - 2 * _inset,
                    sc.CARD_H * sc.SS - 2 * _inset)
sc.draw_card(_big, "skin_mummy", _rect, equipped=False, secret=False,
             variant=sc.PRICE_VARIANT)
before_card = pygame.transform.smoothscale(_big, (sc.CARD_W, sc.CARD_H))

# ── Load badge crops from each round_2 render sheet ──────────────────────────
# Each render sheet layout: PAD=20, HEADER_H=40; first card at (PAD, HEADER_H) = (20,40).
# Badge zone = top-left 64×64 of the 162×100 card.
PAD_SHEET  = 20
HDR_SHEET  = 40
CARD_X     = PAD_SHEET
CARD_Y     = HDR_SHEET
BADGE_CROP = pygame.Rect(0, 0, 64, 64)   # relative to card top-left

CONCEPTS = [
    ("coin-crown",    "docs/store_price_tl_badges/coin-crown/round_2.png"),
    ("corner-shield", "docs/store_price_tl_badges/corner-shield/round_2.png"),
    ("price-scroll",  "docs/store_price_tl_badges/price-scroll/round_2.png"),
    ("tag-rivet",     "docs/store_price_tl_badges/tag-rivet/round_2.png"),
    ("star-rosette",  "docs/store_price_tl_badges/star-rosette/round_2.png"),
]

concept_crops = []
for slug, path in CONCEPTS:
    sheet = pygame.image.load(path)
    # subsurface the first card from the sheet
    card_rect = pygame.Rect(CARD_X, CARD_Y, sc.CARD_W, sc.CARD_H)
    card = sheet.subsurface(card_rect.clip(sheet.get_rect())).copy()
    # crop the badge zone (top-left 64×64)
    crop = card.subsurface(BADGE_CROP.clip(card.get_rect())).copy()
    concept_crops.append((slug, crop))

# ── Layout ────────────────────────────────────────────────────────────────────
PANEL_SZ  = 200   # each panel is 200×200 (crop scaled up)
NCOLS     = 3
NROWS     = 2     # 6 panels: 1 BEFORE + 5 concepts
PAD       = 20
GAP       = 10
HEADER_H  = 44
LABEL_H   = 22

BG     = (8, 8, 20)
GOLD   = (255, 220, 80)
PALE   = (206, 202, 224)
BORDER = (46, 44, 68)

canvas_w = PAD * 2 + NCOLS * PANEL_SZ + (NCOLS - 1) * GAP
canvas_h = HEADER_H + NROWS * (PANEL_SZ + LABEL_H) + (NROWS - 1) * GAP + PAD
canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

# header
hf = hud_font(11, True)
ht = hf.render("store price · top-left badge · 5 concepts · round 2", True, GOLD)
canvas.blit(ht, (canvas_w // 2 - ht.get_width() // 2,
                 (HEADER_H - ht.get_height()) // 2))

lf = hud_font(8, True)

# BEFORE panel uses the original card, badge zone crop scaled to PANEL_SZ
before_crop = before_card.subsurface(BADGE_CROP.clip(before_card.get_rect())).copy()

panels = [("BEFORE\n(original)", before_crop)] + \
         [(slug, crop) for slug, crop in concept_crops]

for i, (label, crop) in enumerate(panels):
    col = i % NCOLS
    row = i // NCOLS
    px = PAD + col * (PANEL_SZ + GAP)
    py = HEADER_H + row * (PANEL_SZ + LABEL_H + GAP)

    # scale crop to PANEL_SZ × PANEL_SZ
    scaled = pygame.transform.smoothscale(crop, (PANEL_SZ, PANEL_SZ))

    pygame.draw.rect(canvas, BORDER, (px, py, PANEL_SZ, PANEL_SZ))
    canvas.fill(BG, (px + 1, py + 1, PANEL_SZ - 2, PANEL_SZ - 2))
    canvas.blit(scaled, (px, py))
    pygame.draw.rect(canvas, BORDER, (px, py, PANEL_SZ, PANEL_SZ), 1)

    # label
    top_lbl = label.split("\n")[0]
    lt = lf.render(top_lbl, True, GOLD if i == 0 else PALE)
    canvas.blit(lt, (px + (PANEL_SZ - lt.get_width()) // 2, py + PANEL_SZ + 4))
    if "\n" in label:
        sub_lbl = label.split("\n")[1]
        ls = lf.render(sub_lbl, True, (160, 156, 180))
        canvas.blit(ls, (px + (PANEL_SZ - ls.get_width()) // 2,
                         py + PANEL_SZ + 4 + lt.get_height()))

out = "docs/store_price_tl_badges/showcase.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
