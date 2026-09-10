"""Four pimped-up pause button options on top of the chosen Glass-A HUD.

Score / BEST / coins are frozen as glass_a (cream face + 2 px gold rim).
Only the pause button changes. Pick one, then we wire it into hud.py.

Output:
  docs/screenshots/hud_variants/pause_p1_heavy.png    thick double gold ring + gold bars
  docs/screenshots/hud_variants/pause_p2_studded.png  eight rivets around the rim
  docs/screenshots/hud_variants/pause_p3_crested.png  tiny crown / laurel on top
  docs/screenshots/hud_variants/pause_p4_engraved.png stylized gold P with red outline
  docs/screenshots/hud_variants/pause_compare.png     4-up labelled strip

Run from the repo root:

    PYTHONPATH=. python tools/render_pause_pimps.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

sys.path.insert(0, os.path.dirname(__file__))
from render_hud_variants import draw_bg, draw_pillar_context  # noqa: E402


SCORE = 127
BEST  = 842
COINS = 23
UPSCALE = 3


# ── Frozen Glass-A score + side pills (ported from glass iteration A) ────────

def _draw_glass_a_hud(surf, best, coins):
    """The chosen Glass-A treatment for score / BEST / coins. Pause is
    drawn separately by each pimp option."""
    from game.config import W
    from game.hud import (
        _PANEL_DARK, _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE, _coin_icon, _font,
    )
    from game.draw import NEAR_BLACK

    # ── Score: cream + 2 px gold rim + deep shadow on a glass pill
    score_txt = str(SCORE)
    f = _font(48, True)
    img = f.render(score_txt, True, (252, 244, 220))
    rim = f.render(score_txt, True, _GOLD_DEEP)
    sh  = f.render(score_txt, True, NEAR_BLACK)
    r = img.get_rect(center=(W // 2, 92))
    back_w = max(r.width + 56, 96)
    back_h = 56
    back = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
    pygame.draw.rect(back, (*_PANEL_DARK, 120), (0, 0, back_w, back_h),
                     border_radius=back_h // 2)
    pygame.draw.rect(back, (*_GOLD_BRIGHT, 160), (0, 0, back_w, back_h),
                     border_radius=back_h // 2, width=1)
    sheen = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
    for yy in range(back_h // 2):
        a = int(20 * (1 - yy / (back_h / 2)))
        pygame.draw.line(sheen, (255, 245, 220, a),
                         (8, yy + 2), (back_w - 8, yy + 2))
    back.blit(sheen, (0, 0))
    surf.blit(back, (W // 2 - back_w // 2, 92 - back_h // 2))
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(rim, (r.x + ox, r.y + oy))
    sh.set_alpha(180)
    surf.blit(sh, (r.x + 2, r.y + 4))
    surf.blit(img, r.topleft)

    # ── BEST: low-alpha slab + tiny star + gold value
    bp = pygame.Surface((92, 32), pygame.SRCALPHA)
    pygame.draw.rect(bp, (*_PANEL_DARK, 140), (0, 0, 92, 32), border_radius=8)
    pygame.draw.rect(bp, (*_GOLD_BRIGHT, 110), (0, 0, 92, 32),
                     border_radius=8, width=1)
    star = [(11, 8), (13, 13), (18, 13), (14, 16), (16, 21),
            (11, 18), (6, 21), (8, 16), (4, 13), (9, 13)]
    pygame.draw.polygon(bp, (*_GOLD_BRIGHT, 220), star)
    lf = _font(10, True).render("BEST", True, (235, 230, 215))
    bp.blit(lf, lf.get_rect(center=(56, 9)))
    vf = _font(15, True).render(str(best), True, _GOLD_BRIGHT)
    bp.blit(vf, vf.get_rect(center=(56, 21)))
    surf.blit(bp, (10, 14))

    # ── Coins
    cp = pygame.Surface((86, 32), pygame.SRCALPHA)
    pygame.draw.rect(cp, (*_PANEL_DARK, 140), (0, 0, 86, 32), border_radius=8)
    pygame.draw.rect(cp, (*_GOLD_BRIGHT, 110), (0, 0, 86, 32),
                     border_radius=8, width=1)
    _coin_icon(cp, 14, 16, 9)
    cv = _font(16, True).render(f"x{coins}", True, _GOLD_BRIGHT)
    cp.blit(cv, cv.get_rect(center=(52, 16)))
    surf.blit(cp, (W - 154, 14))


# ── Pause option 1: Heavy gold coin ──────────────────────────────────────────
# Slightly larger (48 px), double gold ring, deep-gold inner accent,
# warm gold bars instead of white. Reads as a heavy ceremonial coin.

def render_pause_p1_heavy(surf):
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE
    size = 48
    px = W - size - 8
    py = 10
    cx, cy = px + size // 2, py + size // 2
    # Soft outer halo
    halo = pygame.Surface((size + 14, size + 14), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*_GOLD_BRIGHT, 50),
                       (size // 2 + 7, size // 2 + 7), size // 2 + 6)
    surf.blit(halo, (px - 7, py - 7))
    # Dark disc
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), size // 2)
    # Outer bright gold ring + inner deep-gold accent
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), size // 2, 3)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), size // 2 - 4, 1)
    # Specular sheen on the top-left of the rim
    pygame.draw.arc(surf, _GOLD_PALE,
                    (cx - size // 2 + 2, cy - size // 2 + 2, size - 4, size - 4),
                    math.pi * 0.7, math.pi * 1.3, 2)
    # Gold pause bars (slightly bigger to match the larger button)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - 9, cy - 11, 6, 22), border_radius=2)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx + 3, cy - 11, 6, 22), border_radius=2)


# ── Pause option 2: Studded ──────────────────────────────────────────────────
# Eight tiny gold rivets evenly spaced around the rim, plus a pale top
# highlight. Reads as a leather-and-brass campaign disc.

def render_pause_p2_studded(surf):
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE
    from game.draw import WHITE
    size = 46
    px = W - size - 10
    py = 11
    cx, cy = px + size // 2, py + size // 2
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), size // 2)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), size // 2, 2)
    # Top highlight arc
    pygame.draw.arc(surf, (*_GOLD_PALE, 180),
                    (cx - size // 2 + 3, cy - size // 2 + 3, size - 6, size - 6),
                    math.pi * 0.85, math.pi * 1.15, 2)
    # 8 rivets around the rim, just inside the ring
    rivet_r = size // 2 - 5
    for k in range(8):
        ang = k * math.pi / 4 - math.pi / 2  # start at 12 o'clock
        sx = cx + int(math.cos(ang) * rivet_r)
        sy = cy + int(math.sin(ang) * rivet_r)
        pygame.draw.circle(surf, _GOLD_BRIGHT, (sx, sy), 2)
        pygame.draw.circle(surf, _GOLD_DEEP, (sx, sy), 2, 1)
    # Bright pause bars (kept warm white-cream for legibility against the
    # busy studs)
    bar_col = (252, 244, 220)
    pygame.draw.rect(surf, bar_col, (cx - 7, cy - 9, 4, 18), border_radius=2)
    pygame.draw.rect(surf, bar_col, (cx + 3, cy - 9, 4, 18), border_radius=2)


# ── Pause option 3: Crested ──────────────────────────────────────────────────
# Classic disc with a tiny gold laurel-crown crest sitting on top of the
# rim. Most overtly "royal" of the four.

def render_pause_p3_crested(surf):
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE
    size = 46
    px = W - size - 10
    py = 14   # nudged down to leave room for the crest above
    cx, cy = px + size // 2, py + size // 2

    # Crest above the disc — small gold trapezoid + 3 dots + scarlet line
    cw = 22
    ch = 8
    crest_y = py - ch + 2
    crest_pts = [
        (cx - cw // 2, crest_y + ch),
        (cx - cw // 2 + 2, crest_y),
        (cx + cw // 2 - 2, crest_y),
        (cx + cw // 2, crest_y + ch),
    ]
    pygame.draw.polygon(surf, _GOLD_BRIGHT, crest_pts)
    pygame.draw.polygon(surf, _GOLD_DEEP, crest_pts, 1)
    # 3 prongs / dots on top
    for off in (-6, 0, 6):
        pygame.draw.circle(surf, _GOLD_BRIGHT, (cx + off, crest_y - 1), 2)
        pygame.draw.circle(surf, _GOLD_DEEP, (cx + off, crest_y - 1), 2, 1)

    # Main disc
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), size // 2)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), size // 2, 2)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), size // 2 - 3, 1)

    # Gold pause bars
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - 7, cy - 9, 5, 18), border_radius=2)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx + 2, cy - 9, 5, 18), border_radius=2)


# ── Pause option 4: Engraved P ───────────────────────────────────────────────
# Replaces the pause bars with a stylized "P" letter, gold-faced with a
# red outline — borrows the SKYBIT title treatment. Most distinctive.

def render_pause_p4_engraved(surf):
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_DEEP, _RED_OUTLINE, _font
    from game.draw import NEAR_BLACK
    size = 46
    px = W - size - 10
    py = 11
    cx, cy = px + size // 2, py + size // 2

    # Dark disc + double ring
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), size // 2)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), size // 2, 2)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), size // 2 - 3, 1)

    # Stylized "P" with red outline and gold face
    pf = _font(28, True)
    pi = pf.render("P", True, _GOLD_BRIGHT)
    po = pf.render("P", True, _RED_OUTLINE)
    sh = pf.render("P", True, NEAR_BLACK)
    pr = pi.get_rect(center=(cx, cy))
    # 2 px red outline + soft shadow + gold face
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(po, (pr.x + ox, pr.y + oy))
    sh.set_alpha(150)
    surf.blit(sh, (pr.x + 1, pr.y + 2))
    surf.blit(pi, pr)


# ── Main ─────────────────────────────────────────────────────────────────────

def render_pause_p3_nocrest(surf):
    """P3 without the crest — what the user picked. Plain disc with the
    double gold ring (bright outer + deep-gold inner accent) + gold bars.
    """
    from game.config import W
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_DEEP
    size = 46
    px = W - size - 10
    py = 11
    cx, cy = px + size // 2, py + size // 2
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), size // 2)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), size // 2, 2)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), size // 2 - 3, 1)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - 7, cy - 9, 5, 18), border_radius=2)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx + 2, cy - 9, 5, 18), border_radius=2)


OPTIONS = [
    ("pause_p1_heavy",    "P1 · heavy coin",     render_pause_p1_heavy),
    ("pause_p2_studded",  "P2 · studded rim",    render_pause_p2_studded),
    ("pause_p3_crested",  "P3 · crown crest",    render_pause_p3_crested),
    ("pause_p4_engraved", "P4 · engraved P",     render_pause_p4_engraved),
    ("pause_p3_nocrest",  "P3* · no crest",      render_pause_p3_nocrest),
]


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    pygame.display.set_mode((W, H))

    out_dir = os.path.join("docs", "screenshots", "hud_variants")
    os.makedirs(out_dir, exist_ok=True)

    frames: "list[tuple[str, str, pygame.Surface]]" = []

    for slug, label, render in OPTIONS:
        surf = pygame.Surface((W, H))
        palette = draw_bg(surf, scroll=120.0, phase=0.62)
        draw_pillar_context(surf, palette)
        _draw_glass_a_hud(surf, BEST, COINS)
        render(surf)

        big = pygame.transform.smoothscale(surf, (W * UPSCALE, H * UPSCALE))
        out_path = os.path.join(out_dir, f"{slug}.png")
        pygame.image.save(big, out_path)
        print(f"saved {out_path}  ({W * UPSCALE}x{H * UPSCALE})")
        frames.append((slug, label, big))

    # 2×2 compare grid so each option gets full visual breathing room.
    GAP = 24
    LABEL_H = 56
    PAD = 32
    cell_w = W * UPSCALE
    cell_h = H * UPSCALE
    cols = 4
    canvas_w = cell_w * cols + GAP * (cols - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((22, 18, 32))
    font = pygame.font.SysFont(None, 56, bold=True)
    for i, (_slug, label, fr) in enumerate(frames):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        pygame.draw.rect(canvas, (200, 170, 90),
                         pygame.Rect(x - 4, y - 4, cell_w + 8, cell_h + 8),
                         width=4)
        canvas.blit(fr, (x, y))
        lbl = font.render(label, True, (240, 210, 130))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2, y + cell_h + 12))

    cmp_path = os.path.join(out_dir, "pause_compare.png")
    pygame.image.save(canvas, cmp_path)
    print(f"saved {cmp_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    sys.exit(main() or 0)
