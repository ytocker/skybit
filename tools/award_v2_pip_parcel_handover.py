"""Mockup: the `pip-parcel-handover` award concept — a lore-forward GIFT REVEAL.

Pip the scarlet macaw courier has just flown your commendation to you; she flips
the parcel open and the struck medallion ERUPTS out of the box mouth on a clean
lower-left -> upper-right diagonal, riding a firework starburst, with packing
sparkle spilling out. The badge is the single brightest hero; Pip + the opened
parcel anchor the diagonal's foot.

Composition law (the make-or-break): ONE diagonal read, badge brightest. Every
supporting beat (coins, spare parcels, sparks) is flattened to silhouette
TEXTURE so the still survives the squint test at 360px — no object soup.

Scratch tooling only; nothing here is imported by the game. `game/` untouched.
"""
import os
import math
import random
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import lerp_color, blit_glow
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H
from game.parrot import get_parrot
from game import surprise_box_variants as boxes
from game.entities import CelebrationFireworkBurst, PoofGrain


# Diagonal axis anchors — the spine the whole composition reads along.
BOX_C   = (130, 454)          # opened-parcel mouth (foot of the diagonal)
BADGE_C = (250, 228)          # hero medallion (payoff, upper-right)
R       = 64                  # medallion radius -> ~128px badge


def _starfield(surf, rng, n=46):
    """A few cold stars on the deep navy so the gold badge has something to pop
    against — kept faint and small so they never read as more sparkle clutter."""
    for _ in range(n):
        x = rng.randint(0, W)
        y = rng.randint(0, int(H * 0.62))
        a = rng.randint(30, 110)
        r = 1 if rng.random() < 0.8 else 2
        s = pygame.Surface((r * 2 + 1, r * 2 + 1), pygame.SRCALPHA)
        pygame.draw.circle(s, (210, 218, 255, a), (r, r), r)
        surf.blit(s, (x - r, y - r))


