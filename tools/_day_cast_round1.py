"""Day-cast variety overhaul — round 1 candidate-sheet generator.

Second family in the sidewalk variety overhaul (after the 50-strong adult
pedestrian pool in game/ped_cast.py). The promenade today reuses ONE fixed
template per day-cast role — draw_kids, draw_old_man, and the vendor figures in
_scene_market/_scene_vendor — so the daytime market street (BEAT_MARKET..GOLDEN)
reads as clones. This explores three variety sub-pools, each over ONE shared
per-subfamily drawer (KIDS / ELDERS / VENDORS) consuming palette + pose/accessory
/attrs flags, exactly mirroring ped_cast's _draw_one + foreground_variants.Variant
model so the winners drop in as DATA rows under three new families.

Mirrors the constraints the shipped pedestrian family was held to:
- pure pygame.draw.* on a Surface, no numpy/gfxdraw/PIL, pygbag-safe.
- TINY on screen (FAR ~12-16px, NEAR ~1.5x); variety must live in the OUTLINE
  (body shape/height/stoop + outline-breaking accessories), since the downscale
  erases colour and interior detail first. Authored at native size, FAR drawn
  CRISP (no smoothscale — it just blurred the last family).
- Night cools toward (54,64,96), nothing self-lit, <=150 luma; nothing out-pops
  the gold coin / parrot.

Nothing here touches production game files; this is a review-sheet generator only.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── shared colour helpers (lifted from game/foreground_props) ──────────────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _retint(col, night):
    """Cool toward the night ground band — matches promenade._retint_person."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


SKIN = {
    "fair":  (236, 198, 156), "warm": (222, 178, 132), "tan": (200, 156, 112),
    "deep":  (168, 124, 86),  "ruddy": (228, 176, 150),
}


# ── descriptor mirroring foreground_variants.Variant ──────────────────────────

class V:
    """A subset of foreground_variants.Variant carrying just what the drawers
    read here. `palette` = colour roles, `pose`/`accessory` = flag sets, `attrs`
    = family scalars (height/build/stoop + sub-type). `label`/`flags_note` annotate
    the sheet only."""

    def __init__(self, palette, *, pose=(), acc=(), attrs=None, label="", note=""):
        self.palette = palette
        self.pose = frozenset(pose)
        self.accessory = frozenset(acc)
        self.attrs = dict(attrs or {})
        self.label = label
        self.note = note


# ════════════════════════════════════════════════════════════════════════════
# KIDS DRAWER — the smallest figures (~9-13px). Chibi: big head, stubby body.
# Variety lives in age/height, pose (run/squat/point/carry/piggyback), held prop,
# hair, outfit. attrs: age 0(toddler)..1(older child) -> height; pose flags carry
# the silhouette. Authored feet-on-base_y, facing left (scroll dir).
# ════════════════════════════════════════════════════════════════════════════

KID_H = 13


