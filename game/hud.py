"""HUD: score, hi-score, coin count, mushroom timer bar, combo, pause button."""
import math
import os
import pygame

from game.config import W, H, TRIPLE_DURATION, MAGNET_DURATION, SLOWMO_DURATION
from game.draw import (
    rounded_rect, rounded_rect_grad, lerp_color,
    UI_SCORE, UI_GOLD, UI_ORANGE, UI_SHADOW, UI_CREAM, UI_RED,
    COIN_GOLD, COIN_DARK,
    WHITE, NEAR_BLACK,
)


_fonts: dict = {}


# Vendored Liberation Sans (metric-compatible Arial replacement) so the
# browser/pygbag build doesn't depend on a system font that isn't there.
_FONT_DIR = os.path.join(os.path.dirname(__file__), "assets")
_FONT_BOLD = os.path.join(_FONT_DIR, "LiberationSans-Bold.ttf")
_FONT_REG  = os.path.join(_FONT_DIR, "LiberationSans-Regular.ttf")


def _font(size, bold=True):
    k = (size, bold)
    f = _fonts.get(k)
    if f is None:
        path = _FONT_BOLD if bold else _FONT_REG
        f = pygame.font.Font(path, size)
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
    # Match in-world Coin.draw: dark rim + gold body + embossed parrot.
    # No halo, no pale highlight.
    pygame.draw.circle(surf, COIN_DARK, (cx, cy), r + 1)
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r)
    emboss = (140, 85, 0)
    pygame.draw.ellipse(surf, emboss, (cx - 2, cy - 1, 7, 5))
    pygame.draw.circle(surf, emboss, (cx - 1, cy - 3), 3)
    pygame.draw.polygon(surf, emboss,
                        [(cx - 3, cy - 3), (cx - 6, cy - 2), (cx - 3, cy - 1)])
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy - 4), 1)


