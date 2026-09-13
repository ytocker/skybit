"""
Settings-screen concept explorations — a design-only artifact (NOT wired into
the game). Five distinct layouts for a full-screen Settings scene that today
holds two launchers (How to Play, Power-Ups) and must scale to future items.

Every frame reuses the achievements-screen FRAME (deep night gradient + twinkle
stars + mountain silhouette, a gilded SETTINGS header, and a grounded MENU
footer) so Settings reads as the same UI family. The five bodies diverge on the
core question — what is the *shape* of a settings screen — rather than
re-dressing one base.

Run headless to regenerate the review sheet:
    SDL_VIDEODRIVER=dummy python docs/settings_concepts/render.py
"""
from __future__ import annotations

import math
import os
import random

import pygame

from game.config import W, H
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _pill_btn, _outline_pill_btn, _volume_panel,
    _draw_gear, _draw_overlay_stars, _draw_mountain_silhouette,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _GOLD_MUTED,
    _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP,
)

_WHITE = (245, 246, 255)
_DIM   = (150, 150, 172)
_DIM_SOON = (176, 176, 196)      # a notch brighter than _DIM so 'coming soon'
                                 # rows still read clearly at 1× against the dim plate
_NAVY_INK = (10, 6, 30)          # near-black ink for glyphs on gold discs

_HEADER_H = 56
_FOOTER_H = 54


# Seeded twinkle field so every concept lives in the same night world as the
# menu + achievements wall (same seed-42 discipline).
_STARS = []
def _star_field():
    if not _STARS:
        rng = random.Random(42)
        for _ in range(46):
            _STARS.append((rng.randint(6, W - 6), rng.randint(8, H - 150),
                           rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28)))
    return _STARS


# ── shared frame ─────────────────────────────────────────────────────────────

def _draw_bg(surf, t):
    for yy in range(H):
        f = yy / (H - 1)
        pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, (14, 8, 36), f), (0, yy), (W, yy))
    _draw_overlay_stars(surf, _star_field(), t)
    _draw_mountain_silhouette(surf, alpha=130)


