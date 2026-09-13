"""Mockup: the `airmail-filmstrip` achievement-list notice — the run's earned
badges as franked AIRMAIL STAMPS, with the courier FILMSTRIP kept as the brand
header above a real LIST of every delivery.

The design intent the still must sell:
  * The LIST is the screen. ALL THREE unlocked achievements appear as equal,
    complete rows — each a franked stamp badge + FULL name + short description.
    Nothing is truncated; nothing hides behind an "also earned" footer.
  * The airmail/filmstrip identity is a COMPACT HEADER: a short franked
    celluloid ribbon carrying three mini-stamps + "PAR AVION", so the reel read
    lands instantly without stealing the room the three rows need.
  * A clean deep-night field (a quiet starfield up top) — no run-summary
    bleed-through — so the gold frank + names + badges pop.

Scratch tooling only — nothing here is imported by the game; `game/` untouched.
"""
import os
import math
import pygame

from tools.unlock_notice_common import demo_varied_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, make_gradient_surface, lerp_color
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H


# Classic airmail border palette — alternating red / navy parallelogram dashes,
# the franking that says "by air" at a glance. Kept slightly muted so the gold
# stays the brightest accent on the reel.
_AIR_RED  = (196,  48,  52)
_AIR_NAVY = ( 40,  58, 120)

# Filmstrip celluloid — a near-black warm-charcoal so the gold frames + perfs
# pop, with a faint vertical sheen so the ribbon reads as glossy film stock.
_FILM_TOP = ( 22,  16,  40)
_FILM_BOT = ( 10,   6,  24)
_FILM_EDGE = ( 4,   2,  12)
_SPROCKET = (  5,   3,  14)      # punched-through perforation holes
_SPROCKET_LIP = ( 60,  52,  90)  # the lit lip of each punched hole

# A frame caption strip — a paler kraft-paper tone so the stamp NAME reads as
# printed on the franked label beneath each window.
_KRAFT_TOP = (236, 222, 188)
_KRAFT_BOT = (208, 190, 150)
_KRAFT_INK = ( 48,  34,  20)


def _airmail_border(surf, rect, dash=9, gap=4, thick=5):
    """Lay the alternating red/navy slanted-dash airmail frank around a rect's
    perimeter — the parallelogram border that marks a piece as airmail. Dashes
    march clockwise, flipping colour each step, so all four sides share one
    continuous frank rather than four disconnected runs."""
    x, y, w, h = rect
    i = 0

    def slant(px, py, horizontal):
        nonlocal i
        col = _AIR_RED if i % 2 == 0 else _AIR_NAVY
        i += 1
        if horizontal:
            pts = [(px, py), (px + dash, py),
                   (px + dash - thick, py + thick), (px - thick, py + thick)]
        else:
            pts = [(px, py), (px, py + dash),
                   (px - thick, py + dash - thick), (px - thick, py - thick)]
        pygame.draw.polygon(surf, col, [(int(a), int(b)) for a, b in pts])

    step = dash + gap
    cx = x
    while cx < x + w - dash:
        slant(cx, y, True)
        cx += step
    cy = y
    while cy < y + h - dash:
        slant(x + w, cy, False)
        cy += step
    cx = x + w
    while cx > x + dash:
        slant(cx, y + h, True)
        cx -= step
    cy = y + h
    while cy > y + dash:
        slant(x, cy, False)
        cy -= step


def _scallop_mask(w, h, tooth=5):
    """A stamp's perforated edge: a white mask the size of a frame window with
    semicircular bites taken out of all four sides, so a badge blitted through it
    reads as a real postage stamp, not a plain square."""
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    r = tooth
    step = r * 2
    # bite circles centred ON each edge so half the circle clips the corner away
    for cx in range(0, w + step, step):
        pygame.draw.circle(mask, (0, 0, 0, 0), (cx, 0), r)
        pygame.draw.circle(mask, (0, 0, 0, 0), (cx, h), r)
    for cy in range(0, h + step, step):
        pygame.draw.circle(mask, (0, 0, 0, 0), (0, cy), r)
        pygame.draw.circle(mask, (0, 0, 0, 0), (w, cy), r)
    return mask


