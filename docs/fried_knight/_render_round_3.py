"""Headless exploration sheet for the FRIED KNIGHT — round 3 (final tuning).

Round 2's hybrid (#2 golden-brown base + #4 grease-sheen/belly-glow, plate-
distributed texture, on-silhouette contour, no shell) was approved on hue,
sheen lobe, contour, belly-glow, night read and the fry-family match to the
fried parrot. The ONE remaining problem: at 1x the knight had fried into a
golden BLOB — the three "knight" landmarks (helm T-slit, shield boss/edge,
sword) dissolved. Round 3 fixes exactly that and holds everything else:

  1. LANDMARK INSETS (top priority): re-assert the helm visor T-slit, the
     shield boss + shield perimeter, and the sword as thin 1-2px DARKER-GOLDEN
     recessed inset lines drawn ON TOP of the fry pass (same darker-golden
     family as the contour, ~(150,92,28)). Anchored to the real plate
     positions (helm 0.73x/0.17y, shield via _SHIELD_POS, sword 0.74x/0.5y).
     They survive at ~28px tall.
  2. DE-PUFF JOINTS: keep global plump, but suppress the belly-glow/puff in the
     SEAMS between helm-gorget and shield-chest by ~35% so adjacent plates
     don't bridge into each other. Convex puff on plate INTERIORS is preserved.
  3. PULL CRACKLE ~25% OFF the focal plates (shield boss + helm face) so those
     landmarks read clean; denser crackle stays on the chest skirt/lower body.
  4. HOLD everything else (recolor, sheen, contour, no-shell, belly-glow).

This sheet shows the fixed hybrid at 1.13x and 1.15x, each on day AND night
sky, PLUS a ~28px name-test thumbnail (upscaled) of each so helm/shield/sword
legibility is provable, PLUS the plain steel knight and fried parrot for
reference.

Run with SDL_VIDEODRIVER=dummy. Writes docs/fried_knight/round_3.png.
"""
import os
import sys
import random
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = "/home/user/skybit"
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot
from game import knight_skin as ks

_GOLD = ks._CRISPY_GOLD
_DARK = ks._CRISPY_DARK
_LIGHT = ks._CRISPY_LIGHT
_SPOT = ks._CRISPY_SPOT


# ── plate-region map (frac of the un-padded body rect, mirrors _build_knight_frame)
# Each region carries a relative texture DENSITY weight. Round 3 adds a
# `focal` flag: the helm face and shield boss are landmark plates whose crackle
# is thinned ~25% so the recessed inset lines (drawn after) read clean. The
# chest skirt / lower body KEEP their dense crackle.
# (fx, fy, rw, rh, weight, spot_max, focal)
_PLATE_REGIONS = [
    (0.45, 0.62, 0.50, 0.30, 2.6, 2, False),   # breastplate — large flat -> densest
    (0.92, 0.58, 0.36, 0.46, 2.4, 2, True),    # shield — FOCAL: thinned crackle
    (0.45, 0.46, 0.42, 0.34, 0.7, 1, False),   # pauldron — small, ridged -> sparse
    (0.73, 0.17, 0.50, 0.54, 1.3, 2, True),    # helm — FOCAL: thinned crackle
    (0.74, 0.50, 0.30, 0.95, 0.5, 1, False),   # sword — thin edge -> very sparse
    (0.30, 0.55, 0.40, 0.45, 1.1, 2, False),   # belly/body skirt -> denser crackle
]

# How much to thin crackle (NOT spots) on the focal landmark plates.
_FOCAL_CRACKLE_KEEP = 0.75


