"""
Side-by-side gameplay comparison: regular parrot vs ace-headwrap (last-life skin).
Output: docs/hurt-parrot-v5-comparison.png
"""
import os, sys
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
    _cfg.DAY_EXTRA_SECONDS = 0
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
import game.parrot as parrot

# ── Layout ───────────────────────────────────────────────────────────────────

SCALE    = 0.65
PANEL_W  = int(W * SCALE)   # 234
PANEL_H  = int(H * SCALE)   # 416
N_PANELS = 2
GAP      = 16
MARGIN   = 24
HDR_H    = 54
FTR_H    = 78
BG       = (8, 8, 20)

CANVAS_W = MARGIN + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FTR_H + MARGIN

# ── Scene parameters (identical for both panels) ──────────────────────────────

BIRD_Y     = 268
BIRD_FRAME = 1
BIRD_TILT  = -6.0
BG_SCROLL  = 420
PHASE      = 0.05          # early day / golden morning

PILLAR_SPECS = [
    (230, 240),
    (510, 295),
]


# ── Scene drawing ─────────────────────────────────────────────────────────────

def _draw_pillar(surf, cx, gap_cy, pal):
    x     = cx - PIPE_W // 2
    half  = GAP_START // 2
    top_h = gap_cy - half
    bot_y = gap_cy + half
    bot_h = GROUND_Y - bot_y
    stone     = pal.get("pipe_stone",  (190, 152, 102))
    stone_dk  = pal.get("pipe_shadow", (150, 115,  72))
    stone_cap = pal.get("pipe_cap",    (210, 175, 125))
    pygame.draw.rect(surf, stone,     (x,     0,      PIPE_W,     top_h))
    pygame.draw.rect(surf, stone_dk,  (x,     0,      4,          top_h))
    pygame.draw.rect(surf, stone_cap, (x - 3, top_h - 8, PIPE_W + 6, 8))
    if bot_h > 0:
        pygame.draw.rect(surf, stone,     (x,     bot_y, PIPE_W,     bot_h))
        pygame.draw.rect(surf, stone_dk,  (x,     bot_y, 4,          bot_h))
        pygame.draw.rect(surf, stone_cap, (x - 3, bot_y, PIPE_W + 6, 8))


def _draw_hearts(surf, total, remaining):
    """Minimal heart-row HUD, centred near the top."""
    r  = 7
    sp = 20
    n  = total
    ox = W // 2 - (n * sp) // 2
    oy = 22
    RED_FILL  = (220, 60, 80)
    DARK_FILL = (50, 50, 68)
    for i in range(n):
        cx = ox + i * sp
        col = RED_FILL if i < remaining else DARK_FILL
        # Heart shape via two circles + triangle
        pygame.draw.circle(surf, col, (cx - r // 2, oy), r // 2)
        pygame.draw.circle(surf, col, (cx + r // 2, oy), r // 2)
        pygame.draw.polygon(surf, col, [(cx - r, oy + 1), (cx, oy + r + 2), (cx + r, oy + 1)])


def draw_scene(screen, getter, hearts_remaining, hearts_total=2):
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

    sprite = getter(BIRD_FRAME, BIRD_TILT)
    sw, sh = sprite.get_size()
    screen.blit(sprite, (BIRD_X - sw // 2, BIRD_Y - sh // 2))

    _draw_hearts(screen, hearts_total, hearts_remaining)


def _surf_to_pil(surf):
    arr   = pygame.surfarray.array3d(surf)
    return Image.fromarray(arr.transpose(1, 0, 2), "RGB")


def _font(size, bold=False):
    paths = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
         if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
         if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ── Panel definitions ─────────────────────────────────────────────────────────

PANELS = [
    # getter,                hearts_remaining, title,           sublabel,           accent colour
    (parrot.get_parrot,      2, "NORMAL",       "2 lives — base skin",    (160, 220, 160)),
    (parrot.get_hurt_parrot, 0, "LAST LIFE",    "0 lives — ace headwrap", (255, 180, 100)),
]


def main():
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw   = ImageDraw.Draw(canvas)
    screen = pygame.Surface((W, H))

    hdr_f   = _font(20, bold=True)
    title_f = _font(17, bold=True)
    sub_f   = _font(13)

    # Header
    hdr_txt = "HURT PARROT  ·  ACE-HEADWRAP  ·  IN-GAME COMPARISON"
    bb = draw.textbbox((0, 0), hdr_txt, font=hdr_f)
    draw.text(((CANVAS_W - (bb[2] - bb[0])) // 2,
               MARGIN + (HDR_H - (bb[3] - bb[1])) // 2),
              hdr_txt, font=hdr_f, fill=(255, 245, 220))

    panel_top = MARGIN + HDR_H + GAP

    for idx, (getter, hearts, title, sublabel, accent) in enumerate(PANELS):
        x0 = MARGIN + idx * (PANEL_W + GAP)

        screen.fill((0, 0, 0))
        draw_scene(screen, getter, hearts_remaining=hearts)
        pil_full  = _surf_to_pil(screen)
        pil_panel = pil_full.resize((PANEL_W, PANEL_H), Image.LANCZOS)
        canvas.paste(pil_panel, (x0, panel_top))

        # Panel border in accent colour
        draw.rectangle([x0 - 1, panel_top - 1, x0 + PANEL_W, panel_top + PANEL_H],
                       outline=accent, width=2)

        # Footer
        fy = panel_top + PANEL_H + 8
        bb = draw.textbbox((0, 0), title, font=title_f)
        tw = bb[2] - bb[0]
        draw.text((x0 + (PANEL_W - tw) // 2, fy), title, font=title_f, fill=accent)
        fy += (bb[3] - bb[1]) + 6
        bb2 = draw.textbbox((0, 0), sublabel, font=sub_f)
        draw.text((x0 + (PANEL_W - (bb2[2] - bb2[0])) // 2, fy),
                  sublabel, font=sub_f, fill=(200, 200, 220))

    out_path = os.path.join(os.path.dirname(__file__), "hurt-parrot-v5-comparison.png")
    canvas.save(out_path)
    print(f"Saved {CANVAS_W}x{CANVAS_H} -> {out_path}")

    # Sanity: each panel must have scene content
    arr = np.array(canvas)
    for idx, (_, _, title, _, _) in enumerate(PANELS):
        x0 = MARGIN + idx * (PANEL_W + GAP)
        region = arr[panel_top:panel_top + PANEL_H, x0:x0 + PANEL_W]
        count  = int(np.any(region != np.array(BG), axis=2).sum())
        assert count > 5000, f"panel '{title}' appears blank: {count} px"
        print(f"  {title}: {count} non-bg pixels ✓")

    print("Done.")


if __name__ == "__main__":
    main()