def _stamp_frame(badge_key, win, focus):
    """Build ONE franked-stamp window on its own SRCALPHA surface: a kraft-paper
    stamp body with a scalloped perforated edge, the airmail frank around it, and
    the real procedural badge struck in the centre. ``focus`` lifts the kraft to
    a brighter, warmer tone + saturates the frank so the hero frame reads lit and
    the side frames read quieter."""
    s = pygame.Surface((win, win), pygame.SRCALPHA)
    # kraft-paper stamp body (vertical gradient), then a perforated-edge clip.
    top = _KRAFT_TOP if focus else (196, 184, 156)
    bot = _KRAFT_BOT if focus else (168, 156, 128)
    body = make_gradient_surface(win, win, [(0.0, top), (1.0, bot)]).convert_alpha()
    perf = _scallop_mask(win, win, tooth=max(3, win // 18))
    body.blit(perf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(body, (0, 0))

    # airmail frank just inside the perforated edge.
    inset = max(5, win // 12)
    fr = pygame.Rect(inset, inset, win - inset * 2, win - inset * 2)
    _airmail_border(s, fr, dash=max(6, win // 12), gap=max(2, win // 28),
                    thick=max(3, win // 22))

    # the real badge, centred, filling the franked window.
    pad = inset + max(5, win // 11)
    brect = pygame.Rect(pad, pad, win - pad * 2, win - pad * 2)
    draw_badge(s, badge_key, brect, True, False)
    if not focus:
        # the side stamps sit dimmer so the carousel hierarchy reads instantly.
        s.set_alpha(168)
    return s


def _mini_stamp(badge_key, win):
    """A tiny franked stamp for the header ribbon: the procedural badge struck on
    a scalloped kraft window with a thin airmail frank. Small enough to ride the
    compact celluloid header without competing with the three list rows below."""
    s = pygame.Surface((win, win), pygame.SRCALPHA)
    body = make_gradient_surface(win, win,
                                 [(0.0, _KRAFT_TOP), (1.0, _KRAFT_BOT)]).convert_alpha()
    perf = _scallop_mask(win, win, tooth=max(2, win // 16))
    body.blit(perf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(body, (0, 0))
    inset = max(3, win // 10)
    fr = pygame.Rect(inset, inset, win - inset * 2, win - inset * 2)
    _airmail_border(s, fr, dash=max(4, win // 11), gap=max(2, win // 24),
                    thick=max(2, win // 20))
    pad = inset + max(3, win // 9)
    draw_badge(s, badge_key, pygame.Rect(pad, pad, win - pad * 2, win - pad * 2),
               True, False)
    return s


def _list_row(badge_key, name, desc, w, h):
    """ONE complete delivery row of the list: a franked stamp badge on the left,
    then the FULL achievement name (gold) over its short description, on a quiet
    kraft-edged night card. Every row carries equal, complete weight — no
    truncation, no hero/side hierarchy."""
    row = pygame.Surface((w, h), pygame.SRCALPHA)

    # the night card: a deep panel with a thin gold keyline so each row reads as
    # its own franked envelope without lighting up brighter than the badges.
    pygame.draw.rect(row, (*_PANEL_DARK, 235), (0, 0, w, h), border_radius=12)
    pygame.draw.rect(row, (*_GOLD_DEEP, 150), (0, 0, w, h), width=1,
                     border_radius=12)
    pygame.draw.line(row, (*_GOLD_PALE, 60), (12, 2), (w - 12, 2), 1)

    # the franked stamp badge, vertically centred at the card's left.
    stamp = h - 18
    frame = _stamp_frame(badge_key, stamp, focus=True)
    row.blit(frame, frame.get_rect(midleft=(12, h // 2)))

    # name + description, left-aligned in the remaining width.
    tx = 12 + stamp + 14
    nf = _font(16, True)
    nimg = nf.render(name, True, _GOLD_BRIGHT)
    nsh = nf.render(name, True, _NIGHT_DEEP)
    nsh.set_alpha(160)
    ny = h // 2 - nimg.get_height()
    row.blit(nsh, (tx + 1, ny + 2))
    row.blit(nimg, (tx, ny))

    df = _font(12, True)
    dimg = df.render(desc, True, (206, 196, 226))
    row.blit(dimg, (tx, h // 2 + 3))

    # a small gold "earned" check at the far right so the row reads as completed.
    chk_cx, chk_cy = w - 22, h // 2
    pygame.draw.circle(row, (*_GOLD_BRIGHT, 70), (chk_cx, chk_cy), 11)
    pygame.draw.lines(row, _GOLD_BRIGHT, False,
                      [(chk_cx - 5, chk_cy), (chk_cx - 1, chk_cy + 4),
                       (chk_cx + 6, chk_cy - 5)], 3)
    return row


def _chevron_motif(surf, cx, y, n=11, w=9, gap=4, thick=4):
    """A short run of the airmail red/navy slanted dashes, centred under the
    headline — the frank motif echoed up top so the airmail read lands before
    the eye reaches the ribbon."""
    total = n * (w + gap) - gap
    x = cx - total // 2
    for i in range(n):
        col = _AIR_RED if i % 2 == 0 else _AIR_NAVY
        pts = [(x, y), (x + w, y), (x + w - thick, y + thick), (x - thick, y + thick)]
        pygame.draw.polygon(surf, col, [(int(a), int(b)) for a, b in pts])
        x += w + gap


def _ticks(surf, cx, cy, label):
    """Tiny PAR AVION tick text at a ribbon end, rotated vertically so it reads
    as a film-stock edge print without stealing width from the frames."""
    f = _font(9, True)
    img = f.render(label, True, (150, 160, 200))
    img = pygame.transform.rotate(img, 90)
    img.set_alpha(190)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def _headline(surf, txt, center):
    """Gold headline with the menu's red pixel-outline + navy drop, the strongest
    on-brand title treatment, so ACHIEVEMENT EARNED! owns the top of frame. Size
    is chosen so the outlined word fits the canvas width with a clear margin —
    a clipped headline reads as a bug, not as a flourish."""
    size = 28
    f = _font(size, True)
    while f.size(txt)[0] > W - 30 and size > 16:
        size -= 1
        f = _font(size, True)
    fill = f.render(txt, True, _GOLD_BRIGHT)
    out = f.render(txt, True, _AIR_RED)
    r = fill.get_rect(center=center)
    px = 3
    for ox, oy in [(-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)]:
        surf.blit(out, (r.x + ox, r.y + oy))
    sh = f.render(txt, True, _NIGHT_DEEP)
    sh.set_alpha(180)
    surf.blit(sh, (r.x + 2, r.y + 5))
    surf.blit(fill, r)
    sheen = f.render(txt, True, _GOLD_PALE)
    sheen.set_alpha(110)
    surf.blit(sheen, (r.x, r.y - 1))
    return r


def _header_ribbon(surf, top, name_count):
    """The COMPACT airmail/filmstrip header: a short franked celluloid band with
    sprocket perfs + PAR AVION edge prints + three mini-stamps. It carries the
    brand identity in a thin strip so the three full list rows own the screen."""
    rib_x, rib_w, rib_h = 14, W - 28, 56
    ribbon = pygame.Surface((rib_w, rib_h), pygame.SRCALPHA)
    band = make_gradient_surface(rib_w, rib_h,
                                 [(0.0, _FILM_TOP), (1.0, _FILM_BOT)]).convert_alpha()
    ribbon.blit(band, (0, 0))
    pygame.draw.rect(ribbon, _FILM_EDGE, (0, 0, rib_w, rib_h), width=2)
    pygame.draw.line(ribbon, (70, 60, 104), (0, 1), (rib_w, 1), 1)

    sp_w, sp_h, sp_gap = 11, 7, 20
    for row_y in (5, rib_h - 5 - sp_h):
        sx = 12
        while sx < rib_w - sp_w - 6:
            pygame.draw.rect(ribbon, _SPROCKET_LIP,
                             (sx - 1, row_y - 1, sp_w + 2, sp_h + 2), border_radius=2)
            pygame.draw.rect(ribbon, _SPROCKET, (sx, row_y, sp_w, sp_h),
                             border_radius=2)
            sx += sp_w + sp_gap
    surf.blit(ribbon, (rib_x, top))
    _ticks(surf, rib_x + 8, top + rib_h // 2, "PAR AVION")
    _ticks(surf, rib_x + rib_w - 8, top + rib_h // 2, "PAR AVION")
    return pygame.Rect(rib_x, top, rib_w, rib_h)


def build():
    ids = demo_varied_ids(3)
    rows = [(ach.BY_ID[i].icon_key, ach.BY_ID[i].title, ach.BY_ID[i].desc)
            for i in ids]   # First Delivery | Pocket Change | Power Up!

    surf = pygame.Surface((W, H))
    cx = W // 2

    # ── 1. CLEAN deep-night field — no run-summary bleed-through — with a quiet
    # starfield up top so the frank + gold names + badges pop. ──
    night = make_gradient_surface(W, H,
                                  [(0.0, _NIGHT_DEEP), (0.55, (14, 12, 34)),
                                   (1.0, (8, 6, 22))])
    surf.blit(night, (0, 0))
    import random
    rng = random.Random(91)
    for _ in range(70):
        sx = rng.randint(0, W - 1)
        sy = rng.randint(0, int(H * 0.34))
        a = rng.randint(40, 150)
        sr = rng.choice((1, 1, 2))
        star = pygame.Surface((sr * 2 + 1, sr * 2 + 1), pygame.SRCALPHA)
        pygame.draw.circle(star, (255, 255, 255, a), (sr, sr), sr)
        surf.blit(star, (sx, sy))

    # ── 2. HEADLINE + chevron frank motif + subhead. ──
    _headline(surf, "ACHIEVEMENT EARNED!", (cx, 52))
    _chevron_motif(surf, cx, 80)
    sub = _font(12, True).render("3 DELIVERIES COMMENDED THIS RUN", True, _GOLD_PALE)
    sub.set_alpha(205)
    surf.blit(sub, sub.get_rect(center=(cx, 104)))

    # ── 3. COMPACT FILMSTRIP HEADER carrying three franked mini-stamps. ──
    rib = _header_ribbon(surf, 122, len(rows))
    mini = rib.height - 16
    mxs = (int(W * 0.30), cx, int(W * 0.70))
    for (key, _n, _d), mx in zip(rows, mxs):
        ms = _mini_stamp(key, mini)
        surf.blit(ms, ms.get_rect(center=(mx, rib.centery)))

    # ── 4. THE LIST: all three deliveries as equal, complete rows — franked
    # badge + FULL name + short description, nothing truncated. ──
    row_w, row_h = W - 28, 96
    gap = 12
    list_top = rib.bottom + 22
    for i, (key, name, desc) in enumerate(rows):
        r = _list_row(key, name, desc, row_w, row_h)
        ry = list_top + i * (row_h + gap)
        surf.blit(r, r.get_rect(midtop=(cx, ry)))

    # ── 5. TAP TO CONTINUE pill, pinned low, handing off to the run summary. ──
    tap = _font(15, True)
    tt = tap.render("TAP TO CONTINUE", True, _GOLD_BRIGHT)
    pw, ph = tt.get_width() + 36, 32
    py = int(H * 0.935)
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*_PANEL_LIGHTER, 215), (0, 0, pw, ph), border_radius=16)
    pygame.draw.rect(pill, (*_GOLD_BRIGHT, 160), (0, 0, pw, ph), width=2,
                     border_radius=16)
    pygame.draw.line(pill, (*_GOLD_PALE, 120), (16, 3), (pw - 16, 3), 1)
    surf.blit(pill, pill.get_rect(center=(cx, py)))
    surf.blit(tt, tt.get_rect(center=(cx, py)))

    return surf


def main():
    # a video mode is required before convert_alpha(); the dummy driver gives us
    # one headlessly now that this concept no longer pulls in the run backdrop.
    pygame.display.set_mode((W, H))
    surf = build()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice", "award_list",
                       "airmail-filmstrip")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "round_2.png")
    pygame.image.save(surf, path)
    print(path)


if __name__ == "__main__":
    main()
