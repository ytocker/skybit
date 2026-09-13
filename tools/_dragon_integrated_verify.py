"""IN-ENGINE verification of the integrated NIGHT dragon dance.

Renders a NIGHT foreground filmstrip through the LIVE foreground.draw_near_lane
path (not the round-2 harness) at increasing scroll, so the lion/dragon
alternation scrolls past on the front edge. A live gameplay Coin is composited
into each frame at its real size + brightness, so the gate is verifiable:

  * the figure reads as a DRAGON at true scrolling size, and
  * NOTHING in the dragon (dorsal tooth, head sparkle, gold belly) out-glows or
    is mistaken for the coin.

Headless (SDL dummy) -> docs/foreground_redesign/dragon/integrated.png. Not shipped.
"""
from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))   # a video mode so convert_alpha/coin cache work

from game import biome
from game import foreground
from game.config import W, H, GROUND_Y, COIN_R
from game.entities import Coin


NIGHT_PHASE = 0.69          # deep in the festival window (0.58..0.80)
PAL = biome.palette_for_phase(NIGHT_PHASE)

# t past the run-start fill so the street is fully busy (density > 0.25 gate).
T = 9.0

# Scroll steps chosen to walk the festival performance period (540 world-px at
# NEAR_MULT) so the filmstrip shows BOTH a lion slot and a dragon slot passing.
SCROLLS = [0, 240, 480, 720, 960, 1200]


def _night_sky(surf):
    """A cheap deep-night vertical wash so the front edge sits on a believable
    night sky (the real scene's sky/terrain draw earlier; we just need a dark
    backdrop to judge glow against)."""
    top = (10, 12, 30)
    bot = (26, 24, 46)
    for y in range(H):
        f = y / H
        c = (int(top[0] + (bot[0] - top[0]) * f),
             int(top[1] + (bot[1] - top[1]) * f),
             int(top[2] + (bot[2] - top[2]) * f))
        surf.fill(c, (0, y, W, 1))
    # A simple sidewalk band so the near figures have a deck under their feet.
    deck = (28, 36, 58)
    surf.fill(deck, (0, GROUND_Y, W, H - GROUND_Y))


def build():
    cols = len(SCROLLS)
    gap = 6
    label_h = 16
    sheet_w = W * cols + gap * (cols + 1)
    sheet_h = H + label_h * 2 + gap * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((8, 10, 22))

    font = pygame.font.SysFont("dejavusans", 12, bold=True)
    small = pygame.font.SysFont("dejavusans", 9, bold=True)
    sheet.blit(font.render(
        "NIGHT festival via LIVE foreground.draw_near_lane — lion/dragon alternate; "
        "coin in frame (read as dragon? out-glow coin?)",
        True, (235, 220, 180)), (gap, 2))

    coin = Coin(0, 0)

    for i, scroll in enumerate(SCROLLS):
        frame = pygame.Surface((W, H))
        _night_sky(frame)
        # THE LIVE PATH — exactly what the play scene calls each frame.
        foreground.draw_near_lane(frame, scroll, PAL, NIGHT_PHASE, T)
        # A live gameplay coin composited at its true size + brightness, placed
        # at the bird's coin column over the near figures, so it's a direct
        # brightness reference against the dragon's accents.
        coin.x = 168
        coin.y = NIGHT_PHASE * 0 + 300   # mid-screen, in the near figures' path
        coin.draw(frame)
        # A second coin lower, near deck height, right beside a passing performer.
        coin.x = 168
        coin.y = GROUND_Y - 40
        coin.draw(frame)

        x = gap + i * (W + gap)
        y = label_h + gap
        sheet.blit(frame, (x, y))
        pygame.draw.rect(sheet, (60, 64, 90), (x, y, W, H), 1)
        sheet.blit(small.render(f"scroll={scroll}", True, (240, 226, 170)),
                   (x + 2, y + H + 1))

    # ── a 3x magnified DETAIL strip of the front edge at the two scrolls where the
    # dragon head + a coin share the frame, so the dragon-read + the coin-vs-tooth
    # brightness is directly inspectable at true scrolling size.
    detail_scrolls = [(480, "dragon body"), (720, "dragon HEAD + coin")]
    crop_y = GROUND_Y - 70
    dh = H - crop_y
    zoom = 3
    band_y = sheet_h - 4
    strip = pygame.Surface((sheet_w, dh * zoom + label_h + gap))
    strip.fill((8, 10, 22))
    strip.blit(font.render("3x DETAIL — front edge (dragon read + coin reference)",
                           True, (235, 220, 180)), (gap, 2))
    for j, (scroll, lab) in enumerate(detail_scrolls):
        frame = pygame.Surface((W, H))
        _night_sky(frame)
        foreground.draw_near_lane(frame, scroll, PAL, NIGHT_PHASE, T)
        coin.x = 168; coin.y = GROUND_Y - 36
        coin.draw(frame)
        crop = frame.subsurface((0, crop_y, W, dh)).copy()
        big = pygame.transform.scale(crop, (W * zoom, dh * zoom))
        x = gap + j * (W * zoom + gap)
        if x + W * zoom > sheet_w:
            break
        strip.blit(big, (x, label_h + gap))
        strip.blit(small.render(f"scroll={scroll} · {lab}", True, (240, 226, 170)),
                   (x + 2, label_h - 2))
    full = pygame.Surface((sheet_w, sheet_h + strip.get_height() + gap))
    full.fill((8, 10, 22))
    full.blit(sheet, (0, 0))
    full.blit(strip, (0, sheet_h + gap))

    out = "/home/user/skybit/docs/foreground_redesign/dragon/integrated.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(full, out)
    print("saved", out, full.get_size())


if __name__ == "__main__":
    build()
