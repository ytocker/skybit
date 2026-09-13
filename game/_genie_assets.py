"""Self-contained genie design assets — palette, helpers, body-part
drawing functions used by GenieCharacter + GenieShineParticle.

This is a CONSOLIDATION of these design-tool modules:
  tools/render_a1_refined.py
  tools/render_a1_arms_variants.py
  tools/render_a1_crossed_legs_variants.py
  tools/render_a1_shine_variants.py
  tools/render_a1_carpet_variants.py

Required because the deploy workflow strips tools/ from the bundle
(too much unrelated content to ship). The drawing logic here is
BYTE-IDENTICAL to those tools — only module-level pygame init /
display.set_mode / os.makedirs boilerplate is removed, and
cross-module `from tools import ...` lines are folded out (all
helpers live in this single namespace now).

DO NOT add new design experiments here — iterate in tools/ first,
then re-consolidate by re-running scripts/rebuild_genie_assets.py
(or manually with the steps in commit history).
"""
import math
import random
import pygame


# ═════════════════════════════════════════════════════════════════════════
# Consolidated from render_a1_refined.py
# ═════════════════════════════════════════════════════════════════════════

# Higher canvas + supersample than v5 (240×340 ×5 → 320×460 ×6).
W, H, SS = 320, 460, 6
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)


# ─────────────────────────────────────────────────────────────────────────────
# Palette
# ─────────────────────────────────────────────────────────────────────────────
P = dict(
    # Skin (cyan/teal gradient)
    SKIN     = ( 70, 175, 220),
    SKIN_HI  = (175, 230, 252),
    SKIN_MID = (110, 200, 235),
    SKIN_LO  = ( 25, 110, 170),
    SKIN_DK  = ( 12,  70, 120),
    # Pants (deeper teal so they sit visually below the body)
    PANT     = ( 40, 130, 180),
    PANT_HI  = ( 90, 175, 220),
    PANT_MID = ( 65, 150, 200),
    PANT_LO  = ( 18,  85, 140),
    PANT_DK  = (  8,  55, 100),
    # Gold
    GOLD     = (245, 205, 105),
    GOLD_HI  = (255, 240, 175),
    GOLD_MID = (220, 175,  70),
    GOLD_LO  = (160, 115,  30),
    GOLD_DK  = (110,  75,  15),
    # Gems
    RUBY     = (220,  60,  80),
    RUBY_HI  = (255, 175, 195),
    EMERALD  = ( 65, 180,  95),
    SAPPHIRE = ( 70, 130, 220),
    # Other
    WHITE    = (250, 250, 245),
    HAIR     = ( 28,  22,  20),
    HAIR_HI  = ( 75,  55,  45),
    BLACK    = ( 18,  14,  10),
    CYAN     = (160, 230, 255),
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def s(v):
    """Convenience: scale native px to supersample px."""
    return int(v * SS)


def ell(surf, color, cx, cy, w, h):
    """Centred ellipse."""
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)))


def aa_circle(surf, color, cx, cy, r):
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r))


def gradient_ellipse(surf, cx, cy, w, h, colors, alpha=255):
    """Stack 3+ concentric ellipses from outer (lo) to inner (hi)
    for soft volume shading."""
    n = len(colors)
    for i, col in enumerate(colors):
        k = 1.0 - i / n
        ew = int(w * (0.35 + 0.65 * k))
        eh = int(h * (0.35 + 0.65 * k))
        s_off_x = int((w - ew) * 0.15)  # offset highlight slightly up-left
        s_off_y = int((h - eh) * 0.15)
        if alpha < 255:
            srf = pygame.Surface((ew + 2, eh + 2), pygame.SRCALPHA)
            pygame.draw.ellipse(srf, (*col, alpha),
                                (1, 1, ew, eh))
            surf.blit(srf, (int(cx - ew / 2 - s_off_x),
                            int(cy - eh / 2 - s_off_y)))
        else:
            pygame.draw.ellipse(surf, col,
                                (int(cx - ew / 2 - s_off_x),
                                 int(cy - eh / 2 - s_off_y),
                                 ew, eh))


def gem_facet(surf, cx, cy, r, color, hi_color, lo_color):
    """Faceted gem — 4-point diamond with bright facet on upper-left
    and shadow on lower-right."""
    pts_full = [(cx, cy - r), (cx + r, cy),
                (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, lo_color, pts_full)
    # Inner faceted shape
    inner = int(r * 0.85)
    pts_inner = [(cx, cy - inner), (cx + inner, cy),
                 (cx, cy + inner), (cx - inner, cy)]
    pygame.draw.polygon(surf, color, pts_inner)
    # Upper-left highlight facet
    pygame.draw.polygon(surf, hi_color,
                        [(cx, cy - inner),
                         (cx - int(inner * 0.55), cy),
                         (cx - int(inner * 0.3), cy - int(inner * 0.3))])
    # White sparkle dot
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - inner * 0.3), int(cy - inner * 0.5)),
                       max(1, int(r * 0.12)))


def outlined_polygon(surf, points, fill, outline, w=None):
    if w is None:
        w = max(2, int(SS * 0.4))
    pygame.draw.polygon(surf, fill, points)
    pygame.draw.polygon(surf, outline, points, w)


# ─────────────────────────────────────────────────────────────────────────────
# Body parts
# ─────────────────────────────────────────────────────────────────────────────

