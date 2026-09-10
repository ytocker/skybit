"""
4-panel in-game view: ORIGINAL · bandaged-cheek · belly-strapped · field-dressed-plus
Renders a synthetic gameplay frame (sky, clouds, mountains, pillars, ground, bird).
Uses only game.parrot + game.draw + game.biome — avoids game.world/entities which
have missing imports on this task branch.
Output: docs/hurt-parrot-v5-gameplay-showcase.png
"""
import importlib.util, os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import numpy as np
import pygame
from PIL import Image, ImageDraw, ImageFont
pygame.init()

from game.config import W, H, GROUND_Y, BIRD_X, PIPE_W, GAP_START
import game.config as _cfg
if not hasattr(_cfg, "DAY_EXTRA_SECONDS"):
    _cfg.DAY_EXTRA_SECONDS = 0   # missing on this branch; biome.py requires it
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
import game.parrot as parrot

REPO     = "/home/user/skybit"
SCALE    = 0.5
PANEL_W  = int(W * SCALE)    # 180
PANEL_H  = int(H * SCALE)    # 320
N_PANELS = 4
GAP      = 12
MARGIN   = 20
HDR_H    = 50
FTR_H    = 65
BG       = (8, 8, 20)

CANVAS_W = MARGIN + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FTR_H + MARGIN

# Fixed scene parameters
BIRD_Y      = 268        # comfortable mid-height y
BIRD_FRAME  = 1          # mid-wing position
BIRD_TILT   = -6.0       # slight nose-up
BG_SCROLL   = 420        # background parallax position
PHASE       = 0.05       # early day (golden-hour morning light)
PIPE_GAP    = GAP_START  # 170 px vertical gap between top/bottom pillar

# Two pillar pairs on screen: one ahead (right), one approaching further right
PILLAR_SPECS = [
    (230, 240),   # cx, gap_center_y — first pillar ahead of bird
    (510, 290),   # second pillar further right (partially off-screen)
]

_HURT_ANGLES = (10, -5, -20, -35)


