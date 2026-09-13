"""
Necrarch — the crowned floating lich sorcerer  [SOLE VIOLET]  · ROUND 2

Round-2 renderer (headless). Resolves the AD round-1 critique whose gate
issue was that the 32px read collapsed to "a glowing orb in a purple
poncho": the skull, crown, cuffs and wisp all evaporated and the orb ate
the character.

The round-2 rebuild is structural, not cosmetic — WHY it changed:
  · ONE continuous tall silhouette. The skull seats DIRECTLY on narrowing
    bone shoulders (no sky gap between head and body); the robe falls from
    those shoulders so head+body read as a single figure, killing the
    two-object collapse that caused the 32px failure.
  · Orb shrunk to ~40% diameter and pulled to the CHEST as a held accent,
    with tight glow falloff so it no longer out-masses the skull.
  · Crown rebuilt as 3 bold triangular bone spikes that NOTCH the head
    outline by several px even at 32px, so the spiked-crown tell survives.
  · Robe hem tapers to a SINGLE asymmetric trailing wisp-curl (no
    bilateral leg-lobes) so "floats, no feet" reads instead of "standing".
  · Eye-sockets are rounded teardrop hollows with a CONTAINED violet inner
    glow + darker plum rim (bone reads first, glow second) — not square
    "visor" tiles, and the white halo is dialled back.
  · Cuffs are two chunky bronze-trimmed shapes flanking the orb so the
    "hands cradling a heart" gesture reads small and the orb reads HELD.

House grammar verbatim: chibi proportions, FLAT saturated fills + hard
ink keylines, dark-core -> flat-fill -> top-left rim-sheen TRIAD,
silhouette POP via a 1px alpha-grown outline, supersample -> smoothscale.
PINNED PALETTE hexes used exactly (SOLE violet in the roster).
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (verbatim from the locked brief) ──────────────────────────
BONE       = (224, 212, 186)
BONE_SH    = (162, 140, 104)
VIOLET     = ( 98,  58, 140)
PLUM       = ( 60,  34,  92)
ORB        = (178, 122, 236)
BRONZE     = (186, 138,  70)
INK        = ( 28,  22,  30)
SHEEN      = (244, 236, 216)

# derived working tones (kept inside the pinned families)
BRONZE_SH  = (128,  92,  44)
BRONZE_HI  = (224, 184,  96)
ORB_CORE   = (232, 206, 255)
ORB_DEEP   = (120,  70, 196)
SOCKET     = ( 34,  18,  52)   # plum socket-rim darkness (bone reads first)

SS = 4   # supersample factor


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def grow_outline(src, color=INK, grow=1):
    """1px (post-downscale) ink keyline grown from the alpha mask — the
    house silhouette-POP. Grown at supersample scale so the smoothscale
    carries it down to ~1px."""
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
#  THE CREATURE — ONE continuous tall figure, built large then outlined.
#  Vertical stack with NO gaps: crown spikes -> skull -> bone shoulders ->
#  robe from the shoulders -> cuffs cradling a small chest-orb -> single
#  trailing wisp. Origin frame ~150w x 220h creature-units, scaled by SS.
# ─────────────────────────────────────────────────────────────────────────────

def build_necrarch(target_h=200):
    U = SS
    W, H = 150 * U, 224 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    # ---- ROBE (drawn first, behind the skull/shoulders) ------------------
    # Robe rises to MEET the skull's jawline at the shoulders (y~62) so the
    # figure is one continuous mass; it widens at the body then collapses to
    # a single asymmetric wisp-curl trailing off to the lower-right.
    robe = P([
        (-16, 60),                       # left shoulder meets skull jaw
        (-30, 86), (-38, 120), (-34, 150),
        (-40, 178), (-26, 190),          # left hem
        (-14, 196), (-2, 198),           # hem valley
        (4, 196),
        (18, 200), (34, 190),            # right hem -> begins the wisp
        (46, 196), (40, 206), (26, 204), # SINGLE trailing wisp-curl (S-tip)
        (30, 192), (22, 184),
        (28, 150), (34, 120), (24, 86),
        (16, 60),                        # right shoulder meets skull jaw
    ])
    robe_shade = [(x + 3 * U, y + 3 * U) for (x, y) in robe]
    pygame.draw.polygon(s, PLUM, robe_shade)
    pygame.draw.polygon(s, VIOLET, robe)
    # dark-core valley + flat triad panel down the robe centre
    pygame.draw.polygon(s, PLUM, P([
        (-9, 92), (-15, 140), (-7, 184), (0, 190),
        (7, 184), (15, 140), (9, 92),
    ]))
    # top-left rim-sheen sliver on the robe's left edge
    pygame.draw.polygon(s, lerp(VIOLET, SHEEN, 0.30), P([
        (-16, 62), (-28, 88), (-35, 122), (-31, 150),
        (-27, 150), (-31, 122), (-24, 90), (-12, 66),
    ]))

    # ---- BONE SHOULDERS (the join) ---------------------------------------
    # Narrow clavicle/shoulder bone bridging skull -> robe so there is no
    # empty sky between head and body — the root fix for the 32px collapse.
    shoulders = P([
        (-22, 60), (-12, 56), (0, 58), (12, 56), (22, 60),
        (16, 70), (0, 72), (-16, 70),
    ])
    pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + 2 * U) for (x, y) in shoulders])
    pygame.draw.polygon(s, BONE, shoulders)
    pygame.draw.polygon(s, SHEEN, P([
        (-22, 60), (-12, 56), (-6, 58), (-14, 62), (-19, 66),
    ]))

    # ---- SLEEVE-CUFFS cradling a small chest-orb -------------------------
    # Two chunky bronze-trimmed cuffs sweep UP-and-IN under the chest to
    # cradle the orb so it reads HELD (and small) even at 32px.
    orb_cx, orb_cy = cx, int(96 * U)
    orb_r = int(8 * U)   # ~40% of the round-1 20-unit orb

    for sx in (-1, 1):
        cuff = P([
            (sx * 26, 84), (sx * 34, 96), (sx * 30, 112),
            (sx * 18, 118), (sx * 9, 110), (sx * 13, 96), (sx * 17, 86),
        ])
        pygame.draw.polygon(s, PLUM, [(x + 2 * U, y + 2 * U) for (x, y) in cuff])
        pygame.draw.polygon(s, VIOLET, cuff)
        # bronze cuff-band trim (chunky, reads at 32px)
        band = P([
            (sx * 27, 86), (sx * 35, 97), (sx * 31, 105), (sx * 22, 94),
        ])
        pygame.draw.polygon(s, BRONZE_SH, [(x + U, y + U) for (x, y) in band])
        pygame.draw.polygon(s, BRONZE, band)
        pygame.draw.polygon(s, BRONZE_HI, P([
            (sx * 28, 87), (sx * 34, 96), (sx * 32, 100), (sx * 26, 91),
        ]))
        # bony fingertips peeking from the cuff toward the orb
        for fi in range(2):
            fx = sx * (5 + fi * 5)
            pygame.draw.polygon(s, BONE, P([
                (fx, 104), (fx + sx * 4, 104), (fx + sx * 2, 114),
            ]))
            pygame.draw.polygon(s, BONE_SH, P([
                (fx + sx * 2, 110), (fx + sx * 4, 104), (fx + sx * 2, 114),
            ]))

    # ---- THE SOUL-ORB (phylactery heart) — small, contained --------------
    glow = radial_glow(orb_r + 6 * U, ORB, alpha_center=140, falloff=2.6)
    s.blit(glow, (orb_cx - glow.get_width() // 2,
                  orb_cy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (orb_cx, orb_cy), orb_r)
    pygame.draw.circle(s, ORB, (orb_cx, orb_cy), int(orb_r * 0.78))
    pygame.draw.circle(s, ORB_CORE, (orb_cx - orb_r // 4, orb_cy - orb_r // 4),
                       int(orb_r * 0.4))
    pygame.draw.circle(s, SHEEN, (orb_cx - orb_r // 3, orb_cy - orb_r // 3),
                       max(1, int(orb_r * 0.18)))

    # ---- HOODED SKULL — tall, narrow, seated on the shoulders ------------
    skull = P([
        (-22, 30), (-24, 16), (-16, 5), (0, 1), (16, 5),
        (24, 16), (22, 30), (18, 44), (12, 56), (6, 62),
        (0, 64), (-6, 62), (-12, 56), (-18, 44),
    ])
    skull_shade = [(x + 2 * U, y + 3 * U) for (x, y) in skull]
    pygame.draw.polygon(s, BONE_SH, skull_shade)
    pygame.draw.polygon(s, BONE, skull)
    # top-left cranium rim-sheen
    pygame.draw.polygon(s, SHEEN, P([
        (-22, 28), (-23, 16), (-15, 6), (-3, 3), (-5, 11),
        (-15, 16), (-19, 28),
    ]))
    # gaunt cheek dark-core hollows
    for sx in (-1, 1):
        pygame.draw.polygon(s, BONE_SH, P([
            (sx * 18, 38), (sx * 20, 46), (sx * 12, 54), (sx * 10, 44),
        ]))

    # rounded teardrop eye-sockets: plum rim, CONTAINED violet inner glow
    for sx in (-1, 1):
        eye_cx = cx + int(sx * 10 * U)
        eye_cy = int(34 * U)
        socket = [
            (eye_cx - int(sx * 7 * U), eye_cy - 6 * U),
            (eye_cx + int(sx * 5 * U), eye_cy - 5 * U),
            (eye_cx + int(sx * 4 * U), eye_cy + 4 * U),
            (eye_cx, eye_cy + 8 * U),
            (eye_cx - int(sx * 6 * U), eye_cy + 3 * U),
        ]
        pygame.draw.polygon(s, SOCKET, socket)
        # contained inner glow — small radius, no white halo blow-out
        eg = radial_glow(5 * U, ORB, alpha_center=150, falloff=2.8)
        s.blit(eg, (eye_cx - eg.get_width() // 2, eye_cy - eg.get_height() // 2),
               special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(s, ORB, (eye_cx, eye_cy + U), int(2.4 * U))
        pygame.draw.circle(s, ORB_CORE, (eye_cx, eye_cy + U), int(1.1 * U))

    # nasal hollow
    pygame.draw.polygon(s, SOCKET, P([
        (0, 46), (-3, 54), (0, 58), (3, 54),
    ]))
    # grim clenched teeth row
    teeth_y = int(58 * U)
    for ti in range(-3, 4):
        tx = cx + int(ti * 3.6 * U)
        pygame.draw.rect(s, BONE, (tx, teeth_y, int(2.8 * U), int(5 * U)))
        pygame.draw.line(s, BONE_SH, (tx, teeth_y), (tx, teeth_y + 5 * U),
                         max(1, U // 2))

    # ---- SPIKED BONE CROWN — 3 bold spikes that NOTCH the outline --------
    crown_base = P([(-25, 14), (25, 14), (22, 3), (-22, 3)])
    pygame.draw.polygon(s, BRONZE_SH, [(x + 2 * U, y + 2 * U) for (x, y) in crown_base])
    pygame.draw.polygon(s, BRONZE, crown_base)
    pygame.draw.polygon(s, BRONZE_HI, P([
        (-25, 13), (25, 13), (24, 9), (-24, 9),
    ]))
    # three bold triangular bone spikes (center tallest, two flanking) —
    # wide-based and tall so the silhouette is notched even at 32px.
    spikes = [
        (-24, 3, -18, -26, -10, 3),
        (-8, 1, 0, -42, 8, 1),
        (10, 3, 18, -26, 24, 3),
    ]
    for (lx, ly, tx, ty, rx, ry) in spikes:
        sp = P([(lx, ly), (tx, ty), (rx, ry)])
        pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + 2 * U) for (x, y) in sp])
        pygame.draw.polygon(s, BONE, sp)
        pygame.draw.polygon(s, SHEEN, P([
            (lx, ly), (tx, ty), ((lx + tx * 2) // 3, (ly + ty * 2) // 3),
        ]))
    # small violet gem set in the bronze band centre
    gem_cx, gem_cy = cx, int(9 * U)
    pygame.draw.polygon(s, ORB, [
        (gem_cx, gem_cy - 3 * U), (gem_cx + 3 * U, gem_cy),
        (gem_cx, gem_cy + 3 * U), (gem_cx - 3 * U, gem_cy),
    ])
    pygame.draw.circle(s, ORB_CORE, (gem_cx - U, gem_cy - U), max(1, int(1.3 * U)))

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


# ─────────────────────────────────────────────────────────────────────────────
#  THE PROP -> PILLAR — crozier SOUL-STAFF (AD: keep; minor finial polish).
# ─────────────────────────────────────────────────────────────────────────────

def build_staff(target_h=210):
    U = SS
    W, H = 64 * U, 230 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    shaft_w = 9
    shaft = P([(-shaft_w, 60), (shaft_w, 60), (shaft_w, 224), (-shaft_w, 224)])
    pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y) for (x, y) in shaft])
    pygame.draw.polygon(s, BONE, shaft)
    pygame.draw.rect(s, SHEEN, (cx - shaft_w * U, 60 * U, int(2.5 * U), 164 * U))
    for by in range(78, 224, 22):
        pygame.draw.rect(s, BRONZE,
                         (cx - shaft_w * U, by * U, shaft_w * 2 * U, int(5 * U)))
        pygame.draw.rect(s, BRONZE_HI,
                         (cx - shaft_w * U, by * U, shaft_w * 2 * U, int(1.5 * U)))
        pygame.draw.polygon(s, PLUM, P([(-3, by + 1), (3, by + 1), (0, by + 4)]))

    # claw-finial cradling the phylactery-orb — inward curl + sheen polish
    for sx in (-1, 0, 1):
        if sx == 0:
            claw = P([(-3, 62), (3, 62), (2, 30), (-2, 30)])
        else:
            claw = P([
                (sx * 4, 64), (sx * 13, 56), (sx * 19, 34),
                (sx * 17, 18), (sx * 11, 24),     # inward curl at the tip
                (sx * 13, 32), (sx * 11, 48), (sx * 2, 60),
            ])
        pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + U) for (x, y) in claw])
        pygame.draw.polygon(s, BONE, claw)
        # 1px sheen on the upper-left prong
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 4, 64), (sx * 13, 56), (sx * 17, 38),
                (sx * 14, 42), (sx * 7, 58),
            ]))

    ocx, ocy, orr = cx, int(40 * U), int(13 * U)
    glow = radial_glow(orr + 9 * U, ORB, alpha_center=150, falloff=2.6)
    s.blit(glow, (ocx - glow.get_width() // 2, ocy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (ocx, ocy), orr)
    pygame.draw.circle(s, ORB, (ocx, ocy), int(orr * 0.78))
    pygame.draw.circle(s, ORB_CORE, (ocx - orr // 4, ocy - orr // 4), int(orr * 0.4))
    pygame.draw.circle(s, SHEEN, (ocx - orr // 3, ocy - orr // 3), int(orr * 0.16))

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


def build_pillar(target_h=210):
    """Mirror the staff into a repeatable PILLAR: bone shaft repeats as the
    body; claw-finial + caged orb is the detachable gap-edge cap pointing
    down into the gap (Big Reapy bone-bident grammar). Cap orb matches the
    creature/staff glow falloff so prop and creature read as one magic."""
    U = SS
    W, H = 64 * U, 230 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    shaft_w = 9
    shaft = P([(-shaft_w, 0), (shaft_w, 0), (shaft_w, 168), (-shaft_w, 168)])
    pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y) for (x, y) in shaft])
    pygame.draw.polygon(s, BONE, shaft)
    pygame.draw.rect(s, SHEEN, (cx - shaft_w * U, 0, int(2.5 * U), 168 * U))
    for by in range(10, 168, 22):
        pygame.draw.rect(s, BRONZE,
                         (cx - shaft_w * U, by * U, shaft_w * 2 * U, int(5 * U)))
        pygame.draw.rect(s, BRONZE_HI,
                         (cx - shaft_w * U, by * U, shaft_w * 2 * U, int(1.5 * U)))
        pygame.draw.polygon(s, PLUM, P([(-3, by + 1), (3, by + 1), (0, by + 4)]))

    for sx in (-1, 0, 1):
        if sx == 0:
            claw = P([(-3, 168), (3, 168), (2, 200), (-2, 200)])
        else:
            claw = P([
                (sx * 4, 166), (sx * 13, 174), (sx * 19, 196),
                (sx * 17, 212), (sx * 11, 206),
                (sx * 13, 198), (sx * 11, 182), (sx * 2, 170),
            ])
        pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + U) for (x, y) in claw])
        pygame.draw.polygon(s, BONE, claw)
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 4, 166), (sx * 13, 174), (sx * 17, 192),
                (sx * 14, 188), (sx * 7, 172),
            ]))

    ocx, ocy, orr = cx, int(190 * U), int(13 * U)
    glow = radial_glow(orr + 9 * U, ORB, alpha_center=160, falloff=2.6)
    s.blit(glow, (ocx - glow.get_width() // 2, ocy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (ocx, ocy), orr)
    pygame.draw.circle(s, ORB, (ocx, ocy), int(orr * 0.78))
    pygame.draw.circle(s, ORB_CORE, (ocx - orr // 4, ocy - orr // 4), int(orr * 0.4))
    pygame.draw.circle(s, SHEEN, (ocx - orr // 3, ocy - orr // 3), int(orr * 0.16))

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


# ─────────────────────────────────────────────────────────────────────────────
#  SHEET COMPOSITION — creature + pillar at large AND 32px, on day + night.
# ─────────────────────────────────────────────────────────────────────────────

def main():
    SHEET_W, SHEET_H = 820, 600
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    for y in range(SHEET_H):
        t = y / SHEET_H
        sheet.fill(lerp((40, 38, 50), (24, 22, 32), t), (0, y, SHEET_W, 1))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    tiny = pygame.font.SysFont("dejavusans", 11)

    def label(txt, x, y, f=small, col=(236, 230, 242)):
        sheet.blit(f.render(txt, True, (0, 0, 0)), (x + 1, y + 1))
        sheet.blit(f.render(txt, True, col), (x, y))

    label("NECRARCH — crowned floating lich sorcerer  [SOLE VIOLET]  · ROUND 2",
          16, 12, font)
    label("R2: ONE unified figure (skull on shoulders) · orb shrunk ~40% to a held chest accent · 3 bold crown spikes · single robe-wisp · teardrop sockets",
          16, 36, tiny, (188, 168, 214))

    # large creature
    big = build_necrarch(target_h=330)
    bx, by = 36, 70
    sheet.blit(big, (bx, by))
    label("creature (large)", bx + big.get_width() // 2 - 42, by + big.get_height() + 4)

    # 32px creature — 3x zoom + actual swatch, on DAY and NIGHT backings
    small_creat = build_necrarch(target_h=32)
    zoom = pygame.transform.scale(small_creat,
                                  (small_creat.get_width() * 3,
                                   small_creat.get_height() * 3))
    zx = bx + 4
    sy = by + big.get_height() + 28
    # day backing (bright sky) behind the 3x zoom
    day_rect = pygame.Rect(zx - 4, sy - 4, zoom.get_width() + 8, zoom.get_height() + 8)
    pygame.draw.rect(sheet, (150, 196, 226), day_rect)
    sheet.blit(zoom, (zx, sy))
    # night backing + actual-32 swatch on it
    nx = zx + zoom.get_width() + 18
    night_rect = pygame.Rect(nx - 4, sy - 4, zoom.get_width() + 8, zoom.get_height() + 8)
    pygame.draw.rect(sheet, (26, 28, 54), night_rect)
    sheet.blit(zoom, (nx, sy))
    # true 32px reads on both backings
    sheet.blit(small_creat, (zx + 6, sy + zoom.get_height() + 8))
    sheet.blit(small_creat, (nx + 6, sy + zoom.get_height() + 8))
    label("32px  ·  DAY sky          NIGHT sky", zx, sy + zoom.get_height() + 44, tiny)

    # large staff prop + mirrored pillar
    staff = build_staff(target_h=380)
    stx, sty = 330, 64
    sheet.blit(staff, (stx, sty))
    label("crozier soul-staff", stx - 4, sty + staff.get_height() + 2, tiny)

    pill = build_pillar(target_h=380)
    px = 432
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
    zy, zx2 = 70, 600
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
    swx, swy = 600, 360
    for i, (nm, col) in enumerate(swatches):
        ry = swy + i * 22
        pygame.draw.rect(sheet, col, (swx, ry, 26, 18))
        pygame.draw.rect(sheet, (10, 10, 14), (swx, ry, 26, 18), 1)
        label(nm, swx + 32, ry + 3, tiny)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