def draw_smoke_aura(big, cx, t):
    """Atmospheric smoke wisps drifting behind/below the figure —
    just ambience now that the figure has real legs."""
    for i, (dx, dy, w, h, alpha) in enumerate((
            (-90, 380, 130, 70, 60),
            ( 90, 380, 130, 70, 60),
            (  0, 420, 200, 60, 50),
            (-130, 330, 90, 50, 50),
            ( 130, 330, 90, 50, 50),
            )):
        sway = math.sin(t * 1.5 + i * 0.7) * s(3)
        srf = pygame.Surface((s(w + 4), s(h + 4)), pygame.SRCALPHA)
        pygame.draw.ellipse(srf, (*P["SKIN_HI"], alpha),
                            (s(2), s(2), s(w), s(h)))
        big.blit(srf, (s(W // 2 + dx - w / 2) + sway, s(dy - h / 2)))


def draw_pants(big, cx, t):
    """Harem pants with gold ankle cuffs + embroidered waist band."""
    # Hips top
    hip_y = s(248)
    knee_y = s(360)
    ankle_y = s(424)
    # Each pant leg as polygon (baggy on outside, cinched at ankle)
    for side in (-1, 1):
        # Outer + inner boundary
        leg_top_x_out = cx + side * s(38)
        leg_top_x_in  = cx + side * s(8)
        leg_knee_x_out = cx + side * s(48)  # baggy outward
        leg_knee_x_in  = cx + side * s(14)
        leg_ankle_x_out = cx + side * s(26)  # cinched
        leg_ankle_x_in  = cx + side * s(10)
        # Pant leg polygon
        pts = [
            (leg_top_x_in, hip_y),
            (leg_top_x_out, hip_y),
            (leg_knee_x_out, knee_y),
            (leg_ankle_x_out, ankle_y),
            (leg_ankle_x_in, ankle_y),
            (leg_knee_x_in, knee_y),
        ]
        # Shadow polygon
        shadow_pts = [(x + s(2), y + s(2)) for x, y in pts]
        pygame.draw.polygon(big, P["PANT_DK"], shadow_pts)
        pygame.draw.polygon(big, P["PANT"], pts)
        # Outer highlight stripe
        pygame.draw.line(big, P["PANT_HI"],
                         (leg_top_x_out - side * s(4), hip_y + s(6)),
                         (leg_knee_x_out - side * s(4), knee_y - s(8)),
                         s(3))
        # Inner shadow line
        pygame.draw.line(big, P["PANT_LO"],
                         (leg_top_x_in + side * s(3), hip_y + s(8)),
                         (leg_ankle_x_in + side * s(2), ankle_y - s(4)),
                         s(2))
        # Pleat ripple — two faint vertical curves
        for off in (s(8), s(20)):
            pygame.draw.line(big, P["PANT_LO"],
                             (cx + side * (s(18) + off), hip_y + s(12)),
                             (cx + side * (s(14) + off // 2), ankle_y - s(10)),
                             max(1, s(1)))
        # Gold ankle cuff
        cuff_y = ankle_y - s(2)
        cuff_top_x_out = leg_ankle_x_out + side * s(3)
        cuff_top_x_in  = leg_ankle_x_in - side * s(3)
        cuff_pts = [
            (cuff_top_x_in, cuff_y - s(8)),
            (cuff_top_x_out, cuff_y - s(8)),
            (leg_ankle_x_out + side * s(2), cuff_y + s(6)),
            (leg_ankle_x_in - side * s(2), cuff_y + s(6)),
        ]
        pygame.draw.polygon(big, P["GOLD_LO"],
                            [(x + s(1), y + s(1)) for x, y in cuff_pts])
        pygame.draw.polygon(big, P["GOLD"], cuff_pts)
        pygame.draw.line(big, P["GOLD_HI"],
                         (cuff_pts[0][0] + s(2), cuff_pts[0][1] + s(2)),
                         (cuff_pts[1][0] - s(2), cuff_pts[1][1] + s(2)),
                         s(2))
        # Small gem on the cuff
        gx = cx + side * s(18)
        gy = cuff_y - s(1)
        gem_facet(big, gx, gy, s(3), P["RUBY"], P["RUBY_HI"], (110, 30, 40))

    # Pants waist band (gold strip)
    waist_pts = [
        (cx - s(46), hip_y - s(4)),
        (cx + s(46), hip_y - s(4)),
        (cx + s(42), hip_y + s(8)),
        (cx - s(42), hip_y + s(8)),
    ]
    pygame.draw.polygon(big, P["GOLD_LO"],
                        [(x + s(1), y + s(1)) for x, y in waist_pts])
    pygame.draw.polygon(big, P["GOLD"], waist_pts)
    pygame.draw.line(big, P["GOLD_HI"],
                     (waist_pts[0][0] + s(3), waist_pts[0][1] + s(2)),
                     (waist_pts[1][0] - s(3), waist_pts[1][1] + s(2)),
                     s(2))
    # Embroidery dots along the waist band
    for fx in (-s(35), -s(20), -s(5), s(10), s(25), s(40)):
        pygame.draw.circle(big, P["GOLD_DK"],
                           (cx + fx, hip_y + s(2)), max(1, s(1)))


def draw_slippers(big, cx):
    """Curled-toe Arabian slippers in gold + ruby."""
    slipper_y = s(440)
    for side in (-1, 1):
        sx = cx + side * s(18)
        # Sole
        sole_pts = [
            (sx - s(12), slipper_y + s(4)),
            (sx + s(16), slipper_y + s(4)),
            (sx + s(24), slipper_y - s(2)),  # curled toe lifts up
            (sx + s(20), slipper_y - s(8)),
            (sx + s(8), slipper_y - s(4)),
            (sx - s(10), slipper_y - s(4)),
        ]
        if side < 0:
            sole_pts = [(2 * sx - x, y) for x, y in sole_pts]
        pygame.draw.polygon(big, P["GOLD_DK"],
                            [(x + s(1), y + s(1)) for x, y in sole_pts])
        pygame.draw.polygon(big, P["GOLD"], sole_pts)
        # Highlight on top of slipper
        pygame.draw.line(big, P["GOLD_HI"],
                         (sx - s(6), slipper_y - s(2)),
                         (sx + side * s(10), slipper_y - s(5)),
                         s(2))
        # Ruby gem on the toe
        toe_x = sx + side * s(16)
        toe_y = slipper_y - s(4)
        gem_facet(big, toe_x, toe_y, s(3), P["RUBY"], P["RUBY_HI"],
                  (110, 30, 40))


def draw_torso(big, cx):
    """Bare muscular V-torso with multi-tone shading."""
    neck_y     = s(120)
    shoulder_y = s(138)
    waist_y    = s(220)
    base_y     = s(252)
    pts = [
        (cx - s(20), neck_y),
        (cx - s(58), shoulder_y),
        (cx - s(34), waist_y),
        (cx - s(36), base_y),
        (cx + s(36), base_y),
        (cx + s(34), waist_y),
        (cx + s(58), shoulder_y),
        (cx + s(20), neck_y),
    ]
    # Drop shadow
    pygame.draw.polygon(big, P["SKIN_DK"],
                        [(x + s(2), y + s(3)) for x, y in pts])
    # Mid-tone base
    pygame.draw.polygon(big, P["SKIN_LO"], pts)
    # Inner main fill (slightly smaller)
    inner = [
        (cx - s(18), neck_y + s(1)),
        (cx - s(54), shoulder_y + s(1)),
        (cx - s(32), waist_y - s(1)),
        (cx - s(34), base_y - s(1)),
        (cx + s(34), base_y - s(1)),
        (cx + s(32), waist_y - s(1)),
        (cx + s(54), shoulder_y + s(1)),
        (cx + s(18), neck_y + s(1)),
    ]
    pygame.draw.polygon(big, P["SKIN"], inner)
    # Soft top-down highlight gradient (alpha stripe along upper chest)
    srf = pygame.Surface((s(120), s(40)), pygame.SRCALPHA)
    pygame.draw.ellipse(srf, (*P["SKIN_HI"], 100),
                        (0, 0, s(120), s(40)))
    big.blit(srf, (cx - s(60), shoulder_y - s(2)))
    # ── pecs ──
    for sx in (-s(20), s(20)):
        # Pec base (shaded)
        ell(big, P["SKIN_HI"], cx + sx, s(150), s(38), s(22))
        # Pec under-shadow arc
        pygame.draw.arc(big, P["SKIN_LO"],
                        (cx + sx - s(19), s(154), s(38), s(16)),
                        math.radians(0), math.radians(180), s(2))
        # Tiny shaded crease where pec meets sternum
        pygame.draw.arc(big, P["SKIN_DK"],
                        (cx + sx - s(19), s(155), s(38), s(14)),
                        math.radians(20), math.radians(160), max(1, s(1)))
    # Sternum line
    pygame.draw.line(big, P["SKIN_LO"],
                     (cx, s(150)), (cx, s(180)), s(2))
    # ── abs ──
    for ay in (s(184), s(200), s(216)):
        for ax in (-s(8), s(8)):
            ell(big, P["SKIN_HI"], cx + ax, ay, s(14), s(8))
            pygame.draw.line(big, P["SKIN_LO"],
                             (cx + ax, ay - s(2)),
                             (cx + ax, ay + s(2)), max(1, s(1)))
    pygame.draw.line(big, P["SKIN_LO"],
                     (cx, s(178)), (cx, s(225)), max(1, s(1)))
    # Side oblique highlights
    for sx in (-s(28), s(28)):
        pygame.draw.line(big, P["SKIN_HI"],
                         (cx + sx, s(180)), (cx + int(sx * 0.7), s(220)),
                         max(1, s(1)))


def draw_arms(big, cx):
    """Crossed arms drawn as forearm + bicep + hand polygons with
    clear overlap shadow at the centre."""
    L = P
    # ── Arm 1 (lower) — RIGHT arm: right shoulder to LEFT waist ──
    sh1 = (cx + s(56), s(138))
    el1 = (cx + s(28), s(170))
    wr1 = (cx - s(30), s(200))
    # ── Arm 2 (upper) — LEFT arm: left shoulder to RIGHT waist ──
    sh2 = (cx - s(56), s(138))
    el2 = (cx - s(28), s(168))
    wr2 = (cx + s(30), s(198))

    # Draw arm 1 (lower) first
    _draw_one_arm(big, sh1, el1, wr1, side=+1)
    # Cross-shadow under where arm 2 will lay
    s_ovr = pygame.Surface((s(70), s(28)), pygame.SRCALPHA)
    pygame.draw.ellipse(s_ovr, (*L["SKIN_DK"], 130), (0, 0, s(70), s(28)))
    big.blit(s_ovr, (cx - s(35), s(166)))
    # Draw arm 2 (upper) on top
    _draw_one_arm(big, sh2, el2, wr2, side=-1)


def _draw_one_arm(big, shoulder, elbow, wrist, side):
    """One muscular arm with shoulder ball, bicep, forearm, hand."""
    L = P
    sh_x, sh_y = shoulder
    el_x, el_y = elbow
    wr_x, wr_y = wrist

    # ── Upper arm (bicep) drawn as elongated ellipse ──
    mx = (sh_x + el_x) // 2
    my = (sh_y + el_y) // 2
    dx = el_x - sh_x
    dy = el_y - sh_y
    length = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(dy, dx))
    # Bicep ellipse
    bicep_surf = pygame.Surface((int(length * 1.2), s(26)),
                                pygame.SRCALPHA)
    bw, bh = bicep_surf.get_size()
    pygame.draw.ellipse(bicep_surf, L["SKIN_DK"], (s(1), s(2), bw - s(2), bh - s(4)))
    pygame.draw.ellipse(bicep_surf, L["SKIN_LO"], (0, 0, bw, bh))
    pygame.draw.ellipse(bicep_surf, L["SKIN"], (s(2), s(2), bw - s(4), bh - s(6)))
    pygame.draw.ellipse(bicep_surf, L["SKIN_HI"],
                        (s(4), s(2), int(bw * 0.4), s(7)))
    bicep_rot = pygame.transform.rotate(bicep_surf, -angle)
    rect = bicep_rot.get_rect(center=(mx, my))
    big.blit(bicep_rot, rect.topleft)

    # ── Elbow ball ──
    aa_circle(big, L["SKIN_DK"], el_x + s(1), el_y + s(1), s(10))
    aa_circle(big, L["SKIN_LO"], el_x, el_y, s(9))
    aa_circle(big, L["SKIN"], el_x, el_y, s(8))
    aa_circle(big, L["SKIN_HI"], el_x - s(2), el_y - s(2), s(3))

    # ── Forearm (elbow → wrist) ──
    dx2 = wr_x - el_x
    dy2 = wr_y - el_y
    length2 = math.hypot(dx2, dy2)
    angle2 = math.degrees(math.atan2(dy2, dx2))
    fore_w = int(length2 * 1.15)
    fore_h = s(22)
    fore_surf = pygame.Surface((fore_w, fore_h), pygame.SRCALPHA)
    pygame.draw.ellipse(fore_surf, L["SKIN_DK"], (s(1), s(2), fore_w - s(2), fore_h - s(4)))
    pygame.draw.ellipse(fore_surf, L["SKIN_LO"], (0, 0, fore_w, fore_h))
    pygame.draw.ellipse(fore_surf, L["SKIN"], (s(2), s(2), fore_w - s(4), fore_h - s(6)))
    pygame.draw.ellipse(fore_surf, L["SKIN_HI"],
                        (s(4), s(2), int(fore_w * 0.4), s(6)))
    fore_rot = pygame.transform.rotate(fore_surf, -angle2)
    rect = fore_rot.get_rect(center=((el_x + wr_x) // 2, (el_y + wr_y) // 2))
    big.blit(fore_rot, rect.topleft)

    # ── Gold cuff at wrist ──
    aa_circle(big, L["GOLD_DK"], wr_x + s(1), wr_y + s(1), s(12))
    aa_circle(big, L["GOLD_LO"], wr_x, wr_y, s(11))
    aa_circle(big, L["GOLD"], wr_x, wr_y, s(10))
    aa_circle(big, L["GOLD_HI"], wr_x - s(3), wr_y - s(3), s(4))
    # Tiny engraved band ring around the cuff
    pygame.draw.circle(big, L["GOLD_DK"], (wr_x, wr_y), s(10), max(1, s(1)))

    # ── Fist (closed hand) ──
    # Fist sits just past the cuff in the arm direction
    fist_x = wr_x + int(dx2 / length2 * s(11))
    fist_y = wr_y + int(dy2 / length2 * s(11))
    # Fist body
    aa_circle(big, L["SKIN_DK"], fist_x + s(1), fist_y + s(1), s(10))
    aa_circle(big, L["SKIN_LO"], fist_x, fist_y, s(9))
    aa_circle(big, L["SKIN"], fist_x, fist_y, s(8))
    aa_circle(big, L["SKIN_HI"], fist_x - s(2), fist_y - s(2), s(3))
    # Knuckle bumps (3 small ellipses on top)
    for k in (-s(4), 0, s(4)):
        ell(big, L["SKIN_LO"], fist_x + k, fist_y - s(5), s(3), s(2))
    # Tiny shadow line under the knuckles
    pygame.draw.line(big, L["SKIN_DK"],
                     (fist_x - s(5), fist_y - s(3)),
                     (fist_x + s(5), fist_y - s(3)), max(1, s(1)))
    # ── Armband above the wrist cuff ──
    ab_x = el_x + int((wr_x - el_x) * 0.5)
    ab_y = el_y + int((wr_y - el_y) * 0.5)
    # Find tangent perpendicular to arm
    perp = (-(wr_y - el_y) / length2, (wr_x - el_x) / length2)
    ab_surf = pygame.Surface((s(20), s(10)), pygame.SRCALPHA)
    pygame.draw.ellipse(ab_surf, L["GOLD_LO"], (0, 0, s(20), s(10)))
    pygame.draw.ellipse(ab_surf, L["GOLD"], (s(1), s(1), s(18), s(8)))
    pygame.draw.line(ab_surf, L["GOLD_HI"], (s(3), s(3)), (s(17), s(3)), s(1))
    ab_rot = pygame.transform.rotate(ab_surf, -angle2)
    rect = ab_rot.get_rect(center=(ab_x, ab_y))
    big.blit(ab_rot, rect.topleft)


def draw_sash(big, cx):
    """Gold sash at the waist with multi-gem buckle."""
    sash_y = s(245)
    sash_pts = [
        (cx - s(54), sash_y - s(6)),
        (cx + s(54), sash_y - s(5)),
        (cx + s(48), sash_y + s(14)),
        (cx - s(48), sash_y + s(13)),
    ]
    pygame.draw.polygon(big, P["GOLD_DK"],
                        [(x + s(1), y + s(2)) for x, y in sash_pts])
    pygame.draw.polygon(big, P["GOLD_LO"], sash_pts)
    pygame.draw.polygon(big, P["GOLD"],
                        [(x, y + s(1)) for x, y in sash_pts])
    # Top highlight ribbon
    pygame.draw.line(big, P["GOLD_HI"],
                     (sash_pts[0][0] + s(3), sash_pts[0][1] + s(3)),
                     (sash_pts[1][0] - s(3), sash_pts[1][1] + s(3)),
                     s(2))
    # Sash embroidery — small repeated diamond pattern
    for fx in (-s(40), -s(28), -s(16), s(0), s(12), s(24), s(36)):
        cx_p, cy_p = cx + fx, sash_y + s(5)
        pygame.draw.polygon(big, P["GOLD_DK"],
                            [(cx_p, cy_p - s(2)),
                             (cx_p + s(2), cy_p),
                             (cx_p, cy_p + s(2)),
                             (cx_p - s(2), cy_p)])
    # ── Buckle (large gold disc with three gems) ──
    bx, by = cx, sash_y + s(5)
    aa_circle(big, P["GOLD_DK"], bx + s(1), by + s(1), s(16))
    aa_circle(big, P["GOLD_LO"], bx, by, s(15))
    aa_circle(big, P["GOLD"], bx, by, s(13))
    aa_circle(big, P["GOLD_HI"], bx - s(4), by - s(4), s(4))
    # Three faceted gems: ruby centre + emerald left + sapphire right
    gem_facet(big, bx, by, s(7), P["RUBY"], P["RUBY_HI"], (110, 30, 40))
    gem_facet(big, bx - s(10), by, s(3), P["EMERALD"], (180, 245, 200), (20, 100, 50))
    gem_facet(big, bx + s(10), by, s(3), P["SAPPHIRE"], (170, 215, 255), (20, 60, 130))


def draw_head(big, cx, head_cy, head_r):
    """Head with cheek + chin + nose + earlobe shading."""
    # Shadow
    aa_circle(big, P["SKIN_DK"], cx + s(3), head_cy + s(3), head_r + s(1))
    # Base
    aa_circle(big, P["SKIN_LO"], cx, head_cy, head_r)
    # Mid (slightly inset, brighter)
    aa_circle(big, P["SKIN"], cx, head_cy - s(1), head_r - s(2))
    # Highlight on upper-left
    aa_circle(big, P["SKIN_HI"], cx - head_r // 3, head_cy - head_r // 3,
              head_r // 3)
    # Cheek soft glow (right side)
    cheek = pygame.Surface((s(20), s(14)), pygame.SRCALPHA)
    pygame.draw.ellipse(cheek, (255, 180, 200, 80), (0, 0, s(20), s(14)))
    big.blit(cheek, (cx + s(4), head_cy + s(6)))
    cheek2 = pygame.Surface((s(20), s(14)), pygame.SRCALPHA)
    pygame.draw.ellipse(cheek2, (255, 180, 200, 60), (0, 0, s(20), s(14)))
    big.blit(cheek2, (cx - s(24), head_cy + s(6)))
    # Chin shadow
    pygame.draw.arc(big, P["SKIN_LO"],
                    (cx - head_r + s(4), head_cy + s(4),
                     2 * head_r - s(8), head_r),
                    math.radians(200), math.radians(340), s(2))
    # Nose
    nose_pts = [
        (cx, head_cy - s(2)),
        (cx + s(3), head_cy + s(6)),
        (cx, head_cy + s(8)),
        (cx - s(3), head_cy + s(6)),
    ]
    pygame.draw.polygon(big, P["SKIN_LO"], nose_pts)
    pygame.draw.polygon(big, P["SKIN_HI"],
                        [(cx - s(1), head_cy - s(1)),
                         (cx, head_cy + s(2)),
                         (cx - s(2), head_cy + s(3))])
    # Subtle nostrils
    pygame.draw.circle(big, P["SKIN_DK"],
                       (cx - s(2), head_cy + s(6)), max(1, s(1)))
    pygame.draw.circle(big, P["SKIN_DK"],
                       (cx + s(2), head_cy + s(6)), max(1, s(1)))


def draw_topknot_and_headband(big, cx, head_cy, head_r):
    """Black hair tuft + topknot + gold headband + central ruby
    + small hair locks across the forehead."""
    # Hair locks/tuft over the forehead
    tuft_pts = [
        (cx - head_r + s(4), head_cy - s(16)),
        (cx - s(8), head_cy - s(20)),
        (cx + s(8), head_cy - s(20)),
        (cx + head_r - s(4), head_cy - s(16)),
        (cx + s(14), head_cy - s(11)),
        (cx, head_cy - s(8)),
        (cx - s(14), head_cy - s(11)),
    ]
    pygame.draw.polygon(big, P["HAIR"], tuft_pts)
    pygame.draw.line(big, P["HAIR_HI"],
                     (cx - s(20), head_cy - s(17)),
                     (cx + s(20), head_cy - s(17)),
                     max(1, s(1)))

    # Topknot at the top of head
    tk_cx = cx
    tk_cy = head_cy - head_r - s(4)
    # Base of the topknot (small gold tie)
    pygame.draw.rect(big, P["GOLD"],
                     (tk_cx - s(8), tk_cy + s(6), s(16), s(4)))
    pygame.draw.line(big, P["GOLD_HI"],
                     (tk_cx - s(6), tk_cy + s(7)),
                     (tk_cx + s(6), tk_cy + s(7)), max(1, s(1)))
    # Black hair ball
    aa_circle(big, P["BLACK"], tk_cx + s(1), tk_cy + s(1), s(14))
    aa_circle(big, P["HAIR"], tk_cx, tk_cy, s(13))
    aa_circle(big, P["HAIR_HI"], tk_cx - s(3), tk_cy - s(3), s(4))

    # Gold headband (3-layer)
    band_y = head_cy - s(18)
    pygame.draw.rect(big, P["GOLD_DK"],
                     (cx - s(38), band_y - s(2), s(76), s(11)))
    pygame.draw.rect(big, P["GOLD_LO"],
                     (cx - s(38), band_y - s(1), s(76), s(9)))
    pygame.draw.rect(big, P["GOLD"],
                     (cx - s(36), band_y, s(72), s(7)))
    pygame.draw.line(big, P["GOLD_HI"],
                     (cx - s(34), band_y + s(2)),
                     (cx + s(34), band_y + s(2)), max(1, s(1)))
    # Engraved band pattern
    for fx in (-s(30), -s(20), -s(10), s(10), s(20), s(30)):
        pygame.draw.line(big, P["GOLD_DK"],
                         (cx + fx, band_y + s(1)),
                         (cx + fx, band_y + s(6)),
                         max(1, s(1)))
    # Central ruby (diamond cut)
    gem_facet(big, cx, band_y + s(3), s(8),
              P["RUBY"], P["RUBY_HI"], (110, 30, 40))
    # Mini gold spikes flanking the ruby
    for sxd in (-s(12), s(12)):
        pygame.draw.polygon(big, P["GOLD"],
                            [(cx + sxd - s(2), band_y - s(2)),
                             (cx + sxd, band_y - s(6)),
                             (cx + sxd + s(2), band_y - s(2))])


def draw_face(big, cx, head_cy):
    """Brow + eyes + mustache + grin + goatee."""
    # ── Brows (thick angled) ──
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - s(20), head_cy - s(6)),
                         (cx - s(5), head_cy - s(9)),
                         (cx - s(5), head_cy - s(4)),
                         (cx - s(20), head_cy - s(2))])
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx + s(20), head_cy - s(6)),
                         (cx + s(5), head_cy - s(9)),
                         (cx + s(5), head_cy - s(4)),
                         (cx + s(20), head_cy - s(2))])

    # ── Eyes (whites + iris + pupil + 2 glints) ──
    for sx in (-s(12), s(12)):
        # Whites
        pygame.draw.ellipse(big, P["WHITE"],
                            (cx + sx - s(8), head_cy - s(4),
                             s(16), s(12)))
        # Iris (dark brown)
        aa_circle(big, P["HAIR"], cx + sx, head_cy + s(1), s(5))
        # Pupil
        aa_circle(big, P["BLACK"], cx + sx, head_cy + s(1), s(3))
        # Glints
        aa_circle(big, P["WHITE"], cx + sx - s(2), head_cy - s(1), s(2))
        aa_circle(big, P["WHITE"], cx + sx + s(2), head_cy + s(3),
                  max(1, s(1)))
        # Eyelash hint
        pygame.draw.line(big, P["HAIR"],
                         (cx + sx - s(8), head_cy - s(4)),
                         (cx + sx + s(8), head_cy - s(4)),
                         max(1, s(1)))

    # ── Curled mustache (two arcs ending in spiral curls) ──
    pygame.draw.arc(big, P["HAIR"],
                    (cx - s(20), head_cy + s(10),
                     s(20), s(10)),
                    math.radians(195), math.radians(360), s(3))
    pygame.draw.arc(big, P["HAIR"],
                    (cx, head_cy + s(10),
                     s(20), s(10)),
                    math.radians(180), math.radians(345), s(3))
    # Curl loops at the ends
    for sxc in (-s(20), s(20)):
        aa_circle(big, P["HAIR"], cx + sxc, head_cy + s(13), s(3))
        aa_circle(big, P["HAIR_HI"], cx + sxc - s(1), head_cy + s(12),
                  max(1, s(1)))

    # ── Mouth (confident grin showing teeth) ──
    mt_y = head_cy + s(18)
    # Mouth interior
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - s(13), mt_y),
                         (cx + s(13), mt_y),
                         (cx + s(10), mt_y + s(8)),
                         (cx - s(10), mt_y + s(8))])
    # Teeth
    pygame.draw.polygon(big, P["WHITE"],
                        [(cx - s(11), mt_y + s(1)),
                         (cx + s(11), mt_y + s(1)),
                         (cx + s(8), mt_y + s(6)),
                         (cx - s(8), mt_y + s(6))])
    for tx in (-s(7), -s(3), s(0), s(3), s(7)):
        pygame.draw.line(big, P["HAIR"],
                         (cx + tx, mt_y + s(1)),
                         (cx + tx, mt_y + s(6)),
                         max(1, s(1)))

    # ── Goatee ──
    pygame.draw.polygon(big, P["HAIR"],
                        [(cx - s(8), mt_y + s(8)),
                         (cx + s(8), mt_y + s(8)),
                         (cx + s(4), mt_y + s(20)),
                         (cx - s(4), mt_y + s(20))])
    pygame.draw.line(big, P["HAIR_HI"],
                     (cx - s(2), mt_y + s(10)),
                     (cx - s(1), mt_y + s(18)),
                     max(1, s(1)))


