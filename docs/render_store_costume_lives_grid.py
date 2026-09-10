"""
Render a grid: rows = store COSTUME-tab skins, columns = lives states.

Output: docs/costume_lives_grid.png
"""
import sys, os, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# skin_basketball imports game.store_data which needs STORE_FILE from config —
# a symbol not present on this branch. Stub it out before any game imports.
if 'game.store_data' not in sys.modules:
    _sd = types.ModuleType('game.store_data')
    _sd.sync_from_store = lambda: None
    sys.modules['game.store_data'] = _sd

import pygame
pygame.init()
pygame.font.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.parrot as _parrot
from game.parrot import (
    _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
    _h_draw_ragged_cuts, _h_draw_cracked_lens, _fh_draw_single_crack,
    _h_build_hurt_frame, _fh_build_hurt_frame,
    _add_outline, get_parcel,
)
from game.dollar_parrot_ghost import _build_parrot_with_palette, _draw_lenses
from game.store_skins import (
    PARROT_DY,
    P_NINJA, _TH_BODY, _MU_BODY, P_ASTRONAUT, P_PILOT,
    _VK_PAL, _VK_OUTLINE,
    _paint_pirate, _paint_cowboy, _paint_pharaoh, _paint_crown,
    _paint_baseball, _paint_tennis, _paint_wizard,
    _paint_ninja, _paint_tophat, _paint_mummy, _paint_astronaut, _paint_pilot,
    _viking_axe, _viking_back, _viking_helm, _viking_face, _viking_base,
)
from game.skin_basketball import _paint_laker

# ── layout ────────────────────────────────────────────────────────────────────
LABEL_W = 150
CELL_W  = 110
CELL_H  = 140
HDR_H   = 48
MARGIN  = 14
BIRD_Y  = 52

BG       = (22, 26, 36)
LABEL_BG = (32, 36, 50)
TEXT_COL = (220, 220, 230)
SKY_TOP  = (80, 130, 210)
SKY_BOT  = (100, 150, 200)

COLS      = ["CLEAN", "FIRST-HIT", "LAST-LIFE"]
COL_STATES = ["clean", "first_hit", "last_life"]

# (skin_id, display_name, base_type, palette, paint_fn)
# base_type "standard" → scarlet macaw body (_h/_fh_build_hurt_frame) + paint_fn
# base_type "palette"  → _build_parrot_with_palette(palette) + paint_fn + manual dressings
# base_type "viking"   → custom axe-behind-body composite
COSTUMES = [
    # (skin_id, display_name, base_type, palette, paint_fn, draw_std_lenses)
    ("skin_pirate",     "PIRATE",     "standard", None,        _paint_pirate,     False),
    ("skin_cowboy",     "COWBOY",     "standard", None,        _paint_cowboy,     False),
    ("skin_pharaoh",    "PHARAOH",    "standard", None,        _paint_pharaoh,    False),
    ("skin_crown",      "CROWN",      "standard", None,        _paint_crown,      False),
    ("skin_baseball",   "BASEBALL",   "standard", None,        _paint_baseball,   False),
    ("skin_tennis",     "TENNIS",     "standard", None,        _paint_tennis,     False),
    ("skin_wizard",     "WIZARD",     "standard", None,        _paint_wizard,     False),
    ("skin_basketball", "BASKETBALL", "standard", None,        _paint_laker,      False),
    ("skin_tophat",     "GENTLEMAN",  "palette",  _TH_BODY,    _paint_tophat,     False),
    ("skin_ninja",      "NINJA",      "palette",  P_NINJA,     _paint_ninja,      False),
    ("skin_mummy",      "MUMMY",      "palette",  _MU_BODY,    _paint_mummy,      False),
    ("skin_astronaut",  "ASTRONAUT",  "palette",  P_ASTRONAUT, _paint_astronaut,  False),
    ("skin_pilot",      "CAPTAIN",    "palette",  P_PILOT,     _paint_pilot,      True),
    ("skin_viking",     "VIKING",     "viking",   _VK_PAL,     None,              False),
]


def _font(size):
    return pygame.font.SysFont("monospace", size, bold=True)


def fill_sky(surf):
    w, h = surf.get_size()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w - 1, y))


def _build_standard_hurt(paint_fn, lives_state):
    """Hurt frame for standard scarlet-macaw-body costumes: hurt body + costume accessories."""
    if lives_state == "first_hit":
        body = _fh_build_hurt_frame(10.0)
    else:
        body = _h_build_hurt_frame(10.0)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, 10.0)
    return _add_outline(comp)


def _build_palette_hurt(palette, paint_fn, lives_state, draw_std_lenses=False):
    """Hurt frame for custom-palette costumes: palette body + accessories + manual dressings."""
    base = _build_parrot_with_palette(10.0, palette, draw_lenses=False)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(base, (0, PARROT_DY))
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    if lives_state == "first_hit":
        if draw_std_lenses:
            _draw_lenses(sprite, 50, 20, palette)
        _fh_draw_single_crack(sprite)
        if paint_fn:
            paint_fn(comp, 10.0)
    else:
        _h_draw_headwrap(sprite)
        _h_draw_chest_dressing(sprite)
        _h_draw_ragged_cuts(sprite)
        if draw_std_lenses:
            _draw_lenses(sprite, 50, 20, palette)
        _h_draw_cracked_lens(sprite)
        if paint_fn:
            paint_fn(comp, 10.0)
    return _add_outline(comp)


