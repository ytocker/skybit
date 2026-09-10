"""dispatch-manifest — the achievement-unlock screen styled as a courier
DISPATCH SLIP: earned commendations stamped as ✓ line-items on a torn,
perforated paper manifest over the deep-night field.

Scratch mockup tooling. Nothing here is imported by the game; `game/` is
untouched (procedural-art hard rule honoured — every mark is drawn from code).
"""
import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
import math
import random

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
if not pygame.get_init():
    pygame.init()

from tools.unlock_notice_common import render_backdrop, demo_varied_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, make_gradient_surface, lerp_color
from game.hud import _font, _NIGHT_DEEP, _PANEL_DARK, _PANEL_LIGHTER
from game.config import W, H

ids = demo_varied_ids(3)
items = [(ach.BY_ID[i].icon_key, ach.BY_ID[i].title, ach.BY_ID[i].desc)
         for i in ids]

# ── Courier-slip palette ─────────────────────────────────────────────────────
# ONE accent story: gold badge + scarlet ✓ stamp on warm cream. The paper is a
# warm parchment ramp; ink is a soft sepia (never pure black) so type reads like
# a rubber-stamped form, not a laser print.
CREAM_HI   = (247, 236, 210)   # lit upper sheet
CREAM_MID  = (236, 222, 188)   # body parchment
CREAM_LO   = (221, 203, 162)   # shadowed lower sheet / fold
PAPER_EDGE = (196, 174, 128)   # torn-edge core (slightly darker pulp)
INK        = ( 74,  56,  34)   # sepia stamp ink (headline / names)
INK_SOFT   = (120,  98,  68)   # lighter sepia for descriptions / rules
SCARLET    = (188,  42,  38)   # hand-stamped ✓ + seal + header bar
SCARLET_LO = (146,  26,  26)   # seal shadow side
WAX_HI     = (224,  78,  64)   # wax seal lit crest
GOLD_BORD  = (198, 150,  52)   # thin gold frame on the stamp-box / seal ring


def _rng(seed):
    return random.Random(seed)


# ── torn + perforated parchment slip ─────────────────────────────────────────

def _torn_slip(w, h, seed=7):
    """A tall parchment slip with sine-jittered torn vertical edges and a row of
    punched perforation holes near top + bottom. Returned as an SRCALPHA surface
    so the night field shows through the torn gaps and punch-holes."""
    rng = _rng(seed)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Build the ragged outline: left edge top→bottom, then right edge bottom→top.
    # Amplitude is small so the slip still reads as a clean rectangle with a
    # deckled hand-torn margin, not a blob.
    amp = 4.0
    step = 6
    left = []
    right = []
    base_l, base_r = 3.0, w - 3.0
    for y in range(0, h + 1, step):
        ph = y * 0.07
        lx = base_l + math.sin(ph * 1.3 + 0.5) * amp + rng.uniform(-1.4, 1.4)
        rx = base_r - math.sin(ph * 1.1 + 1.7) * amp - rng.uniform(-1.4, 1.4)
        left.append((lx, y))
        right.append((rx, y))
    outline = left + right[::-1]

    # Paper body: a vertical cream gradient clipped to the torn outline. A soft
    # diagonal sheen across the top sells "loose sheet caught in the light."
    grad = make_gradient_surface(w, h, [(0.0, CREAM_HI), (0.5, CREAM_MID),
                                        (1.0, CREAM_LO)])
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(int(x), int(y)) for x, y in outline])
    body = grad.convert_alpha()
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Faint fibre flecks — kept VERY sparse so paper texture never turns the
    # type behind it to noise (AD steer). Just enough to break a flat fill.
    for _ in range(70):
        fx = rng.randint(8, w - 8)
        fy = rng.randint(8, h - 8)
        a = rng.randint(10, 26)
        c = INK_SOFT if rng.random() < 0.5 else CREAM_LO
        body.set_at((fx, fy), (*c, a)) if False else None
        pygame.draw.circle(body, (*c, a), (fx, fy), 1)

    surf.blit(body, (0, 0))

    # Darken the torn edges so the rip has thickness (a lit top lip + shadow).
    pygame.draw.lines(surf, (*PAPER_EDGE, 200), False,
                      [(int(x), int(y)) for x, y in left], 2)
    pygame.draw.lines(surf, (*PAPER_EDGE, 200), False,
                      [(int(x), int(y)) for x, y in right], 2)

    return surf, outline


