"""
Render a grid: rows = store COSTUME-tab skins × 3 life states,
               columns = powerup effects (Normal, Ghost, Triple, Gst+Trpl, Grow, Poison).

Output: docs/costume_powerup_lives_grid.png
"""
import sys, os, types
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

if 'game.store_data' not in sys.modules:
    _sd = types.ModuleType('game.store_data')
    _sd.sync_from_store = lambda: None
    sys.modules['game.store_data'] = _sd

import numpy as np
import pygame
import pygame.surfarray as sa
pygame.init()
pygame.font.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.parrot as _parrot
from game.parrot import (
    _build_frame,
    _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
    _h_draw_ragged_cuts, _h_draw_cracked_lens, _fh_draw_single_crack,
    _h_build_hurt_frame, _fh_build_hurt_frame,
    _add_outline, get_parcel, get_fried_parrot,
)
from game.entities import Bird
from game.dollar_parrot_ghost import _build_parrot_with_palette, _draw_lenses
from game.dollar_parrot_dead import P_CHARTREUSE, _draw_b_x_eyes
from game.dollar_parrot_hat import draw_stovepipe, HAT_HX, HAT_HY
from game.config import GROW_SCALE, PARCEL_Y_OFFSET
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

# ── layout ─────────────────────────────────────────────────────────────────────
LABEL_W  = 150
CELL_W   = 100
CELL_H   = 130
HDR_H    = 48
MARGIN   = 12
SKIN_DIV = 6
BIRD_Y   = 46

BG       = (22, 26, 36)
LABEL_BG = (32, 36, 50)
DIV_COL  = (45, 50, 68)
TEXT_COL = (220, 220, 230)
DIM_COL  = (130, 130, 150)
SKY_TOP  = (80, 130, 210)
SKY_BOT  = (100, 150, 200)

COLS     = ["Normal", "Ghost", "Triple", "Gst+Trpl", "Grow", "Poison", "KFC", "Skateboard"]
COL_KEYS = ["normal", "ghost", "triple", "ghost_triple", "grow", "poison", "kfc", "skateboard"]

_HELMET_CACHE = None
_BOARD_CACHE  = None

ROWS     = ["CLEAN", "FIRST-HIT", "LAST-LIFE"]
ROW_KEYS = ["clean", "first_hit", "last_life"]

