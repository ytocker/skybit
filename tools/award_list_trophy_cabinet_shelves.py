"""Trophy-cabinet (shelved-niche) concept for the ACHIEVEMENT EARNED! notice.

Scratch tooling only — nothing here is imported by the game; game/ is untouched.
A glass-fronted courier's trophy cabinet: each earned badge seated in its own
lit 3-D niche on a wooden shelf with an engraved brass nameplate. The whole
brief lives or dies on per-niche LIGHTING and badge RIM-LIGHT, so the niche
back-wall pools a warm glow up behind each badge and a bright rim arc is laid
on the badge's upper-left to lift navy enamel off the recess.
"""
import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import math
import pygame

from tools.unlock_notice_common import demo_varied_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, make_gradient_surface, lerp_color
from game.hud import (_font, _outlined_text, _draw_overlay_stars,
                      _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _PANEL_DARK,
                      _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H

if not pygame.get_init():
    pygame.init()

# ── palette ──────────────────────────────────────────────────────────────────
# Deep MAHOGANY wood for the case + shelves. The cabinet must read clearly
# DARKER than both the lit niche pools and the brass — that value gap is what
# lets the gold badges and brass nameplates pop as the bright focal elements
# instead of dissolving into one uniform tan band.
_WOOD_TOP   = ( 64,  32,  18)   # plank face, lit front edge
_WOOD_BOT   = ( 32,  14,   8)   # plank face, shadowed back
_WOOD_LIP   = ( 96,  54,  28)   # front lip of the ledge — a controlled catch-light
_WOOD_LIP_LO = ( 24,  10,   5)
_NICHE_BACK_TOP = ( 30,  20,  56)   # niche back panel, top
_NICHE_BACK_BOT = ( 14,   9,  34)   # niche back panel, base
_BRASS_HI   = (236, 196, 110)
_BRASS_MID  = (190, 150,  70)
_BRASS_LO   = (118,  86,  34)
_BRASS_EDGE = ( 70,  48,  16)


def _vgradient_rect(surf, rect, top, bot):
    x, y, w, h = rect
    g = make_gradient_surface(w, h, [(0.0, top), (1.0, bot)])
    surf.blit(g, (x, y))


def _cabinet_backdrop(surf):
    """Deep night-sky case interior with a twinkle field — the same palette as
    every overlay so the cabinet sits inside Skybit, not on a foreign card."""
    bg = make_gradient_surface(W, H, [
        (0.0, _NIGHT_DEEP), (0.5, _PANEL_DARK), (1.0, _PANEL_LIGHTER)])
    surf.blit(bg, (0, 0))
    stars = [(37, 70, 1, 0.3), (92, 44, 2, 1.1), (150, 96, 1, 2.0),
             (228, 58, 1, 0.7), (300, 88, 2, 1.7), (330, 150, 1, 2.5),
             (24, 150, 1, 3.0), (200, 36, 1, 0.2)]
    _draw_overlay_stars(surf, stars, 0.6)


def _pediment(surf, x, y, w, h):
    """A shallow arched gold cornice crowning the case — the headline rides on
    it. A brass gradient bar with a raised top keyline and a shadowed underside,
    its lower edge dentil-notched so it reads as carved cornice, not a banner.
    The headline sits on a recessed dark mahogany inlay so the gold lettering
    has a deep backing to pop against instead of brass-on-brass."""
    # cast shadow under the cornice onto the case
    sh = pygame.Surface((w + 12, h + 16), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 110), (0, 8, w + 12, h + 6), border_radius=18)
    surf.blit(sh, (x - 6, y))

    body = pygame.Surface((w, h), pygame.SRCALPHA)
    grad = make_gradient_surface(w, h, [
        (0.0, _BRASS_HI), (0.45, _BRASS_MID), (1.0, _BRASS_LO)])
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    # gentle arch: rounded-top rectangle
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_top_left_radius=46, border_top_right_radius=46,
                     border_bottom_left_radius=10, border_bottom_right_radius=10)
    body.blit(grad, (0, 0))
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x, y))

    # raised top keyline (specular) + dark outer keyline
    pygame.draw.rect(surf, _GOLD_PALE, (x, y, w, h), width=2,
                     border_top_left_radius=46, border_top_right_radius=46,
                     border_bottom_left_radius=10, border_bottom_right_radius=10)
    pygame.draw.rect(surf, _BRASS_EDGE, (x - 1, y - 1, w + 2, h + 2), width=2,
                     border_top_left_radius=47, border_top_right_radius=47,
                     border_bottom_left_radius=11, border_bottom_right_radius=11)
    # dentil notches along the underside — carved cornice cue
    ny = y + h - 7
    for nx in range(x + 14, x + w - 12, 16):
        pygame.draw.rect(surf, _BRASS_LO, (nx, ny, 8, 5), border_radius=1)
        pygame.draw.rect(surf, _BRASS_EDGE, (nx, ny, 8, 5), width=1, border_radius=1)

    # recessed dark-mahogany inlay the headline rides on — a deep backing so the
    # gold lettering reads as a bright focal element, not brass lost on brass.
    inlay = pygame.Rect(x + 14, y + 16, w - 28, h - 30)
    _vgradient_rect_round(surf, inlay, (34, 14, 8), (18, 7, 4), 14)
    # inner cast shadow so the inlay reads as a genuine recess, not a flat panel
    ish = pygame.Surface(inlay.size, pygame.SRCALPHA)
    for i in range(10):
        a = int(120 * (1 - i / 10))
        pygame.draw.line(ish, (0, 0, 0, a), (0, i), (inlay.w, i))
    surf.blit(ish, inlay.topleft)
    pygame.draw.rect(surf, _BRASS_EDGE, inlay, width=2, border_radius=14)
    # bright keyline along the inlay's lower lip — the recess catches a glint
    pygame.draw.line(surf, _GOLD_PALE, (inlay.x + 8, inlay.bottom - 1),
                     (inlay.right - 8, inlay.bottom - 1), 1)


