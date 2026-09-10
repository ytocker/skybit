"""
Review renderer for KAPPA — the turtle-shelled water-dish imp
(Section 3 Japanese, GREEN-BAND #3 BRIGHT YELLOW-GREEN).

House style: chibi, flat saturated fills, hard ink keylines, the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, a 1px outline grown from
the alpha mask, and supersample -> smoothscale. The creature is drawn once at
a high supersample factor onto a transparent surface, outlined from its own
alpha mask, then downscaled for the crisp large + 32px review tiles.

Standalone headless script: writes round_N.png next to itself. No game imports
so the review sheet stays reproducible in isolation. (writes round_2.png)
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame

# ── PINNED PALETTE (exact hexes from the locked Kappa brief) ────────────────
# The body MUST be the brightest, yellowest, warmest of the three greens — it
# is the green-band gate, so the fill is held to the pin verbatim and the
# shade/sheen are kept warm+yellow-leaning so the whole mass stays in lane.
BODY      = (120, 194, 72)    # BRIGHT YELLOW-GREEN — most saturated, yellowest
BODY_D    = (72, 138, 56)     # deep-green shade (dark core)
SHEEN     = (188, 232, 132)   # top-left rim sheen (warm/yellow-leaning)
SHELL     = (150, 108, 52)    # turtle-bronze shell
SHELL_D   = (98, 68, 32)      # shell dark core (derived, same family)
SHELL_RIM = (200, 152, 88)    # shell sheen (derived)
DISH      = (120, 206, 200)   # dish-water turquoise
DISH_D    = (66, 148, 146)    # dish water dark
DISH_RIM  = (192, 240, 236)   # dish ripple highlight
BEAK      = (228, 188, 72)    # beak-gold
BEAK_D    = (172, 136, 42)
BEAK_RIM  = (248, 222, 140)
BAMBOO    = (196, 178, 110)   # bamboo-tan
BAMBOO_D  = (150, 132, 70)
BAMBOO_RIM= (224, 210, 156)
INK       = (24, 34, 24)      # keyline ink
WHITE     = (244, 248, 242)
# pale plastron belly so the bronze shell has a value partner and the
# yellow-green body reads via internal contrast against green skies
PLASTRON  = (224, 232, 168)
PLASTRON_D= (176, 196, 120)
CUKE      = (96, 168, 70)     # cucumber (a touch darker/greener than body)
CUKE_D    = (58, 120, 46)
CUKE_RIM  = (164, 212, 122)

SS = 4   # supersample factor for the large render


def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def _ellipse(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color, (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def grow_outline(src, ink, px):
    """1px (scaled) ink keyline grown from the sprite's own alpha mask, so the
    silhouette POPs against any biome. We dilate by stamping the alpha mask in
    a ring of offsets behind the art."""
    mask = pygame.mask.from_surface(src)
    out = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    stamp = mask.to_surface(setcolor=(*ink, 255), unsetcolor=(0, 0, 0, 0))
    r = px
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out.blit(stamp, (dx, dy))
    out.blit(src, (0, 0))
    return out


def _hex(surf, color, cx, cy, r, squash=0.86):
    """A pointy-top hex plate (slightly squashed) for the shell facets."""
    pts = [(cx + r * math.sin(math.radians(a)),
            cy - r * squash * math.cos(math.radians(a)))
           for a in range(0, 360, 60)]
    _poly(surf, color, pts)


def draw_kappa(surf, ox, oy, s):
    """Draw the squat froggy kappa centred near (ox, oy). `s` is unit scale.
    Bottom-heavy: a domed turtle-shell HUMP rising off the back so the
    silhouette itself bulges, a dish-crowned beaked head, webbed limbs."""

    def P(x, y):  # local unit coords -> surface px
        return (ox + x * s, oy + y * s)

    # ---- back foot (drawn first, furthest back) ----
    def web_lobe(cx, cy, rx, ry, ang, splay=True):
        base = [(-rx, -ry * 0.2), (rx, -ry * 0.2), (rx * 0.7, ry),
                (0, ry * 1.3), (-rx * 0.7, ry)]
        rot = [(x * math.cos(ang) - y * math.sin(ang),
                x * math.sin(ang) + y * math.cos(ang)) for x, y in base]
        _poly(surf, BODY_D, [P(cx + x, cy + y) for x, y in rot])
        _poly(surf, BODY, [P(cx + x * 0.82 + 0.5, cy + y * 0.82 + 0.5) for x, y in rot])
        if splay:
            for t in (-0.42, 0.0, 0.42):
                tip = P(cx + rx * t, cy + ry * 1.15)
                top = P(cx + rx * t * 0.5, cy + ry * 0.45)
                pygame.draw.line(surf, INK, top, tip, max(1, int(s)))

    web_lobe(-15, 27, 7.5, 6, 0.18)   # back/left foot

    # ---- DOMED turtle-shell HUMP rising off the back (sits ON the silhouette
    #      so the outline bulges up-and-back). Drawn before the body so the
    #      front body overlaps its lower lip and the hump reads as a back dome.
    #      Pushed up + right so the dome crests the back-top outline rather than
    #      reading as a side patch — the signature shell-hump tell at 24px.
    sh_cx, sh_cy = 6, -5
    _ellipse(surf, SHELL_D, *P(sh_cx, sh_cy + 0.5), 25 * s, 22 * s)        # dark core
    _ellipse(surf, SHELL, ox + (sh_cx + 0.8) * s, oy + (sh_cy + 1.2) * s, 23 * s, 20 * s)  # fill
    _ellipse(surf, SHELL_RIM, ox + (sh_cx - 8) * s, oy + (sh_cy - 9) * s, 9 * s, 7 * s)    # TL sheen

    # big hard hexagon plates across the visible dome (few + large = no 1x noise)
    _hex(surf, SHELL_D, *P(sh_cx, sh_cy - 6), 9 * s)
    _hex(surf, SHELL_RIM, ox + sh_cx * s, oy + (sh_cy - 6.7) * s, 7.4 * s)
    _hex(surf, SHELL, ox + sh_cx * s, oy + (sh_cy - 6) * s, 6.6 * s)

    for hx, hy in [(-13, 3), (13, 1), (-6, 12), (8, 11)]:
        _hex(surf, SHELL_D, *P(sh_cx + hx, sh_cy + hy), 7.6 * s)
        _hex(surf, SHELL, ox + (sh_cx + hx) * s, oy + (sh_cy + hy - 0.6) * s, 5.8 * s)
    # plate seam keylines for the carved-relief read
    for hx, hy in [(0, -6), (-13, 3), (13, 1), (-6, 12), (8, 11)]:
        pygame.draw.circle(surf, SHELL_D, P(sh_cx + hx, sh_cy + hy),
                           int(6.4 * s), max(1, int(s)))

    # ---- body: round, bottom-heavy froggy mass, in front of the shell ----
    bx, by = -1, 11
    _ellipse(surf, BODY_D, *P(bx, by + 1), 19 * s, 21 * s)          # dark core
    _ellipse(surf, BODY, ox + (bx + 1.2) * s, oy + (by + 1.4) * s, 17 * s, 19 * s)  # fill
    _ellipse(surf, SHEEN, ox + (bx - 6) * s, oy + (by - 8) * s, 8 * s, 7 * s)       # TL rim sheen

    # belly plastron — pale oval value-partner for the bronze shell
    _ellipse(surf, PLASTRON_D, *P(bx + 0.5, by + 8), 10 * s, 12 * s)
    _ellipse(surf, PLASTRON, ox + (bx + 0.5) * s, oy + (by + 8.6) * s, 8.4 * s, 10.4 * s)
    # plastron scute seams (light carved lines)
    for sy in (-4, 1, 6):
        pygame.draw.line(surf, PLASTRON_D, P(bx - 6.5, by + 8 + sy), P(bx + 7.5, by + 8 + sy),
                         max(1, int(s)))
    pygame.draw.line(surf, PLASTRON_D, P(bx + 0.5, by + 1), P(bx + 0.5, by + 16), max(1, int(s)))

    # ---- remaining webbed limbs ----
    web_lobe(12, 28, 8, 7, -0.16)    # front/right foot
    web_lobe(-19, 13, 6, 5, 1.2)     # left hand (clutches cucumber)

    # ---- cucumber clutched low in the left hand (signature snack) ----
    cu = [(-10, -3), (9, -8), (12, -4), (-8, 1)]
    cucx, cucy = -22, 14
    _poly(surf, CUKE_D, [P(cucx + x, cucy + y + 0.6) for x, y in cu])
    cu2 = [(-9, -3.2), (8, -7.4), (10.6, -4.2), (-7, 0.4)]
    _poly(surf, CUKE, [P(cucx + x, cucy + y) for x, y in cu2])
    pygame.draw.line(surf, CUKE_RIM, P(cucx - 8, cucy - 4), P(cucx + 8, cucy - 6.5),
                     max(1, int(s)))
    # tiny webbed hand wrapping the cucumber
    _ellipse(surf, BODY_D, *P(cucx + 2, cucy - 1), 4 * s, 4 * s)
    _ellipse(surf, BODY, ox + (cucx + 2) * s, oy + (cucy - 1.4) * s, 3 * s, 3 * s)

    # ---- head: chibi, big, sits high; the beak breaks the lower outline ----
    hx, hy, hr = 0, -19, 15
    _ellipse(surf, BODY_D, *P(hx, hy), hr * s, (hr - 1) * s)
    _ellipse(surf, BODY, ox + (hx + 1) * s, oy + (hy + 1) * s, (hr - 2) * s, (hr - 3) * s)
    _ellipse(surf, SHEEN, ox + (hx - 6) * s, oy + (hy - 6) * s, 5.5 * s, 4.5 * s)
    # froggy wide lower-cheek flare
    _ellipse(surf, BODY, ox + hx * s, oy + (hy + 6) * s, (hr - 1) * s, 10 * s)

    # ---- BEAK on the FACE between/below the eyes, breaking the head outline ----
    bkx, bky = 0, -10
    bk = [(-5.5, 0), (5.5, 0), (2.5, 7.5), (-2.5, 7.5)]   # short downward bird-beak
    _poly(surf, BEAK_D, [P(bkx + x, bky + y + 0.6) for x, y in bk])
    _poly(surf, BEAK, [P(bkx + x, bky + y) for x, y in bk])
    # beak split + nostrils + a sheen catch so it reads as a hard beak, not a bib
    pygame.draw.line(surf, BEAK_D, P(bkx - 4.5, bky + 3.6), P(bkx + 4.5, bky + 3.6),
                     max(1, int(s)))
    pygame.draw.line(surf, BEAK_RIM, P(bkx - 4.5, bky + 0.6), P(bkx + 1, bky + 0.6),
                     max(1, int(s)))
    for nx in (-2, 2):
        _ellipse(surf, BEAK_D, *P(bkx + nx, bky + 1.6), 0.7 * s, 0.7 * s)

    # ---- big round friendly eyes (scary-CUTE) ----
    for ex in (-7, 7):
        _ellipse(surf, WHITE, *P(hx + ex, hy - 3), 5.4 * s, 6.2 * s)
        _ellipse(surf, INK, ox + (hx + ex + ex * 0.05) * s, oy + (hy - 2) * s, 3.2 * s, 3.7 * s)
        _ellipse(surf, WHITE, ox + (hx + ex - 1.5) * s, oy + (hy - 4) * s, 1.3 * s, 1.3 * s)
    # heavy brow ridge — a touch of menace
    pygame.draw.line(surf, BODY_D, P(hx - 12, hy - 8), P(hx - 2, hy - 6), max(2, int(2 * s)))
    pygame.draw.line(surf, BODY_D, P(hx + 12, hy - 8), P(hx + 2, hy - 6), max(2, int(2 * s)))

    # ---- water DISH on the crown (flat bowl + turquoise water ripple) ----
    dx, dy = 0, -31
    _ellipse(surf, BODY_D, *P(dx, dy + 1), 13 * s, 6 * s)        # green fleshy rim
    _ellipse(surf, BODY, ox + dx * s, oy + dy * s, 12 * s, 5 * s)
    _ellipse(surf, DISH_D, ox + dx * s, oy + (dy - 0.5) * s, 9.5 * s, 3.8 * s)
    _ellipse(surf, DISH, ox + dx * s, oy + (dy - 1) * s, 9 * s, 3.2 * s)
    pygame.draw.arc(surf, DISH_RIM,
                    (int(ox + (dx - 6) * s), int(oy + (dy - 3) * s), int(12 * s), int(6 * s)),
                    0.4, 2.4, max(1, int(s)))
    _ellipse(surf, DISH_RIM, ox + (dx - 3) * s, oy + (dy - 1.5) * s, 1.4 * s, 0.9 * s)
    # tuft of hair ringing the dish (kappa signature)
    for ang in range(200, 341, 26):
        a = math.radians(ang)
        x0 = dx + 12 * math.cos(a)
        y0 = dy + 5 * math.sin(a)
        pygame.draw.line(surf, BODY_D, P(x0, y0),
                         P(x0 + 2 * math.cos(a), y0 + 3 * math.sin(a) - 2), max(1, int(s)))


def draw_bamboo_pillar(surf, cx, top, bottom, w, cap=True):
    """Prop -> PILLAR mirror: segmented bamboo water-spout (shishi-odoshi).
    Repeatable node-banded shaft body; a tipping dipper pouring a water-ribbon
    is the detachable gap-edge cap. Symmetric on-axis — clean mirror."""
    half = w // 2
    seg_h = w * 1.7
    pygame.draw.rect(surf, BAMBOO_D, (cx - half - 2, top, w + 4, bottom - top))
    pygame.draw.rect(surf, BAMBOO, (cx - half, top, w, bottom - top))
    pygame.draw.rect(surf, BAMBOO_RIM, (cx - half + 2, top, max(2, w // 5), bottom - top))
    y = top + seg_h
    while y < bottom:
        pygame.draw.rect(surf, BAMBOO_D, (cx - half - 3, int(y) - 3, w + 6, 6))
        pygame.draw.line(surf, BAMBOO_RIM, (cx - half + 2, int(y) - 3),
                         (cx - half + 2, int(y) + 3), 2)
        y += seg_h

    if cap:
        # ---- gap-edge cap: a tipping bamboo DIPPER pouring a water-RIBBON ----
        # The dipper is a fat half-cylinder tilted to spill; mass stays on-axis
        # while the turquoise ribbon (mirroring the head-dish hue) drops INTO
        # the gap as a distinct gap-edge event.
        dip_y = top
        # cradle / pivot collar on the shaft
        pygame.draw.rect(surf, BAMBOO_D, (cx - half - 4, dip_y - 6, w + 8, 8))
        pygame.draw.rect(surf, BAMBOO_RIM, (cx - half - 2, dip_y - 5, w + 4, 2))

        # tilted dipper trough (open scoop, tipping right-down). Kept tight to
        # the shaft axis so the gap-cap mass stays balanced — the mirror reads
        # like Big Reapy's centred finial, not a top-heavy lopsided arm.
        scoop = [(cx - half - 10, dip_y - 28), (cx + half + 10, dip_y - 16),
                 (cx + half + 13, dip_y - 6), (cx + 2, dip_y - 11),
                 (cx - half - 7, dip_y - 21)]
        _poly(surf, BAMBOO_D, [(x + 2, y + 2) for x, y in scoop])
        _poly(surf, BAMBOO, scoop)
        # inner trough shadow + rim sheen so the scoop reads as a half-cylinder
        pygame.draw.line(surf, BAMBOO_D, (cx - half - 8, dip_y - 25),
                         (cx + half + 9, dip_y - 13), max(2, w // 6))
        pygame.draw.line(surf, BAMBOO_RIM, (cx - half - 8, dip_y - 28),
                         (cx + half + 9, dip_y - 16), 2)
        # node band on the dipper so it reads as bamboo
        pygame.draw.line(surf, BAMBOO_D, (cx - 3, dip_y - 24), (cx - 1, dip_y - 11),
                         max(2, w // 7))

        # spilling water RIBBON pouring off the tipped lip into the gap
        lip_x = cx + half + 10
        rib = [(lip_x - 6, dip_y - 14), (lip_x - 2, dip_y - 8),
               (lip_x - 7, dip_y + 14), (lip_x + 1, dip_y + 36),
               (lip_x + 8, dip_y + 16), (lip_x + 4, dip_y - 6)]
        _poly(surf, DISH_D, [(x + 2, y) for x, y in rib])
        _poly(surf, DISH, rib)
        pygame.draw.line(surf, DISH_RIM, (lip_x - 2, dip_y - 8),
                         (lip_x - 3, dip_y + 26), 2)
        # splash droplets at the gap line
        for ddx, ddy, dr in [(-8, 40, 4), (10, 44, 3), (2, 50, 3), (-2, 38, 2)]:
            _ellipse(surf, DISH, lip_x + ddx, dip_y + ddy, dr, dr)
            _ellipse(surf, DISH_RIM, lip_x + ddx - dr * 0.3, dip_y + ddy - dr * 0.3,
                     dr * 0.4, dr * 0.4)


def build_kappa_sprite(unit_px):
    """Render the kappa at unit_px supersampled, outline from its alpha mask,
    return the high-res surface (caller smoothscales)."""
    W = int(60 * unit_px)
    H = int(64 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_kappa(big, big.get_width() // 2, int(H * SS * 0.56), unit_px * SS)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


def build_pillar_sprite(unit_px):
    W = int(46 * unit_px)
    H = int(96 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    # seat the shaft top low enough that the tipping dipper + ribbon (which rise
    # ~36px above `top`) clear the surface edge instead of being clipped
    draw_bamboo_pillar(big, big.get_width() // 2,
                       int(42 * unit_px * SS), big.get_height(),
                       int(12 * unit_px * SS), cap=True)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


# ── tiny sibling-green proxies for the on-one-card separation check ─────────
# Just enough to verify Kappa jumps warm/yellow off Cernun pine + Tlaloc jade.
CERNUN_G = (54, 92, 68)
TLALOC_G = (86, 134, 128)
TLALOC_CORAL = (224, 90, 74)


def _green_chip(surf, cx, cy, body, label_fn, name, extra=None):
    _ellipse(surf, tuple(int(c * 0.7) for c in body), cx, cy + 1, 16, 17)
    _ellipse(surf, body, cx + 1, cy + 1, 14, 15)
    _ellipse(surf, tuple(min(255, int(c * 1.3 + 30)) for c in body), cx - 5, cy - 5, 5, 4)
    if extra:
        _ellipse(surf, extra, cx, cy + 7, 5, 3)   # coral focal mouth for Tlaloc
    label_fn(name, cx - 22, cy + 20)


def main():
    pygame.init()

    SHEET_W, SHEET_H = 820, 620
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sky_a, sky_b = (152, 198, 232), (108, 156, 196)
    for y in range(SHEET_H):
        t = y / SHEET_H
        c = tuple(int(sky_a[i] + (sky_b[i] - sky_a[i]) * t) for i in range(3))
        pygame.draw.line(sheet, c, (0, y), (SHEET_W, y))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    title = pygame.font.SysFont("dejavusans", 22, bold=True)

    def label(text, x, y, col=(20, 28, 24)):
        sheet.blit(font.render(text, True, (250, 252, 248)), (x + 1, y + 1))
        sheet.blit(font.render(text, True, col), (x, y))

    def slabel(text, x, y):
        sheet.blit(small.render(text, True, (250, 252, 248)), (x + 1, y + 1))
        sheet.blit(small.render(text, True, (24, 32, 26)), (x, y))

    sheet.blit(title.render("KAPPA — turtle-shelled water-dish imp  (round 2)", True, (250, 252, 248)), (19, 13))
    sheet.blit(title.render("KAPPA — turtle-shelled water-dish imp  (round 2)", True, (22, 36, 24)), (18, 12))
    sheet.blit(small.render("GREEN-BAND #3 BRIGHT YELLOW-GREEN  ·  domed shell-hump / dish-crowned beaked head / bottom-heavy froggy",
                            True, (24, 40, 26)), (18, 38))

    # ---- large creature ----
    big_c, _ = build_kappa_sprite(5.0)
    large_c = pygame.transform.smoothscale(big_c, (big_c.get_width() // SS, big_c.get_height() // SS))
    sheet.blit(large_c, (24, 64))
    label("creature", 90, 60 + large_c.get_height())

    # ---- large pillar mirror ----
    big_p, _ = build_pillar_sprite(4.0)
    large_p = pygame.transform.smoothscale(big_p, (big_p.get_width() // SS, big_p.get_height() // SS))
    sheet.blit(large_p, (336, 64))
    label("bamboo water-spout pillar", 300, 58 + large_p.get_height())
    slabel("tipping-dipper cap pours a turquoise ribbon into the gap · node-banded shaft repeats",
           300, 78 + large_p.get_height())

    panel_x = 546
    # light panel
    pygame.draw.rect(sheet, (236, 240, 232), (panel_x, 64, 252, 250), border_radius=8)
    pygame.draw.rect(sheet, (40, 60, 44), (panel_x, 64, 252, 250), 2, border_radius=8)
    # dark panel
    pygame.draw.rect(sheet, (28, 36, 52), (panel_x, 326, 252, 130), border_radius=8)
    pygame.draw.rect(sheet, (90, 110, 130), (panel_x, 326, 252, 130), 2, border_radius=8)

    def to_h(big, target_h):
        w, h = big.get_size()
        scale = (target_h * SS) / h
        return pygame.transform.smoothscale(big, (max(1, int(w * scale / SS)), target_h))

    slabel("32px on day sky  ·  48 / 24px detail", panel_x + 10, 70)
    sheet.blit(to_h(big_c, 48), (panel_x + 18, 96))
    sheet.blit(to_h(big_c, 32), (panel_x + 92, 110))
    sheet.blit(to_h(big_c, 24), (panel_x + 150, 116))
    sheet.blit(to_h(big_p, 90), (panel_x + 196, 96))
    slabel("48px", panel_x + 26, 150)
    slabel("32", panel_x + 100, 150)
    slabel("24", panel_x + 154, 150)

    slabel("32px on night sky", panel_x + 10, 332)
    sheet.blit(to_h(big_c, 36), (panel_x + 24, 360))
    sheet.blit(to_h(big_c, 24), (panel_x + 86, 372))
    sheet.blit(to_h(big_p, 72), (panel_x + 150, 358))

    # ---- GREEN-BAND separation card: three creatures on ONE green day-sky ----
    gy0 = 470
    pygame.draw.rect(sheet, (150, 196, 132), (24, gy0, 510, 124), border_radius=8)   # green day-sky
    pygame.draw.rect(sheet, (60, 96, 60), (24, gy0, 510, 124), 2, border_radius=8)
    slabel("GREEN-BAND CHECK on one green day-sky @ 32px — Kappa must jump warm/yellow:",
           34, gy0 + 6)

    # Kappa (real sprite) at 32px
    k32 = to_h(big_c, 40)
    sheet.blit(k32, (60, gy0 + 38))
    slabel("Kappa (120,194,72)", 44, gy0 + 100)
    # Cernun pine + Tlaloc grey-jade (proxy chips, same triad grammar)
    def clab(name, x, y):
        sheet.blit(small.render(name, True, (250, 252, 248)), (x + 1, y + 1))
        sheet.blit(small.render(name, True, (20, 30, 22)), (x, y))
    _green_chip(sheet, 250, gy0 + 64, CERNUN_G, clab, "Cernun pine")
    clab("(54,92,68)", 228, gy0 + 100)
    _green_chip(sheet, 410, gy0 + 64, TLALOC_G, clab, "Tlaloc jade", extra=TLALOC_CORAL)
    clab("(86,134,128)+coral", 372, gy0 + 100)

    # palette swatches
    swatches = [("body", BODY), ("shade", BODY_D), ("shell", SHELL), ("plastron", PLASTRON),
                ("dish", DISH), ("beak", BEAK), ("bamboo", BAMBOO), ("sheen", SHEEN)]
    sx = 548
    sy = 530
    slabel("pinned palette:", sx, sy - 18)
    for name, col in swatches:
        if sx > SHEET_W - 40:
            sx = 548
            sy += 46
        pygame.draw.rect(sheet, col, (sx, sy, 28, 28), border_radius=4)
        pygame.draw.rect(sheet, (20, 28, 24), (sx, sy, 28, 28), 1, border_radius=4)
        sheet.blit(small.render(name, True, (250, 252, 248)), (sx + 1, sy + 29))
        sheet.blit(small.render(name, True, (22, 30, 24)), (sx, sy + 28))
        sx += 66

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
