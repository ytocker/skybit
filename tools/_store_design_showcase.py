"""Showcase: the three in-game store designs in all states.

Every surface is rendered by the REAL game code (game/store.py,
game/store_cards.py, game/store_design.py) under each STORE_DESIGN value —
no tools patching. Each design runs in its own subprocess so the flag is
resolved exactly as the game resolves it at import.

Per design column: the confirm popup in both states (affordable /
can't-afford), the item card in its five states (priced affordable,
priced can't-afford, owned EQUIP, EQUIPPED, secret), and the store
category screen.

Output: colorways/store_design_showcase_v6.png
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "docs", "confirm_purchase_v8", "premium-v1",
                       "colorways")
TMP = os.path.join(REPO, ".showcase_tmp")

CARD_STATES = ["price_ok", "price_locked", "equip", "equipped", "secret"]

_RENDER_ONE = '''
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, {repo!r})
import game.config as config
config.STORE_DESIGN = {flag!r}
import pygame
pygame.init(); pygame.display.set_mode((8, 8))
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import m
from game.config import W, H

SID = "skin_mummy"
SECRET_SID = next((s for s in store_catalog.CATALOG
                   if store_catalog.is_secret(s)), SID)
store_catalog.cost = lambda sid: 1100

class _Stub:
    _confirm = SID
    _confirm_panel = None
    confirm_yes_rect = None
    confirm_no_rect = None
    @staticmethod
    def _disp_name(_sid):
        return "MUMMY"

def pop(balance):
    store_data.balance = lambda: balance
    surf = pygame.Surface((360, 640))
    surf.fill((8, 8, 20))
    store_mod.StoreScene._draw_confirm(_Stub(), surf)
    return surf.subsurface(pygame.Rect(50, 40, 260, 442)).copy()

def card(sid, equipped, secret, owned, balance):
    store_data.balance = lambda: balance
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS),
                         pygame.SRCALPHA)
    rect = pygame.Rect(m(sc._INSET), m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * m(sc._INSET))
    sc.draw_card(big, sid, rect, equipped, secret, owned=owned)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))

tmp = {tmp!r}
flag = {flag!r}
pygame.image.save(pop(99999), f"{{tmp}}/{{flag}}_pop_ok.png")
pygame.image.save(pop(50), f"{{tmp}}/{{flag}}_pop_locked.png")
pygame.image.save(card(SID, False, False, False, 99999),
                  f"{{tmp}}/{{flag}}_card_price_ok.png")
pygame.image.save(card(SID, False, False, False, 50),
                  f"{{tmp}}/{{flag}}_card_price_locked.png")
pygame.image.save(card(SID, False, False, True, 99999),
                  f"{{tmp}}/{{flag}}_card_equip.png")
pygame.image.save(card(SID, True, False, False, 99999),
                  f"{{tmp}}/{{flag}}_card_equipped.png")
pygame.image.save(card(SECRET_SID, False, True, False, 99999),
                  f"{{tmp}}/{{flag}}_card_secret.png")

_orig_owned = store_data.is_owned
store_data.balance = lambda: 99999
store_data.is_owned = lambda s: s == "skin_cowboy" or _orig_owned(s)
store_data.equipped = lambda slot: "skin_cowboy"
sc.clear_cache()
scene = StoreScene()
scene.view = "category"
scene.tab = 0
scene.page = 0
cat = pygame.Surface((W, H))
scene.render(cat)
pygame.image.save(cat, f"{{tmp}}/{{flag}}_cat.png")
print(flag, "rendered")
'''


def main():
    os.makedirs(TMP, exist_ok=True)
    for flag in ("classic", "antique", "gilded"):
        r = subprocess.run(
            [sys.executable, "-c",
             _RENDER_ONE.format(repo=REPO, flag=flag, tmp=TMP)],
            capture_output=True, text=True, cwd=REPO)
        if r.returncode != 0:
            print(r.stderr[-800:])
            sys.exit(1)

    from PIL import Image, ImageDraw, ImageFont
    f_head = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    f_role = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    f_lab = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 21)

    MARGIN, HEAD, GAP, COLGAP = 24, 70, 24, 40
    pop_w, pop_h = 520, 884
    col_w = 2 * pop_w + GAP

    def load(name):
        return Image.open(os.path.join(TMP, name))

    card0 = load("gilded_card_price_ok.png")
    cw0, ch0 = card0.size
    card_w, card_h = cw0 * 2, ch0 * 2
    grid_cols = 3
    grid_rows = 2
    cat_w = col_w
    cat_h = cat_w * 640 // 360
    LAB = 30
    col_h = (pop_h + LAB + 16
             + grid_rows * (card_h + LAB + 12)
             + 16 + cat_h)
    strip_w = MARGIN * 2 + 3 * col_w + 2 * COLGAP
    strip_h = HEAD + col_h + 30
    strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
    idr = ImageDraw.Draw(strip)
    idr.text((MARGIN, 18),
             "STORE_DESIGN showcase · rendered by the shipped game code · "
             "popup states / card states / category · 2x",
             fill=(236, 214, 160), font=f_head)

    DESIGNS = [("classic", "CLASSIC"), ("antique", "ANTIQUE"),
               ("gilded", "GILDED (active)")]
    CARD_LABELS = {"price_ok": "priced · affordable",
                   "price_locked": "priced · can't afford",
                   "equip": "owned · EQUIP",
                   "equipped": "EQUIPPED",
                   "secret": "secret"}

    for ci, (flag, title) in enumerate(DESIGNS):
        x0 = MARGIN + ci * (col_w + COLGAP)
        idr.text((x0 + col_w // 2, HEAD - 6), title,
                 fill=(236, 214, 160), anchor="mb", font=f_role)
        y = HEAD
        for pi, (suffix, lab) in enumerate(
                (("pop_ok", "affordable"), ("pop_locked", "can't afford"))):
            p = load(f"{flag}_{suffix}.png").resize((pop_w, pop_h),
                                                    Image.LANCZOS)
            px = x0 + pi * (pop_w + GAP)
            strip.paste(p, (px, y))
            idr.text((px + pop_w // 2, y + pop_h + 6), lab,
                     fill=(200, 190, 160), anchor="mt", font=f_lab)
        y += pop_h + LAB + 16
        for si, state in enumerate(CARD_STATES):
            gx = x0 + (si % grid_cols) * (card_w + GAP)
            gy = y + (si // grid_cols) * (card_h + LAB + 12)
            c = load(f"{flag}_card_{state}.png").convert("RGBA")
            cbg = Image.new("RGBA", (card_w, card_h), (10, 9, 20, 255))
            cbg.alpha_composite(c.resize((card_w, card_h), Image.LANCZOS))
            strip.paste(cbg.convert("RGB"), (gx, gy))
            idr.text((gx + card_w // 2, gy + card_h + 4),
                     CARD_LABELS[state], fill=(200, 190, 160),
                     anchor="mt", font=f_lab)
        y += grid_rows * (card_h + LAB + 12) + 16
        cat = load(f"{flag}_cat.png").resize((cat_w, cat_h), Image.LANCZOS)
        strip.paste(cat, (x0, y))

    out = os.path.join(OUT_DIR, "store_design_showcase_v6.png")
    strip.save(out)
    print("saved", out, strip.size)
    for f in os.listdir(TMP):
        os.remove(os.path.join(TMP, f))
    os.rmdir(TMP)


if __name__ == "__main__":
    main()
