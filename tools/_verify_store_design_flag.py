"""Verify STORE_DESIGN flag renders against before_vs_chosen_v4.png.

Usage: python _verify_store_design_flag.py <classic|antique|gilded>

Sets game.config.STORE_DESIGN BEFORE the store modules import, renders the
confirm popup (same stub + crop as the reference figures), one card, and
the category screen through the REAL game code — no tools patching — and
diffs each against the matching column of the reference figure
(col 0 = classic, 1 = antique, 2 = gilded). The figure composited its overlays
after the popup downscale while the game draws everything in one pass, so
small sub-pixel differences are expected; the check uses a mean-abs-diff
tolerance and reports per-surface numbers.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FLAG = sys.argv[1] if len(sys.argv) > 1 else "gilded"
COL = {"classic": 0, "antique": 1, "gilded": 2}[FLAG]

import game.config as config
config.STORE_DESIGN = FLAG

import numpy as np
import pygame
pygame.init()
pygame.display.set_mode((8, 8))

import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import m
from game.config import W, H

assert store_mod.store_design.STORE_DESIGN == FLAG

store_data.balance = lambda: 99999
store_catalog.cost = lambda sid: 1100
SID = "skin_mummy"


class _Stub:
    _confirm = SID
    _confirm_panel = None
    confirm_yes_rect = None
    confirm_no_rect = None

    @staticmethod
    def _disp_name(_sid):
        return "MUMMY"


surf = pygame.Surface((360, 640))
surf.fill((8, 8, 20))
store_mod.StoreScene._draw_confirm(_Stub(), surf)
pop = surf.subsurface(pygame.Rect(50, 40, 260, 442)).copy()

big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
rect = pygame.Rect(m(sc._INSET), m(sc._INSET),
                   sc.CARD_W * sc.SS - 2 * m(sc._INSET),
                   sc.CARD_H * sc.SS - 2 * m(sc._INSET))
sc.draw_card(big, SID, rect, False, False, owned=False)
card = pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))

_orig_owned = store_data.is_owned
store_data.is_owned = lambda s: s == "skin_cowboy" or _orig_owned(s)
store_data.equipped = lambda slot: "skin_cowboy"
sc.clear_cache()
scene = StoreScene()
scene.view = "category"
scene.tab = 0
scene.page = 0
cat = pygame.Surface((W, H))
scene.render(cat)

from PIL import Image
fig = np.array(Image.open(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "confirm_purchase_v8", "premium-v1", "colorways",
    "before_vs_chosen_v4.png")), dtype=np.float64)[..., :3]


x0 = 24 + COL * 580
# popup: figure pasted a PIL LANCZOS 2x of the RGB surface
pp = Image.frombytes("RGB", pop.get_size(), pygame.image.tostring(pop, "RGB"))
pop2 = np.array(pp.resize((520, 884), Image.LANCZOS), dtype=np.float64)
d_pop = np.abs(pop2 - fig[64:64 + 884, x0 + 20:x0 + 540]).mean()
# card: figure LANCZOS-resized the RGBA card 2x and composited on (10,9,20)
cc = Image.frombytes("RGBA", card.get_size(),
                     pygame.image.tostring(card, "RGBA"))
cbg = Image.new("RGBA", (sc.CARD_W * 2, sc.CARD_H * 2), (10, 9, 20, 255))
cbg.alpha_composite(cc.resize((sc.CARD_W * 2, sc.CARD_H * 2), Image.LANCZOS))
d_card = np.abs(np.array(cbg.convert("RGB"), dtype=np.float64)
                - fig[64 + 884 + 12:64 + 884 + 12 + sc.CARD_H * 2,
                      x0 + 118:x0 + 118 + sc.CARD_W * 2]).mean()
# category: figure LANCZOS-resized the full screen to 560 wide
cat_w = 560
cat_h = cat_w * H // W
ci = Image.frombytes("RGB", cat.get_size(), pygame.image.tostring(cat, "RGB"))
cat2 = np.array(ci.resize((cat_w, cat_h), Image.LANCZOS), dtype=np.float64)
y_cat = 64 + 884 + 12 + sc.CARD_H * 2 + 12
d_cat = np.abs(cat2 - fig[y_cat:y_cat + cat_h, x0:x0 + cat_w]).mean()

print(f"[{FLAG}] popup diff={d_pop:.2f}  card diff={d_card:.2f}  "
      f"category diff={d_cat:.2f}  (mean abs, 0-255 scale)")
ok = d_pop < 1.0 and d_card < 1.0 and d_cat < 1.0
print(f"[{FLAG}] {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
