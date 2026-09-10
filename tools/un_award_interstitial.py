"""Mockup: the `award-interstitial` concept — a brief celebratory full-screen
BEAT that plays on death BEFORE the run summary, then dissolves into a clean,
unmodified summary. Because it lives in TIME (not space), it occludes nothing
on the summary; its still here IS the ceremony frame itself.

The design intent the still must sell: a hero medallion strike that reads as
premium + FAST + tap-skippable, delivering the score rather than gating it.
Scratch tooling only — nothing here is imported by the game; `game/` untouched.
"""
import os
import math
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import lerp_color, blit_glow
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H


def _radial_vignette(surf, cx, cy, inner_r, outer_r, edge_col):
    """Deep-navy vignette that darkens toward the corners and pulls the eye to
    the medallion. Painted big-to-small so each smaller (more central) ring is
    LESS opaque — the centre stays clear, the corners go near-black. Cheap and
    identical on both build targets (no per-pixel surface locks)."""
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    maxd = math.hypot(max(cx, W - cx), max(cy, H - cy))
    # Concentric ANNULI (ring outlines) so per-ring alpha doesn't accumulate as
    # it would with stacked filled discs — each radius gets exactly its falloff.
    step = 2
    for r in range(int(maxd), 0, -step):
        t = max(0.0, (r - inner_r) / max(1, outer_r - inner_r))
        a = int(252 * min(1.0, t) ** 1.25)
        if a <= 0:
            continue
        pygame.draw.circle(vig, (*edge_col, a), (cx, cy), r, step + 1)
    surf.blit(vig, (0, 0))


