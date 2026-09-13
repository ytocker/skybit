"""Design-only render: a pillar built by STACKING the various small skulls from
the chosen king-skull design (Asthi-Dakini SWITCHED+BIG) one on top of another,
pagoda-style — plus a second version with a skewer threaded down through them.

Reuses the chosen design's own skull functions (crown_skull / palm_skull /
palm_cabochon) + palette + house helpers, imported directly from its render
script. Not wired into the game; produces review sheets under docs/.
"""
import os, sys, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASTHI = os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye")
sys.path.insert(0, ASTHI)

import pygame
pygame.init()
import render_switchbig as sk   # the chosen design — defines the skull functions + palette

OUT = os.path.join(ROOT, "docs/skull_king_stack")
os.makedirs(OUT, exist_ok=True)

SS = 8                     # supersample, matching the source ELEVATED pipeline
PIPE_W = 58                # the game's pillar width
R = 23                     # skull radius (final px) — ~2.3*R spans the column
S_UNIT = R / 12.0          # the source's r≈12*s convention → correct line weights
PITCH = 34                 # vertical centre-to-centre (skulls overlap → dense totem)

# The 12 various small skulls of the design, interleaved crown / palm so each
# column shows the bare relic skulls AND the jewelled cradled ones (gem colour).
SKULLS = []
for i in range(6):
    SKULLS.append(("crown", i))
    SKULLS.append(("palm", i))


