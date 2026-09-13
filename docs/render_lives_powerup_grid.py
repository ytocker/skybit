"""Render a 3-row × 11-column grid: lives states × power-up appearances.

Each row is one of the three lives phases (Clean / First-hit / Last-life).
Each column is one power-up visual effect applied on top of that lives state.

Run headlessly:
    SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=offscreen python docs/render_lives_powerup_grid.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "offscreen")

import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.entities import Bird

# ── Grid geometry ─────────────────────────────────────────────────────────────

LABEL_W = 140
CELL_W   = 100
CELL_H   = 130
HDR_H    = 48
MARGIN   = 12

BG       = (22, 26, 36)
LABEL_BG = (32, 36, 50)
TEXT_COL = (220, 220, 230)
DIM_COL  = (130, 130, 150)

SKY_TOP  = (80, 130, 210)
SKY_BOT  = (100, 150, 200)

# ── Content definition ────────────────────────────────────────────────────────

ROWS = [
    ("CLEAN\n(2 lives)", "clean"),
    ("FIRST HIT\n(1 life)",  "first_hit"),
    ("LAST LIFE\n(0 lives)", "last_life"),
]

COLS = [
    ("Normal",    "normal"),
    ("KFC",       "kfc"),
    ("Ghost",     "ghost"),
    ("Triple",    "triple"),
    ("KFC+Ghost", "kfc_ghost"),
    ("KFC+Triple","kfc_triple"),
    ("Gst+Trpl",  "ghost_triple"),
    ("Skateboard","skateboard"),
    ("Grow",      "grow"),
    ("Shrink",    "shrink"),
    ("Poison",    "poison"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def fill_sky(surf: pygame.Surface):
    w, h = surf.get_size()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w - 1, y))


def make_font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("dejavusans,arial,sans", size, bold=bold)


BIRD_Y      = 46   # bird center y within cell — pushed up so board/parcel fit
BOARD_EXTRA = 20   # extra cell height added when skateboard is active

def configure_bird(b: Bird, lives_state: str, effect: str):
    """Apply lives-state flags and power-up flags to a fresh Bird."""
    b.frame_t  = 1.0
    b.x        = CELL_W / 2
    b.y        = BIRD_Y
    b.lives_flicker_visible = True

    if lives_state == "first_hit":
        b.on_first_hit = True
    elif lives_state == "last_life":
        b.on_last_life = True

    if effect == "kfc":
        b.kfc_active = True
    elif effect == "ghost":
        b.ghost_active = True
        b.ghost_pulse  = math.pi / 2
    elif effect == "triple":
        b.triple_active = True
    elif effect == "kfc_ghost":
        b.kfc_active   = True
        b.ghost_active = True
        b.ghost_pulse  = math.pi / 2
    elif effect == "kfc_triple":
        b.kfc_active    = True
        b.triple_active = True
    elif effect == "ghost_triple":
        b.ghost_active  = True
        b.ghost_pulse   = math.pi / 2
        b.triple_active = True
    elif effect == "skateboard":
        b.skateboard_active = True
    elif effect == "grow":
        b.grow_active = True
    elif effect == "shrink":
        b.shrink_active = True
        b.shrink_scale  = 0.6
    # poison: no Bird flags — handled directly via get_poisoned_parrot


def render_cell(lives_state: str, effect: str) -> pygame.Surface:
    from game import parrot as _parrot

    # Ghost + lives skin: spectral blue base + lives dressings + ghost alpha.
    # draw_lenses=False for last_life so the headwrap is drawn BEFORE the lenses,
    # matching the draw order in _h_build_hurt_frame. Dressings are numpy-blended
    # toward the spectral palette so warm earthy tones go ghostly. Parcel drawn
    # separately (it is never part of any parrot sprite surface).
    if effect == "ghost" and lives_state != "clean":
        import numpy as np
        import pygame.surfarray as sa
        from game.dollar_parrot_ghost import _build_parrot_with_palette, P_SPECTRAL, _draw_lenses
        from game.parrot import (
            _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
            _h_draw_cracked_lens, _h_draw_ragged_cuts,
            _fh_draw_single_crack, _add_outline, get_parcel,
        )
        if lives_state == "last_life":
            base = _build_parrot_with_palette(10.0, P_SPECTRAL, draw_lenses=False)
            _h_draw_bandaids(base)
            _h_draw_headwrap(base)
            _draw_lenses(base, 50, 20, P_SPECTRAL)
            _h_draw_chest_dressing(base)
            _h_draw_ragged_cuts(base)
            _h_draw_cracked_lens(base)
        else:  # first_hit — no headwrap, lens draw order is fine
            base = _build_parrot_with_palette(10.0, P_SPECTRAL)
            _h_draw_bandaids(base)
            _fh_draw_single_crack(base)
        img = _add_outline(base)
        arr = sa.pixels3d(img)
        target = np.array([140, 200, 230], dtype=np.float32)
        arr[:] = (arr.astype(np.float32) * 0.60 + target * 0.40).clip(0, 255).astype(np.uint8)
        del arr
        img.set_alpha(170)
        cell = pygame.Surface((CELL_W, CELL_H))
        fill_sky(cell)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        par = get_parcel("ghost").copy()
        par.set_alpha(170)
        cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    # Ghost + Triple + lives: spectral blue base + lives dressings + ghost hat + tint + parcel.
    # Same pattern as ghost+lives but parrot is composited onto a taller canvas before the hat.
    if effect == "ghost_triple" and lives_state != "clean":
        import numpy as np
        import pygame.surfarray as sa
        from game.dollar_parrot_ghost import _build_parrot_with_palette, P_SPECTRAL, _draw_lenses
        from game.dollar_parrot_hat import (
            draw_stovepipe_ghost, COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY,
        )
        from game.parrot import (
            _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
            _h_draw_cracked_lens, _h_draw_ragged_cuts,
            _fh_draw_single_crack, _add_outline, get_parcel,
        )
        if lives_state == "last_life":
            base = _build_parrot_with_palette(10.0, P_SPECTRAL, draw_lenses=False)
            _h_draw_bandaids(base)
            _h_draw_headwrap(base)
            _draw_lenses(base, 50, 20, P_SPECTRAL)
            _h_draw_chest_dressing(base)
            _h_draw_ragged_cuts(base)
            _h_draw_cracked_lens(base)
        else:  # first_hit
            base = _build_parrot_with_palette(10.0, P_SPECTRAL)
            _h_draw_bandaids(base)
            _fh_draw_single_crack(base)
        canvas = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        canvas.blit(base, (0, PARROT_DY))
        draw_stovepipe_ghost(canvas, HAT_HX, HAT_HY)
        img = _add_outline(canvas)
        arr = sa.pixels3d(img)
        target = np.array([140, 200, 230], dtype=np.float32)
        arr[:] = (arr.astype(np.float32) * 0.60 + target * 0.40).clip(0, 255).astype(np.uint8)
        del arr
        img.set_alpha(170)
        cell = pygame.Surface((CELL_W, CELL_H))
        fill_sky(cell)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        par = get_parcel("ghost").copy()
        par.set_alpha(170)
        cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    # Grow + lives: hurt/first_hit frame scaled up by GROW_SCALE with scaled parcel.
    if effect == "grow" and lives_state != "clean":
        from game.parrot import _h_build_hurt_frame, _fh_build_hurt_frame, _add_outline, get_parcel
        from game.config import GROW_SCALE, PARCEL_Y_OFFSET
        raw_fn = _h_build_hurt_frame if lives_state == "last_life" else _fh_build_hurt_frame
        raw = raw_fn(10.0)
        img = _add_outline(raw)
        img = pygame.transform.smoothscale(
            img, (int(img.get_width() * GROW_SCALE), int(img.get_height() * GROW_SCALE)))
        cell = pygame.Surface((CELL_W, CELL_H))
        fill_sky(cell)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        par = get_parcel("normal").copy()
        pw, ph = par.get_size()
        par = pygame.transform.smoothscale(par, (int(pw * GROW_SCALE), int(ph * GROW_SCALE)))
        cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + int(PARCEL_Y_OFFSET * GROW_SCALE))))
        return cell

    # Triple (hat) + lives skin: build composite with lives sprite + stovepipe hat.
    # Uses the same canvas layout as build_hat_frames in dollar_parrot_hat.py.
    if effect == "triple" and lives_state != "clean":
        from game.parrot import _h_build_hurt_frame, _fh_build_hurt_frame, _add_outline, get_parcel
        from game.dollar_parrot_hat import (
            draw_stovepipe, COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY,
        )
        raw_fn = _h_build_hurt_frame if lives_state == "last_life" \
                 else _fh_build_hurt_frame
        raw = raw_fn(10.0)  # wing angle 10° = hero frame
        canvas = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        canvas.blit(raw, (0, PARROT_DY))
        draw_stovepipe(canvas, HAT_HX, HAT_HY)
        img = _add_outline(canvas)
        cell = pygame.Surface((CELL_W, CELL_H))
        fill_sky(cell)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        par = get_parcel("normal").copy()
        cell.blit(par, par.get_rect(center=(CELL_W // 2, BIRD_Y + 12)))
        return cell

    # Poison: clean → terminal chartreuse-dead sprite (no parcel, no shades);
    # lives → chartreuse palette base + lives dressings, also no shades and no parcel
    # to match the terminal dead look where X-eyes replace the aviators.
    if effect == "poison":
        cell = pygame.Surface((CELL_W, CELL_H))
        fill_sky(cell)
        if lives_state == "clean":
            img = _parrot.get_poisoned_parrot(1, 0.0)
        else:
            from game.dollar_parrot_ghost import _build_parrot_with_palette
            from game.dollar_parrot_dead import P_CHARTREUSE, _draw_b_x_eyes
            from game.parrot import (
                _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
                _h_draw_cracked_lens, _h_draw_ragged_cuts,
                _fh_draw_single_crack, _add_outline,
            )
            if lives_state == "last_life":
                base = _build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False)
                _h_draw_bandaids(base)
                _h_draw_headwrap(base)
                _h_draw_chest_dressing(base)
                _h_draw_ragged_cuts(base)
                _h_draw_cracked_lens(base)
            else:  # first_hit
                base = _build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False)
                _h_draw_bandaids(base)
                _fh_draw_single_crack(base)
            _draw_b_x_eyes(base)
            img = _add_outline(base)
            cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
            return cell
        cell.blit(img, img.get_rect(center=(CELL_W // 2, BIRD_Y)))
        return cell

    # Skateboard board extends below the parcel y-offset; give it extra height
    # so the wheels aren't clipped, then crop back to CELL_H for the canvas.
    tall = CELL_H + (BOARD_EXTRA if effect == "skateboard" else 0)
    cell = pygame.Surface((CELL_W, tall))
    fill_sky(cell)

    b = Bird()
    configure_bird(b, lives_state, effect)
    b.draw(cell, 0, 0)

    if tall > CELL_H:
        # Crop to standard height — board is fully drawn within the tall buffer.
        out = pygame.Surface((CELL_W, CELL_H))
        out.blit(cell, (0, 0))
        return out
    return cell


# ── Canvas assembly ───────────────────────────────────────────────────────────

def main():
    n_rows = len(ROWS)
    n_cols = len(COLS)

    total_w = MARGIN + LABEL_W + n_cols * CELL_W + MARGIN
    total_h = MARGIN + HDR_H + n_rows * CELL_H + MARGIN

    canvas = pygame.Surface((total_w, total_h))
    canvas.fill(BG)

    font_title = make_font(13, bold=True)
    font_hdr   = make_font(10, bold=True)
    font_row   = make_font(10, bold=True)

    # Title
    title = font_title.render(
        "LIVES STATES  ×  POWER-UP APPEARANCES", True, TEXT_COL)
    canvas.blit(title, title.get_rect(
        centerx=total_w // 2, centery=MARGIN + HDR_H // 2))

    # Column headers
    hdr_y = MARGIN + HDR_H // 2
    for ci, (label, _) in enumerate(COLS):
        cx = MARGIN + LABEL_W + ci * CELL_W + CELL_W // 2
        lines = label.split("+")
        line_h = 13
        start_y = hdr_y - (len(lines) * line_h) // 2
        for i, ln in enumerate(lines):
            txt = font_hdr.render(ln, True, TEXT_COL)
            canvas.blit(txt, txt.get_rect(centerx=cx, top=start_y + i * line_h))

    # Rows
    for ri, (row_label, lives_state) in enumerate(ROWS):
        row_top = MARGIN + HDR_H + ri * CELL_H

        # Row label panel
        label_rect = pygame.Rect(MARGIN, row_top, LABEL_W, CELL_H)
        pygame.draw.rect(canvas, LABEL_BG, label_rect)
        lines = row_label.split("\n")
        line_h = 14
        cy = row_top + CELL_H // 2 - (len(lines) * line_h) // 2
        for ln in lines:
            col = DIM_COL if ln.startswith("(") else TEXT_COL
            txt = font_row.render(ln, True, col)
            canvas.blit(txt, txt.get_rect(centerx=MARGIN + LABEL_W // 2, top=cy))
            cy += line_h

        for ci, (_, effect) in enumerate(COLS):
            cell_x = MARGIN + LABEL_W + ci * CELL_W
            cell = render_cell(lives_state, effect)
            canvas.blit(cell, (cell_x, row_top))
            pygame.draw.rect(canvas, BG,
                             pygame.Rect(cell_x, row_top, CELL_W, CELL_H), 1)

    # Outer border
    pygame.draw.rect(canvas, (60, 65, 85), canvas.get_rect(), 2)

    # Save
    out_dir  = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "lives_powerup_grid.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {canvas.get_width()}×{canvas.get_height()} -> {out_path}")
    pygame.quit()


if __name__ == "__main__":
    main()
