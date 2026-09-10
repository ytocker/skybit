"""Warren roll-result celebration — the chosen design "E".

A high-res jester PRIZE-WHEEL (8 plum/lime wedges, crisp gold rim, three cardinal
gold studs, a cream hub holding the rolled N as the hero) crowned by the staff's
full mini-clown BAUBLE (4-point bell cap + lime belled ruff + grinning face),
seated low so the face touches the round frame. A GHOST roll re-skins the wheel to
a cool cyan/periwinkle. Ported into game/ (no tools/ import) so it ships in both
build targets; warren_demo renders it once per roll and pop-scales the bitmap.
"""
import math

import pygame

from game import hud
from game.draw import _shade_c
from game.pillar_staff import (
    PLUM, PLUM_DK, LIME, LIME_DK, GOLD, GOLD_HI, GOLD_DK, CREAM,
    _mini_clown_face, _marotte_ruff,
)

# Taller-than-wide popup so the tall jester cap clears the top of the canvas.
DW, DH = 264, 360
WHEEL_A, WHEEL_B = PLUM, LIME
WHEEL_A_G, WHEEL_B_G = (120, 220, 210), (150, 174, 255)   # ghost: cool cyan/periwinkle
# Ghost re-skin palette — the WHOLE medallion goes spectral: icy chrome replaces the
# warm gold, deep periwinkle replaces the plum, and a cool cream replaces the warm one.
GH_METAL, GH_METAL_HI, GH_METAL_DK = (196, 232, 244), (236, 250, 252), (84, 138, 176)
GH_INDIGO, GH_INDIGO_DK = (74, 86, 168), (44, 52, 112)
GH_CREAM = (228, 240, 252)


