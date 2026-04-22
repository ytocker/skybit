"""HUD: score, hi-score, coin count, mushroom timer bar, combo, pause button."""
import math
import pygame

from game.config import W, H, TRIPLE_DURATION
from game.draw import (
    rounded_rect, rounded_rect_grad, blit_glow,
    UI_SCORE, UI_GOLD, UI_ORANGE, UI_SHADOW, UI_CREAM, UI_RED,
    COIN_GOLD, COIN_LIGHT, COIN_DARK,
    WHITE, NEAR_BLACK,
)


_fonts: dict = {}


def _font(size, bold=True):
    k = (size, bold)
    f = _fonts.get(k)
    if f is None:
        f = pygame.font.SysFont("arial", size, bold=bold)
        _fonts[k] = f
    return f


def _text(surf, txt, center, size=36, color=WHITE, shadow=True):
    f = _font(size, True)
    img = f.render(txt, True, color)
    r = img.get_rect(center=center)
    if shadow:
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(170)
        surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(img, r.topleft)
    return r


def _coin_icon(surf, cx, cy, r=10):
    blit_glow(surf, cx, cy, r + 4, COIN_GOLD, 120)
    pygame.draw.circle(surf, COIN_DARK, (cx, cy), r + 1)
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r)
    pygame.draw.ellipse(surf, COIN_LIGHT, (cx - r + 2, cy - r + 2, r - 1, r - 4))


class PauseButton:
    def __init__(self):
        self.rect = pygame.Rect(W - 56, 12, 44, 44)
        self.hover = False

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surf, paused=False):
        rounded_rect(surf, self.rect, 10, (255, 255, 255), 60)
        rounded_rect(surf, self.rect, 10, (20, 30, 60), 110)
        # draw bars or play triangle
        cx, cy = self.rect.center
        if paused:
            pygame.draw.polygon(surf, WHITE, [
                (cx - 7, cy - 10),
                (cx - 7, cy + 10),
                (cx + 9, cy),
            ])
        else:
            pygame.draw.rect(surf, WHITE, (cx - 8, cy - 10, 5, 20), border_radius=2)
            pygame.draw.rect(surf, WHITE, (cx + 3, cy - 10, 5, 20), border_radius=2)