def _fry_texture_by_plate(out, *, total_spots, total_crackle, pad, body_rect,
                          seed=0x5C0FFEE):
    """Crispy spots + crackle distributed BY PLATE SIZE, clamped to the
    silhouette (no shell). Round 3: crackle on the FOCAL plates (helm face,
    shield boss) is pulled ~25% so the recessed landmark insets drawn on top
    stay legible; spot density is unchanged so the fry texture still reads."""
    w, h = out.get_size()
    tex = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(seed)

    boxes = []
    wsum = 0.0
    for fx, fy, rw, rh, weight, smax, focal in _PLATE_REGIONS:
        cx = pad + fx * body_rect[2]
        cy = pad + fy * body_rect[3]
        bw = rw * body_rect[2]
        bh = rh * body_rect[3]
        bx = cx - bw / 2
        by = cy - bh / 2
        a = bw * bh * weight
        boxes.append((bx, by, bw, bh, smax, a, focal))
        wsum += a

    for bx, by, bw, bh, smax, a, focal in boxes:
        n = max(1, int(round(total_spots * a / wsum)))
        for _ in range(n):
            px = int(bx + rng.random() * bw)
            py = int(by + rng.random() * bh)
            px = max(0, min(w - 1, px))
            py = max(0, min(h - 1, py))
            pygame.draw.circle(tex, _SPOT, (px, py), rng.randint(1, smax))
        nc = max(0, int(round(total_crackle * a / wsum)))
        if focal:
            nc = int(round(nc * _FOCAL_CRACKLE_KEEP))
        for _ in range(nc):
            x1 = int(max(2, min(w - 12, bx + rng.random() * bw)))
            y1 = int(max(2, min(h - 12, by + rng.random() * bh)))
            dx, dy = rng.randint(5, 11), rng.randint(-5, 5)
            pygame.draw.line(tex, _DARK, (x1, y1), (x1 + dx, y1 + dy), 2)
            pygame.draw.line(tex, _LIGHT, (x1 - 1, y1 - 1), (x1 + dx - 1, y1 + dy - 1), 1)

    tex.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(tex, (0, 0))


