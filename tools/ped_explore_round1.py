"""SCRATCH (exploration only — not imported by the game).

Round-1 variety pool for the promenade ADULT PEDESTRIANS. One shared, richer body
drawer parameterised by a Variant descriptor (palette roles + pose/accessory
flags), authored at ~3x and smoothscaled DOWN to the on-screen footprint so fine
features resolve crisply small. Renders each person at true on-screen far/near
size AND a zoomed inset, on a day strip and a night strip, into one sheet.
"""
import math
import os

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

NIGHT_GLOW_CAP = 150

def _cap150(c):
    return (min(int(c[0]), NIGHT_GLOW_CAP), min(int(c[1]), NIGHT_GLOW_CAP), min(int(c[2]), NIGHT_GLOW_CAP))

def _retint_person(col, night):
    """Cool clothing toward the night ground band (matches the live _retint_person)."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


# ── Variant descriptor (mirrors game.foreground_variants.Variant in spirit) ───
# Each pedestrian is a palette dict of named roles + pose flags + accessory flags
# over the SINGLE shared drawer below. This is what becomes a registry row.

class V:
    def __init__(self, name, palette, pose=(), acc=(), build=1.0, height=1.0, roles=""):
        self.name = name
        self.palette = palette
        self.pose = set(pose)
        self.acc = set(acc)
        self.build = build      # torso width multiplier (slim..stout)
        self.height = height    # overall height multiplier (short..tall)
        self.roles = roles      # human-readable role/flag note for the sheet


SKIN_TONES = {
    "fair":   (236, 198, 156),
    "warm":   (222, 178, 132),
    "tan":    (200, 156, 112),
    "deep":   (168, 124, 86),
    "ruddy":  (228, 176, 150),
}


# ── the SHARED richer body drawer ─────────────────────────────────────────────
# Authored in a render box where the figure is ~3x the on-screen footprint, feet
# at the bottom edge, facing right (the scroll direction). Everything reads off
# the Variant palette/flags so adding a person = adding a data row, not code.

def draw_person(scratch, v, night, t):
    sw, sh = scratch.get_size()
    P = v.palette
    pal = lambda c: _retint_person(c, night)

    skin = pal(SKIN_TONES.get(P.get("skin", "warm"), SKIN_TONES["warm"]))
    skin_sh = _shade(skin, -28)
    coat = pal(P["coat"])
    coat_dk = pal(P.get("coat_dk", _shade(P["coat"], -42)))
    coat_lt = _shade(coat, 18)
    trim = pal(P.get("trim", _shade(P["coat"], 30)))
    hair = pal(P.get("hair", (58, 42, 34)))
    hair_dk = _shade(hair, -22)
    sash = pal(P.get("sash", trim))

    # Geometry in the render box. Authoring units are generous so curves/folds
    # resolve when the whole thing is smoothscaled down to ~14px tall.
    cx = sw // 2
    ground = sh - 3
    # Height + build scale the canonical proportions.
    total_h = int(sh * 0.86 * v.height)
    head_r = max(5, int(total_h * 0.14))
    torso_h = int(total_h * 0.46)
    leg_h = total_h - torso_h - head_r * 2
    body_w = int(total_h * 0.30 * v.build)

    head_cy = ground - leg_h - torso_h - head_r
    torso_top = head_cy + head_r
    torso_bot = torso_top + torso_h

    # Gait: a slow walk cycle; hurry doubles the cadence and adds a forward lean.
    hurry = "hurry" in v.pose
    hz = 2.6 if hurry else 1.5
    gait = math.sin(t * hz)
    lean = int(body_w * (0.30 if hurry else 0.12) * (1 if (hurry or "stroll" in v.pose) else 0.6))
    bob = -abs(gait) * (total_h * 0.03)
    head_cy += int(bob)
    torso_top += int(bob)

    seated = "seated" in v.pose

    # ---- legs (drawn first, behind the robe hem) ----
    if not seated:
        swing = gait * body_w * (0.55 if hurry else 0.32)
        for sgn, sw_ in ((-1, swing), (1, -swing)):
            foot_x = cx + sgn * body_w * 0.22 + sw_ * 0.5
            if "robe" in v.pose:
                # Robe hides legs; only a hem-foot peeks.
                pygame.draw.line(scratch, coat_dk, (cx + sgn * body_w * 0.22, torso_bot),
                                 (foot_x, ground), max(2, body_w // 4))
            else:
                trousers = pal(P.get("trousers", coat_dk))
                pygame.draw.line(scratch, trousers, (cx + sgn * body_w * 0.22, torso_bot - body_w * 0.2),
                                 (foot_x, ground), max(2, body_w // 3))
                pygame.draw.line(scratch, _shade(trousers, -30), (foot_x - 1, ground),
                                 (foot_x + 2, ground), max(2, body_w // 3))  # foot

    # ---- torso ----
    if "robe" in v.pose:
        # A flowing robe: narrow shoulders, broad hem (A-line), with a centre
        # fold seam and a sash band. Reads as Hanfu / vendor's long coat.
        sh_w = int(body_w * 0.78)
        hem_w = int(body_w * 1.25)
        pts = [
            (cx - sh_w + lean, torso_top),
            (cx + sh_w + lean, torso_top),
            (cx + hem_w, torso_bot + leg_h * (0.0 if seated else 0.0)),
            (cx - hem_w, torso_bot),
        ]
        if seated:
            pts[2] = (cx + hem_w, ground)
            pts[3] = (cx - hem_w, ground)
        pygame.draw.polygon(scratch, coat, pts)
        pygame.draw.polygon(scratch, coat_dk, pts, max(1, body_w // 8))
        # Centre fold + lapel cross (the wrap-front cue).
        pygame.draw.line(scratch, coat_dk, (cx + lean // 2, torso_top + head_r // 2),
                         (cx, pts[3][1]), max(1, body_w // 10))
        pygame.draw.line(scratch, coat_lt, (cx - sh_w + lean, torso_top + 1),
                         (cx + lean // 3, torso_top + head_r), max(1, body_w // 10))
        # Sash band.
        sy = torso_top + torso_h // 2
        pygame.draw.line(scratch, sash, (cx - body_w + 1, sy), (cx + body_w - 1, sy), max(2, body_w // 5))
        pygame.draw.line(scratch, _shade(sash, -28), (cx - body_w + 1, sy + body_w // 5),
                         (cx + body_w - 1, sy + body_w // 5), 1)
    else:
        # A fitted tunic/coat: rounded-shoulder rect with a front placket.
        r = pygame.Rect(cx - body_w + lean, torso_top, body_w * 2, torso_h)
        pygame.draw.rect(scratch, coat, r, border_radius=max(2, body_w // 3))
        pygame.draw.rect(scratch, coat_dk, r, max(1, body_w // 8), border_radius=max(2, body_w // 3))
        pygame.draw.line(scratch, coat_lt, (cx + lean, torso_top + 1), (cx + lean, torso_bot - 1),
                         max(1, body_w // 9))
        if "apron" in v.acc:
            ap = pal(P.get("apron", (210, 200, 180)))
            ar = pygame.Rect(cx - int(body_w * 0.7) + lean, torso_top + torso_h // 3,
                             int(body_w * 1.4), int(torso_h * 0.7))
            pygame.draw.rect(scratch, ap, ar, border_radius=max(1, body_w // 4))
            pygame.draw.rect(scratch, _shade(ap, -26), ar, 1, border_radius=max(1, body_w // 4))

    # ---- arms / carried items (behind-or-front depending on pose) ----
    arm_y = torso_top + int(head_r * 0.8)
    if "hands_sleeve" in v.pose:
        # Hands tucked into opposing sleeves at the belly — a calm muff shape.
        muff = pygame.Rect(cx - body_w // 2 + lean, arm_y + torso_h // 4, body_w, torso_h // 3)
        pygame.draw.rect(scratch, coat_lt, muff, border_radius=body_w // 3)
        pygame.draw.rect(scratch, coat_dk, muff, 1, border_radius=body_w // 3)

    if "pole" in v.acc:
        # Carrying-pole (biandan) across the shoulder with a basket each end.
        pole_c = (120, 88, 54)
        py = torso_top - 1
        x0, x1 = cx - body_w * 1.5, cx + body_w * 1.5 + lean
        pygame.draw.line(scratch, pole_c, (x0, py + 2), (x1, py - 2), max(2, body_w // 6))
        for ex, ey, droop in ((x0, py + 2, 1), (x1, py - 2, 1)):
            bk = pal(P.get("basket", (176, 132, 78)))
            br = pygame.Rect(ex - body_w * 0.55, ey + body_w * 0.4, body_w * 1.1, body_w * 0.9)
            pygame.draw.ellipse(scratch, bk, br)
            pygame.draw.ellipse(scratch, _shade(bk, -30), br, 1)
            pygame.draw.arc(scratch, _shade(bk, -34), br, math.radians(20), math.radians(160), 1)
            # produce lump
            pygame.draw.circle(scratch, pal(P.get("goods", (220, 120, 60))),
                               (int(ex), int(ey + body_w * 0.55)), max(1, body_w // 4))

    elif "basket_arm" in v.acc:
        # A basket carried on the forearm at the hip.
        bk = pal(P.get("basket", (176, 132, 78)))
        hx = cx + body_w + lean
        pygame.draw.line(scratch, coat, (cx + body_w * 0.5 + lean, arm_y),
                         (hx, arm_y + torso_h // 2), max(2, body_w // 5))  # arm
        br = pygame.Rect(hx - body_w * 0.5, arm_y + torso_h // 2, body_w, body_w * 0.85)
        pygame.draw.ellipse(scratch, bk, br)
        pygame.draw.ellipse(scratch, _shade(bk, -30), br, 1)
        pygame.draw.arc(scratch, _shade(bk, -34), br.inflate(0, body_w // 2),
                        math.radians(15), math.radians(165), 1)  # handle
        pygame.draw.circle(scratch, pal(P.get("goods", (210, 90, 90))),
                           (int(hx), int(arm_y + torso_h // 2 + 2)), max(1, body_w // 4))

    elif "bundle" in v.acc:
        # A wrapped bundle hugged to the chest (snow-bundled errand-runner).
        bd = pal(P.get("bundle", (198, 176, 150)))
        br = pygame.Rect(cx - body_w * 0.7 + lean, arm_y + 1, body_w * 1.4, torso_h // 2)
        pygame.draw.rect(scratch, bd, br, border_radius=body_w // 4)
        pygame.draw.line(scratch, _shade(bd, -34), (br.centerx, br.top), (br.centerx, br.bottom), 1)
        # arms wrapping it
        pygame.draw.line(scratch, coat, (cx - body_w + lean, arm_y), (br.left, br.centery), max(2, body_w // 5))
        pygame.draw.line(scratch, coat, (cx + body_w + lean, arm_y), (br.right, br.centery), max(2, body_w // 5))

    elif "swing_arm" in v.pose and not seated:
        # A natural counter-swung arm so a plain walker isn't a frozen plank.
        ax = cx + lean + int(gait * body_w * 0.5)
        pygame.draw.line(scratch, coat, (cx + lean, arm_y), (ax + body_w * 0.4, arm_y + torso_h * 0.55),
                         max(2, body_w // 5))
        pygame.draw.circle(scratch, skin, (int(ax + body_w * 0.4), int(arm_y + torso_h * 0.55)),
                           max(1, body_w // 6))

    # ---- head + face ----
    hx, hy = cx + lean, head_cy
    # neck
    pygame.draw.line(scratch, skin_sh, (hx, head_cy + head_r - 1), (hx, torso_top + 1), max(2, head_r // 2))
    pygame.draw.circle(scratch, skin, (hx, hy), head_r)
    pygame.draw.circle(scratch, skin_sh, (hx, hy), head_r, 1)
    # cheek shade on the trailing side for a touch of form
    pygame.draw.circle(scratch, skin_sh, (hx - head_r // 2, hy + head_r // 4), max(1, head_r // 3))
    # eye(s) — facing right, so one near eye + a brow
    eye = (40, 28, 22)
    pygame.draw.circle(scratch, eye, (hx + head_r // 3, hy - head_r // 6), max(1, head_r // 4))
    if "beard" in v.acc:
        grey = pal(P.get("beard", (210, 208, 200)))
        pygame.draw.polygon(scratch, grey, [
            (hx - head_r * 0.6, hy + head_r * 0.3), (hx + head_r * 0.6, hy + head_r * 0.3),
            (hx + head_r * 0.2, hy + head_r * 1.6), (hx - head_r * 0.2, hy + head_r * 1.6)])

    # ---- headwear / hair ----
    hat = P.get("hat")
    if hat == "conical":
        # Dǒulì conical sun hat — broad shallow cone, the festival's signature.
        col = pal(P.get("hat_c", (198, 162, 96)))
        brim_w = int(head_r * 2.6)
        apex = (hx, hy - head_r * 1.7)
        pygame.draw.polygon(scratch, col, [(hx - brim_w, hy - head_r * 0.2), apex, (hx + brim_w, hy - head_r * 0.2)])
        pygame.draw.polygon(scratch, _shade(col, -34),
                            [(hx - brim_w, hy - head_r * 0.2), apex, (hx + brim_w, hy - head_r * 0.2)], 1)
        pygame.draw.line(scratch, _shade(col, 16), (hx, hy - head_r * 0.2), apex, max(1, head_r // 4))
        pygame.draw.line(scratch, _shade(col, -30), (hx - brim_w, hy - head_r * 0.2),
                         (hx + brim_w, hy - head_r * 0.2), 1)  # brim edge
    elif hat == "bun":
        pygame.draw.circle(scratch, hair, (hx, hy - head_r), head_r)  # hair cap
        pygame.draw.circle(scratch, hair_dk, (hx - head_r // 3, hy - head_r * 1.3), max(2, head_r // 2))  # bun
        if "hairpin" in v.acc:
            pin = pal(P.get("pin", (220, 90, 100)))
            pygame.draw.line(scratch, pin, (hx - head_r // 3, hy - head_r * 1.5),
                             (hx + head_r // 2, hy - head_r * 1.7), 2)
    elif hat == "hood":
        col = pal(P.get("hat_c", coat))
        pygame.draw.circle(scratch, col, (hx, hy - head_r // 3), int(head_r * 1.35))
        # carve the face opening
        pygame.draw.circle(scratch, skin, (hx + head_r // 4, hy), int(head_r * 0.8))
        pygame.draw.arc(scratch, _shade(col, -30), pygame.Rect(hx - int(head_r * 1.35), hy - head_r // 3 - int(head_r * 1.35),
                        int(head_r * 2.7), int(head_r * 2.7)), math.radians(20), math.radians(340), max(1, head_r // 3))
    elif hat == "winter":
        # A padded winter cap with fur brim (snow).
        col = pal(P.get("hat_c", (150, 96, 80)))
        cap = pygame.Rect(hx - head_r, hy - head_r * 1.6, head_r * 2, int(head_r * 1.5))
        pygame.draw.ellipse(scratch, col, cap)
        fur = pal(P.get("fur", (224, 214, 198)))
        pygame.draw.line(scratch, fur, (hx - head_r, hy - head_r * 0.35),
                         (hx + head_r, hy - head_r * 0.35), max(2, head_r // 2))
    elif hat == "cloth":
        # A wrapped headcloth / kerchief (vendor women, cooks).
        col = pal(P.get("hat_c", (190, 90, 80)))
        pygame.draw.circle(scratch, col, (hx, hy - head_r // 2), int(head_r * 1.1))
        pygame.draw.circle(scratch, skin, (hx + head_r // 3, hy + head_r // 5), int(head_r * 0.75))
        pygame.draw.polygon(scratch, _shade(col, -22), [  # knot tail at back
            (hx - head_r, hy - head_r // 2), (hx - head_r * 1.5, hy), (hx - head_r * 0.8, hy + head_r // 3)])
    else:
        # Bare hair: a domed cap + a topknot/short crop depending on the role.
        pygame.draw.circle(scratch, hair, (hx, hy - head_r // 3), head_r)
        pygame.draw.arc(scratch, hair, pygame.Rect(hx - head_r, hy - head_r, head_r * 2, head_r * 2),
                        math.radians(0), math.radians(180), max(1, head_r // 2))
        if "topknot" in v.acc:
            pygame.draw.circle(scratch, hair_dk, (hx, hy - int(head_r * 1.4)), max(2, head_r // 2))

    # ---- held parasol / umbrella (drawn last, over the head) ----
    if "parasol" in v.acc or "umbrella" in v.acc:
        is_para = "parasol" in v.acc
        col = pal(P.get("canopy", (210, 80, 80) if not is_para else (236, 224, 210)))
        dark = _shade(col, -42)
        cr = int(head_r * 2.4)
        tilt = int(head_r * (0.5 if "umbrella" in v.acc else 0.2))
        cy = hy - int(head_r * 2.6)
        apex_x = hx + tilt
        canopy = [
            (hx - cr, cy), (apex_x - cr // 2, cy - cr // 2), (apex_x, cy - cr),
            (apex_x + cr // 2, cy - cr // 2), (hx + cr, cy),
            (hx + cr * 3 // 5, cy + 3), (hx, cy + 1), (hx - cr * 3 // 5, cy + 3),
        ]
        pygame.draw.polygon(scratch, col, canopy)
        pygame.draw.polygon(scratch, dark, canopy, max(1, head_r // 4))
        for tx in (-cr * 3 // 5, 0, cr * 3 // 5):
            pygame.draw.line(scratch, dark, (apex_x, cy - cr), (hx + tx, cy + (1 if tx == 0 else 3)), 1)
        pygame.draw.circle(scratch, dark, (apex_x, cy - cr), max(1, head_r // 4))
        if is_para:
            # a hanging tassel — the decorative oil-paper parasol cue
            pygame.draw.line(scratch, pal(P.get("tassel", (200, 70, 80))),
                             (hx + cr, cy), (hx + cr, cy + head_r), 2)
        # pole down to the hand
        pygame.draw.line(scratch, (110, 84, 56), (hx, cy + 1), (hx - 1, arm_y + torso_h // 3), max(2, head_r // 4))


# ── the variety pool ──────────────────────────────────────────────────────────

POOL = [
    V("Vendor — carrying pole",
      dict(coat=(150, 84, 70), trim=(214, 176, 96), sash=(214, 176, 96), hair=(46, 36, 30),
           skin="tan", hat="conical", hat_c=(196, 158, 92), basket=(176, 132, 78), goods=(224, 120, 60)),
      pose=("robe", "hurry"), acc=("pole",),
      build=1.05, height=1.0, roles="coat/trim/sash/hat_c/basket/goods · robe+hurry · pole"),

    V("Matron — basket on arm",
      dict(coat=(120, 150, 132), coat_dk=(72, 100, 88), trim=(220, 200, 150), hair=(40, 32, 28),
           skin="warm", hat="cloth", hat_c=(196, 92, 84), basket=(182, 138, 84), goods=(210, 90, 90)),
      pose=("stroll",), acc=("basket_arm",),
      build=1.1, height=0.95, roles="coat/coat_dk/hat_c(cloth)/basket · stroll · basket_arm"),

    V("Scholar — hands in sleeves",
      dict(coat=(86, 96, 150), coat_dk=(52, 60, 104), trim=(196, 196, 210), sash=(208, 200, 170),
           hair=(36, 30, 28), skin="fair", hat="bun"),
      pose=("robe", "hands_sleeve", "stroll"), acc=("topknot",),
      build=0.95, height=1.08, roles="coat/coat_dk/trim/sash · robe+hands_sleeve · topknot"),

    V("Lady — oil-paper parasol",
      dict(coat=(196, 132, 168), coat_dk=(140, 84, 122), trim=(240, 220, 180), sash=(220, 150, 120),
           hair=(34, 28, 26), skin="fair", hat="bun", pin=(220, 80, 96), canopy=(232, 170, 180),
           tassel=(208, 70, 90)),
      pose=("robe", "stroll"), acc=("parasol", "hairpin"),
      build=0.92, height=1.04, roles="coat/trim/sash/canopy/pin · robe · parasol+hairpin"),

    V("Porter — hurrying tunic",
      dict(coat=(170, 120, 70), coat_dk=(112, 76, 44), trousers=(74, 64, 56), hair=(40, 30, 24),
           skin="deep"),
      pose=("hurry", "swing_arm"), acc=(),
      build=1.15, height=1.02, roles="coat/coat_dk/trousers · hurry+swing_arm"),

    V("Cook — apron + headcloth",
      dict(coat=(96, 110, 120), coat_dk=(60, 72, 82), apron=(214, 206, 188), trousers=(70, 70, 78),
           hair=(38, 30, 26), skin="ruddy", hat="cloth", hat_c=(180, 80, 72)),
      pose=("swing_arm",), acc=("apron",),
      build=1.2, height=0.96, roles="coat/apron/hat_c(cloth) · swing_arm · apron"),

    V("Elder — beard + sleeves",
      dict(coat=(104, 80, 116), coat_dk=(66, 48, 78), trim=(206, 200, 210), sash=(196, 180, 150),
           hair=(206, 204, 196), beard=(212, 210, 202), skin="fair", hat="bun"),
      pose=("robe", "hands_sleeve"), acc=("beard", "topknot"),
      build=1.0, height=0.92, roles="coat/coat_dk/beard · robe+hands_sleeve · beard"),

    V("Youth — short tunic, swinging",
      dict(coat=(74, 150, 158), coat_dk=(44, 100, 108), trousers=(70, 64, 70), hair=(34, 28, 26),
           skin="warm"),
      pose=("hurry", "swing_arm"), acc=(),
      build=0.88, height=1.0, roles="coat/coat_dk/trousers · hurry+swing_arm"),

    V("Stout merchant — conical hat",
      dict(coat=(150, 130, 90), coat_dk=(100, 84, 56), trim=(90, 70, 60), sash=(160, 70, 64),
           hair=(40, 32, 26), skin="tan", hat="conical", hat_c=(188, 152, 90)),
      pose=("robe", "stroll", "hands_sleeve"), acc=(),
      build=1.28, height=0.98, roles="coat/sash/hat_c(conical) · robe+stroll · (stout build)"),

    # ── WEATHER MEMBERS ──
    V("Rain — red umbrella, hurrying",
      dict(coat=(96, 108, 140), coat_dk=(58, 68, 96), trousers=(64, 66, 78), hair=(38, 30, 26),
           skin="warm", canopy=(212, 76, 76)),
      pose=("hurry", "swing_arm"), acc=("umbrella",),
      build=1.0, height=1.0, roles="coat/canopy(red) · hurry · umbrella  [RAIN]"),

    V("Rain — hooded oilskin",
      dict(coat=(86, 116, 110), coat_dk=(52, 78, 74), trim=(70, 96, 92), hair=(38, 30, 26),
           skin="warm", hat="hood", hat_c=(72, 100, 96)),
      pose=("robe", "hurry"), acc=(),
      build=1.05, height=1.0, roles="coat/hat_c(hood) · robe+hurry · hood  [RAIN]"),

    V("Rain — blue umbrella, calm",
      dict(coat=(118, 110, 96), coat_dk=(78, 72, 60), trim=(200, 188, 160), sash=(150, 120, 90),
           hair=(40, 32, 26), skin="fair", hat="bun", canopy=(74, 122, 198)),
      pose=("robe", "stroll"), acc=("umbrella",),
      build=0.95, height=1.02, roles="coat/canopy(blue) · robe+stroll · umbrella  [RAIN]"),

    V("Snow — heavy padded coat",
      dict(coat=(168, 92, 78), coat_dk=(116, 60, 52), trim=(226, 216, 200), fur=(228, 220, 206),
           hair=(40, 32, 28), skin="ruddy", hat="winter", hat_c=(150, 88, 74)),
      pose=("hurry",), acc=("bundle",),
      build=1.3, height=0.98, roles="coat/fur/hat_c(winter)/bundle · hurry · winter+bundle  [SNOW]"),

    V("Snow — bundled with scarf",
      dict(coat=(96, 110, 150), coat_dk=(60, 72, 104), trim=(214, 110, 96), fur=(222, 214, 200),
           hair=(40, 32, 28), skin="fair", hat="winter", hat_c=(86, 100, 138)),
      pose=("stroll", "hands_sleeve"), acc=(),
      build=1.22, height=0.96, roles="coat/trim(scarf)/fur · stroll+hands_sleeve · winter  [SNOW]"),
]


# ── sheet assembly ────────────────────────────────────────────────────────────

def baked(v, footprint_h, night, t):
    """Author at 3x then smoothscale DOWN — the higher-resolution path."""
    box_h = footprint_h * 3
    box_w = int(box_h * 0.72)
    scratch = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    draw_person(scratch, v, night, t)
    fw = max(1, int(box_w / 3))
    return pygame.transform.smoothscale(scratch, (fw, footprint_h))


def main():
    pygame.init()
    font = pygame.font.SysFont("dejavusans", 11)
    font_sm = pygame.font.SysFont("dejavusans", 9)
    font_hd = pygame.font.SysFont("dejavusans", 16, bold=True)

    cols = 4
    rows = (len(POOL) + cols - 1) // cols
    tile_w, tile_h = 250, 150
    pad_top = 78
    sheet_w = cols * tile_w + 24
    sheet_h = pad_top + rows * tile_h + 30

    sheet = pygame.Surface((sheet_w, sheet_h))

    # Two background bands so each tile shows day (left half) + night (right half),
    # proving the palette stays legible across the day->night arc.
    DAY_GROUND = (150, 134, 110)
    NIGHT_GROUND = _mix((150, 134, 110), (54, 64, 96), 0.62)
    DAY_SKY = (176, 168, 142)
    NIGHT_SKY = (26, 30, 56)

    sheet.fill((40, 42, 50))
    # header
    pygame.draw.rect(sheet, (24, 26, 34), (0, 0, sheet_w, pad_top - 12))
    sheet.blit(font_hd.render("SKYBIT PROMENADE — ADULT PEDESTRIAN VARIETY POOL (round 1)", True, (240, 232, 210)), (14, 10))
    sheet.blit(font_sm.render(
        "One shared body drawer + per-figure Variant (palette roles / pose / accessory flags). Authored at 3x, smoothscaled DOWN to on-screen size.",
        True, (190, 196, 200)), (14, 32))
    sheet.blit(font_sm.render(
        "Each tile: DAY half + NIGHT half (night-cooled, <=150 luma cap).  Per figure L->R: FAR ~14px  ·  NEAR ~22px  ·  4-6x zoom inset (day & night).",
        True, (190, 196, 200)), (14, 46))

    FAR_H, NEAR_H, ZOOM_H = 14, 22, 70
    t = 1.1  # a pleasant mid-gait frame

    for i, v in enumerate(POOL):
        cxr, cyr = i % cols, i // cols
        ox = 12 + cxr * tile_w
        oy = pad_top + cyr * tile_h

        # tile background: day left, night right
        half = tile_w // 2
        for h2 in range(tile_h - 30):
            ty = oy + h2
            f = h2 / (tile_h - 30)
            sheet.fill(_mix(DAY_SKY, DAY_GROUND, min(1.0, f * 1.4)), (ox, ty, half, 1))
            sheet.fill(_mix(NIGHT_SKY, NIGHT_GROUND, min(1.0, f * 1.4)), (ox + half, ty, tile_w - half, 1))
        ground_line = oy + tile_h - 46
        pygame.draw.line(sheet, _shade(DAY_GROUND, -24), (ox, ground_line), (ox + half, ground_line), 1)
        pygame.draw.line(sheet, _shade(NIGHT_GROUND, -18), (ox + half, ground_line), (ox + tile_w, ground_line), 1)

        # label
        weather = " [WEATHER]" if any(w in v.roles for w in ("RAIN", "SNOW")) else ""
        lbl = font.render(f"{i+1}. {v.name}", True, (245, 238, 220))
        sheet.blit(lbl, (ox + 6, oy + 4))

        def place(night, side_x):
            far = baked(v, FAR_H, night, t)
            near = baked(v, NEAR_H, night, t)
            zoom = pygame.transform.scale(baked(v, ZOOM_H // 5, night, 0.7), (int(ZOOM_H * 0.72), ZOOM_H))
            # far + near feet on ground line
            sheet.blit(far, (side_x, ground_line - FAR_H))
            sheet.blit(near, (side_x + 22, ground_line - NEAR_H))
            sheet.blit(zoom, (side_x + 52, ground_line - ZOOM_H))
            return zoom

        place(0.0, ox + 8)
        place(1.0, ox + half + 8)

        # tiny day/night markers
        sheet.blit(font_sm.render("day", True, (60, 50, 40)), (ox + 8, ground_line + 4))
        sheet.blit(font_sm.render("night", True, (200, 206, 220)), (ox + half + 8, ground_line + 4))
        # roles/flags note
        note = font_sm.render(v.roles, True, (210, 214, 218))
        sheet.blit(note, (ox + 6, oy + tile_h - 26))

    pygame.draw.rect(sheet, (60, 64, 74), (0, 0, sheet_w, sheet_h), 2)

    out = "/home/user/skybit/docs/sidewalk_overhaul/pedestrians/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
