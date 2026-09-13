"""Preview 5 variants of "magnificent #1" styling on the top-10 screen.

Run from the repo root:  python tools/preview_crown_variants.py
Outputs:
  tools/screenshots/crown_v1.png  — Royal crown (clean perched crown)
  tools/screenshots/crown_v2.png  — Halo crown (V1 + pulsing gold halo)
  tools/screenshots/crown_v3.png  — Velvet throne (V1 + scarlet row)
  tools/screenshots/crown_v4.png  — Golden throne (V1 + gold row)
  tools/screenshots/crown_v5.png  — Imperial majesty (maximalist)
  tools/screenshots/crown_v6.png  — V4 chosen + silver/bronze medal rows

Nothing here lands in game/hud.py until the user picks a variant.
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import sys

import pygame
pygame.init()
pygame.font.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H, GROUND_Y
from game.draw import (
    WHITE, NEAR_BLACK,
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game import biome as _biome
from game.hud import (
    _font, _outlined_text,
    _GOLD_BRIGHT, _GOLD_MUTED, _GOLD_DEEP, _PANEL_DARK,
    _SCARLET_TOP,
    _draw_trophy,
)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def draw_bg(surf, scroll=0, phase=0.62):
    """Same biome-aware background as the shared screenshot harness.
    Inlined here instead of imported so we don't pull in the harness's
    `pygame.quit()` side effect at import time."""
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    t = bucket_f - int(bucket_f)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None); surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255)); surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, variant) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3,
                   sc, variant=variant)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W,
                   pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))


def _draw_crown(surf, cx, cy, size):
    """Procedural king's crown — three peaks with gems + jewelled band.
    Drawn fully symmetric about a vertical axis through (cx, cy).
    `size` is approximate half-width (good range: 8-14)."""
    s = size
    pad = 4
    g_w = s * 2 + pad * 2 + 1   # odd → exact centre column
    g_h = s + pad * 2 + 2
    g = pygame.Surface((g_w, g_h), pygame.SRCALPHA)
    gx = g_w // 2

    GOLD       = (240, 192,  64, 255)
    GOLD_LIGHT = (255, 230, 130, 255)
    GOLD_DARK  = (140,  90,   8, 255)
    RUBY       = (220,  50,  50, 255)
    RUBY_HI    = (255, 160, 160, 255)
    SAPPHIRE   = ( 60, 100, 220, 255)
    EMERALD    = ( 60, 200, 100, 255)

    band_h = max(4, s // 2)
    band_top = pad + s - band_h + 2
    band_bot = band_top + band_h
    band_left = pad
    band_right = pad + s * 2

    # Drop shadow under the band
    pygame.draw.rect(g, GOLD_DARK,
                     (band_left - 1, band_top + 1,
                      band_right - band_left + 2, band_h),
                     border_radius=2)
    # Gold band
    pygame.draw.rect(g, GOLD,
                     (band_left, band_top,
                      band_right - band_left, band_h),
                     border_radius=2)
    # Highlight strip on top of band
    pygame.draw.line(g, GOLD_LIGHT,
                     (band_left + 2, band_top + 1),
                     (band_right - 2, band_top + 1), 1)

    # Center peak (tallest)
    cp_tip = (gx, pad)
    cp_left = (gx - s // 3, band_top)
    cp_right = (gx + s // 3, band_top)
    pygame.draw.polygon(g, GOLD_DARK,
                        [(cp_tip[0], cp_tip[1] + 1),
                         (cp_left[0] - 1, cp_left[1] + 1),
                         (cp_right[0] + 1, cp_right[1] + 1)])
    pygame.draw.polygon(g, GOLD, [cp_tip, cp_left, cp_right])
    pygame.draw.line(g, GOLD_LIGHT, cp_tip,
                     ((cp_tip[0] + cp_left[0]) // 2,
                      (cp_tip[1] + cp_left[1]) // 2), 1)

    # Side peaks (shorter) — left, then mirror for right
    sp_h = max(3, (s * 2) // 3)
    sp_w = s - s // 3
    lp_tip = (gx - s + sp_w // 2, band_top - sp_h)
    lp_left = (gx - s, band_top)
    lp_right = (gx - s // 3, band_top)
    pygame.draw.polygon(g, GOLD_DARK,
                        [(lp_tip[0], lp_tip[1] + 1),
                         (lp_left[0] - 1, lp_left[1] + 1),
                         (lp_right[0], lp_right[1] + 1)])
    pygame.draw.polygon(g, GOLD, [lp_tip, lp_left, lp_right])

    rp_tip = (g_w - lp_tip[0] - 1, lp_tip[1])
    rp_left = (g_w - lp_left[0] - 1, lp_left[1])
    rp_right = (g_w - lp_right[0] - 1, lp_right[1])
    pygame.draw.polygon(g, GOLD_DARK,
                        [(rp_tip[0], rp_tip[1] + 1),
                         (rp_left[0] + 1, rp_left[1] + 1),
                         (rp_right[0], rp_right[1] + 1)])
    pygame.draw.polygon(g, GOLD, [rp_tip, rp_left, rp_right])

    # Gems on the peak tips
    pygame.draw.circle(g, RUBY, cp_tip, 2)
    pygame.draw.circle(g, RUBY_HI, (cp_tip[0] - 1, cp_tip[1] - 1), 1)
    pygame.draw.circle(g, SAPPHIRE, lp_tip, 1)
    pygame.draw.circle(g, EMERALD, rp_tip, 1)

    # Center gem on band
    band_cy = (band_top + band_bot) // 2
    pygame.draw.circle(g, RUBY, (gx, band_cy), 2)
    pygame.draw.circle(g, RUBY_HI, (gx - 1, band_cy - 1), 1)

    surf.blit(g, (cx - g_w // 2, cy - g_h // 2))


def draw_leaderboard_variant(surf, title_t, scores, player_rank, variant,
                             crown_drawer=None):
    """Replica of game.hud.HUD.draw_leaderboard with one extra knob
    (variant in 1..6) that controls the #1 row's chrome. Pass
    `crown_drawer=fn(surf, cx, cy)` to swap the perched-crown art."""
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((0, 0, 20, 200))
    surf.blit(dim, (0, 0))

    _outlined_text(surf, "TOP 10", (W // 2, 46), size=32, px=3)
    for side in (-1, 1):
        tx = W // 2 + side * 88
        ty = 46
        _draw_trophy(surf, tx, ty, 18)

    card_x, card_w = 14, W - 28

    slide_t = min(1.0, title_t / 0.4)
    e = slide_t * slide_t * (3 - 2 * slide_t)
    card_y = int(88 + (1.0 - e) * 80)

    row_h = 42
    row_gap = 4
    SILVER = (185, 195, 205)
    BRONZE = (185, 125,  55)

    f_badge = _font(13, True)
    f_name  = _font(16, True)
    f_you   = _font(10, True)
    f_score = _font(17, True)

    ry = card_y
    for i, entry in enumerate(scores):
        rank = i + 1
        if rank == 1:
            badge_col = _GOLD_BRIGHT
        elif rank == 2:
            badge_col = SILVER
        elif rank == 3:
            badge_col = BRONZE
        else:
            badge_col = _GOLD_BRIGHT

        is_player = (i == player_rank)
        row_cy = ry + row_h // 2
        row_rect = pygame.Rect(card_x, ry, card_w, row_h)
        row_radius = row_h // 2

        wants_crown    = (rank == 1)
        wants_halo     = (rank == 1) and variant in (2, 5)
        wants_velvet   = (rank == 1) and variant == 3
        wants_sparkles = (rank == 1) and variant == 5
        wants_big      = (rank == 1) and variant == 5

        # Decide the row's gradient (or None to fall back to dark navy):
        # — variant 4/5/6 use a gold gradient for #1
        # — variant 3 uses scarlet velvet for #1
        # — variant 6 ALSO paints silver / bronze rows for #2 / #3
        GOLD_GRAD   = ((240, 192,  64), (180, 130,  20))
        VELVET_GRAD = ((210,  36,  48), (120,  14,  26))
        SILVER_GRAD = ((215, 222, 232), (110, 125, 145))
        BRONZE_GRAD = ((215, 150,  85), (125,  74,  28))
        grad_top, grad_bot = None, None
        if rank == 1 and variant in (4, 5, 6):
            grad_top, grad_bot = GOLD_GRAD
        elif rank == 1 and variant == 3:
            grad_top, grad_bot = VELVET_GRAD
        elif rank == 2 and variant == 6:
            grad_top, grad_bot = SILVER_GRAD
        elif rank == 3 and variant == 6:
            grad_top, grad_bot = BRONZE_GRAD

        crown_size  = 14 if wants_big else 12
        badge_r     = 15 if wants_big else 13

        # ── pulsing gold halo BEHIND the row ───────────────────────────────
        if wants_halo:
            for offset, alpha_base in ((12, 35), (8, 70), (4, 120)):
                hw, hh = card_w + offset * 2, row_h + offset * 2
                halo = pygame.Surface((hw, hh), pygame.SRCALPHA)
                pygame.draw.rect(halo, (*_GOLD_BRIGHT, alpha_base),
                                 (0, 0, hw, hh),
                                 border_radius=row_radius + offset)
                surf.blit(halo, (card_x - offset, ry - offset))

        # ── row pill ────────────────────────────────────────────────────────
        pnl = pygame.Surface(row_rect.size, pygame.SRCALPHA)

        if grad_top is not None:
            # Vertical medal gradient (gold / velvet / silver / bronze)
            for yy in range(row_h):
                u = yy / max(1, row_h - 1)
                r  = int(grad_top[0] * (1 - u) + grad_bot[0] * u)
                g_ = int(grad_top[1] * (1 - u) + grad_bot[1] * u)
                b  = int(grad_top[2] * (1 - u) + grad_bot[2] * u)
                pygame.draw.line(pnl, (r, g_, b, 255),
                                 (0, yy), (card_w, yy))
            # Mask to rounded corners
            mask = pygame.Surface(row_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255),
                             (0, 0, card_w, row_h),
                             border_radius=row_radius)
            pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            # Border: velvet keeps the gold trim, all others use dark
            border_col = _GOLD_BRIGHT if wants_velvet else NEAR_BLACK
            pygame.draw.rect(pnl, border_col,
                             (0, 0, card_w, row_h),
                             width=2, border_radius=row_radius)
        else:
            pygame.draw.rect(pnl, (*_PANEL_DARK, 220),
                             (0, 0, card_w, row_h),
                             border_radius=row_radius)
            if is_player:
                pygame.draw.rect(pnl, _GOLD_BRIGHT,
                                 (0, 0, card_w, row_h),
                                 width=3, border_radius=row_radius)
            elif rank == 1:
                pygame.draw.rect(pnl, _GOLD_BRIGHT,
                                 (0, 0, card_w, row_h),
                                 width=2, border_radius=row_radius)
            else:
                pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 110),
                                 (0, 0, card_w, row_h),
                                 width=1, border_radius=row_radius)
        surf.blit(pnl, row_rect.topleft)

        # ── rank badge ──────────────────────────────────────────────────────
        badge_cx = card_x + 24
        if rank <= 3:
            this_r = badge_r if rank == 1 else 13
            pygame.draw.circle(surf, badge_col, (badge_cx, row_cy), this_r)
            pygame.draw.circle(surf, NEAR_BLACK,
                               (badge_cx, row_cy), this_r, 1)
            num_col = NEAR_BLACK
        else:
            pygame.draw.circle(surf, badge_col,
                               (badge_cx, row_cy), 13, 2)
            num_col = _GOLD_BRIGHT
        num_img = f_badge.render(str(rank), True, num_col)
        surf.blit(num_img,
                  num_img.get_rect(center=(badge_cx, row_cy)))

        # ── crown perched on top of #1's badge ─────────────────────────────
        if wants_crown:
            # Position so the crown's band overlaps the badge top by ~3px
            crown_cy = row_cy - badge_r - crown_size // 2 + 4
            if crown_drawer is None:
                _draw_crown(surf, badge_cx, crown_cy, crown_size)
            else:
                crown_drawer(surf, badge_cx, crown_cy)

        # ── sparkles around the crown (static for preview) ─────────────────
        if wants_sparkles:
            crown_cy = row_cy - badge_r - crown_size // 2 + 4
            cw = crown_size * 2 + 8   # crown half-width approx
            anchors = [
                (badge_cx - cw - 4, crown_cy - 6, 3, 220),
                (badge_cx + cw + 4, crown_cy - 6, 3, 220),
                (badge_cx - cw + 4, crown_cy + 12, 2, 160),
                (badge_cx + cw - 4, crown_cy + 12, 2, 160),
                (badge_cx,           crown_cy - crown_size - 4, 2, 200),
            ]
            for sx, sy, sz, a in anchors:
                star = pygame.Surface((sz * 2 + 3, sz * 2 + 3),
                                      pygame.SRCALPHA)
                col = (255, 250, 200, a)
                pygame.draw.line(star, col, (sz + 1, 0),
                                 (sz + 1, sz * 2 + 2), 1)
                pygame.draw.line(star, col, (0, sz + 1),
                                 (sz * 2 + 2, sz + 1), 1)
                pygame.draw.circle(star, (255, 255, 240, a),
                                   (sz + 1, sz + 1), 1)
                surf.blit(star, (sx - sz - 1, sy - sz - 1))

        # ── name + YOU badge + score ────────────────────────────────────────
        nm = entry["name"][:10]
        # Velvet row keeps white on red; all other gradient rows
        # (gold / silver / bronze) read better with dark text.
        if grad_top is not None and not wants_velvet:
            name_col = NEAR_BLACK
        elif wants_velvet:
            name_col = WHITE
        else:
            name_col = _GOLD_BRIGHT if is_player else WHITE
        nm_img = f_name.render(nm, True, name_col)
        nm_x = card_x + 44
        surf.blit(nm_img,
                  (nm_x, row_cy - nm_img.get_height() // 2))

        if is_player:
            you_img = f_you.render("YOU", True, WHITE)
            pw = you_img.get_width() + 10
            ph = you_img.get_height() + 6
            pxr = nm_x + nm_img.get_width() + 7
            pyr = row_cy - ph // 2
            you_pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pygame.draw.rect(you_pill, _SCARLET_TOP,
                             (0, 0, pw, ph), border_radius=ph // 2)
            pygame.draw.rect(you_pill, _GOLD_BRIGHT,
                             (0, 0, pw, ph),
                             width=1, border_radius=ph // 2)
            surf.blit(you_pill, (pxr, pyr))
            surf.blit(you_img, (pxr + 5, pyr + 3))

        if grad_top is not None and not wants_velvet:
            score_col = NEAR_BLACK
        else:
            score_col = _GOLD_BRIGHT
        sc_img = f_score.render(str(entry["score"]), True, score_col)
        surf.blit(sc_img,
                  (card_x + card_w - 16 - sc_img.get_width(),
                   row_cy - sc_img.get_height() // 2))

        ry += row_h + row_gap

    alpha = int(170 + math.sin(title_t * 4) * 70)
    f2 = _font(16, True)
    prompt = f2.render("TAP  TO  MENU", True, _GOLD_MUTED)
    prompt.set_alpha(alpha)
    pr = prompt.get_rect(center=(W // 2, H - 28))
    surf.blit(prompt, pr.topleft)


SCORES = [
    {"name": "Hawkins", "score": 148},
    {"name": "Garrick", "score": 132},
    {"name": "Atticus", "score": 117},
    {"name": "Mira",    "score": 104},
    {"name": "Quill",   "score":  96},
    {"name": "Bo",      "score":  83},
    {"name": "Pip",     "score":  42},
    {"name": "Wren",    "score":  38},
    {"name": "Stilt",   "score":  29},
    {"name": "Cinder",  "score":  18},
]


def main():
    screen = pygame.Surface((W, H))
    for variant in (1, 2, 3, 4, 5, 6):
        draw_bg(screen)
        draw_leaderboard_variant(
            screen, title_t=1.4, scores=SCORES,
            player_rank=6, variant=variant)
        out = os.path.join(OUT_DIR, f"crown_v{variant}.png")
        pygame.image.save(screen, out)
        print(f"saved {out}")


if __name__ == "__main__":
    main()
