"""Promenade DAY-CAST — three variety pools that fill the daytime market street.

KIDS (6), temple ELDERS (6), market VENDORS/WORKERS (7), each a variety set over
ONE shared drawer, registered as foreground_variants 'kid'/'elder'/'vendor' rows.
Replaces the single fixed draw_kids / draw_old_man / vendor templates. Sibling to
the adult-pedestrian pool (game/ped_cast.py) — same model: silhouette-distinct
archetypes (here pose/stance + age/build) × palette role-sets × pose/accessory/
attrs flags. Art-director SHIP-READY (docs/sidewalk_overhaul/day_cast/round_2.png).

Variety lives in the OUTLINE (pose/stance/build/height) because the tiny on-screen
size kills colour and interior detail first; hot accent props (balloons, candy,
the vendor price-board) are desaturated (_knock) and luma-capped (_cap_luma) so
none can rival the gold coin. Authored feet-on-base_y; drawn crisp. Night cooling
via ped_cast._retint_person (toward (54,64,96), nothing self-lit, ≤150 luma).
Pure-Pygame / pygbag-safe.
"""
from __future__ import annotations

import math

import pygame

from game.foreground_props import _mix, _shade, _clamp
from game.ped_cast import _retint_person as _retint, SKIN_TONES as SKIN
from game import foreground_variants as fv


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _cap_luma(col, cap=150.0):
    """Hold a colour at/under the night-glow ceiling so no prop rivals the coin."""
    g = _luma(col)
    if g <= cap:
        return col
    return _clamp((col[0] * cap / g, col[1] * cap / g, col[2] * cap / g))


def _knock(col, amount=0.18):
    """Desaturate + darken a hot accent so it reads as a warm accent, not a beacon."""
    g = _luma(col)
    desat = _mix(col, (g, g, g), amount * 0.7)
    return _shade(desat, -int(255 * amount * 0.55))


# ── KIDS — smallest figures (~9-13px), chibi big-head/stubby-body ─────────────
KID_H = 13