class HUD:
    def __init__(self):
        self.pause_btn = PauseButton()
        self.title_t = 0.0

    def draw_play(self, surf, world, best: int):
        # Score — large, centered under status strip
        score_txt = str(world.score)
        cf = _font(48, True)
        img = cf.render(score_txt, True, UI_SCORE)
        shadow = cf.render(score_txt, True, NEAR_BLACK)
        outline = cf.render(score_txt, True, UI_GOLD)
        r = img.get_rect(center=(W // 2, 72))
        # gold outline by offsetting
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            surf.blit(outline, (r.x + ox, r.y + oy))
        surf.blit(shadow, (r.x + 3, r.y + 4))
        surf.blit(img, r.topleft)

        # Hi-score pill
        hi_rect = pygame.Rect(10, 14, 94, 34)
        rounded_rect(surf, hi_rect, 12, (15, 25, 60), 200)
        # trophy icon (stylised cup) on the left
        tx, ty = hi_rect.x + 18, hi_rect.y + 17
        pygame.draw.polygon(surf, UI_GOLD, [
            (tx - 7, ty - 7), (tx + 7, ty - 7),
            (tx + 5, ty + 3), (tx - 5, ty + 3),
        ])
        pygame.draw.rect(surf, UI_GOLD, (tx - 3, ty + 3, 6, 4))
        pygame.draw.rect(surf, UI_GOLD, (tx - 6, ty + 7, 12, 3), border_radius=2)
        # label + value stacked
        _text(surf, "BEST", (hi_rect.x + 60, hi_rect.y + 11), size=12, color=UI_CREAM, shadow=False)
        _text(surf, str(best), (hi_rect.x + 60, hi_rect.y + 23), size=15, color=UI_GOLD, shadow=False)

        # Coin count (top-right, just left of pause button)
        cc_rect = pygame.Rect(W - 156, 14, 88, 34)
        rounded_rect(surf, cc_rect, 12, (15, 25, 60), 170)
        _coin_icon(surf, cc_rect.x + 18, cc_rect.y + 17, 10)
        _text(surf, f"x{world.coin_count}", (cc_rect.x + 54, cc_rect.y + 18), size=18, color=UI_GOLD, shadow=False)

        # Pause button
        self.pause_btn.draw(surf, paused=False)

        # Mushroom timer bar under score
        if world.triple_timer > 0:
            frac = world.triple_timer / TRIPLE_DURATION
            bw = 180
            bx = (W - bw) // 2
            by = 160
            _text(surf, "3X POWER", (W // 2, by - 10), size=14, color=UI_ORANGE, shadow=True)
            rounded_rect(surf, pygame.Rect(bx - 2, by, bw + 4, 16), 8, (30, 30, 60), 200)
            fill = pygame.Rect(bx, by + 2, int(bw * frac), 12)
            if fill.width > 0:
                rounded_rect_grad(surf, fill, 6, UI_ORANGE, UI_GOLD)

        # Combo badge bottom-center
        if world.combo >= 3 and world.combo_timer > 0:
            t = world.combo_timer / 1.6
            scale = 1.0 + math.sin(self.title_t * 12) * 0.08
            size = int(22 * scale)
            color = UI_ORANGE if world.combo < 5 else UI_RED
            f = _font(size, True)
            txt = f"X{world.combo} COMBO"
            img = f.render(txt, True, color)
            sh = f.render(txt, True, NEAR_BLACK)
            rr = img.get_rect(center=(W // 2, H - 60))
            sh.set_alpha(int(230 * t))
            img.set_alpha(int(255 * t))
            surf.blit(sh, (rr.x + 2, rr.y + 2))
            surf.blit(img, rr.topleft)

        # Float texts
        for ft in world.float_texts:
            ft.draw(surf)

    def draw_menu(self, surf, dt, best: int):
        self.title_t += dt
        # Faded dim layer
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 10, 70))
        surf.blit(dim, (0, 0))
        # Title pulsing
        pulse = 1.0 + math.sin(self.title_t * 2.4) * 0.04
        f = _font(int(68 * pulse), True)
        title = "Skybit"
        img = f.render(title, True, UI_GOLD)
        shadow = f.render(title, True, NEAR_BLACK)
        outline = f.render(title, True, UI_RED)
        r = img.get_rect(center=(W // 2, 180))
        for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3), (2, 2), (-2, 2)):
            surf.blit(outline, (r.x + ox, r.y + oy))
        surf.blit(shadow, (r.x + 3, r.y + 5))
        surf.blit(img, r.topleft)
        # Subtitle
        _text(surf, "Pocket Sky Flyer", (W // 2, 228), size=18, color=UI_CREAM)
        # Tap to start
        alpha = int(160 + math.sin(self.title_t * 3.6) * 90)
        f2 = _font(24, True)
        prompt = f2.render("TAP  ·  SPACE  ·  CLICK", True, WHITE)
        prompt.set_alpha(alpha)
        pr = prompt.get_rect(center=(W // 2, H - 170))
        surf.blit(prompt, pr.topleft)
        _text(surf, "to flap and start", (W // 2, H - 142), size=16, color=UI_CREAM)

        # Best pill
        hi_rect = pygame.Rect(W // 2 - 60, H - 100, 120, 40)
        rounded_rect(surf, hi_rect, 12, (15, 25, 60), 180)
        _text(surf, "BEST", (hi_rect.centerx, hi_rect.y + 12), size=14, color=UI_CREAM, shadow=False)
        _text(surf, str(best), (hi_rect.centerx, hi_rect.y + 28), size=18, color=UI_GOLD, shadow=False)

    def draw_gameover(self, surf, dt, score: int, scores: list, new_best: bool, highlight_rank=-1):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 170))
        surf.blit(dim, (0, 0))

        # Top band — score + game over label
        _text(surf, "GAME OVER", (W // 2, 80), size=30, color=UI_RED)
        if score > 0:
            _text(surf, "SCORE", (W // 2, 118), size=13, color=UI_CREAM, shadow=False)
            _text(surf, str(score), (W // 2, 148), size=38, color=UI_GOLD)
            if new_best:
                pulse = 1 + math.sin(self.title_t * 6) * 0.1
                _text(surf, "NEW BEST!", (W // 2, 182), size=int(17 * pulse), color=UI_ORANGE)
        else:
            # Dying before the first pipe shouldn't read as a graded result.
            pulse = 1 + math.sin(self.title_t * 4) * 0.05
            _text(surf, "TRY AGAIN!", (W // 2, 138), size=int(26 * pulse),
                  color=UI_ORANGE)

        # Leaderboard card
        self._draw_leaderboard(surf, y_top=200, highlight_rank=highlight_rank, scores=scores)

        alpha = int(150 + math.sin(self.title_t * 4) * 90)
        f = _font(20, True)
        t = f.render("TAP TO RETRY", True, WHITE)
        t.set_alpha(alpha)
        r = t.get_rect(center=(W // 2, H - 48))
        surf.blit(t, r.topleft)

    def _draw_leaderboard(self, surf, y_top: int, highlight_rank: int, scores: list):
        card_h = 330
        card = pygame.Rect(20, y_top, W - 40, card_h)
        rounded_rect(surf, card, 14, (15, 25, 60), 220)
        _text(surf, "TOP 10", (card.centerx, card.y + 18), size=16, color=UI_GOLD, shadow=False)

        f_row = _font(15, True)
        f_small = _font(14, False)
        row_y = card.y + 46
        muted = (110, 130, 170)
        for i in range(10):
            filled = i < len(scores)
            if filled:
                entry = scores[i]
                name = entry["name"]
                score = entry["score"]
            else:
                name = "---"
                score = None
            bg_col = (40, 60, 120) if i == highlight_rank else None
            if bg_col is not None:
                rr = pygame.Rect(card.x + 8, row_y - 10, card.width - 16, 24)
                rounded_rect(surf, rr, 6, bg_col, 200)
            if filled:
                rank_color = UI_GOLD if i == 0 else (UI_ORANGE if i == 1 else (UI_CREAM if i == 2 else WHITE))
                name_color = WHITE
                score_color = UI_GOLD
            else:
                rank_color = name_color = score_color = muted
            rank_img = f_row.render(f"{i + 1:>2}.", True, rank_color)
            surf.blit(rank_img, (card.x + 16, row_y - 8))
            name_img = f_row.render(name, True, name_color)
            surf.blit(name_img, (card.x + 62, row_y - 8))
            if score is not None:
                score_img = f_row.render(str(score), True, score_color)
                sr = score_img.get_rect()
                sr.topright = (card.right - 20, row_y - 8)
                surf.blit(score_img, sr.topleft)
            row_y += 26
