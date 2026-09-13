"""Full-card comparison: BEFORE + 5 tl2 price-tag concepts (affordable & locked).

6 rows × 2 columns. Each cell = full 162×100 1× card (skin_mummy EPIC).
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
    ("BEFORE\n(original)",   None),
    ("hang-tag",             "tools/_store_price_tl2_hang_tag_r2.py"),
    ("shelf-sticker",        "tools/_store_price_tl2_shelf_sticker_r2.py"),
    ("corner-sash",          "tools/_store_price_tl2_corner_sash_r2.py"),
    ("dog-ear",              "tools/_store_price_tl2_dog_ear_r2.py"),
    ("receipt-stub",         "tools/_store_price_tl2_receipt_stub_r2.py"),
]

# ── layout ────────────────────────────────────────────────────────────────────
CW, CH    = sc.CARD_W, sc.CARD_H   # 162 × 100
PAD       = 20
GAP_COL   = 8
GAP_ROW   = 14
HEADER_H  = 44
LABEL_W   = 100
COL_HDR_H = 24

BG   = (8, 8, 20)
GOLD = (255, 220, 80)
PALE = (206, 202, 224)
DIM  = (140, 136, 160)

canvas_w = PAD + LABEL_W + GAP_COL + 2 * CW + GAP_COL + PAD
canvas_h = (HEADER_H + COL_HDR_H
            + len(CONCEPTS) * (CH + GAP_ROW)
            - GAP_ROW + PAD)

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf  = hud_font(11, True)
lf  = hud_font(8, True)
smf = hud_font(7)

# main header
ht = hf.render("store price · top-left price tag · full-card comparison", True, GOLD)
canvas.blit(ht, (canvas_w // 2 - ht.get_width() // 2,
                 (HEADER_H - ht.get_height()) // 2))

# column headers
col_aff_x = PAD + LABEL_W + GAP_COL
col_lck_x = col_aff_x + CW + GAP_COL
for text, cx in [("AFFORDABLE", col_aff_x + CW // 2),
                 ("LOCKED",     col_lck_x + CW // 2)]:
    img = smf.render(text, True, DIM)
    canvas.blit(img, (cx - img.get_width() // 2, HEADER_H + 4))

y0 = HEADER_H + COL_HDR_H

for i, (label, r2_path) in enumerate(CONCEPTS):
    y = y0 + i * (CH + GAP_ROW)

    if r2_path is None:
        sc.price_chip = _orig_price_chip
    else:
        sc.price_chip = load_concept(r2_path)

    card_aff  = render_card_1x("skin_mummy", True)
    card_lock = render_card_1x("skin_mummy", False)

    canvas.blit(card_aff,  (col_aff_x, y))
    canvas.blit(card_lock, (col_lck_x, y))

    # sidebar label
    is_before = (i == 0)
    colour = GOLD if is_before else PALE
    top_lbl = label.split("\n")[0]
    lt = lf.render(top_lbl, True, colour)
    canvas.blit(lt, (PAD + LABEL_W - lt.get_width() - 4,
                     y + (CH - lt.get_height()) // 2 - 6))
    if "\n" in label:
        sub = smf.render(label.split("\n")[1], True, DIM)
        canvas.blit(sub, (PAD + LABEL_W - sub.get_width() - 4,
                          y + (CH - lt.get_height()) // 2 + lt.get_height() - 4))

sc.price_chip = _orig_price_chip

out = "docs/store_price_tl2/full_card_comparison.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