def draw_earrings(big, cx, head_cy, head_r):
    """Gold hoop earrings with small ruby drops."""
    for sx in (-head_r - s(2), head_r + s(2)):
        ex = cx + sx
        ey = head_cy + s(4)
        # Outer hoop
        pygame.draw.circle(big, P["GOLD_DK"], (ex, ey), s(8), s(2))
        pygame.draw.circle(big, P["GOLD"], (ex, ey), s(7), s(2))
        pygame.draw.circle(big, P["GOLD_HI"], (ex - s(2), ey - s(2)),
                           max(1, s(1)))
        # Ruby drop pendant
        py = ey + s(10)
        pygame.draw.line(big, P["GOLD"], (ex, ey + s(3)),
                         (ex, py - s(2)), max(1, s(1)))
        gem_facet(big, ex, py, s(3), P["RUBY"], P["RUBY_HI"], (110, 30, 40))


def draw_neck(big, cx):
    """Short cylindrical neck connecting head to torso."""
    neck_top = s(100)
    neck_bot = s(120)
    pygame.draw.polygon(big, P["SKIN_DK"],
                        [(cx - s(15), neck_top),
                         (cx + s(15), neck_top),
                         (cx + s(18), neck_bot),
                         (cx - s(18), neck_bot)])
    pygame.draw.polygon(big, P["SKIN_LO"],
                        [(cx - s(14), neck_top),
                         (cx + s(14), neck_top),
                         (cx + s(17), neck_bot - s(1)),
                         (cx - s(17), neck_bot - s(1))])
    pygame.draw.polygon(big, P["SKIN"],
                        [(cx - s(12), neck_top + s(2)),
                         (cx + s(12), neck_top + s(2)),
                         (cx + s(15), neck_bot - s(2)),
                         (cx - s(15), neck_bot - s(2))])
    # Collarbone shadow
    pygame.draw.arc(big, P["SKIN_LO"],
                    (cx - s(40), s(120), s(80), s(20)),
                    math.radians(200), math.radians(340), max(1, s(1)))


def draw_a1_refined(big, cx, t=0.0):
    """Compose the full refined A1 figure in z-order."""
    # 1. Atmosphere behind
    draw_smoke_aura(big, cx, t)
    # 2. Legs/pants/slippers (lowest)
    draw_pants(big, cx, t)
    draw_slippers(big, cx)
    # 3. Torso
    draw_torso(big, cx)
    # 4. Neck
    draw_neck(big, cx)
    # 5. Head (face first, then hair on top)
    head_cy = s(60)
    head_r = s(40)
    draw_head(big, cx, head_cy, head_r)
    draw_face(big, cx, head_cy)
    draw_earrings(big, cx, head_cy, head_r)
    draw_topknot_and_headband(big, cx, head_cy, head_r)
    # 6. Sash + buckle
    draw_sash(big, cx)
    # 7. Arms ON TOP of sash so they read as crossed in front
    draw_arms(big, cx)


# ─────────────────────────────────────────────────────────────────────────────

# ═════════════════════════════════════════════════════════════════════════
# Consolidated from render_a1_arms_variants.py
# ═════════════════════════════════════════════════════════════════════════



# Display scale for individual portraits + sheet.
DISPLAY_SCALE = 2


# ─────────────────────────────────────────────────────────────────────────────
# Local arm primitives (mirror _draw_one_arm but unbundled so each pose
# can compose its own geometry)
# ─────────────────────────────────────────────────────────────────────────────

