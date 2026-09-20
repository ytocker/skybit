"""Promenade DAY-CAST — three variety pools that fill the daytime market street.

KIDS (10), temple ELDERS (10), market VENDORS/WORKERS (10), each a variety set
over ONE shared drawer, registered as foreground_variants 'kid'/'elder'/'vendor'
rows. Replaces the single fixed draw_kids / draw_old_man / vendor templates.
Sibling to the adult-pedestrian pool (game/ped_cast.py) — same model: silhouette-
distinct archetypes (here pose/stance + age/build) × palette role-sets × pose/
accessory/attrs flags.

Variety lives in the OUTLINE (pose/stance/build/height) because the tiny on-screen
size kills colour and interior detail first; hot accent props (balloons, lanterns,
the vendor price-board) are desaturated (_knock) and luma-capped (_cap_luma) so
none can rival the gold coin. Authored feet-on-base_y; drawn crisp. Night cooling
via ped_cast._retint_person (toward (54,64,96)) with every cooled colour clamped
through _cap_luma — nothing self-lit, ≤150 luma. Pure-Pygame / pygbag-safe.
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
    return (_clamp(col[0] * cap / g), _clamp(col[1] * cap / g), _clamp(col[2] * cap / g))


def _knock(col, amount=0.18):
    """Desaturate + darken a hot accent so it reads as a warm accent, not a beacon."""
    g = _luma(col)
    desat = _mix(col, (g, g, g), amount * 0.7)
    return _shade(desat, -int(255 * amount * 0.55))


# ── KIDS — smallest figures (~9-13px), chibi big-head/stubby-body ─────────────
KID_H = 13


def draw_kid(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _cap_luma(_retint(c, night)) if night > 0.05 else c
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
    tiptoe = "tiptoe" in v.pose
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
    elif tiptoe:
        # STANCE — the child stretches: body lifted off its usual seat, legs
        # dead straight with the heels off the deck and both arms thrown up over a
        # counter edge. Reads as a tall thin exclamation mark, which is the exact
        # opposite of the squat/chase rows and survives the far-lane downscale.
        stretch = 0.5 + 0.5 * math.sin(t * 1.9)
        body_y = ground - int(total * 0.46) - body_h - int(round(stretch))
        body_bot = body_y + body_h
        hy = body_y - head_r + 1
        pygame.draw.ellipse(surf, shirt, (cx - body_w + 1, body_y, body_w * 2 - 2, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (cx - body_w + 1, body_y, body_w * 2 - 2, body_h + 1), 1)
        for sgn in (-1, 1):
            lx = cx + sgn * body_w * 0.45
            pygame.draw.line(surf, pants, (lx, body_bot), (lx, ground - 1), 2)
            pygame.draw.line(surf, _shade(pants, -22), (lx - 1, ground - 1), (lx + 1, ground), 1)
        for sgn, off in ((-1, 0.12), (1, 0.0)):
            # The REACH is the animation. Truncating a 0..1 float with int() froze
            # the whole cycle at zero, so the row read as a still figure; driving
            # the fingertips off the float instead moves the top of the silhouette
            # ~2px a beat and puts the crown-to-fingertip stack above the squat
            # rows without touching the kite runner's ceiling.
            tip_y = hy - head_r * (2.15 + off + 0.70 * stretch)
            pygame.draw.line(surf, skin, (cx + sgn * body_w * 0.5, body_y + 1),
                             (cx + sgn * body_w * 0.85 - body_w * 0.35, tip_y), 2)
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
    elif hairstyle == "sidetails":
        # Two tails swinging out past the jaw, so the head silhouette widens at
        # the BOTTOM (buns widen it at the top). A cheap, readable note.
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        for sgn in (-1, 1):
            tip = (hx + sgn * (head_r + 2), hy + head_r + 1 + int(round(gait * 0.8)))
            pygame.draw.line(surf, hair, (hx + sgn * head_r, hy - head_r // 3), tip, 2)
            pygame.draw.circle(surf, _shade(hair, -20), tip, 1)
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
        pygame.draw.circle(surf, _cap_luma(_shade(bcol, 24)), (sx2 - 1, hy - head_r * 3 - 3), max(1, head_r // 2))
    if "kite" in v.accessory:
        kcol = _cap_luma(pf(_knock(P.get("prop", (240, 196, 70)))))
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.3, arm_y - 2), 2)
        kx, ky = cx + body_w + 4, hy - head_r * 3
        tail = _cap_luma(pf(_knock(P.get("tail", (224, 150, 70)))))
        # A 1px string is erased by the crisp far-lane downscale and the kite
        # detaches into a floating lozenge; 2px keeps child and kite one object.
        pygame.draw.line(surf, tail, (cx - body_w * 1.3, arm_y - 2), (kx, ky), 2)
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
    if "ribbon" in v.accessory:
        # A long wavy streamer trailing BEHIND the runner: a horizontal squiggle
        # twice the child's own width, which is a bigger outline event than any
        # held object could be at 10px.
        rc = _cap_luma(pf(_knock(P.get("prop", (216, 120, 150)))))
        hxr, hyr = cx - body_w * 1.0, arm_y - body_h * 0.5
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (hxr, hyr), 2)
        pts = []
        for k in range(6):
            px = hxr + body_w * (0.6 * k + 0.4)
            py = hyr + math.sin(t * 3.0 + k * 1.1) * (1.2 + 0.35 * k)
            pts.append((px, py))
        pygame.draw.lines(surf, rc, False, pts, 1)
    if "lantern" in v.accessory:
        # Carried FORWARD on a short stick at chest height — deliberately not an
        # overhead sphere, so it never doubles the balloon row's silhouette.
        pc = pf(P.get("stick", (140, 106, 66)))
        lc = _cap_luma(pf(_knock(P.get("prop", (214, 122, 74)))))
        hxp, hyp = cx - body_w * 1.9, arm_y - body_h * 0.7
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.1, arm_y - 1), 2)
        pygame.draw.line(surf, pc, (cx - body_w * 1.1, arm_y - 1), (hxp, hyp), 1)
        lr = pygame.Rect(int(hxp - 2), int(hyp + 1), 4, 5)
        pygame.draw.ellipse(surf, lc, lr)
        pygame.draw.ellipse(surf, _shade(lc, -40), lr, 1)
        pygame.draw.line(surf, _shade(lc, -50), (lr.left, lr.centery), (lr.right, lr.centery), 1)
    if "satchel" in v.accessory:
        sc = pf(P.get("bag", (146, 122, 86)))
        sr = pygame.Rect(int(cx + body_w * 0.5), int(body_y + body_h * 0.25),
                         int(body_w * 1.2), int(body_h * 1.0))
        pygame.draw.rect(surf, sc, sr, border_radius=1)
        pygame.draw.rect(surf, _shade(sc, -34), sr, 1, border_radius=1)
        pygame.draw.line(surf, _shade(sc, -28), (sr.left, sr.top), (cx - body_w * 0.4, body_y + 1), 1)


    # ── HELD UMBRELLA (rain rows only) ────────────────────────────────────
    # Same contract as ped_cast's: the canopy comes from the row's own
    # palette and its size is derived from THIS figure's head radius, so a
    # child's brolly scales down without a second set of numbers. Deferred
    # import because the kit imports this module.
    if "umbrella" in v.accessory:
        from game import weekend_kit as _wkit
        _ucol = pf(P.get("canopy", (236, 224, 210)))
        _ur = int(head_r * 2.5)
        _uy = hy - int(head_r * 2.7)
        _usc = max(0.5, _ur / 8.0)
        _wkit.draw_umbrella8(surf, hx, _uy, 0, night=0.0, scale=_usc,
                             pole_len=max(6, int((hy - (_uy + 1)) / _usc)),
                             wind=0.5, color=_ucol)

# ── ELDERS — robe/padded body, outline built from stance + accessory (~16-18px) ─
ELDER_H = 17


def draw_elder(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _cap_luma(_retint(c, night)) if night > 0.05 else c
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
    brush = stance == "brush"
    reading = stance == "reading"

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
        if taichi or brush:
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
        sh_w = int(body_w * 0.72); hem_w = int(body_w * (1.4 if not (taichi or brush) else 1.55))
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
    elif brush:
        # STANCE — water calligraphy. A long brush runs from the low hand all
        # the way to the DECK ahead of the figure, so the silhouette gains a
        # ground-touching diagonal no other elder has; the wet stroke it leaves
        # behind sits on the deck and dries (fades) on a slow cycle.
        bcol = pf(P.get("brush", (126, 96, 62)))
        hxb = cx - body_w * 1.4
        hyb = arm_y + torso_h * 0.45
        tip_x = cx - body_w * 2.9 + math.sin(t * 1.5) * body_w * 0.5
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (hxb, hyb), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(hxb), int(hyb)), max(1, body_w // 4))
        pygame.draw.line(surf, bcol, (hxb, hyb), (tip_x, ground - 1), max(1, body_w // 5))
        pygame.draw.circle(surf, _shade(bcol, -40), (int(tip_x), int(ground - 1)), 1)
        wet = pf(P.get("wet", (96, 88, 78)))
        for k, wx in enumerate((cx - body_w * 3.4, cx - body_w * 2.2)):
            fade = 0.4 + 0.4 * math.sin(t * 1.1 + k)
            pygame.draw.line(surf, _mix(wet, (140, 130, 112), fade),
                             (wx, ground), (wx + body_w * 0.8, ground), 1)
    elif reading:
        # STANCE — an open scroll held wide at chest height on both hands: a
        # hard horizontal bar across the body, the one elder read that widens the
        # figure instead of extending it.
        sc = _cap_luma(pf(P.get("scroll", (208, 196, 168))))
        sw2 = int(body_w * 2.1)
        sy2 = int(arm_y + torso_h * 0.26)
        for sgn in (-1, 1):
            pygame.draw.line(surf, robe, (cx + sgn * body_w * 0.5 + lean, arm_y),
                             (cx + sgn * sw2 * 0.8, sy2), max(2, body_w // 4))
        r = pygame.Rect(cx - sw2, sy2 - 1, sw2 * 2, max(4, int(torso_h * 0.38)))
        pygame.draw.rect(surf, sc, r)
        pygame.draw.rect(surf, _shade(sc, -46), r, 1)
        for k in range(2):
            pygame.draw.line(surf, _shade(sc, -60), (r.left + 2, r.top + 2 + k * 2),
                             (r.right - 2, r.top + 2 + k * 2), 1)

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
        # int() on a (-1,1) float is zero everywhere but the two extremes — the
        # tap never moved a pixel until it was rounded instead of truncated.
        tap = int(round(math.sin(t * 1.3)))
        chx = cx + body_w * 1.4 + lean
        pygame.draw.line(surf, cane, (chx, arm_y), (chx + tap, ground), max(2, body_w // 6))
        pygame.draw.line(surf, cane, (chx, arm_y), (chx - 3, arm_y), max(2, body_w // 6))
        pygame.draw.line(surf, robe, (cx + body_w * 0.5 + lean, arm_y), (chx, arm_y), max(2, body_w // 5))
    if "fan" in v.accessory:
        fcol = _cap_luma(pf(P.get("fan", (224, 212, 190))))
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
        tc = _cap_luma(pf(P.get("tea", (228, 222, 210))))
        tx = cx - body_w * 1.2 + lean; ty = arm_y + 1
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (tx, ty), max(2, body_w // 5))
        pygame.draw.ellipse(surf, tc, (tx - 2, ty - 1, 4, 3))
        pygame.draw.ellipse(surf, _shade(tc, -34), (tx - 2, ty - 1, 4, 3), 1)
    if "sword" in v.accessory:
        # A straight blade continuing the arm well past the hand: the taichi
        # stance's soft curves get one hard straight edge, which is the whole
        # difference between the two sword/empty-hand rows at 15px.
        bl = _cap_luma(pf(P.get("blade", (168, 176, 184))))
        h0 = (cx - body_w * 1.5, arm_y + torso_h * 0.2)
        tip = (cx - body_w * 3.4, arm_y - torso_h * 0.55 + math.sin(t * 1.4) * 1.5)
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), h0, max(2, body_w // 4))
        pygame.draw.line(surf, bl, h0, tip, 1)
        pygame.draw.line(surf, pf((120, 96, 60)), (h0[0] - 1, h0[1] - 1), (h0[0] + 1, h0[1] + 1), 2)
        tsl = pf(P.get("tassel", (150, 92, 88)))
        pygame.draw.line(surf, tsl, h0, (h0[0] + 2, h0[1] + 3 + math.sin(t * 2.2)), 1)
    if "back_basket" in v.accessory:
        # A tall pannier riding on the BACK — the day cast carried nothing behind
        # the body before.
        bk = pf(P.get("basket", (166, 126, 76)))
        bwid = int(body_w * 1.25)
        bh = int(torso_h * 1.15)
        br = pygame.Rect(int(cx + body_w * 0.8 + lean), int(torso_top - head_r * 0.8), bwid, bh)
        pygame.draw.polygon(surf, bk, [
            (br.left, br.bottom), (br.right - 1, br.bottom - 1),
            (br.right, br.top + 2), (br.left - 1, br.top)])
        pygame.draw.polygon(surf, _shade(bk, -34), [
            (br.left, br.bottom), (br.right - 1, br.bottom - 1),
            (br.right, br.top + 2), (br.left - 1, br.top)], 1)
        for q in (0.4, 0.75):
            yy = int(br.top + bh * q)
            pygame.draw.line(surf, _shade(bk, -26), (br.left, yy), (br.right - 1, yy), 1)
        grn = pf(P.get("herbs", (104, 128, 92)))
        for gx in (0.25, 0.6):
            pygame.draw.circle(surf, grn, (int(br.left + bwid * gx), br.top), 1)


    # ── HELD UMBRELLA (rain rows only) ────────────────────────────────────
    # Same contract as ped_cast's: the canopy comes from the row's own
    # palette and its size is derived from THIS figure's head radius, so a
    # child's brolly scales down without a second set of numbers. Deferred
    # import because the kit imports this module.
    if "umbrella" in v.accessory:
        from game import weekend_kit as _wkit
        _ucol = pf(P.get("canopy", (236, 224, 210)))
        _ur = int(head_r * 2.5)
        _uy = hy - int(head_r * 2.7)
        _usc = max(0.5, _ur / 8.0)
        _wkit.draw_umbrella8(surf, hx, _uy, 0, night=0.0, scale=_usc,
                             pole_len=max(6, int((hy - (_uy + 1)) / _usc)),
                             wind=0.5, color=_ucol)

# ── VENDORS — standing working cast, must read chest-up behind a counter ──────
VEND_H = 17


def draw_vendor(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _cap_luma(_retint(c, night)) if night > 0.05 else c
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
        tw = _cap_luma(pf(P.get("towel", (220, 214, 200))))
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
        # int() on a (-1,1) float is zero everywhere but the two extremes — this
        # flutter never moved a pixel until it was rounded instead of truncated.
        fy = arm_y + int(round(math.sin(t * 6) * 1.2))
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
    elif pose == "chop":
        # 2-beat cleaver: the arm swings from above the shoulder down to the
        # board — the most total motion in the family across a cycle.
        beat = max(0.0, math.sin(t * 5.0))
        hxc = cx - body_w * 1.35
        hyc = arm_y + torso_h * 0.30 - beat * head_r * 3.2
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (hxc, hyc), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(hxc), int(hyc)), max(1, body_w // 5))
        bl = _cap_luma(pf(P.get("blade", (176, 182, 190))))
        blade = pygame.Rect(int(hxc - body_w * 0.9), int(hyc - 1), max(3, int(body_w * 0.9)), max(2, head_r))
        pygame.draw.rect(surf, bl, blade)
        pygame.draw.rect(surf, _shade(bl, -50), blade, 1)
        board = pf(P.get("board", (146, 116, 76)))
        brd = pygame.Rect(int(cx - body_w * 2.1), int(arm_y + torso_h * 0.62), int(body_w * 1.9), 3)
        pygame.draw.rect(surf, board, brd)
        pygame.draw.rect(surf, _shade(board, -34), brd, 1)
    elif pose == "pour":
        # Long-spout pot held HIGH with a thin thread of tea falling into a cup:
        # a tall arm plus a vertical hairline, unlike any other vendor action.
        lift = math.sin(t * 2.2) * 1.5
        hxp = cx - body_w * 1.25
        hyp = hy + head_r * 0.2 + lift
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (hxp, hyp), max(2, body_w // 4))
        pot = pf(P.get("pot", (140, 118, 96)))
        pr = pygame.Rect(int(hxp - body_w * 0.6), int(hyp - 1), max(4, int(body_w * 1.1)), max(3, head_r + 1))
        pygame.draw.ellipse(surf, pot, pr)
        pygame.draw.ellipse(surf, _shade(pot, -34), pr, 1)
        spout_tip = (pr.left - body_w * 1.1, pr.centery + 1)
        pygame.draw.line(surf, pot, (pr.left + 1, pr.centery), spout_tip, 1)
        tea = _cap_luma(pf(P.get("tea", (196, 168, 120))))
        cup_y = arm_y + torso_h * 0.66
        pygame.draw.line(surf, tea, spout_tip, (spout_tip[0] - 1, cup_y), 1)
        cup = pygame.Rect(int(spout_tip[0] - 3), int(cup_y), 5, 3)
        pygame.draw.ellipse(surf, _cap_luma(pf((216, 210, 196))), cup)
        pygame.draw.ellipse(surf, (90, 84, 76), cup, 1)
    elif pose == "wok":
        # Both hands on a wide tilted pan with a tossed arc of food above it: the
        # only vendor whose outline is a WIDE ellipse held away from the body.
        toss = math.sin(t * 3.4)
        wx = cx - body_w * 1.5
        wy = arm_y + torso_h * 0.30 + toss
        for sgn, off in ((-1, 0.0), (1, 0.5)):
            pygame.draw.line(surf, shirt, (cx + sgn * body_w * 0.5, arm_y),
                             (wx + off * body_w * 1.6, wy + 1), max(2, body_w // 4))
        pan = pf(P.get("pan", (96, 88, 82)))
        pr = pygame.Rect(int(wx - body_w * 1.0), int(wy - 1), max(6, int(body_w * 2.2)), max(3, head_r + 1))
        pygame.draw.ellipse(surf, pan, pr)
        pygame.draw.ellipse(surf, _shade(pan, -30), pr, 1)
        pygame.draw.line(surf, _shade(pan, 20), (pr.right - 1, pr.centery), (pr.right + body_w * 0.8, pr.centery - 1), 1)
        food = _cap_luma(pf(_knock(P.get("food", (206, 156, 92)))))
        for k in range(3):
            fx = pr.centerx - 2 + k * 2
            fy = pr.top - 2 - abs(math.sin(t * 3.4 + k * 0.7)) * 3
            pygame.draw.circle(surf, food, (int(fx), int(fy)), 1)

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


    # ── HELD UMBRELLA (rain rows only) ────────────────────────────────────
    # Same contract as ped_cast's: the canopy comes from the row's own
    # palette and its size is derived from THIS figure's head radius, so a
    # child's brolly scales down without a second set of numbers. Deferred
    # import because the kit imports this module.
    if "umbrella" in v.accessory:
        from game import weekend_kit as _wkit
        _ucol = pf(P.get("canopy", (236, 224, 210)))
        _ur = int(head_r * 2.5)
        _uy = hy - int(head_r * 2.7)
        _usc = max(0.5, _ur / 8.0)
        _wkit.draw_umbrella8(surf, hx, _uy, 0, night=0.0, scale=_usc,
                             pole_len=max(6, int((hy - (_uy + 1)) / _usc)),
                             wind=0.5, color=_ucol)

# ── pools → foreground_variants rows ──────────────────────────────────────────
_B = fv
_BW_KID = {_B.BEAT_MARKET: 1.4, _B.BEAT_MORNING: 1.0, _B.BEAT_GOLDEN: 1.1,
           _B.BEAT_DUSK: 0.9, _B.BEAT_FESTIVAL: 1.6, _B.BEAT_PREDAWN: 0.2}
_BW_ELDER = {_B.BEAT_MARKET: 0.8, _B.BEAT_MORNING: 1.1, _B.BEAT_GOLDEN: 1.5,
             _B.BEAT_DUSK: 1.4, _B.BEAT_FESTIVAL: 1.0, _B.BEAT_PREDAWN: 0.5}
_BW_VENDOR = {_B.BEAT_MARKET: 2.4, _B.BEAT_MORNING: 1.8, _B.BEAT_GOLDEN: 1.0,
              _B.BEAT_DUSK: 0.8, _B.BEAT_FESTIVAL: 0.9, _B.BEAT_PREDAWN: 0.3}
# A padded winter mass must never turn up on a warm market day — snow-only, zero
# elsewhere (same gating idea as ped_cast's _WW buckets).
_WW_SNOW = {_B.WB_CLEAR: 0.0, _B.WB_RAIN: 0.0, _B.WB_SNOW: 1.0}
# Rain rows: the only ones eligible once it is raining (see _V's default, which
# locks every ordinary row OUT of rain). Mirrors ped_cast's _WW_RAIN.
_WW_RAIN = {_B.WB_CLEAR: 0.0, _B.WB_RAIN: 1.0, _B.WB_SNOW: 0.0}
# An ordinary row is barred from RAIN only. Deliberately NOT a full clear-preset:
# zeroing WB_SNOW too would empty these pools in the squall, where they are
# currently the whole cast, and the snow look is not being changed here.
_WW_DRY = {_B.WB_RAIN: 0.0}


def _V(palette, *, pose=(), acc=(), attrs=None, bw=None, ww=None):
    return fv.Variant(palette=palette, pose=frozenset(pose), accessory=frozenset(acc),
                      attrs=dict(attrs or {}), beat_weights=dict(bw or {}),
                      weather_weights=dict(_WW_DRY if ww is None else ww))


def _build_kids():
    return [
        _V(dict(shirt=(90, 165, 220), pants=(58, 52, 56), hair=(46, 36, 30), hair_style="bowl", skin="fair", prop=(150, 110, 64)),
           pose=("chase",), acc=("hoop", "stick"), attrs=dict(age=0.9), bw=_BW_KID),
        _V(dict(shirt=(250, 200, 70), pants=(70, 56, 48), hair=(40, 32, 28), hair_style="bowl", skin="tan"),
           pose=("squat",), attrs=dict(age=0.55), bw=_BW_KID),
        _V(dict(shirt=(120, 200, 130), pants=(64, 58, 50), hair=(50, 40, 32), hair_style="buns", skin="warm", prop=(228, 84, 92)),
           pose=("point",), acc=("balloon",), attrs=dict(age=0.7), bw=_BW_KID),
        _V(dict(shirt=(110, 130, 235), pants=(60, 54, 58), hair=(54, 42, 34), hair_style="bowl", skin="warm", carrier=(96, 84, 110)),
           pose=("carried",), attrs=dict(age=0.2), bw=_BW_KID),
        _V(dict(shirt=(212, 128, 92), pants=(66, 56, 50), hair=(44, 34, 28), hair_style="bowl", skin="tan"),
           pose=("tiptoe",), attrs=dict(age=0.5), bw=_BW_KID),
        _V(dict(shirt=(96, 186, 176), pants=(58, 56, 52), hair=(38, 30, 26), hair_style="tuft", skin="warm", prop=(240, 196, 70), tail=(224, 150, 70)),
           pose=("run",), acc=("kite",), attrs=dict(age=0.8), bw=_BW_KID),
        _V(dict(shirt=(226, 156, 186), pants=(64, 54, 58), hair=(46, 36, 30), hair_style="sidetails", skin="fair", prop=(216, 120, 150)),
           pose=("run",), acc=("ribbon",), attrs=dict(age=0.65), bw=_BW_KID),
        _V(dict(shirt=(150, 120, 200), pants=(60, 52, 56), hair=(40, 32, 28), hair_style="bowl", skin="ruddy", prop=(214, 122, 74), stick=(140, 106, 66)),
           acc=("lantern",), attrs=dict(age=0.6), bw=_BW_KID),
        _V(dict(shirt=(120, 158, 108), pants=(62, 56, 48), hair=(52, 40, 32), hair_style="bowl", skin="deep", bag=(146, 122, 86)),
           pose=("run",), acc=("satchel",), attrs=dict(age=0.95), bw=_BW_KID),
        _V(dict(shirt=(232, 176, 96), pants=(68, 58, 50), hair=(44, 34, 28), hair_style="sidetails", skin="warm"),
           pose=("squat",), attrs=dict(age=0.35), bw=_BW_KID),
        # RAIN — the only kid rows live once it is raining. Muted canopies so a
        # brolly never out-reads the coin; ages kept low so the umbrella is
        # comically oversized on the smallest of them.
        _V(dict(shirt=(96, 140, 190), pants=(60, 54, 56), hair=(44, 34, 28), hair_style="bowl", skin="fair",
                canopy=(150, 138, 102)),
           pose=("run",), acc=("umbrella",), attrs=dict(age=0.5), bw=_BW_KID, ww=_WW_RAIN),
        _V(dict(shirt=(200, 120, 110), pants=(64, 56, 50), hair=(50, 40, 32), hair_style="sidetails", skin="tan",
                canopy=(116, 132, 150)),
           acc=("umbrella",), attrs=dict(age=0.75), bw=_BW_KID, ww=_WW_RAIN),
        _V(dict(shirt=(126, 166, 122), pants=(58, 52, 48), hair=(38, 30, 26), hair_style="tuft", skin="warm",
                canopy=(176, 156, 120)),
           pose=("tiptoe",), acc=("umbrella",), attrs=dict(age=0.4), bw=_BW_KID, ww=_WW_RAIN),
    ]


def _build_elders():
    return [
        _V(dict(robe=(86, 96, 140), robe_dk=(52, 60, 100), sash=(200, 188, 150), hair=(208, 206, 198), skin="warm", head="bun"),
           acc=("fan", "beard"), attrs=dict(stance="taichi", height=1.04, build=1.0, fan=(224, 212, 190)), bw=_BW_ELDER),
        _V(dict(robe=(110, 134, 112), robe_dk=(70, 92, 76), sash=(206, 180, 140), hair=(204, 202, 196), skin="tan", head="cap", cap=(120, 96, 70)),
           acc=("birdcage",), attrs=dict(stance="upright", height=1.0, build=1.05, cage=(150, 116, 70)), bw=_BW_ELDER),
        _V(dict(robe=(118, 96, 84), robe_dk=(74, 58, 50), fur=(224, 216, 202), sash=(196, 170, 130), hair=(206, 204, 196), skin="ruddy", head="cap", cap=(110, 90, 66)),
           acc=("teacup", "beard"), attrs=dict(stance="seated", height=0.94, build=1.15, padded=True, tea=(228, 222, 210)), bw=_BW_ELDER),
        _V(dict(robe=(104, 80, 116), robe_dk=(66, 48, 78), sash=(208, 160, 140), hair=(206, 204, 198), skin="deep", head="bun"),
           attrs=dict(stance="birds", height=0.98, build=1.0), bw=_BW_ELDER),
        _V(dict(robe=(96, 110, 118), robe_dk=(58, 72, 80), sash=(184, 180, 156), hair=(210, 208, 200), skin="warm", head="bald", brush=(126, 96, 62), wet=(96, 88, 78)),
           acc=("beard",), attrs=dict(stance="brush", height=1.0, build=1.0, stoop=0.30), bw=_BW_ELDER),
        _V(dict(robe=(126, 108, 92), robe_dk=(82, 68, 56), sash=(196, 182, 152), hair=(208, 206, 198), skin="fair", head="cap", cap=(112, 92, 68), scroll=(208, 196, 168)),
           acc=("beard",), attrs=dict(stance="reading", height=1.02, build=1.02), bw=_BW_ELDER),
        _V(dict(robe=(92, 108, 96), robe_dk=(56, 72, 62), sash=(190, 184, 150), hair=(206, 204, 198), skin="tan", head="bun", blade=(168, 176, 184), tassel=(150, 92, 88)),
           acc=("sword",), attrs=dict(stance="taichi", height=1.06, build=0.96), bw=_BW_ELDER),
        _V(dict(robe=(120, 116, 88), robe_dk=(78, 76, 56), sash=(190, 176, 138), hair=(204, 202, 196), skin="deep", head="cap", cap=(118, 96, 70), basket=(166, 126, 76), herbs=(104, 128, 92), cane=(118, 82, 50)),
           acc=("back_basket", "cane"), attrs=dict(stance="upright", height=0.96, build=1.0, stoop=0.22), bw=_BW_ELDER),
        _V(dict(robe=(112, 92, 116), robe_dk=(72, 56, 76), sash=(198, 176, 150), hair=(210, 208, 200), skin="warm", head="bald", fan=(214, 202, 180)),
           acc=("fan",), attrs=dict(stance="seated", height=0.96, build=1.05), bw=_BW_ELDER),
        _V(dict(robe=(100, 96, 108), robe_dk=(62, 60, 70), fur=(216, 208, 194), sash=(186, 180, 160), hair=(208, 206, 198), skin="fair", head="cap", cap=(106, 88, 70), tea=(224, 218, 206)),
           acc=("teacup", "beard"), attrs=dict(stance="upright", height=0.98, build=1.12, padded=True), bw=_BW_ELDER, ww=_WW_SNOW),
        # RAIN — an elder does not hurry, so the brolly is the whole costume
        # change: the robe palette is the family's own, only the canopy is new.
        _V(dict(robe=(92, 100, 132), robe_dk=(58, 64, 94), sash=(196, 184, 148), hair=(206, 204, 198),
                skin="warm", head="bun", canopy=(150, 138, 102)),
           acc=("umbrella", "beard"), attrs=dict(stance="upright", height=1.0, build=1.0), bw=_BW_ELDER, ww=_WW_RAIN),
        _V(dict(robe=(106, 120, 106), robe_dk=(68, 82, 70), sash=(200, 178, 138), hair=(204, 202, 196),
                skin="tan", head="cap", cap=(114, 92, 68), canopy=(116, 132, 150)),
           acc=("umbrella",), attrs=dict(stance="upright", height=0.98, build=1.06), bw=_BW_ELDER, ww=_WW_RAIN),
        _V(dict(robe=(112, 92, 82), robe_dk=(72, 56, 50), sash=(192, 168, 130), hair=(208, 206, 198),
                skin="deep", head="bun", canopy=(176, 156, 120)),
           acc=("umbrella", "beard"), attrs=dict(stance="upright", height=0.96, build=1.1), bw=_BW_ELDER, ww=_WW_RAIN),
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
        _V(dict(shirt=(140, 104, 130), shirt_dk=(94, 66, 90), apron=(206, 194, 174), pants=(64, 56, 58), hair=(50, 40, 32), skin="fair", hat="cloth", hat_c=(150, 100, 84), sign=(168, 78, 70)),
           attrs=dict(pose="sign", height=1.0, build=1.04), bw=_BW_VENDOR),
        _V(dict(shirt=(150, 86, 70), shirt_dk=(104, 56, 46), apron=(214, 200, 178), pants=(70, 60, 52), hair=(46, 36, 30), skin="tan", hat="wrap", hat_c=(146, 108, 92), blade=(176, 182, 190), board=(146, 116, 76)),
           acc=("rolled",), attrs=dict(pose="chop", height=1.0, build=1.1), bw=_BW_VENDOR),
        _V(dict(shirt=(88, 110, 148), shirt_dk=(54, 70, 104), apron=(204, 194, 176), pants=(60, 58, 62), hair=(40, 32, 28), skin="fair", hat="cap", hat_c=(112, 96, 74), pot=(140, 118, 96), tea=(196, 168, 120)),
           acc=("towel",), attrs=dict(pose="pour", height=1.04, build=0.98), bw=_BW_VENDOR),
        _V(dict(shirt=(126, 92, 84), shirt_dk=(84, 58, 52), apron=(208, 196, 176), pants=(66, 56, 50), hair=(50, 40, 32), skin="deep", hat="none", pan=(96, 88, 82), food=(206, 156, 92)),
           acc=("rolled", "towel"), attrs=dict(pose="wok", height=0.98, build=1.16), bw=_BW_VENDOR),
        _V(dict(shirt=(112, 128, 96), shirt_dk=(72, 88, 62), apron=(208, 198, 176), pants=(62, 58, 48), hair=(44, 34, 28), skin="ruddy", hat="cloth", hat_c=(148, 104, 88)),
           acc=("rolled",), attrs=dict(pose="weigh", height=0.96, build=1.22), bw=_BW_VENDOR),
        # RAIN — a vendor keeps working, so the brolly is wedged over the stall
        # while the free hand still calls/ladles. Poses reuse the shipped set.
        _V(dict(shirt=(138, 92, 78), shirt_dk=(96, 60, 50), apron=(208, 196, 174), pants=(66, 58, 50),
                hair=(46, 36, 30), skin="tan", hat="none", canopy=(150, 138, 102)),
           acc=("umbrella", "rolled"), attrs=dict(pose="call", height=1.0, build=1.06), bw=_BW_VENDOR, ww=_WW_RAIN),
        _V(dict(shirt=(80, 118, 118), shirt_dk=(50, 80, 80), apron=(202, 192, 172), pants=(62, 56, 48),
                hair=(40, 32, 28), skin="warm", hat="none", canopy=(116, 132, 150)),
           acc=("umbrella",), attrs=dict(pose="ladle", height=1.04, build=0.96), bw=_BW_VENDOR, ww=_WW_RAIN),
        _V(dict(shirt=(146, 122, 76), shirt_dk=(100, 82, 50), apron=(206, 194, 170), pants=(62, 56, 46),
                hair=(50, 40, 32), skin="deep", hat="none", canopy=(176, 156, 120)),
           acc=("umbrella", "towel"), attrs=dict(pose="fan", height=0.98, build=1.14), bw=_BW_VENDOR, ww=_WW_RAIN),
    ]


fv.register("kid", _build_kids())
fv.register("elder", _build_elders())
fv.register("vendor", _build_vendors())
