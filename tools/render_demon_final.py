"""Render the ORIGINAL Demon Jester boss (the liked one — boss #3 from
`render_jester_boss.py`) with ONE change: a BIGGER, properly-CRADLED die.

The five red "demon variations" were rejected ("the original is much better").
This keeps the original demon's look verbatim (its plum/lime + fiery palette,
horns, glowing eyes, fangs, the amorphous reddish shadow-pool aura, scale 1.40)
and only fixes the die: bigger, and repositioned UP-LEFT so the enlarged raised
arm actually cradles it (the original die sat small at base position while the
arm was scaled up). The die keeps its familiar warm gold/yellow power-up aura.

No game/ files touched; reuses the boss + die kit. Headless + deterministic.

    PYTHONPATH=. python tools/render_demon_final.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from tools.render_jester_boss import (
    build_boss, silhouette_aura, _scene_bg, _blit_parrot,
    PANEL_W, PANEL_H, FEET_Y, SS, BOSSES,
)
from tools.render_demon_variants import draw_boss_die, _die_seat

DIE_SIZE = 62                      # bigger than the original ~40
SPEC = BOSSES[2]                   # "The Demon Jester" — the original the user likes


def render_panel():
    """The original Demon with the bigger die cradled in the (scaled) raised arm."""
    scale = SPEC["scale"]
    mass = SPEC.get("mass", 1.0)
    bw, bh = PANEL_W * SS, PANEL_H * SS
    big = pygame.Surface((bw, bh))
    _scene_bg(big, bw, bh, 2)

    jester_cx = PANEL_W // 2 + 12
    base_feet = FEET_Y

    # Repositioned seat (up-left) + cradle inverse-solve so the SCALED raised arm
    # cups the bigger die (mirrors the demon-variants cradle math).
    _, die_x, die_base_y = _die_seat(scale, original=False)
    cradle_x, cradle_y = die_x - 8, die_base_y + 26
    hand_x = int(jester_cx + (cradle_x - jester_cx) / (scale * mass))
    hand_y = int(base_feet + (cradle_y - base_feet) / scale)
    hand_up = (hand_x, hand_y)

    fig = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pal = SPEC["pal"]
    build_boss(fig, jester_cx, base_feet, hand_up,
               dark=pal["dark"], light=pal["light"], gold=pal["gold"],
               cap_fn=SPEC["cap"], glow_col=SPEC["glow"],
               fang_xtra=SPEC.get("fang_xtra", 0),
               narrow_eyes=SPEC.get("narrow_eyes", False),
               skin=SPEC.get("skin", (200, 150, 140)),
               shadow_face=SPEC.get("shadow_face", False),
               mass=mass, lean=SPEC.get("lean", 0.0),
               head_extra_tilt=SPEC.get("head_tilt", 0))

    sw, sh = int(PANEL_W * scale), int(PANEL_H * scale)
    fig_big = pygame.transform.smoothscale(fig, (sw, sh))
    off_x = int(jester_cx - jester_cx * scale)
    off_y = int(base_feet - base_feet * scale)
    boss_layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    boss_layer.blit(fig_big, (off_x, off_y))
    boss_ss = pygame.transform.smoothscale(boss_layer, (bw, bh))

    breathe = 0.5 + 0.5 * math.sin(2.0 * 1.3)
    silhouette_aura(big, boss_ss, int(jester_cx * SS), int((FEET_Y - 70) * SS),
                    SPEC["aura_hue"], breathe, dark=SPEC["aura_dark"],
                    rim=SPEC.get("rim"), embers=SPEC.get("embers", True),
                    smoke=SPEC.get("smoke", True), seed=2, scl=SS,
                    bulk=0.85 + 0.35 * scale)
    big.blit(boss_ss, (0, 0))

    overlay = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    # The original's WARM GOLD / yellow power-up die — only size + seat changed.
    draw_boss_die(overlay, die_x, die_base_y, 2.0, size=DIE_SIZE,
                  core=(255, 242, 170), mid=(255, 200, 70),
                  edge=(232, 150, 36), spark=(255, 236, 150))
    _blit_parrot(overlay)
    big.blit(pygame.transform.smoothscale(overlay, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    panel = render_panel()

    SCALE = 2
    pw, ph = PANEL_W * SCALE, PANEL_H * SCALE
    PAD, TITLE_H = 28, 64
    # the figure at 2x, plus a 1x inset beside it to confirm the die reads at
    # in-game scale.
    iw, ih = PANEL_W, PANEL_H
    cw = PAD * 3 + pw + iw
    ch = TITLE_H + max(ph, ih) + PAD
    canvas = pygame.Surface((cw, ch))
    canvas.fill((22, 22, 30))

    f_title = pygame.font.SysFont(None, 44, bold=True)
    f_cap = pygame.font.SysFont(None, 26, bold=True)
    canvas.blit(f_title.render(
        "DEMON JESTER (original) — bigger die, cradled in the raised arm",
        True, (250, 240, 210)), (PAD, PAD - 2))

    big2x = pygame.transform.smoothscale(panel, (pw, ph))
    canvas.blit(big2x, (PAD, TITLE_H))
    pygame.draw.rect(canvas, (70, 76, 96),
                     pygame.Rect(PAD - 1, TITLE_H - 1, pw + 2, ph + 2), 1)

    ix = PAD * 2 + pw
    canvas.blit(panel, (ix, TITLE_H))
    pygame.draw.rect(canvas, (70, 76, 96),
                     pygame.Rect(ix - 1, TITLE_H - 1, iw + 2, ih + 2), 1)
    canvas.blit(f_cap.render("1x in-game scale", True, (200, 206, 216)),
                (ix, TITLE_H + ih + 6))

    out = os.path.join("docs", "jester", "demon_original_die.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"saved {out}  ({cw}x{ch})")


if __name__ == "__main__":
    main()