# (skin_id, display_name, base_type, palette, paint_fn, draw_std_lenses, outline_color)
COSTUMES = [
    ("skin_pirate",     "PIRATE",     "standard", None,        _paint_pirate,    False, None),
    ("skin_cowboy",     "COWBOY",     "standard", None,        _paint_cowboy,    False, None),
    ("skin_pharaoh",    "PHARAOH",    "standard", None,        _paint_pharaoh,   False, None),
    ("skin_crown",      "CROWN",      "standard", None,        _paint_crown,     False, None),
    ("skin_baseball",   "BASEBALL",   "standard", None,        _paint_baseball,  False, None),
    ("skin_tennis",     "TENNIS",     "standard", None,        _paint_tennis,    False, None),
    ("skin_wizard",     "WIZARD",     "standard", None,        _paint_wizard,    False, None),
    ("skin_basketball", "BASKETBALL", "standard", None,        _paint_laker,     False, None),
    ("skin_tophat",     "GENTLEMAN",  "palette",  _TH_BODY,    _paint_tophat,    False, None),
    ("skin_ninja",      "NINJA",      "palette",  P_NINJA,     _paint_ninja,     False, None),
    ("skin_mummy",      "MUMMY",      "palette",  _MU_BODY,    _paint_mummy,     False, None, True),
    ("skin_astronaut",  "ASTRONAUT",  "palette",  P_ASTRONAUT, _paint_astronaut, False, None),
    ("skin_pilot",      "CAPTAIN",    "palette",  P_PILOT,     _paint_pilot,     True,  None),
    ("skin_viking",     "VIKING",     "viking",   _VK_PAL,     None,             False, _VK_OUTLINE),
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


def _ghost_tint(img):
    """Spectral-blue luminance remap in-place; handles SRCALPHA."""
    arr = sa.pixels3d(img)
    f = arr.astype(np.float32)
    lum = f[:, :, 0] * 0.299 + f[:, :, 1] * 0.587 + f[:, :, 2] * 0.114
    lum_n = lum / 255.0
    dark   = np.array([50,  95, 145], np.float32)
    bright = np.array([200, 230, 245], np.float32)
    for c in range(3):
        f[:, :, c] = dark[c] + lum_n * (bright[c] - dark[c])
    arr[:] = f.clip(0, 255).astype(np.uint8)
    del arr
    if img.get_flags() & pygame.SRCALPHA:
        alpha = sa.pixels_alpha(img)
        alpha[:] = (alpha.astype(np.float32) * (170 / 255)).clip(0, 255).astype(np.uint8)
        del alpha
    else:
        img.set_alpha(170)


def _poison_tint(img):
    """Chartreuse luminance remap in-place."""
    arr = sa.pixels3d(img)
    f = arr.astype(np.float32)
    lum = f[:, :, 0] * 0.299 + f[:, :, 1] * 0.587 + f[:, :, 2] * 0.114
    lum_n = lum / 255.0
    dark   = np.array([30,  75, 10], np.float32)
    bright = np.array([200, 240, 75], np.float32)
    for c in range(3):
        f[:, :, c] = dark[c] + lum_n * (bright[c] - dark[c])
    arr[:] = f.clip(0, 255).astype(np.uint8)
    del arr


# ── raw composite builder (unoutlined 64×100) ─────────────────────────────────

def _build_costume_raw_comp(base_type, palette, paint_fn, draw_std_lenses, lives_state,
                            damage_over_costume=False):
    """Return an unoutlined 64×100 SRCALPHA composite with dressings applied."""
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)

    if base_type == "standard":
        if lives_state == "clean":
            comp.blit(_build_frame(10.0), (0, PARROT_DY))
        elif lives_state == "first_hit":
            comp.blit(_fh_build_hurt_frame(10.0), (0, PARROT_DY))
        else:
            comp.blit(_h_build_hurt_frame(10.0), (0, PARROT_DY))
        if paint_fn:
            paint_fn(comp, 10.0)

    elif base_type == "palette":
        if lives_state == "clean":
            comp.blit(_build_parrot_with_palette(10.0, palette), (0, PARROT_DY))
            if paint_fn:
                paint_fn(comp, 10.0)
        else:
            comp.blit(_build_parrot_with_palette(10.0, palette, draw_lenses=False), (0, PARROT_DY))
            sprite = comp.subsurface((0, PARROT_DY, 64, 60))
            if lives_state == "first_hit":
                if damage_over_costume and paint_fn:
                    paint_fn(comp, 10.0)
                _h_draw_bandaids(sprite)
                if draw_std_lenses:
                    _draw_lenses(sprite, 50, 20, palette)
                _fh_draw_single_crack(sprite)
                if not damage_over_costume and paint_fn:
                    paint_fn(comp, 10.0)
            else:
                if damage_over_costume and paint_fn:
                    paint_fn(comp, 10.0)
                _h_draw_bandaids(sprite)
                _h_draw_headwrap(sprite)
                _h_draw_chest_dressing(sprite)
                _h_draw_ragged_cuts(sprite)
                if draw_std_lenses:
                    _draw_lenses(sprite, 50, 20, palette)
                _h_draw_cracked_lens(sprite)
                if not damage_over_costume and paint_fn:
                    paint_fn(comp, 10.0)

    else:  # viking
        if lives_state == "clean":
            _viking_axe(comp)
            comp.blit(_viking_base(10.0), (0, PARROT_DY))
            _viking_back(comp)
            _viking_helm(comp)
            _viking_face(comp)
        else:
            body = _build_parrot_with_palette(10.0, _VK_PAL, draw_lenses=False)
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

    return comp


def _build_costume_normal(base_type, palette, paint_fn, draw_std_lenses, outline_color, lives_state,
                          damage_over_costume=False):
    comp = _build_costume_raw_comp(base_type, palette, paint_fn, draw_std_lenses, lives_state,
                                   damage_over_costume)
    kw = {"outline_color": outline_color} if outline_color else {}
    return _add_outline(comp, **kw)


def _build_costume_triple(base_type, palette, paint_fn, draw_std_lenses, outline_color, lives_state,
                          damage_over_costume=False):
    comp = _build_costume_raw_comp(base_type, palette, paint_fn, draw_std_lenses, lives_state,
                                   damage_over_costume)
    draw_stovepipe(comp, HAT_HX, HAT_HY)
    kw = {"outline_color": outline_color} if outline_color else {}
    return _add_outline(comp, **kw)