def _shelf(surf, x, y, w, item, t):
    """One shelf: a lit recessed niche back-panel with a warm wall-glow pooling
    up behind the rim-lit badge, a wooden ledge with a bright front lip and a
    cast under-shadow, and a bright engraved brass nameplate to the right."""
    icon_key, title, desc = item
    NICHE_H = 96
    LEDGE_H = 14

    # ── recessed niche back panel (sits above the ledge) ──
    niche = pygame.Rect(x, y, w, NICHE_H)
    _vgradient_rect(surf, niche, _NICHE_BACK_TOP, _NICHE_BACK_BOT)
    # side walls darkened so the cavity reads as inset, not flush
    side = pygame.Surface((w, NICHE_H), pygame.SRCALPHA)
    for i in range(18):
        a = int(150 * (1 - i / 18))
        pygame.draw.line(side, (0, 0, 0, a), (i, 0), (i, NICHE_H))
        pygame.draw.line(side, (0, 0, 0, a), (w - 1 - i, 0), (w - 1 - i, NICHE_H))
    surf.blit(side, (x, y))
    # top inner shadow (the niche's overhang)
    topsh = pygame.Surface((w, 16), pygame.SRCALPHA)
    for i in range(16):
        pygame.draw.line(topsh, (0, 0, 0, int(150 * (1 - i / 16))),
                         (0, i), (w, i))
    surf.blit(topsh, (x, y))

    # badge centred in the left third of the niche
    bx = x + 60
    by = y + NICHE_H // 2

    # ── wall-glow pooling UP the back panel behind the badge (the lighting) ──
    # A warm vertical pool: brightest at the badge, fading up the wall, so the
    # niche floor is clearly LIT and the badge never sinks into a dark cavity.
    blit_glow(surf, bx, by + 8, 60, (236, 170, 78), 96)
    blit_glow(surf, bx, by - 14, 42, (120, 96, 200), 52)

    # contact/ambient-occlusion shadow where the badge meets the ledge
    contact = pygame.Surface((110, 26), pygame.SRCALPHA)
    pygame.draw.ellipse(contact, (0, 0, 0, 130), (0, 0, 110, 26))
    surf.blit(contact, (bx - 55, y + NICHE_H - 20))

    # ── the real badge ──
    b_rect = pygame.Rect(0, 0, 74, 74)
    b_rect.center = (bx, by)
    draw_badge(surf, icon_key, b_rect, unlocked=True)

    # rim-light arc on the badge's upper-left so navy enamel lifts off the
    # recess — a thin bright crescent hugging the medallion edge.
    rim = pygame.Surface((84, 84), pygame.SRCALPHA)
    pygame.draw.arc(rim, (255, 244, 210, 210), (2, 2, 80, 80),
                    math.radians(70), math.radians(200), 3)
    pygame.draw.arc(rim, (255, 230, 170, 120), (4, 4, 76, 76),
                    math.radians(75), math.radians(195), 2)
    surf.blit(rim, (bx - 42, by - 42), special_flags=pygame.BLEND_ADD)

    # ── wooden ledge below the niche ──
    ledge = pygame.Rect(x - 4, y + NICHE_H, w + 8, LEDGE_H)
    _vgradient_rect(surf, ledge, _WOOD_TOP, _WOOD_BOT)
    # thin front lip catching the light — kept narrow + muted so the dark
    # mahogany ledge stays well below the brass plates in value.
    pygame.draw.rect(surf, _WOOD_LIP, (ledge.x, ledge.y, ledge.w, 2))
    pygame.draw.line(surf, _WOOD_LIP_LO, (ledge.x, ledge.bottom - 1),
                     (ledge.right, ledge.bottom - 1), 1)
    # cast under-shadow of the ledge onto the niche below
    under = pygame.Surface((w + 8, 12), pygame.SRCALPHA)
    for i in range(12):
        pygame.draw.line(under, (0, 0, 0, int(120 * (1 - i / 12))),
                         (0, i), (w + 8, i))
    surf.blit(under, (ledge.x, ledge.bottom))

    # ── engraved brass nameplate to the right of the badge ──
    plate = pygame.Rect(x + 116, y + 20, w - 132, NICHE_H - 40)
    pgrad = make_gradient_surface(plate.w, plate.h, [
        (0.0, _BRASS_HI), (0.5, _BRASS_MID), (1.0, _BRASS_LO)])
    pg = pygame.Surface(plate.size, pygame.SRCALPHA)
    pg.blit(pgrad, (0, 0))
    pm = pygame.Surface(plate.size, pygame.SRCALPHA)
    pygame.draw.rect(pm, (255, 255, 255, 255), (0, 0, plate.w, plate.h),
                     border_radius=6)
    pg.blit(pm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(pg, plate.topleft)
    # bevel: bright top keyline, dark base + screw rivets
    pygame.draw.line(surf, _GOLD_PALE, (plate.x + 4, plate.y + 1),
                     (plate.right - 4, plate.y + 1), 1)
    pygame.draw.rect(surf, _BRASS_EDGE, plate, width=2, border_radius=6)
    for rx in (plate.x + 7, plate.right - 7):
        for ry in (plate.y + 7, plate.bottom - 7):
            pygame.draw.circle(surf, _BRASS_EDGE, (rx, ry), 2)
            pygame.draw.circle(surf, _GOLD_PALE, (rx - 1, ry - 1), 1)

    # incised NAME — deep-engrave look: dark inset down-right, gold lifted up.
    fn = _font(20, True)
    cxn = plate.centerx
    yname = plate.y + 17
    n_sh = fn.render(title, True, _BRASS_EDGE)
    surf.blit(n_sh, n_sh.get_rect(center=(cxn + 1, yname + 1)))
    n_hi = fn.render(title, True, (60, 38, 12))  # incised shadow first
    surf.blit(n_hi, n_hi.get_rect(center=(cxn, yname)))
    n_lt = fn.render(title, True, _GOLD_PALE)
    surf.blit(n_lt, n_lt.get_rect(center=(cxn - 1, yname - 1)))

    # description in a smaller darker engrave
    fd = _font(12, True)
    ydesc = plate.y + 38
    # wrap description to fit
    words = desc.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if fd.size(trial)[0] <= plate.w - 16:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    for li, line in enumerate(lines):
        d_sh = fd.render(line, True, _BRASS_EDGE)
        surf.blit(d_sh, d_sh.get_rect(center=(cxn + 1, ydesc + li * 14 + 1)))
        d_lt = fd.render(line, True, (44, 28, 10))
        surf.blit(d_lt, d_lt.get_rect(center=(cxn, ydesc + li * 14)))


def _glass_sheen(surf, rect):
    """Two faint diagonal alpha streaks across the case glass — kept OFF the
    badges (drawn over the panel margins only, low alpha) so it reads as glass
    without glaring out the medals the AD warned about."""
    sheen = pygame.Surface(rect.size, pygame.SRCALPHA)
    w, h = rect.size
    # Two NARROW diagonal streaks kept thin + low-alpha so the glass reads
    # without glaring out the badges (the AD's make-or-break note).
    for (sx, sw, a) in ((int(w * 0.20), 12, 22), (int(w * 0.70), 7, 14)):
        pts = [(sx, 0), (sx + sw, 0), (sx + sw - 60, h), (sx - 60, h)]
        pygame.draw.polygon(sheen, (210, 222, 245, a), pts)
    surf.blit(sheen, rect.topleft)


def _tap_plaque(surf, cx, y):
    """Small brass plaque at the cabinet base — TAP TO CONTINUE."""
    txt = "TAP TO CONTINUE"
    f = _font(14, True)
    tw = f.size(txt)[0]
    pw, ph = tw + 36, 30
    plate = pygame.Rect(cx - pw // 2, y, pw, ph)
    pgrad = make_gradient_surface(pw, ph, [
        (0.0, _BRASS_HI), (0.5, _BRASS_MID), (1.0, _BRASS_LO)])
    pg = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pg.blit(pgrad, (0, 0))
    pm = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(pm, (255, 255, 255, 255), (0, 0, pw, ph), border_radius=14)
    pg.blit(pm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(pg, plate.topleft)
    pygame.draw.rect(surf, _BRASS_EDGE, plate, width=2, border_radius=14)
    pygame.draw.line(surf, _GOLD_PALE, (plate.x + 6, plate.y + 1),
                     (plate.right - 6, plate.y + 1), 1)
    s_sh = f.render(txt, True, _BRASS_EDGE)
    surf.blit(s_sh, s_sh.get_rect(center=(cx, y + ph // 2 + 1)))
    s_lt = f.render(txt, True, (52, 32, 10))
    surf.blit(s_lt, s_lt.get_rect(center=(cx, y + ph // 2)))


def render():
    surf = pygame.Surface((W, H))
    _cabinet_backdrop(surf)

    # ── the cabinet case frame ──
    case = pygame.Rect(12, 92, W - 24, H - 150)
    # outer wood frame
    frame = case.inflate(16, 16)
    fg = make_gradient_surface(frame.w, frame.h, [
        (0.0, _WOOD_TOP), (1.0, _WOOD_LIP_LO)])
    fpanel = pygame.Surface(frame.size, pygame.SRCALPHA)
    fpanel.blit(fg, (0, 0))
    fm = pygame.Surface(frame.size, pygame.SRCALPHA)
    pygame.draw.rect(fm, (255, 255, 255, 255), (0, 0, frame.w, frame.h),
                     border_radius=20)
    fpanel.blit(fm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fpanel, frame.topleft)
    pygame.draw.rect(surf, _GOLD_DEEP, frame, width=2, border_radius=20)

    # case interior (back panel behind everything) — deep navy
    _vgradient_rect_round(surf, case, (18, 12, 44), (10, 6, 28), 16)

    # ── three shelves ──
    shelf_x = case.x + 12
    shelf_w = case.w - 24
    top0 = case.y + 18
    pitch = 124
    items_y = []
    for i, item in enumerate(items):
        sy = top0 + i * pitch
        items_y.append(sy)
        _shelf(surf, shelf_x, sy, shelf_w, item, 0.6)

    # ── glass sheen across the case (over margins, low alpha) ──
    _glass_sheen(surf, case)
    # thin inner glass frame highlight
    gl = pygame.Surface(case.size, pygame.SRCALPHA)
    pygame.draw.rect(gl, (210, 222, 245, 40), (0, 0, case.w, case.h),
                     width=2, border_radius=16)
    surf.blit(gl, case.topleft)

    # ── pediment + headline crowning the case ──
    ped_w, ped_h = W - 28, 70
    _pediment(surf, 14, 30, ped_w, ped_h)
    _outlined_text(surf, "ACHIEVEMENT EARNED!", (W // 2, 62), 22,
                   fill=_GOLD_BRIGHT, outline=(28, 12, 4), px=2,
                   shadow_offset=(2, 3))

    # ── tap plaque at the cabinet base ──
    _tap_plaque(surf, W // 2, case.bottom - 4)

    return surf


def _vgradient_rect_round(surf, rect, top, bot, radius):
    g = make_gradient_surface(rect.w, rect.h, [(0.0, top), (1.0, bot)])
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.blit(g, (0, 0))
    m = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, rect.w, rect.h),
                     border_radius=radius)
    panel.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(panel, rect.topleft)


ids = demo_varied_ids(3)
# Override to the exact three the brief lists, by icon glyph.
items = [
    ("pillar", "First Delivery", "Clear your very first pillar."),
    ("coin", "Pocket Change", "Collect 25 coins in one run."),
    ("powerup", "Power Up!", "Grab your first power-up."),
]

OUT = os.path.join(_ROOT, "docs", "achievements", "unlock_notice",
                   "award_list", "trophy-cabinet-shelves")
os.makedirs(OUT, exist_ok=True)

surf = render()
pygame.image.save(surf, os.path.join(OUT, "round_2.png"))
print("saved", os.path.join(OUT, "round_2.png"))
