"""Assemble the chibi Death/Reaper boss-candidate lineup into ONE labeled sheet.

Composition only — every figure is pulled from its OWN final renderer module so
each character's settled design, palette, and proportions are preserved exactly;
nothing here re-draws or re-styles a boss. The house-style endgame CLOWN anchors
the left as the scale + style reference; the five matured Reapers follow.

Each figure is rendered on its own native canvas, auto-cropped to its opaque
bbox, then scaled so every figure stands at ONE matched reference height on a
SHARED ground line. Matching by full opaque bbox keeps a prop-heavy take (the
great-scythe) from rendering huge and a squat take from rendering tiny — the
playful chibi mass differences between bosses survive, but no figure is mis-sized
by a differing internal canvas. Run headless:

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python \
        tools/render_skybit_reaper_showcase.py
"""

import os
import pygame

# Each boss comes straight from its final renderer; the clown via the live path.
from game.pillar_staff import draw_chosen_hero
from tools.render_jester_variants import build_jester, JESTERS
from tools.render_skybit_reaper_grim_sprout import build_grim_sprout
from tools.render_skybit_reaper_big_reapy import build_big_reapy
from tools.render_skybit_reaper_dr_quill import build_dr_quill
from tools.render_skybit_reaper_tick_tock import draw_tick_tock
from tools.render_skybit_reaper_the_hollow import draw_hollow


# Neutral studio panel — a soft cool-grey gradient so every palette reads true.
BG_TOP = (212, 218, 228)
BG_BOT = (180, 188, 200)
GROUND = (150, 158, 170)
INK = (34, 30, 40)
LABEL = (28, 24, 34)


def _opaque_bbox(surf):
    """Tight bbox of all non-transparent pixels (so canvas padding never skews
    the matched-scale normalization)."""
    rect = surf.get_bounding_rect(min_alpha=8)
    if rect.width == 0 or rect.height == 0:
        return surf.get_rect()
    return rect


def _crop(surf):
    rect = _opaque_bbox(surf)
    out = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    out.blit(surf, (0, 0), rect)
    return out


def _clown_figure(ss=4):
    """The settled endgame clown via the live draw path, onto a tight canvas.
    The pop() of `no_shadow` follows the brief so the figure renders without the
    pillar-cell shadow disc."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    # Generous canvas: the raised arm + die-hand reach up-left and the staff
    # plants below the feet, so pad on every side, then crop to the opaque bbox.
    W, H = 320 * ss, 420 * ss
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = int(W * 0.55)
    feet_y = int(H * 0.74)
    # draw_chosen_hero works in 1x body units; supersample by scaling the whole
    # composite afterwards rather than passing ss into the un-ss-aware builder.
    base = pygame.Surface((320, 420), pygame.SRCALPHA)
    draw_chosen_hero(base, int(320 * 0.55), int(420 * 0.74),
                     build_jester=build_jester, spec=spec)
    surf = pygame.transform.smoothscale(base, (W, H))
    return _crop(surf)


def _grim_sprout_figure():
    return _crop(build_grim_sprout(scale=1.0, ss=3))


def _big_reapy_figure():
    surf, _feet = build_big_reapy(scale=1.0, ss=3)
    return _crop(surf)


def _dr_quill_figure():
    return _crop(build_dr_quill(scale=1.0, ss=3))


def _tick_tock_figure(ss=3):
    # draw_* boss builders paint in place onto a host surface at (cx, feet_y).
    W, H = 220 * ss, 260 * ss
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_tick_tock(surf, W // 2, int(H * 0.93), scale=1.0, ss=ss)
    return _crop(surf)


def _hollow_figure(ss=3):
    W, H = 240 * ss, 240 * ss
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_hollow(surf, W // 2, int(H * 0.93), scale=1.0, ss=ss)
    return _crop(surf)


def _bg_panel(w, h):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        surf.fill((int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t),
                   int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t),
                   int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)),
                  (0, y, w, 1))
    return surf


def main():
    pygame.init()

    cells = [
        ("CLOWN (house style)", _clown_figure()),
        ("GRIM SPROUT", _grim_sprout_figure()),
        ("BIG REAPY", _big_reapy_figure()),
        ("DR. QUILL", _dr_quill_figure()),
        ("TICK-TOCK", _tick_tock_figure()),
        ("THE HOLLOW", _hollow_figure()),
    ]

    # Matched scale: every figure is scaled so its full opaque height equals one
    # reference height. The clown is the house-style scale anchor.
    REF_H = 300
    norm = []
    for label, fig in cells:
        scale = REF_H / fig.get_height()
        nw = max(1, int(fig.get_width() * scale))
        nh = max(1, int(fig.get_height() * scale))
        norm.append((label, pygame.transform.smoothscale(fig, (nw, nh))))

    # Layout: a title strip on top, even-width columns, a shared ground line.
    pad = 40
    col_gap = 26
    title_h = 64
    label_h = 40
    ground_pad = 30          # gap between feet (ground line) and label band
    fig_max_w = max(f.get_width() for _, f in norm)
    col_w = fig_max_w + col_gap
    n = len(norm)
    panel_w = pad * 2 + col_w * n
    ground_y = title_h + pad + REF_H + 18
    panel_h = ground_y + ground_pad + label_h + pad

    sheet = _bg_panel(panel_w, panel_h)

    # Title strip.
    title_band = pygame.Surface((panel_w, title_h), pygame.SRCALPHA)
    title_band.fill((26, 22, 32, 235))
    sheet.blit(title_band, (0, 0))
    tfont = pygame.font.SysFont("dejavusans", 30, bold=True)
    title = tfont.render("Skybit — chibi Death/Reaper boss candidates",
                         True, (244, 240, 250))
    sheet.blit(title, ((panel_w - title.get_width()) // 2,
                       (title_h - title.get_height()) // 2))

    # Shared ground line.
    pygame.draw.line(sheet, GROUND, (pad // 2, ground_y),
                     (panel_w - pad // 2, ground_y), 3)

    lfont = pygame.font.SysFont("dejavusans", 19, bold=True)
    for i, (label, fig) in enumerate(norm):
        col_x = pad + i * col_w
        fx = col_x + (col_w - col_gap - fig.get_width()) // 2 + col_gap // 2
        # Feet sit ON the shared ground line.
        fy = ground_y - fig.get_height()
        sheet.blit(fig, (fx, fy))
        # Soft contact shadow so figures read as standing, not floating.
        sh_w = max(20, int(fig.get_width() * 0.6))
        shadow = pygame.Surface((sh_w, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (40, 44, 54, 70), shadow.get_rect())
        sheet.blit(shadow, (col_x + (col_w - sh_w) // 2, ground_y - 7))

        txt = lfont.render(label, True, LABEL)
        sheet.blit(txt, (col_x + (col_w - txt.get_width()) // 2,
                         ground_y + ground_pad))

    out_dir = "/home/user/skybit/docs/skybit_reaper"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "showcase.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