def _palm_skull_bare(surf, cx, cy, r, s, idx=0):
    """The cradled-skull CORE of render_switchbig.palm_skull, WITHOUT the open
    palm cup / finger-ticks (the 'hands') — per the user's request to stack just
    the skulls. Cranium sized to the full radius so it fills like the crown skulls.
    Faithfully mirrors the source's per-skull personality table + drawing."""
    INK, BEAD, BEAD_BR = sk.INK, sk.BEAD, sk.BEAD_BR
    BONE_D, BONE_DD, GOLD = sk.BONE_D, sk.BONE_DD, sk.GOLD
    ow1 = max(1, int(1.4 * s))
    ow_thin = max(1, int(1.0 * s))
    PROFILE = [
        dict(tilt=-0.16, cw=0.96, ch=1.12, jaw="agape", teeth=5, sut="zig", gem=True,  chip=False),
        dict(tilt= 0.10, cw=1.14, ch=0.96, jaw="closed", teeth=6, sut="dots", gem=False, chip=False),
        dict(tilt=-0.30, cw=0.88, ch=1.04, jaw="cracked", teeth=3, sut="zig", gem="socket", chip=True),
        dict(tilt= 0.06, cw=1.06, ch=0.90, jaw="agape", teeth=7, sut="line", gem=False, chip=False),
        dict(tilt= 0.22, cw=0.90, ch=1.10, jaw="closed", teeth=5, sut="dots", gem=True,  chip=False),
        dict(tilt=-0.08, cw=1.02, ch=1.00, jaw="cracked", teeth=4, sut="zig", gem=False, chip=True),
    ]
    p = PROFILE[idx % len(PROFILE)]
    t = 0.0                           # straight pose (was p["tilt"]) — no rotation
    ct, st = math.cos(t), math.sin(t)

    def rot(dx, dy):
        return (cx + dx * ct - dy * st, cy + dx * st + dy * ct)

    cw, ch = p["cw"], p["ch"]
    cr = r * 0.96                     # full-size cranium (no palm to nest into)

    dome = []
    for ang_deg in range(-180, 1, 20):
        a = math.radians(ang_deg)
        dome.append(rot(math.cos(a) * cr * cw, math.sin(a) * cr * ch))
    dome.append(rot(cr * cw * 0.78, cr * ch * 0.30))
    dome.append(rot(cr * cw * 0.52, cr * ch * 0.72))
    dome.append(rot(-cr * cw * 0.52, cr * ch * 0.72))
    dome.append(rot(-cr * cw * 0.78, cr * ch * 0.30))
    sk.triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in dome], ow=ow1)
    sheen = [rot(-cr * cw * 0.62, -cr * ch * 0.30),
             rot(-cr * cw * 0.12, -cr * ch * 0.74),
             rot(-cr * cw * 0.04, -cr * ch * 0.40),
             rot(-cr * cw * 0.50, -cr * ch * 0.04)]
    pygame.draw.polygon(surf, BEAD_BR, [(int(x), int(y)) for x, y in sheen])

    if p["sut"] == "zig":
        zp = []
        for j in range(5):
            zx = -cr * 0.34 + j * (cr * 0.68 / 4)
            zy = -cr * ch * 0.62 + (cr * 0.10 if j % 2 else -cr * 0.06)
            zp.append(rot(zx, zy))
        pygame.draw.lines(surf, BONE_DD, False, [(int(x), int(y)) for x, y in zp], ow_thin)
    elif p["sut"] == "dots":
        for j in range(5):
            zx = -cr * 0.34 + j * (cr * 0.68 / 4)
            dx, dy = rot(zx, -cr * ch * 0.60)
            pygame.draw.circle(surf, BONE_DD, (int(dx), int(dy)), max(1, int(0.9 * s)))
            if j % 2 == 0:
                gx, gy = rot(zx, -cr * ch * 0.60)
                pygame.draw.circle(surf, GOLD, (int(gx), int(gy)), max(1, int(0.8 * s)))
    else:
        pygame.draw.line(surf, BONE_DD,
                         (int(rot(0, -cr * ch * 0.80)[0]), int(rot(0, -cr * ch * 0.80)[1])),
                         (int(rot(0, -cr * 0.10)[0]), int(rot(0, -cr * 0.10)[1])), ow_thin)

    br0 = rot(-cr * 0.46, -cr * 0.02)
    br1 = rot(cr * 0.46, -cr * 0.02)
    pygame.draw.line(surf, BONE_D, (int(br0[0]), int(br0[1])), (int(br1[0]), int(br1[1])),
                     max(1, int(1.4 * s)))

    hollow = [rot(cr * 0.20, cr * 0.18), rot(cr * 0.60, cr * 0.20),
              rot(cr * 0.52, cr * 0.56), rot(cr * 0.18, cr * 0.50)]
    pygame.draw.polygon(surf, BONE_D, [(int(x), int(y)) for x, y in hollow])

    socket_r = cr * 0.30
    for sgn in (-1, 1):
        ecx, ecy = rot(sgn * cr * 0.40, cr * 0.14)
        ecx, ecy = int(ecx), int(ecy)
        pygame.draw.circle(surf, BONE_D, (ecx, ecy), int(socket_r + max(1, 1.2 * s)))
        pygame.draw.circle(surf, INK, (ecx, ecy), int(socket_r))
        pygame.draw.circle(surf, BONE_DD, (ecx, ecy), int(socket_r * 0.62))
        pygame.draw.circle(surf, INK, (ecx, ecy), int(socket_r * 0.34))
    if p["gem"] == "socket":
        scx2, scy2 = rot(-cr * 0.40, cr * 0.14)
        sk.palm_cabochon(surf, (scx2, scy2), max(2, int(socket_r * 0.66)), s)

    n_top = rot(0, cr * 0.30)
    n_l = rot(-cr * 0.16, cr * 0.58)
    n_r = rot(cr * 0.16, cr * 0.58)
    pygame.draw.polygon(surf, INK, [(int(n_top[0]), int(n_top[1])),
                                    (int(n_l[0]), int(n_l[1])),
                                    (int(n_r[0]), int(n_r[1]))])

    jl, jr = -cr * 0.40, cr * 0.40
    if p["jaw"] == "closed":
        jaw = [rot(jl, cr * 0.74), rot(jr, cr * 0.74),
               rot(jr * 0.70, cr * 1.04), rot(jl * 0.70, cr * 1.04)]
        sk.triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        teeth_y0, teeth_y1 = cr * 0.74, cr * 1.00
    elif p["jaw"] == "agape":
        gap = [rot(jl * 0.86, cr * 0.70), rot(jr * 0.86, cr * 0.70),
               rot(jr * 0.70, cr * 1.06), rot(jl * 0.70, cr * 1.06)]
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in gap])
        jaw = [rot(jl * 0.74, cr * 1.06), rot(jr * 0.74, cr * 1.06),
               rot(jr * 0.54, cr * 1.34), rot(jl * 0.54, cr * 1.34)]
        sk.triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        teeth_y0, teeth_y1 = cr * 0.70, cr * 0.94
    else:
        jaw = [rot(jl, cr * 0.74), rot(jr * 0.55, cr * 0.74),
               rot(jr * 0.20, cr * 1.02), rot(jl * 0.78, cr * 1.06)]
        sk.triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        pygame.draw.line(surf, BONE_DD,
                         (int(rot(jr * 0.55, cr * 0.76)[0]), int(rot(jr * 0.55, cr * 0.76)[1])),
                         (int(rot(jr * 0.30, cr * 0.98)[0]), int(rot(jr * 0.30, cr * 0.98)[1])),
                         ow_thin)
        teeth_y0, teeth_y1 = cr * 0.74, cr * 1.00

    nt = p["teeth"]
    for j in range(nt):
        fx = -cr * 0.34 + j * (cr * 0.68 / max(1, nt - 1))
        if p["chip"] and j == nt // 2:
            continue
        tp0 = rot(fx, teeth_y0)
        tp1 = rot(fx, teeth_y1)
        pygame.draw.line(surf, INK, (int(tp0[0]), int(tp0[1])),
                         (int(tp1[0]), int(tp1[1])), max(1, int(1.0 * s)))

    if p["gem"] is True:
        gx, gy = rot(0, -cr * 0.20)
        sk.palm_cabochon(surf, (gx, gy), max(2, int(cr * 0.26)), s)