def _punch_perforations(surf, y, w, holes=15, r=3, margin=14):
    """Punch a row of transparent circles across the sheet at height ``y`` — the
    tear-off perforation. A faint shadow on the lower lip of each hole gives the
    punched paper depth."""
    span = w - margin * 2
    for i in range(holes):
        cx = margin + int(span * i / (holes - 1))
        # shadow lip first (just below), then knock the actual hole transparent
        pygame.draw.circle(surf, (90, 72, 44, 120), (cx, y + 1), r)
        pygame.draw.circle(surf, (0, 0, 0, 0), (cx, y), r)
        pygame.draw.circle(surf, (0, 0, 0, 0), (cx, y), r,
                           0)  # ensure cleared
    # erase via BLEND so the holes are truly see-through
    knock = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for i in range(holes):
        cx = margin + int(span * i / (holes - 1))
        pygame.draw.circle(knock, (255, 255, 255, 255), (cx, y), r)
    surf.blit(knock, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


# ── rubber-stamp ink helpers ─────────────────────────────────────────────────

def _stamp_text(surf, txt, center, size, color, jitter=1.0, alpha=255,
                seed=0):
    """Render text the way an inked rubber stamp lands: slightly uneven coverage
    by stacking the glyph a couple times with tiny offsets + a speckled erase, so
    it reads hand-pressed rather than printed. Returns the blit rect."""
    f = _font(size, True)
    img = f.render(txt, True, color)
    img = img.convert_alpha()
    if alpha < 255:
        img.set_alpha(alpha)
    rng = _rng(seed)
    # speckle: knock out a few pixels so the ink looks worn
    for _ in range(int(img.get_width() * 0.18)):
        x = rng.randint(0, img.get_width() - 1)
        y = rng.randint(0, img.get_height() - 1)
        if img.get_at((x, y))[3] > 60:
            pygame.draw.circle(img, (0, 0, 0, 0), (x, y), rng.choice([0, 0, 1]))
    r = img.get_rect(center=center)
    # faint double-strike to feel like uneven pressure
    surf.blit(img, (r.x + jitter, r.y + jitter))
    surf.blit(img, r.topleft)
    return r


def _scarlet_check(surf, cx, cy, s, seed=0):
    """A scarlet hand-stamped ✓ — two strokes, slightly rough, with an ink halo
    so it reads as wet rubber-stamp ink pressed over the badge corner."""
    rng = _rng(seed)
    # soft ink bloom under the stroke
    bloom = pygame.Surface((s * 3, s * 3), pygame.SRCALPHA)
    pygame.draw.circle(bloom, (*SCARLET, 40), (int(s * 1.5), int(s * 1.5)),
                       int(s * 1.2))
    surf.blit(bloom, (int(cx - s * 1.5), int(cy - s * 1.5)))
    # the check: short stroke down-right, long stroke up-right — drawn bold so
    # the hand-stamp reads as the loud "approved" mark, not a faint tick.
    p0 = (cx - s * 1.00, cy - s * 0.04)
    p1 = (cx - s * 0.20, cy + s * 0.78)
    p2 = (cx + s * 1.10, cy - s * 0.98)
    w = max(5, int(s * 0.42))
    for jx, jy in ((0, 0), (rng.uniform(-1.2, 1.2), rng.uniform(-1.2, 1.2))):
        pygame.draw.lines(surf, SCARLET, False,
                          [(p0[0] + jx, p0[1] + jy),
                           (p1[0] + jx, p1[1] + jy),
                           (p2[0] + jx, p2[1] + jy)], w)
    # rounded stroke ends so the ink doesn't taper to a hairline
    for p in (p0, p1, p2):
        pygame.draw.circle(surf, SCARLET, (int(p[0]), int(p[1])), w // 2)


def _wax_seal(surf, cx, cy, r):
    """A small wax-red dispatch seal: a domed scarlet wafer with a thin gold ring
    and a tiny embossed wing mark — the courier's authorising stamp, top-right."""
    # soft drop shadow
    sh = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
    pygame.draw.circle(sh, (40, 14, 10, 110), (int(r * 1.5), int(r * 1.6)), r)
    surf.blit(sh, (int(cx - r * 1.5), int(cy - r * 1.5)))
    # radial wax dome — lit upper-left
    for i in range(r, 0, -1):
        t = 1 - i / r
        c = lerp_color(WAX_HI, SCARLET_LO, t)
        ox = int(-i * 0.18)
        oy = int(-i * 0.18)
        pygame.draw.circle(surf, c, (cx + ox, cy + oy), i)
    # scalloped wax rim (wax-press notches)
    pts = []
    for k in range(28):
        a = k / 28 * math.tau
        rad = r * (1.04 if k % 2 == 0 else 0.97)
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    pygame.draw.polygon(surf, SCARLET_LO,
                        [(int(x), int(y)) for x, y in pts], 2)
    # thin gold authorising ring
    pygame.draw.circle(surf, GOLD_BORD, (cx, cy), int(r * 0.74), 2)
    # embossed courier wing-tick at centre — a small four-point spark struck
    # into the wax (dark deboss offset down-right, lit highlight up-left). Drawn
    # procedurally so it never depends on a glyph the bundled font may lack.
    def _spark(scx, scy, col):
        sr = r * 0.42
        pts = [(scx, scy - sr), (scx + sr * 0.26, scy - sr * 0.26),
               (scx + sr, scy), (scx + sr * 0.26, scy + sr * 0.26),
               (scx, scy + sr), (scx - sr * 0.26, scy + sr * 0.26),
               (scx - sr, scy), (scx - sr * 0.26, scy - sr * 0.26)]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    _spark(cx + 1, cy + 1, SCARLET_LO)
    _spark(cx - 1, cy - 1, WAX_HI)
    _spark(cx, cy, (252, 226, 206))


# ── compose the screen ───────────────────────────────────────────────────────

def render():
    surf = pygame.Surface((W, H))

    # Deep-night field behind the slip — the game's night palette, vignetted so
    # the cream slip pops as the lit focal object.
    field = make_gradient_surface(W, H, [(0.0, _NIGHT_DEEP),
                                         (0.55, _PANEL_DARK),
                                         (1.0, _PANEL_LIGHTER)])
    surf.blit(field, (0, 0))

    # Dim ghost of the run summary underneath, so the slip feels laid OVER the
    # results it files away (story beat). Heavily darkened.
    ghost = render_backdrop()
    ghost.set_alpha(46)
    surf.blit(ghost, (0, 0))

    # vignette
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(90):
        a = int(2.0 * i)
        pygame.draw.rect(vig, (0, 0, 0, min(120, a)),
                         (i, i, W - i * 2, H - i * 2), 2,
                         border_radius=20)
    surf.blit(vig, (0, 0))

    # ── the slip ──────────────────────────────────────────────────────────────
    slip_w = W - 40
    slip_x = 20
    slip_y = 24
    slip_h = H - 48
    slip, outline = _torn_slip(slip_w, slip_h, seed=11)

    # perforation rows: just under the header, and the tear-off tab line
    header_h = 104
    perf_top_y = header_h + 6
    perf_tab_y = slip_h - 70
    _punch_perforations(slip, perf_top_y, slip_w, holes=17, r=3)
    _punch_perforations(slip, perf_tab_y, slip_w, holes=17, r=3)

    # soft cast shadow under the whole slip
    sh = pygame.Surface((slip_w + 16, slip_h + 16), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120),
                        [(int(x + 8), int(y + 12)) for x, y in outline])
    surf.blit(sh, (slip_x - 8, slip_y - 8))
    surf.blit(slip, (slip_x, slip_y))

    # Everything below is drawn in SCREEN space at slip offset.
    ox, oy = slip_x, slip_y

    # ── header block: rubber-stamped on parchment ─────────────────────────────
    # A scarlet ruled frame (the stamp's box) with a tiny "DISPATCH SLIP" kicker,
    # the big ACHIEVEMENT EARNED! headline in sepia ink, and the wax seal pinned
    # to the top-right corner.
    hx0, hy0 = ox + 16, oy + 14
    hx1 = ox + slip_w - 16
    hy1 = oy + header_h - 8
    # double-rule stamp frame (rubber-stamp outline look)
    for inset, wdt in ((0, 3), (5, 1)):
        pygame.draw.rect(surf, SCARLET,
                         (hx0 + inset, hy0 + inset,
                          hx1 - hx0 - inset * 2, hy1 - hy0 - inset * 2),
                         wdt, border_radius=6)
    # kicker line — biased left of centre so it clears the corner wax seal.
    _stamp_text(surf, "— DISPATCH SLIP —", (hx0 + 96, hy0 + 16),
                14, SCARLET, jitter=0.6, seed=3)
    # headline — ONE confident phrase in a single scarlet rubber-stamp ink, so it
    # reads as one stamped commendation rather than a sepia title over a red
    # error-stamp. Both words share the same colour, size and two-strike texture;
    # they stack on two tight lines (the phrase is too wide for the frame at this
    # weight) with matching scarlet so the eye reads them as a unit.
    hcx = (hx0 + hx1) // 2
    _stamp_text(surf, "ACHIEVEMENT", (hcx, hy0 + 46),
                30, SCARLET, jitter=1.0, seed=1)
    er = _stamp_text(surf, "EARNED!", (hcx, hy0 + 76),
                     30, SCARLET, jitter=1.0, seed=2)
    # a thin scarlet underline just under EARNED! pulls the two stacked words into
    # one headline block; clearance below the descenders keeps it off the type.
    ul_y = er.bottom + 1
    pygame.draw.line(surf, SCARLET, (hcx - 64, ul_y), (hcx + 64, ul_y), 2)
    # wax dispatch seal pinned over the top-right corner of the frame
    _wax_seal(surf, hx1 - 8, hy0 + 4, 20)

    # ── line-items ────────────────────────────────────────────────────────────
    # Three ruled rows, each: a gold-framed navy stamp-box holding the REAL
    # badge with a scarlet ✓ over its corner; the NAME in bold sepia caps on the
    # ruled line; a short description beneath; a faint dotted rule dividing rows.
    list_top = oy + header_h + 18
    list_bot = oy + perf_tab_y - 18
    n = len(items)
    row_h = (list_bot - list_top) // n
    box = 60          # stamp-box size
    badge_sz = 46     # ~44px badge per AD spec

    name_f = _font(23, True)
    desc_f = _font(15, True)

    for idx, (icon_key, title, desc) in enumerate(items):
        ry = list_top + idx * row_h
        rcy = ry + row_h // 2

        # left stamp-box: navy enamel field + thin gold frame, so the gold badge
        # never collapses in value on cream (AD steer).
        bx = ox + 26
        by = rcy - box // 2
        # box shadow
        bsh = pygame.Surface((box + 8, box + 8), pygame.SRCALPHA)
        pygame.draw.rect(bsh, (0, 0, 0, 90), (0, 0, box + 8, box + 8),
                         border_radius=10)
        surf.blit(bsh, (bx - 2, by + 3))
        # navy field
        navy = make_gradient_surface(box, box, [(0.0, _PANEL_LIGHTER),
                                                (1.0, _PANEL_DARK)])
        rr = pygame.Surface((box, box), pygame.SRCALPHA)
        rr.blit(navy, (0, 0))
        m = pygame.Surface((box, box), pygame.SRCALPHA)
        pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, box, box),
                         border_radius=10)
        rr.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(rr, (bx, by))
        # thin gold frame
        pygame.draw.rect(surf, GOLD_BORD, (bx, by, box, box), 2,
                         border_radius=10)

        # the REAL badge, centred in the box
        brect = pygame.Rect(0, 0, badge_sz, badge_sz)
        brect.center = (bx + box // 2, by + box // 2)
        draw_badge(surf, icon_key, brect, unlocked=True)

        # scarlet hand-stamped ✓ overlapping the box's top-right corner
        _scarlet_check(surf, bx + box - 7, by + 8, 13, seed=10 + idx)

        # text column
        tx = bx + box + 18
        # NAME — bold caps sepia on the ruled line
        nm = name_f.render(title.upper(), True, INK)
        nm_r = nm.get_rect(midleft=(tx, rcy - 9))
        # subtle drop so the stamped name sits on the paper
        nsh = name_f.render(title.upper(), True, (200, 184, 150))
        surf.blit(nsh, (nm_r.x + 1, nm_r.y + 1))
        surf.blit(nm, nm_r.topleft)

        # the ruled writing line under the name, running to the right margin
        rule_y = rcy + 6
        pygame.draw.line(surf, (*INK_SOFT, ), (tx, rule_y),
                         (ox + slip_w - 22, rule_y), 1)

        # DESCRIPTION beneath — kept short, lighter sepia
        ds = desc_f.render(desc, True, INK_SOFT)
        surf.blit(ds, ds.get_rect(midleft=(tx, rule_y + 14)).topleft)

        # faint dotted divider between rows (not under the last row)
        if idx < n - 1:
            dy = ry + row_h - 2
            for dxp in range(ox + 24, ox + slip_w - 24, 7):
                pygame.draw.line(surf, (170, 150, 112),
                                 (dxp, dy), (dxp + 3, dy), 1)

    # ── tear-off TAP tab footer ───────────────────────────────────────────────
    # Below the lower perforation: a slightly recessed tab with the scarlet
    # rubber-stamp call to action.
    tab_y0 = oy + perf_tab_y + 4
    tab_cy = (tab_y0 + oy + slip_h - 12) // 2
    # tint the tab a touch darker so it reads as the detachable stub
    tab = pygame.Surface((slip_w - 6, oy + slip_h - 10 - tab_y0),
                         pygame.SRCALPHA)
    tab.fill((150, 132, 96, 40))
    surf.blit(tab, (ox + 3, tab_y0))
    # stamped CTA
    _stamp_text(surf, "TAP TO FILE & CONTINUE",
                ((ox + slip_w // 2), tab_cy), 19, SCARLET, jitter=0.8,
                seed=21)
    # little tap glyph (a pointing pulse) to the right
    gx = ox + slip_w - 40
    blit_glow(surf, gx, tab_cy, 12, (210, 70, 60), 70)

    return surf


def main():
    surf = render()
    out_dir = os.path.join(_ROOT, "docs", "achievements", "unlock_notice",
                           "award_list", "dispatch-manifest")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(surf, path)
    print(path)


if __name__ == "__main__":
    main()
