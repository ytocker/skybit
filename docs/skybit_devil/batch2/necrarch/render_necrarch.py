"""
Necrarch — the crowned floating lich sorcerer  [SOLE VIOLET]

Review-sheet renderer (headless). Draws the ONE locked concept from
batch2/brainstorm_locked15.md: a tall narrow hooded skull under a spiked
bone crown, legless robe-wisp, sleeve-cuffs cradling a glowing soul-orb,
plus its crozier soul-staff prop mirrored into a repeatable pillar — all
at large + 32px scales on one labelled sheet.

House grammar followed verbatim: chibi proportions, FLAT saturated fills
+ hard ink keylines, form via the dark-core -> flat-fill -> top-left
rim-sheen TRIAD, silhouette POP via a 1px outline grown from the alpha
mask, supersampled then smoothscaled down. PINNED PALETTE hexes are used
exactly so this stays the SOLE violet in the roster.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (verbatim from the locked brief) ──────────────────────────
BONE       = (224, 212, 186)   # bone-parchment base
BONE_SH    = (162, 140, 104)   # umber-bone shade (dark-core)
VIOLET     = ( 98,  58, 140)   # royal-violet robe accent
PLUM       = ( 60,  34,  92)   # deep-plum shade (dark-core for robe)
ORB        = (178, 122, 236)   # arcane-violet orb-glow
BRONZE     = (186, 138,  70)   # bronze crown
INK        = ( 28,  22,  30)   # keyline
SHEEN      = (244, 236, 216)   # top-left rim-sheen

# derived working tones (kept inside the pinned families)
BRONZE_SH  = ( 128,  92,  44)
BRONZE_HI  = ( 224, 184,  96)
ORB_CORE   = ( 232, 206, 255)
ORB_DEEP   = ( 120,  70, 196)
SOCKET     = ( 30,  18,  46)   # sunken violet socket darkness

SS = 4   # supersample factor


def triad(surf, poly, fill, shade, sheen, ink=INK, ink_w=0,
          sheen_poly=None, shade_poly=None):
    """Lay a shape down in the house TRIAD order on `surf`:
    dark-core (shade) underneath, flat saturated fill on top, then a
    top-left rim-sheen sliver. Keylines come later from the alpha mask, so
    `ink_w` is normally left 0 here."""
    # dark-core sits as a thin offset bed toward bottom-right
    if shade_poly is None:
        off = max(2, SS)
        shade_poly = [(x + off, y + off) for (x, y) in poly]
    pygame.draw.polygon(surf, shade, shade_poly)
    pygame.draw.polygon(surf, fill, poly)
    if sheen_poly:
        pygame.draw.polygon(surf, sheen, sheen_poly)
    if ink_w:
        pygame.draw.polygon(surf, ink, poly, ink_w)


def grow_outline(src, color=INK, grow=1):
    """1px (post-downscale) ink keyline grown from the alpha mask, the way
    the house silhouette-POP works. Done at supersample scale then carried
    down by the smoothscale, so we grow by `grow*SS` here."""
    g = grow * SS
    mask = pygame.mask.from_surface(src)
    out_surf = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    w, h = src.get_size()
    canvas = pygame.Surface((w + 2 * g, h + 2 * g), pygame.SRCALPHA)
    for dx in range(-g, g + 1):
        for dy in range(-g, g + 1):
            if dx * dx + dy * dy <= g * g:
                canvas.blit(out_surf, (g + dx, g + dy))
    canvas.blit(src, (g, g))
    return canvas, g


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


# ─────────────────────────────────────────────────────────────────────────────
#  THE CREATURE — built large (supersampled), then outlined + downscaled.
#  Tall, narrow. Origin frame ~ 130w x 200h (creature units), scaled by SS.
# ─────────────────────────────────────────────────────────────────────────────

def build_necrarch(target_h=200):
    """Return a SRCALPHA surface of Necrarch at roughly `target_h` px tall
    (the soul-orb glow extends a little beyond the body)."""
    U = SS                       # work in supersampled units
    W, H = 150 * U, 210 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # convenient unit helpers
    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    # ---- ROBE / WISP (drawn first, behind body) --------------------------
    # Long tapering robe ending in a curling wisp — no feet, floats.
    robe = P([
        (-26, 92), (-34, 120), (-30, 150), (-40, 176),
        (-22, 190), (-30, 206), (-10, 198), (0, 205),
        (10, 198), (30, 206), (22, 190), (40, 176),
        (30, 150), (34, 120), (26, 92),
    ])
    robe_shade = [(x + 3 * U, y + 3 * U) for (x, y) in robe]
    pygame.draw.polygon(s, PLUM, robe_shade)
    pygame.draw.polygon(s, VIOLET, robe)
    # dark-core valley down the robe centre + side panel seams (flat triad panels)
    pygame.draw.polygon(s, PLUM, P([
        (-10, 110), (-16, 150), (-8, 188), (0, 196),
        (8, 188), (16, 150), (10, 110),
    ]))
    # top-left rim-sheen sliver on the robe's left edge
    pygame.draw.polygon(s, lerp(VIOLET, SHEEN, 0.32), P([
        (-26, 94), (-32, 120), (-28, 150), (-37, 175),
        (-30, 178), (-23, 150), (-26, 120), (-20, 96),
    ]))

    # wisp tail flourishes (curling smoke-ends of the hem)
    for sx in (-1, 1):
        tail = P([
            (sx * 38, 178), (sx * 50, 196), (sx * 44, 204),
            (sx * 33, 198), (sx * 30, 190),
        ])
        pygame.draw.polygon(s, lerp(VIOLET, PLUM, 0.5), tail)

    # ---- SLEEVE-CUFFS + soul-orb cradle ----------------------------------
    # Oversized cuffs sweep inward to cradle the orb at the chest.
    for sx in (-1, 1):
        cuff = P([
            (sx * 30, 96), (sx * 40, 108), (sx * 34, 134),
            (sx * 20, 148), (sx * 8, 142), (sx * 12, 120),
            (sx * 18, 100),
        ])
        pygame.draw.polygon(s, PLUM, [(x + 2 * U, y + 2 * U) for (x, y) in cuff])
        pygame.draw.polygon(s, VIOLET, cuff)
        # bronze cuff-band trim
        band = P([
            (sx * 32, 100), (sx * 40, 110), (sx * 37, 120),
            (sx * 26, 112),
        ])
        pygame.draw.polygon(s, BRONZE, band)
        pygame.draw.polygon(s, BRONZE_HI, P([
            (sx * 33, 101), (sx * 39, 109), (sx * 37, 113),
            (sx * 31, 105),
        ]))
        # bony fingertips peeking out of the cuff toward the orb
        for fi in range(3):
            fx = sx * (4 + fi * 6)
            pygame.draw.polygon(s, BONE, P([
                (fx, 138), (fx + sx * 4, 138), (fx + sx * 2, 152),
            ]))
            pygame.draw.polygon(s, BONE_SH, P([
                (fx + sx * 2, 146), (fx + sx * 4, 138), (fx + sx * 2, 152),
            ]))

    # ---- THE SOUL-ORB (phylactery heart) ---------------------------------
    orb_cx, orb_cy = cx, int(132 * U)
    orb_r = int(20 * U)
    # outer arcane glow (blitted additively after, but lay a soft bed here too)
    glow = radial_glow(orb_r + 14 * U, ORB, alpha_center=150, falloff=2.2)
    s.blit(glow, (orb_cx - glow.get_width() // 2,
                  orb_cy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (orb_cx, orb_cy), orb_r)
    pygame.draw.circle(s, ORB, (orb_cx, orb_cy), int(orb_r * 0.82))
    pygame.draw.circle(s, ORB_CORE, (orb_cx - orb_r // 4, orb_cy - orb_r // 4),
                       int(orb_r * 0.42))
    # tiny inner soul-spark
    pygame.draw.circle(s, SHEEN, (orb_cx - orb_r // 3, orb_cy - orb_r // 3),
                       int(orb_r * 0.16))

    # ---- HOODED SKULL ----------------------------------------------------
    # Gaunt, tall, narrow skull. Cranium dome + cheekbones + tapering jaw.
    skull = P([
        (-24, 34), (-26, 18), (-18, 6), (0, 2), (18, 6),
        (26, 18), (24, 34), (20, 50), (14, 64), (8, 74),
        (0, 78), (-8, 74), (-14, 64), (-20, 50),
    ])
    skull_shade = [(x + 2 * U, y + 3 * U) for (x, y) in skull]
    pygame.draw.polygon(s, BONE_SH, skull_shade)
    pygame.draw.polygon(s, BONE, skull)
    # top-left rim-sheen on the cranium
    pygame.draw.polygon(s, SHEEN, P([
        (-24, 32), (-25, 18), (-17, 7), (-4, 4), (-6, 12),
        (-16, 18), (-20, 32),
    ]))
    # cheek dark-core hollows (gaunt)
    for sx in (-1, 1):
        pygame.draw.polygon(s, BONE_SH, P([
            (sx * 20, 44), (sx * 22, 52), (sx * 14, 60), (sx * 12, 50),
        ]))

    # sunken violet socket-glow eyes
    for sx in (-1, 1):
        eye_cx = cx + int(sx * 11 * U)
        eye_cy = int(38 * U)
        pygame.draw.polygon(s, SOCKET, [
            (eye_cx - int(sx * 9 * U), eye_cy - 7 * U),
            (eye_cx + int(sx * 5 * U), eye_cy - 5 * U),
            (eye_cx + int(sx * 3 * U), eye_cy + 9 * U),
            (eye_cx - int(sx * 8 * U), eye_cy + 6 * U),
        ])
        eg = radial_glow(11 * U, ORB, alpha_center=235, falloff=2.4)
        s.blit(eg, (eye_cx - eg.get_width() // 2, eye_cy - eg.get_height() // 2),
               special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(s, ORB_CORE, (eye_cx, eye_cy), int(3.4 * U))

    # nasal hollow
    pygame.draw.polygon(s, SOCKET, P([
        (0, 50), (-4, 60), (0, 66), (4, 60),
    ]))
    # grim clenched teeth row
    teeth_y = int(68 * U)
    for ti in range(-3, 4):
        tx = cx + int(ti * 4 * U)
        pygame.draw.rect(s, BONE, (tx, teeth_y, int(3 * U), int(6 * U)))
        pygame.draw.line(s, BONE_SH, (tx, teeth_y), (tx, teeth_y + 6 * U), max(1, U // 2))

    # ---- SPIKED BONE CROWN -----------------------------------------------
    # Tall multi-spiked bone crown ringing the cranium; bronze band base.
    crown_base = P([
        (-27, 16), (27, 16), (24, 4), (-24, 4),
    ])
    pygame.draw.polygon(s, BRONZE_SH, [(x + 2 * U, y + 2 * U) for (x, y) in crown_base])
    pygame.draw.polygon(s, BRONZE, crown_base)
    pygame.draw.polygon(s, BRONZE_HI, P([
        (-27, 15), (27, 15), (26, 11), (-26, 11),
    ]))
    # five bone spikes; centre tallest, fanning a tree-crown read
    spikes = [
        (-22, 4, -26, -18, -16, 2),
        (-12, 2, -14, -30, -5, 0),
        (0, 0, 0, -42, 0, 0),
        (12, 2, 14, -30, 5, 0),
        (22, 4, 26, -18, 16, 2),
    ]
    for (lx, ly, tx, ty, rx, ry) in spikes:
        sp = P([(lx, ly), (tx, ty), (rx, ry)])
        pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + 2 * U) for (x, y) in sp])
        pygame.draw.polygon(s, BONE, sp)
        # top-left sheen edge of each spike
        pygame.draw.polygon(s, SHEEN, P([
            (lx, ly), (tx, ty), ((lx + tx) // 2, (ly + ty) // 2),
        ]))
    # small violet gem set in the bronze band centre
    gem_cx, gem_cy = cx, int(11 * U)
    pygame.draw.polygon(s, ORB, [
        (gem_cx, gem_cy - 4 * U), (gem_cx + 4 * U, gem_cy),
        (gem_cx, gem_cy + 4 * U), (gem_cx - 4 * U, gem_cy),
    ])
    pygame.draw.circle(s, ORB_CORE, (gem_cx - U, gem_cy - U), int(1.6 * U))

    # ---- ink keyline grown from the alpha mask + downscale ---------------
    outlined, _ = grow_outline(s, INK, grow=1)
    # downscale to the requested height, preserving aspect
    ow, oh = outlined.get_size()
    scale = target_h / oh
    final = pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))
    return final


# ─────────────────────────────────────────────────────────────────────────────
#  THE PROP -> PILLAR — crozier SOUL-STAFF.
#  Ornate bone shaft (knuckle/rune banding) = repeatable body;
#  caged glowing phylactery-orb in a claw-finial = gap-edge cap.
# ─────────────────────────────────────────────────────────────────────────────

def build_staff(target_h=210):
    U = SS
    W, H = 64 * U, 230 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    # ---- bone shaft body (repeatable) -----------------------------------
    shaft_w = 9
    shaft = P([
        (-shaft_w, 60), (shaft_w, 60), (shaft_w, 224), (-shaft_w, 224),
    ])
    pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y) for (x, y) in shaft])
    pygame.draw.polygon(s, BONE, shaft)
    # top-left sheen column
    pygame.draw.rect(s, SHEEN,
                     (cx - shaft_w * U, 60 * U, int(2.5 * U), 164 * U))
    # knuckle/rune banding (the repeatable banding for the pillar body)
    for by in range(78, 224, 22):
        # bronze rune band
        pygame.draw.rect(s, BRONZE,
                         (cx - shaft_w * U, by * U, shaft_w * 2 * U, int(5 * U)))
        pygame.draw.rect(s, BRONZE_HI,
                         (cx - shaft_w * U, by * U, shaft_w * 2 * U, int(1.5 * U)))
        # carved violet rune notch
        pygame.draw.polygon(s, PLUM, P([
            (-3, by + 1), (3, by + 1), (0, by + 4),
        ]))

    # ---- claw-finial cradling the phylactery-orb (gap-edge cap) ----------
    # three bone claws curl up around the orb
    for sx in (-1, 0, 1):
        if sx == 0:
            claw = P([(-3, 62), (3, 62), (2, 30), (-2, 30)])
        else:
            claw = P([
                (sx * 4, 64), (sx * 13, 56), (sx * 19, 34),
                (sx * 16, 20), (sx * 12, 30), (sx * 11, 48), (sx * 2, 60),
            ])
        pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + U) for (x, y) in claw])
        pygame.draw.polygon(s, BONE, claw)
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 4, 64), (sx * 13, 56), (sx * 16, 40),
                (sx * 13, 44), (sx * 7, 58),
            ]))

    # caged phylactery-orb glowing at the gap
    ocx, ocy, orr = cx, int(40 * U), int(13 * U)
    glow = radial_glow(orr + 12 * U, ORB, alpha_center=170, falloff=2.1)
    s.blit(glow, (ocx - glow.get_width() // 2, ocy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (ocx, ocy), orr)
    pygame.draw.circle(s, ORB, (ocx, ocy), int(orr * 0.8))
    pygame.draw.circle(s, ORB_CORE, (ocx - orr // 4, ocy - orr // 4),
                       int(orr * 0.4))
    pygame.draw.circle(s, SHEEN, (ocx - orr // 3, ocy - orr // 3), int(orr * 0.16))

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


def build_pillar(target_h=210):
    """Mirror the staff prop into a clean repeatable PILLAR: the bone shaft
    repeats as the body, the claw-finial + caged orb is the detachable
    gap-edge cap radiating at the gap. Shown as a top cap so the gap is at
    the bottom (the way Big Reapy's bone-bident mirrors)."""
    U = SS
    W, H = 64 * U, 230 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    shaft_w = 9
    # repeatable shaft body filling from the top
    shaft = P([(-shaft_w, 0), (shaft_w, 0), (shaft_w, 168), (-shaft_w, 168)])
    pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y) for (x, y) in shaft])
    pygame.draw.polygon(s, BONE, shaft)
    pygame.draw.rect(s, SHEEN, (cx - shaft_w * U, 0, int(2.5 * U), 168 * U))
    for by in range(10, 168, 22):
        pygame.draw.rect(s, BRONZE,
                         (cx - shaft_w * U, by * U, shaft_w * 2 * U, int(5 * U)))
        pygame.draw.rect(s, BRONZE_HI,
                         (cx - shaft_w * U, by * U, shaft_w * 2 * U, int(1.5 * U)))
        pygame.draw.polygon(s, PLUM, P([
            (-3, by + 1), (3, by + 1), (0, by + 4),
        ]))

    # detachable gap-edge cap at the BOTTOM: claw-finial + caged orb pointing
    # down into the gap (mirror of the staff finial)
    for sx in (-1, 0, 1):
        if sx == 0:
            claw = P([(-3, 168), (3, 168), (2, 200), (-2, 200)])
        else:
            claw = P([
                (sx * 4, 166), (sx * 13, 174), (sx * 19, 196),
                (sx * 16, 210), (sx * 12, 200), (sx * 11, 182), (sx * 2, 170),
            ])
        pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + U) for (x, y) in claw])
        pygame.draw.polygon(s, BONE, claw)
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 4, 166), (sx * 13, 174), (sx * 16, 190),
                (sx * 13, 186), (sx * 7, 172),
            ]))

    ocx, ocy, orr = cx, int(190 * U), int(13 * U)
    glow = radial_glow(orr + 14 * U, ORB, alpha_center=185, falloff=2.0)
    s.blit(glow, (ocx - glow.get_width() // 2, ocy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (ocx, ocy), orr)
    pygame.draw.circle(s, ORB, (ocx, ocy), int(orr * 0.8))
    pygame.draw.circle(s, ORB_CORE, (ocx - orr // 4, ocy - orr // 4), int(orr * 0.4))
    pygame.draw.circle(s, SHEEN, (ocx - orr // 3, ocy - orr // 3), int(orr * 0.16))

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


# ── small colour helper (module-local to avoid game imports at headless) ─────
def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ─────────────────────────────────────────────────────────────────────────────
#  SHEET COMPOSITION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    SHEET_W, SHEET_H = 760, 560
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    # neutral-cool review backdrop so the violet + bone read honestly
    for y in range(SHEET_H):
        t = y / SHEET_H
        sheet.fill(lerp((40, 38, 50), (24, 22, 32), t), (0, y, SHEET_W, 1))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    tiny = pygame.font.SysFont("dejavusans", 11)

    def label(txt, x, y, f=small, col=(236, 230, 242)):
        sheet.blit(f.render(txt, True, (0, 0, 0)), (x + 1, y + 1))
        sheet.blit(f.render(txt, True, col), (x, y))

    label("NECRARCH — crowned floating lich sorcerer  [SOLE VIOLET]", 16, 12, font)
    label("royal-violet + bronze  ·  tall narrow hooded skull · spiked bone crown · legless robe-wisp · sleeve-cuffs cradling a soul-orb",
          16, 36, tiny, (188, 168, 214))

    # large creature
    big = build_necrarch(target_h=320)
    bx = 40
    by = 70
    sheet.blit(big, (bx, by))
    label("creature (large)", bx + big.get_width() // 2 - 42, by + big.get_height() + 4)

    # 32px creature (scaled from supersample for a clean min-read)
    small_creat = build_necrarch(target_h=32)
    sx = bx + big.get_width() // 2 - small_creat.get_width() // 2
    sy = by + big.get_height() + 26
    # 3x nearest-neighbor zoom + true 32px swatch side by side
    zoom = pygame.transform.scale(small_creat,
                                  (small_creat.get_width() * 3,
                                   small_creat.get_height() * 3))
    zx = bx + 8
    sheet.blit(zoom, (zx, sy))
    sheet.blit(small_creat, (zx + zoom.get_width() + 16, sy + zoom.get_height() - 32))
    label("32px read (3x + actual)", zx, sy + zoom.get_height() + 4, tiny)

    # large staff prop
    staff = build_staff(target_h=360)
    stx = 330
    sty = 64
    sheet.blit(staff, (stx, sty))
    label("crozier soul-staff (prop)", stx - 6, sty + staff.get_height() + 2, tiny)

    # mirrored pillar
    pill = build_pillar(target_h=360)
    px = 440
    sheet.blit(pill, (px, sty))
    label("-> PILLAR mirror", px - 2, sty + pill.get_height() + 2, tiny)
    label("(repeatable shaft +", px - 2, sty + pill.get_height() + 16, tiny,
          (170, 152, 196))
    label(" caged-orb gap cap)", px - 2, sty + pill.get_height() + 28, tiny,
          (170, 152, 196))

    # 32px staff + pillar reads
    staff32 = build_staff(target_h=32)
    pill32 = build_pillar(target_h=32)
    z2 = pygame.transform.scale(staff32,
                                (staff32.get_width() * 3, staff32.get_height() * 3))
    z3 = pygame.transform.scale(pill32,
                                (pill32.get_width() * 3, pill32.get_height() * 3))
    zy = 70
    zx2 = 560
    sheet.blit(z2, (zx2, zy))
    sheet.blit(z3, (zx2 + z2.get_width() + 24, zy))
    sheet.blit(staff32, (zx2 + 6, zy + z2.get_height() + 8))
    sheet.blit(pill32, (zx2 + z2.get_width() + 30, zy + z2.get_height() + 8))
    label("32px staff / pillar", zx2, zy + z2.get_height() + 34, tiny)

    # palette swatch strip
    swatches = [
        ("bone", BONE), ("bone-sh", BONE_SH), ("violet", VIOLET),
        ("plum", PLUM), ("orb-glow", ORB), ("bronze", BRONZE),
        ("ink", INK), ("sheen", SHEEN),
    ]
    swx, swy = 560, 360
    for i, (nm, col) in enumerate(swatches):
        ry = swy + i * 22
        pygame.draw.rect(sheet, col, (swx, ry, 26, 18))
        pygame.draw.rect(sheet, (10, 10, 14), (swx, ry, 26, 18), 1)
        label(nm, swx + 32, ry + 3, tiny)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