def _crown_skull_straight(surf, cx, cy, r, s, lit=False, idx=0):
    """render_switchbig.crown_skull with `lean` forced to 0 (straight, upright
    pose). Everything else — the per-relic silhouette variety, suture, jaw, pip —
    is preserved verbatim."""
    CROWN_BONE, CROWN_BONE_D, CROWN_SH = sk.CROWN_BONE, sk.CROWN_BONE_D, sk.CROWN_SH
    INK, GOLD_D, CYAN_D = sk.INK, sk.GOLD_D, sk.CYAN_D
    ow1 = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))
    CROWN_PROFILE = [
        dict(cw=0.88, ch=1.18, heart=False, sut="dots", brow=True,  jaw="set",   pip=True,  chip=False),
        dict(cw=1.16, ch=0.96, heart=False, sut="zig",  brow=False, jaw="plain", pip=False, chip=False),
        dict(cw=1.10, ch=0.86, heart=True,  sut="dots", brow=True,  jaw="set",   pip=True,  chip=False),
        dict(cw=1.00, ch=1.02, heart=False, sut="zig",  brow=True,  jaw="plain", pip=False, chip=True),
        dict(cw=1.02, ch=1.06, heart=True,  sut="line", brow=False, jaw="set",   pip=False, chip=False),
        dict(cw=1.08, ch=0.92, heart=False, sut="zig",  brow=True,  jaw="plain", pip=False, chip=True),
    ]
    p = CROWN_PROFILE[idx % len(CROWN_PROFILE)]
    cw, ch, lean = p["cw"], p["ch"], 0.0      # lean → 0 (straight)

    dome = []
    for ang_deg in range(-180, 1, 18):
        a = math.radians(ang_deg)
        dx = math.cos(a) * r * cw
        dy = math.sin(a) * r * ch
        dx += lean * r * (-dy / max(1.0, r))
        if p["heart"] and abs(math.cos(a)) < 0.34 and math.sin(a) < -0.4:
            dy += r * 0.22
        dome.append((cx + dx, cy + dy))
    dome.append((cx + r * cw * 0.74 + lean * r * 0.2, cy + r * ch * 0.34))
    dome.append((cx - r * cw * 0.74 + lean * r * 0.2, cy + r * ch * 0.34))
    sk.triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in dome], ow=ow1)
    sheen = [(cx - r * cw * 0.58, cy - r * ch * 0.10),
             (cx - r * cw * 0.10 + lean * r * 0.2, cy - r * ch * 0.66),
             (cx - r * cw * 0.02, cy - r * ch * 0.34),
             (cx - r * cw * 0.46, cy + r * ch * 0.02)]
    pygame.draw.polygon(surf, CROWN_SH, [(int(x), int(y)) for x, y in sheen])

    seam_y = cy - r * ch * 0.56
    if p["sut"] == "zig":
        zp = [(cx - r * 0.34 + j * (r * 0.68 / 4),
               seam_y + (r * 0.10 if j % 2 else -r * 0.06)) for j in range(5)]
        pygame.draw.lines(surf, CROWN_BONE_D, False, [(int(x), int(y)) for x, y in zp], ow_thin)
    elif p["sut"] == "dots":
        for j in range(5):
            zx = cx - r * 0.34 + j * (r * 0.68 / 4)
            pygame.draw.circle(surf, CROWN_BONE_D, (int(zx), int(seam_y)), max(1, int(0.9 * s)))
            if j % 2 == 0:
                pygame.draw.circle(surf, GOLD_D, (int(zx), int(seam_y)), max(1, int(0.8 * s)))
    else:
        pygame.draw.line(surf, CROWN_BONE_D, (int(cx), int(cy - r * ch * 0.78)),
                         (int(cx), int(cy - r * 0.06)), ow_thin)

    if p["brow"]:
        pygame.draw.line(surf, CROWN_BONE_D,
                         (int(cx - r * 0.46), int(cy - r * 0.02)),
                         (int(cx + r * 0.46), int(cy - r * 0.02)), max(1, int(1.3 * s)))

    if p["jaw"] == "set":
        jaw = [(cx - r * 0.44, cy + r * 0.52), (cx + r * 0.44, cy + r * 0.52),
               (cx + r * 0.26, cy + r * 0.98), (cx - r * 0.26, cy + r * 0.98)]
    else:
        jaw = [(cx - r * 0.54, cy + r * 0.50), (cx + r * 0.54, cy + r * 0.50),
               (cx + r * 0.38, cy + r * 1.02), (cx - r * 0.38, cy + r * 1.02)]
    sk.triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in jaw], ow=max(1, int(1.2 * s)))

    eye_c = CYAN_D if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.12)))

    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))

    ty = cy + int(r * 0.70)
    pygame.draw.line(surf, INK, (cx - int(r * 0.32), ty), (cx + int(r * 0.32), ty),
                     max(1, int(1.2 * s)))
    for j in range(3):
        tx = cx - int(r * 0.24) + j * int(r * 0.24)
        if p["chip"] and j == 1:
            continue
        pygame.draw.line(surf, INK, (tx, ty - int(r * 0.08)), (tx, ty + int(r * 0.10)),
                         max(1, int(1.0 * s)))

    if p["pip"]:
        bg_y = cy - int(r * 0.28)
        pygame.draw.circle(surf, GOLD_D, (cx, bg_y), max(1, int(r * 0.18)))
        pygame.draw.circle(surf, CYAN_D, (cx, bg_y), max(1, int(r * 0.11)))


