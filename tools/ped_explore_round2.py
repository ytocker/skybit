"""SCRATCH (exploration only — not imported by the game).

Round-2 variety pool for the promenade ADULT PEDESTRIANS, scaled to FIFTY people.

The pool is built data-driven: ~9 SILHOUETTE-DISTINCT body archetypes (the
readable variety) × palette sets × pose/accessory flags (within-class diversity)
over ONE richer shared body drawer. That is exactly the production model — adding
a person is a Variant data row (palette roles + pose/accessory/shape flags), never
a bespoke function.

Two things this round fixes over round 1:
  * DOWNSCALE — at FAR ~14px a smoothscale rounds every figure into the same soft
    cone and erases the silhouette. So FAR is baked CRISP (nearest, smooth=False,
    matching foreground_sprite's `smooth=` flag) and only NEAR ~22px gets a light
    smoothscale. Variety therefore lives in the OUTLINE, which the downscale keeps.
  * SILHOUETTE — body-shape flags (narrow/wide-skirt/boxy/stooped/short) + a
    height-scale flag + outline-BREAKER accessories (held away from the body,
    overhead, or changing the hat) so figures stay distinct after the downscale,
    when colour and interior surface detail are the first things to vanish.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

# ── palette helpers (mirror foreground_props so explorations match the game) ──

def _clamp(c):
    return (max(0, min(255, int(c[0]))), max(0, min(255, int(c[1]))), max(0, min(255, int(c[2]))))

def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return _clamp((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t))

def _shade(c, d):
    return _clamp((c[0] + d, c[1] + d, c[2] + d))

def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

NIGHT_GLOW_CAP = 150

def _retint_person(col, night):
    """Cool clothing toward the night ground band (matches the live _retint_person)."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


SKIN_TONES = {
    "fair":   (236, 198, 156),
    "warm":   (222, 178, 132),
    "tan":    (200, 156, 112),
    "deep":   (168, 124, 86),
    "ruddy":  (228, 176, 150),
}


# ── Variant descriptor (mirrors game.foreground_variants.Variant in spirit) ───
# arch = which SILHOUETTE archetype body-shape to draw (the outline-distinct
# class). palette = named colour roles. pose/acc = flag sets toggling code paths.
# height/stoop = the figure-shape modifiers the AD asked for. This whole object
# maps 1:1 onto a foreground_variants.Variant row at integration.

class V:
    def __init__(self, name, arch, palette, pose=(), acc=(),
                 height=1.0, stoop=0.0, build=1.0, roles=""):
        self.name = name
        self.arch = arch
        self.palette = palette
        self.pose = set(pose)
        self.acc = set(acc)
        self.height = height    # 0.85 short youth · 1.0 · 1.1 tall
        self.stoop = stoop      # 0 upright · 0.3 hunch · 0.5 deep elder hunch
        self.build = build      # torso width multiplier (slim..stout)
        self.roles = roles


# ── the SHARED richer body drawer ─────────────────────────────────────────────
# Authored in a render box at ~3x the on-screen footprint, feet at the bottom
# edge, facing right (scroll direction). `arch` picks the body SILHOUETTE; flags
# layer palette/accessory variety on top. Everything reads off the Variant so a
# new person is a data row.

# Archetype keys (the ~9 outline-distinct silhouette classes).
A_ROBE      = "robe"        # narrow straight robe (scholar / lady walker)
A_SKIRT     = "skirt"       # wide A-line skirted robe (matron / merchant)
A_TUNIC     = "tunic"       # short tunic + trousers (porter / youth, slim)
A_PADDED    = "padded"      # boxy bulky padded winter coat (snow figure)
A_STOOP     = "stoop"       # hunched cane-walker elder (deeply stooped)
A_POLE      = "pole"        # carrying-pole vendor (biandan over shoulder)
A_YOKE      = "yoke"        # shoulder-yoke porter (two hanging loads)
A_HEADLOAD  = "headload"    # flat tray/box balanced on head
A_CHILD     = "child"       # small child (pairs with a tall parent)


def _body_geom(sh, v):
    """Canonical vertical bands scaled by height. Returns key y/sizes."""
    total_h = int(sh * 0.90 * v.height)
    head_r = max(4, int(total_h * 0.135))
    torso_h = int(total_h * 0.44)
    leg_h = max(2, total_h - torso_h - head_r * 2)
    return total_h, head_r, torso_h, leg_h