def _draw_buff_icon(surf, rect, kind):
    """Tiny 20x20-ish icon for an active buff. Matches in-world sprites."""
    cx, cy = rect.center
    if kind == "triple":
        # Red mushroom cap + stem
        pygame.draw.rect(surf, (245, 225, 195), (cx - 3, cy + 1, 6, 7), border_radius=1)
        pygame.draw.ellipse(surf, (130, 10, 20),
                            (cx - 9, cy - 6, 18, 10))
        pygame.draw.ellipse(surf, (220, 30, 30),
                            (cx - 8, cy - 5, 16, 8))
        pygame.draw.circle(surf, WHITE, (cx - 3, cy - 3), 1)
        pygame.draw.circle(surf, WHITE, (cx + 3, cy - 2), 1)
    elif kind == "magnet":
        # Horseshoe U
        pygame.draw.arc(surf, (220, 30, 40),
                        (cx - 8, cy - 7, 16, 14),
                        math.pi, 2 * math.pi, 4)
        pygame.draw.rect(surf, (220, 30, 40), (cx - 8, cy, 3, 7))
        pygame.draw.rect(surf, (220, 30, 40), (cx + 5, cy, 3, 7))
        pygame.draw.rect(surf, (220, 220, 235), (cx - 8, cy + 4, 3, 3))
        pygame.draw.rect(surf, (220, 220, 235), (cx + 5, cy + 4, 3, 3))
    elif kind == "slowmo":
        top = [(cx - 6, cy - 7), (cx + 6, cy - 7), (cx, cy)]
        bot = [(cx - 6, cy + 7), (cx + 6, cy + 7), (cx, cy)]
        pygame.draw.polygon(surf, (140, 70, 210), top)
        pygame.draw.polygon(surf, (140, 70, 210), bot)
        pygame.draw.line(surf, (255, 230, 150), (cx, cy - 4), (cx, cy + 4), 2)
        pygame.draw.rect(surf, (120, 60, 30), (cx - 7, cy - 9, 14, 2))
        pygame.draw.rect(surf, (120, 60, 30), (cx - 7, cy + 7, 14, 2))


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

    def draw_pause_overlay(self, surf):
        self.title_t += 1 / 60
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 150))
        surf.blit(dim, (0, 0))
        pulse = 1.0 + math.sin(self.title_t * 2.6) * 0.04
        f = _font(int(56 * pulse), True)
        title = "PAUSED"
        img = f.render(title, True, UI_GOLD)
        shadow = f.render(title, True, NEAR_BLACK)
        outline = f.render(title, True, UI_RED)
        r = img.get_rect(center=(W // 2, H // 2 - 30))
        for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            surf.blit(outline, (r.x + ox, r.y + oy))
        surf.blit(shadow, (r.x + 3, r.y + 5))
        surf.blit(img, r.topleft)
        alpha = int(160 + math.sin(self.title_t * 3.6) * 90)
        f2 = _font(20, True)
        prompt = f2.render("TAP  ·  P  ·  ESC", True, WHITE)
        prompt.set_alpha(alpha)
        pr = prompt.get_rect(center=(W // 2, H // 2 + 24))
        surf.blit(prompt, pr.topleft)
        _text(surf, "to resume", (W // 2, H // 2 + 52), size=16, color=UI_CREAM)

    def draw_play(self, surf, world, best: int, paused: bool = False):
        # ── Score: centered, with a soft dark backdrop so the digits stay
        # legible against any sky/pillar/cloud behind them.
        score_txt = str(world.score)
        cf = _font(48, True)
        img = cf.render(score_txt, True, UI_SCORE)
        shadow = cf.render(score_txt, True, NEAR_BLACK)
        outline = cf.render(score_txt, True, UI_GOLD)
        r = img.get_rect(center=(W // 2, 72))
        # Soft dark ellipse behind the score, wider+shorter than the text
        back_w = r.width + 48
        back_h = r.height + 18
        back = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
        pygame.draw.ellipse(back, (0, 0, 20, 100), back.get_rect())
        pygame.draw.ellipse(back, (0, 0, 20, 70), back.get_rect().inflate(20, 10))
        surf.blit(back, (W // 2 - back_w // 2, r.y - 9))
        # gold outline by offsetting
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            surf.blit(outline, (r.x + ox, r.y + oy))
        surf.blit(shadow, (r.x + 3, r.y + 4))
        surf.blit(img, r.topleft)

        # ── Top-left BEST pill and top-right coin pill fade out when the
        # bird flies up into the upper 60 px so the player never loses the
        # sprite behind UI chrome.
        bird_y = world.bird.y
        if bird_y >= 80:
            ui_alpha = 255
        elif bird_y <= 20:
            ui_alpha = 40
        else:
            ui_alpha = int(40 + (215 * (bird_y - 20) / 60))

        hi_pill = pygame.Surface((94, 34), pygame.SRCALPHA)
        rounded_rect(hi_pill, hi_pill.get_rect(), 12, (15, 25, 60), 200)
        tx, ty = 18, 17
        pygame.draw.polygon(hi_pill, UI_GOLD, [
            (tx - 7, ty - 7), (tx + 7, ty - 7),
            (tx + 5, ty + 3), (tx - 5, ty + 3),
        ])
        pygame.draw.rect(hi_pill, UI_GOLD, (tx - 3, ty + 3, 6, 4))
        pygame.draw.rect(hi_pill, UI_GOLD, (tx - 6, ty + 7, 12, 3), border_radius=2)
        _text(hi_pill, "BEST", (60, 11), size=12, color=UI_CREAM, shadow=False)
        _text(hi_pill, str(best), (60, 23), size=15, color=UI_GOLD, shadow=False)
        hi_pill.set_alpha(ui_alpha)
        surf.blit(hi_pill, (10, 14))

        cc_pill = pygame.Surface((88, 34), pygame.SRCALPHA)
        rounded_rect(cc_pill, cc_pill.get_rect(), 12, (15, 25, 60), 170)
        _coin_icon(cc_pill, 18, 17, 10)
        _text(cc_pill, f"x{world.coin_count}", (54, 18),
              size=18, color=UI_GOLD, shadow=False)
        cc_pill.set_alpha(ui_alpha)
        surf.blit(cc_pill, (W - 156, 14))

        # Pause button
        self.pause_btn.draw(surf, paused=paused)

        # "Get ready" prompt while the pre-start freeze is active.
        if world.ready_t > 0:
            pulse = 0.5 + 0.5 * math.sin(self.title_t * 5)
            alpha = int(180 + 60 * pulse)
            font_big = _font(22, True)
            label = font_big.render("TAP TO FLY", True, WHITE)
            label.set_alpha(alpha)
            lr = label.get_rect(center=(W // 2, 340))
            # dark plate behind for legibility
            plate = pygame.Surface((lr.width + 36, lr.height + 18),
                                   pygame.SRCALPHA)
            pygame.draw.ellipse(plate, (0, 0, 20, 140), plate.get_rect())
            surf.blit(plate, (W // 2 - plate.get_width() // 2,
                              lr.y - 9))
            surf.blit(label, lr.topleft)

        # Mushroom (3x-coin) timer bar — depletes gold → orange → red so the
        # urgency is obvious at a glance. Pulses in the last two seconds.
        if world.triple_timer > 0:
            frac = world.triple_timer / TRIPLE_DURATION
            bw = 168
            bx = (W - bw) // 2
            by = 128
            # Label above the track
            label_col = UI_RED if frac < 0.25 else UI_ORANGE
            _text(surf, f"3X POWER  {world.triple_timer:.1f}s",
                  (W // 2, by - 10), size=13, color=label_col, shadow=True)
            # Track
            track_rect = pygame.Rect(bx - 2, by, bw + 4, 12)
            rounded_rect(surf, track_rect, 6, (20, 25, 50), 200)
            # Fill — color lerps with remaining time, pulses when critical
            if frac > 0.5:
                fill_lo = UI_ORANGE
                fill_hi = UI_GOLD
            elif frac > 0.25:
                t = (frac - 0.25) / 0.25
                fill_lo = lerp_color(UI_RED, UI_ORANGE, t)
                fill_hi = lerp_color(UI_ORANGE, UI_GOLD, t)
            else:
                fill_lo = (180, 20, 20)
                fill_hi = UI_RED
            fill = pygame.Rect(bx, by + 2, int(bw * frac), 8)
            if fill.width > 0:
                rounded_rect_grad(surf, fill, 4, fill_hi, fill_lo)
            # Low-time pulse ring
            if frac < 0.25:
                pulse = 0.5 + 0.5 * math.sin(self.title_t * 14)
                ring_a = int(140 * pulse)
                ring = pygame.Surface((bw + 10, 18), pygame.SRCALPHA)
                pygame.draw.rect(ring, (*UI_RED, ring_a), ring.get_rect(),
                                 border_radius=8, width=2)
                surf.blit(ring, (bx - 5, by - 3))

        # Active-buff strip (magnet + slowmo badges). Triple has its own
        # bigger timer bar above, so we don't duplicate it here.
        active = []
        if world.magnet_timer > 0:
            active.append(("magnet", world.magnet_timer, MAGNET_DURATION))
        if world.slowmo_timer > 0:
            active.append(("slowmo", world.slowmo_timer, SLOWMO_DURATION))
        if active:
            slot_w, slot_h = 28, 32
            gap = 6
            strip_w = len(active) * slot_w + (len(active) - 1) * gap
            sx = (W - strip_w) // 2
            sy = H - 108
            for i, (kind, remain, total) in enumerate(active):
                r = pygame.Rect(sx + i * (slot_w + gap), sy, slot_w, slot_h)
                rounded_rect(surf, r, 6, (15, 25, 60), 190)
                _draw_buff_icon(surf, r.inflate(-6, -14).move(0, -2), kind)
                if remain is not None and total:
                    frac = max(0.0, min(1.0, remain / total))
                    bar_rect = pygame.Rect(r.x + 3, r.bottom - 6, r.width - 6, 3)
                    pygame.draw.rect(surf, (25, 25, 50), bar_rect, border_radius=1)
                    fw = int(bar_rect.width * frac)
                    if fw > 0:
                        pygame.draw.rect(surf, UI_GOLD,
                                         (bar_rect.x, bar_rect.y, fw, bar_rect.height),
                                         border_radius=1)

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

    def draw_stats(self, surf, world, dt, elapsed):
        """Post-run summary: score + coins + combo + pillars + time + near-misses
        + power-up counters. Taps (after a short lockout) advance to the
        leaderboard/name-entry; auto-advances after ~4.5 s."""
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 180))
        surf.blit(dim, (0, 0))

        # Slide-in animation from below
        slide_t = max(0.0, min(1.0, elapsed / 0.35))
        e = slide_t * slide_t * (3 - 2 * slide_t)
        card_y = int(60 + (1.0 - e) * 60)

        _text(surf, "RUN SUMMARY", (W // 2, card_y), size=22, color=UI_GOLD)

        # Score headline
        _text(surf, str(world.score), (W // 2, card_y + 50), size=48, color=UI_GOLD)
        _text(surf, "SCORE", (W // 2, card_y + 82), size=12, color=UI_CREAM, shadow=False)

        # Stats card
        mins = int(world.time_alive) // 60
        secs = int(world.time_alive) % 60
        time_str = f"{mins}:{secs:02d}" if mins else f"{secs}s"

        rows = [
            ("Coins", str(world.coin_count)),
            ("Max combo", f"x{world.max_combo}" if world.max_combo > 1 else "—"),
            ("Pillars cleared", str(world.pillars_passed)),
            ("Near misses", str(world.near_misses)),
            ("Time alive", time_str),
        ]
        total_pu = sum(world.powerups_picked.values())
        if total_pu > 0:
            rows.append(("Power-ups", str(total_pu)))

        card_rect = pygame.Rect(22, card_y + 104, W - 44, len(rows) * 30 + 24)
        rounded_rect(surf, card_rect, 14, (15, 25, 60), 220)

        f_key = _font(16, True)
        f_val = _font(18, True)
        ry = card_rect.y + 16
        for label, value in rows:
            k_img = f_key.render(label.upper(), True, UI_CREAM)
            v_img = f_val.render(value, True, UI_GOLD)
            surf.blit(k_img, (card_rect.x + 18, ry))
            vr = v_img.get_rect()
            vr.topright = (card_rect.right - 18, ry - 2)
            surf.blit(v_img, vr.topleft)
            ry += 30

        # Continue prompt (fades in after short lockout)
        if elapsed >= 0.6:
            alpha = int(120 + math.sin(self.title_t * 4) * 90)
            alpha = max(60, min(220, alpha))
            f = _font(18, True)
            t = f.render("TAP TO CONTINUE", True, WHITE)
            t.set_alpha(alpha)
            pr = t.get_rect(center=(W // 2, H - 56))
            surf.blit(t, pr.topleft)

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