def _load_hurt_design(slug):
    path = f"{REPO}/docs/hurt-parrot-v5/{slug}/design.py"
    spec = importlib.util.spec_from_file_location("design", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_hurt_getter(slug):
    mod    = _load_hurt_design(slug)
    frames = [parrot._add_outline(mod._build_hurt_frame(a)) for a in _HURT_ANGLES]
    cache  = {}
    def getter(frame_idx, tilt_deg):
        key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
        if key not in cache:
            cache[key] = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        return cache[key]
    return getter


def _draw_pillar(surf, cx, gap_cy, palette):
    """Draw one sandstone pillar pair with a vertical gap centred at gap_cy."""
    x      = cx - PIPE_W // 2
    half_g = PIPE_GAP // 2
    top_h  = gap_cy - half_g           # height of top pillar
    bot_y  = gap_cy + half_g           # top of bottom pillar
    bot_h  = GROUND_Y - bot_y

    stone     = palette.get("pipe_stone",  (190, 152, 102))
    stone_dk  = palette.get("pipe_shadow", (150, 115,  72))
    stone_cap = palette.get("pipe_cap",    (210, 175, 125))

    # Top pillar body
    pygame.draw.rect(surf, stone,    (x,      0,      PIPE_W, top_h))
    pygame.draw.rect(surf, stone_dk, (x,      0,      4,      top_h))   # left shadow
    # Crown cap (bottom edge of top pillar)
    pygame.draw.rect(surf, stone_cap, (x - 3, top_h - 8, PIPE_W + 6, 8))

    if bot_h > 0:
        # Bottom pillar body
        pygame.draw.rect(surf, stone,    (x,     bot_y, PIPE_W, bot_h))
        pygame.draw.rect(surf, stone_dk, (x,     bot_y, 4,      bot_h))   # left shadow
        # Crown cap (top edge of bottom pillar)
        pygame.draw.rect(surf, stone_cap, (x - 3, bot_y, PIPE_W + 6, 8))


def draw_scene(screen, getter):
    """Render a synthetic gameplay frame; use getter to draw the bird sprite."""
    pal = _biome.palette_for_phase(PHASE)
    a   = int(PHASE * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    sky.set_alpha(None)
    screen.blit(sky, (0, 0))

    for i, (bx, by, sc) in enumerate(((20, 90, .9), (180, 140, 1.1), (60, 220, .8),
                                       (230, 60, .7), (320, 180, .9))):
        ox = ((bx - BG_SCROLL * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(screen, ox, by, sc, variant=0, palette=pal)

    draw_mountains(screen, BG_SCROLL, GROUND_Y, W, phase=PHASE)

    draw_ground(screen, GROUND_Y, W, H, BG_SCROLL,
                pal.get("ground_top"), pal.get("ground_mid"))

    for cx, gap_cy in PILLAR_SPECS:
        _draw_pillar(screen, cx, gap_cy, pal)

    # Bird sprite
    sprite = getter(BIRD_FRAME, BIRD_TILT)
    sw, sh = sprite.get_size()
    screen.blit(sprite, (BIRD_X - sw // 2, BIRD_Y - sh // 2))


def _surf_to_pil(surf):
    arr   = pygame.surfarray.array3d(surf)
    alpha = pygame.surfarray.array_alpha(surf)
    return Image.fromarray(np.dstack([arr, alpha]).transpose(1, 0, 2), "RGBA")


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# Build hurt getters at module level (before PANELS list)
_getter_original      = parrot.get_parrot
_getter_bandaged      = make_hurt_getter("bandaged-cheek")
_getter_belly         = make_hurt_getter("belly-strapped")
_getter_field_plus    = make_hurt_getter("field-dressed-plus")

PANELS = [
    ("original",           "ORIGINAL",           _getter_original,   (140, 200, 140)),
    ("bandaged-cheek",     "bandaged-cheek",      _getter_bandaged,   (255, 210,  80)),
    ("belly-strapped",     "belly-strapped",      _getter_belly,      (100, 200, 255)),
    ("field-dressed-plus", "field-dressed-plus",  _getter_field_plus, (255, 210,  80)),
]


def main():
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (*BG, 255))
    draw   = ImageDraw.Draw(canvas)

    hdr_font  = _font(18, bold=True)
    id_font   = _font(22, bold=True)
    slug_font = _font(14, bold=False)

    title = "HURT PARROT · LAST LIFE · IN-GAME VIEW"
    bbox  = draw.textbbox((0, 0), title, font=hdr_font)
    draw.text(((CANVAS_W - (bbox[2] - bbox[0])) // 2,
               MARGIN + (HDR_H - (bbox[3] - bbox[1])) // 2),
              title, font=hdr_font, fill=(255, 235, 200, 255))

    panel_top = MARGIN + HDR_H + GAP
    screen    = pygame.Surface((W, H))

    for idx, (key, label, getter, name_color) in enumerate(PANELS):
        x0 = MARGIN + idx * (PANEL_W + GAP)

        screen.fill((0, 0, 0))
        draw_scene(screen, getter)

        pil_full  = _surf_to_pil(screen)
        pil_panel = pil_full.resize((PANEL_W, PANEL_H), Image.LANCZOS)
        cell      = Image.new("RGBA", (PANEL_W, PANEL_H), (*BG, 255))
        cell.paste(pil_panel, (0, 0))
        canvas.paste(cell, (x0, panel_top))

        # Footer: numeric ID then slug
        id_label = str(idx + 1)
        id_bb    = draw.textbbox((0, 0), id_label, font=id_font)
        id_w, id_h = id_bb[2] - id_bb[0], id_bb[3] - id_bb[1]
        id_y = panel_top + PANEL_H + 6
        draw.text((x0 + (PANEL_W - id_w) // 2, id_y),
                  id_label, font=id_font, fill=(220, 220, 240, 255))

        slug_y = id_y + id_h + 4
        bb = draw.textbbox((0, 0), label, font=slug_font)
        draw.text((x0 + (PANEL_W - (bb[2] - bb[0])) // 2, slug_y),
                  label, font=slug_font, fill=(*name_color, 255))

    out_path = os.path.join(REPO, "docs", "hurt-parrot-v5-gameplay-showcase.png")
    canvas.save(out_path)
    print(f"Saved {CANVAS_W}x{CANVAS_H} -> {out_path}")

    for idx, (key, _, _, _) in enumerate(PANELS):
        x0     = MARGIN + idx * (PANEL_W + GAP)
        region = canvas.crop((x0, panel_top, x0 + PANEL_W, panel_top + PANEL_H))
        count  = int(np.any(np.array(region)[:, :, :3] != np.array(BG), axis=2).sum())
        print(f"  panel {idx+1} ({key}): {count} non-bg pixels  [{'OK' if count > 1000 else 'BLANK'}]")

    assert all(
        int(np.any(
            np.array(canvas.crop((MARGIN + i * (PANEL_W + GAP), panel_top,
                                  MARGIN + i * (PANEL_W + GAP) + PANEL_W,
                                  panel_top + PANEL_H)))[:, :, :3]
            != np.array(BG), axis=2
        ).sum()) > 1000
        for i in range(N_PANELS)
    ), "One or more panels appear blank"

    print("All panels populated. Done.")


if __name__ == "__main__":
    main()
