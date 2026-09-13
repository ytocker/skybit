"""Side-by-side comparison of the SKATEBOARD pickup icon recipe.

LEFT  = current production state (NATIVE = 40, broken proportions —
        ears too big, crossed-X boards clip at the corners).
MID   = restored design: render the icon at its AUTHORED 96-native
        footprint, then smoothscale down to the user's chosen 40 px.
RIGHT = reference at full 96 px so the user can see what the original
        design looks like at its authored size.

Lets the user confirm the MID cell matches the pre-helmet original
before we change `_draw_skateboard_icon` in production.

Output: docs/screenshots/icon_sizes/skateboard_compare.png
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game.entities import PowerUp


SHIPPED_DISPLAY = 40   # what production currently shows
AUTHORED        = 96   # what the recipe was designed for


def _render_at_recipe_native(target_n: int) -> pygame.Surface:
    """Run _draw_skateboard_icon with NATIVE_W/H monkey-patched to
    `target_n` (the value the recipe sees). Returns a `target_n`-sized
    sprite — the SAME path as production."""
    from unittest.mock import patch

    # The recipe pulls NATIVE_W from the local scope; we re-rewrite the
    # module-level constant the icon uses by editing the bytecode is too
    # fiddly. Simpler: bake a wrapper that draws to a temp surface big
    # enough, then crop the central region the recipe touched.
    #
    # Easier route: run the recipe by injecting NATIVE through a quick
    # rewrite — we re-exec just the relevant inner block on a fresh
    # PowerUp.
    #
    # Simplest of all: render at production-current settings into a
    # 200×200 canvas and crop the result. Production uses NATIVE=40
    # baked into the function, so for that cell we just call it.
    surf = pygame.Surface((target_n + 80, target_n + 80), pygame.SRCALPHA)
    p = PowerUp(surf.get_width() // 2, surf.get_height() // 2,
                kind="skateboard")
    p.pulse = 0.0
    p._draw_skateboard_icon(surf)
    cx, cy = surf.get_width() // 2, surf.get_height() // 2
    r = pygame.Rect(0, 0, target_n, target_n)
    r.center = (cx, cy)
    return surf.subsurface(r).copy()


def _render_with_native_override(target_n: int) -> pygame.Surface:
    """Render with NATIVE_W/H temporarily set to `target_n` so the icon
    is authored at that footprint. We do this by rewriting the bound
    method's __code__ co_consts — the cleanest source-faithful approach
    without forking the recipe."""
    # The recipe has `NATIVE_W = NATIVE_H = 40` baked in as a literal.
    # We work around this by writing a temporary module-level mirror
    # that mutates and reinstalls the function.
    import importlib
    from game import entities as E_mod

    src = open(E_mod.__file__).read()
    needle = "        NATIVE_W = NATIVE_H = 40"
    replacement = f"        NATIVE_W = NATIVE_H = {target_n}"
    if needle not in src:
        raise SystemExit(f"could not find {needle!r} in entities.py")
    patched = src.replace(needle, replacement, 1)

    # Load the patched module under a throwaway name so production
    # state isn't touched.
    tmp_path = os.path.join(os.path.dirname(THIS_DIR),
                            "tools", "_entities_recipe_tmp.py")
    with open(tmp_path, "w") as f:
        f.write(patched)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_entities_tmp",
                                                       tmp_path)
        tmp_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tmp_mod)
        surf = pygame.Surface((target_n + 80, target_n + 80),
                               pygame.SRCALPHA)
        p = tmp_mod.PowerUp(surf.get_width() // 2,
                             surf.get_height() // 2, kind="skateboard")
        p.pulse = 0.0
        p._draw_skateboard_icon(surf)
        cx, cy = surf.get_width() // 2, surf.get_height() // 2
        r = pygame.Rect(0, 0, target_n, target_n)
        r.center = (cx, cy)
        return surf.subsurface(r).copy()
    finally:
        os.remove(tmp_path)


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "skateboard_compare.png")

    # LEFT: current production state. Recipe NATIVE = 40, shape sizes
    # in SS-units → ears proportionally larger, X boards clipped.
    left = _render_at_recipe_native(SHIPPED_DISPLAY)

    # MID: restored — recipe runs at authored NATIVE = 96, then we
    # smoothscale the produced sprite down to the user's 40-px display.
    big = _render_with_native_override(AUTHORED)
    mid = pygame.transform.smoothscale(big, (SHIPPED_DISPLAY,
                                             SHIPPED_DISPLAY))

    # RIGHT: reference — recipe at authored NATIVE = 96, full size.
    right = big

    # Compose sheet
    ZOOM = 6
    cell_l = pygame.transform.scale(left, (left.get_width() * ZOOM,
                                            left.get_height() * ZOOM))
    cell_m = pygame.transform.scale(mid, (mid.get_width() * ZOOM,
                                           mid.get_height() * ZOOM))
    cell_r = pygame.transform.scale(right, (right.get_width() * 3,
                                             right.get_height() * 3))

    CARD_BG = (24, 26, 34)
    BORDER  = (50, 54, 66)
    LABEL   = (235, 235, 240)
    SUB     = (165, 173, 185)

    PAD       = 20
    LABEL_H   = 26
    SUB_H     = 18
    GAP       = 24
    TITLE_H   = 50

    sheet_w = (PAD * 2 + cell_l.get_width() + GAP
               + cell_m.get_width() + GAP + cell_r.get_width())
    sheet_h = (TITLE_H + LABEL_H + max(cell_l.get_height(),
                                        cell_m.get_height(),
                                        cell_r.get_height())
               + SUB_H + PAD * 2)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title_font = pygame.font.SysFont("Arial", 22, bold=True)
    title = title_font.render(
        "SKATEBOARD icon: current (broken) vs restored at 40 px display",
        True, LABEL)
    sheet.blit(title, (PAD, PAD))

    cap_font = pygame.font.SysFont("Arial", 14, bold=True)
    sub_font = pygame.font.SysFont("Arial", 12)

    cells = (
        (cell_l, "CURRENT (broken)",
         "recipe at NATIVE=40 → big canvas 240 px → X boards clip"),
        (cell_m, "RESTORED at 40 px",
         "recipe at NATIVE=96 → smoothscale to 40 → full design"),
        (cell_r, "REFERENCE at 96 px",
         "the pre-helmet shipped design (commit 06520cb)"),
    )
    x = PAD
    y_top = TITLE_H + PAD
    for cell, lbl, sub in cells:
        cap = cap_font.render(lbl, True, LABEL)
        sheet.blit(cap, (x + (cell.get_width() - cap.get_width()) // 2,
                         y_top))
        cy = y_top + LABEL_H
        pygame.draw.rect(sheet, BORDER,
                         (x - 2, cy - 2, cell.get_width() + 4,
                          cell.get_height() + 4), 1)
        sheet.blit(cell, (x, cy))
        sub_s = sub_font.render(sub, True, SUB)
        sheet.blit(sub_s,
                   (x + (cell.get_width() - sub_s.get_width()) // 2,
                    cy + cell.get_height() + 4))
        x += cell.get_width() + GAP

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