def draw_kid(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _retint(c, night)
    skin = pf(SKIN.get(P.get("skin", "warm"), SKIN["warm"]))
    skin_sh = _shade(skin, -26)
    shirt = pf(P["shirt"]); shirt_dk = pf(P.get("shirt_dk", _shade(P["shirt"], -42)))
    pants = pf(P.get("pants", _shade(shirt, -60)))
    hair = pf(P.get("hair", (60, 44, 34)))

    age = A.get("age", 0.6)                 # 0 toddler .. 1 older child
    height = 0.62 + 0.38 * age              # toddler short, older taller
    total = max(7, int(KID_H * height))
    head_r = max(2, int(total * (0.34 - 0.06 * age)))   # toddler = bigger head
    body_h = max(3, int(total * 0.32))
    body_w = max(3, int(total * 0.30))
    ground = int(base_y)
    body_bot = ground - max(2, int(total * 0.30))       # short legs
    body_y = body_bot - body_h
    hx = cx
    hy = body_y - head_r + 1

    squat = "squat" in v.pose
    run = "run" in v.pose
    carried = "carried" in v.pose
    gait = math.sin(t * (2.6 if run else 1.7))

    if carried:
        # Piggyback: the kid rides high on a stooped adult's back, legs splayed.
        body_y = ground - int(total * 1.4)
        body_bot = body_y + body_h
        hy = body_y - head_r + 1
        # adult carrier (simple bent back) drawn first
        ad = pf(P.get("carrier", (96, 84, 110)))
        ad_dk = _shade(ad, -40)
        a_w = max(4, int(KID_H * 0.46))
        pygame.draw.polygon(surf, ad, [
            (cx - a_w, ground), (cx + a_w, ground),
            (cx + a_w - 1, ground - int(KID_H * 0.9)),
            (cx - a_w + 2, ground - KID_H)])
        pygame.draw.circle(surf, pf(SKIN["tan"]), (cx - 1, ground - KID_H - 2), 3)
        pygame.draw.circle(surf, ad_dk, (cx - 1, ground - KID_H - 3), 3, 1)

    if squat:
        # Crouched playing: knees up, body compressed low to the deck.
        body_y = ground - body_h - 1
        body_bot = body_y + body_h
        hy = body_y - head_r + 1
        pygame.draw.ellipse(surf, shirt, (cx - body_w, body_y, body_w * 2, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (cx - body_w, body_y, body_w * 2, body_h + 1), 1)
        # bent knees as two stubs to the deck
        for sgn in (-1, 1):
            pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.5, body_bot),
                             (cx + sgn * body_w * 1.1, ground), 2)
    else:
        # Standing/running torso — rounded chibi ellipse.
        pygame.draw.ellipse(surf, shirt, (cx - body_w, body_y, body_w * 2, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (cx - body_w, body_y, body_w * 2, body_h + 1), 1)
        if not carried:
            swing = gait * body_w * (0.8 if run else 0.4)
            for sgn, sw in ((-1, swing), (1, -swing)):
                fx = cx + sgn * body_w * 0.4 + sw
                pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.4, body_bot),
                                 (fx, ground), 2)
        else:
            # dangling legs gripping the carrier
            for sgn in (-1, 1):
                pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.5, body_bot),
                                 (cx + sgn * body_w * 1.0, body_bot + 4), 2)

    # ── head + hair ──
    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (hx, body_y + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (38, 26, 20), (hx - head_r // 2, hy), max(1, head_r // 4))

    hairstyle = P.get("hair_style", "bowl")
    if hairstyle == "buns":           # two side buns (girl)
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(10), math.radians(170), max(1, head_r // 2))
        for sgn in (-1, 1):
            pygame.draw.circle(surf, hair, (hx + sgn * (head_r + 1), hy - head_r // 2), max(1, head_r // 2))
    elif hairstyle == "tuft":         # toddler top tuft
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(20), math.radians(160), max(1, head_r // 2))
        pygame.draw.circle(surf, hair, (hx, hy - head_r), max(1, head_r // 3))
    elif hairstyle == "cap":          # little cap
        cap = pf(P.get("cap", (210, 90, 80)))
        pygame.draw.circle(surf, cap, (hx, hy - head_r // 3), int(head_r * 1.05))
        pygame.draw.circle(surf, skin, (hx + head_r // 3, hy + head_r // 4), int(head_r * 0.7))
    else:                             # bowl cut
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), max(1, head_r // 2))

    # ── outline-breaking held props (the big silhouette differentiators) ──
    ax = cx - body_w * 0.6
    arm_y = body_y + 1
    if "point" in v.pose:
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y),
                         (cx - body_w * 1.7, arm_y - body_h * 0.3), 2)
    if "balloon" in v.accessory:
        bcol = pf(P.get("prop", (228, 84, 92)))
        sx2 = cx + body_w + 2
        pygame.draw.line(surf, (70, 64, 60), (cx + body_w * 0.3, arm_y), (sx2, hy - head_r * 3), 1)
        pygame.draw.circle(surf, bcol, (sx2, hy - head_r * 3 - 2), max(2, int(head_r * 1.2)))
        pygame.draw.circle(surf, _shade(bcol, 30), (sx2 - 1, hy - head_r * 3 - 3), max(1, head_r // 2))
    if "kite" in v.accessory:
        kcol = pf(P.get("prop", (240, 196, 70)))
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.3, arm_y - 2), 2)
        kx, ky = cx + body_w + 4, hy - head_r * 3
        pygame.draw.line(surf, (70, 64, 60), (cx - body_w * 1.3, arm_y - 2), (kx, ky), 1)
        pygame.draw.polygon(surf, kcol, [(kx, ky - 3), (kx + 3, ky), (kx, ky + 3), (kx - 3, ky)])
        pygame.draw.polygon(surf, _shade(kcol, -34), [(kx, ky - 3), (kx + 3, ky), (kx, ky + 3), (kx - 3, ky)], 1)
    if "stick" in v.accessory:
        scol = pf(P.get("prop", (150, 110, 64)))
        pygame.draw.line(surf, scol, (cx - body_w * 0.4, arm_y),
                         (cx - body_w * 2.4, arm_y - body_h * 0.6), 2)
    if "candy" in v.accessory:        # tanghulu / candied skewer — a red bobble on a stick
        ccol = pf(P.get("prop", (224, 60, 60)))
        sx2 = cx - body_w * 0.4
        pygame.draw.line(surf, (150, 120, 70), (sx2, arm_y), (sx2 - 1, hy - head_r * 2), 1)
        for k in range(3):
            pygame.draw.circle(surf, ccol, (int(sx2 - 1), int(hy - head_r * 2 + k * 3)), 2)


# ════════════════════════════════════════════════════════════════════════════
# ELDER DRAWER — robe/padded body, the OUTLINE built from stance + accessory.
# attrs: build, stoop, stance one of upright/stoop/hands_back/seated/taichi/birds.
# headwear bald/bun/cap; acc fan/cane/birdcage/teacup + beard. ~16-18px.
# ════════════════════════════════════════════════════════════════════════════

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
        # On a low stool — knees bent, torso compressed, a stool block beneath.
        stool = pf((120, 92, 60))
        sy = ground - leg_h
        pygame.draw.rect(surf, stool, (cx - body_w, sy, body_w * 2, leg_h))
        pygame.draw.rect(surf, _shade(stool, -28), (cx - body_w, sy, body_w * 2, leg_h), 1)
        torso_bot = sy
        torso_top = torso_bot - torso_h
        # knees out front
        for sgn in (-1, 1):
            pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.5, torso_bot),
                             (cx + sgn * body_w * 1.2, ground), max(2, body_w // 3))
    else:
        torso_bot = ground - leg_h
        torso_top = torso_bot - torso_h
        # legs / robe-hem feet
        if taichi:
            # wide horse stance — feet spread, knees bent
            for sgn in (-1, 1):
                pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.4, torso_bot),
                                 (cx + sgn * body_w * 1.5, ground), max(2, body_w // 3))
        else:
            gait = math.sin(t * 1.2)
            for sgn in (-1, 1):
                fx = cx + sgn * body_w * 0.3
                pygame.draw.line(surf, robe_dk, (cx + sgn * body_w * 0.3, torso_bot),
                                 (fx, ground), max(2, body_w // 3))

    torso_top += int(torso_h * 0.5 * stoop)
    head_cy = torso_top - head_r
    hx = cx + lean
    hy = head_cy

    # ── robe / padded torso (the silhouette mass) ──
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
        if stoop > 0.25:              # hunched upper-back hump
            pygame.draw.circle(surf, robe_dk, (cx - sh_w + lean + 1, torso_top + 1), max(1, body_w // 4))

    arm_y = torso_top + head_r // 2

    # ── stance-driven arms (strong outline cues) ──
    if taichi:
        # rounded "holding the ball" arms out front
        pygame.draw.line(surf, robe, (cx + lean, arm_y), (cx - body_w * 1.6, arm_y + torso_h * 0.3), max(2, body_w // 4))
        pygame.draw.line(surf, robe, (cx + lean, arm_y + head_r), (cx - body_w * 1.4, arm_y + torso_h * 0.7), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx - body_w * 1.6), int(arm_y + torso_h * 0.3)), max(1, body_w // 4))
    elif hands_back:
        # hands clasped behind — arms swept to the rear, contemplative
        pygame.draw.line(surf, robe, (cx + body_w * 0.6 + lean, arm_y),
                         (cx + body_w * 1.5 + lean, arm_y + torso_h * 0.5), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx + body_w * 1.5 + lean), int(arm_y + torso_h * 0.5)), max(1, body_w // 4))
    elif birds:
        # one arm extended low, palm out, scattering seed
        pygame.draw.line(surf, robe, (cx - body_w * 0.4 + lean, arm_y),
                         (cx - body_w * 1.8, arm_y + torso_h * 0.4), max(2, body_w // 4))
        pygame.draw.circle(surf, skin, (int(cx - body_w * 1.8), int(arm_y + torso_h * 0.4)), max(1, body_w // 4))
        # a couple of birds pecking near the leading foot
        for bx2, by2 in ((cx - body_w * 2.2, ground - 1), (cx - body_w * 1.4, ground)):
            pygame.draw.circle(surf, pf((90, 80, 70)), (int(bx2), int(by2)), 1)

    # ── head, neck, beard ──
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
    elif head == "cap":               # skullcap / felt cap
        col = pf(P.get("cap", (120, 96, 70)))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(surf, skin, (hx, hy + head_r // 4), int(head_r * 0.75))

    # ── handheld accessories (overhead/side outline-breakers) ──
    if "cane" in v.accessory:
        cane = pf(P.get("cane", (118, 82, 50)))
        tap = int(math.sin(t * 1.3))
        chx = cx + body_w * 1.4 + lean
        pygame.draw.line(surf, cane, (chx, arm_y), (chx + tap, ground), max(2, body_w // 6))
        pygame.draw.line(surf, cane, (chx, arm_y), (chx - 3, arm_y), max(2, body_w // 6))  # crook
        pygame.draw.line(surf, robe, (cx + body_w * 0.5 + lean, arm_y), (chx, arm_y), max(2, body_w // 5))
    if "fan" in v.accessory:
        fcol = pf(P.get("fan", (224, 212, 190)))
        fx = cx - body_w * 1.5 + lean; fy = arm_y - 1
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (fx, fy), max(2, body_w // 5))
        # an open folding fan as a small sector
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
        pygame.draw.circle(surf, pf((110, 150, 90)), (cg.centerx, cg.centery + 1), 1)  # bird
    if "teacup" in v.accessory:
        tc = pf(P.get("tea", (228, 222, 210)))
        tx = cx - body_w * 1.2 + lean; ty = arm_y + 1
        pygame.draw.line(surf, robe, (cx - body_w * 0.3 + lean, arm_y), (tx, ty), max(2, body_w // 5))
        pygame.draw.ellipse(surf, tc, (tx - 2, ty - 1, 4, 3))
        pygame.draw.ellipse(surf, _shade(tc, -34), (tx - 2, ty - 1, 4, 3), 1)


# ════════════════════════════════════════════════════════════════════════════
# VENDOR DRAWER — STANDING/working cast. Stands, often cropped at the waist by a
# counter, so the read must hold from the chest up. attrs: build, height, crop
# (False=full / True=waist-cropped behind counter). pose one of: call/weigh/fan/
# ladle/stack/sign. apron + rolled sleeves + conical/cloth hat + shoulder towel.
# ════════════════════════════════════════════════════════════════════════════

VEND_H = 17


def draw_vendor(surf, cx, base_y, v, night, t, crop_y=None):
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

    # legs
    for sgn in (-1, 1):
        pygame.draw.line(surf, pants, (cx + sgn * body_w * 0.4, torso_bot),
                         (cx + sgn * body_w * 0.4, ground), max(2, body_w // 3))

    # ── torso (tunic) + apron front ──
    r = pygame.Rect(cx - body_w, torso_top, body_w * 2, torso_h)
    pygame.draw.rect(surf, shirt, r, border_radius=max(2, body_w // 4))
    pygame.draw.rect(surf, shirt_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 4))
    # apron — a paler panel down the front, the vendor's defining mark
    apr = pygame.Rect(cx - body_w * 0.7, torso_top + head_r, body_w * 1.4, torso_h - head_r // 2)
    pygame.draw.rect(surf, apron, apr)
    pygame.draw.rect(surf, apron_dk, apr, 1)
    pygame.draw.line(surf, apron_dk, (cx - body_w * 0.5, torso_top + 1), (apr.left + 1, apr.top), 1)
    pygame.draw.line(surf, apron_dk, (cx + body_w * 0.5, torso_top + 1), (apr.right - 1, apr.top), 1)
    # rolled sleeves — thicker upper arm stub on the working side
    if "rolled" in v.accessory:
        pygame.draw.line(surf, _shade(shirt, 14), (cx - body_w * 0.6, arm_y), (cx - body_w, arm_y + 2), max(2, body_w // 3))
    if "towel" in v.accessory:        # towel over the shoulder
        tw = pf(P.get("towel", (220, 214, 200)))
        pygame.draw.line(surf, tw, (cx + body_w * 0.3, torso_top - 1), (cx + body_w * 0.9, torso_top + torso_h * 0.4), max(2, body_w // 4))

    # ── pose-driven working arms (outline-breakers) ──
    if pose == "call":                # one hand cupped to the mouth, calling out
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (hx - head_r, hy + head_r // 2), max(2, body_w // 4))
    elif pose == "weigh":             # a hand-scale dangling from a raised arm
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.5, arm_y - 2), max(2, body_w // 4))
        sx2 = cx - body_w * 1.5
        pygame.draw.line(surf, pf((120, 96, 60)), (sx2, arm_y - 2), (sx2, arm_y - 5), 1)  # beam
        for ox in (-3, 3):
            pygame.draw.line(surf, (90, 80, 64), (sx2 + ox, arm_y - 4), (sx2 + ox, arm_y), 1)
            pygame.draw.arc(surf, pf((150, 120, 70)), (sx2 + ox - 2, arm_y - 1, 4, 3), math.radians(180), math.radians(360), 1)
    elif pose == "fan":               # fanning a grill — a paddle fan over coals
        fy = arm_y + int(math.sin(t * 6) * 1)
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.4, fy + 2), max(2, body_w // 4))
        pygame.draw.rect(surf, pf((200, 180, 140)), (int(cx - body_w * 1.7), int(fy), 4, 5))
        pygame.draw.rect(surf, pf((140, 110, 70)), (int(cx - body_w * 1.7), int(fy), 4, 5), 1)
    elif pose == "ladle":             # ladling from a pot — arm dipped low
        pygame.draw.line(surf, shirt, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.4, arm_y + torso_h * 0.5), max(2, body_w // 4))
        lx = cx - body_w * 1.4
        pygame.draw.line(surf, pf((150, 120, 70)), (lx, arm_y + torso_h * 0.5), (lx - 2, arm_y + torso_h * 0.8), 1)
        pygame.draw.circle(surf, pf((180, 150, 100)), (int(lx - 2), int(arm_y + torso_h * 0.8)), 1)
    elif pose == "stack":             # both arms up balancing stacked baskets
        for sgn in (-1, 1):
            pygame.draw.line(surf, shirt, (cx + sgn * body_w * 0.5, arm_y), (cx + sgn * body_w * 0.9, hy), max(2, body_w // 4))
        bk = pf(P.get("basket", (176, 132, 78)))
        for k in range(3):
            br = pygame.Rect(int(cx - body_w * 0.9), int(hy - head_r * 1.3 - k * 4), int(body_w * 1.8), 4)
            pygame.draw.ellipse(surf, bk, br)
            pygame.draw.ellipse(surf, _shade(bk, -30), br, 1)
    elif pose == "sign":              # holding a tall sign-board / skewer bundle
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, arm_y), (cx - body_w * 1.2, arm_y - 1), max(2, body_w // 4))
        if "skewers" in v.accessory:
            for k in range(4):
                pygame.draw.line(surf, pf((150, 120, 70)), (cx - body_w * 1.2 + k, arm_y - 1),
                                 (cx - body_w * 1.6 + k, arm_y - head_r * 2), 1)
                pygame.draw.circle(surf, pf((180, 90, 60)), (int(cx - body_w * 1.6 + k), int(arm_y - head_r * 2)), 1)
        else:
            sg = pf(P.get("sign", (200, 70, 64)))
            pygame.draw.line(surf, pf((120, 90, 60)), (cx - body_w * 1.2, arm_y - 1), (cx - body_w * 1.2, hy - head_r * 2), 1)
            sr = pygame.Rect(int(cx - body_w * 1.9), int(hy - head_r * 2.6), int(body_w * 1.6), int(head_r * 1.8))
            pygame.draw.rect(surf, sg, sr)
            pygame.draw.rect(surf, _shade(sg, -34), sr, 1)
            pygame.draw.line(surf, _shade(sg, 40), (sr.left + 1, sr.centery), (sr.right - 1, sr.centery), 1)

    # ── head + neck ──
    pygame.draw.line(surf, skin_sh, (hx, hy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (hx, hy), head_r)
    pygame.draw.circle(surf, skin_sh, (hx, hy), head_r, 1)
    pygame.draw.circle(surf, (40, 28, 22), (hx - head_r // 2, hy - head_r // 6), max(1, head_r // 4))

    hat = P.get("hat", "none")
    if hat == "conical":
        col = pf(P.get("hat_c", (198, 162, 96))); bw = int(head_r * 2.4)
        pygame.draw.polygon(surf, col, [(hx - bw, hy - head_r * 0.1), (hx, hy - head_r * 1.9), (hx + bw, hy - head_r * 0.1)])
        pygame.draw.polygon(surf, _shade(col, -34), [(hx - bw, hy - head_r * 0.1), (hx, hy - head_r * 1.9), (hx + bw, hy - head_r * 0.1)], 1)
    elif hat == "cloth":              # cloth wrap / headscarf
        col = pf(P.get("hat_c", (180, 88, 78)))
        pygame.draw.circle(surf, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(surf, skin, (hx, hy + head_r // 4), int(head_r * 0.72))
    elif hat == "cap":               # small worker cap
        col = pf(P.get("hat_c", (120, 100, 76)))
        cap = pygame.Rect(hx - head_r, hy - int(head_r * 1.5), head_r * 2, int(head_r * 1.3))
        pygame.draw.ellipse(surf, col, cap)
        pygame.draw.line(surf, _shade(col, -24), (hx - head_r, hy - head_r // 2), (hx - head_r - 2, hy - head_r // 3), 2)  # brim
    else:
        pygame.draw.circle(surf, hair, (hx, hy - head_r // 3), head_r)
        pygame.draw.arc(surf, hair, (hx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), max(1, head_r // 2))


# ════════════════════════════════════════════════════════════════════════════
# THE THREE SUB-POOLS — each a variety set over its shared drawer.
# ════════════════════════════════════════════════════════════════════════════

KIDS = [
    V(dict(shirt=(235, 95, 90), pants=(74, 60, 52), hair=(58, 44, 36), hair_style="tuft", skin="warm"),
      pose=("run",), attrs=dict(age=0.05), label="K1 toddler run",
      note="roles: shirt+pants+hair | attrs: age0.05(h0.64) | pose: run | hair_style:tuft"),
    V(dict(shirt=(90, 165, 220), pants=(58, 52, 56), hair=(46, 36, 30), hair_style="bowl", skin="fair", prop=(240, 196, 70)),
      pose=("run",), acc=("kite",), attrs=dict(age=0.9), label="K2 kite run",
      note="roles: shirt+pants+hair+prop(kite) | attrs: age0.9(h0.96) | pose: run | acc: kite"),
    V(dict(shirt=(250, 200, 70), pants=(70, 56, 48), hair=(40, 32, 28), hair_style="bowl", skin="tan"),
      pose=("squat",), attrs=dict(age=0.55), label="K3 squat play",
      note="roles: shirt+pants+hair | attrs: age0.55(h0.83) | pose: squat | (playing low)"),
    V(dict(shirt=(120, 200, 130), pants=(64, 58, 50), hair=(50, 40, 32), hair_style="buns", skin="warm", prop=(228, 84, 92)),
      pose=("point",), acc=("balloon",), attrs=dict(age=0.7), label="K4 balloon girl",
      note="roles: shirt+pants+hair+prop(balloon) | attrs: age0.7(h0.89) | pose: point | acc: balloon | hair_style:buns"),
    V(dict(shirt=(220, 130, 200), pants=(70, 56, 60), hair=(44, 34, 28), hair_style="cap", skin="ruddy", cap=(210, 90, 80), prop=(224, 60, 60)),
      acc=("candy",), attrs=dict(age=0.45), label="K5 candy + cap",
      note="roles: shirt+pants+hair+cap+prop(candy) | attrs: age0.45(h0.79) | acc: candy | hair_style:cap"),
    V(dict(shirt=(110, 130, 235), pants=(60, 54, 58), hair=(54, 42, 34), hair_style="bowl", skin="warm", carrier=(96, 84, 110)),
      pose=("carried",), attrs=dict(age=0.2), label="K6 piggyback",
      note="roles: shirt+pants+hair+carrier | attrs: age0.2(h0.70) | pose: carried (rides adult back)"),
    V(dict(shirt=(240, 150, 70), pants=(66, 56, 48), hair=(40, 32, 28), hair_style="bowl", skin="deep", prop=(150, 110, 64)),
      pose=("run",), acc=("stick",), attrs=dict(age=0.85), label="K7 stick chase",
      note="roles: shirt+pants+hair+prop(stick) | attrs: age0.85(h0.94) | pose: run | acc: stick"),
]

ELDERS = [
    V(dict(robe=(92, 72, 108), robe_dk=(58, 44, 74), sash=(196, 180, 150), hair=(212, 210, 202), skin="fair", head="bald", cane=(118, 82, 50)),
      acc=("beard", "cane"), attrs=dict(stance="stoop", stoop=0.46, height=0.92, build=0.95), label="E1 stoop+cane",
      note="roles: robe+sash+hair+cane | attrs: stance:stoop stoop0.46 | acc: beard,cane | head:bald"),
    V(dict(robe=(86, 96, 140), robe_dk=(52, 60, 100), sash=(200, 188, 150), hair=(208, 206, 198), skin="warm", head="bun"),
      acc=("fan", "beard"), attrs=dict(stance="taichi", height=1.04, build=1.0, fan=(224, 212, 190)),
      label="E2 tai-chi", note="roles: robe+sash+hair+fan | attrs: stance:taichi | acc: fan,beard | head:bun"),
    V(dict(robe=(110, 134, 112), robe_dk=(70, 92, 76), sash=(206, 180, 140), hair=(204, 202, 196), skin="tan", head="cap", cap=(120, 96, 70)),
      acc=("birdcage",), attrs=dict(stance="upright", height=1.0, build=1.05, cage=(150, 116, 70)),
      label="E3 birdcage", note="roles: robe+sash+hair+cap+cage | attrs: stance:upright | acc: birdcage | head:cap"),
    V(dict(robe=(128, 124, 112), robe_dk=(84, 82, 72), sash=(186, 188, 196), hair=(210, 208, 200), skin="warm", head="bald"),
      acc=("beard",), attrs=dict(stance="hands_back", stoop=0.18, height=1.02, build=0.98),
      label="E4 hands-behind", note="roles: robe+sash+hair | attrs: stance:hands_back stoop0.18 | acc: beard | head:bald"),
    V(dict(robe=(118, 96, 84), robe_dk=(74, 58, 50), fur=(224, 216, 202), sash=(196, 170, 130), hair=(206, 204, 196), skin="ruddy", head="cap", cap=(110, 90, 66)),
      acc=("teacup", "beard"), attrs=dict(stance="seated", height=0.94, build=1.15, padded=True, tea=(228, 222, 210)),
      label="E5 seated+tea", note="roles: robe+fur+sash+hair+cap+tea | attrs: stance:seated padded | acc: teacup,beard"),
    V(dict(robe=(104, 80, 116), robe_dk=(66, 48, 78), sash=(208, 160, 140), hair=(206, 204, 198), skin="deep", head="bun"),
      acc=("birds",) if False else (), attrs=dict(stance="birds", height=0.98, build=1.0),
      label="E6 feeding birds", note="roles: robe+sash+hair | attrs: stance:birds | (palm out, birds peck)"),
    V(dict(robe=(78, 124, 124), robe_dk=(48, 84, 84), fur=(220, 214, 200), sash=(200, 188, 150), hair=(208, 206, 198), skin="fair", head="cap", cap=(86, 100, 138)),
      acc=("cane", "beard"), attrs=dict(stance="upright", stoop=0.1, height=1.0, build=1.18, padded=True, cane=(116, 80, 48)),
      label="E7 padded+cane", note="roles: robe(padded)+fur+sash+hair+cap+cane | attrs: padded build1.18 | acc: cane,beard"),
]

VENDORS = [
    V(dict(shirt=(150, 86, 70), shirt_dk=(104, 56, 46), apron=(214, 200, 178), pants=(70, 60, 52), hair=(46, 36, 30), skin="tan", hat="conical", hat_c=(196, 158, 92)),
      acc=("rolled", "towel"), attrs=dict(pose="call", height=1.0, build=1.08), label="V1 calling",
      note="roles: shirt+apron+pants+hair+hat_c | attrs: pose:call | acc: rolled,towel | hat:conical"),
    V(dict(shirt=(78, 124, 124), shirt_dk=(48, 84, 84), apron=(206, 196, 176), pants=(66, 58, 50), hair=(40, 32, 28), skin="warm", hat="cloth", hat_c=(170, 96, 80)),
      attrs=dict(pose="weigh", height=1.0, build=1.05), label="V2 weighing",
      note="roles: shirt+apron+pants+hair+hat_c | attrs: pose:weigh | hat:cloth (hand-scale)"),
    V(dict(shirt=(158, 128, 78), shirt_dk=(108, 84, 50), apron=(210, 196, 172), pants=(64, 58, 48), hair=(50, 40, 32), skin="deep", hat="cap", hat_c=(120, 100, 76), towel=(220, 214, 200)),
      acc=("rolled", "towel"), attrs=dict(pose="fan", height=0.98, build=1.12), label="V3 fanning grill",
      note="roles: shirt+apron+pants+hair+hat_c+towel | attrs: pose:fan | acc: rolled,towel | hat:cap"),
    V(dict(shirt=(118, 116, 80), shirt_dk=(78, 78, 52), apron=(204, 192, 170), pants=(60, 56, 46), hair=(44, 34, 28), skin="ruddy", hat="cloth", hat_c=(150, 110, 96)),
      acc=("rolled",), attrs=dict(pose="ladle", height=1.0, build=1.06), label="V4 ladling",
      note="roles: shirt+apron+pants+hair+hat_c | attrs: pose:ladle | acc: rolled | hat:cloth"),
    V(dict(shirt=(100, 108, 124), shirt_dk=(64, 72, 90), apron=(200, 192, 178), pants=(58, 60, 70), hair=(54, 42, 34), skin="warm", hat="conical", hat_c=(184, 150, 88), basket=(176, 132, 78)),
      attrs=dict(pose="stack", height=1.04, build=1.0), label="V5 stacking baskets",
      note="roles: shirt+apron+pants+hair+hat_c+basket | attrs: pose:stack | hat:conical"),
    V(dict(shirt=(168, 120, 84), shirt_dk=(114, 78, 54), apron=(208, 198, 178), pants=(70, 60, 50), hair=(40, 32, 28), skin="tan", hat="cap", hat_c=(110, 96, 74)),
      acc=("skewers",), attrs=dict(pose="sign", height=1.0, build=1.05), label="V6 skewers",
      note="roles: shirt+apron+pants+hair+hat_c | attrs: pose:sign | acc: skewers | hat:cap"),
    V(dict(shirt=(140, 104, 130), shirt_dk=(94, 66, 90), apron=(206, 194, 174), pants=(64, 56, 58), hair=(50, 40, 32), skin="fair", hat="cloth", hat_c=(150, 100, 84), sign=(200, 70, 64)),
      attrs=dict(pose="sign", height=1.0, build=1.04), label="V7 sign-board",
      note="roles: shirt+apron+pants+hair+hat_c+sign | attrs: pose:sign | hat:cloth (price board)"),
]


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER
# ════════════════════════════════════════════════════════════════════════════

DAY = dict(sky_top=(70, 150, 235))
NIGHT = dict(sky_top=(10, 16, 44))
BG_DAY = (150, 140, 118)        # warm sandstone deck
BG_NIGHT = (40, 46, 70)

DRAWERS = {"kid": draw_kid, "elder": draw_elder, "vendor": draw_vendor}
SUBFAM_H = {"kid": KID_H, "elder": ELDER_H, "vendor": VEND_H}


def _draw_at(fam, surf, cx, base_y, v, night, t):
    DRAWERS[fam](surf, cx, base_y, v, night, t)


def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=(228, 224, 214), bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _gold_coin(surf, cx, cy, r=8):
    """A brightness yardstick — the in-game gold coin. Nothing in the cast must
    out-pop this."""
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, (255, 232, 150))):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


def _figure_cell(parent, fam, v, x, y, w, h, night, t):
    """One annotated cell: FAR true-size + NEAR true-size + a 4x zoom inset, on a
    day or night deck, with the per-figure flag note."""
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    # subtle ground line
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 16
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    # FAR (1.0x authored) and NEAR (1.5x) on a scratch tall enough that overhead
    # props (kite/balloon/stacked baskets/fan) are not clipped, then crisp-scaled.
    NW, NH = 44, 56
    nat = pygame.Surface((NW, NH), pygame.SRCALPHA)
    _draw_at(fam, nat, NW // 2, NH - 4, v, night, t)
    crop = nat.subsurface(pygame.Rect(0, 0, NW, NH))

    far_x = 18
    cell.blit(crop, (far_x - NW // 2, base - NH + 4))
    _text(cell, "FAR 1x", far_x - 14, base + 1, 8, _shade(bg, 60))

    near = pygame.transform.scale(crop, (int(NW * 1.5), int(NH * 1.5)))   # nearest, crisp
    near_x = 62
    cell.blit(near, (near_x - int(NW * 0.75), base - int(NH * 1.5) + 6))
    _text(cell, "NEAR 1.5x", near_x - 22, base + 1, 8, _shade(bg, 60))

    # zoom inset (~3x) framed at right
    zoom = pygame.transform.scale(crop, (int(NW * 3.4), int(NH * 3.4)))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 6
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)

    # label + note
    _text(cell, v.label, 6, 4, 12, (240, 236, 226), bold=True)
    # wrap the note
    note = v.note
    fnt = _font(9, False)
    words = note.split(" ")
    line = ""; yy = 22
    wrap_w = w - int(44 * 3.4) - 18
    for wd in words:
        test = (line + " " + wd).strip()
        if fnt.size(test)[0] > wrap_w:
            cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy)); yy += 11; line = wd
        else:
            line = test
    if line:
        cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy))

    parent.blit(cell, (x, y))
    pygame.draw.rect(parent, (70, 74, 90), (x, y, w, h), 1)


def render():
    t = 0.55
    W = 1100
    pad = 12
    sections = []

    title_h = 54
    # ── A. TRUE-SIZE BAND grouped by sub-pool (day) ──
    band_h = 120
    band_rows = [("KIDS  (~9-13px)", "kid", KIDS),
                 ("ELDERS  (~16-17px)", "elder", ELDERS),
                 ("VENDORS / WORKERS  (~16-17px, design for waist-crop)", "vendor", VENDORS)]
    bandA_h = 30 + len(band_rows) * band_h

    # ── B. PER-FIGURE detail cells (day + night), 3 cols ──
    cell_w = (W - pad * 4) // 3
    cell_h = 200
    all_figs = [("kid", v) for v in KIDS] + [("elder", v) for v in ELDERS] + [("vendor", v) for v in VENDORS]
    n_rows = (len(all_figs) + 2) // 3
    # each fig gets a day cell and a night cell stacked -> we lay day grid then night grid
    detail_h = 30 + n_rows * (cell_h + 4)
    detailB_h = 30 + 2 * detail_h

    # ── C. ON-STREET COMPOSITE strip (day + night) ──
    strip_h = 96
    compC_h = 30 + 2 * (strip_h + 6)

    total_h = title_h + bandA_h + detailB_h + compC_h + pad * 5
    sheet = pygame.Surface((W, total_h))
    sheet.fill((26, 28, 38))

    y = pad
    _text(sheet, "SKYBIT PROMENADE — DAY-CAST VARIETY (round 1): KIDS · ELDERS · VENDORS/WORKERS", pad, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "3 sub-pools, each ONE shared drawer over palette + pose/accessory/attrs flags (mirrors ped_cast). FAR crisp (no smoothscale). Night cools to (54,64,96), <=150 luma — nothing out-pops the gold coin.", pad, y, 10, (188, 186, 200))
    y += title_h - 22

    # ── SECTION A ──
    _text(sheet, "A.  TRUE-SIZE BAND — grouped by sub-pool (day deck)", pad, y, 13, (240, 220, 150), bold=True)
    y += 24
    for caption, fam, pool in band_rows:
        row = pygame.Surface((W - pad * 2, band_h - 6))
        row.fill(BG_DAY)
        deck = _mix(BG_DAY, (0, 0, 0), 0.18)
        base = band_h - 6 - 26
        pygame.draw.rect(row, deck, (0, base, W - pad * 2, 26))
        pygame.draw.line(row, _shade(BG_DAY, 26), (0, base), (W - pad * 2, base), 1)
        _gold_coin(row, W - pad * 2 - 24, base - 30)
        _text(row, "coin ref", W - pad * 2 - 44, base + 2, 8, _shade(BG_DAY, 50))
        _text(row, caption, 6, 4, 11, (60, 50, 40), bold=True)
        spacing = (W - pad * 2 - 80) // len(pool)
        for i, v in enumerate(pool):
            cx = 40 + i * spacing
            _draw_at(fam, row, cx, base, v, 0.0, t)
            _text(row, v.label.split(" ")[0], cx - 8, base + 2, 8, (70, 58, 46))
        sheet.blit(row, (pad, y))
        pygame.draw.rect(sheet, (70, 74, 90), (pad, y, W - pad * 2, band_h - 6), 1)
        y += band_h
    y += 8

    # ── SECTION B (day grid then night grid) ──
    _text(sheet, "B.  PER-FIGURE — FAR 1x · NEAR 1.5x · 4x zoom inset · flag annotation  (DAY rows then NIGHT rows)", pad, y, 13, (240, 220, 150), bold=True)
    y += 22
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT" if is_night else "DAY", pad, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 14
        for r in range(n_rows):
            for c in range(3):
                idx = r * 3 + c
                if idx >= len(all_figs):
                    break
                fam, v = all_figs[idx]
                cx = pad + c * (cell_w + pad)
                _figure_cell(sheet, fam, v, cx, y, cell_w, cell_h, night, t)
            y += cell_h + 4
        y += 8

    # ── SECTION C — on-street composite ──
    _text(sheet, "C.  ON-STREET COMPOSITE — all three sub-pools mixed at true size, with the gold-coin brightness reference", pad, y, 13, (240, 220, 150), bold=True)
    y += 22
    # a representative market-row mix
    mix = [("vendor", VENDORS[0]), ("kid", KIDS[1]), ("elder", ELDERS[1]),
           ("vendor", VENDORS[2]), ("kid", KIDS[3]), ("vendor", VENDORS[4]),
           ("elder", ELDERS[2]), ("kid", KIDS[5]), ("elder", ELDERS[0]),
           ("vendor", VENDORS[5]), ("kid", KIDS[6]), ("elder", ELDERS[4]),
           ("vendor", VENDORS[3]), ("kid", KIDS[2]), ("elder", ELDERS[5])]
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        bg = BG_NIGHT if is_night else BG_DAY
        strip = pygame.Surface((W - pad * 2, strip_h))
        strip.fill(bg)
        deck = _mix(bg, (0, 0, 0), 0.2)
        base = strip_h - 22
        # a faint counter line behind so some vendors read as cropped at the waist
        counter_y = base - 22
        pygame.draw.rect(strip, _mix(bg, (110, 84, 54), 0.5 if not is_night else 0.3), (0, counter_y, W - pad * 2, 3))
        pygame.draw.rect(strip, deck, (0, base, W - pad * 2, strip_h - base))
        pygame.draw.line(strip, _shade(bg, 24), (0, base), (W - pad * 2, base), 1)
        spacing = (W - pad * 2 - 40) // len(mix)
        for i, (fam, v) in enumerate(mix):
            cx = 26 + i * spacing
            # stagger feet a touch for depth
            by = base - (i % 3)
            _draw_at(fam, strip, cx, by, v, night, t)
        _gold_coin(strip, W - pad * 2 - 18, 22)
        _text(strip, "coin ref", W - pad * 2 - 44, 34, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9, (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (pad, y))
        pygame.draw.rect(sheet, (70, 74, 90), (pad, y, W - pad * 2, strip_h), 1)
        y += strip_h + 6

    out = "/home/user/skybit/docs/sidewalk_overhaul/day_cast/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    render()