def _diagonal_shaft(surf):
    """A soft warm light-shaft running BOX -> BADGE so the eye is railed up the
    diagonal before any object asks for attention. Drawn as a stack of fat,
    additive, fading line segments tapering toward the box — light pouring OUT
    of the opened parcel and carrying the medal up-right."""
    bx, by = BOX_C
    gx, gy = BADGE_C
    dx, dy = gx - bx, gy - by
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux                     # perpendicular (shaft half-width axis)
    shaft = pygame.Surface((W, H), pygame.SRCALPHA)
    steps = 40
    for i in range(steps):
        t = i / (steps - 1)
        # widen toward the badge, pinch to a near-point at the box mouth
        half = 6 + t * 30
        # brighter mid-shaft, fading at both ends
        a = int(46 * math.sin(min(1.0, t * 1.12) * math.pi) ** 1.3)
        if a <= 0:
            continue
        cx = bx + ux * length * t
        cy = by + uy * length * t
        col = lerp_color(_GOLD_DEEP, (255, 226, 150), t)
        p0 = (cx + nx * half, cy + ny * half)
        p1 = (cx - nx * half, cy - ny * half)
        pygame.draw.line(shaft, (*col, a), p0, p1, 10)
    surf.blit(shaft, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _spare_parcel(surf, cx, cy, w, h, base, shade, tilt):
    """A spare wrapped commendation behind Pip — one per PENDING unlock. Drawn
    as a FLAT tilted silhouette (body + one cross ribbon + a tick of bow), no
    interior detail, so the stack reads as quiet 'more to come' texture and
    never competes with the open hero parcel."""
    card = pygame.Surface((w + 16, h + 22), pygame.SRCALPHA)
    ox, oy = 8, 14
    rect = pygame.Rect(ox, oy, w, h)
    # body — single vertical gradient, dark keyline
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        body.fill(lerp_color(base, shade, yy / max(1, h - 1)) + (255,),
                  pygame.Rect(0, yy, w, 1))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=5)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    card.blit(body, (ox, oy))
    pygame.draw.rect(card, (20, 8, 26), rect, 2, border_radius=5)
    # one gold cross ribbon (flat) + a small gold bow tick on top
    pygame.draw.rect(card, _GOLD_DEEP, (rect.centerx - 3, rect.y, 6, h))
    pygame.draw.rect(card, _GOLD_DEEP, (rect.x, rect.centery - 3, w, 6))
    pygame.draw.line(card, _GOLD_BRIGHT, (rect.centerx - 2, rect.y),
                     (rect.centerx - 2, rect.bottom), 1)
    bowx = rect.centerx
    pygame.draw.ellipse(card, _GOLD_DEEP, (bowx - 11, rect.y - 6, 9, 8))
    pygame.draw.ellipse(card, _GOLD_DEEP, (bowx + 2, rect.y - 6, 9, 8))
    pygame.draw.circle(card, _GOLD_BRIGHT, (bowx, rect.y - 2), 3)
    rot = pygame.transform.rotozoom(card, tilt, 1.0)
    # soft contact shadow grounding the stack
    sh = pygame.Surface((w, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 90), sh.get_rect())
    surf.blit(sh, sh.get_rect(center=(cx, cy + h // 2 + 4)))
    surf.blit(rot, rot.get_rect(center=(cx, cy)))


def _open_parcel(surf, cx, cy):
    """The hero parcel, OPENED: the red box body low, its lid tipped off to the
    side on the far rim, and the bow flying free up-left — so the badge clearly
    just burst OUT of the mouth. Built from the surprise-box silhouette language
    (red gradient body + gold cross ribbon) but cracked open and lit from within
    by the diagonal shaft, so it anchors the foot of the read without a second
    bright 'gift' competing with the medal."""
    bw, bh = 86, 64
    # ── box body (a flat red gradient slab with a gold cross + dark keyline) ──
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for yy in range(bh):
        body.fill(lerp_color((214, 52, 56), (132, 18, 26),
                             yy / max(1, bh - 1)) + (255,),
                  pygame.Rect(0, yy, bw, 1))
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=6)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # dark open mouth carved into the top so the badge reads as rising OUT of it
    mouth = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pts = [(8, 0), (bw - 8, 0), (bw - 18, 20), (18, 20)]
    pygame.draw.polygon(mouth, (16, 6, 22, 235), pts)
    body.blit(mouth, (0, 0))
    # gold cross ribbon on the front face (flat texture)
    pygame.draw.rect(body, _GOLD_DEEP, (bw // 2 - 4, 18, 8, bh - 18))
    pygame.draw.rect(body, _GOLD_DEEP, (0, bh // 2 + 6, bw, 8))
    pygame.draw.line(body, _GOLD_BRIGHT, (bw // 2 - 3, 18), (bw // 2 - 3, bh), 1)
    pygame.draw.rect(body, (20, 8, 26), (0, 0, bw, bh), 2, border_radius=6)

    # contact shadow under the box
    sh = pygame.Surface((bw + 20, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 120), sh.get_rect())
    surf.blit(sh, sh.get_rect(center=(cx, cy + bh // 2 + 2)))
    surf.blit(body, body.get_rect(center=(cx, cy + 4)))

    # warm interior glow at the mouth — light spilling out as the badge erupts
    blit_glow(surf, cx, cy - bh // 2 + 8, 30, (255, 214, 130), 120)

    # ── the lid, tipped off onto the far (right) rim ──
    lw, lh = 64, 20
    lid = pygame.Surface((lw, lh), pygame.SRCALPHA)
    for yy in range(lh):
        lid.fill(lerp_color((232, 78, 76), (150, 24, 30),
                            yy / max(1, lh - 1)) + (255,),
                 pygame.Rect(0, yy, lw, 1))
    lmask = pygame.Surface((lw, lh), pygame.SRCALPHA)
    pygame.draw.rect(lmask, (255, 255, 255, 255), lmask.get_rect(), border_radius=5)
    lid.blit(lmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(lid, _GOLD_DEEP, (lw // 2 - 4, 0, 8, lh))
    pygame.draw.rect(lid, (20, 8, 26), (0, 0, lw, lh), 2, border_radius=5)
    lid_rot = pygame.transform.rotozoom(lid, -22, 1.0)
    surf.blit(lid_rot, lid_rot.get_rect(center=(cx + bw // 2 + 6, cy - 4)))

    # ── the bow, flying free up-left off the box (motion = it just popped) ──
    bow = pygame.Surface((40, 30), pygame.SRCALPHA)
    boxes._draw_bow(bow, 20, 16, _GOLD_BRIGHT, _GOLD_PALE)
    bow_rot = pygame.transform.rotozoom(bow, 26, 0.95)
    surf.blit(bow_rot, bow_rot.get_rect(center=(cx - bw // 2 - 6, cy - bh // 2 - 10)))


def _step_fx(objs, dt, n):
    for _ in range(n):
        for o in objs:
            o.update(dt)


def _gold_text(surf, txt, center, size, sheen=True):
    f = _font(size, True)
    sh = f.render(txt, True, _NIGHT_DEEP)
    sh.set_alpha(205)
    surf.blit(sh, sh.get_rect(center=(center[0] + 2, center[1] + 3)))
    body = f.render(txt, True, _GOLD_BRIGHT)
    r = body.get_rect(center=center)
    surf.blit(body, r)
    if sheen:
        sn = f.render(txt, True, _GOLD_PALE)
        sn.set_alpha(130)
        surf.blit(sn, (r.x, r.y - 1))
    return r


def _crest_glint(surf, cx, cy, R):
    """Struck-metal catch-light on the medallion's upper-left crest — the 'just
    minted, fresh out of the box' flash."""
    gl = pygame.Surface((W, H), pygame.SRCALPHA)
    light = math.radians(135)
    base = pygame.Rect(cx - R, cy - R, R * 2, R * 2)
    for spread, w, a in ((1.0, 5, 55), (0.7, 4, 90), (0.4, 3, 130)):
        pygame.draw.arc(gl, (255, 250, 235, a), base, light - spread,
                        light + spread, w)
    surf.blit(gl, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    hx = cx + int(math.cos(light) * R * 0.88)
    hy = cy - int(math.sin(light) * R * 0.88)
    blit_glow(surf, hx, hy, int(R * 0.20), (255, 252, 242), 120)
    pygame.draw.circle(surf, (255, 254, 248), (hx, hy), 3)


def build():
    ids = demo_ids(2)
    a0 = ach.BY_ID[ids[0]]
    rng = random.Random(7)

    surf = pygame.Surface((W, H))

    # ── 1. Night backdrop: deep-navy vertical wash + faint dim summary ghost ──
    for y in range(H):
        surf.fill(lerp_color(_NIGHT_DEEP, (14, 8, 34), y / (H - 1)),
                  pygame.Rect(0, y, W, 1))
    ghost = render_backdrop().copy()
    ghost.set_alpha(7)
    surf.blit(ghost, (0, 0))
    # scrim the whole frame back down so the dim summary never reads as words —
    # it should be a felt presence (the score we're handing off to), not text
    # competing with the gold title.
    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((*_NIGHT_DEEP, 150))
    surf.blit(scrim, (0, 0))
    _starfield(surf, rng)

    # corner vignette so the diagonal stays the only lit lane
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(int(math.hypot(W, H)) // 2, 0, -3):
        t = r / (math.hypot(W, H) / 2)
        a = int(150 * t ** 2.0)
        pygame.draw.circle(vig, (*_NIGHT_DEEP, a), (W // 2, int(H * 0.42)), r, 4)
    surf.blit(vig, (0, 0))

    # ── 2. The diagonal light-shaft — railing BOX -> BADGE before any object ──
    _diagonal_shaft(surf)

    # ── 3. Spare wrapped parcels behind Pip (2 pending commendations) ──
    # Flat tilted silhouettes, dimmed, low-left — quiet 'more to come' texture.
    _spare_parcel(surf, 56, 506, 46, 40, (150, 30, 36), (88, 14, 22), 10)
    _spare_parcel(surf, 92, 520, 42, 36, (120, 26, 34), (70, 12, 20), -8)

    # ── 4. Pip the courier — scaled ~2x, tilted, anchoring the lower-left ──
    pip = get_parrot(2, 14)                      # mid-flap frame, banked up-right
    pip = pygame.transform.rotozoom(pip, 0, 2.05)
    # cool back-rim behind Pip so her scarlet silhouette separates cleanly off
    # the navy (a warm rim muddied into her red feathers in r1)
    rim = pygame.Surface((150, 150), pygame.SRCALPHA)
    for r in range(64, 0, -2):
        a = int(70 * (1 - r / 64) ** 1.4)
        pygame.draw.ellipse(rim, (44, 50, 98, a),
                            (75 - r, 75 - int(r * 0.82), r * 2, int(r * 1.64)))
    surf.blit(rim, rim.get_rect(center=(84, 428)))
    surf.blit(pip, pip.get_rect(center=(86, 430)))

    # ── 5. The opened hero parcel at the diagonal's foot ──
    _open_parcel(surf, *BOX_C)

    # ── 6. Packing-sparkle spill — PoofGrain dust + a flat coin texture ──
    # Stepped to a settled moment so the dust hangs as a cloud, not confetti.
    grains = []
    for _ in range(34):
        ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)   # upward fan
        spd = rng.uniform(40, 150)
        col = rng.choice([(255, 224, 150), (255, 196, 96), (252, 244, 218)])
        grains.append(PoofGrain(BOX_C[0], BOX_C[1] - 18,
                                math.cos(ang) * spd, math.sin(ang) * spd,
                                rng.uniform(0.5, 0.9), rng.randint(2, 4), col))
    _step_fx(grains, 1 / 60, 9)
    for g in grains:
        g.draw(surf)

    # flat gold coin TEXTURE riding the diagonal (silhouette discs, no detail)
    bx, by = BOX_C
    gx, gy = BADGE_C
    for f, jx, jy, rr in ((0.18, -16, 8, 6), (0.30, 14, -4, 5), (0.44, -8, 10, 7),
                          (0.40, 22, 6, 4), (0.24, 4, -12, 5)):
        x = int(bx + (gx - bx) * f + jx)
        y = int(by + (gy - by) * f + jy)
        pygame.draw.circle(surf, (210, 150, 32), (x, y), rr)
        pygame.draw.circle(surf, (255, 224, 132), (x, y), rr - 2)
        pygame.draw.circle(surf, (150, 100, 18), (x, y), rr, 1)

    # ── 7. The firework starburst out of the box mouth, BEHIND the badge ──
    bursts = [
        CelebrationFireworkBurst(BADGE_C[0], BADGE_C[1], 0.0, (255, 220, 110), 0.95),
        CelebrationFireworkBurst(BADGE_C[0] - 18, BADGE_C[1] + 14, 0.12,
                                 (255, 150, 70), 0.64),
        CelebrationFireworkBurst(BADGE_C[0] + 20, BADGE_C[1] - 10, 0.18,
                                 (252, 244, 218), 0.58),
    ]
    _step_fx(bursts, 1 / 60, 22)               # ~0.37s in: rays at full flare
    for b in bursts:
        b.draw(surf)

    # ── 8. The HERO medallion — the single brightest object, the payoff ──
    # warm radiance hugging the medal. The outer peach halo is dimmed +
    # desaturated and pulled tighter so it FRAMES the medal rather than
    # outshining it; the inner core is pushed bright so the gold medallion
    # itself is the single brightest, highest-contrast value on screen.
    blit_glow(surf, *BADGE_C, int(R * 1.55), (176, 120, 70), 26)
    blit_glow(surf, *BADGE_C, int(R * 1.05), (236, 184, 112), 52)
    blit_glow(surf, *BADGE_C, int(R * 0.74), (255, 244, 196), 130)
    badge_rect = pygame.Rect(BADGE_C[0] - R, BADGE_C[1] - R, R * 2, R * 2)
    draw_badge(surf, a0.icon_key, badge_rect, True, False)
    _crest_glint(surf, *BADGE_C, R)

    # ── 9. Title block upper-right, following the badge's arc ──
    tx = W // 2 - 18
    # small kicker, then the achievement title BIG — a clear payoff hierarchy.
    # Kept clear of the badge bloom (which lives lower-right) so the type stays
    # crisp on clean navy.
    _gold_text(surf, "COMMENDATION  EARNED", (tx, 70), 15)
    pygame.draw.line(surf, _GOLD_DEEP, (tx - 78, 84), (tx + 78, 84), 1)
    _gold_text(surf, a0.title.upper(), (tx, 108), 28)
    fd = _font(13, True)
    d = fd.render(a0.desc, True, (214, 200, 236))
    d.set_alpha(225)
    surf.blit(d, d.get_rect(center=(tx, 132)))

    # ── 10. Multiplicity pager '1 / 2' — a run can pop several ──
    py = 154
    pager = _font(13, True).render("1 / 2", True, _GOLD_PALE)
    pager.set_alpha(230)
    surf.blit(pager, pager.get_rect(center=(tx, py)))
    for dx, lit in ((-26, True), (26, False)):
        col = _GOLD_BRIGHT if lit else (96, 86, 120)
        pygame.draw.circle(surf, col, (tx + dx, py + 1), 4)
        if lit:
            pygame.draw.circle(surf, _GOLD_PALE, (tx + dx, py + 1), 4, 1)

    # ── 11. TAP TO CONTINUE — bottom affordance ──
    tap = _font(15, True)
    tt = tap.render("TAP TO CONTINUE", True, _GOLD_BRIGHT)
    pw, ph = tt.get_width() + 34, 30
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*_PANEL_LIGHTER, 215), (0, 0, pw, ph), border_radius=15)
    pygame.draw.rect(pill, (*_GOLD_BRIGHT, 160), (0, 0, pw, ph), 1, border_radius=15)
    py2 = int(H * 0.93)
    surf.blit(pill, pill.get_rect(center=(W // 2, py2)))
    surf.blit(tt, tt.get_rect(center=(W // 2, py2)))

    return surf


def main():
    surf = build()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice",
                       "award_interstitial_v2", "pip-parcel-handover")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "round_2.png")
    pygame.image.save(surf, path)
    print(path)


if __name__ == "__main__":
    main()
