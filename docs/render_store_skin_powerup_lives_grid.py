"""
Render a grid: rows = store PARROT-tab skins × 3 life states,
               columns = powerup effects (Normal, Ghost, Triple, Gst+Trpl, Grow, Poison).

Output: docs/parrot_skin_powerup_lives_grid.png
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame
import pygame.surfarray as sa
pygame.init()
pygame.font.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.parrot as _parrot
from game.parrot import (
    _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
    _h_draw_ragged_cuts, _h_draw_cracked_lens, _fh_draw_single_crack,
    _add_outline, get_parcel,
)
from game.dollar_parrot_ghost import _build_parrot_with_palette, P_SPECTRAL, _draw_lenses
from game.dollar_parrot_dead import P_CHARTREUSE, _draw_b_x_eyes
from game.dollar_parrot_hat import (
    draw_stovepipe, draw_stovepipe_ghost,
    COMPOSITE_W, COMPOSITE_H, HAT_HX, HAT_HY,
)
from game.config import GROW_SCALE, PARCEL_Y_OFFSET
from game.store_skins import (
    PARROT_DY,
    P_DISCO, P_BLUEGOLD, P_AMAZON, P_SUNCONURE, P_HYACINTH,
    P_COCKATOO, P_LORIKEET, P_PRISM, P_THORNCREST, P_EMBERMOTH,
    _AURORA_PAL, P_MOONBLOOM, P_TEMPEST, P_BINKY, P_CHROME,
    _build_voodoo_zombie,
    _paint_disco, _paint_cockatoo_crest, _paint_prism,
    _paint_thorncrest, _paint_embermoth, _paint_binky,
    _aurora_front,    _aurora_back,
    _moonbloom_front, _moonbloom_back, _MB_OUTLINE,
    _tempest_front,   _tempest_back,   _TP_OUTLINE,
    _chrome_front,    _chrome_back,
    _zb_hex_aura, _zb_rim_halo,
    _ZB_STITCH, _ZB_CURSED, _ZB_CURSED_H,
)
from game.skeleton_skin import _flesh_base, _paint as _skeleton_paint, _eye_socket

# ── layout ────────────────────────────────────────────────────────────────────
LABEL_W  = 150
CELL_W   = 100
CELL_H   = 130
HDR_H    = 48
MARGIN   = 12
SKIN_DIV = 6       # separator height between skin groups
BIRD_Y   = 46

BG       = (22, 26, 36)
LABEL_BG = (32, 36, 50)
DIV_COL  = (45, 50, 68)
TEXT_COL = (220, 220, 230)
DIM_COL  = (130, 130, 150)
SKY_TOP  = (80, 130, 210)
SKY_BOT  = (100, 150, 200)

COLS     = ["Normal", "Ghost", "Triple", "Gst+Trpl", "Grow", "Poison"]
COL_KEYS = ["normal", "ghost", "triple", "ghost_triple", "grow", "poison"]

ROWS     = ["CLEAN", "FIRST-HIT", "LAST-LIFE"]
ROW_KEYS = ["clean", "first_hit", "last_life"]

# Skin table — identical to render_store_parrot_lives_grid.py
# (skin_id, display_name, palette, paint_fn, back_fn, outline_color, draw_std_lenses, special)
SKINS = [
    ("skin_skeleton",   "SKELETON",   None,        None,                  None,            None,        True,  "skeleton"),
    ("skin_zombie",     "ZOMBIE",     None,        None,                  None,            None,        True,  "zombie"),
    ("skin_disco",      "DISCO",      P_DISCO,     _paint_disco,          None,            None,        True,  None),
    ("skin_bluegold",   "BLUE MACAW", P_BLUEGOLD,  None,                  None,            None,        True,  None),
    ("skin_amazon",     "AMAZON",     P_AMAZON,    None,                  None,            None,        True,  None),
    ("skin_sunconure",  "SUN CONURE", P_SUNCONURE, None,                  None,            None,        True,  None),
    ("skin_hyacinth",   "HYACINTH",   P_HYACINTH,  None,                  None,            None,        True,  None),
    ("skin_cockatoo",   "COCKATOO",   P_COCKATOO,  None,                  _paint_cockatoo_crest, None,  True,  None),
    ("skin_lorikeet",   "LORIKEET",   P_LORIKEET,  None,                  None,            None,        True,  None),
    ("skin_prism",      "PRISM",      P_PRISM,     _paint_prism,          None,            None,        True,  None),
    ("skin_thorncrest", "THORNCREST", P_THORNCREST,_paint_thorncrest,     None,            None,        True,  None),
    ("skin_embermoth",  "EMBERMOTH",  P_EMBERMOTH, _paint_embermoth,      None,            None,        True,  None),
    ("skin_aurora",     "AURORA",     _AURORA_PAL, _aurora_front,         _aurora_back,    None,        True,  None),
    ("skin_moonbloom",  "MOONBLOOM",  P_MOONBLOOM, _moonbloom_front,      _moonbloom_back, _MB_OUTLINE, True,  None),
    ("skin_tempest",    "TEMPEST",    P_TEMPEST,   _tempest_front,        _tempest_back,   _TP_OUTLINE, True,  None),
    ("skin_binky",      "BINKY",      P_BINKY,     _paint_binky,          None,            None,        True,  None),
    ("skin_chrome",     "CHROME",     P_CHROME,    _chrome_front,         _chrome_back,    None,        False, None),
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


def _open_beak(surf, P):
    """Split two-polygon beak for hurt states (open mouth look)."""
    beak_lo = tuple(int(c * 0.87) for c in P['beak_main'])
    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    pygame.draw.polygon(surf, P['beak_main'], upper)
    pygame.draw.polygon(surf, P['beak_dark'], upper, 1)
    pygame.draw.polygon(surf, beak_lo, lower)
    pygame.draw.polygon(surf, P['beak_dark'], lower, 1)
    pygame.draw.line(surf, P['beak_gloss'], (55, 22), (59, 24), 1)


def _composite_with_back(comp, back_fn, outline_color):
    """Outline comp, composite back_fn behind it, return final surface."""
    kw = {"outline_color": outline_color} if outline_color else {}
    bird = _add_outline(comp, **kw)
    if back_fn is None:
        return bird
    pad = (bird.get_width() - 64) // 2
    result = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
    back = pygame.Surface((64, 100), pygame.SRCALPHA)
    back_fn(back, 10.0)
    result.blit(back, (pad, pad))
    result.blit(bird, (0, 0))
    return result


def _ghost_tint(img):
    """Colorize to spectral-blue preserving per-pixel luminance; handles SRCALPHA."""
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
    """Chartreuse luminance remap in-place; handles SRCALPHA."""
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


def _build_poison_hurt(lives_state):
    """Chartreuse macaw + lives dressings + X-eyes. For no-element skins."""
    if lives_state == "last_life":
        base = _build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False)
        _h_draw_bandaids(base)
        _h_draw_headwrap(base)
        _h_draw_chest_dressing(base)
        _h_draw_ragged_cuts(base)
        _h_draw_cracked_lens(base)
    else:
        base = _build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False)
        _h_draw_bandaids(base)
        _fh_draw_single_crack(base)
    _draw_b_x_eyes(base)
    return _add_outline(base)


def _build_poison_skin(palette, paint_fn, back_fn, outline_color, draw_std_lenses,
                       special, lives_state):
    """Poison visual for element skins: P_CHARTREUSE body + skin accessories + X-eyes."""
    if special == "skeleton":
        comp = pygame.Surface((64, 100), pygame.SRCALPHA)
        body = _build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False)
        comp.blit(body, (0, PARROT_DY))
        _skeleton_paint(comp, 10.0)
        _poison_tint(comp)
        sprite = comp.subsurface((0, PARROT_DY, 64, 60))
        if lives_state == "clean":
            _eye_socket(comp)
        elif lives_state == "first_hit":
            _h_draw_bandaids(sprite)
            _fh_draw_single_crack(sprite)
        else:
            _h_draw_bandaids(sprite)
            _h_draw_headwrap(sprite)
            _eye_socket(comp)
            _h_draw_chest_dressing(sprite)
            _h_draw_ragged_cuts(sprite)
        _draw_b_x_eyes(sprite)
        return _add_outline(comp)

    if special == "zombie":
        base = _build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False)
        if lives_state == "first_hit":
            _h_draw_bandaids(base)
            _fh_draw_single_crack(base)
        elif lives_state == "last_life":
            _h_draw_bandaids(base)
            _h_draw_headwrap(base)
            _h_draw_chest_dressing(base)
            _h_draw_ragged_cuts(base)
        _draw_b_x_eyes(base)
        core = _add_outline(base)
        pad = 16
        cw, ch = core.get_size()
        out = pygame.Surface((cw + pad * 2, ch + pad * 2), pygame.SRCALPHA)
        _zb_hex_aura(out, out.get_width() // 2, out.get_height() // 2 + 4,
                     max(cw, ch) // 2 + 6)
        _poison_tint(out)
        ring = _zb_rim_halo(core)
        out.blit(ring, (pad - 2, pad - 2))
        out.blit(core, (pad, pad))
        return out

    # Standard composite skins: chartreuse base + paint_fn + back_fn
    is_last = (lives_state == "last_life")
    body = _build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, 10.0)
    _poison_tint(comp)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    if lives_state == "last_life":
        _h_draw_bandaids(sprite)
        _h_draw_headwrap(sprite)
        _h_draw_chest_dressing(sprite)
        _h_draw_ragged_cuts(sprite)
        _h_draw_cracked_lens(sprite)
    elif lives_state == "first_hit":
        _h_draw_bandaids(sprite)
        _fh_draw_single_crack(sprite)
    _draw_b_x_eyes(sprite)

    kw = {"outline_color": outline_color} if outline_color else {}
    outlined = _add_outline(comp, **kw)
    if back_fn is None:
        return outlined
    pad = (outlined.get_width() - 64) // 2
    result = pygame.Surface(outlined.get_size(), pygame.SRCALPHA)
    back = pygame.Surface((64, 100), pygame.SRCALPHA)
    back_fn(back, 10.0)
    _poison_tint(back)
    result.blit(back, (pad, pad))
    result.blit(outlined, (0, 0))
    return result


# ── skin raw composite (unoutlined, for hat insertion) ────────────────────────

def _build_skin_raw_comp(palette, paint_fn, draw_std_lenses, lives_state, angle=10.0):
    """Build an unoutlined 64×100 SRCALPHA composite with skin accessories
    and lives dressings applied.  back_fn is NOT applied — caller handles it
    after outlining (same flow as _composite_with_back)."""
    if lives_state == "clean":
        body = _build_parrot_with_palette(angle, palette)
        comp = pygame.Surface((64, 100), pygame.SRCALPHA)
        comp.blit(body, (0, PARROT_DY))
        if paint_fn:
            paint_fn(comp, angle)
        return comp

    is_last = (lives_state == "last_life")
    body = _build_parrot_with_palette(
        angle, palette, draw_lenses=(not is_last) and draw_std_lenses)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, angle)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    if is_last:
        _h_draw_bandaids(sprite)
        _h_draw_headwrap(sprite)
        if draw_std_lenses:
            _draw_lenses(sprite, 50, 20, palette)
        _open_beak(sprite, palette)
        _h_draw_chest_dressing(sprite)
        _h_draw_ragged_cuts(sprite)
        _h_draw_cracked_lens(sprite)
    else:
        _open_beak(sprite, palette)
        _h_draw_bandaids(sprite)
        _fh_draw_single_crack(sprite)
    return comp


# ── "triple" (hat) cell builders ──────────────────────────────────────────────

def _build_triple(palette, paint_fn, back_fn, outline_color, draw_std_lenses,
                  special, lives_state):
    """Hat composite for the 'triple' effect column, per skin + lives state."""
    if special == "skeleton":
        comp = pygame.Surface((64, 100), pygame.SRCALPHA)
        comp.blit(_flesh_base(10.0), (0, PARROT_DY))
        _skeleton_paint(comp, 10.0)
        sprite = comp.subsurface((0, PARROT_DY, 64, 60))
        if lives_state == "first_hit":
            _h_draw_bandaids(sprite)
            _fh_draw_single_crack(sprite)
        elif lives_state == "last_life":
            _h_draw_bandaids(sprite)
            _h_draw_headwrap(sprite)
            _eye_socket(comp)
            _h_draw_chest_dressing(sprite)
            _h_draw_ragged_cuts(sprite)
        draw_stovepipe(comp, HAT_HX, HAT_HY)
        return _add_outline(comp)

    if special == "zombie":
        base = _build_voodoo_zombie(10.0)
        if lives_state == "first_hit":
            _h_draw_bandaids(base)
            _fh_draw_single_crack(base)
        elif lives_state == "last_life":
            _h_draw_bandaids(base)
            _h_draw_headwrap(base)
            pygame.draw.line(base, _ZB_STITCH, (41, 21), (47, 21), 2)
            for vx in (42, 44, 46):
                pygame.draw.line(base, _ZB_STITCH, (vx, 19), (vx, 23), 1)
            _zb_hex_aura(base, 50, 19, 7)
            pygame.draw.circle(base, _ZB_STITCH, (50, 19), 5)
            pygame.draw.circle(base, _ZB_CURSED, (50, 19), 4)
            pygame.draw.circle(base, _ZB_CURSED_H, (49, 18), 1)
            _h_draw_chest_dressing(base)
            _h_draw_ragged_cuts(base)
        comp = pygame.Surface((64, 100), pygame.SRCALPHA)
        comp.blit(base, (0, PARROT_DY))
        draw_stovepipe(comp, HAT_HX, HAT_HY)
        core = _add_outline(comp)
        pad = 16
        cw, ch = core.get_size()
        out = pygame.Surface((cw + pad * 2, ch + pad * 2), pygame.SRCALPHA)
        _zb_hex_aura(out, out.get_width() // 2, out.get_height() // 2 + 4,
                     max(cw, ch) // 2 + 6)
        ring = _zb_rim_halo(core)
        out.blit(ring, (pad - 2, pad - 2))
        out.blit(core, (pad, pad))
        return out

    # Standard palette / composite skins
    comp = _build_skin_raw_comp(palette, paint_fn, draw_std_lenses, lives_state)
    draw_stovepipe(comp, HAT_HX, HAT_HY)
    kw = {"outline_color": outline_color} if outline_color else {}
    outlined = _add_outline(comp, **kw)
    if back_fn is None:
        return outlined
    pad = (outlined.get_width() - 64) // 2
    result = pygame.Surface(outlined.get_size(), pygame.SRCALPHA)
    back = pygame.Surface((64, 100), pygame.SRCALPHA)
    back_fn(back, 10.0)
    result.blit(back, (pad, pad))
    result.blit(outlined, (0, 0))
    return result




# ── cell renderer ──────────────────────────────────────────────────────────────

def render_cell(skin_id, palette, paint_fn, back_fn, outline_color,
                draw_std_lenses, special, lives_state, effect):
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)
    is_hurt = (lives_state != "clean")

    # ── normal ──
    if effect == "normal":
        if lives_state == "clean":
            img = _parrot.get_skin_frame(skin_id, 1, 0.0)
        elif lives_state == "first_hit":
            img = _parrot.get_skin_first_hit_frame(skin_id, 1, 0.0)
        else:
            img = _parrot.get_skin_hurt_frame(skin_id, 1, 0.0)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("normal")
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    # ── ghost (skin-aware: tint each skin's own frame to spectral) ──
    if effect == "ghost":
        if lives_state == "clean":
            img = _parrot.get_skin_frame(skin_id, 1, 0.0).copy()
        elif lives_state == "first_hit":
            img = _parrot.get_skin_first_hit_frame(skin_id, 1, 0.0).copy()
        else:
            img = _parrot.get_skin_hurt_frame(skin_id, 1, 0.0).copy()
        _ghost_tint(img)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("ghost").copy()
            par.set_alpha(170)
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    # ── triple (hat + skin) ──
    if effect == "triple":
        img = _build_triple(palette, paint_fn, back_fn, outline_color,
                            draw_std_lenses, special, lives_state)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("normal")
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    # ── ghost_triple (skin-aware: triple build + tint) ──
    if effect == "ghost_triple":
        img = _build_triple(palette, paint_fn, back_fn, outline_color,
                            draw_std_lenses, special, lives_state).copy()
        _ghost_tint(img)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("ghost").copy()
            par.set_alpha(170)
            cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    # ── grow (scale skin's frame by GROW_SCALE) ──
    if effect == "grow":
        if lives_state == "clean":
            raw = _parrot.get_skin_frame(skin_id, 1, 0.0)
        elif lives_state == "first_hit":
            raw = _parrot.get_skin_first_hit_frame(skin_id, 1, 0.0)
        else:
            raw = _parrot.get_skin_hurt_frame(skin_id, 1, 0.0)
        img = pygame.transform.smoothscale(
            raw, (int(raw.get_width() * GROW_SCALE), int(raw.get_height() * GROW_SCALE)))
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        if is_hurt:
            par = get_parcel("normal").copy()
            pw, ph = par.get_size()
            par = pygame.transform.smoothscale(
                par, (int(pw * GROW_SCALE), int(ph * GROW_SCALE)))
            cell.blit(par, par.get_rect(
                center=(CELL_W // 2, BIRD_Y + int(PARCEL_Y_OFFSET * GROW_SCALE))))
        return cell

    # ── poison: chartreuse macaw base; element skins add their accessories ──
    if effect == "poison":
        has_elements = (paint_fn is not None or back_fn is not None
                        or special is not None)
        if not has_elements:
            if lives_state == "clean":
                img = _parrot.get_poisoned_parrot(1, 0.0)
            else:
                img = _build_poison_hurt(lives_state)
        else:
            img = _build_poison_skin(palette, paint_fn, back_fn, outline_color,
                                     draw_std_lenses, special, lives_state)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        return cell

    return cell


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    n_skins = len(SKINS)
    n_cols  = len(COLS)

    # Total height: HDR + (3 rows per skin × CELL_H) + (skin_div between skins)
    total_h = MARGIN + HDR_H + n_skins * 3 * CELL_H + (n_skins - 1) * SKIN_DIV + MARGIN
    total_w = MARGIN + LABEL_W + n_cols * CELL_W + MARGIN

    canvas = pygame.Surface((total_w, total_h))
    canvas.fill(BG)

    fnt_title  = pygame.font.SysFont("monospace", 13, bold=True)
    fnt_hdr    = pygame.font.SysFont("monospace", 10, bold=True)
    fnt_label  = pygame.font.SysFont("monospace",  9, bold=True)
    fnt_sublbl = pygame.font.SysFont("monospace",  8, bold=False)

    # Title
    title = fnt_title.render("STORE PARROTS × POWERUP × LIVES STATE", True, TEXT_COL)
    canvas.blit(title, title.get_rect(center=(total_w // 2, MARGIN + HDR_H // 2)))

    # Column headers
    for ci, col_label in enumerate(COLS):
        cx = MARGIN + LABEL_W + ci * CELL_W + CELL_W // 2
        surf = fnt_hdr.render(col_label, True, TEXT_COL)
        canvas.blit(surf, surf.get_rect(center=(cx, MARGIN + HDR_H // 2)))

    # Skin groups
    for si, (skin_id, display_name, palette, paint_fn, back_fn,
             outline_color, draw_std_lenses, special) in enumerate(SKINS):

        group_top = MARGIN + HDR_H + si * (3 * CELL_H + SKIN_DIV)

        # Skin-group divider (not before first group)
        if si > 0:
            div_y = group_top - SKIN_DIV
            pygame.draw.rect(canvas, DIV_COL, (MARGIN, div_y, total_w - 2 * MARGIN, SKIN_DIV))

        for ri, (row_label, row_key) in enumerate(zip(ROWS, ROW_KEYS)):
            row_top = group_top + ri * CELL_H

            # Label column
            label_rect = pygame.Rect(MARGIN, row_top, LABEL_W, CELL_H)
            pygame.draw.rect(canvas, LABEL_BG, label_rect)

            # Skin name on the first row of the group
            if ri == 0:
                lbl = fnt_label.render(display_name, True, TEXT_COL)
                canvas.blit(lbl, lbl.get_rect(
                    center=(MARGIN + LABEL_W // 2, row_top + CELL_H // 2 - 8)))
            sub = fnt_sublbl.render(row_label, True, DIM_COL)
            canvas.blit(sub, sub.get_rect(
                center=(MARGIN + LABEL_W // 2, row_top + CELL_H // 2 + 8)))

            # Cells
            for ci, effect in enumerate(COL_KEYS):
                cell_x = MARGIN + LABEL_W + ci * CELL_W
                cell = render_cell(skin_id, palette, paint_fn, back_fn, outline_color,
                                   draw_std_lenses, special, row_key, effect)
                canvas.blit(cell, (cell_x, row_top))
                # Grid lines
                pygame.draw.rect(canvas, BG, (cell_x, row_top, CELL_W, 1))
                pygame.draw.rect(canvas, BG, (cell_x, row_top, 1, CELL_H))

    pygame.draw.rect(canvas, (60, 65, 85), canvas.get_rect(), 2)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "parrot_skin_powerup_lives_grid.png")
    pygame.image.save(canvas, out_path)
    print(f"Saved {total_w}×{total_h} → {out_path}")
    pygame.quit()


if __name__ == "__main__":
    main()