def _draw_skull(big, kind, idx, cx, cy, *, lit=False):
    r = int(R * SS)
    s = S_UNIT * SS
    if kind == "crown":
        _crown_skull_straight(big, int(cx), int(cy), r, s, lit=lit, idx=idx)
    else:
        _palm_skull_bare(big, int(cx), int(cy), r, s, idx=idx)


_SK_HW = int(4.5 * SS)                       # skewer shaft half-width (inside 58px)


def _rod_seg(big, cx, ya, yb):
    """A short ink-keyed bone rod segment with a gold marrow seam, ya→yb."""
    s = S_UNIT * SS
    hw = _SK_HW
    y, h = int(min(ya, yb)), int(abs(yb - ya))
    pygame.draw.rect(big, sk.INK, (cx - hw - int(1.4 * s), y, 2 * (hw + int(1.4 * s)), h))
    pygame.draw.rect(big, sk.BONE, (cx - hw, y, 2 * hw, h))
    pygame.draw.rect(big, sk.BONE_SH, (cx - hw, y, max(1, int(1.6 * s)), h))
    pygame.draw.rect(big, sk.GOLD_D, (cx - int(1.6 * s), y, int(3.2 * s), h))
    pygame.draw.rect(big, sk.GOLD, (cx - int(0.9 * s), y, int(1.8 * s), h))


def _skewer_bg(big, cx, y_gap, y_far):
    """The full shaft drawn BEHIND the skulls (so it shows in any sky between
    tiers), plus a small bound tail nub at the far end."""
    _rod_seg(big, int(cx), y_gap, y_far)


def _skewer_thread(big, cx, centres, point_y, point_dir):
    """Drawn ON TOP of the skulls: a visible rod nub piercing each inter-skull
    seam (so the skewer reads as threaded through), and a barbed point juts into
    the gap at the near end."""
    s = S_UNIT * SS
    hw = _SK_HW
    cx = int(cx)
    # rod nub at every seam between adjacent skulls + just outside the far skull
    seams = [(centres[i] + centres[i + 1]) / 2.0 for i in range(len(centres) - 1)]
    if centres:
        seams.append(centres[-1] - point_dir * (R * 0.95))   # tail past the far skull
    for ym in seams:
        _rod_seg(big, cx, (ym - 7) * SS, (ym + 7) * SS)
    # barbed point at the gap end (on top of the focal skull's brow)
    tip = (point_y + point_dir * 26) * SS
    base = (point_y + point_dir * 2) * SS
    barb = int(11 * SS)
    pts = [(cx, tip), (cx - hw - barb, base + point_dir * int(9 * SS)),
           (cx - hw, base), (cx + hw, base),
           (cx + hw + barb, base + point_dir * int(9 * SS))]
    sk.triad_blob(big, sk.BONE, [(int(x), int(y)) for x, y in pts], ow=max(1, int(1.4 * s)))
    pygame.draw.line(big, sk.GOLD, (cx, base), (cx, tip), max(1, int(1.8 * s)))
    pygame.draw.circle(big, sk.GOLD_BR, (cx, int(tip)), max(1, int(2.2 * s)))


