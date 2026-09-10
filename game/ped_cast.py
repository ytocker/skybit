"""Promenade adult-pedestrian cast — a 50-strong variety pool.

Replaces the single repeated walker template. Variety is data: ~9 SILHOUETTE-
distinct body archetypes × palette role-sets × pose/accessory/height/stoop/build
flags over ONE shared body drawer (`_draw_one`), registered as
`foreground_variants` rows under the 'pedestrian' family. The per-slot/beat/
weather selector then spreads them across the street so the same person rarely
recurs, and weather members (rain umbrellas/hoods, snow padded coats) swap in via
the weather-weight buckets.

Figures are authored at a fixed pixel height anchored to an explicit `base_y`
(the caller passes GROUND_Y, which the near lane temporarily repoints to its
scratch deck), facing the scroll direction. The art-director's findings drove the
look: variety lives in the OUTLINE (body shape + height + stoop + outline-breaking
accessories), since the small on-screen size erases colour and interior detail
first; the FAR lane draws crisp, the NEAR lane lightly smoothscales for AA.

Pure-Pygame / pygbag-safe (draw.* + Surface only). Night cooling via the local
_retint_person (matches the promenade) keeps every figure under the coin.
"""
from __future__ import annotations

import math

import pygame

from game.foreground_props import _mix, _shade, _clamp
from game import foreground_variants as fv

# Fixed authoring height for a 1.0-height figure (px, feet→crown). Height/build/
# stoop flags modulate it. A touch taller + more detailed than the old ~11px
# template, but still tiny — the silhouette carries it.
PED_H = 18

NIGHT_GLOW_CAP = 150