def _legs(scratch, cx, body_w, torso_bot, ground, gait, hurry, col_leg, col_foot, hidden):
    swing = gait * body_w * (0.55 if hurry else 0.30)
    for sgn, sw_ in ((-1, swing), (1, -swing)):
        foot_x = cx + sgn * body_w * 0.20 + sw_ * 0.5
        if hidden:
            pygame.draw.line(scratch, col_leg, (cx + sgn * body_w * 0.20, torso_bot),
                             (foot_x, ground), max(2, body_w // 4))
        else:
            pygame.draw.line(scratch, col_leg, (cx + sgn * body_w * 0.20, torso_bot - body_w * 0.2),
                             (foot_x, ground), max(2, body_w // 3))
            pygame.draw.line(scratch, col_foot, (foot_x - 1, ground), (foot_x + 2, ground),
                             max(2, body_w // 3))


def draw_person(scratch, v, night, t):
    sw, sh = scratch.get_size()
    P = v.palette
    pal = lambda c: _retint_person(c, night)

    skin = pal(SKIN_TONES.get(P.get("skin", "warm"), SKIN_TONES["warm"]))
    skin_sh = _shade(skin, -28)
    coat = pal(P["coat"])
    coat_dk = pal(P.get("coat_dk", _shade(P["coat"], -42)))
    coat_lt = _shade(coat, 16)
    trim = pal(P.get("trim", _shade(P["coat"], 28)))
    hair = pal(P.get("hair", (58, 42, 34)))
    hair_dk = _shade(hair, -22)
    sash = pal(P.get("sash", trim))
    trousers = pal(P.get("trousers", coat_dk))

    cx = sw // 2
    ground = sh - 2
    total_h, head_r, torso_h, leg_h = _body_geom(sh, v)
    body_w = int(total_h * 0.27 * v.build)

    # Stoop pitches the upper body forward and drops the head — the elder cue that
    # survives downscale because it changes the whole outline, not a surface mark.
    stoop = v.stoop
    head_cy = ground - leg_h - torso_h - head_r
    torso_top = head_cy + head_r
    torso_bot = torso_top + torso_h

    hurry = "hurry" in v.pose
    hz = 2.6 if hurry else 1.5
    gait = math.sin(t * hz)
    lean = int(body_w * (0.30 if hurry else 0.12))
    lean += int(body_w * 1.6 * stoop)        # stoop adds a strong forward pitch
    bob = -abs(gait) * (total_h * 0.03)
    head_cy += int(bob) + int(torso_h * 0.55 * stoop)
    torso_top += int(bob)

    arch = v.arch
    arm_y = torso_top + int(head_r * 0.7)
    hx = cx + lean
    hy = head_cy

    # ── LEGS (behind torso/hem) ──────────────────────────────────────────────
    robe_like = arch in (A_ROBE, A_SKIRT, A_STOOP)
    if arch != A_CHILD:
        _legs(scratch, cx, body_w, torso_bot, ground, gait, hurry,
              coat_dk if robe_like else trousers,
              _shade(coat_dk if robe_like else trousers, -30), robe_like)
    else:
        # stubby kid legs, wider stance
        for sgn in (-1, 1):
            fx = cx + sgn * body_w * 0.4 + gait * body_w * 0.4 * sgn
            pygame.draw.line(scratch, trousers, (cx + sgn * body_w * 0.3, torso_bot),
                             (fx, ground), max(2, body_w // 2))

    # ── TORSO per ARCHETYPE — the silhouette-defining shape ──────────────────
    if arch == A_ROBE:
        # NARROW STRAIGHT robe: near-vertical sides, slim — reads tall & lean.
        sh_w = int(body_w * 0.70)
        hem_w = int(body_w * 0.82)
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(scratch, coat, pts)
        pygame.draw.polygon(scratch, coat_dk, pts, max(1, body_w // 8))
        pygame.draw.line(scratch, coat_dk, (cx + lean // 2, torso_top + head_r // 2),
                         (cx, pts[3][1]), max(1, body_w // 10))
        sy = torso_top + torso_h // 2
        pygame.draw.line(scratch, sash, (cx - sh_w, sy), (cx + sh_w, sy), max(2, body_w // 5))

    elif arch in (A_SKIRT, A_STOOP):
        # WIDE A-LINE skirted robe: narrow shoulders flaring to a broad hem — a
        # bell silhouette that can never be confused with the narrow robe.
        sh_w = int(body_w * 0.74)
        hem_w = int(body_w * 1.45)
        bot = ground if arch == A_STOOP else torso_bot
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, bot), (cx - hem_w, bot)]
        pygame.draw.polygon(scratch, coat, pts)
        pygame.draw.polygon(scratch, coat_dk, pts, max(1, body_w // 8))
        sy = torso_top + torso_h // 2
        pygame.draw.line(scratch, sash, (cx - body_w, sy), (cx + body_w, sy), max(2, body_w // 5))

    elif arch == A_TUNIC:
        # SHORT tunic over trousers: a compact rounded rect, legs fully visible —
        # the only class showing a clear leg gap, reads as a working figure.
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(scratch, coat, r, border_radius=max(2, body_w // 3))
        pygame.draw.rect(scratch, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 3))
        pygame.draw.line(scratch, coat_lt, (cx + lean, torso_top + 1), (cx + lean, torso_bot - 1),
                         max(1, body_w // 9))

    elif arch == A_PADDED:
        # BOXY bulky padded coat: square shoulders, near-rectangular, the widest
        # straight-sided body — instantly the snow figure.
        pad_w = int(body_w * 1.35)
        r = pygame.Rect(cx - pad_w + lean, torso_top - head_r // 2, pad_w * 2,
                        torso_h + head_r // 2)
        pygame.draw.rect(scratch, coat, r, border_radius=max(2, body_w // 5))
        pygame.draw.rect(scratch, coat_dk, r, max(2, body_w // 6), border_radius=max(2, body_w // 5))
        # quilting seams — interior, but the square outline carries it small
        for q in (0.34, 0.66):
            yy = int(r.top + r.height * q)
            pygame.draw.line(scratch, coat_dk, (r.left + 2, yy), (r.right - 2, yy), 1)
        fur = pal(P.get("fur", (226, 218, 204)))
        pygame.draw.line(scratch, fur, (r.left, r.top), (r.right, r.top), max(2, body_w // 4))

    elif arch == A_POLE:
        # Carrying-pole vendor body: a working robe, but its silhouette is OWNED
        # by the pole + two baskets held wide of the body (drawn below).
        sh_w = int(body_w * 0.74)
        hem_w = int(body_w * 1.0)
        pts = [(cx - sh_w + lean, torso_top), (cx + sh_w + lean, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(scratch, coat, pts)
        pygame.draw.polygon(scratch, coat_dk, pts, max(1, body_w // 8))

    elif arch == A_YOKE:
        # Shoulder-yoke porter: a compact tunic body; the silhouette is defined by
        # the horizontal yoke bar + two long hanging loads (drawn below).
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(scratch, coat, r, border_radius=max(2, body_w // 4))
        pygame.draw.rect(scratch, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 4))

    elif arch == A_HEADLOAD:
        # Tray-on-head carrier: an upright robe held very straight (balancing),
        # the silhouette topped by a wide flat slab above the head (drawn below).
        sh_w = int(body_w * 0.80)
        hem_w = int(body_w * 0.95)
        pts = [(cx - sh_w, torso_top), (cx + sh_w, torso_top),
               (cx + hem_w, torso_bot), (cx - hem_w, torso_bot)]
        pygame.draw.polygon(scratch, coat, pts)
        pygame.draw.polygon(scratch, coat_dk, pts, max(1, body_w // 8))
        # a steadying arm raised to the load
        pygame.draw.line(scratch, coat, (cx + sh_w * 0.4, torso_top + head_r // 2),
                         (cx + head_r // 2, hy - head_r), max(2, body_w // 5))

    elif arch == A_CHILD:
        # Small child: round little body, oversized head — the universal kid cue.
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(scratch, coat, r, border_radius=max(2, body_w // 2))
        pygame.draw.rect(scratch, coat_dk, r, 1, border_radius=max(2, body_w // 2))

    # ── ACCESSORIES that BREAK the outline (held away / overhead / hat) ──────
    if arch == A_POLE:
        pole_c = pal((120, 88, 54))
        py = torso_top - 1
        x0, x1 = cx - body_w * 1.7, cx + body_w * 1.7 + lean
        pygame.draw.line(scratch, pole_c, (x0, py + 3), (x1, py - 3), max(2, body_w // 6))
        for ex, ey in ((x0, py + 3), (x1, py - 3)):
            bk = pal(P.get("basket", (176, 132, 78)))
            br = pygame.Rect(ex - body_w * 0.6, ey + body_w * 0.5, body_w * 1.2, body_w * 1.0)
            pygame.draw.ellipse(scratch, bk, br)
            pygame.draw.ellipse(scratch, _shade(bk, -30), br, 1)
            pygame.draw.circle(scratch, pal(P.get("goods", (224, 120, 60))),
                               (int(ex), int(ey + body_w * 0.6)), max(1, body_w // 4))

    elif arch == A_YOKE:
        yoke_c = pal((110, 80, 50))
        yy = torso_top - 1
        x0, x1 = cx - body_w * 1.5, cx + body_w * 1.5 + lean
        pygame.draw.line(scratch, yoke_c, (x0, yy), (x1, yy), max(2, body_w // 6))
        # two long sacks hanging well below the body — strong vertical breakers
        for ex in (x0, x1):
            sk = pal(P.get("load", (150, 124, 86)))
            sr = pygame.Rect(ex - body_w * 0.5, yy + 2, body_w * 1.0, torso_h * 1.15)
            pygame.draw.rect(scratch, sk, sr, border_radius=max(1, body_w // 3))
            pygame.draw.rect(scratch, _shade(sk, -32), sr, 1, border_radius=max(1, body_w // 3))
            pygame.draw.line(scratch, yoke_c, (ex, yy), (ex, sr.top), max(1, body_w // 6))

    elif arch == A_HEADLOAD:
        tray = pal(P.get("tray", (164, 120, 76)))
        tw = int(body_w * 1.9)
        th = max(3, int(head_r * 0.9))
        ty = hy - head_r - th - 1
        tr = pygame.Rect(hx - tw, ty, tw * 2, th)
        pygame.draw.rect(scratch, tray, tr, border_radius=max(1, body_w // 4))
        pygame.draw.rect(scratch, _shade(tray, -34), tr, 1, border_radius=max(1, body_w // 4))
        # stacked goods bumps on top — breaks the flat top edge
        for gx in (-0.5, 0.0, 0.5):
            pygame.draw.circle(scratch, pal(P.get("goods", (218, 130, 70))),
                               (int(hx + gx * tw), int(ty)), max(1, body_w // 3))

    # generic carry/arm accessories on classes that allow them
    if "basket_arm" in v.acc:
        bk = pal(P.get("basket", (176, 132, 78)))
        bhx = cx + body_w * 1.5 + lean
        pygame.draw.line(scratch, coat, (cx + body_w * 0.6 + lean, arm_y),
                         (bhx, arm_y + torso_h // 2), max(2, body_w // 5))
        br = pygame.Rect(bhx - body_w * 0.55, arm_y + torso_h // 2, body_w * 1.1, body_w * 0.9)
        pygame.draw.ellipse(scratch, bk, br)
        pygame.draw.ellipse(scratch, _shade(bk, -30), br, 1)
        pygame.draw.arc(scratch, _shade(bk, -34), br.inflate(0, body_w // 2),
                        math.radians(15), math.radians(165), 1)
    if "cane" in v.acc:
        cane_c = pal(P.get("cane", (120, 84, 50)))
        chx = cx + body_w * 1.3 + lean
        pygame.draw.line(scratch, cane_c, (chx, arm_y), (chx + body_w * 0.3, ground),
                         max(2, body_w // 6))
        # gripping arm reaching out to the cane top — extends the outline sideways
        pygame.draw.line(scratch, coat, (cx + body_w * 0.5 + lean, arm_y),
                         (chx, arm_y), max(2, body_w // 5))
    if "bundle" in v.acc:
        bd = pal(P.get("bundle", (198, 176, 150)))
        br = pygame.Rect(cx - body_w * 0.7 + lean, arm_y + 1, body_w * 1.4, torso_h // 2)
        pygame.draw.rect(scratch, bd, br, border_radius=body_w // 4)
        pygame.draw.line(scratch, _shade(bd, -34), (br.centerx, br.top), (br.centerx, br.bottom), 1)
    if "hand_hold" in v.acc:
        # a small hand reaching down/sideways to a child's hand (parent of a pair)
        pygame.draw.line(scratch, skin, (cx + body_w * 0.7 + lean, arm_y + torso_h // 2),
                         (cx + body_w * 1.2 + lean, ground - leg_h * 0.3), max(2, body_w // 5))
    if "reach_up" in v.acc:
        # child reaching up to the parent's hand — the pairing's small half
        pygame.draw.line(scratch, skin, (cx + body_w * 0.5 + lean, arm_y),
                         (cx + body_w * 1.3 + lean, arm_y - torso_h * 0.4), max(2, body_w // 4))
    if "swing_arm" in v.pose and arch in (A_TUNIC,):
        ax = cx + lean + int(gait * body_w * 0.5)
        pygame.draw.line(scratch, coat, (cx + lean, arm_y),
                         (ax + body_w * 0.4, arm_y + torso_h * 0.55), max(2, body_w // 5))
        pygame.draw.circle(scratch, skin, (int(ax + body_w * 0.4), int(arm_y + torso_h * 0.55)),
                           max(1, body_w // 6))

    # ── HEAD + NECK ──────────────────────────────────────────────────────────
    pygame.draw.line(scratch, skin_sh, (hx, hy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(scratch, skin, (hx, hy), head_r)
    pygame.draw.circle(scratch, skin_sh, (hx, hy), head_r, 1)
    eye = (40, 28, 22)
    pygame.draw.circle(scratch, eye, (hx + head_r // 3, hy - head_r // 6), max(1, head_r // 4))
    if "beard" in v.acc:
        grey = pal(P.get("beard", (210, 208, 200)))
        pygame.draw.polygon(scratch, grey, [
            (hx - head_r * 0.6, hy + head_r * 0.3), (hx + head_r * 0.6, hy + head_r * 0.3),
            (hx + head_r * 0.2, hy + head_r * 1.7), (hx - head_r * 0.2, hy + head_r * 1.7)])

    # ── HEADWEAR (an outline-breaker — changes the top of the silhouette) ─────
    hat = P.get("hat")
    if hat == "conical":
        col = pal(P.get("hat_c", (198, 162, 96)))
        brim_w = int(head_r * 2.5)
        apex = (hx, hy - head_r * 1.8)
        cone = [(hx - brim_w, hy - head_r * 0.15), apex, (hx + brim_w, hy - head_r * 0.15)]
        pygame.draw.polygon(scratch, col, cone)
        pygame.draw.polygon(scratch, _shade(col, -34), cone, 1)
        pygame.draw.line(scratch, _shade(col, -30), (hx - brim_w, hy - head_r * 0.15),
                         (hx + brim_w, hy - head_r * 0.15), 1)
    elif hat == "winter":
        col = pal(P.get("hat_c", (150, 96, 80)))
        cap = pygame.Rect(hx - head_r, hy - head_r * 1.7, head_r * 2, int(head_r * 1.6))
        pygame.draw.ellipse(scratch, col, cap)
        fur = pal(P.get("fur", (224, 214, 198)))
        pygame.draw.line(scratch, fur, (hx - head_r, hy - head_r * 0.35),
                         (hx + head_r, hy - head_r * 0.35), max(2, head_r // 2))
    elif hat == "hood":
        col = pal(P.get("hat_c", coat))
        pygame.draw.circle(scratch, col, (hx, hy - head_r // 3), int(head_r * 1.35))
        pygame.draw.circle(scratch, skin, (hx + head_r // 4, hy), int(head_r * 0.8))
    elif hat == "cloth":
        col = pal(P.get("hat_c", (190, 90, 80)))
        pygame.draw.circle(scratch, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(scratch, skin, (hx + head_r // 3, hy + head_r // 5), int(head_r * 0.75))
        pygame.draw.polygon(scratch, _shade(col, -22), [
            (hx - head_r, hy - head_r // 2), (hx - head_r * 1.5, hy), (hx - head_r * 0.8, hy + head_r // 3)])
    elif hat == "bald":
        pygame.draw.circle(scratch, skin, (hx, hy - head_r // 4), head_r)  # bare pate
        pygame.draw.arc(scratch, hair, pygame.Rect(hx - head_r, hy - head_r // 2, head_r * 2, head_r * 2),
                        math.radians(200), math.radians(340), max(1, head_r // 3))  # fringe at back
    elif hat == "bun":
        pygame.draw.circle(scratch, hair, (hx, hy - head_r), head_r)
        pygame.draw.circle(scratch, hair_dk, (hx - head_r // 3, hy - head_r * 1.3), max(2, head_r // 2))
        if "hairpin" in v.acc:
            pin = pal(P.get("pin", (220, 90, 100)))
            pygame.draw.line(scratch, pin, (hx - head_r // 3, hy - head_r * 1.5),
                             (hx + head_r // 2, hy - head_r * 1.7), 2)
    else:
        pygame.draw.circle(scratch, hair, (hx, hy - head_r // 3), head_r)
        pygame.draw.arc(scratch, hair, pygame.Rect(hx - head_r, hy - head_r, head_r * 2, head_r * 2),
                        math.radians(0), math.radians(180), max(1, head_r // 2))
        if "topknot" in v.acc:
            pygame.draw.circle(scratch, hair_dk, (hx, hy - int(head_r * 1.4)), max(2, head_r // 2))

    # ── HELD PARASOL / UMBRELLA (overhead — the strongest outline-breaker) ────
    if "parasol" in v.acc or "umbrella" in v.acc:
        is_para = "parasol" in v.acc
        col = pal(P.get("canopy", (236, 224, 210)))
        dark = _shade(col, -42)
        cr = int(head_r * 2.5)
        tilt = int(head_r * (0.5 if "umbrella" in v.acc else 0.15))
        cy = hy - int(head_r * 2.7)
        apex_x = hx + tilt
        canopy = [(hx - cr, cy), (apex_x - cr // 2, cy - cr // 2), (apex_x, cy - cr),
                  (apex_x + cr // 2, cy - cr // 2), (hx + cr, cy),
                  (hx + cr * 3 // 5, cy + 3), (hx, cy + 1), (hx - cr * 3 // 5, cy + 3)]
        pygame.draw.polygon(scratch, col, canopy)
        pygame.draw.polygon(scratch, dark, canopy, max(1, head_r // 4))
        for tx in (-cr * 3 // 5, 0, cr * 3 // 5):
            pygame.draw.line(scratch, dark, (apex_x, cy - cr), (hx + tx, cy + (1 if tx == 0 else 3)), 1)
        pygame.draw.line(scratch, pal((110, 84, 56)), (hx, cy + 1), (hx - 1, arm_y + torso_h // 3),
                         max(2, head_r // 4))


# ── archetype palette/accessory variation → 50 people ─────────────────────────
# 9 silhouette archetypes. Within each, vary skin / coat hue / hat / accessory /
# height to get within-class diversity that survives because the OUTLINE is shared
# but recoloured & re-accessorised. Weather members tagged in roles.

# colour role-sets reused across archetypes (muted, NEVER out-popping the coin)
COATS = {
    "indigo":  ((86, 96, 140), (52, 60, 100)),
    "plum":    ((104, 80, 116), (66, 48, 78)),
    "sage":    ((110, 134, 112), (70, 92, 76)),
    "ochre":   ((158, 128, 78), (108, 84, 50)),
    "rust":    ((150, 86, 70), (104, 56, 46)),
    "teal":    ((78, 124, 124), (48, 84, 84)),
    "slate":   ((100, 108, 124), (64, 72, 90)),
    "olive":   ((118, 116, 80), (78, 78, 52)),
    "clay":    ((168, 120, 84), (114, 78, 54)),
    "mauve":   ((140, 104, 130), (94, 66, 90)),
    "stone":   ((128, 124, 112), (84, 82, 72)),
    "wine":    ((128, 70, 78), (84, 44, 50)),
}
SKINS = ["fair", "warm", "tan", "deep", "ruddy"]
HAIRS = [(46, 36, 30), (40, 32, 28), (58, 44, 36), (34, 28, 26), (70, 56, 44)]


def _c(name):
    return dict(coat=COATS[name][0], coat_dk=COATS[name][1])


POOL = []

def add(*args, **kw):
    POOL.append(V(*args, **kw))


# ARCH 1 — NARROW STRAIGHT ROBE (scholar / lady walker)  [tall, lean]
add("Robe · scholar indigo", A_ROBE, dict(**_c("indigo"), sash=(206, 200, 170), hair=HAIRS[2],
    skin="fair", hat="bun"), pose=("stroll",), acc=("topknot",), height=1.10,
    roles="ARCH robe(narrow,tall) · coat/coat_dk/sash · hat=bun · topknot")
add("Robe · plum elder upright", A_ROBE, dict(**_c("plum"), sash=(196, 180, 150),
    hair=(206, 204, 196), beard=(212, 210, 202), skin="fair", hat="bun"),
    pose=("stroll",), acc=("beard", "topknot"), height=1.0,
    roles="ARCH robe · coat/sash/beard · hat=bun · beard+topknot")
add("Robe · teal slim youth", A_ROBE, dict(**_c("teal"), sash=(200, 188, 150), hair=HAIRS[1],
    skin="warm", hat="bun"), pose=("hurry",), acc=("topknot",), height=0.92, build=0.9,
    roles="ARCH robe · coat/sash · hat=bun · hurry")
add("Robe · mauve hairpin lady", A_ROBE, dict(**_c("mauve"), sash=(208, 160, 140), hair=HAIRS[3],
    skin="fair", hat="bun", pin=(214, 110, 120)), pose=("stroll",), acc=("hairpin",),
    height=1.04, build=0.92, roles="ARCH robe · coat/sash/pin · hat=bun · hairpin")
add("Robe · slate tall scholar", A_ROBE, dict(**_c("slate"), sash=(180, 186, 196), hair=HAIRS[0],
    skin="tan", hat="bun"), pose=("stroll",), acc=("topknot",), height=1.10, build=0.95,
    roles="ARCH robe · coat/sash · hat=bun · topknot")
# ARCH 2 — WIDE A-LINE SKIRTED ROBE (matron / merchant)  [bell silhouette]
add("Skirt · matron sage basket", A_SKIRT, dict(**_c("sage"), sash=(214, 190, 140), hair=HAIRS[1],
    skin="warm", hat="cloth", hat_c=(186, 92, 84), basket=(182, 138, 84), goods=(196, 96, 90)),
    pose=("stroll",), acc=("basket_arm",), height=0.96, build=1.1,
    roles="ARCH skirt(wide) · coat/sash/hat_c(cloth)/basket · basket_arm")
add("Skirt · stout merchant conical", A_SKIRT, dict(**_c("ochre"), sash=(150, 74, 66), hair=HAIRS[0],
    skin="tan", hat="conical", hat_c=(188, 152, 90)), pose=("stroll",), acc=(), height=0.98, build=1.28,
    roles="ARCH skirt · coat/sash/hat_c(conical) · stout build · MODEL #9")
add("Skirt · clay matron cloth", A_SKIRT, dict(**_c("clay"), sash=(206, 180, 140), hair=HAIRS[4],
    skin="ruddy", hat="cloth", hat_c=(170, 96, 80), basket=(176, 132, 78), goods=(200, 120, 70)),
    pose=("stroll",), acc=("basket_arm",), height=0.94, build=1.12,
    roles="ARCH skirt · coat/hat_c(cloth)/basket · basket_arm")
add("Skirt · olive merchant conical", A_SKIRT, dict(**_c("olive"), sash=(140, 80, 70), hair=HAIRS[3],
    skin="deep", hat="conical", hat_c=(176, 146, 86)), pose=("stroll",), acc=(), height=1.0, build=1.22,
    roles="ARCH skirt · coat/sash/hat_c(conical) · stout build")
add("Skirt · stone matron basket", A_SKIRT, dict(**_c("stone"), sash=(196, 150, 120), hair=HAIRS[2],
    skin="warm", hat="cloth", hat_c=(150, 110, 96), basket=(170, 128, 80), goods=(180, 140, 80)),
    pose=("stroll",), acc=("basket_arm",), height=0.97, build=1.08,
    roles="ARCH skirt · coat/hat_c(cloth)/basket · basket_arm")
# ARCH 3 — SHORT TUNIC + TROUSERS (porter / youth)  [clear leg gap]
add("Tunic · porter clay deep", A_TUNIC, dict(**_c("clay"), trousers=(74, 64, 56), hair=HAIRS[3],
    skin="deep"), pose=("hurry", "swing_arm"), acc=(), height=1.02, build=1.12,
    roles="ARCH tunic(legs) · coat/trousers · hurry+swing_arm")
add("Tunic · youth teal", A_TUNIC, dict(**_c("teal"), trousers=(68, 62, 66), hair=HAIRS[1],
    skin="warm"), pose=("hurry", "swing_arm"), acc=(), height=0.92, build=0.9,
    roles="ARCH tunic · coat/trousers · hurry+swing_arm · short youth")
add("Tunic · ochre laborer tan", A_TUNIC, dict(**_c("ochre"), trousers=(70, 60, 50), hair=HAIRS[0],
    skin="tan"), pose=("hurry", "swing_arm"), acc=(), height=1.0, build=1.05,
    roles="ARCH tunic · coat/trousers · hurry+swing_arm")
add("Tunic · slate strolling warm", A_TUNIC, dict(**_c("slate"), trousers=(60, 64, 74), hair=HAIRS[2],
    skin="warm"), pose=("stroll", "swing_arm"), acc=(), height=1.0, build=1.0,
    roles="ARCH tunic · coat/trousers · stroll+swing_arm")
add("Tunic · rust porter ruddy", A_TUNIC, dict(**_c("rust"), trousers=(72, 56, 50), hair=HAIRS[4],
    skin="ruddy"), pose=("hurry", "swing_arm"), acc=(), height=1.04, build=1.1,
    roles="ARCH tunic · coat/trousers · hurry+swing_arm")
add("Tunic · olive youth deep", A_TUNIC, dict(**_c("olive"), trousers=(64, 62, 48), hair=HAIRS[3],
    skin="deep"), pose=("hurry", "swing_arm"), acc=(), height=0.9, build=0.92,
    roles="ARCH tunic · coat/trousers · hurry · short youth")
# ARCH 4 — BOXY PADDED WINTER COAT (snow)  [widest straight-sided]  [SNOW]
add("Padded · rust snow bundle", A_PADDED, dict(**_c("rust"), fur=(228, 220, 206), hair=HAIRS[3],
    skin="ruddy", hat="winter", hat_c=(150, 88, 74), bundle=(206, 188, 162)),
    pose=("hurry",), acc=("bundle",), height=0.98, build=1.2,
    roles="ARCH padded(boxy) · coat/fur/hat_c(winter)/bundle · bundle  [SNOW]")
add("Padded · indigo scarf snow", A_PADDED, dict(**_c("indigo"), fur=(222, 214, 200),
    trim=(206, 110, 96), hair=HAIRS[2], skin="fair", hat="winter", hat_c=(86, 100, 138)),
    pose=("stroll",), acc=(), height=0.96, build=1.18,
    roles="ARCH padded · coat/trim(scarf)/fur/hat_c(winter)  [SNOW]")
add("Padded · olive snow elder", A_PADDED, dict(**_c("olive"), fur=(226, 218, 204),
    hair=(206, 204, 196), beard=(214, 212, 204), skin="warm", hat="winter", hat_c=(120, 100, 70)),
    pose=("stroll",), acc=("beard",), height=0.92, build=1.15,
    roles="ARCH padded · coat/fur/beard/hat_c(winter) · beard  [SNOW]")
add("Padded · clay snow child", A_PADDED, dict(**_c("clay"), fur=(228, 222, 210), hair=HAIRS[1],
    skin="warm", hat="winter", hat_c=(150, 104, 76)), pose=("hurry",), acc=(), height=0.78, build=1.0,
    roles="ARCH padded · coat/fur/hat_c(winter) · short child  [SNOW]")
add("Padded · slate bundle snow", A_PADDED, dict(**_c("slate"), fur=(224, 216, 202),
    hair=HAIRS[0], skin="tan", hat="winter", hat_c=(96, 102, 120), bundle=(200, 184, 158)),
    pose=("hurry",), acc=("bundle",), height=1.0, build=1.22,
    roles="ARCH padded · coat/fur/bundle/hat_c(winter) · bundle  [SNOW]")

# ARCH 5 — HUNCHED CANE-WALKER ELDER (deeply stooped)  [elder cue]
add("Stoop · plum cane elder", A_STOOP, dict(**_c("plum"), sash=(196, 180, 150),
    hair=(208, 206, 198), beard=(214, 212, 204), skin="fair", hat="bald", cane=(120, 84, 50)),
    pose=("stroll",), acc=("beard", "cane"), height=0.9, stoop=0.42,
    roles="ARCH stoop(hunch) · coat/sash/beard/cane · STOOP=0.42 · cane+beard")
add("Stoop · slate cane elder", A_STOOP, dict(**_c("slate"), sash=(180, 184, 192),
    hair=(204, 202, 196), beard=(210, 208, 200), skin="warm", hat="bald", cane=(116, 80, 48)),
    pose=("stroll",), acc=("beard", "cane"), height=0.88, stoop=0.46,
    roles="ARCH stoop · coat/beard/cane · STOOP=0.46 · cane+beard")
add("Stoop · olive cane matron", A_STOOP, dict(**_c("olive"), sash=(196, 170, 130),
    hair=(202, 200, 194), skin="ruddy", hat="cloth", hat_c=(150, 110, 96), cane=(118, 82, 50)),
    pose=("stroll",), acc=("cane",), height=0.88, stoop=0.40,
    roles="ARCH stoop · coat/hat_c(cloth)/cane · STOOP=0.40 · cane")
add("Stoop · mauve deep elder", A_STOOP, dict(**_c("mauve"), sash=(200, 170, 150),
    hair=(206, 204, 198), beard=(212, 210, 202), skin="deep", hat="bald", cane=(110, 78, 46)),
    pose=("stroll",), acc=("beard", "cane"), height=0.86, stoop=0.48,
    roles="ARCH stoop · coat/beard/cane · STOOP=0.48 · cane+beard")

# ARCH 6 — CARRYING-POLE VENDOR (biandan)  [MODEL #1 — keep]
add("Pole · vendor rust conical", A_POLE, dict(**_c("rust"), hair=HAIRS[0], skin="tan",
    hat="conical", hat_c=(196, 158, 92), basket=(176, 132, 78), goods=(214, 130, 70)),
    pose=("hurry",), acc=(), height=1.0, build=1.05,
    roles="ARCH pole(biandan) · coat/hat_c(conical)/basket/goods · MODEL #1")
add("Pole · vendor ochre cloth", A_POLE, dict(**_c("ochre"), hair=HAIRS[3], skin="deep",
    hat="cloth", hat_c=(160, 96, 84), basket=(170, 126, 76), goods=(200, 110, 80)),
    pose=("hurry",), acc=(), height=1.0, build=1.05,
    roles="ARCH pole · coat/hat_c(cloth)/basket/goods")
add("Pole · vendor sage conical", A_POLE, dict(**_c("sage"), hair=HAIRS[1], skin="warm",
    hat="conical", hat_c=(184, 150, 88), basket=(178, 134, 80), goods=(186, 150, 80)),
    pose=("stroll",), acc=(), height=1.04, build=1.0,
    roles="ARCH pole · coat/hat_c(conical)/basket/goods")
add("Pole · vendor clay conical", A_POLE, dict(**_c("clay"), hair=HAIRS[4], skin="ruddy",
    hat="conical", hat_c=(190, 156, 92), basket=(172, 128, 78), goods=(210, 120, 64)),
    pose=("hurry",), acc=(), height=0.98, build=1.08,
    roles="ARCH pole · coat/hat_c(conical)/basket/goods")
add("Pole · vendor olive cloth", A_POLE, dict(**_c("olive"), hair=HAIRS[0], skin="tan",
    hat="cloth", hat_c=(150, 100, 80), basket=(176, 130, 80), goods=(190, 140, 70)),
    pose=("hurry",), acc=(), height=1.0, build=1.05,
    roles="ARCH pole · coat/hat_c(cloth)/basket/goods")

# ARCH 7 — SHOULDER-YOKE PORTER (two hanging loads)  [NEW outline]
add("Yoke · porter ochre sacks", A_YOKE, dict(**_c("ochre"), trousers=(72, 60, 50), hair=HAIRS[0],
    skin="deep", load=(150, 124, 86)), pose=("hurry",), acc=(), height=1.02, build=1.1,
    roles="ARCH yoke(2 loads) · coat/trousers/load · hurry · NEW")
add("Yoke · porter rust sacks", A_YOKE, dict(**_c("rust"), trousers=(74, 56, 50), hair=HAIRS[3],
    skin="tan", load=(158, 130, 90)), pose=("hurry",), acc=(), height=1.0, build=1.12,
    roles="ARCH yoke · coat/trousers/load · hurry")
add("Yoke · porter slate sacks", A_YOKE, dict(**_c("slate"), trousers=(60, 62, 70), hair=HAIRS[1],
    skin="warm", load=(146, 120, 84)), pose=("hurry",), acc=(), height=1.06, build=1.08,
    roles="ARCH yoke · coat/trousers/load · hurry · tall")
add("Yoke · porter clay sacks", A_YOKE, dict(**_c("clay"), trousers=(70, 58, 50), hair=HAIRS[4],
    skin="ruddy", load=(162, 134, 92)), pose=("hurry",), acc=(), height=0.98, build=1.1,
    roles="ARCH yoke · coat/trousers/load · hurry")
add("Yoke · porter olive sacks", A_YOKE, dict(**_c("olive"), trousers=(64, 62, 48), hair=HAIRS[2],
    skin="warm", load=(152, 126, 88)), pose=("hurry",), acc=(), height=1.0, build=1.06,
    roles="ARCH yoke · coat/trousers/load · hurry")

# ARCH 8 — TRAY/BOX ON HEAD (flat slab above the head)  [NEW outline]
add("Headload · tray sage", A_HEADLOAD, dict(**_c("sage"), tray=(164, 120, 76), hair=HAIRS[1],
    skin="warm", goods=(214, 130, 70)), pose=("stroll",), acc=(), height=1.0, build=1.0,
    roles="ARCH headload(tray) · coat/tray/goods · NEW")
add("Headload · tray clay", A_HEADLOAD, dict(**_c("clay"), tray=(160, 118, 74), hair=HAIRS[4],
    skin="ruddy", goods=(196, 150, 80)), pose=("stroll",), acc=(), height=0.96, build=1.0,
    roles="ARCH headload · coat/tray/goods")
add("Headload · tray indigo", A_HEADLOAD, dict(**_c("indigo"), tray=(150, 112, 70), hair=HAIRS[2],
    skin="fair", goods=(206, 120, 70)), pose=("stroll",), acc=(), height=1.04, build=0.98,
    roles="ARCH headload · coat/tray/goods · tall")
add("Headload · box ochre", A_HEADLOAD, dict(**_c("ochre"), tray=(140, 104, 64), hair=HAIRS[0],
    skin="tan", goods=(180, 140, 84)), pose=("stroll",), acc=(), height=1.0, build=1.05,
    roles="ARCH headload · coat/tray/goods")
add("Headload · tray rust", A_HEADLOAD, dict(**_c("rust"), tray=(158, 116, 74), hair=HAIRS[3],
    skin="deep", goods=(210, 120, 64)), pose=("stroll",), acc=(), height=0.98, build=1.0,
    roles="ARCH headload · coat/tray/goods")

# ARCH 9 — CHILD (small, big head — pairs w/ a tall parent)  [height story]
add("Child · teal running", A_CHILD, dict(**_c("teal"), trousers=(64, 60, 64), hair=HAIRS[1],
    skin="warm"), pose=("hurry",), acc=("reach_up",), height=0.62, build=1.0,
    roles="ARCH child(small,bighead) · coat/trousers · reach_up · pairs w/ parent")
add("Child · wine waving", A_CHILD, dict(**_c("wine"), trousers=(70, 56, 60), hair=HAIRS[3],
    skin="ruddy"), pose=("hurry",), acc=("reach_up",), height=0.6, build=1.0,
    roles="ARCH child · coat/trousers · reach_up")
add("Child · sage skipping", A_CHILD, dict(**_c("sage"), trousers=(62, 64, 56), hair=HAIRS[2],
    skin="fair"), pose=("hurry",), acc=(), height=0.64, build=1.0,
    roles="ARCH child · coat/trousers · hurry")
# the tall PARENT halves of the pairings (reach down to a child's hand)
add("Parent · robe slate (w/ child)", A_ROBE, dict(**_c("slate"), sash=(186, 188, 196),
    hair=HAIRS[0], skin="fair", hat="bun"), pose=("stroll",), acc=("hand_hold", "topknot"),
    height=1.10, roles="ARCH robe · coat/sash · hand_hold · TALL parent of a child pair")
add("Parent · skirt clay (w/ child)", A_SKIRT, dict(**_c("clay"), sash=(204, 178, 140),
    hair=HAIRS[2], skin="warm", hat="cloth", hat_c=(170, 96, 80)), pose=("stroll",),
    acc=("hand_hold",), height=1.04, build=1.08,
    roles="ARCH skirt · coat/hat_c(cloth) · hand_hold · TALL parent of a child pair")

# ── WEATHER: umbrella walkers (rain) — desaturated, value-lowered canopies ────
# AD: desaturate the parasol pink ~25-30% and lower its value; nothing on the
# sidewalk should out-pop the gold coin or parrot. These canopies are muted.
add("Umbrella · rain red walker", A_TUNIC, dict(**_c("slate"), trousers=(60, 62, 70),
    hair=HAIRS[2], skin="warm", canopy=(176, 96, 92)), pose=("hurry", "swing_arm"),
    acc=("umbrella",), height=1.0, roles="ARCH tunic · canopy(muted red) · umbrella  [RAIN]")
add("Umbrella · rain ochre calm", A_ROBE, dict(**_c("olive"), sash=(180, 160, 120),
    hair=HAIRS[0], skin="fair", hat="bun", canopy=(150, 138, 102)), pose=("stroll",),
    acc=("umbrella",), height=1.02, roles="ARCH robe · canopy(muted ochre) · umbrella  [RAIN]")
add("Umbrella · rain blue calm", A_SKIRT, dict(**_c("stone"), sash=(150, 120, 90),
    hair=HAIRS[1], skin="fair", hat="bun", canopy=(96, 122, 162)), pose=("stroll",),
    acc=("umbrella",), height=1.0, build=1.05, roles="ARCH skirt · canopy(muted blue) · umbrella  [RAIN]")
add("Umbrella · rain hood oilskin", A_ROBE, dict(**_c("teal"), sash=(70, 96, 92),
    hair=HAIRS[3], skin="warm", hat="hood", hat_c=(72, 100, 96)), pose=("hurry",),
    acc=(), height=1.0, roles="ARCH robe · hat_c(hood) · hood  [RAIN]")
# the desaturated parasol lady (focal-hierarchy pass: muted pink, lower value)
add("Parasol · lady muted rose", A_ROBE, dict(**_c("mauve"), sash=(190, 150, 140),
    hair=HAIRS[3], skin="fair", hat="bun", pin=(196, 120, 124), canopy=(196, 156, 166)),
    pose=("stroll",), acc=("parasol", "hairpin"), height=1.04, build=0.92,
    roles="ARCH robe · canopy(muted rose -28% sat) · parasol+hairpin")

assert len(POOL) == 50, f"pool is {len(POOL)}, need 50"


# ── archetype groupings for the labelled grid ─────────────────────────────────
ARCH_GROUPS = [
    ("ARCH 1 · NARROW ROBE (tall/lean)", A_ROBE),
    ("ARCH 2 · WIDE A-LINE SKIRT (bell)", A_SKIRT),
    ("ARCH 3 · SHORT TUNIC (leg gap)", A_TUNIC),
    ("ARCH 4 · BOXY PADDED COAT [SNOW]", A_PADDED),
    ("ARCH 5 · HUNCHED CANE ELDER", A_STOOP),
    ("ARCH 6 · CARRYING-POLE VENDOR", A_POLE),
    ("ARCH 7 · SHOULDER-YOKE PORTER", A_YOKE),
    ("ARCH 8 · TRAY-ON-HEAD CARRIER", A_HEADLOAD),
    ("ARCH 9 · CHILD (pairs w/ parent)", A_CHILD),
]


# ── bake: CRISP far, light-smooth near (the AD's hybrid-by-footprint rule) ────

def baked(v, footprint_h, night, t, smooth):
    """Author at 3x then resample to footprint. `smooth=False` is the crisp
    NEAREST path (FAR); `smooth=True` is the light bilinear path (NEAR). This is
    exactly the `smooth=` selector on game.foreground_sprite.baked_sprite."""
    box_h = footprint_h * 3
    box_w = int(box_h * 0.78)
    scratch = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    draw_person(scratch, v, night, t)
    fw = max(1, int(box_w / 3))
    if smooth:
        return pygame.transform.smoothscale(scratch, (fw, footprint_h))
    return pygame.transform.scale(scratch, (fw, footprint_h))


# ── day / night palette pulled from the live biome so context is authentic ────
from game import biome  # noqa: E402

P_DAY = biome.palette_for_phase(0.30)
P_NIGHT = biome.palette_for_phase(0.68)


def _street_bg(surf, rect, pal, ground_frac=0.42):
    """Paint a vertical sky→ground street slab matching the live floor bands."""
    x, y, w, h = rect
    gy = int(h * (1 - ground_frac))
    for i in range(h):
        if i < gy:
            f = i / max(1, gy)
            col = _mix(pal["sky_top"], pal["sky_bot"], f)
        else:
            f = (i - gy) / max(1, h - gy)
            col = _mix(pal["ground_top"], pal["ground_mid"], min(1.0, f * 1.3))
        surf.fill(col, (x, y + i, w, 1))
    return y + gy  # ground line


def main():
    pygame.init()
    font = pygame.font.SysFont("dejavusans", 10)
    font_sm = pygame.font.SysFont("dejavusans", 8)
    font_md = pygame.font.SysFont("dejavusans", 12, bold=True)
    font_hd = pygame.font.SysFont("dejavusans", 17, bold=True)

    FAR_H, NEAR_H, ZOOM_H = 14, 22, 64
    t = 1.1

    # ── SECTION A: ALL 50 at true FAR size, grouped by archetype ─────────────
    cell_w, cell_h = 92, 64
    grp_cols = 6                          # up to 6 variants per archetype row band
    a_x0 = 16
    a_y0 = 96
    band_label_h = 18
    note_h = 26
    band_h = band_label_h + cell_h + note_h

    # ── SECTION B: representative NEAR + zoom, day/night halves ──────────────
    # one+ from each archetype, plus weather, parent/child pair, parasol lady
    REP = [4, 0, 6, 8, 10, 11, 16, 19, 21, 24, 25, 30,
           35, 40, 43, 49]
    b_tile_w, b_tile_h = 196, 132
    b_cols = 4
    b_rows = (len(REP) + b_cols - 1) // b_cols

    # ── SECTION C: on-street composite strips (day + night) ──────────────────
    # a representative cross-section spanning all 9 archetypes + weather + pair
    STRIP_PEOPLE = [25, 0, 6, 10, 30, 1, 35, 21, 4, 16, 40, 43, 8, 11, 24, 49,
                    32, 37, 47, 19]
    strip_w = 760
    strip_h = 92

    # Bands wrap to as many member-rows as the archetype needs (robe carries the
    # parent + umbrella/parasol variants, so it's the tallest).
    def _band_rows(arch):
        n = sum(1 for v in POOL if v.arch == arch)
        return (n + grp_cols - 1) // grp_cols
    a_h = sum(band_label_h + _band_rows(a) * (cell_h + note_h) + 6 for _, a in ARCH_GROUPS)
    b_h = b_rows * (b_tile_h + 6) + 34
    c_h = 2 * (strip_h + 22) + 34

    sheet_w = max(a_x0 + grp_cols * (cell_w + 4) + 24, a_x0 + b_cols * (b_tile_w + 6) + 16, strip_w + 32)
    sheet_h = a_y0 + a_h + b_h + c_h + 40
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((40, 42, 50))

    # header
    pygame.draw.rect(sheet, (24, 26, 34), (0, 0, sheet_w, 84))
    sheet.blit(font_hd.render("SKYBIT PROMENADE — 50 ADULT PEDESTRIANS (round 2)", True, (240, 232, 210)), (16, 10))
    sheet.blit(font_sm.render(
        "9 SILHOUETTE-DISTINCT archetypes x palette sets x pose/accessory/height flags over ONE shared body drawer (= foreground_variants.Variant rows).",
        True, (192, 198, 202)), (16, 34))
    sheet.blit(font_sm.render(
        "FAR ~14px baked CRISP (nearest, smooth=False); NEAR ~22px light smoothscale (smooth=True) — the per-call selector on foreground_sprite.baked_sprite.",
        True, (192, 198, 202)), (16, 48))
    sheet.blit(font_sm.render(
        "Variety lives in the OUTLINE (body-shape + height + stoop + outline-breaker accessories) because the downscale kills colour/interior detail first.",
        True, (192, 198, 202)), (16, 62))

    # ─── SECTION A ───
    sheet.blit(font_md.render("A · ALL 50 AT TRUE FAR SIZE (~14px), grouped by silhouette archetype  [crisp downscale]",
                              True, (236, 226, 200)), (16, a_y0 - 24))
    y = a_y0
    row_h = cell_h + note_h
    for label, arch in ARCH_GROUPS:
        members = [(i, v) for i, v in enumerate(POOL) if v.arch == arch]
        nrows = (len(members) + grp_cols - 1) // grp_cols
        bh = band_label_h + nrows * row_h
        pygame.draw.rect(sheet, (30, 33, 42), (a_x0 - 6, y, sheet_w - a_x0 - 10, bh), border_radius=6)
        sheet.blit(font.render(f"{label}   ({len(members)})", True, (220, 224, 230)), (a_x0, y + 3))
        for j, (i, v) in enumerate(members):
            cxr, cyr = j % grp_cols, j // grp_cols
            ox = a_x0 + cxr * (cell_w + 4)
            gy = y + band_label_h + cyr * row_h + cell_h - 6
            if cxr == 0:
                pygame.draw.line(sheet, _shade(P_DAY["ground_top"], -20),
                                 (a_x0, gy + 1), (a_x0 + grp_cols * (cell_w + 4), gy + 1), 1)
            far = baked(v, FAR_H, 0.0, t, smooth=False)
            sheet.blit(far, (ox + cell_w // 2 - far.get_width() // 2, gy - FAR_H))
            sheet.blit(font_sm.render(f"#{i+1}", True, (210, 214, 220)), (ox + 2, gy + 3))
            fl = f"h{v.height:.2f}"
            if v.stoop:
                fl += f" st{v.stoop:.2f}"
            if v.build != 1.0:
                fl += f" b{v.build:.2f}"
            sheet.blit(font_sm.render(fl, True, (160, 200, 180)), (ox + 2, gy + 13))
        y += bh + 6
    a_end = y

    # ─── SECTION B ───
    by0 = a_end + 14
    sheet.blit(font_md.render("B · REPRESENTATIVE CROSS-SECTION — NEAR ~22px + zoom inset, DAY half | NIGHT half",
                              True, (236, 226, 200)), (16, by0))
    by0 += 22
    DAYG = P_DAY["ground_top"]
    NIGHTG = P_NIGHT["ground_top"]
    for bi, idx in enumerate(REP):
        v = POOL[idx]
        cxr, cyr = bi % b_cols, bi // b_cols
        ox = 16 + cxr * (b_tile_w + 6)
        oy = by0 + cyr * (b_tile_h + 6)
        half = b_tile_w // 2
        gl = _street_bg(sheet, (ox, oy + 16, half, b_tile_h - 30), P_DAY, ground_frac=0.34)
        _street_bg(sheet, (ox + half, oy + 16, b_tile_w - half, b_tile_h - 30), P_NIGHT, ground_frac=0.34)
        sheet.blit(font_sm.render(f"#{idx+1} {v.name}", True, (244, 238, 222)), (ox + 3, oy + 2))

        for night, sx in ((0.0, ox), (1.0, ox + half)):
            far = baked(v, FAR_H, night, t, smooth=False)
            near = baked(v, NEAR_H, night, t, smooth=True)
            zoom = pygame.transform.scale(baked(v, ZOOM_H // 4, night, 0.7, smooth=True),
                                          (int(ZOOM_H * 0.78), ZOOM_H))
            sheet.blit(far, (sx + 8, gl - FAR_H))
            sheet.blit(near, (sx + 24, gl - NEAR_H))
            sheet.blit(zoom, (sx + half - int(ZOOM_H * 0.78) - 4, gl - ZOOM_H))
        sheet.blit(font_sm.render("FAR NEAR  zoom", True, (90, 80, 64)), (ox + 6, gl + 3))
        sheet.blit(font_sm.render("day", True, (60, 54, 42)), (ox + 6, oy + b_tile_h - 22))
        sheet.blit(font_sm.render("night", True, (198, 206, 222)), (ox + half + 6, oy + b_tile_h - 22))
        sheet.blit(font_sm.render(v.roles[:54], True, (200, 206, 212)), (ox + 3, oy + b_tile_h - 11))
    b_end = by0 + b_rows * (b_tile_h + 6)

    # ─── SECTION C ───
    cy0 = b_end + 14
    sheet.blit(font_md.render("C · ON-STREET COMPOSITE — representative cross-section at FAR size, on the ACTUAL day & night street",
                              True, (236, 226, 200)), (16, cy0))
    cy0 += 22
    for night, pal, tag in ((0.0, P_DAY, "DAY"), (1.0, P_NIGHT, "NIGHT")):
        sx0 = 16
        gl = _street_bg(sheet, (sx0, cy0, strip_w, strip_h), pal, ground_frac=0.5)
        sheet.blit(font_sm.render(tag, True, (240, 236, 224) if night else (40, 36, 28)), (sx0 + 4, cy0 + 3))
        # a reference gold coin so reviewers can confirm no pedestrian out-pops it
        coin_x = sx0 + strip_w - 30
        coin_y = cy0 + 22
        pygame.draw.circle(sheet, (255, 208, 70), (coin_x, coin_y), 8)
        pygame.draw.circle(sheet, (210, 150, 30), (coin_x, coin_y), 8, 2)
        sheet.blit(font_sm.render("coin ref", True, (240, 236, 224) if night else (40, 36, 28)),
                   (coin_x - 18, coin_y + 10))
        step = (strip_w - 80) // len(STRIP_PEOPLE)
        for k, idx in enumerate(STRIP_PEOPLE):
            v = POOL[idx]
            far = baked(v, FAR_H, night, t + k * 0.4, smooth=False)
            px = sx0 + 16 + k * step
            sheet.blit(far, (px, gl - FAR_H + 1))
        cy0 += strip_h + 22

    pygame.draw.rect(sheet, (60, 64, 74), (0, 0, sheet_w, sheet_h), 2)

    out = "/home/user/skybit/docs/sidewalk_overhaul/pedestrians/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
