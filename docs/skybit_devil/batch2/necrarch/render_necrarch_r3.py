"""
Necrarch — the crowned floating lich sorcerer  [SOLE VIOLET]  · ROUND 3 (FINAL)

Round-3 renderer (headless). Folds in the AD round-2 critique whose entire
SHIP-READY gate was: at the real 32px DAY/NIGHT chips the crown melted into a
bronze nub and the orb out-shouted the skull, so the small read drifted toward
batch-1's faceless Hollow hood.

WHY each change was made (round-2 -> round-3):
  · CROWN spikes are now BONE-parchment (not bronze) on a THIN bronze base-band,
    and are tall + narrow-based with clear sky-gaps between them, so they break
    the head's alpha outline by ~3-4px as THREE distinct notches at 32px instead
    of filling into one bronze blob. The crown is the #1 Hollow separator.
  · SKULL value lifted above the orb: the bone face is pushed brighter (toward
    sheen), the gaunt cheek-shade mass is shrunk so it can't darken the face at
    small scale, and the orb bloom is pulled in another notch + its core
    desaturated so "skull mage" reads before "glowing chest dot." The skull is
    the hero and must win the first glance on both chips.
  · CUFFS given more mass + a continuous 1px bronze rim so the two cradle-
    brackets survive as shapes flanking the orb at 32px — the orb reads HELD,
    not free-floating.
  · Eye-sockets kept as teardrop hollows with a CONTAINED violet inner glow and
    a plum rim (bone first, glow second) — no white halo blow-out.
  · NIGHT contrast leans on the 1px alpha-grown ink outline + the high-value
    bone skull/spikes as the bright top anchor; deep-plum robe edge is held by
    the outline so the lower-right silhouette does not vanish on dark-blue sky.
  · Crozier finial prongs get an inward tip-curl + an upper-left sheen for the
    AAA-casual lift; cap-orb glow falloff matches the now-smaller creature orb so
    prop and creature read as the same magic.

House grammar verbatim: chibi proportions, FLAT saturated fills + hard ink
keylines, dark-core -> flat-fill -> top-left rim-sheen TRIAD, silhouette POP via
a 1px alpha-grown outline, supersample -> smoothscale. PINNED PALETTE hexes used
exactly (SOLE violet in the roster).
"""
import os

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
# round-3: brighter bone for the FACE so the skull out-values the orb at 32px
BONE_HI    = (242, 232, 210)
ORB_CORE   = (224, 198, 250)
ORB_DEEP   = (120,  70, 196)
SOCKET     = ( 34,  18,  52)   # plum socket-rim darkness (bone reads first)