def _ghostify(surf):
    """Wash a warm sub-render (the jester bauble) into the spectral ghost palette so
    the crown matches the recoloured wheel — multiply toward periwinkle to cool the
    hue, then lift with a cyan add so it glows ethereal instead of muddying."""
    tint = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    tint.fill((150, 178, 252))
    surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    lift = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    lift.fill((30, 46, 74))
    surf.blit(lift, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def _wheel(canvas, c, R, ss, wedges, col_a, col_b, *, spin=0.42, rim=None,
           rim_w=6, cy=None, hi=GOLD_HI, spoke=PLUM_DK):
    """A radiating two-colour prize-wheel rosette with hairline keylines + an
    optional crisp rim. `cy` seats it low so a tall bauble can crown the top;
    `hi`/`spoke` let the ghost re-skin swap the rim sheen + spoke keylines."""
    cy = c if cy is None else cy
    step = math.tau / wedges
    for i in range(wedges):
        a0 = spin + i * step
        a1 = a0 + step
        col = col_a if i % 2 == 0 else col_b
        pygame.draw.polygon(canvas, col, [
            (c, cy),
            (c + math.cos(a0) * R, cy + math.sin(a0) * R),
            (c + math.cos(a1) * R, cy + math.sin(a1) * R)])
    for i in range(wedges):
        a = spin + i * step
        pygame.draw.line(canvas, _shade_c(spoke, -10), (c, cy),
                         (c + math.cos(a) * R, cy + math.sin(a) * R), max(1, ss))
    if rim is not None:
        pygame.draw.circle(canvas, _shade_c(rim, -45), (c, cy), R, max(2, int((rim_w + 2) * ss)))
        pygame.draw.circle(canvas, rim, (c, cy), R, max(2, int(rim_w * ss)))
        pygame.draw.circle(canvas, hi, (c, cy), R - int(rim_w * 0.5 * ss), max(1, ss))


def _gold_stud(canvas, cx, cy, r, ss, col=GOLD, hi=GOLD_HI):
    """A solid domed rivet/stud: dark seat + lit dome + a top-left pip — a single
    bold disc that survives the downscale where a belled tip would mud. `hi` lets
    the ghost re-skin swap the warm sheen for an icy one."""
    pygame.draw.circle(canvas, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(canvas, col, (int(cx), int(cy)), int(r - ss))
    pygame.draw.circle(canvas, hi, (int(cx - r * 0.34), int(cy - r * 0.34)),
                       max(1, int(r * 0.3)))


def _num_block(canvas, c, ncy, roll, ss, *, size=88, num_col=CREAM, edge_col=PLUM,
               shadow_a=110, edge_w=5):
    """The hero rolled number — vendored bold font with a soft drop shadow + a
    thick outline ring, the fill re-stamped LAST so the digit counters stay open."""
    nf = hud._font(int(size * ss), True)
    num = nf.render(str(roll), True, num_col)
    edge = nf.render(str(roll), True, edge_col)
    shadow = nf.render(str(roll), True, (0, 0, 0))
    shadow.set_alpha(shadow_a)
    canvas.blit(shadow, shadow.get_rect(center=(c + 3 * ss, ncy + 5 * ss)))
    o = edge_w * ss
    for ang in range(0, 360, 15):
        ox = math.cos(math.radians(ang)) * o
        oy = math.sin(math.radians(ang)) * o
        canvas.blit(edge, edge.get_rect(center=(c + ox, ncy + oy)))
    canvas.blit(num, num.get_rect(center=(c, ncy)))


def _flat_text(canvas, text, cx, cy, ss, *, size, fill, edge, edge_w,
               shadow_a=120, letter_spacing=1.0):
    """A straight bold wordmark: drop shadow, ONE thick outline ring, fill stamped
    last so counters stay open. `letter_spacing` > 1 opens the tracking. A single
    solid fill (no per-letter outline, which smears at the popup downscale)."""
    f = hud._font(int(size * ss), True)
    surfs = [f.render(g, True, fill) for g in text]
    advances = [s.get_width() * letter_spacing for s in surfs]
    total = sum(advances)
    o = edge_w * ss
    x0 = cx - total / 2
    x = x0
    for g, adv in zip(text, advances):
        sh = f.render(g, True, (0, 0, 0))
        sh.set_alpha(shadow_a)
        canvas.blit(sh, sh.get_rect(center=(int(x + adv / 2 + 2 * ss), int(cy + 3 * ss))))
        x += adv
    for da in range(0, 360, 30):
        ox, oy = math.cos(math.radians(da)) * o, math.sin(math.radians(da)) * o
        x = x0
        for g, adv in zip(text, advances):
            eg = f.render(g, True, edge)
            canvas.blit(eg, eg.get_rect(center=(int(x + adv / 2 + ox), int(cy + oy))))
            x += adv
    x = x0
    for s, adv in zip(surfs, advances):
        canvas.blit(s, s.get_rect(center=(int(x + adv / 2), int(cy))))
        x += adv


def _chrome_vgrad(canvas, rect, rr, ss):
    """Fill a rounded-rect with a top-down light->mid periwinkle vertical gradient so
    the plate reads as the same brushed icy metal as the rim, masked to the round
    rect so it only paints inside the plate."""
    top, bot = GH_METAL_HI, _shade_c(GH_METAL, -22)
    grad = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        grad.fill((int(top[0] + (bot[0] - top[0]) * t),
                   int(top[1] + (bot[1] - top[1]) * t),
                   int(top[2] + (bot[2] - top[2]) * t)),
                  pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rr)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(grad, rect.topleft)


def _ghost_nameplate(canvas, cx, cy, R, ss):
    """The GHOST flavour label as an icy-chrome nameplate INSET into the lower wheel
    face (design loop winner "V5-A"): a top-down periwinkle chrome gradient matching
    the rim, a top catch-light, and a deep-navy keyline frame, with GHOST in deep navy
    at open tracking ~half the number height — the rolled number stays the hero, this
    just names the result. (Drop shadows are intentionally off here.)"""
    w, h = int(R * 1.52), int(30 * ss)
    rect = pygame.Rect(int(cx - w / 2), int(cy - h / 2), w, h)
    rr = int(9 * ss)
    # Single thin deep-navy keyline (a filled frame behind the chrome fill), then
    # the chrome gradient + top catch-light. No second edge stroke — one hairline.
    pygame.draw.rect(canvas, GH_INDIGO_DK, rect.inflate(int(2 * ss), int(2 * ss)),
                     border_radius=rr + int(1 * ss))
    _chrome_vgrad(canvas, rect, rr, ss)
    pygame.draw.line(canvas, GH_METAL_HI, (rect.x + rr, rect.y + max(1, int(ss))),
                     (rect.right - rr, rect.y + max(1, int(ss))), max(1, int(ss)))
    _flat_text(canvas, "GHOST", cx, cy - int(ss), ss, size=18,
               fill=GH_INDIGO_DK, edge=GH_CREAM, edge_w=2, shadow_a=0,
               letter_spacing=1.12)


def _jester_bauble(canvas, cx, hy, hr, ss):
    """The staff's mini-clown bauble head: a 4-point bell-tipped jester CAP, the
    lime belled RUFF, and the grinning FACE. Cap offsets are authored for
    hr = 13*ss, so they scale by u = hr / (13*ss)."""
    u = hr / (13.0 * ss)
    base_y = hy - hr + int(1 * ss)
    span = max(2, int(8 * ss * u))
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp = cx + int(dx * ss * u)
        byp = base_y + int(dy * ss * u)
        tri = [(cx - span, base_y + int(2 * ss)),
               (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(canvas, col, tri)
        pygame.draw.polygon(canvas, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)),
                             (cx, base_y + int(2 * ss)), (bxp, byp)])
        pygame.draw.polygon(canvas, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        br = max(2, int(3.4 * ss * u))
        pygame.draw.circle(canvas, GOLD, (int(bxp), int(byp)), br)
        pygame.draw.circle(canvas, GOLD_DK, (int(bxp), int(byp)), br, max(1, int(ss)))
    _marotte_ruff(canvas, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME, lobes=9)
    _mini_clown_face(canvas, cx, hy, hr, ss, expr="grin")


def render(roll, ghost=False, ss=4, b_hr_ss=28):
    """Render design E into a `DW*ss x DH*ss` SRCALPHA surface. Returns
    (surface, DW, DH); the caller downscales to true size + pop-scales it.
    `b_hr_ss` is the clown-bauble head radius (ss-px) — the face/topper size."""
    hdw, hdh = DW * ss, DH * ss
    cx = hdw // 2
    canvas = pygame.Surface((hdw, hdh), pygame.SRCALPHA)

    R = int(hdw * 0.27)
    wcy = int(hdh * 0.60)
    # The ghost roll re-skins the ENTIRE medallion into the spectral palette — wheel,
    # rim, studs, hub, number, label and the crowning bauble — not just the wedges.
    if ghost:
        a_col, b_col = WHEEL_A_G, WHEEL_B_G
        metal, metal_hi = GH_METAL, GH_METAL_HI
        ring, disc, spoke = GH_INDIGO, GH_CREAM, GH_INDIGO_DK
    else:
        a_col, b_col = WHEEL_A, WHEEL_B
        metal, metal_hi = GOLD, GOLD_HI
        ring, disc, spoke = PLUM, CREAM, PLUM_DK
    _wheel(canvas, cx, R, ss, 8, a_col, b_col, spin=0.42, rim=metal, rim_w=7, cy=wcy,
           hi=metal_hi, spoke=spoke)
    # three side/bottom cardinal studs; the TOP one is replaced by the bauble.
    for i in range(1, 4):
        a = i * math.tau / 4 - math.pi / 2
        sx = cx + math.cos(a) * (R + int(2 * ss))
        sy = wcy + math.sin(a) * (R + int(2 * ss))
        _gold_stud(canvas, sx, sy, int(11 * ss), ss, col=metal, hi=metal_hi)
    # hub + hero number, scaled to the wheel.
    hub_r = int(R * 0.62)
    pygame.draw.circle(canvas, ring, (cx, wcy), hub_r + int(4 * ss))
    pygame.draw.circle(canvas, metal, (cx, wcy), hub_r + int(4 * ss), max(2, int(2 * ss)))
    pygame.draw.circle(canvas, disc, (cx, wcy), hub_r)
    pygame.draw.circle(canvas, ring, (cx, wcy), hub_r, max(2, int(2 * ss)))
    num_size = max(46, int(96 * R / int(hdw * 0.40)))
    # On a ghost roll the number is pulled UP and shrunk a touch so it clears the
    # GHOST nameplate inset into the lower wheel face (both live on the hub).
    num_cy = wcy - int(R * 0.11) if ghost else wcy
    _num_block(canvas, cx, num_cy, roll, ss,
               size=int(num_size * 0.9) if ghost else num_size,
               num_col=ring, edge_col=disc, edge_w=4)
    # the full clown bauble crowns the top, seated so the face touches the rim. For a
    # ghost roll it is rendered to its own layer and washed into the spectral palette
    # (its face/cap colours are baked into the shared marotte helpers).
    b_hr = int(b_hr_ss * ss)
    b_hy = (wcy - R) - int(0.95 * b_hr)
    if ghost:
        blayer = pygame.Surface((hdw, hdh), pygame.SRCALPHA)
        _jester_bauble(blayer, cx, b_hy, b_hr, ss)
        _ghostify(blayer)
        canvas.blit(blayer, (0, 0))
        # GHOST nameplate inset into the lower wheel face (design-loop winner V5-A).
        _ghost_nameplate(canvas, cx, wcy + int(R * 0.62), R, ss)
    else:
        _jester_bauble(canvas, cx, b_hy, b_hr, ss)
    return canvas, DW, DH
