import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
sys.path.insert(0, os.path.dirname(__file__))

import pygame
pygame.init()

from game.config import W, H
from game.scenes import App, STATE_MENU
from game.hud import _volume_panel, _draw_trophy, _font, _GOLD_PALE, _GOLD_BRIGHT
import stars as S

# ── Live menu base frame ────────────────────────────────────────────────────
app = App()
app.state = STATE_MENU
for _ in range(3):
    app.world.update(1 / 60)
app._render()
base = app.screen.copy()


def tile_frame(star_fn):
    """The live menu with the bottom row replaced by AWARDS(star) + TOP 10."""
    frame = base.copy()
    bg = frame.get_at((6, 490))
    frame.fill(bg, (0, 466, W, H - 466))

    panel_w, gap = 132, 8
    total_w = panel_w * 2 + gap
    left_x = (W - total_w) // 2
    cy = H - 86
    lf = _font(13, True)

    # AWARDS tile (left) with the candidate star.
    awd_cx = left_x + panel_w // 2
    awd_rect = pygame.Rect(left_x, cy - 24, panel_w, 48)
    _volume_panel(frame, awd_rect, radius=14)
    lbl = lf.render("A W A R D S", True, _GOLD_PALE)
    lbl.set_alpha(230)
    frame.blit(lbl, lbl.get_rect(center=(awd_cx, cy - 12)))
    star_fn(frame, awd_cx, cy + 7, 10)

    # Real TOP 10 tile (right) for sibling pairing.
    top_cx = left_x + panel_w + gap + panel_w // 2
    top_rect = pygame.Rect(left_x + panel_w + gap, cy - 24, panel_w, 48)
    _volume_panel(frame, top_rect, radius=14)
    top_lbl = lf.render("T O P  10", True, _GOLD_PALE)
    top_lbl.set_alpha(230)
    frame.blit(top_lbl, top_lbl.get_rect(center=(top_cx, cy - 12)))
    _draw_trophy(frame, top_cx, cy + 6, 9)
    return frame


# ── Candidate sheet layout ──────────────────────────────────────────────────
PAD = 26
COL_W = W                       # each in-context column is a full menu frame
DETAIL = 128                    # bare-star detail cell size
N = len(S.STARS)

sheet_w = PAD + N * (COL_W + PAD)
detail_row_h = DETAIL + 64
sheet_h = PAD + 40 + detail_row_h + PAD + H + PAD + 30

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 22, 34))

title = _font(30, True).render("Skybit — AWARDS star emblem · Round 1 · 5 candidates",
                               True, _GOLD_BRIGHT)
sheet.blit(title, (PAD, 14))

lab = _font(15, True).render("Detail (bare emblem @120px, supersampled)",
                             True, _GOLD_PALE)
sheet.blit(lab, (PAD, 54))

detail_y = PAD + 56
for i, (name, fn) in enumerate(S.STARS):
    x = PAD + i * (COL_W + PAD)
    cell = pygame.Rect(x, detail_y, COL_W, DETAIL + 8)
    pygame.draw.rect(sheet, (30, 34, 50), cell, border_radius=10)
    pygame.draw.rect(sheet, (70, 80, 110), cell, width=1, border_radius=10)
    # Bare star large — scale the same crisp emblem up to ~120px.
    big = pygame.Surface((DETAIL, DETAIL), pygame.SRCALPHA)
    fn(big, DETAIL // 2, DETAIL // 2, DETAIL * 0.40)
    sheet.blit(big, (x + (COL_W - DETAIL) // 2, detail_y + 4))
    nm = _font(17, True).render(f"{i+1}. {name}", True, (235, 238, 248))
    sheet.blit(nm, nm.get_rect(center=(x + COL_W // 2, detail_y + DETAIL + 22)))

# In-context menu row.
ctx_y = detail_y + detail_row_h + 8
lab2 = _font(15, True).render("In situ — AWARDS tile (candidate star) beside the live TOP 10 tile",
                              True, _GOLD_PALE)
sheet.blit(lab2, (PAD, ctx_y - 24))
for i, (name, fn) in enumerate(S.STARS):
    x = PAD + i * (COL_W + PAD)
    frame = tile_frame(fn)
    sheet.blit(frame, (x, ctx_y))
    pygame.draw.rect(sheet, (70, 80, 110), (x, ctx_y, W, H), width=1)

out = "/home/user/skybit/docs/menu_profile_concepts/star_options/round_1.png"
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
