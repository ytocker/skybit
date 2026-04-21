"""
Arcade-style 3-letter-initials name entry with an on-screen keyboard.
Works on mobile (tap), desktop mouse (click), and physical keyboard
(A-Z, Backspace, Enter).
"""
import pygame

from game.config import W, H
from game.draw import (
    rounded_rect, UI_GOLD, UI_ORANGE, UI_CREAM, UI_RED, WHITE, NEAR_BLACK,
)

LETTERS = [
    "ABCDEFG",
    "HIJKLMN",
    "OPQRSTU",
    "VWXYZ_?",
]

KEY_W = 40
KEY_H = 40
KEY_GAP = 4


class NameEntry:
    """Owned by the App while in the name-entry scene."""

    def __init__(self, score: int, rank: int):
        self.score = score
        self.rank = rank
        self.chars = ["A", " ", " "]
        self.pos = 0  # which slot is active
        self.done = False
        self.submitted_name: str | None = None
        self.t = 0.0

        # Build keyboard layout
        self.keys: list[tuple[pygame.Rect, str]] = []
        rows = len(LETTERS)
        cols = len(LETTERS[0])
        board_w = cols * KEY_W + (cols - 1) * KEY_GAP
        x0 = (W - board_w) // 2
        y0 = 380
        for r, row in enumerate(LETTERS):
            for c, ch in enumerate(row):
                rect = pygame.Rect(
                    x0 + c * (KEY_W + KEY_GAP),
                    y0 + r * (KEY_H + KEY_GAP),
                    KEY_W, KEY_H,
                )
                self.keys.append((rect, ch))

        # Action buttons
        act_y = y0 + rows * (KEY_H + KEY_GAP) + 8
        self.back_rect = pygame.Rect(x0, act_y, (board_w - KEY_GAP) // 2, 40)
        self.ok_rect = pygame.Rect(self.back_rect.right + KEY_GAP, act_y,
                                   (board_w - KEY_GAP) // 2, 40)

    # ── input ────────────────────────────────────────────────────────────────

    def press_char(self, ch: str):
        ch = ch.upper()
        if ch == "_":
            ch = " "
        if ch == "?":
            ch = "."
        self.chars[self.pos] = ch
        if self.pos < 2:
            self.pos += 1

    def backspace(self):
        if self.chars[self.pos] != " ":
            self.chars[self.pos] = " "
        elif self.pos > 0:
            self.pos -= 1
            self.chars[self.pos] = " "

    def submit(self):
        name = "".join(self.chars).strip().replace(" ", "")
        if not name:
            name = "???"
        self.submitted_name = name[:3].upper()
        self.done = True

    def handle_tap(self, pos):
        for rect, ch in self.keys:
            if rect.collidepoint(pos):
                self.press_char(ch)
                return True
        if self.back_rect.collidepoint(pos):
            self.backspace()
            return True
        if self.ok_rect.collidepoint(pos):
            self.submit()
            return True
        # tap on one of the three letter slots to select it
        for i in range(3):
            r = self._slot_rect(i)
            if r.collidepoint(pos):
                self.pos = i
                return True
        return False

    def handle_key(self, ev: pygame.event.Event):
        if ev.key == pygame.K_BACKSPACE:
            self.backspace()
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.submit()
        elif ev.key == pygame.K_LEFT:
            self.pos = max(0, self.pos - 1)
        elif ev.key == pygame.K_RIGHT:
            self.pos = min(2, self.pos + 1)
        else:
            u = ev.unicode
            if u and (u.isalnum()):
                self.press_char(u)

    # ── drawing ──────────────────────────────────────────────────────────────

    def _slot_rect(self, i):
        slot_w = 60
        gap = 10
        total = 3 * slot_w + 2 * gap
        x0 = (W - total) // 2
        return pygame.Rect(x0 + i * (slot_w + gap), 240, slot_w, 80)

    def update(self, dt):
        self.t += dt

    def draw(self, surf, font_factory):
        # Dim background
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 180))
        surf.blit(dim, (0, 0))

        # Title
        f_title = font_factory(26, True)
        title = f_title.render("NEW HIGH SCORE!", True, UI_ORANGE)
        sh = f_title.render("NEW HIGH SCORE!", True, NEAR_BLACK)
        r = title.get_rect(center=(W // 2, 140))
        surf.blit(sh, (r.x + 2, r.y + 2))
        surf.blit(title, r.topleft)

        # Rank + score
        f_sub = font_factory(16, True)
        sub = f_sub.render(f"Rank #{self.rank + 1}    Score {self.score}", True, UI_CREAM)
        surf.blit(sub, sub.get_rect(center=(W // 2, 176)))

        # Instructions
        f_small = font_factory(13, False)
        info = f_small.render("Enter your initials (tap keys or type)", True, WHITE)
        surf.blit(info, info.get_rect(center=(W // 2, 204)))

        # 3 letter slots
        f_slot = font_factory(46, True)
        for i in range(3):
            rect = self._slot_rect(i)
            bg = (30, 40, 80) if i != self.pos else (60, 80, 140)
            rounded_rect(surf, rect, 12, bg, 230)
            border = UI_GOLD if i == self.pos else (80, 100, 170)
            pygame.draw.rect(surf, border, rect, 3, border_radius=12)
            ch = self.chars[i]
            if ch == " ":
                # blinking underline
                if int(self.t * 2) % 2 == 0 and i == self.pos:
                    pygame.draw.line(surf, UI_GOLD,
                                     (rect.x + 12, rect.bottom - 14),
                                     (rect.right - 12, rect.bottom - 14), 3)
            else:
                img = f_slot.render(ch, True, WHITE)
                surf.blit(img, img.get_rect(center=rect.center))

        # Keyboard
        f_key = font_factory(20, True)
        for rect, ch in self.keys:
            rounded_rect(surf, rect, 8, (30, 40, 80), 220)
            pygame.draw.rect(surf, (80, 100, 170), rect, 1, border_radius=8)
            label = "␣" if ch == "_" else ("?" if ch == "?" else ch)
            img = f_key.render(label, True, WHITE)
            surf.blit(img, img.get_rect(center=rect.center))

        # Backspace / OK
        rounded_rect(surf, self.back_rect, 10, (90, 30, 30), 240)
        pygame.draw.rect(surf, UI_RED, self.back_rect, 2, border_radius=10)
        f_btn = font_factory(18, True)
        bt = f_btn.render("DEL", True, WHITE)
        surf.blit(bt, bt.get_rect(center=self.back_rect.center))

        rounded_rect(surf, self.ok_rect, 10, (30, 90, 40), 240)
        pygame.draw.rect(surf, (60, 200, 80), self.ok_rect, 2, border_radius=10)
        ok = f_btn.render("OK", True, WHITE)
        surf.blit(ok, ok.get_rect(center=self.ok_rect.center))