def _build_costume_poison(base_type, palette, paint_fn, draw_std_lenses, outline_color, lives_state,
                          damage_over_costume=False):
    """Chartreuse parrot body for all skin types; costume accessories (hat, epaulette, etc.)
    keep their original colours via paint_fn.  Lens frames are omitted — X-eyes replace them,
    matching the base poison parrot appearance.  No _poison_tint needed — P_CHARTREUSE already
    matches get_poisoned_parrot's beak/foot colours."""
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)

    if base_type in ("standard", "palette"):
        comp.blit(_build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False), (0, PARROT_DY))
        sprite = comp.subsurface((0, PARROT_DY, 64, 60))
        if lives_state == "last_life":
            if damage_over_costume and paint_fn:
                paint_fn(comp, 10.0)
            _h_draw_bandaids(sprite)
            _h_draw_headwrap(sprite)
            _h_draw_chest_dressing(sprite)
            _h_draw_ragged_cuts(sprite)
            _h_draw_cracked_lens(sprite)
            if not damage_over_costume and paint_fn:
                paint_fn(comp, 10.0)
        elif lives_state == "first_hit":
            if damage_over_costume and paint_fn:
                paint_fn(comp, 10.0)
            _h_draw_bandaids(sprite)
            _fh_draw_single_crack(sprite)
            if not damage_over_costume and paint_fn:
                paint_fn(comp, 10.0)
        else:  # clean
            if paint_fn:
                paint_fn(comp, 10.0)
        _draw_b_x_eyes(sprite)
        return _add_outline(comp)

    else:  # viking
        _viking_axe(comp)
        comp.blit(_build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False), (0, PARROT_DY))
        _viking_back(comp)
        sprite = comp.subsurface((0, PARROT_DY, 64, 60))
        if lives_state != "clean":
            _h_draw_bandaids(sprite)
        if lives_state == "last_life":
            _h_draw_headwrap(sprite)
        _viking_helm(comp)
        _viking_face(comp)
        if lives_state == "first_hit":
            _fh_draw_single_crack(sprite)
        elif lives_state == "last_life":
            _h_draw_chest_dressing(sprite)
            _h_draw_ragged_cuts(sprite)
            _h_draw_cracked_lens(sprite)
        _draw_b_x_eyes(sprite)
        kw = {"outline_color": outline_color} if outline_color else {}
        return _add_outline(comp, **kw)


# ── cell renderer ──────────────────────────────────────────────────────────────