def _sheen_upper(sprite, top_col, bot_col, top_a, bot_a):
    """Grease gloss anchored UPPER-LEFT to match the fried parrot's highlight.
    Strong soft top lobe + faint lower fill, peak pulled down so it's wet
    gloss, not hot plastic. Masked to the silhouette (on-surface, no halo)."""
    w, h = sprite.get_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(ov, (*top_col, top_a),
                        (int(w * 0.10), int(-h * 0.10), int(w * 0.62), int(h * 0.60)))
    pygame.draw.ellipse(ov, (*bot_col, bot_a),
                        (int(w * 0.12), int(h * 0.50), int(w * 0.78), int(h * 0.56)))
    ov.blit(ks._amask(sprite), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(ov, (0, 0))
    return sprite


def _belly_glow(out, alpha, pad, body_rect):
    """Subtle warm 'juicy inside' glow, LOW and CENTRED, masked to the body so
    it never rings the outside. Round 3: the glow is punched out where the
    helm-gorget meets the shield-chest (the upper seam band) by ~35% so the
    puff stops bridging adjacent plates into a single lump — the convex puff on
    each plate's interior is kept, only the gap-fill in the seam is suppressed."""
    w, h = out.get_size()
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 200, 104, alpha),
                        (int(w * 0.26), int(h * 0.50), int(w * 0.40), int(h * 0.30)))

    # De-puff the seam: a soft horizontal band across the helm-gorget / shield-
    # chest junction (~0.40-0.56 of height) where plates abut. Subtracting alpha
    # here keeps the puff convex on each plate but stops it filling the joint.
    seam = pygame.Surface((w, h), pygame.SRCALPHA)
    sy0 = int(h * 0.40)
    sy1 = int(h * 0.56)
    cut = int(255 * 0.35)   # ~35% suppression at the seam centre
    band_h = max(1, sy1 - sy0)
    for j in range(band_h):
        t = j / band_h
        # triangular falloff -> strongest cut mid-band, feathered at edges.
        a = int(cut * (1.0 - abs(t - 0.5) * 2.0))
        if a > 0:
            pygame.draw.line(seam, (0, 0, 0, a), (0, sy0 + j), (w, sy0 + j))
    glow.blit(seam, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    glow.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(glow, (0, 0))


def _contour(out, col, alpha):
    """A thin 1px darker-golden line ON the outer silhouette so the knight read
    survives a bright sheen on a night sky. Traces the alpha mask outline and
    clamps it to the silhouette so the closing segments never cut a gap."""
    mask = pygame.mask.from_surface(out, 40)
    line = pygame.Surface(out.get_size(), pygame.SRCALPHA)
    for comp in mask.connected_components():
        pts = comp.outline(1)
        if len(pts) >= 2:
            pygame.draw.lines(line, (*col, alpha), True, pts, 1)
    line.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(line, (0, 0))


# ── ROUND-3 LANDMARK INSETS ──────────────────────────────────────────────────
# Thin recessed inset lines in the darker-golden family (same as the contour)
# drawn ON TOP of the fry pass. They re-cut the three "knight" reads that the
# fry had dissolved: the helm visor T-slit, the shield boss + heater edge, and
# the sword spine + crossguard. Anchored to the SAME _P() plate positions
# _build_knight_frame uses so they land exactly on the steel features. A faint
# warm highlight is laid 1px above/left of each recess so it reads as a sculpted
# groove (lit upper-left), not a smudge.
_INSET_DARK = (150, 92, 28)      # recessed groove — darker-golden, matches contour
_INSET_DARK_A = 205
_INSET_LIT = (255, 226, 150)     # 1px warm ridge above the groove (upper-left light)
_INSET_LIT_A = 120


def _landmark_insets(out, *, pad, body_rect):
    """Re-assert helm T-slit, shield boss/edge, sword as darker-golden recessed
    insets ON the fried sprite, at the real plate anchors. Masked to the
    silhouette so nothing spills past the edge."""
    w, h = out.get_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    bw, bh = body_rect[2], body_rect[3]

    def bx(fx):
        return pad + fx * bw

    def by(fy):
        return pad + fy * bh

    def groove(p0, p1, width=2):
        """A recessed line + a 1px lit ridge offset up-left (sculpted look)."""
        pygame.draw.line(ov, (*_INSET_DARK, _INSET_DARK_A), p0, p1, width)
        pygame.draw.line(ov, (*_INSET_LIT, _INSET_LIT_A),
                         (p0[0] - 1, p0[1] - 1), (p1[0] - 1, p1[1] - 1), 1)

    # ── HELM visor T-slit ── helm anchored at (0.73,0.17), sub-surface 0.5x0.54.
    # _helm draws the visor band at 0.40*helm_h from the helm-box TOP, i.e. at
    # ~-0.10*helm_h above the helm centre; the central nasal/breath bar runs down
    # from it. Recut that exact T: a horizontal brow/eye slot at the real visor
    # line + a short vertical nasal hanging below it.
    hcx = bx(0.73)
    hcy = by(0.17)
    hw = 0.50 * bw
    hh = 0.54 * bh
    brow_y = hcy - 0.10 * hh                                                  # real visor line
    bx0 = hcx - 0.22 * hw
    bx1 = hcx + 0.24 * hw
    groove((int(bx0), int(brow_y)), (int(bx1), int(brow_y + 0.02 * hh)), width=2)  # brow/eye slot
    nasal_top = brow_y + 0.02 * hh
    nasal_bot = hcy + 0.16 * hh
    groove((int(hcx + 0.02 * hw), int(nasal_top)),
           (int(hcx + 0.02 * hw), int(nasal_bot)), width=2)                   # nasal bar

    # ── SHIELD boss + heater edge ── shield via _SHIELD_POS (0.92,0.58,0.36,0.46).
    sfx, sfy, swf, shf = ks._SHIELD_POS
    scx = bx(sfx)
    scy = by(sfy)
    sw = swf * bw
    sh = shf * bh
    # Heater outline: top corners -> mid waist -> point, traced as a thin recess
    # so the shield silhouette pops off the chest.
    top = scy - 0.40 * sh
    waist = scy + 0.02 * sh
    pt_y = scy + 0.50 * sh
    lx = scx - 0.46 * sw
    rx = scx + 0.46 * sw
    heater = [
        (int(lx), int(top)), (int(rx), int(top)),
        (int(rx), int(waist)), (int(scx), int(pt_y)), (int(lx), int(waist)),
    ]
    for a, b in zip(heater, heater[1:] + heater[:1]):
        groove(a, b, width=2)
    # Boss: a small recessed ring + centre dot at the shield middle (the brass
    # stud in _breast/_shield) so the focal plate has a clear centre read.
    pygame.draw.circle(ov, (*_INSET_DARK, _INSET_DARK_A),
                       (int(scx), int(scy)), max(2, int(0.12 * sw)), 2)
    pygame.draw.circle(ov, (*_INSET_LIT, _INSET_LIT_A),
                       (int(scx - 1), int(scy - 1)), max(1, int(0.05 * sw)))

    # ── SWORD spine + crossguard ── sword anchored (0.74,0.5), sub 0.5x0.95.
    # _sword runs grip (0.42,0.80) -> tip (0.74,0.06) of ITS 0.5x0.95 surface.
    scx2 = bx(0.74)
    scy2 = by(0.50)
    sww = 0.50 * bw
    swh = 0.95 * bh
    gx = scx2 + (0.42 - 0.5) * sww
    gy = scy2 + (0.80 - 0.5) * swh
    tx = scx2 + (0.74 - 0.5) * sww
    ty = scy2 + (0.06 - 0.5) * swh
    groove((int(gx), int(gy)), (int(tx), int(ty)), width=2)                   # blade spine
    # crossguard: short bar perpendicular to the blade at the grip.
    ux, uy = (tx - gx), (ty - gy)
    ln = math.hypot(ux, uy) or 1.0
    ux, uy = ux / ln, uy / ln
    px, py = -uy, ux
    cg = 0.05 * swh
    groove((int(gx + px * cg), int(gy + py * cg)),
           (int(gx - px * cg), int(gy - py * cg)), width=2)                   # crossguard

    ov.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(ov, (0, 0))


# ── THE HYBRID deep-fry (round-3 canonical candidate for _deep_fry) ───────────
def hybrid_fry(frame, *, mult, add, spots, crackle, sheen_top, sheen_bot,
               top_a, bot_a, belly_a, contour_col, contour_a):
    """#2 golden-brown recolor + plate-distributed texture (focal crackle
    thinned) + #4 sheen/belly-glow (seam de-puffed) + darker-golden landmark
    insets on top + on-silhouette contour. NO shell."""
    out = ks._recolor(frame, mult, add=add)
    bw, bh = parrot._get_frames()[0].get_size()
    pad = ks._PAD
    body_rect = (pad, pad, bw, bh)
    _fry_texture_by_plate(out, total_spots=spots, total_crackle=crackle,
                          pad=pad, body_rect=body_rect)
    _belly_glow(out, belly_a, pad, body_rect)
    _sheen_upper(out, sheen_top, sheen_bot, top_a, bot_a)
    # Landmark insets go AFTER sheen/glow so the recessed reads aren't washed
    # out by the gloss; contour last so the silhouette stays crisp.
    _landmark_insets(out, pad=pad, body_rect=body_rect)
    _contour(out, contour_col, contour_a)
    return out


def _plump(frame, scale):
    w, h = frame.get_size()
    return pygame.transform.smoothscale(frame, (round(w * scale), round(h * scale)))


# ── final settings: ship target 1.15x, fallback 1.13x ────────────────────────
# Shared golden-brown floor + sheen lobe + contour + belly-glow are FINAL from
# round 2; only the landmark insets, focal-crackle thinning and seam de-puff are
# new. Both rows use the exact round-2 recolor/sheen/contour numbers.
_BASE_MULT = (214, 142, 46)
_BASE_ADD = (44, 22, 2)
_SPOTS = 70
_CRACKLE = 24
_CONTOUR = (150, 92, 28)
_CONTOUR_A = 150

SETTINGS = {
    "1.13x  (fallback — if joints still bridge)": dict(
        mult=_BASE_MULT, add=_BASE_ADD, spots=_SPOTS, crackle=_CRACKLE,
        sheen_top=(255, 240, 184), sheen_bot=(244, 198, 112),
        top_a=66, bot_a=42, belly_a=46,
        contour_col=_CONTOUR, contour_a=_CONTOUR_A, plump=1.13),
    "1.15x  (SHIP TARGET)": dict(
        mult=_BASE_MULT, add=_BASE_ADD, spots=_SPOTS, crackle=_CRACKLE,
        sheen_top=(255, 240, 188), sheen_bot=(244, 200, 116),
        top_a=74, bot_a=46, belly_a=54,
        contour_col=_CONTOUR, contour_a=_CONTOUR_A, plump=1.15),
}

FRAME_IDX = 2
plain_knight = ks.build_knight_frames()
steel_ref = plain_knight[FRAME_IDX]
fried_parrot = parrot.get_fried_parrot(FRAME_IDX, 0.0)


def make_hybrid(cfg):
    base = ks.build_knight_frames()[FRAME_IDX]
    fried = hybrid_fry(
        base, mult=cfg["mult"], add=cfg["add"], spots=cfg["spots"],
        crackle=cfg["crackle"], sheen_top=cfg["sheen_top"],
        sheen_bot=cfg["sheen_bot"], top_a=cfg["top_a"], bot_a=cfg["bot_a"],
        belly_a=cfg["belly_a"], contour_col=cfg["contour_col"],
        contour_a=cfg["contour_a"])
    return _plump(fried, cfg["plump"])


# ── sky backdrops (busy day + night) ─────────────────────────────────────────
def day_sky(surf, rect):
    for j in range(rect.h):
        t = j / rect.h
        col = (int(96 + 120 * (1 - t)), int(170 + 60 * (1 - t)), int(230 - 40 * t))
        pygame.draw.line(surf, col, (rect.x, rect.y + j), (rect.right, rect.y + j))
    rng = random.Random(7)
    for _ in range(5):
        cx = rect.x + rng.randint(10, rect.w - 30)
        cy = rect.y + rng.randint(10, rect.h - 30)
        for k in range(4):
            pygame.draw.circle(surf, (245, 250, 255),
                               (cx + k * 9, cy + (k % 2) * 4), 9 - k)
    for _ in range(40):
        px = rect.x + rng.randint(0, rect.w - 1)
        py = rect.y + rng.randint(0, rect.h - 1)
        pygame.draw.circle(surf, (255, 235, 170), (px, py), rng.randint(1, 2))


def night_sky(surf, rect):
    for j in range(rect.h):
        t = j / rect.h
        col = (int(18 + 26 * t), int(20 + 30 * t), int(46 + 40 * t))
        pygame.draw.line(surf, col, (rect.x, rect.y + j), (rect.right, rect.y + j))
    rng = random.Random(13)
    for _ in range(70):
        px = rect.x + rng.randint(0, rect.w - 1)
        py = rect.y + rng.randint(0, rect.h - 1)
        pygame.draw.circle(surf, (220, 228, 255), (px, py), rng.randint(0, 1) + 1)
    pygame.draw.circle(surf, (236, 240, 220),
                       (rect.right - 34, rect.y + 30), 16)
    pygame.draw.circle(surf, (200, 206, 188),
                       (rect.right - 30, rect.y + 26), 13)


# ── sheet layout ─────────────────────────────────────────────────────────────
BG = (40, 46, 60)
PANEL = (52, 60, 78)
INK = (236, 242, 255)
SUB = (176, 186, 206)
ACC = (255, 214, 132)
GOOD = (150, 224, 160)

_FONT = os.path.join(_ROOT, "game", "assets", "LiberationSans-Bold.ttf")
font = pygame.font.Font(_FONT, 22)
fsmall = pygame.font.Font(_FONT, 15)
ftiny = pygame.font.Font(_FONT, 12)
ftitle = pygame.font.Font(_FONT, 30)

GAME_SCALE = 1.7
ZOOM_SCALE = 3.6
# name-test: render the fried sprite at the real in-world pixel height (~28px
# tall body), then nearest-neighbour upscale so the 1x legibility is provable.
NAME_TEST_PX = 28
NAME_TEST_UP = 5

MARGIN = 24
HEADER = 124
ROW_H = 330
# columns: steel ref | day-sky fried | night-sky fried | zoom | NAME-TEST @28px
CELLS = 5
CELL_W = 196
COL_W = CELL_W * CELLS
ROW_LBL = 30

sheet_w = COL_W + MARGIN * 2
sheet_h = HEADER + ROW_H * len(SETTINGS) + MARGIN * 2 + 70


def scaled(spr, sc):
    w, h = spr.get_size()
    return pygame.transform.smoothscale(spr, (round(w * sc), round(h * sc)))


def name_test_thumb(spr):
    """Downscale the fried sprite to ~NAME_TEST_PX tall (its real in-world
    size), then nearest-neighbour upscale so the helm/shield/sword reads are
    visible at print size without smoothing-blur hiding the 1x truth."""
    w, h = spr.get_size()
    sc = NAME_TEST_PX / h
    small = pygame.transform.smoothscale(spr, (max(1, round(w * sc)), NAME_TEST_PX))
    return pygame.transform.scale(
        small, (small.get_width() * NAME_TEST_UP, small.get_height() * NAME_TEST_UP))


sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill(BG)

# Header
sheet.blit(ftitle.render("FRIED KNIGHT  —  round 3  (final: landmark insets recovered)", True, INK), (MARGIN, 16))
sheet.blit(fsmall.render("HOLDS round-2 hybrid (recolor, sheen, contour, belly-glow, no-shell). NEW: darker-golden "
                         "recessed insets re-cut the helm T-slit / shield boss+edge / sword,", True, SUB), (MARGIN, 52))
sheet.blit(fsmall.render("focal-plate crackle thinned ~25% (helm face + shield boss), seam puff de-bridged ~35% "
                         "between helm-gorget and shield-chest.", True, SUB), (MARGIN, 72))
sheet.blit(fsmall.render("Per row: plain steel | fried DAY | fried NIGHT | zoom | NAME-TEST @~28px (prove helm+shield+sword). "
                         "Fried PARROT bottom-right.", True, ACC), (MARGIN, 94))


def draw_cell_bg(rect, kind):
    if kind == "day":
        day_sky(sheet, rect)
    elif kind == "night":
        night_sky(sheet, rect)
    else:
        pygame.draw.rect(sheet, (60, 68, 86), rect, border_radius=6)


for i, (name, cfg) in enumerate(SETTINGS.items()):
    y = HEADER + i * ROW_H
    panel = pygame.Rect(MARGIN, y, COL_W, ROW_H - 16)
    pygame.draw.rect(sheet, PANEL, panel, border_radius=12)
    is_ship = "SHIP" in name
    sheet.blit(font.render(name, True, GOOD if is_ship else INK),
               (panel.x + 16, panel.y + 6))

    fried = make_hybrid(cfg)
    cy = panel.y + ROW_LBL + 6
    inner_h = ROW_H - 16 - ROW_LBL - 36

    def place(spr, col, kind, caption, cap_col=SUB):
        box = pygame.Rect(panel.x + col * CELL_W + 8, cy,
                          CELL_W - 16, inner_h)
        draw_cell_bg(box, kind)
        pygame.draw.rect(sheet, (24, 28, 38), box, 2, border_radius=6)
        sx = box.x + box.w // 2 - spr.get_width() // 2
        sy = box.y + box.h // 2 - spr.get_height() // 2
        clip = sheet.get_clip()
        sheet.set_clip(box)
        sheet.blit(spr, (sx, sy))
        sheet.set_clip(clip)
        cap = fsmall.render(caption, True, cap_col)
        sheet.blit(cap, (box.x + box.w // 2 - cap.get_width() // 2, box.bottom + 6))

    place(scaled(steel_ref, GAME_SCALE), 0, "flat", "plain steel")
    place(scaled(fried, GAME_SCALE), 1, "day", "fried — day sky", ACC)
    place(scaled(fried, GAME_SCALE), 2, "night", "fried — night sky", ACC)
    place(scaled(fried, ZOOM_SCALE), 3, "flat", "zoom")
    place(name_test_thumb(fried), 4, "flat", "NAME-TEST @~28px tall", GOOD)

# ── bottom consistency strip: fried parrot next to the SHIP fried knight ─────
strip_y = HEADER + len(SETTINGS) * ROW_H + 8
strip = pygame.Rect(MARGIN, strip_y, COL_W, 60)
pygame.draw.rect(sheet, PANEL, strip, border_radius=10)
sheet.blit(fsmall.render("consistency check  —  fried parrot  vs  fried knight (1.15x ship), same fry recipe",
                         True, SUB), (strip.x + 12, strip.y + 6))
pf = scaled(fried_parrot, 1.1)
sheet.blit(pf, (strip.x + 420, strip.y + strip.h // 2 - pf.get_height() // 2))
kf = scaled(make_hybrid(SETTINGS["1.15x  (SHIP TARGET)"]), 1.0)
sheet.blit(kf, (strip.x + 540, strip.y + strip.h // 2 - kf.get_height() // 2))

out_path = os.path.join(_ROOT, "docs", "fried_knight", "round_3.png")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