def _build_viking_hurt(lives_state):
    """Viking hurt: axe behind palette hurt body, then shield/helm/face, then dressings."""
    body = _build_parrot_with_palette(10.0, _VK_PAL, draw_lenses=False)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    _viking_axe(comp)
    comp.blit(body, (0, PARROT_DY))
    _viking_back(comp)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    if lives_state == "last_life":
        _h_draw_headwrap(sprite)
    _viking_helm(comp)
    _viking_face(comp)
    if lives_state == "first_hit":
        _fh_draw_single_crack(sprite)
    else:
        _h_draw_chest_dressing(sprite)
        _h_draw_ragged_cuts(sprite)
        _h_draw_cracked_lens(sprite)
    return _add_outline(comp, outline_color=_VK_OUTLINE)


def render_cell(skin_id, base_type, palette, paint_fn, draw_std_lenses, lives_state):
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)

    par = get_parcel("normal")

    if lives_state == "clean":
        if base_type == "standard":
            # Build manually for consistency (avoids store-sync issues with basketball).
            comp = pygame.Surface((64, 100), pygame.SRCALPHA)
            from game.parrot import _build_frame
            comp.blit(_build_frame(10.0), (0, PARROT_DY))
            if paint_fn:
                paint_fn(comp, 10.0)
            img = _add_outline(comp)
        elif base_type == "palette":
            base = _build_parrot_with_palette(10.0, palette)
            comp = pygame.Surface((64, 100), pygame.SRCALPHA)
            comp.blit(base, (0, PARROT_DY))
            if paint_fn:
                paint_fn(comp, 10.0)
            img = _add_outline(comp)
        else:  # viking
            comp = pygame.Surface((64, 100), pygame.SRCALPHA)
            _viking_axe(comp)
            comp.blit(_viking_base(10.0), (0, PARROT_DY))
            _viking_back(comp)
            _viking_helm(comp)
            _viking_face(comp)
            img = _add_outline(comp, outline_color=_VK_OUTLINE)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
    else:
        if base_type == "standard":
            img = _build_standard_hurt(paint_fn, lives_state)
        elif base_type == "palette":
            img = _build_palette_hurt(palette, paint_fn, lives_state, draw_std_lenses)
        else:  # viking
            img = _build_viking_hurt(lives_state)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))

    return cell


def main():
    n_rows = len(COSTUMES)
    n_cols = len(COLS)
    total_w = MARGIN + LABEL_W + n_cols * CELL_W + MARGIN
    total_h = MARGIN + HDR_H + n_rows * CELL_H + MARGIN

    canvas = pygame.Surface((total_w, total_h))
    canvas.fill(BG)

    fnt_title = _font(14)
    fnt_hdr   = _font(11)
    fnt_label = _font(11)

    title = fnt_title.render("STORE COSTUMES × LIVES STATE", True, TEXT_COL)
    canvas.blit(title, title.get_rect(center=(total_w // 2, MARGIN + HDR_H // 2)))

    for ci, col_label in enumerate(COLS):
        cx = MARGIN + LABEL_W + ci * CELL_W + CELL_W // 2
        surf = fnt_hdr.render(col_label, True, TEXT_COL)
        canvas.blit(surf, surf.get_rect(center=(cx, MARGIN + HDR_H // 2)))

    for ri, (skin_id, display_name, base_type, palette, paint_fn, draw_std_lenses) in enumerate(COSTUMES):
        row_top = MARGIN + HDR_H + ri * CELL_H

        label_rect = pygame.Rect(MARGIN, row_top, LABEL_W, CELL_H)
        pygame.draw.rect(canvas, LABEL_BG, label_rect)
        lbl = fnt_label.render(display_name, True, TEXT_COL)
        canvas.blit(lbl, lbl.get_rect(center=(MARGIN + LABEL_W // 2, row_top + CELL_H // 2)))

        for ci, col_state in enumerate(COL_STATES):
            cell_x = MARGIN + LABEL_W + ci * CELL_W
            cell = render_cell(skin_id, base_type, palette, paint_fn, draw_std_lenses, col_state)
            canvas.blit(cell, (cell_x, row_top))
            pygame.draw.rect(canvas, BG, (cell_x, row_top, CELL_W, 1))
            pygame.draw.rect(canvas, BG, (cell_x, row_top, 1, CELL_H))

    pygame.draw.rect(canvas, (60, 65, 85), canvas.get_rect(), 2)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "costume_lives_grid.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {total_w}×{total_h} → {out_path}")
    pygame.quit()


if __name__ == "__main__":
    main()