def _retint_person(col, night):
    """Cool clothing toward the night ground band (matches promenade._retint_person)."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


SKIN_TONES = {
    "fair":  (236, 198, 156),
    "warm":  (222, 178, 132),
    "tan":   (200, 156, 112),
    "deep":  (168, 124, 86),
    "ruddy": (228, 176, 150),
}

# Silhouette archetype keys (the outline-distinct classes).
A_ROBE = "robe"; A_SKIRT = "skirt"; A_TUNIC = "tunic"; A_PADDED = "padded"
A_STOOP = "stoop"; A_POLE = "pole"; A_YOKE = "yoke"; A_HEADLOAD = "headload"
A_CHILD = "child"


def _legs(surf, cx, body_w, torso_bot, ground, gait, hurry, col_leg, col_foot, hidden):
    swing = gait * body_w * (0.55 if hurry else 0.30)
    for sgn, sw_ in ((-1, swing), (1, -swing)):
        foot_x = cx + sgn * body_w * 0.20 + sw_ * 0.5
        if hidden:
            pygame.draw.line(surf, col_leg, (cx + sgn * body_w * 0.20, torso_bot),
                             (foot_x, ground), max(2, body_w // 4))
        else:
            pygame.draw.line(surf, col_leg, (cx + sgn * body_w * 0.20, torso_bot - body_w * 0.2),
                             (foot_x, ground), max(2, body_w // 3))
            pygame.draw.line(surf, col_foot, (foot_x - 1, ground), (foot_x + 2, ground),
                             max(2, body_w // 3))


def _draw_one(surf, cx, base_y, pal, v, night, t):
    """Draw one pedestrian: feet on `base_y`, centred on `cx`, total height
    PED_H×height. `v` is a foreground_variants.Variant; its `attrs` carry the
    archetype/height/stoop/build, `palette` the colour roles, `pose`/`accessory`
    the flag sets."""
    P = v.palette
    A = v.attrs
    pf = lambda c: _retint_person(c, night)

    skin = pf(SKIN_TONES.get(P.get("skin", "warm"), SKIN_TONES["warm"]))
    skin_sh = _shade(skin, -28)
    coat = pf(P["coat"])
    coat_dk = pf(P.get("coat_dk", _shade(P["coat"], -42)))
    coat_lt = _shade(coat, 16)
    trim = pf(P.get("trim", _shade(P["coat"], 28)))
    hair = pf(P.get("hair", (58, 42, 34)))
    hair_dk = _shade(hair, -22)
    sash = pf(P.get("sash", trim))
    trousers = pf(P.get("trousers", coat_dk))

    height = A.get("height", 1.0)
    build = A.get("build", 1.0)
    stoop = A.get("stoop", 0.0)
    arch = A.get("arch", A_ROBE)

    total_h = max(7, int(PED_H * height))
    head_r = max(2, int(total_h * 0.135))
    torso_h = int(total_h * 0.44)
    leg_h = max(2, total_h - torso_h - head_r * 2)
    body_w = max(2, int(total_h * 0.27 * build))

    ground = int(base_y)
    head_cy = ground - leg_h - torso_h - head_r
    torso_top = head_cy + head_r
    torso_bot = torso_top + torso_h

    hurry = "hurry" in v.pose
    hz = 2.6 if hurry else 1.5
    gait = math.sin(t * hz)
    lean = int(body_w * (0.30 if hurry else 0.12)) + int(body_w * 1.6 * stoop)
    bob = -abs(gait) * (total_h * 0.03)
    head_cy += int(bob) + int(torso_h * 0.55 * stoop)
    torso_top += int(bob)

    arm_y = torso_top + int(head_r * 0.7)
    hx = cx + lean
    hy = head_cy

    robe_like = arch in (A_ROBE, A_SKIRT, A_STOOP)
    if arch != A_CHILD:
        _legs(surf, cx, body_w, torso_bot, ground, gait, hurry,
              coat_dk if robe_like else trousers,
              _shade(coat_dk if robe_like else trousers, -30), robe_like)
    else:
        for sgn in (-1, 1):
            fx = cx + sgn * body_w * 0.4 + gait * body_w * 0.4 * sgn
            pygame.draw.line(surf, trousers, (cx + sgn * body_w * 0.3, torso_bot),
                             (fx, ground), max(2, body_w // 2))

    # ── TORSO per archetype — the silhouette-defining shape ──
    if arch == A_ROBE:
        sh_w = int(body_w * 0.70); hem_w = int(body_w * 0.82)
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(surf, coat, pts)
        pygame.draw.polygon(surf, coat_dk, pts, max(1, body_w // 8))
        pygame.draw.line(surf, coat_dk, (cx + lean // 2, torso_top + head_r // 2),
                         (cx, pts[3][1]), max(1, body_w // 10))
        sy = torso_top + torso_h // 2
        pygame.draw.line(surf, sash, (cx - sh_w, sy), (cx + sh_w, sy), max(2, body_w // 5))
    elif arch in (A_SKIRT, A_STOOP):
        sh_w = int(body_w * 0.74); hem_w = int(body_w * 1.45)
        bot = ground if arch == A_STOOP else torso_bot
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, bot), (cx - hem_w, bot)]
        pygame.draw.polygon(surf, coat, pts)
        pygame.draw.polygon(surf, coat_dk, pts, max(1, body_w // 8))
        sy = torso_top + torso_h // 2
        pygame.draw.line(surf, sash, (cx - body_w, sy), (cx + body_w, sy), max(2, body_w // 5))
    elif arch == A_TUNIC:
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 3))
        pygame.draw.rect(surf, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 3))
        pygame.draw.line(surf, coat_lt, (cx + lean, torso_top + 1), (cx + lean, torso_bot - 1),
                         max(1, body_w // 9))
    elif arch == A_PADDED:
        pad_w = int(body_w * 1.35)
        r = pygame.Rect(cx - pad_w + lean, torso_top - head_r // 2, pad_w * 2, torso_h + head_r // 2)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 5))
        pygame.draw.rect(surf, coat_dk, r, max(2, body_w // 6), border_radius=max(2, body_w // 5))
        for q in (0.34, 0.66):
            yy = int(r.top + r.height * q)
            pygame.draw.line(surf, coat_dk, (r.left + 2, yy), (r.right - 2, yy), 1)
        fur = pf(P.get("fur", (226, 218, 204)))
        pygame.draw.line(surf, fur, (r.left, r.top), (r.right, r.top), max(2, body_w // 4))
    elif arch == A_POLE:
        sh_w = int(body_w * 0.74); hem_w = int(body_w * 1.0)
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(surf, coat, pts)
        pygame.draw.polygon(surf, coat_dk, pts, max(1, body_w // 8))
    elif arch == A_YOKE:
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 4))
        pygame.draw.rect(surf, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 4))
    elif arch == A_HEADLOAD:
        sh_w = int(body_w * 0.80); hem_w = int(body_w * 0.95)
        pts = [(cx - sh_w, torso_top), (cx + sh_w, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(surf, coat, pts)
        pygame.draw.polygon(surf, coat_dk, pts, max(1, body_w // 8))
        pygame.draw.line(surf, coat, (cx + sh_w * 0.4, torso_top + head_r // 2),
                         (cx + head_r // 2, hy - head_r), max(2, body_w // 5))
    elif arch == A_CHILD:
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(surf, coat, r, border_radius=max(2, body_w // 2))
        pygame.draw.rect(surf, coat_dk, r, 1, border_radius=max(2, body_w // 2))

    # ── ACCESSORIES that break the outline ──
    if arch == A_POLE:
        pole_c = pf((120, 88, 54)); py = torso_top - 1
        x0, x1 = cx - body_w * 1.7, cx + body_w * 1.7 + lean
        pygame.draw.line(surf, pole_c, (x0, py + 3), (x1, py - 3), max(2, body_w // 6))
        for ex, ey in ((x0, py + 3), (x1, py - 3)):
            bk = pf(P.get("basket", (176, 132, 78)))
            br = pygame.Rect(ex - body_w * 0.6, ey + body_w * 0.5, body_w * 1.2, body_w * 1.0)
            pygame.draw.ellipse(surf, bk, br)
            pygame.draw.ellipse(surf, _shade(bk, -30), br, 1)
            pygame.draw.circle(surf, pf(P.get("goods", (224, 120, 60))),
                               (int(ex), int(ey + body_w * 0.6)), max(1, body_w // 4))
    elif arch == A_YOKE:
        yoke_c = pf((110, 80, 50)); yy = torso_top - 1
        x0, x1 = cx - body_w * 1.5, cx + body_w * 1.5 + lean
        pygame.draw.line(surf, yoke_c, (x0, yy), (x1, yy), max(2, body_w // 6))
        for ex in (x0, x1):
            sk = pf(P.get("load", (150, 124, 86)))
            sr = pygame.Rect(ex - body_w * 0.5, yy + 2, body_w * 1.0, torso_h * 1.15)
            pygame.draw.rect(surf, sk, sr, border_radius=max(1, body_w // 3))
            pygame.draw.rect(surf, _shade(sk, -32), sr, 1, border_radius=max(1, body_w // 3))
            pygame.draw.line(surf, yoke_c, (ex, yy), (ex, sr.top), max(1, body_w // 6))
    elif arch == A_HEADLOAD:
        tray = pf(P.get("tray", (164, 120, 76)))
        tw = int(body_w * 1.9); th = max(3, int(head_r * 0.9)); ty = hy - head_r - th - 1
        tr = pygame.Rect(hx - tw, ty, tw * 2, th)
        pygame.draw.rect(surf, tray, tr, border_radius=max(1, body_w // 4))
        pygame.draw.rect(surf, _shade(tray, -34), tr, 1, border_radius=max(1, body_w // 4))
        for gx in (-0.5, 0.0, 0.5):
            pygame.draw.circle(surf, pf(P.get("goods", (218, 130, 70))),
                               (int(hx + gx * tw), int(ty)), max(1, body_w // 3))

    if "basket_arm" in v.accessory:
        bk = pf(P.get("basket", (176, 132, 78))); bhx = cx + body_w * 1.5 + lean
        pygame.draw.line(surf, coat, (cx + body_w * 0.6 + lean, arm_y),
                         (bhx, arm_y + torso_h // 2), max(2, body_w // 5))
        br = pygame.Rect(bhx - body_w * 0.55, arm_y + torso_h // 2, body_w * 1.1, body_w * 0.9)
        pygame.draw.ellipse(surf, bk, br)
        pygame.draw.ellipse(surf, _shade(bk, -30), br, 1)
    if "cane" in v.accessory:
        cane_c = pf(P.get("cane", (120, 84, 50))); chx = cx + body_w * 1.3 + lean
        pygame.draw.line(surf, cane_c, (chx, arm_y), (chx + body_w * 0.3, ground), max(2, body_w // 6))
        pygame.draw.line(surf, coat, (cx + body_w * 0.5 + lean, arm_y), (chx, arm_y), max(2, body_w // 5))
    if "bundle" in v.accessory:
        bd = pf(P.get("bundle", (198, 176, 150)))
        br = pygame.Rect(cx - body_w * 0.7 + lean, arm_y + 1, body_w * 1.4, torso_h // 2)
        pygame.draw.rect(surf, bd, br, border_radius=max(1, body_w // 4))
    if "hand_hold" in v.accessory:
        pygame.draw.line(surf, skin, (cx + body_w * 0.7 + lean, arm_y + torso_h // 2),
                         (cx + body_w * 1.2 + lean, ground - leg_h * 0.3), max(2, body_w // 5))
    if "reach_up" in v.accessory:
        pygame.draw.line(surf, skin, (cx + body_w * 0.5 + lean, arm_y),
                         (cx + body_w * 1.3 + lean, arm_y - torso_h * 0.4), max(2, body_w // 4))
    if "swing_arm" in v.pose and arch == A_TUNIC:
        ax = cx + lean + int(gait * body_w * 0.5)
        pygame.draw.line(surf, coat, (cx + lean, arm_y),
                         (ax + body_w * 0.4, arm_y + torso_h * 0.55), max(2, body_w // 5))
        pygame.draw.circle(surf, skin, (int(ax + body_w * 0.4), int(arm_y + torso_h * 0.55)),
                           max(1, body_w // 6))

    # ── HEAD + NECK ──
    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (40, 28, 22), (hx + head_r // 3, hy - head_r // 6), max(1, head_r // 4))
    if "beard" in v.accessory:
        grey = pf(P.get("beard", (210, 208, 200)))
        pygame.draw.polygon(surf, grey, [
            (hx - head_r * 0.6, hy + head_r * 0.3), (hx + head_r * 0.6, hy + head_r * 0.3),
            (hx + head_r * 0.2, hy + head_r * 1.7), (hx - head_r * 0.2, hy + head_r * 1.7)])

    # ── HEADWEAR (outline-breaker) ──
    hat = P.get("hat")
    if hat == "conical":
        col = pf(P.get("hat_c", (198, 162, 96))); brim_w = int(head_r * 2.5)
        apex = (hx, hy - head_r * 1.8)
        cone = [(hx - brim_w, hy - head_r * 0.15), apex, (hx + brim_w, hy - head_r * 0.15)]
        pygame.draw.polygon(surf, col, cone)
        pygame.draw.polygon(surf, _shade(col, -34), cone, 1)
    elif hat == "winter":
        col = pf(P.get("hat_c", (150, 96, 80)))
        cap = pygame.Rect(hx - head_r, hy - head_r * 1.7, head_r * 2, int(head_r * 1.6))
        pygame.draw.ellipse(surf, col, cap)
        fur = pf(P.get("fur", (224, 214, 198)))
        pygame.draw.line(surf, fur, (hx - head_r, hy - head_r * 0.35),
                         (hx + head_r, hy - head_r * 0.35), max(2, head_r // 2))
    elif hat == "hood":
        col = pf(P.get("hat_c", coat))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 3), int(head_r * 1.35))
        pygame.draw.circle(surf, skin, (hx + head_r // 4, hy), int(head_r * 0.8))
    elif hat == "cloth":
        col = pf(P.get("hat_c", (190, 90, 80)))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(surf, skin, (hx + head_r // 3, hy + head_r // 5), int(head_r * 0.75))
    elif hat == "bald":
        pygame.draw.circle(surf, skin, (hx, hy - head_r // 4), head_r)
        pygame.draw.arc(surf, hair, pygame.Rect(hx - head_r, hy - head_r // 2, head_r * 2, head_r * 2),
                        math.radians(200), math.radians(340), max(1, head_r // 3))
    elif hat == "bun":
        pygame.draw.circle(surf, hair, (hx, hy - head_r), head_r)
        pygame.draw.circle(surf, hair_dk, (hx - head_r // 3, hy - int(head_r * 1.3)), max(2, head_r // 2))
        if "hairpin" in v.accessory:
            pin = pf(P.get("pin", (220, 90, 100)))
            pygame.draw.line(surf, pin, (hx - head_r // 3, hy - int(head_r * 1.5)),
                             (hx + head_r // 2, hy - int(head_r * 1.7)), 2)
    else:
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        pygame.draw.arc(surf, hair, pygame.Rect(hx - head_r, hy - head_r, head_r * 2, head_r * 2),
                        math.radians(0), math.radians(180), max(1, head_r // 2))
        if "topknot" in v.accessory:
            pygame.draw.circle(surf, hair_dk, (hx, hy - int(head_r * 1.4)), max(2, head_r // 2))

    # ── HELD PARASOL / UMBRELLA (overhead — strongest outline-breaker) ──
    if "parasol" in v.accessory or "umbrella" in v.accessory:
        col = pf(P.get("canopy", (236, 224, 210))); dark = _shade(col, -42)
        cr = int(head_r * 2.5)
        tilt = int(head_r * (0.5 if "umbrella" in v.accessory else 0.15))
        cy = hy - int(head_r * 2.7); apex_x = hx + tilt
        canopy = [(hx - cr, cy), (apex_x - cr // 2, cy - cr // 2), (apex_x, cy - cr),
                  (apex_x + cr // 2, cy - cr // 2), (hx + cr, cy),
                  (hx + cr * 3 // 5, cy + 3), (hx, cy + 1), (hx - cr * 3 // 5, cy + 3)]
        pygame.draw.polygon(surf, col, canopy)
        pygame.draw.polygon(surf, dark, canopy, max(1, head_r // 4))
        pygame.draw.line(surf, pf((110, 84, 56)), (hx, cy + 1), (hx - 1, arm_y + torso_h // 3),
                         max(2, head_r // 4))


# ── the 50-strong pool, registered as foreground_variants 'pedestrian' rows ───

_COATS = {
    "indigo": ((86, 96, 140), (52, 60, 100)), "plum": ((104, 80, 116), (66, 48, 78)),
    "sage": ((110, 134, 112), (70, 92, 76)), "ochre": ((158, 128, 78), (108, 84, 50)),
    "rust": ((150, 86, 70), (104, 56, 46)), "teal": ((78, 124, 124), (48, 84, 84)),
    "slate": ((100, 108, 124), (64, 72, 90)), "olive": ((118, 116, 80), (78, 78, 52)),
    "clay": ((168, 120, 84), (114, 78, 54)), "mauve": ((140, 104, 130), (94, 66, 90)),
    "stone": ((128, 124, 112), (84, 82, 72)), "wine": ((128, 70, 78), (84, 44, 50)),
}
_HAIRS = [(46, 36, 30), (40, 32, 28), (58, 44, 36), (34, 28, 26), (70, 56, 44)]

_B = fv.BEAT_MARKET, fv.BEAT_MORNING, fv.BEAT_GOLDEN, fv.BEAT_DUSK, fv.BEAT_FESTIVAL, fv.BEAT_PREDAWN
# beat-weight presets by social role
_BW_MARKET = {fv.BEAT_MARKET: 2.6, fv.BEAT_MORNING: 1.6, fv.BEAT_GOLDEN: 1.0,
              fv.BEAT_DUSK: 0.8, fv.BEAT_FESTIVAL: 0.7, fv.BEAT_PREDAWN: 0.3}
_BW_STROLL = {fv.BEAT_MARKET: 0.8, fv.BEAT_MORNING: 1.0, fv.BEAT_GOLDEN: 1.4,
              fv.BEAT_DUSK: 1.3, fv.BEAT_FESTIVAL: 1.2, fv.BEAT_PREDAWN: 0.4}
_BW_ELDER = {fv.BEAT_GOLDEN: 1.4, fv.BEAT_DUSK: 1.3, fv.BEAT_FESTIVAL: 0.9, fv.BEAT_PREDAWN: 0.4}
_BW_CHILD = {fv.BEAT_MARKET: 1.6, fv.BEAT_MORNING: 1.0, fv.BEAT_GOLDEN: 1.1,
             fv.BEAT_FESTIVAL: 1.8, fv.BEAT_PREDAWN: 0.2}
# weather presets — clear figures stay out of rain/snow; weather figures own them
_WW_CLEAR = {fv.WB_RAIN: 0.0, fv.WB_SNOW: 0.0}
_WW_RAIN = {fv.WB_CLEAR: 0.0, fv.WB_RAIN: 1.0, fv.WB_SNOW: 0.0}
_WW_SNOW = {fv.WB_CLEAR: 0.0, fv.WB_RAIN: 0.0, fv.WB_SNOW: 1.0}


def _c(name):
    return dict(coat=_COATS[name][0], coat_dk=_COATS[name][1])


def _V(palette, arch, *, pose=(), acc=(), height=1.0, stoop=0.0, build=1.0,
       bw=None, ww=None):
    return fv.Variant(
        palette=palette, pose=frozenset(pose), accessory=frozenset(acc),
        beat_weights=dict(bw or {}), weather_weights=dict(ww if ww is not None else _WW_CLEAR),
        attrs={"arch": arch, "height": height, "stoop": stoop, "build": build})


def _build_pool():
    P = []
    # ARCH 1 — narrow robe (scholar/lady/parent)
    P += [
        _V(dict(**_c("indigo"), sash=(206, 200, 170), hair=_HAIRS[2], skin="fair", hat="bun"),
           A_ROBE, pose=("stroll",), acc=("topknot",), height=1.10, bw=_BW_STROLL),
        _V(dict(**_c("plum"), sash=(196, 180, 150), hair=(206, 204, 196), beard=(212, 210, 202),
                skin="fair", hat="bun"), A_ROBE, pose=("stroll",), acc=("beard", "topknot"),
           bw=_BW_ELDER),
        _V(dict(**_c("teal"), sash=(200, 188, 150), hair=_HAIRS[1], skin="warm", hat="bun"),
           A_ROBE, pose=("hurry",), acc=("topknot",), height=0.92, build=0.9, bw=_BW_STROLL),
        _V(dict(**_c("mauve"), sash=(208, 160, 140), hair=_HAIRS[3], skin="fair", hat="bun",
                pin=(214, 110, 120)), A_ROBE, pose=("stroll",), acc=("hairpin",),
           height=1.04, build=0.92, bw=_BW_STROLL),
        _V(dict(**_c("slate"), sash=(180, 186, 196), hair=_HAIRS[0], skin="tan", hat="bun"),
           A_ROBE, pose=("stroll",), acc=("topknot",), height=1.10, build=0.95, bw=_BW_STROLL),
    ]
    # ARCH 2 — wide A-line skirt (matron/merchant)
    P += [
        _V(dict(**_c("sage"), sash=(214, 190, 140), hair=_HAIRS[1], skin="warm", hat="cloth",
                hat_c=(186, 92, 84), basket=(182, 138, 84), goods=(196, 96, 90)), A_SKIRT,
           pose=("stroll",), acc=("basket_arm",), height=0.96, build=1.1, bw=_BW_MARKET),
        _V(dict(**_c("ochre"), sash=(150, 74, 66), hair=_HAIRS[0], skin="tan", hat="conical",
                hat_c=(188, 152, 90)), A_SKIRT, pose=("stroll",), height=0.98, build=1.28, bw=_BW_MARKET),
        _V(dict(**_c("clay"), sash=(206, 180, 140), hair=_HAIRS[4], skin="ruddy", hat="cloth",
                hat_c=(170, 96, 80), basket=(176, 132, 78), goods=(200, 120, 70)), A_SKIRT,
           pose=("stroll",), acc=("basket_arm",), height=0.94, build=1.12, bw=_BW_MARKET),
        _V(dict(**_c("olive"), sash=(140, 80, 70), hair=_HAIRS[3], skin="deep", hat="conical",
                hat_c=(176, 146, 86)), A_SKIRT, pose=("stroll",), height=1.0, build=1.22, bw=_BW_MARKET),
        _V(dict(**_c("stone"), sash=(196, 150, 120), hair=_HAIRS[2], skin="warm", hat="cloth",
                hat_c=(150, 110, 96), basket=(170, 128, 80), goods=(180, 140, 80)), A_SKIRT,
           pose=("stroll",), acc=("basket_arm",), height=0.97, build=1.08, bw=_BW_MARKET),
    ]
    # ARCH 3 — short tunic (porter/youth)
    P += [
        _V(dict(**_c("clay"), trousers=(74, 64, 56), hair=_HAIRS[3], skin="deep"), A_TUNIC,
           pose=("hurry", "swing_arm"), height=1.02, build=1.12, bw=_BW_MARKET),
        _V(dict(**_c("teal"), trousers=(68, 62, 66), hair=_HAIRS[1], skin="warm"), A_TUNIC,
           pose=("hurry", "swing_arm"), height=0.92, build=0.9, bw=_BW_MARKET),
        _V(dict(**_c("ochre"), trousers=(70, 60, 50), hair=_HAIRS[0], skin="tan"), A_TUNIC,
           pose=("hurry", "swing_arm"), height=1.0, build=1.05, bw=_BW_MARKET),
        _V(dict(**_c("slate"), trousers=(60, 64, 74), hair=_HAIRS[2], skin="warm"), A_TUNIC,
           pose=("stroll", "swing_arm"), height=1.0, build=1.0, bw=_BW_STROLL),
        _V(dict(**_c("rust"), trousers=(72, 56, 50), hair=_HAIRS[4], skin="ruddy"), A_TUNIC,
           pose=("hurry", "swing_arm"), height=1.04, build=1.1, bw=_BW_MARKET),
        _V(dict(**_c("olive"), trousers=(64, 62, 48), hair=_HAIRS[3], skin="deep"), A_TUNIC,
           pose=("hurry", "swing_arm"), height=0.9, build=0.92, bw=_BW_MARKET),
    ]
    # ARCH 4 — boxy padded coat [SNOW]
    P += [
        _V(dict(**_c("rust"), fur=(228, 220, 206), hair=_HAIRS[3], skin="ruddy", hat="winter",
                hat_c=(150, 88, 74), bundle=(206, 188, 162)), A_PADDED, pose=("hurry",),
           acc=("bundle",), height=0.98, build=1.2, ww=_WW_SNOW),
        _V(dict(**_c("indigo"), fur=(222, 214, 200), trim=(206, 110, 96), hair=_HAIRS[2],
                skin="fair", hat="winter", hat_c=(86, 100, 138)), A_PADDED, pose=("stroll",),
           height=0.96, build=1.18, ww=_WW_SNOW),
        _V(dict(**_c("olive"), fur=(226, 218, 204), hair=(206, 204, 196), beard=(214, 212, 204),
                skin="warm", hat="winter", hat_c=(120, 100, 70)), A_PADDED, pose=("stroll",),
           acc=("beard",), height=0.92, build=1.15, ww=_WW_SNOW),
        _V(dict(**_c("clay"), fur=(228, 222, 210), hair=_HAIRS[1], skin="warm", hat="winter",
                hat_c=(150, 104, 76)), A_PADDED, pose=("hurry",), height=0.78, build=1.0, ww=_WW_SNOW),
        _V(dict(**_c("slate"), fur=(224, 216, 202), hair=_HAIRS[0], skin="tan", hat="winter",
                hat_c=(96, 102, 120), bundle=(200, 184, 158)), A_PADDED, pose=("hurry",),
           acc=("bundle",), height=1.0, build=1.22, ww=_WW_SNOW),
    ]
    # ARCH 5 — hunched cane elder
    P += [
        _V(dict(**_c("plum"), sash=(196, 180, 150), hair=(208, 206, 198), beard=(214, 212, 204),
                skin="fair", hat="bald", cane=(120, 84, 50)), A_STOOP, pose=("stroll",),
           acc=("beard", "cane"), height=0.9, stoop=0.42, bw=_BW_ELDER),
        _V(dict(**_c("slate"), sash=(180, 184, 192), hair=(204, 202, 196), beard=(210, 208, 200),
                skin="warm", hat="bald", cane=(116, 80, 48)), A_STOOP, pose=("stroll",),
           acc=("beard", "cane"), height=0.88, stoop=0.46, bw=_BW_ELDER),
        _V(dict(**_c("olive"), sash=(196, 170, 130), hair=(202, 200, 194), skin="ruddy",
                hat="cloth", hat_c=(150, 110, 96), cane=(118, 82, 50)), A_STOOP, pose=("stroll",),
           acc=("cane",), height=0.88, stoop=0.40, bw=_BW_ELDER),
        _V(dict(**_c("mauve"), sash=(200, 170, 150), hair=(206, 204, 198), beard=(212, 210, 202),
                skin="deep", hat="bald", cane=(110, 78, 46)), A_STOOP, pose=("stroll",),
           acc=("beard", "cane"), height=0.86, stoop=0.48, bw=_BW_ELDER),
    ]
    # ARCH 6 — carrying-pole vendor
    P += [
        _V(dict(**_c("rust"), hair=_HAIRS[0], skin="tan", hat="conical", hat_c=(196, 158, 92),
                basket=(176, 132, 78), goods=(214, 130, 70)), A_POLE, pose=("hurry",),
           height=1.0, build=1.05, bw=_BW_MARKET),
        _V(dict(**_c("ochre"), hair=_HAIRS[3], skin="deep", hat="cloth", hat_c=(160, 96, 84),
                basket=(170, 126, 76), goods=(200, 110, 80)), A_POLE, pose=("hurry",),
           height=1.0, build=1.05, bw=_BW_MARKET),
        _V(dict(**_c("sage"), hair=_HAIRS[1], skin="warm", hat="conical", hat_c=(184, 150, 88),
                basket=(178, 134, 80), goods=(186, 150, 80)), A_POLE, pose=("stroll",),
           height=1.04, bw=_BW_MARKET),
        _V(dict(**_c("clay"), hair=_HAIRS[4], skin="ruddy", hat="conical", hat_c=(190, 156, 92),
                basket=(172, 128, 78), goods=(210, 120, 64)), A_POLE, pose=("hurry",),
           height=0.98, build=1.08, bw=_BW_MARKET),
        _V(dict(**_c("olive"), hair=_HAIRS[0], skin="tan", hat="cloth", hat_c=(150, 100, 80),
                basket=(176, 130, 80), goods=(190, 140, 70)), A_POLE, pose=("hurry",),
           height=1.0, build=1.05, bw=_BW_MARKET),
    ]
    # ARCH 7 — shoulder-yoke porter
    for nm, hr, sk, ld, h, b in [("ochre", 0, "deep", (150, 124, 86), 1.02, 1.1),
                                 ("rust", 3, "tan", (158, 130, 90), 1.0, 1.12),
                                 ("slate", 1, "warm", (146, 120, 84), 1.06, 1.08),
                                 ("clay", 4, "ruddy", (162, 134, 92), 0.98, 1.1),
                                 ("olive", 2, "warm", (152, 126, 88), 1.0, 1.06)]:
        P.append(_V(dict(**_c(nm), trousers=(70, 60, 52), hair=_HAIRS[hr], skin=sk, load=ld),
                    A_YOKE, pose=("hurry",), height=h, build=b, bw=_BW_MARKET))
    # ARCH 8 — tray on head
    for nm, hr, sk, tr, gd, h in [("sage", 1, "warm", (164, 120, 76), (214, 130, 70), 1.0),
                                  ("clay", 4, "ruddy", (160, 118, 74), (196, 150, 80), 0.96),
                                  ("indigo", 2, "fair", (150, 112, 70), (206, 120, 70), 1.04),
                                  ("ochre", 0, "tan", (140, 104, 64), (180, 140, 84), 1.0),
                                  ("rust", 3, "deep", (158, 116, 74), (210, 120, 64), 0.98)]:
        P.append(_V(dict(**_c(nm), tray=tr, hair=_HAIRS[hr], skin=sk, goods=gd), A_HEADLOAD,
                    pose=("stroll",), height=h, bw=_BW_MARKET))
    # ARCH 9 — children + tall parents
    P += [
        _V(dict(**_c("teal"), trousers=(64, 60, 64), hair=_HAIRS[1], skin="warm"), A_CHILD,
           pose=("hurry",), acc=("reach_up",), height=0.62, bw=_BW_CHILD),
        _V(dict(**_c("wine"), trousers=(70, 56, 60), hair=_HAIRS[3], skin="ruddy"), A_CHILD,
           pose=("hurry",), acc=("reach_up",), height=0.6, bw=_BW_CHILD),
        _V(dict(**_c("sage"), trousers=(62, 64, 56), hair=_HAIRS[2], skin="fair"), A_CHILD,
           pose=("hurry",), height=0.64, bw=_BW_CHILD),
        _V(dict(**_c("slate"), sash=(186, 188, 196), hair=_HAIRS[0], skin="fair", hat="bun"),
           A_ROBE, pose=("stroll",), acc=("hand_hold", "topknot"), height=1.10, bw=_BW_STROLL),
        _V(dict(**_c("clay"), sash=(204, 178, 140), hair=_HAIRS[2], skin="warm", hat="cloth",
                hat_c=(170, 96, 80)), A_SKIRT, pose=("stroll",), acc=("hand_hold",),
           height=1.04, build=1.08, bw=_BW_MARKET),
    ]
    # WEATHER — rain umbrellas/hood (muted canopies) + parasol (clear)
    P += [
        _V(dict(**_c("slate"), trousers=(60, 62, 70), hair=_HAIRS[2], skin="warm",
                canopy=(176, 96, 92)), A_TUNIC, pose=("hurry", "swing_arm"),
           acc=("umbrella",), ww=_WW_RAIN),
        _V(dict(**_c("olive"), sash=(180, 160, 120), hair=_HAIRS[0], skin="fair", hat="bun",
                canopy=(150, 138, 102)), A_ROBE, pose=("stroll",), acc=("umbrella",), ww=_WW_RAIN),
        _V(dict(**_c("stone"), sash=(150, 120, 90), hair=_HAIRS[1], skin="fair", hat="bun",
                canopy=(96, 122, 162)), A_SKIRT, pose=("stroll",), acc=("umbrella",),
           build=1.05, ww=_WW_RAIN),
        _V(dict(**_c("teal"), sash=(70, 96, 92), hair=_HAIRS[3], skin="warm", hat="hood",
                hat_c=(72, 100, 96)), A_ROBE, pose=("hurry",), ww=_WW_RAIN),
        _V(dict(**_c("mauve"), sash=(190, 150, 140), hair=_HAIRS[3], skin="fair", hat="bun",
                pin=(196, 120, 124), canopy=(196, 156, 166)), A_ROBE, pose=("stroll",),
           acc=("parasol", "hairpin"), height=1.04, build=0.92, bw=_BW_STROLL),
    ]
    return P


fv.register("pedestrian", _build_pool())