def render_cell(skin_id, base_type, palette, paint_fn, draw_std_lenses,
                outline_color, lives_state, effect, damage_over_costume=False):
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)
    is_hurt = (lives_state != "clean")

    if effect == "normal":
        img = _build_costume_normal(base_type, palette, paint_fn, draw_std_lenses,
                                    outline_color, lives_state, damage_over_costume)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("normal")
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    if effect == "ghost":
        img = _build_costume_normal(base_type, palette, paint_fn, draw_std_lenses,
                                    outline_color, lives_state, damage_over_costume).copy()
        _ghost_tint(img)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("ghost").copy()
            par.set_alpha(170)
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    if effect == "triple":
        img = _build_costume_triple(base_type, palette, paint_fn, draw_std_lenses,
                                    outline_color, lives_state, damage_over_costume)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("normal")
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    if effect == "ghost_triple":
        img = _build_costume_triple(base_type, palette, paint_fn, draw_std_lenses,
                                    outline_color, lives_state, damage_over_costume).copy()
        _ghost_tint(img)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("ghost").copy()
            par.set_alpha(170)
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    if effect == "grow":
        img = _build_costume_normal(base_type, palette, paint_fn, draw_std_lenses,
                                    outline_color, lives_state, damage_over_costume)
        img = pygame.transform.smoothscale(
            img, (int(img.get_width() * GROW_SCALE), int(img.get_height() * GROW_SCALE)))
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("normal").copy()
            pw, ph = par.get_size()
            par = pygame.transform.smoothscale(par, (int(pw * GROW_SCALE), int(ph * GROW_SCALE)))
            cell.blit(par, par.get_rect(
                center=(CELL_W // 2, BIRD_Y + int(PARCEL_Y_OFFSET * GROW_SCALE))))
        return cell

    if effect == "poison":
        img = _build_costume_poison(base_type, palette, paint_fn, draw_std_lenses,
                                    outline_color, lives_state, damage_over_costume)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("normal")
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    if effect == "kfc":
        img = get_fried_parrot(1, 0.0)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("kfc")
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    if effect == "skateboard":
        global _HELMET_CACHE, _BOARD_CACHE
        if _HELMET_CACHE is None:
            _HELMET_CACHE = Bird._build_helmet_sprite()
        if _BOARD_CACHE is None:
            _BOARD_CACHE, _ = Bird._build_board_base()
        bird_cx, bird_cy = CELL_W // 2, BIRD_Y
        # Board below feet first
        cell.blit(_BOARD_CACHE, _BOARD_CACHE.get_rect(
            center=(bird_cx, bird_cy + PARCEL_Y_OFFSET + 4)))
        # Lives-aware costume sprite
        img = _build_costume_normal(base_type, palette, paint_fn, draw_std_lenses,
                                    outline_color, lives_state)
        cell.blit(img, img.get_rect(center=(bird_cx, bird_cy)))
        # Punk skull-bunny helmet above head
        # At s=1.0, tilt=0, flipped=False: Vector2(18, -10 + (-18/2)) = (18, -19)
        cell.blit(_HELMET_CACHE, _HELMET_CACHE.get_rect(center=(bird_cx + 18, bird_cy - 19)))
        return cell

    return cell


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    n_skins = len(COSTUMES)
    n_cols  = len(COLS)

    total_h = MARGIN + HDR_H + n_skins * 3 * CELL_H + (n_skins - 1) * SKIN_DIV + MARGIN
    total_w = MARGIN + LABEL_W + n_cols * CELL_W + MARGIN

    canvas = pygame.Surface((total_w, total_h))
    canvas.fill(BG)

    fnt_title  = pygame.font.SysFont("monospace", 13, bold=True)
    fnt_hdr    = pygame.font.SysFont("monospace", 10, bold=True)
    fnt_label  = pygame.font.SysFont("monospace",  9, bold=True)
    fnt_sublbl = pygame.font.SysFont("monospace",  8, bold=False)

    title = fnt_title.render("STORE COSTUMES × POWERUP × LIVES STATE", True, TEXT_COL)
    canvas.blit(title, title.get_rect(center=(total_w // 2, MARGIN + HDR_H // 2)))

    for ci, col_label in enumerate(COLS):
        cx = MARGIN + LABEL_W + ci * CELL_W + CELL_W // 2
        surf = fnt_hdr.render(col_label, True, TEXT_COL)
        canvas.blit(surf, surf.get_rect(center=(cx, MARGIN + HDR_H // 2)))

    for si, costume in enumerate(COSTUMES):
        skin_id, display_name, base_type, palette, paint_fn, draw_std_lenses, outline_color = costume[:7]
        damage_over_costume = len(costume) > 7 and costume[7]

        group_top = MARGIN + HDR_H + si * (3 * CELL_H + SKIN_DIV)

        if si > 0:
            div_y = group_top - SKIN_DIV
            pygame.draw.rect(canvas, DIV_COL,
                             (MARGIN, div_y, total_w - 2 * MARGIN, SKIN_DIV))

        for ri, (row_label, row_key) in enumerate(zip(ROWS, ROW_KEYS)):
            row_top = group_top + ri * CELL_H

            label_rect = pygame.Rect(MARGIN, row_top, LABEL_W, CELL_H)
            pygame.draw.rect(canvas, LABEL_BG, label_rect)

            if ri == 0:
                lbl = fnt_label.render(display_name, True, TEXT_COL)
                canvas.blit(lbl, lbl.get_rect(
                    center=(MARGIN + LABEL_W // 2, row_top + CELL_H // 2 - 8)))
            sub = fnt_sublbl.render(row_label, True, DIM_COL)
            canvas.blit(sub, sub.get_rect(
                center=(MARGIN + LABEL_W // 2, row_top + CELL_H // 2 + 8)))

            for ci, effect in enumerate(COL_KEYS):
                cell_x = MARGIN + LABEL_W + ci * CELL_W
                cell = render_cell(skin_id, base_type, palette, paint_fn,
                                   draw_std_lenses, outline_color, row_key, effect,
                                   damage_over_costume)
                canvas.blit(cell, (cell_x, row_top))
                pygame.draw.rect(canvas, BG, (cell_x, row_top, CELL_W, 1))
                pygame.draw.rect(canvas, BG, (cell_x, row_top, 1, CELL_H))

    pygame.draw.rect(canvas, (60, 65, 85), canvas.get_rect(), 2)

    import glob as _glob, re as _re
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    existing = _glob.glob(os.path.join(docs_dir, "costume_powerup_lives_grid_v*.png"))
    versions = [int(m.group(1)) for f in existing
                for m in [_re.search(r'_v(\d+)\.png$', f)] if m]
    next_v = max(versions, default=0) + 1
    out_path = os.path.join(docs_dir, f"costume_powerup_lives_grid_v{next_v}.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {total_w}×{total_h} → {out_path}")
    pygame.quit()


if __name__ == "__main__":
    main()