SS = 4   # supersample factor


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def grow_outline(src, color=INK, grow=1):
    """1px (post-downscale) ink keyline grown from the alpha mask — the house
    silhouette-POP, and the round-3 anchor that holds the deep-plum robe edge
    against a dark-blue night sky. Grown at supersample scale so smoothscale
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
#  Vertical stack with NO gaps: bone crown spikes -> skull -> bone shoulders ->
#  robe from the shoulders -> cuffs cradling a small chest-orb -> single
#  trailing wisp. Origin frame ~150w x 224h creature-units, scaled by SS.
# ─────────────────────────────────────────────────────────────────────────────

def build_necrarch(target_h=200):
    U = SS
    W, H = 150 * U, 224 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    # ---- ROBE (drawn first, behind the skull/shoulders) ------------------
    # Robe rises to MEET the skull's jawline at the shoulders so the figure is
    # one continuous mass; it widens at the body then collapses to a single
    # asymmetric wisp-curl trailing off to the lower-right ("floats, no feet").
    robe = P([
        (-16, 60),
        (-30, 86), (-38, 120), (-34, 150),
        (-40, 178), (-26, 190),
        (-14, 196), (-2, 198),
        (4, 196),
        (18, 200), (34, 190),
        (46, 196), (40, 206), (26, 204),
        (30, 192), (22, 184),
        (28, 150), (34, 120), (24, 86),
        (16, 60),
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
    # Narrow clavicle bone bridging skull -> robe so there is no empty sky
    # between head and body — keeps the figure one mass at 32px.
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
    # Round-3: chunkier cuffs with a CONTINUOUS bronze rim so the two cradle-
    # brackets survive as flanking shapes at 32px — orb reads HELD, not loose.
    orb_cx, orb_cy = cx, int(98 * U)
    orb_r = int(7 * U)   # pulled in another notch so the skull out-masses it

    for sx in (-1, 1):
        cuff = P([
            (sx * 28, 82), (sx * 37, 94), (sx * 34, 114),
            (sx * 20, 122), (sx * 8, 114), (sx * 12, 96), (sx * 18, 84),
        ])
        pygame.draw.polygon(s, PLUM, [(x + 2 * U, y + 2 * U) for (x, y) in cuff])
        pygame.draw.polygon(s, VIOLET, cuff)
        # continuous bronze rim along the cuff's outer edge (reads at 32px)
        rim = P([
            (sx * 28, 82), (sx * 37, 94), (sx * 34, 114), (sx * 20, 122),
            (sx * 24, 114), (sx * 33, 96), (sx * 26, 86),
        ])
        pygame.draw.polygon(s, BRONZE_SH, [(x + U, y + U) for (x, y) in rim])
        pygame.draw.polygon(s, BRONZE, rim)
        pygame.draw.polygon(s, BRONZE_HI, P([
            (sx * 29, 84), (sx * 36, 95), (sx * 34, 100), (sx * 27, 88),
        ]))
        # bony fingertips peeking from the cuff toward the orb
        for fi in range(2):
            fx = sx * (5 + fi * 5)
            pygame.draw.polygon(s, BONE, P([
                (fx, 106), (fx + sx * 4, 106), (fx + sx * 2, 116),
            ]))
            pygame.draw.polygon(s, BONE_SH, P([
                (fx + sx * 2, 112), (fx + sx * 4, 106), (fx + sx * 2, 116),
            ]))

    # ---- THE SOUL-ORB (phylactery heart) — small, contained, dimmed ------
    # Bloom pulled in (smaller radius + lower alpha) and the core desaturated so
    # the orb no longer out-values the skull at 32px.
    glow = radial_glow(orb_r + 4 * U, ORB, alpha_center=112, falloff=3.0)
    s.blit(glow, (orb_cx - glow.get_width() // 2,
                  orb_cy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (orb_cx, orb_cy), orb_r)
    pygame.draw.circle(s, ORB, (orb_cx, orb_cy), int(orb_r * 0.74))
    pygame.draw.circle(s, ORB_CORE, (orb_cx - orb_r // 4, orb_cy - orb_r // 4),
                       int(orb_r * 0.36))

    # ---- HOODED SKULL — tall, narrow, seated on the shoulders ------------
    # Round-3: filled with the brighter BONE_HI so the FACE is the highest-value
    # mass and wins the first glance over the orb on both day + night chips.
    skull = P([
        (-22, 30), (-24, 16), (-16, 5), (0, 1), (16, 5),
        (24, 16), (22, 30), (18, 44), (12, 56), (6, 62),
        (0, 64), (-6, 62), (-12, 56), (-18, 44),
    ])
    skull_shade = [(x + 2 * U, y + 3 * U) for (x, y) in skull]
    pygame.draw.polygon(s, BONE_SH, skull_shade)
    pygame.draw.polygon(s, BONE_HI, skull)
    # top-left cranium rim-sheen
    pygame.draw.polygon(s, SHEEN, P([
        (-22, 28), (-23, 16), (-15, 6), (-3, 3), (-5, 11),
        (-15, 16), (-19, 28),
    ]))
    # gaunt cheek dark-core hollows — shrunk so they can't darken the face mass
    for sx in (-1, 1):
        pygame.draw.polygon(s, BONE_SH, P([
            (sx * 18, 40), (sx * 19, 46), (sx * 13, 52), (sx * 12, 45),
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
        eg = radial_glow(4 * U, ORB, alpha_center=140, falloff=3.0)
        s.blit(eg, (eye_cx - eg.get_width() // 2, eye_cy - eg.get_height() // 2),
               special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(s, ORB, (eye_cx, eye_cy + U), int(2.2 * U))
        pygame.draw.circle(s, ORB_CORE, (eye_cx, eye_cy + U), int(1.0 * U))

    # nasal hollow
    pygame.draw.polygon(s, SOCKET, P([
        (0, 46), (-3, 54), (0, 58), (3, 54),
    ]))
    # grim clenched teeth row
    teeth_y = int(58 * U)
    for ti in range(-3, 4):
        tx = cx + int(ti * 3.6 * U)
        pygame.draw.rect(s, BONE_HI, (tx, teeth_y, int(2.8 * U), int(5 * U)))
        pygame.draw.line(s, BONE_SH, (tx, teeth_y), (tx, teeth_y + 5 * U),
                         max(1, U // 2))

    # ---- SPIKED BONE CROWN — 3 BONE spikes that NOTCH the outline ---------
    # Round-3 gate fix: a THIN bronze base-band, then three TALL narrow-based
    # BONE-parchment spikes with clear sky-gaps between them, so each spike
    # breaks the head's alpha outline as a distinct notch at 32px instead of
    # filling into a single bronze nub. Centre spike tallest.
    crown_base = P([(-25, 13), (25, 13), (23, 6), (-23, 6)])
    pygame.draw.polygon(s, BRONZE_SH, [(x + U, y + U) for (x, y) in crown_base])
    pygame.draw.polygon(s, BRONZE, crown_base)
    pygame.draw.polygon(s, BRONZE_HI, P([
        (-25, 12), (25, 12), (24, 9), (-24, 9),
    ]))
    # narrow-based, tall spikes with GAPS — bone-colored so they out-value the
    # bronze band and notch the sky. Each: (left, top-apex, right) at base y=6.
    spikes = [
        (-23, 6, -19, -30, -13, 6),
        (-5, 6,  0, -48,  5, 6),
        (13, 6, 19, -30, 23, 6),
    ]
    for (lx, ly, tx, ty, rx, ry) in spikes:
        sp = P([(lx, ly), (tx, ty), (rx, ry)])
        pygame.draw.polygon(s, BONE_SH, [(x + U, y + U) for (x, y) in sp])
        pygame.draw.polygon(s, BONE_HI, sp)
        # left-edge sheen sliver on each spike
        pygame.draw.polygon(s, SHEEN, P([
            (lx, ly), (tx, ty), ((lx + tx) // 2, (ly + ty) // 2),
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
#  THE PROP -> PILLAR — crozier SOUL-STAFF (AD: keep; finial polish).
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

    # claw-finial cradling the phylactery-orb — inward tip-curl + upper-left
    # sheen for the AAA-casual lift the AD asked for.
    for sx in (-1, 0, 1):
        if sx == 0:
            claw = P([(-3, 62), (3, 62), (2, 30), (-2, 30)])
        else:
            claw = P([
                (sx * 4, 64), (sx * 13, 56), (sx * 19, 34),
                (sx * 16, 16), (sx * 9, 22),      # deeper inward curl at the tip
                (sx * 12, 30), (sx * 11, 48), (sx * 2, 60),
            ])
        pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + U) for (x, y) in claw])
        pygame.draw.polygon(s, BONE, claw)
        # upper-left prong sheen
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 4, 64), (sx * 13, 56), (sx * 18, 36),
                (sx * 15, 40), (sx * 7, 58),
            ]))

    ocx, ocy, orr = cx, int(40 * U), int(12 * U)
    glow = radial_glow(orr + 7 * U, ORB, alpha_center=132, falloff=3.0)
    s.blit(glow, (ocx - glow.get_width() // 2, ocy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (ocx, ocy), orr)
    pygame.draw.circle(s, ORB, (ocx, ocy), int(orr * 0.74))
    pygame.draw.circle(s, ORB_CORE, (ocx - orr // 4, ocy - orr // 4), int(orr * 0.36))

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


def build_pillar(target_h=210):
    """Mirror the staff into a repeatable PILLAR: bone shaft repeats as the
    body; claw-finial + caged orb is the detachable gap-edge cap pointing down
    into the gap (Big Reapy bone-bident grammar). Cap-orb glow falloff matches
    the now-smaller creature orb so prop and creature read as one magic."""
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
                (sx * 16, 214), (sx * 9, 208),
                (sx * 12, 200), (sx * 11, 182), (sx * 2, 170),
            ])
        pygame.draw.polygon(s, BONE_SH, [(x + 2 * U, y + U) for (x, y) in claw])
        pygame.draw.polygon(s, BONE, claw)
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 4, 166), (sx * 13, 174), (sx * 18, 194),
                (sx * 15, 190), (sx * 7, 172),
            ]))

    ocx, ocy, orr = cx, int(190 * U), int(12 * U)
    glow = radial_glow(orr + 7 * U, ORB, alpha_center=140, falloff=3.0)
    s.blit(glow, (ocx - glow.get_width() // 2, ocy - glow.get_height() // 2),
           special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(s, ORB_DEEP, (ocx, ocy), orr)
    pygame.draw.circle(s, ORB, (ocx, ocy), int(orr * 0.74))
    pygame.draw.circle(s, ORB_CORE, (ocx - orr // 4, ocy - orr // 4), int(orr * 0.36))

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

    label("NECRARCH — crowned floating lich sorcerer  [SOLE VIOLET]  · ROUND 3 (FINAL)",
          16, 12, font)
    label("R3: 3 BONE crown spikes notch the 32px outline (gaps + thin bronze band) · skull value lifted ABOVE the orb · cuffs rimmed to read HELD · orb bloom dimmed",
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
    day_rect = pygame.Rect(zx - 4, sy - 4, zoom.get_width() + 8, zoom.get_height() + 8)
    pygame.draw.rect(sheet, (150, 196, 226), day_rect)
    sheet.blit(zoom, (zx, sy))
    nx = zx + zoom.get_width() + 18
    night_rect = pygame.Rect(nx - 4, sy - 4, zoom.get_width() + 8, zoom.get_height() + 8)
    pygame.draw.rect(sheet, (26, 28, 54), night_rect)
    sheet.blit(zoom, (nx, sy))
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

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