def render_half(H, *, cap, with_skewer):
    """One pillar half, skulls upright, the lit focal skull at the gap edge.
    cap='bottom' → TOP pillar (gap below); cap='top' → BOTTOM pillar (gap above)."""
    big = pygame.Surface((PIPE_W * SS, H * SS), pygame.SRCALPHA)
    cx = PIPE_W * SS // 2

    margin = int(R * 1.05)
    if cap == "bottom":
        focal_y = H - margin
        step = -PITCH
        point_dir = +1                       # point juts downward into the gap
        gap_edge_y = H * SS
    else:
        focal_y = margin
        step = +PITCH
        point_dir = -1                       # point juts upward into the gap
        gap_edge_y = 0

    # tier centres from the gap edge outward until off the far end
    centres = []
    y = focal_y
    while -R * 0.6 <= y <= H + R * 0.6:
        centres.append(y)
        y += step

    if with_skewer:
        _skewer_bg(big, cx, gap_edge_y, centres[-1] * SS)

    # draw far → near so nearer (lower-index) skulls overlap on top toward the gap
    for i, cy in reversed(list(enumerate(centres))):
        # thin gold bead collar seating each skull on the one below (design's tell)
        sk.bead_strand(big, [(cx - int(R * 0.8 * SS), int((cy + R * 0.72) * SS)),
                             (cx + int(R * 0.8 * SS), int((cy + R * 0.72) * SS))],
                       int(2.6 * S_UNIT * SS), S_UNIT * SS, gold_every=2)
        if i == 0:
            _draw_skull(big, "crown", 2, cx, cy * SS, lit=True)   # lit focal (centre relic)
        else:
            kind, idx = SKULLS[i % len(SKULLS)]
            _draw_skull(big, kind, idx, cx, cy * SS)

    if with_skewer:
        _skewer_thread(big, cx, centres, focal_y, point_dir)

    small = pygame.transform.smoothscale(big, (PIPE_W, H))
    return sk.grow_outline(small, sk.INK + (255,), 1)


# ── compositing the review sheets ─────────────────────────────────────────────
def _sky(w, h, night=False):
    top = sk.NIGHT_T if night else sk.DAY_SKY_T
    bot = sk.lerp(top, (255, 255, 255), 0.0 if night else 0.45)
    if night:
        bot = sk.lerp(top, (60, 70, 110), 0.7)
    surf = pygame.Surface((w, h))
    for yy in range(h):
        surf.fill(sk.lerp(top, bot, yy / max(1, h - 1)), (0, yy, w, 1))
    return surf


def _pair_panel(with_skewer, night, half_h=190, gap=150):
    H = half_h * 2 + gap
    panel = _sky(PIPE_W + 24, H, night=night)
    top = render_half(half_h, cap="bottom", with_skewer=with_skewer)
    bot = render_half(half_h, cap="top", with_skewer=with_skewer)
    x = 12
    panel.blit(top, (x, 0))
    panel.blit(bot, (x, half_h + gap))
    return panel


def _label(surf, text, x, y, night=False):
    f = sk.font(15) if hasattr(sk, "font") else pygame.font.SysFont("sans", 15)
    col = (235, 230, 222) if not night else (220, 224, 240)
    surf.blit(f.render(text, True, (20, 16, 22)), (x + 1, y + 1))
    surf.blit(f.render(text, True, col), (x, y))


