"""caption-gap-ticker — a single slim ENGRAVED LINE living in the genuinely-free
~18px gap between the stat tiles (end y~386) and the power-up caption (y~404).

A quiet "newly commended" ticker, NOT a panel: a small inline medallion + a
gold-rich title + a hairline gold rule, in the same flanking-rule divider
vocabulary the power-up caption already uses. The multi-unlock case is made
VISIBLE with a "1/2" pager tag, not a silent rotation.

Scratch tooling only; nothing here is imported by the game. `game/` is untouched.
"""
import os
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _NIGHT_DEEP)

W = 360
# The genuinely-free band measured off the real backdrop: clean navy runs
# ~y377-401 (tiles end ~376, the caption's digits start ~405). Centre the line
# at 388 so it sits in the MIDDLE of that band — clear air above the tiles and
# below the gold-ruled caption, no occlusion either way.
CY = 388


def _hairline(surf, x0, x1, y, col, alpha):
    """A 1px gold hairline that fades to nothing at each end — a faint engraved
    divider, not a hard bar, so it reads as a rule rather than a second border."""
    line = pygame.Surface((x1 - x0, 1), pygame.SRCALPHA)
    n = x1 - x0
    for i in range(n):
        # symmetric triangular falloff, brightest in the middle
        t = 1.0 - abs((i / n) - 0.5) * 2.0
        line.set_at((i, 0), (*col, int(alpha * t)))
    surf.blit(line, (x0, y))


def render():
    surf = render_backdrop()
    ids = demo_ids(2)
    first = ach.BY_ID[ids[0]]
    extra = len(ids) - 1                 # how many MORE were unlocked

    # ── compose the inline line: [badge]  TITLE   ·   [1/2 pager] ─────────────
    # Title in the gold engraving family — a faint pale top-light + body gold,
    # so the line reads premium without a drop shadow eating the tight slot.
    tf = _font(13, True)
    title = first.title.upper()
    t_body = tf.render(title, True, _GOLD_BRIGHT)
    t_lite = tf.render(title, True, _GOLD_PALE)

    # 18px (the top of the brief's 16-18 range): the medallion needs every
    # pixel to read as a struck gold coin rather than a dark blob. Centred at
    # CY=388 it spans y379-397 — still inside the free y377-401 band.
    badge_d = 18
    pager_txt = f"1/{len(ids)}"
    pf = _font(11, True)
    pager = pf.render(pager_txt, True, _NIGHT_DEEP)

    # A "NEW" eyebrow tab so the line announces itself as a fresh commendation
    # rather than a static label — small caps, deep-gold so it sits under the
    # brighter title without competing.
    ef = _font(10, True)
    eyebrow = ef.render("NEW", True, _NIGHT_DEEP)

    gap = 6
    pad_pager = 5
    pager_w = pager.get_width() + pad_pager * 2
    pager_h = 13
    eyebrow_w = eyebrow.get_width() + 5 * 2
    eyebrow_h = 12

    # Total run of the content block (badge + eyebrow + title + pager when >1).
    show_pager = extra > 0
    content_w = (badge_d + gap + eyebrow_w + gap + t_body.get_width()
                 + (gap + 8 + pager_w if show_pager else 0))
    x = (W - content_w) // 2

    # Flanking hairline rules in the caption's own divider language, running
    # from the content edge out toward the panel margins (x18 / x342). They tie
    # the ticker to the gold-rule caption directly beneath it.
    # Kept deliberately FAINTER than the caption's solid 2px gold rule directly
    # below — a 1px fading hairline reads as a quiet engraved divider that the
    # ticker belongs to, without setting up a second bar that competes with it.
    margin = 22
    _hairline(surf, margin, x - 10, CY, _GOLD_DEEP, 150)
    _hairline(surf, x + content_w + 10, W - margin, CY, _GOLD_DEEP, 150)

    # badge (16px medallion — the family's struck-gold coin, unlocked).
    by = CY - badge_d // 2
    draw_badge(surf, first.icon_key, pygame.Rect(x, by, badge_d, badge_d),
               True, False)
    cx = x + badge_d + gap

    # NEW eyebrow tab — a tiny gold pill with navy text, the "freshly earned"
    # affordance that makes the line feel intentional.
    eb = pygame.Rect(cx, CY - eyebrow_h // 2, eyebrow_w, eyebrow_h)
    pygame.draw.rect(surf, _GOLD_BRIGHT, eb, border_radius=3)
    pygame.draw.rect(surf, _GOLD_PALE, eb, width=1, border_radius=3)
    surf.blit(eyebrow, eyebrow.get_rect(center=eb.center))
    cx += eyebrow_w + gap

    # title — pale top-light 1px up for a struck-metal lift, then the gold body.
    tr = t_body.get_rect(midleft=(cx, CY))
    surf.blit(t_lite, (tr.x, tr.y - 1))
    surf.blit(t_body, tr.topleft)
    cx = tr.right + gap

    # pager — a navy gold-rimmed chip reading "1/2", the visible multi-unlock
    # affordance so the player knows more commendations are stacked behind this.
    if show_pager:
        cx += 9
        # a small gold dot separator before the pager — echoes the " · " the
        # caption family uses to part its tokens.
        pygame.draw.circle(surf, _GOLD_BRIGHT, (cx - 7, CY), 2)
        pr = pygame.Rect(cx, CY - pager_h // 2, pager_w, pager_h)
        body = pygame.Surface((pager_w, pager_h), pygame.SRCALPHA)
        pygame.draw.rect(body, (*_GOLD_BRIGHT, 255), (0, 0, pager_w, pager_h),
                         border_radius=4)
        surf.blit(body, pr.topleft)
        pygame.draw.rect(surf, _GOLD_PALE, pr, width=1, border_radius=4)
        surf.blit(pager, pager.get_rect(center=pr.center))

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "achievements", "unlock_notice", "caption-gap-ticker")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "round_1.png")
    pygame.image.save(surf, path)
    print(path)


if __name__ == "__main__":
    render()