def draw_kid(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _retint(c, night)
    skin = pf(SKIN.get(P.get("skin", "warm"), SKIN["warm"]))
    skin_sh = _shade(skin, -26)
    shirt = pf(P["shirt"]); shirt_dk = pf(P.get("shirt_dk", _shade(P["shirt"], -42)))
    pants = pf(P.get("pants", _shade(shirt, -60)))
    hair = pf(P.get("hair", (60, 44, 34)))

    age = A.get("age", 0.6)
    height = 0.62 + 0.38 * age
    total = max(7, int(KID_H * height))
    squat = "squat" in v.pose
    run = "run" in v.pose
    chase = "chase" in v.pose
    carried = "carried" in v.pose
    head_bias = 0.10 if squat else 0.0
    head_r = max(2, int(total * (0.34 + head_bias - 0.06 * age)))
    body_h = max(3, int(total * 0.32))
    body_w = max(3, int(total * 0.30))
    ground = int(base_y)
    body_bot = ground - max(2, int(total * 0.30))
    body_y = body_bot - body_h
    hx = cx
    hy = body_y - head_r + 1

    gait = math.sin(t * (2.6 if (run or chase) else 1.7))

    if carried:
        body_y = ground - int(total * 1.4)
        body_bot = body_y + body_h
        hy = body_y - head_r + 1
        ad = pf(P.get("carrier", (96, 84, 110)))
        ad_dk = _shade(ad, -40)
        a_w = max(4, int(KID_H * 0.46))
        pygame.draw.polygon(surf, ad, [
            (cx - a_w, ground), (cx + a_w, ground),
            (cx + a_w - 1, ground - int(KID_H * 0.9)),
            (cx - a_w + 2, ground - KID_H)])
        pygame.draw.circle(surf, pf(SKIN["tan"]), (cx - 1, ground - KID_H - 2), 3)
        pygame.draw.circle(surf, ad_dk, (cx - 1, ground - KID_H - 3), 3, 1)

    chase_dx = 0
    if squat:
        body_y = ground - body_h - 1
        body_bot = body_y + body_h
        hy = body_y - head_r + 1
        pygame.draw.ellipse(surf, shirt, (cx - body_w, body_y, body_w * 2, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (cx - body_w, body_y, body_w * 2, body_h + 1), 1)
        for sgn in (-1, 1):
            pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.5, body_bot),
                             (cx + sgn * body_w * 1.1, ground), 2)
    elif chase:
        chase_dx = -int(body_w * 0.9)
        body_y = body_y + int(body_h * 0.35)
        body_bot = body_y + body_h
        torso = pygame.Rect(cx + chase_dx - body_w, body_y, int(body_w * 2.4), body_h)
        pygame.draw.ellipse(surf, shirt, torso)
        pygame.draw.ellipse(surf, shirt_dk, torso, 1)
        hy = body_y - head_r + 1
        stride = abs(gait) * body_w * 1.2 + body_w * 0.6
        pygame.draw.line(surf, pants, (cx + chase_dx, body_bot),
                         (cx + chase_dx - stride, ground), 2)
        pygame.draw.line(surf, pants, (cx + chase_dx + body_w * 0.4, body_bot),
                         (cx + chase_dx + stride * 0.7, ground), 2)
    else:
        pygame.draw.ellipse(surf, shirt, (cx - body_w, body_y, body_w * 2, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (cx - body_w, body_y, body_w * 2, body_h + 1), 1)
        if not carried:
            swing = gait * body_w * (0.8 if run else 0.4)
            for sgn, sw in ((-1, swing), (1, -swing)):
                fx = cx + sgn * body_w * 0.4 + sw
                pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.4, body_bot), (fx, ground), 2)
        else:
            for sgn in (-1, 1):
                pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.5, body_bot),
                                 (cx + sgn * body_w * 1.0, body_bot + 4), 2)

    if chase:
        hx = cx + chase_dx - int(body_w * 1.0)
        hy = body_y - head_r // 2
    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (cx + chase_dx, body_y + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (38, 26, 20), (hx - head_r // 2, hy), max(1, head_r // 4))

    hairstyle = P.get("hair_style", "bowl")
    if hairstyle == "buns":
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(10), math.radians(170), max(1, head_r // 2))
        for sgn in (-1, 1):
            pygame.draw.circle(surf, hair, (hx + sgn * (head_r + 1), hy - head_r // 2), max(1, head_r // 2))
    elif hairstyle == "tuft":
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(20), math.radians(160), max(1, head_r // 2))
        pygame.draw.circle(surf, hair, (hx, hy - head_r), max(1, head_r // 3))
    elif hairstyle == "cap":
        cap = pf(P.get("cap", (210, 90, 80)))
        pygame.draw.circle(surf, cap, (hx, hy - head_r // 3), int(head_r * 1.05))
        pygame.draw.circle(surf, skin, (hx + head_r // 3, hy + head_r // 4), int(head_r * 0.7))
    else:
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), max(1, head_r // 2))

    arm_y = body_y + 1 if not chase else body_y + body_h // 2
    bx = cx + chase_dx
    if chase:
        pygame.draw.line(surf, skin, (bx, arm_y), (bx - body_w * 1.6, arm_y + body_h * 0.3), 2)
    if "point" in v.pose:
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y),
                         (cx - body_w * 1.7, arm_y - body_h * 0.3), 2)
    if "balloon" in v.accessory:
        bcol = _cap_luma(pf(_knock(P.get("prop", (228, 84, 92)))))
        sx2 = cx + body_w + 2
        pygame.draw.line(surf, (70, 64, 60), (cx + body_w * 0.3, arm_y), (sx2, hy - head_r * 3), 1)
        pygame.draw.circle(surf, bcol, (sx2, hy - head_r * 3 - 2), max(2, int(head_r * 1.2)))
        pygame.draw.circle(surf, _shade(bcol, 24), (sx2 - 1, hy - head_r * 3 - 3), max(1, head_r // 2))
    if "kite" in v.accessory:
        kcol = _cap_luma(pf(_knock(P.get("prop", (240, 196, 70)))))
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.3, arm_y - 2), 2)
        kx, ky = cx + body_w + 4, hy - head_r * 3
        tail = _cap_luma(pf(_knock(P.get("tail", (224, 150, 70)))))
        pygame.draw.line(surf, tail, (cx - body_w * 1.3, arm_y - 2), (kx, ky), 1)
        pygame.draw.polygon(surf, kcol, [(kx, ky - 3), (kx + 3, ky), (kx, ky + 3), (kx - 3, ky)])
        pygame.draw.polygon(surf, _shade(kcol, -34), [(kx, ky - 3), (kx + 3, ky), (kx, ky + 3), (kx - 3, ky)], 1)
    if "stick" in v.accessory:
        scol = pf(P.get("prop", (150, 110, 64)))
        if chase:
            pygame.draw.line(surf, scol, (bx + body_w * 0.4, arm_y), (bx + body_w * 1.8, arm_y - body_h * 0.2), 2)
        else:
            pygame.draw.line(surf, scol, (cx - body_w * 0.4, arm_y), (cx - body_w * 2.4, arm_y - body_h * 0.6), 2)
    if "hoop" in v.accessory:
        hcol = pf(P.get("prop", (150, 110, 64)))
        ring = pygame.Rect(int(bx - body_w * 2.6), int(ground - body_w * 1.6),
                           int(body_w * 1.5), int(body_w * 1.5))
        pygame.draw.ellipse(surf, hcol, ring, 1)
        pygame.draw.line(surf, hcol, (bx, arm_y), (ring.centerx + 1, ring.centery), 1)
    if "candy" in v.accessory:
        ccol = _cap_luma(pf(_knock(P.get("prop", (224, 60, 60)))))
        sx2 = cx - body_w * 0.4
        pygame.draw.line(surf, (150, 120, 70), (sx2, arm_y), (sx2 - 1, hy - head_r * 2), 1)
        for k in range(3):
            pygame.draw.circle(surf, ccol, (int(sx2 - 1), int(hy - head_r * 2 + k * 3)), 2)


# ── ELDERS — robe/padded body, outline built from stance + accessory (~16-18px) ─
ELDER_H = 17


def draw_elder(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _retint(c, night)
    skin = pf(SKIN.get(P.get("skin", "warm"), SKIN["warm"]))
    skin_sh = _shade(skin, -28)
    robe = pf(P["robe"]); robe_dk = pf(P.get("robe_dk", _shade(P["robe"], -42)))
    sash = pf(P.get("sash", _shade(robe, 26)))
    grey = pf(P.get("hair", (210, 208, 200)))
    padded = A.get("padded", False)

    build = A.get("build", 1.0)
    stoop = A.get("stoop", 0.0)
    stance = A.get("stance", "upright")

    total = max(10, int(ELDER_H * A.get("height", 1.0)))
    head_r = max(2, int(total * 0.15))
    torso_h = int(total * 0.42)
    leg_h = max(2, total - torso_h - head_r * 2)
    body_w = max(3, int(total * 0.27 * build))
    ground = int(base_y)
    lean = int(body_w * 1.7 * stoop)

    seated = stance == "seated"
    taichi = stance == "taichi"
    hands_back = stance == "hands_back"
    birds = stance == "birds"

    if seated:
        stool = pf((120, 92, 60))
        sy = ground - leg_h
        pygame.draw.rect(surf, stool, (cx - body_w, sy, body_w * 2, leg_h))
        pygame.draw.rect(surf, _shade(stool, -28), (cx - body_w, sy, body_w * 2, leg_h), 1)
        torso_bot = sy
        torso_top = torso_bot - torso_h
        for sgn in (-1, 1):
            pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.5, torso_bot),
                             (cx + sgn * body_w * 1.2, ground), max(2, body_w // 3))
    else:
        torso_bot = ground - leg_h
        torso_top = torso_bot - torso_h
        if taichi:
            for sgn in (-1, 1):
                pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.4, torso_bot),
                                 (cx + sgn * body_w * 1.5, ground), max(2, body_w // 3))
        else:
            for sgn in (-1, 1):
                pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.3, torso_bot),
                                 (cx + sgn * body_w * 0.3, ground), max(2, body_w // 3))

    torso_top += int(torso_h * 0.5 * stoop)
    head_cy = torso_top - head_r
    hx = cx + lean
    hy = head_cy

    if padded:
        pad = int(body_w * 1.3)
        r = pygame.Rect(cx - pad + lean, torso_top - head_r // 2, pad * 2, (torso_bot - torso_top) + head_r // 2)
        pygame.draw.rect(surf, robe, r, border_radius=max(2, body_w // 5))
        pygame.draw.rect(surf, robe_dk, r, max(2, body_w // 6), border_radius=max(2, body_w // 5))
        fur = pf(P.get("fur", (224, 216, 202)))
        pygame.draw.line(surf, fur, (r.left, r.top), (r.right, r.top), max(2, body_w // 4))
    else:
        sh_w = int(body_w * 0.72); hem_w = int(body_w * (1.4 if not taichi else 1.55))
        bot = ground if not seated else torso_bot
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, bot), (cx - hem_w, bot)]
        pygame.draw.polygon(surf, robe, pts)
        pygame.draw.polygon(surf, robe_dk, pts, max(1, body_w // 8))
        sy = torso_top + (torso_bot - torso_top) // 2
        pygame.draw.line(surf, sash, (cx - body_w + lean, sy), (cx + body_w + lean, sy), max(2, body_w // 5))
        if stoop > 0.25:
            pygame.draw.circle(surf, robe_dk, (cx - sh_w + lean + 1, torso_top + 1), max(1, body_w // 4))

    arm_y = torso_top + head_r // 2

    if taichi:
        pygame.draw.line(surf, robe, (cx + lean, arm_y), (cx - body_w * 1.6, arm_y + torso_h * 0.3), max(2, body_w // 4))
        pygame.draw.line(surf, robe, (cx + lean, arm_y + head_r), (cx - body_w * 1.4, arm_y + torso_h * 0.7), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx - body_w * 1.6), int(arm_y + torso_h * 0.3)), max(1, body_w // 4))
    elif hands_back:
        pygame.draw.line(surf, robe, (cx + body_w * 0.6 + lean, arm_y),
                         (cx + body_w * 1.5 + lean, arm_y + torso_h * 0.5), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx + body_w * 1.5 + lean), int(arm_y + torso_h * 0.5)), max(1, body_w // 4))
    elif birds:
        pygame.draw.line(surf, robe, (cx - body_w * 0.4 + lean, arm_y),
                         (cx - body_w * 1.8, arm_y + torso_h * 0.4), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx - body_w * 1.8), int(arm_y + torso_h * 0.4)), max(1, body_w // 4))
        for bx2, by2 in ((cx - body_w * 2.2, ground - 1), (cx - body_w * 1.4, ground)):
            pygame.draw.circle(surf, pf((90, 80, 70)), (int(bx2), int(by2)), 1)

    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (40, 28, 22), (hx - head_r // 2, hy - head_r // 6), max(1, head_r // 4))
    if "beard" in v.accessory:
        pygame.draw.polygon(surf, grey, [
            (hx - head_r * 0.6, hy + head_r * 0.3), (hx + head_r * 0.6, hy + head_r * 0.3),
            (hx + head_r * 0.2, hy + head_r * 2.0), (hx - head_r * 0.2, hy + head_r * 2.0)])
        pygame.draw.circle(surf, _shade(grey, -28), (hx, hy + int(head_r * 1.6)), 1)

    head = P.get("head", "bald")
    if head == "bald":
        pygame.draw.arc(surf, grey, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(190), math.radians(350), max(1, head_r // 2))
    elif head == "bun":
        pygame.draw.circle(surf, grey, (hx, hy - head_r // 2), head_r)
        pygame.draw.circle(surf, _shade(grey, -22), (hx, hy - head_r), max(2, head_r // 2))
    elif head == "cap":
        col = pf(P.get("cap", (120, 96, 70)))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(surf, skin, (hx, hy + head_r // 4), int(head_r * 0.75))

    if "cane" in v.accessory:
        cane = pf(P.get("cane", (118, 82, 50)))
        tap = int(math.sin(t * 1.3))
        chx = cx + body_w * 1.4 + lean
        pygame.draw.line(surf, cane, (chx, arm_y), (chx + tap, ground), max(2, body_w // 6))
        pygame.draw.line(surf, cane, (chx, arm_y), (chx - 3, arm_y), max(2, body_w // 6))
        pygame.draw.line(surf, robe, (cx + body_w * 0.5 + lean, arm_y), (chx, arm_y), max(2, body_w // 5))
    if "fan" in v.accessory:
        fcol = pf(P.get("fan", (224, 212, 190)))
        fx = cx - body_w * 1.5 + lean; fy = arm_y - 1
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (fx, fy), max(2, body_w // 5))
        pygame.draw.polygon(surf, fcol, [(fx, fy), (fx - 4, fy - 4), (fx - 5, fy + 1), (fx - 3, fy + 4)])
        pygame.draw.polygon(surf, _shade(fcol, -40), [(fx, fy), (fx - 4, fy - 4), (fx - 5, fy + 1), (fx - 3, fy + 4)], 1)
    if "birdcage" in v.accessory:
        cage = pf(P.get("cage", (150, 116, 70)))
        cgx = cx + body_w * 1.6 + lean
        pygame.draw.line(surf, robe, (cx + body_w * 0.5 + lean, arm_y), (cgx, arm_y + 1), max(2, body_w // 5))
        cg = pygame.Rect(cgx - 3, arm_y + 2, 7, 9)
        pygame.draw.arc(surf, cage, (cg.left, cg.top - 3, cg.width, 6), math.radians(0), math.radians(180), 1)
        pygame.draw.ellipse(surf, _mix(cage, (40, 35, 30), 0.4), cg)
        for gx in range(cg.left + 1, cg.right, 2):
            pygame.draw.line(surf, cage, (gx, cg.top + 1), (gx, cg.bottom - 1), 1)
        pygame.draw.circle(surf, pf((110, 150, 90)), (cg.centerx, cg.centery + 1), 1)
    if "teacup" in v.accessory:
        tc = pf(P.get("tea", (228, 222, 210)))
        tx = cx - body_w * 1.2 + lean; ty = arm_y + 1
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (tx, ty), max(2, body_w // 5))
        pygame.draw.ellipse(surf, tc, (tx - 2, ty - 1, 4, 3))
        pygame.draw.ellipse(surf, _shade(tc, -34), (tx - 2, ty - 1, 4, 3), 1)


# ── VENDORS — standing working cast, must read chest-up behind a counter ──────
VEND_H = 17


def draw_vendor(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _retint(c, night)
    skin = pf(SKIN.get(P.get("skin", "warm"), SKIN["warm"]))
    skin_sh = _shade(skin, -28)
    shirt = pf(P["shirt"]); shirt_dk = pf(P.get("shirt_dk", _shade(P["shirt"], -42)))
    apron = pf(P.get("apron", (206, 196, 176)))
    apron_dk = _shade(apron, -34)
    pants = pf(P.get("pants", (74, 66, 58)))
    hair = pf(P.get("hair", (54, 42, 34)))

    build = A.get("build", 1.05)
    total = max(11, int(VEND_H * A.get("height", 1.0)))
    head_r = max(2, int(total * 0.15))
    torso_h = int(total * 0.46)
    leg_h = max(2, total - torso_h - head_r * 2)
    body_w = max(3, int(total * 0.28 * build))
    ground = int(base_y)
    torso_bot = ground - leg_h
    torso_top = torso_bot - torso_h
    hx = cx; hy = torso_top - head_r
    arm_y = torso_top + head_r // 2
    pose = A.get("pose", "call")

    for sgn in (-1, 1):
        pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.4, torso_bot),
                         (cx + sgn * body_w * 0.4, ground), max(2, body_w // 3))

    heavy = build >= 1.18
    lean = build <= 0.92
    if heavy:
        r = pygame.Rect(int(cx - body_w * 0.92), torso_top, int(body_w * 1.84), torso_h)
        belly = pygame.Rect(int(cx - body_w * 1.18), torso_top + torso_h // 3,
                            int(body_w * 2.36), int(torso_h * 0.7))
        pygame.draw.ellipse(surf, shirt, belly)
        pygame.draw.rect(surf, shirt, r, border_radius=max(2, body_w // 4))
        pygame.draw.ellipse(surf, shirt_dk, belly, 1)
        pygame.draw.rect(surf, shirt_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 4))
    elif lean:
        pts = [(cx - body_w, torso_top), (cx + body_w, torso_top),
               (int(cx + body_w * 0.6), torso_bot), (int(cx - body_w * 0.6), torso_bot)]
        pygame.draw.polygon(surf, shirt, pts)
        pygame.draw.polygon(surf, shirt_dk, pts, max(1, body_w // 8))
    else:
        r = pygame.Rect(cx - body_w, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(surf, shirt, r, border_radius=max(2, body_w // 4))
        pygame.draw.rect(surf, shirt_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 4))
    apr = pygame.Rect(cx - body_w * 0.7, torso_top + head_r, body_w * 1.4, torso_h - head_r // 2)
    pygame.draw.rect(surf, apron, apr)
    pygame.draw.rect(surf, apron_dk, apr, 1)
    pygame.draw.line(surf, apron_dk, (cx - body_w * 0.5, torso_top + 1), (apr.left + 1, apr.top), 1)
    pygame.draw.line(surf, apron_dk, (cx + body_w * 0.5, torso_top + 1), (apr.right - 1, apr.top), 1)
    if "rolled" in v.accessory:
        pygame.draw.line(surf, _shade(shirt, 14), (cx - body_w * 0.6, arm_y), (cx - body_w, arm_y + 2), max(2, body_w // 3))
    if "towel" in v.accessory:
        tw = pf(P.get("towel", (220, 214, 200)))
        pygame.draw.line(surf, tw, (cx + body_w * 0.3, torso_top - 1), (cx + body_w * 0.9, torso_top + torso_h * 0.4), max(2, body_w // 4))

    if pose == "call":
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (hx - head_r, hy + head_r // 2), max(2, body_w // 4))
    elif pose == "weigh":
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.5, arm_y - 2), max(2, body_w // 4))
        sx2 = cx - body_w * 1.5
        pygame.draw.line(surf, pf((120, 96, 60)), (sx2, arm_y - 2), (sx2, arm_y - 5), 1)
        for ox in (-3, 3):
            pygame.draw.line(surf, (90, 80, 64), (sx2 + ox, arm_y - 4), (sx2 + ox, arm_y), 1)
            pygame.draw.arc(surf, pf((150, 120, 70)), (sx2 + ox - 2, arm_y - 1, 4, 3), math.radians(180), math.radians(360), 1)
    elif pose == "fan":
        fy = arm_y + int(math.sin(t * 6) * 1)
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.4, fy + 2), max(2, body_w // 4))
        pygame.draw.rect(surf, pf((200, 180, 140)), (int(cx - body_w * 1.7), int(fy), 4, 5))
        pygame.draw.rect(surf, pf((140, 110, 70)), (int(cx - body_w * 1.7), int(fy), 4, 5), 1)
    elif pose == "ladle":
        px = cx - body_w * 1.3; py = arm_y + torso_h * 0.6
        for sgn, off in ((-1, 0.0), (1, 0.4)):
            pygame.draw.line(surf, shirt, (cx + sgn * body_w * 0.5, arm_y), (px + off * body_w, py), max(2, body_w // 4))
        pygame.draw.line(surf, pf((150, 120, 70)), (px, py), (px - 2, py + torso_h * 0.4), 1)
        pygame.draw.circle(surf, pf((180, 150, 100)), (int(px - 2), int(py + torso_h * 0.4)), 1)
        pot = pygame.Rect(int(px - body_w * 0.7), int(py + torso_h * 0.3), int(body_w * 1.4), 3)
        pygame.draw.ellipse(surf, pf((110, 92, 70)), pot)
        pygame.draw.ellipse(surf, _shade(pf((110, 92, 70)), -28), pot, 1)
    elif pose == "stack":
        for sgn in (-1, 1):
            pygame.draw.line(surf, shirt, (cx + sgn * body_w * 0.5, arm_y), (cx + sgn * body_w * 0.9, hy), max(2, body_w // 4))
        bk = pf(P.get("basket", (176, 132, 78)))
        for k in range(3):
            br = pygame.Rect(int(cx - body_w * 0.9), int(hy - head_r * 1.3 - k * 4), int(body_w * 1.8), 4)
            pygame.draw.ellipse(surf, bk, br)
            pygame.draw.ellipse(surf, _shade(bk, -30), br, 1)
    elif pose == "sign":
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.2, arm_y - 1), max(2, body_w // 4))
        if "skewers" in v.accessory:
            for k in range(4):
                pygame.draw.line(surf, pf((150, 120, 70)), (cx - body_w * 1.2 + k, arm_y - 1),
                                 (cx - body_w * 1.6 + k, arm_y - head_r * 2), 1)
                pygame.draw.circle(surf, pf((180, 90, 60)), (int(cx - body_w * 1.6 + k), int(arm_y - head_r * 2)), 1)
        else:
            sg = _cap_luma(pf(_knock(P.get("sign", (168, 78, 70)))))
            sg_hi = _cap_luma(_shade(sg, 26))
            pygame.draw.line(surf, pf((120, 90, 60)), (cx - body_w * 1.2, arm_y - 1), (cx - body_w * 1.2, hy - head_r * 2), 1)
            sr = pygame.Rect(int(cx - body_w * 1.9), int(hy - head_r * 2.6), int(body_w * 1.6), int(head_r * 1.8))
            pygame.draw.rect(surf, sg, sr)
            pygame.draw.rect(surf, _shade(sg, -34), sr, 1)
            pygame.draw.line(surf, sg_hi, (sr.left + 1, sr.centery), (sr.right - 1, sr.centery), 1)

    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (40, 28, 22), (hx - head_r // 2, hy - head_r // 6), max(1, head_r // 4))

    hat = P.get("hat", "none")
    if hat == "conical":
        col = pf(P.get("hat_c", (198, 162, 96))); bw = int(head_r * 2.4)
        pygame.draw.polygon(surf, col, [(hx - bw, hy - head_r * 0.1), (hx, hy - head_r * 1.9), (hx + bw, hy - head_r * 0.1)])
        pygame.draw.polygon(surf, _shade(col, -34), [(hx - bw, hy - head_r * 0.1), (hx, hy - head_r * 1.9), (hx + bw, hy - head_r * 0.1)], 1)
    elif hat == "cloth":
        col = pf(P.get("hat_c", (180, 88, 78)))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(surf, skin, (hx, hy + head_r // 4), int(head_r * 0.72))
    elif hat == "cap":
        col = pf(P.get("hat_c", (120, 100, 76)))
        cap = pygame.Rect(hx - head_r, hy - int(head_r * 1.5), head_r * 2, int(head_r * 1.3))
        pygame.draw.ellipse(surf, col, cap)
        pygame.draw.line(surf, _shade(col, -24), (hx - head_r, hy - head_r // 2), (hx - head_r - 2, hy - head_r // 3), 2)
    elif hat == "wrap":
        col = pf(P.get("hat_c", (150, 110, 96)))
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        band = pygame.Rect(hx - head_r, hy - head_r // 2, head_r * 2, max(2, head_r))
        pygame.draw.ellipse(surf, col, band)
        pygame.draw.circle(surf, _shade(col, -22), (hx + head_r, hy - head_r // 3), max(1, head_r // 2))
    else:
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), int(head_r * 0.95))
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), max(1, head_r // 3))


# ── pools → foreground_variants rows ──────────────────────────────────────────
_B = fv
_BW_KID = {_B.BEAT_MARKET: 1.4, _B.BEAT_MORNING: 1.0, _B.BEAT_GOLDEN: 1.1,
           _B.BEAT_DUSK: 0.9, _B.BEAT_FESTIVAL: 1.6, _B.BEAT_PREDAWN: 0.2}
_BW_ELDER = {_B.BEAT_MARKET: 0.8, _B.BEAT_MORNING: 1.1, _B.BEAT_GOLDEN: 1.5,
             _B.BEAT_DUSK: 1.4, _B.BEAT_FESTIVAL: 1.0, _B.BEAT_PREDAWN: 0.5}
_BW_VENDOR = {_B.BEAT_MARKET: 2.4, _B.BEAT_MORNING: 1.8, _B.BEAT_GOLDEN: 1.0,
              _B.BEAT_DUSK: 0.8, _B.BEAT_FESTIVAL: 0.9, _B.BEAT_PREDAWN: 0.3}


def _V(palette, *, pose=(), acc=(), attrs=None, bw=None):
    return fv.Variant(palette=palette, pose=frozenset(pose), accessory=frozenset(acc),
                      attrs=dict(attrs or {}), beat_weights=dict(bw or {}))


def _build_kids():
    return [
        _V(dict(shirt=(235, 95, 90), pants=(74, 60, 52), hair=(58, 44, 36), hair_style="tuft", skin="warm"),
           pose=("run",), attrs=dict(age=0.05), bw=_BW_KID),
        _V(dict(shirt=(90, 165, 220), pants=(58, 52, 56), hair=(46, 36, 30), hair_style="bowl", skin="fair", prop=(150, 110, 64)),
           pose=("chase",), acc=("hoop", "stick"), attrs=dict(age=0.9), bw=_BW_KID),
        _V(dict(shirt=(250, 200, 70), pants=(70, 56, 48), hair=(40, 32, 28), hair_style="bowl", skin="tan"),
           pose=("squat",), attrs=dict(age=0.55), bw=_BW_KID),
        _V(dict(shirt=(120, 200, 130), pants=(64, 58, 50), hair=(50, 40, 32), hair_style="buns", skin="warm", prop=(228, 84, 92)),
           pose=("point",), acc=("balloon",), attrs=dict(age=0.7), bw=_BW_KID),
        _V(dict(shirt=(220, 130, 200), pants=(70, 56, 60), hair=(44, 34, 28), hair_style="cap", skin="ruddy", cap=(210, 90, 80), prop=(224, 60, 60)),
           acc=("candy",), attrs=dict(age=0.45), bw=_BW_KID),
        _V(dict(shirt=(110, 130, 235), pants=(60, 54, 58), hair=(54, 42, 34), hair_style="bowl", skin="warm", carrier=(96, 84, 110)),
           pose=("carried",), attrs=dict(age=0.2), bw=_BW_KID),
    ]


def _build_elders():
    return [
        _V(dict(robe=(92, 72, 108), robe_dk=(58, 44, 74), sash=(196, 180, 150), hair=(212, 210, 202), skin="fair", head="bald", cane=(118, 82, 50)),
           acc=("beard", "cane"), attrs=dict(stance="stoop", stoop=0.46, height=0.92, build=0.95), bw=_BW_ELDER),
        _V(dict(robe=(86, 96, 140), robe_dk=(52, 60, 100), sash=(200, 188, 150), hair=(208, 206, 198), skin="warm", head="bun"),
           acc=("fan", "beard"), attrs=dict(stance="taichi", height=1.04, build=1.0, fan=(224, 212, 190)), bw=_BW_ELDER),
        _V(dict(robe=(110, 134, 112), robe_dk=(70, 92, 76), sash=(206, 180, 140), hair=(204, 202, 196), skin="tan", head="cap", cap=(120, 96, 70)),
           acc=("birdcage",), attrs=dict(stance="upright", height=1.0, build=1.05, cage=(150, 116, 70)), bw=_BW_ELDER),
        _V(dict(robe=(128, 124, 112), robe_dk=(84, 82, 72), sash=(186, 188, 196), hair=(210, 208, 200), skin="warm", head="bald"),
           acc=("beard",), attrs=dict(stance="hands_back", stoop=0.18, height=1.02, build=0.98), bw=_BW_ELDER),
        _V(dict(robe=(118, 96, 84), robe_dk=(74, 58, 50), fur=(224, 216, 202), sash=(196, 170, 130), hair=(206, 204, 196), skin="ruddy", head="cap", cap=(110, 90, 66)),
           acc=("teacup", "beard"), attrs=dict(stance="seated", height=0.94, build=1.15, padded=True, tea=(228, 222, 210)), bw=_BW_ELDER),
        _V(dict(robe=(104, 80, 116), robe_dk=(66, 48, 78), sash=(208, 160, 140), hair=(206, 204, 198), skin="deep", head="bun"),
           attrs=dict(stance="birds", height=0.98, build=1.0), bw=_BW_ELDER),
    ]


def _build_vendors():
    return [
        _V(dict(shirt=(150, 86, 70), shirt_dk=(104, 56, 46), apron=(214, 200, 178), pants=(70, 60, 52), hair=(46, 36, 30), skin="tan", hat="conical", hat_c=(196, 158, 92)),
           acc=("rolled", "towel"), attrs=dict(pose="call", height=1.0, build=1.08), bw=_BW_VENDOR),
        _V(dict(shirt=(78, 124, 124), shirt_dk=(48, 84, 84), apron=(206, 196, 176), pants=(66, 58, 50), hair=(40, 32, 28), skin="warm", hat="wrap", hat_c=(150, 110, 96)),
           attrs=dict(pose="weigh", height=1.12, build=0.9), bw=_BW_VENDOR),
        _V(dict(shirt=(158, 128, 78), shirt_dk=(108, 84, 50), apron=(210, 196, 172), pants=(64, 58, 48), hair=(50, 40, 32), skin="deep", hat="cap", hat_c=(120, 100, 76), towel=(220, 214, 200)),
           acc=("rolled", "towel"), attrs=dict(pose="fan", height=0.98, build=1.24), bw=_BW_VENDOR),
        _V(dict(shirt=(118, 116, 80), shirt_dk=(78, 78, 52), apron=(204, 192, 170), pants=(60, 56, 46), hair=(44, 34, 28), skin="ruddy", hat="none"),
           acc=("rolled",), attrs=dict(pose="ladle", height=1.0, build=1.06), bw=_BW_VENDOR),
        _V(dict(shirt=(100, 108, 124), shirt_dk=(64, 72, 90), apron=(200, 192, 178), pants=(58, 60, 70), hair=(54, 42, 34), skin="warm", hat="conical", hat_c=(184, 150, 88), basket=(176, 132, 78)),
           attrs=dict(pose="stack", height=1.04, build=1.0), bw=_BW_VENDOR),
        _V(dict(shirt=(168, 120, 84), shirt_dk=(114, 78, 54), apron=(208, 198, 178), pants=(70, 60, 50), hair=(40, 32, 28), skin="tan", hat="cap", hat_c=(110, 96, 74)),
           acc=("skewers",), attrs=dict(pose="sign", height=1.0, build=1.05), bw=_BW_VENDOR),
        _V(dict(shirt=(140, 104, 130), shirt_dk=(94, 66, 90), apron=(206, 194, 174), pants=(64, 56, 58), hair=(50, 40, 32), skin="fair", hat="cloth", hat_c=(150, 100, 84), sign=(168, 78, 70)),
           attrs=dict(pose="sign", height=1.0, build=1.04), bw=_BW_VENDOR),
    ]


fv.register("kid", _build_kids())
fv.register("elder", _build_elders())
fv.register("vendor", _build_vendors())