def build_variant_sheet(with_skewer, title, fname):
    day = _pair_panel(with_skewer, night=False)
    night = _pair_panel(with_skewer, night=True)
    # a true-58px in-game crop (just the gap region) on day sky
    crop_h = 150
    crop = _sky(PIPE_W + 24, crop_h, night=False)
    top = render_half(crop_h // 2, cap="bottom", with_skewer=with_skewer)
    bot = render_half(crop_h // 2, cap="top", with_skewer=with_skewer)
    crop.blit(top, (12, -crop_h // 2 + 70))
    crop.blit(bot, (12, crop_h - 70))

    pad, head = 24, 56
    W = day.get_width() + night.get_width() + crop.get_width() + pad * 4
    Ht = head + max(day.get_height(), night.get_height(), crop_h) + pad * 2
    sheet = pygame.Surface((W, Ht))
    sheet.fill((26, 24, 30))
    _label(sheet, title, pad, 16)
    x = pad
    y = head
    for cap, surf, n in (("DAY", day, False), ("NIGHT", night, True), ("1x crop", crop, False)):
        sheet.blit(surf, (x, y))
        _label(sheet, cap, x, y + surf.get_height() + 4, night=False)
        x += surf.get_width() + pad
    out = os.path.join(OUT, fname)
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())
    return sheet


def build_showcase(stack_sheet, skewer_sheet):
    pad = 0
    W = max(stack_sheet.get_width(), skewer_sheet.get_width())
    Ht = stack_sheet.get_height() + skewer_sheet.get_height()
    sheet = pygame.Surface((W, Ht))
    sheet.fill((26, 24, 30))
    sheet.blit(stack_sheet, (0, 0))
    sheet.blit(skewer_sheet, (0, stack_sheet.get_height()))
    out = os.path.join(OUT, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


# ── EARLIER crown skull (round 9 — the last single-design crown before the
#    idx 0-5 variance landed at round 10). Vendored from the round-9 source with
#    its OWN warm bone-jewel palette (namespaced _O_/_o_) so it reads as the
#    period-correct "before" against the current high-variance crown row — a
#    same-warm crown drawn in the chosen design's later palette would not. ──────
_O_INK        = (28, 22, 26)
_O_CROWN_BONE = (170, 162, 152)
_O_CYAN_BR    = (188, 248, 252)
_O_CYAN_D     = (40, 132, 150)
_O_GOLD       = (212, 162, 60)


def _o_lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _o_triad_blob(surf, color, pts, ow=2):
    pygame.draw.polygon(surf, _O_INK, pts)
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, _O_INK, pts, ow)


def _o_triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    pygame.draw.circle(surf, _O_INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, _o_lerp(color, _O_INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)), int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, _o_lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)), max(1, int(r * 0.26)))
    pygame.draw.circle(surf, _O_INK, c, r, ow)


def _crown_skull_orig(surf, cx, cy, r, s, lit=False):
    """Round-9 crown skull — domed cranium, two dark sockets, stub jaw. A notch
    darker/cooler than the warm-ivory body so it sits the dimmest value tier and
    keeps its shape against both body and sky. `lit` swaps the centre skull's
    eyes + the only crown glow allowed: a tiny gold-bezel cyan brow pip."""
    _o_triad_circle(surf, _O_CROWN_BONE, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    _o_triad_blob(surf, _O_CROWN_BONE, jaw, ow=max(1, int(1.2 * s)))
    eye_c = _O_CYAN_BR if lit else _O_INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, _O_INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    # subtle bone-jewel echo on the lit centre skull only — gold-bezel cyan brow
    # pip tying the crown to her bead identity; two dots keep the silhouette clean.
    if lit:
        bg_y = cy - int(r * 0.30)
        pygame.draw.circle(surf, _O_GOLD, (cx, bg_y), max(1, int(r * 0.18)))
        pygame.draw.circle(surf, _O_CYAN_D, (cx, bg_y), max(1, int(r * 0.11)))
    pygame.draw.circle(surf, _O_INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, _O_INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))


def _skull_chip(kind, idx, cell_w, cell_h, *, lit=False):
    """One skull rendered on transparent ground, smoothscaled + outlined."""
    ssr = 6
    big = pygame.Surface((cell_w * ssr, cell_h * ssr), pygame.SRCALPHA)
    r = int(min(cell_w, cell_h) * 0.40)
    rb = r * ssr
    s = (r / 12.0) * ssr
    cx = cell_w * ssr // 2
    cy = int(cell_h * ssr * 0.52)
    if kind == "crown":
        _crown_skull_straight(big, cx, cy, rb, s, lit=lit, idx=idx)
    elif kind == "crown_orig":
        _crown_skull_orig(big, cx, cy, rb, s, lit=lit)
    else:
        _palm_skull_bare(big, cx, cy, rb, s, idx=idx)
    small = pygame.transform.smoothscale(big, (cell_w, cell_h))
    return sk.grow_outline(small, sk.INK + (255,), 1)


# ── NEW-8 showcase skulls ─────────────────────────────────────────────────────
# Eight extra designs (a wild + crown-relic mix) matured each in its own loop
# under docs/skull_king_stack/new8/<slug>/. Their draw() fns are imported here so
# the figure stays the single source of truth. WHY per-skull r_frac/cy_frac: the
# appendage-heavy ones (horns out, antlers up, fangs below) would clip the
# 116x132 cell at the default 0.40/0.52 placement, so each carries the cell fit it
# was tuned against; lit=True lets the wild four show their capped cyan device.
import importlib.util as _ilu