def _segment(big, p0, p1, color, color_lo, color_hi, w=10,
             tapered=False):
    """Limb segment from p0 → p1 as a rotated ellipse with shadow +
    base + highlight stripe. `tapered` thins one end (used for the
    forearm)."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = max(1.0, math.hypot(dx, dy))
    ang = math.degrees(math.atan2(dy, dx))
    w_px = s(w)
    sw = int(length * 1.15)
    sh = w_px + s(4)
    seg = pygame.Surface((sw, sh), pygame.SRCALPHA)
    # Shadow + base + main fill
    pygame.draw.ellipse(seg, color_lo, (s(1), s(2), sw - s(2), sh - s(4)))
    pygame.draw.ellipse(seg, color, (s(2), s(2), sw - s(4), sh - s(6)))
    pygame.draw.ellipse(seg, color_hi,
                        (s(4), s(2), int(sw * 0.4), s(6)))
    if tapered:
        # Trim the far end to thin the tip (used when a forearm
        # meets a hand directly).
        # No-op for now; ellipse already tapers visually.
        pass
    rot = pygame.transform.rotate(seg, -ang)
    rect = rot.get_rect(center=((x0 + x1) // 2, (y0 + y1) // 2))
    big.blit(rot, rect.topleft)


def _joint(big, center, color, color_lo, color_hi, r=8):
    """Spherical joint (shoulder / elbow)."""
    cx, cy = center
    aa_circle(big, color_lo, cx + s(1), cy + s(1), s(r + 1))
    aa_circle(big, color, cx, cy, s(r))
    aa_circle(big, color_hi, cx - s(r // 3), cy - s(r // 3),
              max(2, s(r // 3)))


def _fist(big, center, color, color_lo, color_hi, r=9):
    """Closed fist with knuckle bumps."""
    cx, cy = center
    aa_circle(big, color_lo, cx + s(1), cy + s(1), s(r + 1))
    aa_circle(big, color, cx, cy, s(r))
    aa_circle(big, color_hi, cx - s(2), cy - s(2), s(r // 3))
    for k in (-s(4), 0, s(4)):
        ell(big, color_lo, cx + k, cy - s(5), s(3), s(2))


def _open_palm(big, center, color, color_lo, color_hi,
               r_w=12, r_h=14, palm_up=True, side=+1):
    """Open palm — wider than tall when palm-up, with 4 finger
    ridges along the top and a thumb on one side."""
    cx, cy = center
    # Palm base ellipse
    aa_circle(big, color_lo, cx + s(1), cy + s(1), s(r_w))
    ell(big, color_lo, cx + s(1), cy + s(1), s(r_w) * 2, s(r_h) * 2)
    ell(big, color, cx, cy, s(r_w) * 2, s(r_h) * 2)
    ell(big, color_hi, cx - s(2), cy - s(3),
        int(s(r_w) * 1.4), s(4))
    # 4 finger ridges along the top edge (small ellipses)
    finger_y = cy - s(r_h - 1)
    for fx, fw in ((-s(8), s(3)), (-s(3), s(3)),
                   (s(2), s(3)), (s(7), s(3))):
        ell(big, color, cx + fx, finger_y, fw * 2, s(8))
        ell(big, color_hi, cx + fx - s(1), finger_y - s(1),
            fw * 2 - s(1), s(2))
        # Finger crease
        pygame.draw.line(big, color_lo,
                         (cx + fx, finger_y + s(2)),
                         (cx + fx, finger_y + s(4)),
                         max(1, s(1)))
    # Thumb on the outer side
    thumb_x = cx + side * s(r_w + 2)
    thumb_y = cy + s(2)
    ell(big, color_lo, thumb_x + s(1), thumb_y + s(1), s(6), s(10))
    ell(big, color, thumb_x, thumb_y, s(5), s(9))
    ell(big, color_hi, thumb_x - s(1), thumb_y - s(1), s(3), s(3))


def _wrist_cuff(big, center, w=11):
    """Gold wrist cuff — 3-layer with engraved band."""
    cx, cy = center
    aa_circle(big, P["GOLD_DK"], cx + s(1), cy + s(1), s(w + 1))
    aa_circle(big, P["GOLD_LO"], cx, cy, s(w))
    aa_circle(big, P["GOLD"], cx, cy, s(w - 1))
    aa_circle(big, P["GOLD_HI"], cx - s(3), cy - s(3), s(4))
    pygame.draw.circle(big, P["GOLD_DK"], (cx, cy), s(w - 1),
                       max(1, s(1)))


def _armband(big, anchor, perp, color=None, color_hi=None):
    """Small gold armband above the wrist cuff. `perp` is the unit
    vector perpendicular to the arm direction."""
    if color is None:
        color = P["GOLD"]
    if color_hi is None:
        color_hi = P["GOLD_HI"]
    ax, ay = anchor
    ab = pygame.Surface((s(20), s(10)), pygame.SRCALPHA)
    pygame.draw.ellipse(ab, P["GOLD_LO"], (0, 0, s(20), s(10)))
    pygame.draw.ellipse(ab, color, (s(1), s(1), s(18), s(8)))
    pygame.draw.line(ab, color_hi, (s(3), s(3)), (s(17), s(3)), s(1))
    ang = math.degrees(math.atan2(perp[1], perp[0]))
    ab_rot = pygame.transform.rotate(ab, -ang + 90)
    rect = ab_rot.get_rect(center=anchor)
    big.blit(ab_rot, rect.topleft)


# ─────────────────────────────────────────────────────────────────────────────
# Pose 1 — Folded forearms (relaxed cool)
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_1_folded(big, cx):
    """Forearms held HORIZONTAL across the upper chest. The right
    forearm sits on top of the left. Each hand rests visibly on the
    opposite bicep."""
    L = P
    chest_y = s(170)

    # Left arm (drawn first, will be partially behind the right)
    L_sh = (cx - s(54), s(140))          # left shoulder
    L_el = (cx - s(42), s(168))          # left elbow (drops + outward)
    L_wr = (cx + s(28), s(160))          # left wrist — across to RIGHT bicep
    # Bicep (shoulder → elbow)
    _segment(big, L_sh, L_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
             w=11)
    _joint(big, L_sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
    _joint(big, L_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
    # Forearm (elbow → wrist) — horizontal across the chest
    _segment(big, L_el, L_wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
             w=10)
    # Soft shadow under where the right forearm will lie
    shadow = pygame.Surface((s(70), s(22)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (*L["SKIN_DK"], 130),
                        (0, 0, s(70), s(22)))
    big.blit(shadow, (cx - s(35), s(167)))
    # Left hand resting on right bicep
    _wrist_cuff(big, L_wr, w=10)
    _fist(big, (L_wr[0] + s(4), L_wr[1] - s(2)),
          L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)

    # Right arm (drawn on top)
    R_sh = (cx + s(54), s(140))
    R_el = (cx + s(42), s(172))
    R_wr = (cx - s(28), s(178))          # right wrist — across to LEFT bicep
    _segment(big, R_sh, R_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
             w=11)
    _joint(big, R_sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
    _joint(big, R_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
    _segment(big, R_el, R_wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
             w=10)
    _wrist_cuff(big, R_wr, w=10)
    _fist(big, (R_wr[0] - s(4), R_wr[1] - s(2)),
          L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)


# ─────────────────────────────────────────────────────────────────────────────
# Pose 2 — Palms-up offering ("what's your wish?")
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_2_offering(big, cx):
    """Both arms bent at the elbow, forearms angled forward + outward
    with PALMS UP. The classic genie 'what's your wish?' gesture."""
    L = P
    for side in (-1, +1):
        # Shoulder is on the outer flank, elbow tucks closer to body
        # and slightly DOWN, hands flare outward + slightly forward.
        sh = (cx + side * s(54), s(140))
        el = (cx + side * s(34), s(186))
        wr = (cx + side * s(54), s(214))
        # Bicep
        _segment(big, sh, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
        _joint(big, sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
        # Elbow
        _joint(big, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
        # Forearm extending out and slightly forward — palm up
        _segment(big, el, wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
        # Gold wrist cuff
        _wrist_cuff(big, wr, w=11)
        # Open palm UP — palm just past the cuff, slightly above
        palm_x = wr[0] + side * s(4)
        palm_y = wr[1] - s(4)
        _open_palm(big, (palm_x, palm_y),
                   L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
                   r_w=10, r_h=8, side=side)
        # Big magical shine above the palm — outer glow halo + cross
        # rays + bright cyan-gold core. Sized to read as the "offering
        # magic" being conjured (these are the shines that will fly
        # forward as the cast in the in-game cinematic).
        sparkle_y = palm_y - s(28)
        # Soft outer glow halo (cyan + gold, layered low-alpha)
        for r_n, alpha in ((24, 70), (18, 110), (12, 160)):
            srf = pygame.Surface((s(r_n) * 2 + 4, s(r_n) * 2 + 4),
                                 pygame.SRCALPHA)
            pygame.draw.circle(srf, (160, 230, 255, alpha),
                               (s(r_n) + 2, s(r_n) + 2), s(r_n))
            big.blit(srf, (palm_x - s(r_n) - 2,
                           sparkle_y - s(r_n) - 2))
        # Gold inner halo
        srf = pygame.Surface((s(16), s(16)), pygame.SRCALPHA)
        pygame.draw.circle(srf, (255, 230, 140, 230),
                           (s(8), s(8)), s(7))
        big.blit(srf, (palm_x - s(8), sparkle_y - s(8)))
        # 4-point star cross (thick gold)
        for dx, dy in ((s(12), 0), (-s(12), 0), (0, s(12)), (0, -s(12))):
            pygame.draw.line(big, P["GOLD_HI"],
                             (palm_x, sparkle_y),
                             (palm_x + dx, sparkle_y + dy), s(4))
        # White star core
        for dx, dy in ((s(8), 0), (-s(8), 0), (0, s(8)), (0, -s(8))):
            pygame.draw.line(big, (255, 255, 255),
                             (palm_x, sparkle_y),
                             (palm_x + dx, sparkle_y + dy), s(2))
        # Bright centre dot
        aa_circle(big, (255, 255, 255), palm_x, sparkle_y, s(3))
        # Two tiny satellite sparkles for extra magic
        for sat_dx, sat_dy in ((s(14), -s(10)), (-s(12), s(8))):
            sx_p = palm_x + sat_dx
            sy_p = sparkle_y + sat_dy
            pygame.draw.line(big, P["GOLD_HI"],
                             (sx_p - s(3), sy_p), (sx_p + s(3), sy_p),
                             max(1, s(1)))
            pygame.draw.line(big, P["GOLD_HI"],
                             (sx_p, sy_p - s(3)), (sx_p, sy_p + s(3)),
                             max(1, s(1)))
            aa_circle(big, (255, 255, 255), sx_p, sy_p, max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Pose 3 — Hands clasped at waist (butler / dignitary)
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_3_clasped(big, cx):
    """Both forearms angle down toward the centre of the belly.
    Hands meet above the sash with fingers interlaced."""
    L = P
    clasp_x = cx
    clasp_y = s(230)
    for side in (-1, +1):
        sh = (cx + side * s(54), s(140))
        el = (cx + side * s(46), s(186))
        wr = (cx + side * s(14), s(224))
        _segment(big, sh, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
        _joint(big, sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
        _joint(big, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
        _segment(big, el, wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
        _wrist_cuff(big, wr, w=10)
    # Clasped hands — single rounded shape in the middle
    aa_circle(big, L["SKIN_DK"], clasp_x + s(1), clasp_y + s(1), s(15))
    aa_circle(big, L["SKIN_LO"], clasp_x, clasp_y, s(14))
    aa_circle(big, L["SKIN"], clasp_x, clasp_y - s(1), s(13))
    aa_circle(big, L["SKIN_HI"], clasp_x - s(3), clasp_y - s(4), s(4))
    # Interlaced finger lines
    for fx in (-s(8), -s(3), s(2), s(7)):
        pygame.draw.line(big, L["SKIN_LO"],
                         (clasp_x + fx, clasp_y - s(8)),
                         (clasp_x + fx, clasp_y + s(8)),
                         max(2, s(1)))
    # Thumb ridges on each side
    for sx_off in (-s(12), s(12)):
        ell(big, L["SKIN_LO"], clasp_x + sx_off, clasp_y - s(2),
            s(5), s(9))
        ell(big, L["SKIN"], clasp_x + sx_off, clasp_y - s(2),
            s(4), s(7))


# ─────────────────────────────────────────────────────────────────────────────
# Pose 4 — Hand on heart + extended (Middle Eastern welcome)
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_4_heart_extended(big, cx):
    """Left hand pressed flat on chest over the heart; right arm
    extended forward + down with palm up."""
    L = P
    # LEFT arm — hand on heart
    L_sh = (cx - s(54), s(140))
    L_el = (cx - s(46), s(180))
    L_wr = (cx - s(10), s(174))       # wrist near the centre-chest
    _segment(big, L_sh, L_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
    _joint(big, L_sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
    _joint(big, L_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
    _segment(big, L_el, L_wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
    _wrist_cuff(big, L_wr, w=10)
    # Open palm pressed on chest — fingers splayed
    hand_x = L_wr[0] + s(6)
    hand_y = L_wr[1] - s(2)
    aa_circle(big, L["SKIN_DK"], hand_x + s(1), hand_y + s(1), s(13))
    aa_circle(big, L["SKIN_LO"], hand_x, hand_y, s(12))
    ell(big, L["SKIN"], hand_x, hand_y, s(22), s(20))
    ell(big, L["SKIN_HI"], hand_x - s(2), hand_y - s(3), s(10), s(4))
    # 4 finger ridges spreading upward
    for fx in (-s(8), -s(3), s(2), s(7)):
        ell(big, L["SKIN_LO"], hand_x + fx, hand_y - s(7), s(3), s(8))
        ell(big, L["SKIN"], hand_x + fx, hand_y - s(8), s(2), s(7))
    # Thumb sweeping inward
    ell(big, L["SKIN"], hand_x - s(11), hand_y, s(5), s(8))

    # RIGHT arm — extended forward and slightly down, palm up
    R_sh = (cx + s(54), s(140))
    R_el = (cx + s(58), s(180))
    R_wr = (cx + s(68), s(220))
    _segment(big, R_sh, R_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
    _joint(big, R_sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
    _joint(big, R_el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
    _segment(big, R_el, R_wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
    _wrist_cuff(big, R_wr, w=11)
    palm_x = R_wr[0] + s(4)
    palm_y = R_wr[1] - s(4)
    _open_palm(big, (palm_x, palm_y),
               L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
               r_w=10, r_h=8, side=+1)


# ─────────────────────────────────────────────────────────────────────────────
# Pose 5 — Open arms wide (ta-da welcome)
# ─────────────────────────────────────────────────────────────────────────────

def draw_arms_5_open_wide(big, cx):
    """Both arms extended outward horizontally, slightly above the
    shoulder line. Palms facing forward + slightly up."""
    L = P
    for side in (-1, +1):
        sh = (cx + side * s(54), s(140))
        el = (cx + side * s(82), s(132))
        wr = (cx + side * s(110), s(120))
        _segment(big, sh, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
        _joint(big, sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
        _joint(big, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
        _segment(big, el, wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
        _wrist_cuff(big, wr, w=11)
        # Open palm facing forward
        palm_x = wr[0] + side * s(4)
        palm_y = wr[1] - s(2)
        _open_palm(big, (palm_x, palm_y),
                   L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
                   r_w=10, r_h=8, side=side)
        # Tiny sparkle near each open palm — sells the "ta-da"
        sparkle_x = palm_x + side * s(14)
        sparkle_y = palm_y - s(6)
        pygame.draw.line(big, P["GOLD_HI"],
                         (sparkle_x - s(3), sparkle_y),
                         (sparkle_x + s(3), sparkle_y), s(2))
        pygame.draw.line(big, P["GOLD_HI"],
                         (sparkle_x, sparkle_y - s(3)),
                         (sparkle_x, sparkle_y + s(3)), s(2))


# ─────────────────────────────────────────────────────────────────────────────
# Composer — render a full A1 figure with a swapped-in arm pose
# ─────────────────────────────────────────────────────────────────────────────


# ═════════════════════════════════════════════════════════════════════════
# Consolidated from render_a1_crossed_legs_variants.py
# ═════════════════════════════════════════════════════════════════════════


def _pant_polygon(big, pts, shadow_offset=(2, 2)):
    """Pant fabric — drop shadow + mid + base + flank highlight."""
    sx_off, sy_off = shadow_offset
    pygame.draw.polygon(big, P["PANT_DK"],
                        [(x + s(sx_off), y + s(sy_off)) for x, y in pts])
    pygame.draw.polygon(big, P["PANT_LO"], pts)
    inner = [(int(x * 0.97 + sum(p[0] for p in pts) / len(pts) * 0.03),
              int(y * 0.97 + sum(p[1] for p in pts) / len(pts) * 0.03))
             for x, y in pts]
    pygame.draw.polygon(big, P["PANT"], inner)


def _pant_pleats(big, pts):
    """Two faint pleat ripples down the centre of a pant polygon."""
    cx_p = sum(p[0] for p in pts) // len(pts)
    cy_p = sum(p[1] for p in pts) // len(pts)
    for off_x in (-s(4), s(4)):
        pygame.draw.line(big, P["PANT_LO"],
                         (cx_p + off_x, cy_p - s(12)),
                         (cx_p + off_x, cy_p + s(12)),
                         max(1, s(1)))


def _gold_ankle_cuff(big, cx_a, cy_a, angle_deg=0, w_native=18):
    """Gold cuff around an ankle. Rendered as a rotated rounded
    band so it works for legs at any angle."""
    cuff = pygame.Surface((s(w_native), s(10)), pygame.SRCALPHA)
    cw, ch = cuff.get_size()
    pygame.draw.rect(cuff, P["GOLD_LO"], (0, 0, cw, ch))
    pygame.draw.rect(cuff, P["GOLD"], (s(1), s(1), cw - s(2), ch - s(2)))
    pygame.draw.line(cuff, P["GOLD_HI"], (s(2), s(2)),
                     (cw - s(2), s(2)), max(1, s(1)))
    cuff_rot = pygame.transform.rotate(cuff, angle_deg)
    rect = cuff_rot.get_rect(center=(int(cx_a), int(cy_a)))
    big.blit(cuff_rot, rect.topleft)


def _slipper(big, cx_s, cy_s, angle_deg=0, mirror=False, scale=1.0):
    """Curled-toe slipper rotated by angle_deg around (cx_s, cy_s).
    `mirror=True` flips it left-right so the curl points the other
    way."""
    sw = int(s(40) * scale)
    sh = int(s(20) * scale)
    sl = pygame.Surface((sw, sh), pygame.SRCALPHA)
    base_pts = [
        (s(2), s(13)),
        (sw - s(14), s(13)),
        (sw - s(2), s(9)),
        (sw - s(6), s(3)),
        (sw - s(14), s(7)),
        (s(2), s(7)),
    ]
    if mirror:
        base_pts = [(sw - x, y) for x, y in base_pts]
    pygame.draw.polygon(sl, P["GOLD_DK"],
                        [(x + s(1), y + s(1)) for x, y in base_pts])
    pygame.draw.polygon(sl, P["GOLD"], base_pts)
    # Highlight stripe
    pygame.draw.line(sl, P["GOLD_HI"],
                     (s(6) if not mirror else sw - s(6), s(8)),
                     (s(14) if not mirror else sw - s(14), s(8)),
                     max(2, s(1)))
    # Ruby gem on the curled toe
    gem_x = sw - s(6) if not mirror else s(6)
    gem_y = s(6)
    pygame.draw.polygon(sl, P["RUBY"],
                        [(gem_x, gem_y - s(2)),
                         (gem_x + s(2), gem_y),
                         (gem_x, gem_y + s(2)),
                         (gem_x - s(2), gem_y)])
    pygame.draw.circle(sl, (255, 200, 220),
                       (gem_x - s(1), gem_y - s(1)), max(1, s(1)))
    sl_rot = pygame.transform.rotate(sl, angle_deg)
    rect = sl_rot.get_rect(center=(int(cx_s), int(cy_s)))
    big.blit(sl_rot, rect.topleft)


def _smoke_aura_below(big, cx, top_y):
    """Atmospheric smoke cloud filling the space below the crossed
    legs — replaces v6's draw_smoke_aura behind the standing figure."""
    for i, (dx, dy, w, h, alpha) in enumerate((
            (-100, 380, 140, 70, 70),
            ( 100, 380, 140, 70, 70),
            (   0, 410, 230, 60, 60),
            (-140, 340, 90, 50, 55),
            ( 140, 340, 90, 50, 55),
            (-60, 365, 80, 40, 50),
            ( 60, 365, 80, 40, 50))):
        srf = pygame.Surface((s(w + 4), s(h + 4)), pygame.SRCALPHA)
        pygame.draw.ellipse(srf, (*P["SKIN_HI"], alpha),
                            (s(2), s(2), s(w), s(h)))
        big.blit(srf, (s(W // 2 + dx - w / 2), s(dy - h / 2)))


# ─────────────────────────────────────────────────────────────────────────────
# v3 — all five variants are FULL LOTUS with progressively fuller /
# bagger / more decorated pants. User feedback: the v2 legs were too
# thin compared to the standing pose. v3 widens the polygons + adds
# fabric drapery + pleats so the lotus reads as a real harem-pants
# silhouette instead of skinny triangles.
# ─────────────────────────────────────────────────────────────────────────────

def _draw_thigh(big, hip_in, hip_out, knee_inner, knee_outer):
    """Thigh polygon from a hip seat-edge to a knee, with the OUT side
    forming the leg's outer silhouette."""
    pts = [hip_in, hip_out, knee_outer, knee_inner]
    _pant_polygon(big, pts)
    _pant_pleats(big, pts)


def _draw_shin(big, knee_top, knee_bot, foot_top, foot_bot):
    """Shin polygon — same fabric treatment as the thigh."""
    pts = [knee_top, knee_bot, foot_bot, foot_top]
    _pant_polygon(big, pts)
    _pant_pleats(big, pts)


def _cross_shadow(big, cx, y, w=80, h=20, alpha=130):
    """Soft shadow under the top shin so the cross-over reads."""
    sh = pygame.Surface((s(w), s(h)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (*P["PANT_DK"], alpha), (0, 0, s(w), s(h)))
    big.blit(sh, (cx - s(w // 2), y - s(h // 2)))


def _baggy_thigh(big, cx, side, hip_w=20, top_y=248,
                 widest_y=280, widest_w=58,
                 knee_y=300, knee_w=42):
    """Curved/billowing thigh polygon: narrow at the hip, bulges out
    near `widest_y`, then comes back in toward the knee. Multiple
    polygon points make it look like fabric instead of a triangle."""
    pts = [
        (cx + side * s(8),               top_y),                 # inner hip
        (cx + side * s(hip_w),           top_y),                 # outer hip
        (cx + side * s(hip_w + 14),      top_y + s(14)),         # shoulder of bulge
        (cx + side * s(widest_w),        widest_y),              # widest point (knee outer)
        (cx + side * s(widest_w - 6),    widest_y + s(14)),
        (cx + side * s(knee_w + 4),      knee_y),                # knee bottom outer
        (cx + side * s(knee_w - 16),     knee_y + s(4)),         # knee inner
        (cx + side * s(2),               widest_y - s(2)),       # back up inner
    ]
    _pant_polygon(big, pts)
    # Pleat ripples down the thigh — soft inner shadow lines
    for off_x, off_y_top, off_y_bot in (
            (side * s(-4),  s(14), s(40)),
            (side * s(-12), s(10), s(38)),
            (side * s(-22), s(6),  s(34))):
        pygame.draw.line(big, P["PANT_LO"],
                         (cx + side * s(20) + off_x, top_y + off_y_top),
                         (cx + side * s(34) + off_x, top_y + off_y_bot),
                         max(2, s(1)))
    # Outer-flank gloss highlight
    pygame.draw.line(big, P["PANT_HI"],
                     (cx + side * s(hip_w + 8), top_y + s(10)),
                     (cx + side * s(widest_w - 2), widest_y),
                     s(3))
    pygame.draw.line(big, P["PANT_HI"],
                     (cx + side * s(widest_w - 2), widest_y),
                     (cx + side * s(knee_w), knee_y - s(2)),
                     s(2))


def _full_shin(big, cx, side, knee_x, knee_y, foot_x, foot_y,
               knee_width=44, mid_width=40, ankle_width=22):
    """BAGGY shin polygon — bulges out near the knee + mid-shin so the
    lower leg reads as harem-pant fabric rather than a stick, then
    tapers to a cinched ankle. Six anchor points along each side."""
    # Direction vector along the shin (knee → foot)
    dx, dy = foot_x - knee_x, foot_y - knee_y
    length = max(1.0, math.hypot(dx, dy))
    # Perpendicular unit vector
    px, py = -dy / length, dx / length

    # 4 sample points along the shin centreline.
    def along(t):
        return (knee_x + dx * t, knee_y + dy * t)
    pts_centre = [along(0.0), along(0.35), along(0.7), along(1.0)]
    widths = [s(knee_width), s(mid_width), s(mid_width - 6), s(ankle_width)]

    # Outer side (away from body)
    outer = [(c[0] + px * w / 2, c[1] + py * w / 2)
             for c, w in zip(pts_centre, widths)]
    # Inner side
    inner = [(c[0] - px * w / 2, c[1] - py * w / 2)
             for c, w in zip(pts_centre, widths)]
    pts = outer + list(reversed(inner))
    _pant_polygon(big, [(int(x), int(y)) for x, y in pts])

    # Knee bulge — extra darker ellipse at the knee end for volume
    kb = pygame.Surface((s(knee_width + 4), s(knee_width // 2 + 4)),
                        pygame.SRCALPHA)
    pygame.draw.ellipse(kb, (*P["PANT_LO"], 200),
                        (0, 0, s(knee_width + 4), s(knee_width // 2 + 4)))
    angle_deg = math.degrees(math.atan2(dy, dx)) - 90
    kb_rot = pygame.transform.rotate(kb, angle_deg)
    rect = kb_rot.get_rect(center=(int(knee_x), int(knee_y)))
    big.blit(kb_rot, rect.topleft)

    # Pleat ripples down the shin (3 lines parallel to centreline)
    for off in (-s(8), 0, s(8)):
        p_start = (along(0.15)[0] + px * off, along(0.15)[1] + py * off)
        p_end   = (along(0.85)[0] + px * off * 0.5,
                   along(0.85)[1] + py * off * 0.5)
        pygame.draw.line(big, P["PANT_LO"],
                         (int(p_start[0]), int(p_start[1])),
                         (int(p_end[0]), int(p_end[1])),
                         max(2, s(1)))

    # Outer-flank gloss highlight
    pygame.draw.line(big, P["PANT_HI"],
                     (int(outer[0][0]), int(outer[0][1])),
                     (int(outer[2][0]), int(outer[2][1])),
                     s(3))
    pygame.draw.line(big, P["PANT_HI"],
                     (int(outer[2][0]), int(outer[2][1])),
                     (int(outer[3][0]), int(outer[3][1])),
                     s(2))


# ─────────────────────────────────────────────────────────────────────────────
# All 5 variants below are FULL LOTUS (padmasana) — both feet rest on
# top of opposite thighs. They vary in how FULL / BAGGY / DECORATED the
# pants are. Variant 1 is the most modest; variant 5 is maximum poof.
# ─────────────────────────────────────────────────────────────────────────────


def _full_lotus_pose(big, cx, hip_w=20, widest_w=60, knee_w=44,
                     hip_y_n=248, widest_y_n=278, knee_y_n=302,
                     foot_y_n=270, slipper_scale=1.0,
                     extra_pleats=False, extra_drape=False,
                     gold_trim=False, embroidery=False):
    """Compose a full-lotus seat with configurable fullness.

    `hip_w`, `widest_w`, `knee_w` are *half-widths* in native px:
        - hip_w     = how wide the hip seat-edge is
        - widest_w  = how far the thigh bulges out at its widest
        - knee_w    = how wide the knee/ankle edge is
    `extra_pleats`, `extra_drape`, `gold_trim`, `embroidery` flip
    additional decorations on.
    """
    hip_y    = s(hip_y_n)
    widest_y = s(widest_y_n)
    knee_y   = s(knee_y_n)
    foot_y   = s(foot_y_n)

    # ── THIGHS (drawn first, very baggy) ────────────────────────────
    for side in (-1, +1):
        _baggy_thigh(big, cx, side,
                     hip_w=hip_w, top_y=hip_y,
                     widest_y=widest_y, widest_w=widest_w,
                     knee_y=knee_y, knee_w=knee_w)

    # ── Optional extra fabric drape: a hanging fold below each thigh
    if extra_drape:
        for side in (-1, +1):
            drape = [
                (cx + side * s(knee_w + 6),  knee_y + s(4)),
                (cx + side * s(knee_w - 12), knee_y + s(20)),
                (cx + side * s(knee_w - 32), knee_y + s(24)),
                (cx + side * s(knee_w - 28), knee_y + s(8)),
            ]
            _pant_polygon(big, drape)
            pygame.draw.line(big, P["PANT_LO"],
                             ((drape[0][0] + drape[3][0]) // 2,
                              (drape[0][1] + drape[3][1]) // 2),
                             ((drape[1][0] + drape[2][0]) // 2,
                              (drape[1][1] + drape[2][1]) // 2),
                             max(2, s(1)))

    # ── Optional extra pleats
    if extra_pleats:
        for side in (-1, +1):
            for px_off, py_top, py_bot in (
                    (s(-2), s(8), s(38)),
                    (s(-10), s(6), s(36)),
                    (s(-20), s(4), s(32)),
                    (s(-28), s(2), s(28))):
                pygame.draw.line(big, (35, 95, 145),
                                 (cx + side * (s(widest_w - 8) + px_off),
                                  hip_y + py_top),
                                 (cx + side * (s(widest_w - 14) + px_off),
                                  hip_y + py_bot),
                                 max(1, s(1)))

    # ── SHINS (lotus — feet curve UP on top of opposite thigh) ──────
    # Steeper angle now so the shin reads as bent UP, not horizontal.
    # RIGHT shin: from right knee outer-down to ankle resting on LEFT
    # thigh outer-upper. Wider and tapered.
    _full_shin(big, cx, side=+1,
               knee_x=cx + s(widest_w - 4), knee_y=widest_y + s(8),
               foot_x=cx - s(widest_w - 20), foot_y=foot_y + s(2),
               knee_width=46, mid_width=40, ankle_width=24)
    # LEFT shin mirrored
    _full_shin(big, cx, side=-1,
               knee_x=cx - s(widest_w - 4), knee_y=widest_y + s(8),
               foot_x=cx + s(widest_w - 20), foot_y=foot_y + s(2),
               knee_width=46, mid_width=40, ankle_width=24)

    # ── Slippers + ankle cuffs ON TOP of opposite thighs ───────────
    # Pushed further out so they sit on the thigh bulge, not over
    # the central sash buckle. Bigger scale so they balance the
    # fuller pants.
    big_sl_scale = slipper_scale * 1.15
    big_cuff_w   = 26
    # Right foot on left thigh outer
    _slipper(big, cx - s(widest_w - 22), foot_y - s(2),
             angle_deg=12, mirror=True, scale=big_sl_scale)
    _gold_ankle_cuff(big, cx - s(widest_w - 12), foot_y + s(2),
                     angle_deg=22, w_native=big_cuff_w)
    # Left foot on right thigh outer
    _slipper(big, cx + s(widest_w - 22), foot_y - s(2),
             angle_deg=-12, scale=big_sl_scale)
    _gold_ankle_cuff(big, cx + s(widest_w - 12), foot_y + s(2),
                     angle_deg=-22, w_native=big_cuff_w)

    # ── Optional gold trim along the knee bulge ─────────────────────
    if gold_trim:
        for side in (-1, +1):
            pygame.draw.arc(big, P["GOLD_LO"],
                            (cx + side * s(widest_w - 16) - s(20),
                             widest_y - s(10),
                             s(40), s(28)),
                            math.radians(20 if side > 0 else 110),
                            math.radians(160 if side > 0 else 250),
                            max(3, s(2)))
            pygame.draw.arc(big, P["GOLD"],
                            (cx + side * s(widest_w - 16) - s(20),
                             widest_y - s(10),
                             s(40), s(28)),
                            math.radians(20 if side > 0 else 110),
                            math.radians(160 if side > 0 else 250),
                            max(2, s(1)))

    # ── Optional embroidery: gem-dotted line along the lower edge
    if embroidery:
        for side in (-1, +1):
            for fx in range(0, 35, 6):
                ex = cx + side * s(widest_w - fx - 4)
                ey = widest_y + s(20)
                pygame.draw.circle(big, P["GOLD"],
                                   (ex, ey), max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Full lotus, fuller pants (baseline upgrade from v2)
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_full_lotus(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=22, widest_w=58, knee_w=42,
                     extra_pleats=False)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Full lotus, baggy + pleated
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_ankle_cross(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=24, widest_w=66, knee_w=46,
                     extra_pleats=True)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Full lotus, gold trim along knees
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_tight_tuck(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=22, widest_w=64, knee_w=44,
                     extra_pleats=True,
                     gold_trim=True,
                     embroidery=True)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Full lotus, EXTRA baggy with drape hanging below
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_half_lotus_smoke(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=26, widest_w=70, knee_w=50,
                     extra_pleats=True,
                     extra_drape=True)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Full lotus, MAXIMUM poof MC-Hammer / Disney genie style
# ─────────────────────────────────────────────────────────────────────────────
def draw_crossed_legs_side_recline(big, cx):
    _full_lotus_pose(big, cx,
                     hip_w=28, widest_w=78, knee_w=54,
                     hip_y_n=246, widest_y_n=280, knee_y_n=308,
                     foot_y_n=270,
                     extra_pleats=True,
                     extra_drape=True,
                     gold_trim=True,
                     embroidery=True,
                     slipper_scale=1.05)


# ─────────────────────────────────────────────────────────────────────────────
# Composer
# ─────────────────────────────────────────────────────────────────────────────


# ═════════════════════════════════════════════════════════════════════════
# Consolidated from render_a1_shine_variants.py
# ═════════════════════════════════════════════════════════════════════════



def shine_1_classic_pixie(big, px, py):
    """Classic Disney-pixie 4-point sparkle. Long thin gold arms with
    a sharp white-gold diamond centre. NO halo — crisp & graphic."""
    GOLD = (255, 220, 130)
    GOLD_LO = (200, 165, 70)
    WHITE = (255, 255, 245)
    # Long thin star arms
    for dx, dy in ((s(16), 0), (-s(16), 0),
                   (0, s(16)), (0, -s(16))):
        # Arm shape: wide near centre, thin at tip
        pygame.draw.polygon(big, GOLD_LO,
                            [(px, py),
                             (px + dx // 4 - dy // 8, py + dy // 4 + dx // 8),
                             (px + dx, py + dy),
                             (px + dx // 4 + dy // 8, py + dy // 4 - dx // 8)])
        pygame.draw.polygon(big, GOLD,
                            [(px, py),
                             (px + dx // 4 - dy // 12, py + dy // 4 + dx // 12),
                             (px + int(dx * 0.92), py + int(dy * 0.92)),
                             (px + dx // 4 + dy // 12, py + dy // 4 - dx // 12)])
    # Central white diamond (4-point inner shape)
    pygame.draw.polygon(big, WHITE,
                        [(px, py - s(7)), (px + s(7), py),
                         (px, py + s(7)), (px - s(7), py)])
    pygame.draw.polygon(big, GOLD,
                        [(px, py - s(4)), (px + s(4), py),
                         (px, py + s(4)), (px - s(4), py)])
    # Tiny accent dots at the arm tips
    for dx, dy in ((s(18), 0), (-s(18), 0),
                   (0, s(18)), (0, -s(18))):
        pygame.draw.circle(big, WHITE, (px + dx, py + dy), max(1, s(1)))


def shine_2_radial_burst(big, px, py):
    """8-ray radial burst — like a magical 'pop' going outward.
    Each ray is a thin triangle wedge fading from bright gold to
    translucent at the tip. Bright white core."""
    GOLD = (255, 225, 140)
    GOLD_HI = (255, 245, 200)
    WHITE = (255, 255, 250)
    n_rays = 8
    ray_len = s(20)
    base_w = s(4)
    for i in range(n_rays):
        ang = math.radians(i * (360 / n_rays))
        cx_o = math.cos(ang)
        cy_o = math.sin(ang)
        # Perpendicular for base width
        px_o = -cy_o
        py_o = cx_o
        # Wedge polygon: wide at base near centre, point at tip
        tip = (px + cx_o * ray_len, py + cy_o * ray_len)
        b_left = (px + px_o * base_w / 2, py + py_o * base_w / 2)
        b_right = (px - px_o * base_w / 2, py - py_o * base_w / 2)
        # Draw shadow wedge (slightly larger, darker)
        pygame.draw.polygon(big, GOLD,
                            [(int(b_left[0]), int(b_left[1])),
                             (int(tip[0]), int(tip[1])),
                             (int(b_right[0]), int(b_right[1]))])
        # Inner bright wedge
        tip2 = (px + cx_o * ray_len * 0.85,
                py + cy_o * ray_len * 0.85)
        pygame.draw.polygon(big, GOLD_HI,
                            [(int(b_left[0]), int(b_left[1])),
                             (int(tip2[0]), int(tip2[1])),
                             (int(b_right[0]), int(b_right[1]))])
    # Bright white core
    aa_circle(big, GOLD_HI, px, py, s(6))
    aa_circle(big, WHITE, px, py, s(4))
    aa_circle(big, (255, 255, 255), px - s(1), py - s(1), s(2))


def shine_3_orb_of_light(big, px, py):
    """Soft glowing orb — no star points, just a luminous sphere of
    magical energy with internal sparkles. Reads as 'contained
    magic' rather than 'bursting magic'."""
    CYAN = (160, 230, 255)
    CYAN_HI = (220, 245, 255)
    WHITE = (255, 255, 250)
    # Outer glow layers
    for r_n, alpha in ((22, 50), (16, 90), (12, 140)):
        srf = pygame.Surface((s(r_n) * 2 + 4, s(r_n) * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(srf, (*CYAN, alpha),
                           (s(r_n) + 2, s(r_n) + 2), s(r_n))
        big.blit(srf, (px - s(r_n) - 2, py - s(r_n) - 2))
    # Solid inner orb
    aa_circle(big, CYAN, px, py, s(9))
    aa_circle(big, CYAN_HI, px, py, s(7))
    aa_circle(big, WHITE, px - s(2), py - s(2), s(3))
    # Internal mini-sparkles ("stars inside the orb")
    for dx, dy in ((s(3), s(2)), (-s(3), -s(1)), (s(1), -s(4))):
        aa_circle(big, WHITE, px + dx, py + dy, max(1, s(1)))
    # Tiny outer satellite dot above the orb (highlight reflection)
    aa_circle(big, WHITE, px + s(2), py - s(6), max(1, s(1)))


def shine_4_twinkle_cluster(big, px, py):
    """Three twinkle stars in a cluster — main star + 2 smaller
    satellites. Asymmetric, feels like magical pixie dust rather
    than a single discrete spark."""
    GOLD = (255, 225, 140)
    GOLD_HI = (255, 245, 200)
    WHITE = (255, 255, 250)

    def _star(cx_s, cy_s, arm_len, arm_w):
        """Thin 4-point star centred at (cx_s, cy_s)."""
        for dx, dy in ((arm_len, 0), (-arm_len, 0),
                       (0, arm_len), (0, -arm_len)):
            pygame.draw.line(big, GOLD,
                             (cx_s, cy_s),
                             (cx_s + dx, cy_s + dy),
                             arm_w + s(1))
            pygame.draw.line(big, GOLD_HI,
                             (cx_s, cy_s),
                             (cx_s + dx, cy_s + dy),
                             arm_w)
        aa_circle(big, WHITE, cx_s, cy_s, max(1, arm_w // 2))

    # Main star — bigger, at the cluster centre
    _star(px, py, arm_len=s(11), arm_w=s(2))
    # Two smaller satellite stars at offsets
    _star(px + s(11), py - s(8), arm_len=s(6), arm_w=s(1))
    _star(px - s(10), py + s(7), arm_len=s(5), arm_w=s(1))
    # A 4th tiny dot for fullness
    aa_circle(big, WHITE, px + s(7), py + s(10), max(1, s(1)))


def shine_5_crystal_gem(big, px, py):
    """A faceted magical crystal hovering above the palm — tall
    diamond shape with internal gradient + a soft halo. Reads as
    'wish gem' — most thematic for a genie offering wishes."""
    CYAN = (160, 230, 255)
    CYAN_HI = (220, 245, 255)
    BLUE_DK = (40, 90, 150)
    BLUE_MID = (80, 150, 220)
    GOLD = (255, 225, 140)
    WHITE = (255, 255, 250)
    # Soft halo behind the gem
    for r_n, alpha in ((18, 70), (14, 110)):
        srf = pygame.Surface((s(r_n) * 2 + 4, s(r_n) * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(srf, (*CYAN, alpha),
                           (s(r_n) + 2, s(r_n) + 2), s(r_n))
        big.blit(srf, (px - s(r_n) - 2, py - s(r_n) - 2))
    # Crystal shape (tall diamond with faceted middle)
    top = (px, py - s(12))
    bot = (px, py + s(10))
    left = (px - s(7), py - s(1))
    right = (px + s(7), py - s(1))
    mid_left = (px - s(5), py + s(3))
    mid_right = (px + s(5), py + s(3))
    # Dark shadow side (right)
    pygame.draw.polygon(big, BLUE_DK,
                        [top, right, mid_right, bot])
    # Mid-tone fill (left bright side)
    pygame.draw.polygon(big, BLUE_MID,
                        [top, left, mid_left, bot])
    # Top-left highlight facet
    pygame.draw.polygon(big, CYAN_HI,
                        [top, left, (px - s(2), py - s(5))])
    # Centre bright stripe
    pygame.draw.line(big, WHITE,
                     (px - s(1), py - s(10)),
                     (px - s(1), py + s(8)),
                     max(2, s(1)))
    # Top vertex sparkle
    pygame.draw.line(big, GOLD,
                     (px - s(4), py - s(12)),
                     (px + s(4), py - s(12)),
                     s(2))
    aa_circle(big, WHITE, px, py - s(12), s(2))
    # Tiny satellite sparkles flanking the gem
    for sat_dx, sat_dy in ((s(12), -s(6)), (-s(11), s(2))):
        sxp = px + sat_dx
        syp = py + sat_dy
        pygame.draw.line(big, GOLD,
                         (sxp - s(3), syp), (sxp + s(3), syp),
                         max(1, s(1)))
        pygame.draw.line(big, GOLD,
                         (sxp, syp - s(3)), (sxp, syp + s(3)),
                         max(1, s(1)))
        aa_circle(big, WHITE, sxp, syp, max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Arms helper that takes a shine_fn so we don't duplicate the rest of
# the offering pose. (Copy of draw_arms_2_offering with the inline
# shine swapped for a callback.)
# ─────────────────────────────────────────────────────────────────────────────

def draw_offering_arms_with_shine(big, cx, shine_fn):
    L = P
    for side in (-1, +1):
        sh = (cx + side * s(54), s(140))
        el = (cx + side * s(34), s(186))
        wr = (cx + side * s(54), s(214))
        _segment(big, sh, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=11)
        _joint(big, sh, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=9)
        _joint(big, el, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], r=8)
        _segment(big, el, wr, L["SKIN"], L["SKIN_LO"], L["SKIN_HI"], w=10)
        _wrist_cuff(big, wr, w=11)
        palm_x = wr[0] + side * s(4)
        palm_y = wr[1] - s(4)
        _open_palm(big, (palm_x, palm_y),
                   L["SKIN"], L["SKIN_LO"], L["SKIN_HI"],
                   r_w=10, r_h=8, side=side)
        # Shine ABOVE the palm — caller provides the design
        shine_fn(big, palm_x, palm_y - s(28))


# ─────────────────────────────────────────────────────────────────────────────
# Composer + sheet
# ─────────────────────────────────────────────────────────────────────────────


# ═════════════════════════════════════════════════════════════════════════
# Consolidated from render_a1_carpet_variants.py
# ═════════════════════════════════════════════════════════════════════════



def _carpet_perspective_quad(cx, cy_top, half_w_front, half_w_back, height):
    """Trapezoidal quad with the FRONT (bottom) edge wider than the
    BACK (top) edge — gives a faux-3D 'tilted toward viewer' look.
    Returns 4 points in clockwise order: TL, TR, BR, BL."""
    return [
        (cx - half_w_back,  cy_top),
        (cx + half_w_back,  cy_top),
        (cx + half_w_front, cy_top + height),
        (cx - half_w_front, cy_top + height),
    ]


def _shadow_oval(big, cx, cy, w, h, alpha=120):
    """Soft elliptical shadow blot below the carpet to sell that it
    floats above the ground."""
    sh = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (10, 12, 30, alpha), (2, 2, w, h))
    big.blit(sh, (cx - w // 2, cy - h // 2))


def _tassel(big, x, y, color_a, color_b, color_tip, length=s(14)):
    """A dangling tassel with a knot ball + 5 hanging threads."""
    aa_circle(big, color_b, x + s(1), y + s(1), s(4))
    aa_circle(big, color_a, x, y, s(3))
    aa_circle(big, color_tip, x - s(1), y - s(1), s(1))
    for dx in (-s(3), -s(1), s(1), s(3), s(5)):
        pygame.draw.line(big, color_a,
                         (x + dx, y + s(2)),
                         (x + dx - s(1), y + length),
                         max(2, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Design 1 — Aladdin / Disney style
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_aladdin(big, cx):
    """Magenta/burgundy carpet with gold zigzag border, big tassels,
    front edge curling up. Disney Aladdin reference."""
    BURG    = (165,  35,  75)
    BURG_HI = (215,  70, 115)
    BURG_LO = ( 95,  15,  45)
    GOLD    = (245, 205, 105)
    GOLD_HI = (255, 240, 175)
    GOLD_LO = (160, 115,  30)
    BLACK   = ( 18,  14,  10)

    # Soft shadow below
    _shadow_oval(big, cx, s(338), s(220), s(24), alpha=120)

    # Main carpet body (trapezoid, wider at front)
    cy_top  = s(286)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(140),
                                    half_w_back=s(110),
                                    height=s(42))
    pygame.draw.polygon(big, BURG_LO,
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, BURG, body)
    # Front-edge curl: a thin dark stripe at the bottom suggesting
    # the carpet folds under itself
    pygame.draw.polygon(big, BURG_LO,
                        [(body[3][0], body[3][1] - s(2)),
                         (body[2][0], body[2][1] - s(2)),
                         (body[2][0] - s(4), body[2][1] + s(6)),
                         (body[3][0] + s(4), body[3][1] + s(6))])
    # Highlight stripe across the top — suggests sheen
    pygame.draw.line(big, BURG_HI,
                     (body[0][0] + s(8), body[0][1] + s(3)),
                     (body[1][0] - s(8), body[1][1] + s(3)),
                     max(2, s(1)))

    # Gold zigzag border around all four sides
    zigzag_step = s(8)
    # Top edge
    pts = []
    for i in range(0, body[1][0] - body[0][0], zigzag_step):
        x = body[0][0] + i
        y = body[0][1] + (s(2) if (i // zigzag_step) % 2 == 0 else s(6))
        pts.append((x, y))
    if len(pts) >= 2:
        pygame.draw.lines(big, GOLD, False, pts, max(2, s(1)))
    # Bottom edge (wider, more zigzags)
    pts = []
    for i in range(0, body[2][0] - body[3][0], zigzag_step):
        x = body[3][0] + i
        y = body[3][1] - (s(2) if (i // zigzag_step) % 2 == 0 else s(6))
        pts.append((x, y))
    if len(pts) >= 2:
        pygame.draw.lines(big, GOLD, False, pts, max(2, s(1)))
    # Side edges — diagonal gold stripes
    for a, b in ((body[0], body[3]), (body[1], body[2])):
        pygame.draw.line(big, GOLD, a, b, max(2, s(1)))

    # Central star/diamond motif
    cs_y = cy_top + s(20)
    pygame.draw.polygon(big, GOLD_LO,
                        [(cx, cs_y - s(10)), (cx + s(10), cs_y),
                         (cx, cs_y + s(10)), (cx - s(10), cs_y)])
    pygame.draw.polygon(big, GOLD,
                        [(cx, cs_y - s(8)), (cx + s(8), cs_y),
                         (cx, cs_y + s(8)), (cx - s(8), cs_y)])
    aa_circle(big, GOLD_HI, cx, cs_y, s(3))

    # 4 corner tassels (gold knot + crimson threads)
    for corner in body:
        _tassel(big, corner[0], corner[1] + s(2),
                color_a=BURG, color_b=BURG_LO, color_tip=GOLD)


# ─────────────────────────────────────────────────────────────────────────────
# Design 2 — Persian rug (ornate medallion + geometric border)
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_persian(big, cx):
    """Classic Persian carpet: deep red base, ornate central
    medallion, geometric border pattern, fringe on the short edges."""
    RED      = (140,  35,  40)
    RED_HI   = (190,  55,  65)
    RED_LO   = ( 90,  20,  25)
    DEEP     = ( 50,  18,  20)
    GOLD     = (235, 195, 100)
    GOLD_HI  = (255, 240, 175)
    CREAM    = (240, 220, 170)
    NAVY     = ( 40,  50,  90)
    EMERALD  = ( 65, 160,  85)

    _shadow_oval(big, cx, s(336), s(210), s(20), alpha=110)

    cy_top = s(288)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(135),
                                    half_w_back=s(110),
                                    height=s(38))
    pygame.draw.polygon(big, RED_LO,
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, RED, body)

    # Inner navy border (1-unit inset from edge)
    inset = s(6)
    inner = [
        (body[0][0] + inset, body[0][1] + inset),
        (body[1][0] - inset, body[1][1] + inset),
        (body[2][0] - inset, body[2][1] - inset),
        (body[3][0] + inset, body[3][1] - inset),
    ]
    pygame.draw.polygon(big, NAVY, inner)

    # Border-pattern: alternating gold/cream small diamonds along
    # the navy frame
    n = 14
    for i in range(n):
        t = (i + 0.5) / n
        # Top edge
        x = inner[0][0] + (inner[1][0] - inner[0][0]) * t
        y = inner[0][1] + (inner[1][1] - inner[0][1]) * t
        color = GOLD if i % 2 == 0 else CREAM
        pygame.draw.polygon(big, color,
                            [(int(x), int(y)),
                             (int(x) + s(2), int(y) + s(2)),
                             (int(x), int(y) + s(4)),
                             (int(x) - s(2), int(y) + s(2))])
        # Bottom edge
        x = inner[3][0] + (inner[2][0] - inner[3][0]) * t
        y = inner[3][1] + (inner[2][1] - inner[3][1]) * t
        pygame.draw.polygon(big, color,
                            [(int(x), int(y) - s(4)),
                             (int(x) + s(2), int(y) - s(2)),
                             (int(x), int(y)),
                             (int(x) - s(2), int(y) - s(2))])

    # Inner field — deep red
    field_inset = s(11)
    field = [
        (inner[0][0] + field_inset, inner[0][1] + field_inset),
        (inner[1][0] - field_inset, inner[1][1] + field_inset),
        (inner[2][0] - field_inset, inner[2][1] - field_inset),
        (inner[3][0] + field_inset, inner[3][1] - field_inset),
    ]
    pygame.draw.polygon(big, RED, field)

    # Central medallion — ornate gold + navy + emerald
    med_cy = cy_top + s(19)
    # Outer ring (gold)
    pygame.draw.circle(big, GOLD_HI, (cx, med_cy), s(13))
    pygame.draw.circle(big, GOLD,    (cx, med_cy), s(11))
    pygame.draw.circle(big, NAVY,    (cx, med_cy), s(9))
    pygame.draw.circle(big, CREAM,   (cx, med_cy), s(6))
    pygame.draw.circle(big, EMERALD, (cx, med_cy), s(3))
    # 8 radial petals
    for k in range(8):
        ang = math.radians(k * 45)
        tx = cx + math.cos(ang) * s(15)
        ty = med_cy + math.sin(ang) * s(15)
        pygame.draw.line(big, GOLD,
                         (cx + int(math.cos(ang) * s(11)),
                          med_cy + int(math.sin(ang) * s(11))),
                         (int(tx), int(ty)), max(2, s(1)))

    # Fringe on top and bottom edges (short white threads)
    for fx_step in range(int(body[0][0]) - s(2),
                         int(body[1][0]),
                         s(3)):
        pygame.draw.line(big, CREAM,
                         (fx_step, body[0][1] - s(4)),
                         (fx_step, body[0][1] + s(1)),
                         max(1, s(1) // 2))
    for fx_step in range(int(body[3][0]) - s(2),
                         int(body[2][0]),
                         s(3)):
        pygame.draw.line(big, CREAM,
                         (fx_step, body[3][1] - s(1)),
                         (fx_step, body[3][1] + s(4)),
                         max(1, s(1) // 2))


# ─────────────────────────────────────────────────────────────────────────────
# Design 3 — Royal velvet (purple + gold + stars + crescents)
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_royal(big, cx):
    """High-end royal velvet carpet — purple base with multiple layers
    of gold trim, an ornate central medallion, scattered stars +
    crescents arranged in a structured pattern, gem inlay corners,
    and detailed pom-pom + thread tassels. NO ground shadow."""
    PURPLE    = ( 80,  35, 130)
    PURPLE_HI = (140,  85, 200)
    PURPLE_MID= (110,  55, 165)
    PURPLE_LO = ( 45,  18,  85)
    PURPLE_DK = ( 25,  10,  50)
    GOLD      = (245, 205, 105)
    GOLD_HI   = (255, 240, 175)
    GOLD_MID  = (220, 175,  70)
    GOLD_LO   = (160, 115,  30)
    GOLD_DK   = (110,  75,  15)
    WHITE     = (250, 245, 230)
    RUBY      = (220,  60,  80)
    RUBY_HI   = (255, 175, 195)
    EMERALD   = ( 65, 180,  95)
    SAPPHIRE  = ( 70, 130, 220)

    cy_top = s(286)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(140),
                                    half_w_back=s(110),
                                    height=s(42))
    # ── Base velvet body (multi-tone for depth) ─────────────────
    pygame.draw.polygon(big, PURPLE_DK,
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, PURPLE_LO, body)
    # Mid-tone inset for the velvet's volume
    inset_pad = s(2)
    body_in = [
        (body[0][0] + inset_pad, body[0][1] + inset_pad),
        (body[1][0] - inset_pad, body[1][1] + inset_pad),
        (body[2][0] - inset_pad, body[2][1] - inset_pad),
        (body[3][0] + inset_pad, body[3][1] - inset_pad),
    ]
    pygame.draw.polygon(big, PURPLE, body_in)
    # Velvet sheen — soft alpha highlight bands
    for off_y, alpha_v in ((s(2), 140), (s(8), 90)):
        sheen = pygame.Surface((body[1][0] - body[0][0], s(10)),
                               pygame.SRCALPHA)
        pygame.draw.ellipse(sheen, (*PURPLE_HI, alpha_v),
                            (0, 0, sheen.get_width(), s(10)))
        big.blit(sheen, (body[0][0], body[0][1] + off_y))

    # ── Multi-layer gold border (outer thick + inner thin) ──────
    # Outer thick gold rim
    for a, b in ((body[0], body[1]),
                 (body[1], body[2]),
                 (body[2], body[3]),
                 (body[3], body[0])):
        pygame.draw.line(big, GOLD_DK, a, b, max(5, s(1) + 3))
    for a, b in ((body[0], body[1]),
                 (body[1], body[2]),
                 (body[2], body[3]),
                 (body[3], body[0])):
        pygame.draw.line(big, GOLD, a, b, max(3, s(1) + 1))
    for a, b in ((body[0], body[1]),
                 (body[1], body[2]),
                 (body[2], body[3]),
                 (body[3], body[0])):
        pygame.draw.line(big, GOLD_HI, a, b, max(1, s(1) // 2))
    # Inner thin gold frame (1 unit inset)
    inset1 = s(5)
    inner1 = [
        (body[0][0] + inset1, body[0][1] + inset1),
        (body[1][0] - inset1, body[1][1] + inset1),
        (body[2][0] - inset1 + s(1), body[2][1] - inset1),
        (body[3][0] + inset1 - s(1), body[3][1] - inset1),
    ]
    pygame.draw.lines(big, GOLD_MID, True, inner1, max(2, s(1)))
    # Decorative dot row along the inner frame (small gold beads)
    for j in range(20):
        t = (j + 0.5) / 20
        # Top edge
        bx = int(inner1[0][0] + (inner1[1][0] - inner1[0][0]) * t)
        by = int(inner1[0][1] + (inner1[1][1] - inner1[0][1]) * t)
        aa_circle(big, GOLD_HI, bx, by, max(1, s(1) // 2))
        # Bottom edge
        bx = int(inner1[3][0] + (inner1[2][0] - inner1[3][0]) * t)
        by = int(inner1[3][1] + (inner1[2][1] - inner1[3][1]) * t)
        aa_circle(big, GOLD_HI, bx, by, max(1, s(1) // 2))

    # ── Symmetric motif rows: stars + crescents in pattern ──────
    # Top row of small stars
    for fx in (-s(60), -s(36), s(36), s(60)):
        sx_p = cx + fx
        sy_p = cy_top + s(10)
        r = s(2)
        for dx_p, dy_p in ((r * 2, 0), (-r * 2, 0), (0, r * 2), (0, -r * 2)):
            pygame.draw.line(big, GOLD,
                             (sx_p, sy_p), (sx_p + dx_p, sy_p + dy_p),
                             max(1, s(1)))
        aa_circle(big, WHITE, sx_p, sy_p, max(1, s(1) // 2))
    # Mid row of crescent moons flanking the medallion
    for fx in (-s(38), s(38)):
        mx_p = cx + fx
        my_p = cy_top + s(22)
        pygame.draw.circle(big, GOLD, (mx_p, my_p), s(4))
        pygame.draw.circle(big, PURPLE, (mx_p + s(2), my_p), s(4))
        # Star inside crescent's "open" side
        pygame.draw.circle(big, GOLD_HI, (mx_p + s(5), my_p), max(1, s(1)))
    # Bottom row of paired tiny stars
    for fx in (-s(70), -s(46), -s(22), s(22), s(46), s(70)):
        sx_p = cx + fx
        sy_p = cy_top + s(34)
        aa_circle(big, GOLD, sx_p, sy_p, max(1, s(1)))
        aa_circle(big, WHITE, sx_p - s(1), sy_p - s(1),
                  max(1, s(1) // 2))

    # ── Decorative gold curlicue flourishes along the border ───
    # Small swirls at the corners (between border and motifs)
    for corner_index, corner in enumerate(body):
        cx_f, cy_f = corner
        # Pick swirl direction so curl points inward + downward
        sign_x = -1 if corner[0] > cx else 1
        sign_y = -1 if corner[1] > cy_top + s(20) else 1
        # Drawing a small spiral-ish flourish with 2 arcs
        pygame.draw.arc(big, GOLD,
                        (cx_f + sign_x * s(5) - s(4),
                         cy_f + sign_y * s(5) - s(4),
                         s(8), s(8)),
                        math.radians(0), math.radians(270),
                        max(2, s(1)))
        pygame.draw.arc(big, GOLD_HI,
                        (cx_f + sign_x * s(7) - s(3),
                         cy_f + sign_y * s(7) - s(3),
                         s(6), s(6)),
                        math.radians(0), math.radians(270),
                        max(1, s(1) // 2))

    # ── Corner gem inlays (small gold settings with tiny gems) ─
    for corner, gem_col in zip(
            [body[0], body[1], body[2], body[3]],
            [SAPPHIRE, SAPPHIRE, EMERALD, EMERALD]):
        # Move slightly inward from corner
        gx_p = corner[0] + (s(8) if corner[0] < cx else -s(8))
        gy_p = corner[1] + (s(8) if corner[1] < cy_top + s(20) else -s(8))
        pygame.draw.circle(big, GOLD_DK, (gx_p + s(1), gy_p + s(1)), s(4))
        pygame.draw.circle(big, GOLD, (gx_p, gy_p), s(3))
        gem_facet(big, gx_p, gy_p, s(2), gem_col,
                  RUBY_HI if gem_col == EMERALD else (170, 215, 255),
                  (15, 60, 80))

    # ── Detailed pom-pom + tassel at each corner ───────────────
    for corner in body:
        cxc, cyc = corner
        # Multi-layer pom-pom
        aa_circle(big, GOLD_DK, cxc + s(1), cyc + s(2), s(7))
        aa_circle(big, GOLD_LO, cxc,         cyc + s(1), s(6))
        aa_circle(big, GOLD,    cxc,         cyc,         s(5))
        aa_circle(big, GOLD_HI, cxc - s(2),  cyc - s(2),  s(2))
        # Ruby gem set in the pom-pom
        pygame.draw.circle(big, RUBY, (cxc, cyc + s(1)), s(2))
        pygame.draw.circle(big, RUBY_HI, (cxc - s(1), cyc), s(1))
        # Dangling thread bundle below
        for dx in (-s(4), -s(2), 0, s(2), s(4)):
            pygame.draw.line(big, RUBY,
                             (cxc + dx, cyc + s(6)),
                             (cxc + dx - s(1), cyc + s(18)),
                             max(2, s(1)))
        # Gold thread tips at the bottom of each strand
        for dx in (-s(4), -s(2), 0, s(2), s(4)):
            aa_circle(big, GOLD,
                      cxc + dx - s(1), cyc + s(18),
                      max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Design 4 — Cosmic / nebula carpet
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_cosmic(big, cx):
    """Deep blue-purple cosmic carpet with a constellation pattern,
    glowing cyan edges, and tiny stars trailing behind / below.
    Looks like a piece of starry sky."""
    NIGHT    = ( 22,  18,  60)
    NIGHT_HI = ( 60,  45, 130)
    NEBULA_PINK   = (200,  70, 160)
    NEBULA_BLUE   = ( 75, 150, 240)
    NEBULA_PURPLE = (135,  70, 200)
    CYAN     = (160, 230, 255)
    WHITE    = (250, 245, 255)
    GOLD     = (255, 220, 130)

    # Soft glow halo beneath (cyan)
    for r_n, alpha in ((s(130), 60), (s(100), 90), (s(75), 110)):
        glow = pygame.Surface((r_n * 2 + 4, r_n + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*CYAN, alpha),
                            (2, 2, r_n * 2, r_n))
        big.blit(glow, (cx - r_n, s(334)))

    cy_top = s(286)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(138),
                                    half_w_back=s(110),
                                    height=s(42))
    # Dark base
    pygame.draw.polygon(big, (5, 5, 25),
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, NIGHT, body)

    # Nebula clouds inside
    random.seed(17)
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    for _ in range(28):
        nx = cx + random.randint(-s(72), s(72))
        ny = cy_top + random.randint(s(4), s(38))
        nr = random.randint(s(8), s(18))
        nc = random.choice([NEBULA_PINK, NEBULA_PURPLE, NEBULA_BLUE])
        srf = pygame.Surface((nr * 2 + 4, nr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(srf, (*nc, 60),
                           (nr + 2, nr + 2), nr)
        mask.blit(srf, (nx - nr - 2, ny - nr - 2))
    # Clip the mask roughly to the carpet polygon by re-drawing
    # the carpet outline OVER the mask afterwards. Simpler: just
    # blit then re-stroke edges.
    big.blit(mask, (0, 0))

    # Star dots scattered across the carpet
    random.seed(23)
    for _ in range(36):
        sx = cx + random.randint(-s(78), s(78))
        sy = cy_top + random.randint(s(4), s(38))
        sr = random.randint(1, max(1, s(1)))
        pygame.draw.circle(big, WHITE, (sx, sy), sr)
    # A few bigger sparkle stars
    for _ in range(6):
        sx = cx + random.randint(-s(70), s(70))
        sy = cy_top + random.randint(s(6), s(36))
        r = s(2)
        pygame.draw.line(big, CYAN, (sx - r * 2, sy),
                         (sx + r * 2, sy), max(1, s(1)))
        pygame.draw.line(big, CYAN, (sx, sy - r * 2),
                         (sx, sy + r * 2), max(1, s(1)))
        aa_circle(big, WHITE, sx, sy, max(1, s(1) // 2))

    # Glowing cyan edge stroke
    pygame.draw.lines(big, CYAN, True, body, max(2, s(1)))
    pygame.draw.lines(big, WHITE, True, body, max(1, s(1) // 2))

    # 4 corner sparkle stars (instead of tassels)
    for corner in body:
        r = s(3)
        cxc, cyc = corner[0], corner[1] + s(2)
        pygame.draw.line(big, GOLD, (cxc - r * 2, cyc),
                         (cxc + r * 2, cyc), max(2, s(1)))
        pygame.draw.line(big, GOLD, (cxc, cyc - r * 2),
                         (cxc, cyc + r * 2), max(2, s(1)))
        aa_circle(big, WHITE, cxc, cyc, max(1, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Design 5 — Tribal / desert carpet (Bedouin style)
# ─────────────────────────────────────────────────────────────────────────────

def draw_carpet_tribal(big, cx):
    """Warm earth-tone carpet with chevron + diamond tribal pattern,
    leather-look tassels. Rugged / practical look."""
    OCHRE    = (185, 110,  55)
    OCHRE_HI = (220, 155,  85)
    OCHRE_LO = (125,  65,  25)
    BROWN    = ( 95,  55,  30)
    DEEP     = ( 50,  25,  10)
    CREAM    = (235, 215, 175)
    TEAL     = ( 65, 130, 130)
    RUST     = (180,  75,  45)

    _shadow_oval(big, cx, s(338), s(210), s(22), alpha=120)

    cy_top = s(288)
    body = _carpet_perspective_quad(cx, cy_top,
                                    half_w_front=s(135),
                                    half_w_back=s(108),
                                    height=s(40))
    pygame.draw.polygon(big, OCHRE_LO,
                        [(x + s(2), y + s(2)) for x, y in body])
    pygame.draw.polygon(big, OCHRE, body)

    # Chevron pattern across the centre
    chevron_y_top = cy_top + s(6)
    chevron_y_bot = cy_top + s(28)
    n_chevrons = 5
    for i in range(n_chevrons):
        t = (i + 0.5) / n_chevrons
        x_left = body[0][0] + (body[1][0] - body[0][0]) * t - s(8)
        x_right = body[0][0] + (body[1][0] - body[0][0]) * t + s(8)
        x_mid = (x_left + x_right) // 2
        color = RUST if i % 2 == 0 else TEAL
        # V chevron
        pygame.draw.lines(big, color, False,
                          [(int(x_left), chevron_y_top),
                           (int(x_mid), chevron_y_bot),
                           (int(x_right), chevron_y_top)],
                          max(2, s(1)))

    # Diamond pattern between chevrons (small accent)
    for i in range(n_chevrons - 1):
        t = (i + 1) / n_chevrons
        x = body[0][0] + (body[1][0] - body[0][0]) * t
        y = (chevron_y_top + chevron_y_bot) // 2
        pygame.draw.polygon(big, CREAM,
                            [(int(x), int(y - s(3))),
                             (int(x + s(3)), int(y)),
                             (int(x), int(y + s(3))),
                             (int(x - s(3)), int(y))])

    # Cream border lines along top + bottom
    pygame.draw.line(big, CREAM,
                     (body[0][0] + s(4), body[0][1] + s(3)),
                     (body[1][0] - s(4), body[1][1] + s(3)),
                     max(2, s(1)))
    pygame.draw.line(big, CREAM,
                     (body[3][0] + s(4), body[3][1] - s(3)),
                     (body[2][0] - s(4), body[2][1] - s(3)),
                     max(2, s(1)))

    # Leather-tipped tassels at corners
    for corner in body:
        pygame.draw.rect(big, BROWN,
                         (corner[0] - s(2), corner[1] + s(2),
                          s(4), s(4)))
        for dx in (-s(2), 0, s(2)):
            pygame.draw.line(big, OCHRE_LO,
                             (corner[0] + dx, corner[1] + s(6)),
                             (corner[0] + dx - s(1), corner[1] + s(14)),
                             max(2, s(1)))


# ─────────────────────────────────────────────────────────────────────────────
# Composer + sheet
# ─────────────────────────────────────────────────────────────────────────────

