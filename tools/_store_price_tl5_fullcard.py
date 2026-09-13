"""Full-card comparison: BEFORE + 5 tl5 hang-tag concepts (affordable only).

6 rows × 1 column. Each cell = full 162×100 1× card (skin_mummy EPIC).
Numbered IDs on each row (BEFORE has no number; concepts are 1–5).
"""
import os, sys

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

_orig_price_chip = sc.price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def load_concept(r2_path):
    """Exec r2 script in isolated namespace; return its my_price_chip."""
    ns = {"__name__": "__isolated__"}
    with open(r2_path) as f:
        src = f.read()
    lines = src.splitlines()
    cutoff = None
    for i, line in enumerate(lines):
        if line.strip().startswith("sc.price_chip = my_price_chip"):
            cutoff = i + 1
            break
    if cutoff is None:
        cutoff = len(lines)
    exec(compile("\n".join(lines[:cutoff]), r2_path, "exec"), ns)
    return ns["my_price_chip"]


CONCEPTS = [
    (None,  "BEFORE\n(tl2 hang-tag)",  "tools/_store_price_tl2_hang_tag_r2.py"),
    (1,     "cream-ruled",             "tools/_store_price_tl5_cream_ruled_r2.py"),
    (2,     "label-stripe",            "tools/_store_price_tl5_label_stripe_r2.py"),
    (3,     "vellum-border",           "tools/_store_price_tl5_vellum_border_r2.py"),
    (4,     "ornament-rule",           "tools/_store_price_tl5_ornament_rule_r2.py"),
    (5,     "parchment-ledger",        "tools/_store_price_tl5_parchment_ledger_r2.py"),
]

# ── layout ────────────────────────────────────────────────────────────────────
CW, CH    = sc.CARD_W, sc.CARD_H   # 162 × 100
PAD       = 20
GAP_ROW   = 14
HEADER_H  = 44
LABEL_W   = 110
ID_W      = 28

BG   = (8, 8, 20)
GOLD = (255, 220, 80)
PALE = (206, 202, 224)
DIM  = (140, 136, 160)

canvas_w = PAD + ID_W + LABEL_W + CW + PAD
canvas_h = (HEADER_H
            + len(CONCEPTS) * (CH + GAP_ROW)
            - GAP_ROW + PAD)

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf   = hud_font(11, True)
idf  = hud_font(14, True)
lf   = hud_font(8, True)
smf  = hud_font(7)

# main header
ht = hf.render("store price · tl5 hang-tag · full-card comparison", True, GOLD)
canvas.blit(ht, (canvas_w // 2 - ht.get_width() // 2,
                 (HEADER_H - ht.get_height()) // 2))

card_x = PAD + ID_W + LABEL_W
y0 = HEADER_H

for i, (num, label, r2_path) in enumerate(CONCEPTS):
    y = y0 + i * (CH + GAP_ROW)

    sc.price_chip = load_concept(r2_path)
    card_aff = render_card_1x("skin_mummy", True)
    canvas.blit(card_aff, (card_x, y))

    # ID number (large, left of label)
    is_before = (num is None)
    if not is_before:
        id_img = idf.render(str(num), True, GOLD)
        canvas.blit(id_img, (PAD + ID_W - id_img.get_width(),
                              y + (CH - id_img.get_height()) // 2))

    # slug label
    colour = GOLD if is_before else PALE
    top_lbl = label.split("\n")[0]
    lt = lf.render(top_lbl, True, colour)
    lx = PAD + ID_W + LABEL_W - lt.get_width() - 4
    ly = y + (CH - lt.get_height()) // 2 - (6 if "\n" in label else 0)
    canvas.blit(lt, (lx, ly))
    if "\n" in label:
        sub = smf.render(label.split("\n")[1], True, DIM)
        canvas.blit(sub, (PAD + ID_W + LABEL_W - sub.get_width() - 4,
                           ly + lt.get_height() - 2))

sc.price_chip = _orig_price_chip

out = "docs/store_price_tl5/full_card_comparison.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