_NEW8_DIR = os.path.join(ROOT, "docs/skull_king_stack/new8")
_NEW8_SPEC = [
    ("simple-skull",   "render_simple_skull.py",   0.30, 0.46, False),
    ("antler-stag",    "render_antler_stag.py",     0.33, 0.66, True),
    ("sabertooth-maw", "render_sabertooth_maw.py",  0.34, 0.34, True),
    ("cyclops-brow",   "render_cyclops_brow.py",    0.40, 0.52, True),
    ("longjaw-relic",  "render_longjaw_relic.py",   0.40, 0.30, False),
    ("cracked-half",   "render_cracked_half.py",    0.40, 0.52, False),
    ("flat-slab",      "render_flat_slab.py",       0.40, 0.52, False),
    ("keyhole-relic",  "render_keyhole_relic.py",   0.40, 0.52, False),
]


def _new8_load(slug, fname):
    spec = _ilu.spec_from_file_location("new8_" + slug.replace("-", "_"),
                                        os.path.join(_NEW8_DIR, slug, fname))
    m = _ilu.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_NEW8 = {slug: (_new8_load(slug, fn).draw, rf, cyf, lit)
         for (slug, fn, rf, cyf, lit) in _NEW8_SPEC}


def _new8_chip(slug, cell_w, cell_h):
    """Chip for one of the eight new designs, placed with its own cell fit."""
    draw, rf, cyf, lit = _NEW8[slug]
    ssr = 6
    big = pygame.Surface((cell_w * ssr, cell_h * ssr), pygame.SRCALPHA)
    r = int(min(cell_w, cell_h) * rf) * ssr
    s = (int(min(cell_w, cell_h) * rf) / 12.0) * ssr
    draw(big, cell_w * ssr // 2, int(cell_h * ssr * cyf), r, s, lit)
    return sk.grow_outline(pygame.transform.smoothscale(big, (cell_w, cell_h)),
                           sk.INK + (255,), 1)


# ── CLASSIC-8 showcase skulls ─────────────────────────────────────────────────
# Eight plain/simple skulls — the timeless-skull counterpart to new8, matured each
# in its own loop under docs/skull_king_stack/classic8/<slug>/. Same draw() contract;
# all lit=False (plain BONE tier — no cyan device). Per-skull cy_frac/r_frac carry
# the cell fit each was tuned against (tall egg, wide cheeks, jawless mass, etc.).
_CLASSIC8_DIR = os.path.join(ROOT, "docs/skull_king_stack/classic8")
_CLASSIC8_SPEC = [
    ("round-cap",        "render_round_cap.py",        0.30, 0.46),
    ("egg-dome",         "render_egg_dome.py",         0.28, 0.50),
    ("broad-zygo",       "render_broad_zygo.py",       0.27, 0.50),
    ("square-jaw",       "render_square_jaw.py",       0.27, 0.46),
    ("calvaria",         "render_calvaria.py",         0.32, 0.46),
    ("gaunt-hollow",     "render_gaunt_hollow.py",     0.29, 0.48),
    ("child-skull",      "render_child_skull.py",      0.30, 0.48),
    ("flat-brow-robust", "render_flat_brow_robust.py", 0.30, 0.50),
]


def _classic8_load(slug, fname):
    spec = _ilu.spec_from_file_location("classic8_" + slug.replace("-", "_"),
                                        os.path.join(_CLASSIC8_DIR, slug, fname))
    m = _ilu.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_CLASSIC8 = {slug: (_classic8_load(slug, fn).draw, rf, cyf)
             for (slug, fn, rf, cyf) in _CLASSIC8_SPEC}


def _classic8_chip(slug, cell_w, cell_h):
    """Chip for one of the eight classic designs, placed with its own cell fit."""
    draw, rf, cyf = _CLASSIC8[slug]
    ssr = 6
    big = pygame.Surface((cell_w * ssr, cell_h * ssr), pygame.SRCALPHA)
    r = int(min(cell_w, cell_h) * rf) * ssr
    s = (int(min(cell_w, cell_h) * rf) / 12.0) * ssr
    draw(big, cell_w * ssr // 2, int(cell_h * ssr * cyf), r, s, False)
    return sk.grow_outline(pygame.transform.smoothscale(big, (cell_w, cell_h)),
                           sk.INK + (255,), 1)


# ── ORNAMENT swatches ─────────────────────────────────────────────────────────
# The Skull-King's own decorative elements (beads + cyan jewels), pulled out of the
# chosen design verbatim — see docs/skull_king_stack/ornaments/render_ornaments.py.
# Each is (fn-name, chip r_frac, short label); jewels use a bigger r_frac than beads.
_ORN_DIR = os.path.join(ROOT, "docs/skull_king_stack/ornaments")
_ORN_SPEC = [
    ("bead_white",        0.20, "white bead"),
    ("bead_gold",         0.20, "gold pip"),
    ("bead_cyan",         0.20, "cyan bead"),
    ("bead_darkblue",     0.20, "dk-blue bead"),
    ("gem_thirdeye",      0.32, "third-eye gem"),
    ("ornament_necklace", 0.34, "necklace gem"),
]
_orn_spec = _ilu.spec_from_file_location("ornaments_mod",
                                         os.path.join(_ORN_DIR, "render_ornaments.py"))
_ORN_MOD = _ilu.module_from_spec(_orn_spec)
_orn_spec.loader.exec_module(_ORN_MOD)
_ORN_RF = {fn: rf for (fn, rf, _t) in _ORN_SPEC}
_ORN_TAG = {fn: t for (fn, _rf, t) in _ORN_SPEC}


def _orn_chip(fn, cell_w, cell_h):
    """Chip for one ornament swatch, centred in the cell at its own r_frac."""
    ssr = 6
    big = pygame.Surface((cell_w * ssr, cell_h * ssr), pygame.SRCALPHA)
    rf = _ORN_RF[fn]
    r = int(min(cell_w, cell_h) * rf) * ssr
    s = (int(min(cell_w, cell_h) * rf) / 12.0) * ssr
    getattr(_ORN_MOD, fn)(big, cell_w * ssr // 2, cell_h * ssr // 2, r, s)
    return sk.grow_outline(pygame.transform.smoothscale(big, (cell_w, cell_h)),
                           sk.INK + (255,), 1)


def build_individual_sheet():
    """Every distinct small skull of the design, drawn on its own + labelled."""
    cw, ch = 116, 132
    pad = 16
    head = 90
    lab = 22
    rows = [
        ("CROWN skulls (above the head — bare relic skulls; idx 2 is the lit focal)",
         [("crown", i, i == 2) for i in range(6)]),
        ("PALM skulls (the ornamented reliquary skulls — hands removed; some carry the cyan gem)",
         [("palm", i, False) for i in range(6)]),
        ("EARLIER crown skull (round 9, pre-variance) — one uniform design, all 6 positions alike",
         [("crown_orig", 0, False), ("crown_orig", 0, True)]),
        ("NEW designs (8) — wild + crown-relic mix (matured under docs/skull_king_stack/new8/)",
         [("new", slug, lit) for (slug, _f, _r, _c, lit) in _NEW8_SPEC]),
        ("CLASSIC designs (8) — plain/simple skulls (matured under docs/skull_king_stack/classic8/)",
         [("classic", slug, False) for (slug, _f, _r, _c) in _CLASSIC8_SPEC]),
        ("ORNAMENTS (6) — the design's beads + jewels (docs/skull_king_stack/ornaments/)",
         [("orn", fn, False) for (fn, _rf, _t) in _ORN_SPEC]),
    ]
    cols = max(len(items) for _t, items in rows)
    W = cols * cw + (cols + 1) * pad
    H = head + len(rows) * (ch + lab + pad + 26)
    sheet = pygame.Surface((W, H))
    sheet.fill(sk.BG)
    _label(sheet, "SKULL-KING design — every distinct small skull + her ornaments, numbered #1..#N", pad, 20)
    _label(sheet, "Asthi-Dakini SWITCHED+BIG (crown 0-5 · palm 0-5 · r9)  +  8 new wild/relic  +  8 classic/simple  +  6 ornaments (beads + jewels)", pad, 48)

    y = head
    gid = 0                              # running global ID — every chip is #1..#N
    for row_title, items in rows:
        _label(sheet, row_title, pad, y)
        y += 26
        x = pad
        for kind, idx, lit in items:
            gid += 1
            if kind == "new":
                chip = _new8_chip(idx, cw, ch)
                tag = idx.split("-")[0]
            elif kind == "classic":
                chip = _classic8_chip(idx, cw, ch)
                tag = idx.split("-")[0]
            elif kind == "orn":
                chip = _orn_chip(idx, cw, ch)
                tag = _ORN_TAG[idx]
            else:
                chip = _skull_chip(kind, idx, cw, ch, lit=lit)
                if kind == "crown_orig":
                    tag = "r9 (lit)" if lit else "r9 (resting)"
                else:
                    tag = f"{kind} {idx}" + ("  (lit)" if lit else "")
            sheet.blit(chip, (x, y))
            _label(sheet, f"#{gid}  {tag}", x + 6, y + ch + 2)
            x += cw + pad
        y += ch + lab + pad
    out = os.path.join(OUT, "skulls_individual.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    build_individual_sheet()
    a = build_variant_sheet(False, "SKULL-KING STACK  —  the design's various small skulls, stacked pagoda-style", "stack.png")
    b = build_variant_sheet(True, "SKULL-KING SKEWER  —  same stack, skewered down the centre", "skewer.png")
    build_showcase(a, b)