def _draw_header(surf):
    """Gilded SETTINGS band — a night plate carrying a struck cog, the outlined
    title, and a gold underline rule (the ACHIEVEMENTS header, re-titled)."""
    hdr = pygame.Surface((W, _HEADER_H), pygame.SRCALPHA)
    hdr.fill((*_NIGHT_DEEP, 235))
    surf.blit(hdr, (0, 0))
    # A struck cog anchors the title to the SETTINGS chip it opens from.
    _draw_gear(surf, 26, 22, 11)
    _outlined_text(surf, "SETTINGS", (W // 2, 16), size=22, px=2, shadow_offset=(2, 3))
    uw = 152
    ux = W // 2 - uw // 2
    pygame.draw.line(surf, _GOLD_BRIGHT, (ux, 30), (ux + uw, 30), 2)
    pygame.draw.line(surf, (*_GOLD_BRIGHT, 90), (0, _HEADER_H - 1), (W, _HEADER_H - 1), 1)


def _draw_footer(surf):
    """Grounded band + the real MENU pill — the only way back, always present."""
    fy = H - _FOOTER_H
    ftr = pygame.Surface((W, _FOOTER_H), pygame.SRCALPHA)
    ftr.fill((*_NIGHT_DEEP, 236))
    surf.blit(ftr, (0, fy))
    pygame.draw.line(surf, (*_GOLD_BRIGHT, 120), (0, fy), (W, fy), 1)
    _outline_pill_btn(surf, (W // 2, fy + _FOOTER_H // 2), "MENU", size=15, min_width=150)


def _base(t):
    """Fresh 360×640 surface with the shared bg/header/footer already drawn."""
    surf = pygame.Surface((W, H))
    _draw_bg(surf, t)
    _draw_header(surf)
    _draw_footer(surf)
    return surf


# ── small building blocks ────────────────────────────────────────────────────

def _section_header(surf, text, y, accent=_GOLD_BRIGHT, alpha=255):
    """Gold diamond pip + tracked caps + a fading engraved rule — the
    achievements category band, so groups read as one system."""
    py = y + 9
    d = 4
    px0 = 14
    pip = [(px0, py), (px0 + d, py - d), (px0 + 2 * d, py), (px0 + d, py + d)]
    pygame.draw.polygon(surf, accent, pip)
    pygame.draw.polygon(surf, _GOLD_DEEP, pip, 1)
    lab = _font(14, True).render(text, True, accent)
    lab.set_alpha(alpha)
    lx = px0 + 3 * d
    surf.blit(lab, (lx, y + 1))
    rail_l = lx + lab.get_width() + 8
    rail_r = W - 12
    if rail_r > rail_l:
        rail = pygame.Surface((rail_r - rail_l, 2), pygame.SRCALPHA)
        for xx in range(rail.get_width()):
            fade = 1.0 - xx / max(1, rail.get_width())
            rail.fill((*accent, int(150 * fade * (alpha / 255))), (xx, 0, 1, 2))
        surf.blit(rail, (rail_l, py))


def _chevron(surf, cx, cy, s, color, w=3):
    pygame.draw.line(surf, color, (cx - s * 0.35, cy - s), (cx + s * 0.4, cy), w)
    pygame.draw.line(surf, color, (cx + s * 0.4, cy), (cx - s * 0.35, cy + s), w)


def _icon_disc(surf, cx, cy, r):
    """Gold coin-like backer that glyphs sit on — a struck disc with a sheen."""
    disc = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    cc = r + 2
    for yy in range(r * 2):
        f = yy / max(1, r * 2 - 1)
        col = lerp_color(_GOLD_PALE, _GOLD_DEEP, f)
        half = int(math.sqrt(max(0, r * r - (yy - r) ** 2)))
        pygame.draw.line(disc, col, (cc - half, yy + 2), (cc + half, yy + 2))
    pygame.draw.circle(disc, _GOLD_DEEP, (cc, cc), r, 2)
    pygame.draw.circle(disc, (*_GOLD_PALE, 150), (int(cc - r * 0.3), int(cc - r * 0.35)),
                       int(r * 0.28))
    surf.blit(disc, (cx - cc, cy - cc))


# Glyphs — drawn in near-black ink so they read on the gold disc, in the gold
# family when free-standing (``ink=None``). ``s`` is the glyph half-extent.

def _g_question(surf, cx, cy, s, ink=_NAVY_INK):
    img = _font(int(s * 2.2), True).render("?", True, ink or _GOLD_BRIGHT)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def _g_book(surf, cx, cy, s, ink=_NAVY_INK):
    col = ink or _GOLD_BRIGHT
    left = [(cx, cy - s * 0.8), (cx - s, cy - s * 0.5),
            (cx - s, cy + s * 0.8), (cx, cy + s * 0.5)]
    right = [(cx, cy - s * 0.8), (cx + s, cy - s * 0.5),
             (cx + s, cy + s * 0.8), (cx, cy + s * 0.5)]
    pygame.draw.polygon(surf, col, left, 2)
    pygame.draw.polygon(surf, col, right, 2)
    pygame.draw.line(surf, col, (cx, cy - s * 0.8), (cx, cy + s * 0.5), 2)
    for k in range(1, 3):
        yy = cy - s * 0.35 + k * s * 0.4
        pygame.draw.line(surf, col, (cx - s * 0.75, yy), (cx - s * 0.2, yy + 0.15 * s), 1)
        pygame.draw.line(surf, col, (cx + s * 0.2, yy + 0.15 * s), (cx + s * 0.75, yy), 1)


def _g_bolt(surf, cx, cy, s, ink=_NAVY_INK):
    pts = [
        (cx + s * 0.18, cy - s),
        (cx - s * 0.55, cy + s * 0.12),
        (cx - s * 0.05, cy + s * 0.12),
        (cx - s * 0.22, cy + s),
        (cx + s * 0.55, cy - s * 0.18),
        (cx + s * 0.05, cy - s * 0.18),
    ]
    pygame.draw.polygon(surf, ink or _GOLD_BRIGHT, pts)
    pygame.draw.polygon(surf, _NAVY_INK if ink else _GOLD_DEEP, pts, 1)


def _g_spark(surf, cx, cy, s, ink=_GOLD_BRIGHT):
    """A four-point sparkle star — the power-up float-text motif."""
    pts = []
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        rr = s if i % 2 == 0 else s * 0.32
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    pygame.draw.polygon(surf, ink, pts)
    pygame.draw.polygon(surf, _GOLD_DEEP, pts, 1)


def _g_gift(surf, cx, cy, s, ink=_NAVY_INK):
    col = ink or _GOLD_BRIGHT
    body = pygame.Rect(int(cx - s * 0.8), int(cy - s * 0.35), int(s * 1.6), int(s * 1.15))
    pygame.draw.rect(surf, col, body, 2, border_radius=2)
    lid = pygame.Rect(int(cx - s * 0.95), int(cy - s * 0.7), int(s * 1.9), int(s * 0.4))
    pygame.draw.rect(surf, col, lid, 2, border_radius=2)
    pygame.draw.line(surf, col, (cx, cy - s * 0.7), (cx, cy + s * 0.8), 2)
    pygame.draw.polygon(surf, col, [(cx, cy - s * 0.7),
                                    (cx - s * 0.5, cy - s), (cx - s * 0.15, cy - s * 0.7)], 2)
    pygame.draw.polygon(surf, col, [(cx, cy - s * 0.7),
                                    (cx + s * 0.5, cy - s), (cx + s * 0.15, cy - s * 0.7)], 2)


def _g_lock(surf, cx, cy, s, ink=_DIM):
    """Padlock — the unmistakable 'coming soon' seal."""
    body = pygame.Rect(int(cx - s * 0.75), int(cy - s * 0.1), int(s * 1.5), int(s * 1.05))
    pygame.draw.rect(surf, ink, body, border_radius=3)
    pygame.draw.arc(surf, ink, (int(cx - s * 0.5), int(cy - s * 0.95),
                                int(s), int(s * 1.1)), 0.15, math.pi - 0.15, 3)
    pygame.draw.circle(surf, _NIGHT_DEEP, (int(cx), int(cy + s * 0.35)), max(2, int(s * 0.2)))


_GLYPHS = {
    "question": _g_question, "book": _g_book, "bolt": _g_bolt,
    "spark": _g_spark, "gift": _g_gift, "lock": _g_lock,
}


def _row_panel(surf, y, h=56, dim=False):
    rect = pygame.Rect(6, y, W - 12, h)
    if dim:
        # Empty-slot treatment — a faint cool plate, no gold border (the
        # achievements 'masked' row), so 'not yet available' never reads broken.
        plate = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(plate, (14, 10, 34, 210), (0, 0, rect.w, rect.h), border_radius=13)
        pygame.draw.rect(plate, (70, 66, 96, 110), (0, 0, rect.w, rect.h), 1, border_radius=13)
        surf.blit(plate, rect.topleft)
    else:
        _volume_panel(surf, rect, radius=13)
    return rect


# ── Concept 1 — Row list ─────────────────────────────────────────────────────

def concept_row_list(t):
    surf = _base(t)
    rows = [("book", "How to Play", "Controls & the basics"),
            ("bolt", "Power-Ups", "What every pickup does")]
    # Center the whole group in the open body so two rows don't cling to the top
    # and strand 60% of the canvas. The dim caption below fills the residual air
    # and telegraphs that the list keeps growing.
    row_h, gap = 68, 12
    hdr_gap, cap_gap = 34, 30
    group_h = hdr_gap + len(rows) * row_h + (len(rows) - 1) * gap + cap_gap
    body_top, body_bot = _HEADER_H, H - _FOOTER_H
    top = body_top + (body_bot - body_top - group_h) // 2
    _section_header(surf, "HELP", top)
    y = top + hdr_gap
    for kind, label, sub in rows:
        rect = _row_panel(surf, y, row_h)
        cy = rect.centery
        _icon_disc(surf, 42, cy, 21)
        _GLYPHS[kind](surf, 42, cy, 13)
        surf.blit(_font(18, True).render(label, True, _GOLD_PALE), (78, y + 15))
        surf.blit(_font(12, True).render(sub, True, _DIM), (78, y + 40))
        _chevron(surf, W - 28, cy, 8, _GOLD_BRIGHT)
        y += row_h + gap
    cap = _font(12, True).render("More settings coming soon", True, _DIM)
    cap.set_alpha(150)
    surf.blit(cap, (W // 2 - cap.get_width() // 2, y + 12))
    return surf


# ── Concept 2 — Two big cards ────────────────────────────────────────────────

def concept_big_cards(t):
    surf = _base(t)
    cards = [("book", "HOW TO PLAY"), ("bolt", "POWER-UPS")]
    y = 78
    ch = 202          # trimmed so a sliver of a third card peeks at the foot,
    for kind, label in cards:   # hinting the list grows past what fits.
        rect = pygame.Rect(18, y, W - 36, ch)
        _volume_panel(surf, rect, radius=18)
        cx = rect.centerx
        # Icon nudged down so icon / title / button sit optically balanced.
        _icon_disc(surf, cx, y + 78, 38)
        _GLYPHS[kind](surf, cx, y + 78, 24)
        _outlined_text(surf, label, (cx, y + 142), size=21, px=2, shadow_offset=(2, 3))
        # A real outlined pill (not a floating caption) so OPEN reads as a button.
        _outline_pill_btn(surf, (cx, y + ch - 30), "OPEN  ›", size=13, min_width=160)
        y += ch + 16
    # Peeking third card — its foot tucks behind the footer so only a top sliver
    # shows, making clear the stack continues past what fits on screen.
    peek = pygame.Rect(18, y, W - 36, ch)
    _volume_panel(surf, peek, radius=18)
    _draw_footer(surf)
    return surf


# ── Concept 3 — Grouped + coming-soon ────────────────────────────────────────

def concept_grouped(t):
    surf = _base(t)
    _section_header(surf, "HELP", 64)
    y = 88
    for kind, label, sub in [("book", "How to Play", "Controls & the basics"),
                             ("bolt", "Power-Ups", "What every pickup does")]:
        rect = _row_panel(surf, y, 54)
        cy = rect.centery
        _icon_disc(surf, 38, cy, 17)
        _GLYPHS[kind](surf, 38, cy, 11)
        surf.blit(_font(16, True).render(label, True, _GOLD_PALE), (68, y + 10))
        surf.blit(_font(11, True).render(sub, True, _DIM), (68, y + 30))
        _chevron(surf, W - 26, cy, 7, _GOLD_BRIGHT)
        y += 54 + 9

    y += 12
    # Short section label; the row labels below carry the specifics, so the
    # rail fade keeps its breathing room instead of being crowded by text.
    _section_header(surf, "COMING SOON", y, accent=_GOLD_MUTED, alpha=150)
    y += 26
    for label in ("Sound & Music", "Reduce Motion"):
        rect = _row_panel(surf, y, 54, dim=True)
        cy = rect.centery
        _g_lock(surf, 38, cy, 12, ink=_DIM_SOON)
        lab = _font(16, True).render(label, True, _DIM_SOON)
        surf.blit(lab, (68, cy - lab.get_height() // 2))
        tag = _font(11, True).render("SOON", True, _GOLD_MUTED)
        tag.set_alpha(200)
        surf.blit(tag, (W - 22 - tag.get_width(), cy - tag.get_height() // 2))
        y += 54 + 9
    return surf


# ── Concept 4 — Diegetic control panel ───────────────────────────────────────

def _rivet(surf, cx, cy, r=4):
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), r)
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), r, 1)
    pygame.draw.circle(surf, (*_GOLD_PALE, 180), (cx - 1, cy - 1), max(1, r - 2))


def _open_placard(surf, cx, cy):
    """A small navy 'OPEN ›' tab on a switch's right — a launch affordance, so
    it can never be mistaken for an on/off toggle on a navigation panel."""
    img = _font(11, True).render("OPEN", True, _GOLD_BRIGHT)
    pw, ph = img.get_width() + 30, 26
    tab = pygame.Rect(int(cx - pw // 2), int(cy - ph // 2), pw, ph)
    pygame.draw.rect(surf, (6, 3, 18), tab, border_radius=ph // 2)
    pygame.draw.rect(surf, _GOLD_BRIGHT, tab, 2, border_radius=ph // 2)
    surf.blit(img, (tab.left + 10, tab.centery - img.get_height() // 2))
    _chevron(surf, tab.right - 11, tab.centery, 5, _GOLD_BRIGHT, w=2)


def concept_cockpit(t):
    surf = _base(t)
    # Riveted brass fascia — Pip's cockpit. Decoration only; every control is
    # spelled out in a hard-edged label so it stays colourblind/low-vision safe.
    # Darkened so the SETTINGS header stays the brightest gold on screen.
    panel = pygame.Rect(14, 72, W - 28, 502)
    body = pygame.Surface(panel.size, pygame.SRCALPHA)
    for yy in range(panel.h):
        f = yy / max(1, panel.h - 1)
        body.fill(lerp_color((150, 116, 52), (74, 52, 20), f), (0, yy, panel.w, 1))
    mask = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, panel.w, panel.h), border_radius=16)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(body, _GOLD_DEEP, (0, 0, panel.w, panel.h), 3, border_radius=16)
    pygame.draw.line(body, (*_GOLD_PALE, 120), (14, 4), (panel.w - 14, 4), 2)
    surf.blit(body, panel.topleft)
    for rx in (panel.left + 12, panel.right - 12):
        for ry in (panel.top + 12, panel.bottom - 12):
            _rivet(surf, rx, ry)

    plate_head = _font(12, True).render("FLIGHT MANUAL", True, (40, 26, 6))
    surf.blit(plate_head, (panel.centerx - plate_head.get_width() // 2, panel.top + 18))

    # Placard launchers. The LABEL is the source of truth; the right-side OPEN
    # tab says 'go here', never 'toggle'.
    switches = [("book", "HOW TO PLAY"), ("bolt", "POWER-UPS")]
    py = panel.top + 48
    for kind, label in switches:
        plate = pygame.Rect(panel.left + 18, py, panel.w - 36, 96)
        pl = pygame.Surface(plate.size, pygame.SRCALPHA)
        pygame.draw.rect(pl, (*_PANEL_DARK, 245), (0, 0, plate.w, plate.h), border_radius=12)
        pygame.draw.rect(pl, _GOLD_BRIGHT, (0, 0, plate.w, plate.h), 2, border_radius=12)
        surf.blit(pl, plate.topleft)
        _icon_disc(surf, plate.left + 34, plate.centery, 20)
        _GLYPHS[kind](surf, plate.left + 34, plate.centery, 13)
        surf.blit(_font(18, True).render(label, True, _GOLD_PALE),
                  (plate.left + 66, plate.centery - 26))
        surf.blit(_font(11, True).render("PULL TO OPEN", True, _GOLD_PALE),
                  (plate.left + 66, plate.centery + 4))
        _open_placard(surf, plate.right - 46, plate.centery)
        py += 108

    # A dim riveted future slot fills the lower fascia and telegraphs the panel
    # will hold more instruments than the two shipping launchers.
    slot = pygame.Rect(panel.left + 18, py, panel.w - 36, 96)
    ps = pygame.Surface(slot.size, pygame.SRCALPHA)
    pygame.draw.rect(ps, (14, 10, 34, 210), (0, 0, slot.w, slot.h), border_radius=12)
    pygame.draw.rect(ps, (110, 90, 46, 150), (0, 0, slot.w, slot.h), 2, border_radius=12)
    surf.blit(ps, slot.topleft)
    _g_lock(surf, slot.left + 34, slot.centery, 13, ink=_DIM_SOON)
    surf.blit(_font(16, True).render("More instruments", True, _DIM_SOON),
              (slot.left + 62, slot.centery - 22))
    tag = _font(11, True).render("COMING SOON", True, _GOLD_MUTED)
    surf.blit(tag, (slot.left + 62, slot.centery + 4))
    return surf


# ── Concept 5 — Menu-consistent pill stack ───────────────────────────────────

def _topic_pill(surf, cy, kind, label, alpha=230):
    """Secondary navy+gold outline pill with a left-inset topic icon, so it
    reads as a subject to browse — one tier quieter than any scarlet CTA, and
    clearly distinct from the action-shaped MENU pill."""
    rect = _outline_pill_btn(surf, (W // 2, cy), "   " + label, size=17,
                             min_width=250, alpha=alpha)
    if alpha >= 200:
        _icon_disc(surf, rect.left + 30, cy, 15)
        _GLYPHS[kind](surf, rect.left + 30, cy, 10)
    return rect


def concept_pill_stack(t):
    surf = _base(t)
    cap = _font(17, True).render("Choose a topic", True, _GOLD_PALE)
    surf.blit(cap, (W // 2 - cap.get_width() // 2, 150))
    # Quiet secondary outline pills — one clear tier below any scarlet CTA — each
    # fronted by its topic icon so Settings reads as a browse list, not a row of
    # primary actions competing with START.
    _topic_pill(surf, 240, "book", "HOW TO PLAY")
    _topic_pill(surf, 322, "bolt", "POWER-UPS")
    # A faint ghost pill hints the topic list keeps growing.
    _topic_pill(surf, 402, "lock", "MORE SOON", alpha=90)
    return surf


# ── showcase board ───────────────────────────────────────────────────────────

_CONCEPTS = [
    ("1 · ROW LIST", "Centered OS-style rows: icon, label, chevron; a dim caption fills the air.",
     concept_row_list),
    ("2 · BIG CARDS", "Bold tap-targets — centered icon, label, an outlined OPEN pill; a third peeks.",
     concept_big_cards),
    ("3 · GROUPED + SOON", "Real HELP rows plus a dimmed, padlocked COMING SOON group.",
     concept_grouped),
    ("4 · COCKPIT", "Pip's darkened brass fascia; labelled placards with OPEN tabs, not toggles.",
     concept_cockpit),
    ("5 · PILL STACK", "Menu-native: quiet navy+gold topic pills with icons, over the MENU pill.",
     concept_pill_stack),
]


def _wrap(text, font, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def build_showcase():
    t = 1.1  # a fixed twinkle phase so the board is deterministic
    frames = [(name, cap, fn(t)) for name, cap, fn in _CONCEPTS]

    margin, gap = 30, 26
    label_h, cap_h = 34, 66
    cell_w = W
    n = len(frames)
    board_w = margin * 2 + n * cell_w + (n - 1) * gap
    title_h = 66
    board_h = margin + title_h + label_h + H + cap_h + margin

    board = pygame.Surface((board_w, board_h))
    for yy in range(board_h):
        f = yy / (board_h - 1)
        pygame.draw.line(board, lerp_color((18, 12, 32), (8, 5, 18), f),
                         (0, yy), (board_w, yy))

    title = _font(30, True).render("SKYBIT  —  SETTINGS SCREEN CONCEPTS", True, _GOLD_BRIGHT)
    board.blit(title, (margin, margin + 8))
    sub = _font(15, True).render("Same night-world frame; five distinct layouts. "
                                 "Rows are launchers only.", True, _DIM)
    board.blit(sub, (margin, margin + 44))

    lab_font = _font(17, True)
    cap_font = _font(13, True)
    top = margin + title_h
    for i, (name, cap, frame) in enumerate(frames):
        x = margin + i * (cell_w + gap)
        nm = lab_font.render(name, True, _GOLD_PALE)
        board.blit(nm, (x, top + 6))
        board.blit(frame, (x, top + label_h))
        pygame.draw.rect(board, _GOLD_DEEP,
                         (x - 1, top + label_h - 1, cell_w + 2, H + 2), 1)
        cy = top + label_h + H + 8
        for ln in _wrap(cap, cap_font, cell_w)[:3]:
            board.blit(cap_font.render(ln, True, _WHITE), (x, cy))
            cy += 18
    return board


if __name__ == "__main__":
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))
    out = os.path.join(os.path.dirname(__file__), "round_2.png")
    board = build_showcase()
    pygame.image.save(board, out)
    print(f"wrote {out}  ({board.get_width()}x{board.get_height()})")
    pygame.quit()