def _crest_glint(surf, cx, cy, R):
    """A struck-metal glint: a bright crescent arc riding the upper-left rim
    (following the coin's curve, NOT a straight bar that reads as a cancel
    line) plus a tight specular bloom where the light hits hardest. Additive,
    so it blooms against the gold — the 'freshly minted, catching the light'
    beat."""
    gl = pygame.Surface((W, H), pygame.SRCALPHA)
    # multi-pass arc along the upper-left crest, fading at both ends by drawing
    # progressively shorter, brighter arcs stacked on a long faint base.
    light = math.radians(135)
    base = pygame.Rect(cx - R, cy - R, R * 2, R * 2)
    for spread, w, a in ((1.05, 5, 60), (0.72, 4, 90), (0.40, 3, 130)):
        pygame.draw.arc(gl, (255, 250, 235, a), base,
                        light - spread, light + spread, w)
    surf.blit(gl, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # tight specular bloom riding ON the rim crest — small + soft so it reads
    # as a catch-light, not a stray blob.
    hx = cx + int(math.cos(light) * R * 0.90)
    hy = cy - int(math.sin(light) * R * 0.90)
    blit_glow(surf, hx, hy, int(R * 0.20), (255, 252, 242), 120)
    pygame.draw.circle(surf, (255, 254, 248), (hx, hy), 3)


def _flare_ring(surf, cx, cy, R):
    """The sparkle-ring flare: a ring of outward-shooting light spokes plus
    twinkles, sized to crown the medallion. Spokes are additive so they bloom
    against the navy without a hard outline — the 'ta-da' burst."""
    flare = pygame.Surface((W, H), pygame.SRCALPHA)
    # long thin spokes radiating outward at uneven lengths (a real burst is
    # never perfectly even) — additive bloom.
    spokes = 16
    for i in range(spokes):
        a = i * math.tau / spokes + math.radians(11)
        long = (i % 2 == 0)
        r0 = R * 1.04
        r1 = R * (1.62 if long else 1.30)
        x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0
        x1, y1 = cx + math.cos(a) * r1, cy + math.sin(a) * r1
        w = 3 if long else 2
        pygame.draw.line(flare, (255, 244, 210, 120 if long else 70),
                         (x0, y0), (x1, y1), w)
    # four-point twinkles riding the ring at a few accents
    for i in range(8):
        a = i * math.tau / 8 - math.radians(20)
        sx = cx + int(math.cos(a) * R * 1.18)
        sy = cy + int(math.sin(a) * R * 1.18)
        sr = 7 if i % 2 == 0 else 4
        pygame.draw.line(flare, (255, 250, 232, 210), (sx - sr, sy), (sx + sr, sy), 2)
        pygame.draw.line(flare, (255, 250, 232, 210), (sx, sy - sr), (sx, sy + sr), 2)
        pygame.draw.circle(flare, (255, 255, 245, 230), (sx, sy), 2)
    surf.blit(flare, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _gold_text(surf, txt, center, size, tracking=0):
    """Gold engraved title: navy drop shadow under a top-lit gold fill with a
    pale upper sheen — matches the menu's gold-on-navy engraving."""
    f = _font(size, True)
    # optional letter tracking for the headline read
    if tracking:
        txt = (" " * 0).join(txt)
    sh = f.render(txt, True, _NIGHT_DEEP)
    sh.set_alpha(200)
    surf.blit(sh, sh.get_rect(center=(center[0] + 2, center[1] + 3)))
    body = f.render(txt, True, _GOLD_BRIGHT)
    r = body.get_rect(center=center)
    surf.blit(body, r)
    # pale sheen on the top edge of the glyphs
    sheen = f.render(txt, True, _GOLD_PALE)
    sheen.set_alpha(120)
    surf.blit(sheen, (r.x, r.y - 1))
    return r


def build():
    ids = demo_ids(2)
    a0 = ach.BY_ID[ids[0]]

    surf = pygame.Surface((W, H))

    # ── 1. Dissolve target: the real RUN SUMMARY, very dim, under everything ──
    # so the ceremony visibly sits IN FRONT of the score it's about to hand off
    # to — the player can feel the summary is already there, not being waited on.
    base = render_backdrop()
    base = base.copy()
    base.set_alpha(20)
    surf.fill(_NIGHT_DEEP)
    surf.blit(base, (0, 0))

    # ── 2. Deep-navy vignette pulling focus to the medallion ──
    cx, cy = W // 2, int(H * 0.42)
    _radial_vignette(surf, cx, cy, inner_r=54, outer_r=int(H * 0.40),
                     edge_col=_NIGHT_DEEP)
    # A top scrim so the summary's HEADLINE ghost stays fainter than the lower
    # 'RUN SUMMARY → score' hand-off cue — the eye should fall, not rise.
    top = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, int(H * 0.30)):
        a = int(150 * (1 - y / (H * 0.30)))
        pygame.draw.line(top, (*_NIGHT_DEEP, a), (0, y), (W, y))
    surf.blit(top, (0, 0))
    # a second soft navy wash low-down so the dim summary doesn't compete
    low = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(low, (*_PANEL_DARK, 120), (0, int(H * 0.66), W, H))
    surf.blit(low, (0, 0))

    R = 60  # medallion radius → ~120px badge

    # ── 3. Behind-the-medal radiance: a soft warm halo that fades into the
    # navy — small enough to hug the medal, never a flat orange disc. ──
    blit_glow(surf, cx, cy, int(R * 1.34), (255, 196, 96), 60)
    blit_glow(surf, cx, cy, int(R * 0.96), (255, 220, 140), 80)

    # ── 4. The flare ring (behind), then the medal, then the raking sweep ──
    _flare_ring(surf, cx, cy, R)

    # eyebrow kicker above the medal — tiny, fast, celebratory
    _gold_text(surf, "COMMENDATION EARNED", (cx, cy - R - 44), 17)
    # a thin gold hairline under the kicker
    hl_w = 116
    pygame.draw.line(surf, _GOLD_DEEP, (cx - hl_w, cy - R - 31),
                     (cx + hl_w, cy - R - 31), 1)

    # the struck medallion — the hero
    badge_rect = pygame.Rect(cx - R, cy - R, R * 2, R * 2)
    draw_badge(surf, a0.icon_key, badge_rect, True, False)

    # struck-metal glint on the upper-left crest — the "just minted" flash
    _crest_glint(surf, cx, cy, R)

    # ── 5. Title block beneath in gold ──
    ty = cy + R + 36
    _gold_text(surf, a0.title.upper(), (cx, ty), 30)
    # flavour line, soft pale
    fdesc = _font(15, True)
    d = fdesc.render(a0.desc, True, (210, 196, 232))
    d.set_alpha(220)
    surf.blit(d, d.get_rect(center=(cx, ty + 28)))

    # ── 6. Multiplicity pager: "1 / 2" + two pips (a run can pop several) ──
    py = ty + 60
    pf = _font(15, True)
    pager = pf.render("1 / 2", True, _GOLD_PALE)
    pager.set_alpha(235)
    pr = pager.get_rect(center=(cx, py))
    surf.blit(pager, pr)
    # two pips flanking — first lit gold, second dim (next in sequence)
    for i, (dx, lit) in enumerate(((-30, True), (30, False))):
        px = cx + dx
        col = _GOLD_BRIGHT if lit else (96, 86, 120)
        pygame.draw.circle(surf, col, (px, py + 1), 4)
        if lit:
            pygame.draw.circle(surf, _GOLD_PALE, (px, py + 1), 4, 1)

    # ── 7. The hand-off cue: a faint 'RUN SUMMARY' label low, behind the
    # vignette, so the frame reads as DELIVERING the summary it sits in front of.
    rs = _font(16, True)
    rstxt = rs.render("RUN SUMMARY", True, (150, 138, 178))
    rstxt.set_alpha(85)
    surf.blit(rstxt, rstxt.get_rect(center=(cx, int(H * 0.80))))
    # a downward chevron under it — 'dissolving into' the score below
    chy = int(H * 0.80) + 18
    pygame.draw.lines(surf, (130, 120, 160), False,
                      [(cx - 8, chy), (cx, chy + 6), (cx + 8, chy)], 2)

    # ── 8. TAP TO CONTINUE — the skip affordance, pinned bottom ──
    tap = _font(15, True)
    tt = tap.render("TAP TO CONTINUE", True, _GOLD_BRIGHT)
    # subtle pulse-pill behind it so it reads as interactive
    pill_w, pill_h = tt.get_width() + 32, 28
    pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*_PANEL_LIGHTER, 200), (0, 0, pill_w, pill_h),
                     border_radius=14)
    pygame.draw.rect(pill, (*_GOLD_BRIGHT, 150), (0, 0, pill_w, pill_h),
                     width=1, border_radius=14)
    py2 = int(H * 0.915)
    surf.blit(pill, pill.get_rect(center=(cx, py2)))
    surf.blit(tt, tt.get_rect(center=(cx, py2)))

    # ── 9. A thin progress bar high under the kicker hints the beat is ~1.2s,
    # not an open-ended wait — it's almost full (handing off imminently).
    bar_y = 14
    bw = 150
    pygame.draw.rect(surf, (*_PANEL_LIGHTER, ), (cx - bw // 2, bar_y, bw, 4),
                     border_radius=2)
    fill = int(bw * 0.82)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - bw // 2, bar_y, fill, 4),
                     border_radius=2)
    pygame.draw.circle(surf, _GOLD_PALE, (cx - bw // 2 + fill, bar_y + 2), 3)

    return surf


def main():
    surf = build()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice", "award-interstitial")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "round_1.png")
    pygame.image.save(surf, path)
    print(path)


if __name__ == "__main__":
    main()
