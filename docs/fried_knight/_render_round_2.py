"""Headless exploration sheet for the FRIED KNIGHT — round 2.

Round 1 led with #2 Golden Brown; the art-director asked for #2's golden-brown
base + texture with #4's grease-sheen + belly-glow LAYERED ON, tuned:

  - plump ~1.15x (not #4's 1.20x),
  - multiply nudged ~5% warmer toward amber, NOT as dark as #3 (burnt),
  - even tone across helm/shield/sword AND armour,
  - ~70 spots / ~24 crackle, DISTRIBUTED BY PLATE SIZE (denser on the big
    chest/shield plates, sparser on the small high-curvature pauldron/sword so
    detail survives at 1x),
  - #4's sheen strength but PEAK specular pulled down ~25-30% (wet soft gloss),
    highlights on UPPER-FACING surfaces, single light angle matching the fried
    parrot's upper-LEFT highlight,
  - subtle LOW-CENTRE belly glow ("juicy inside"), never an outer halo,
  - a thin 1px darker-golden contour ON the silhouette to guard the night read,
  - NO shell anywhere.

This sheet shows the hybrid at 3 plump/sheen settings (1.13x lighter sheen /
1.15x target / 1.17x richer), each beside the plain steel knight, on BOTH a
busy day sky and a night sky, with the fried PARROT in frame for consistency,
plus tight zoom crops.

Run with SDL_VIDEODRIVER=dummy. Writes docs/fried_knight/round_2.png.
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
# Each region carries a relative texture DENSITY weight: big flat plates (chest,
# shield) get the most spots; small high-curvature pieces (pauldron lames, sword
# edge, helm crown) get few so the detail doesn't dissolve into noise at 1x.
# (fx, fy, rw, rh, weight, spot_max)
_PLATE_REGIONS = [
    (0.45, 0.62, 0.50, 0.30, 2.6, 2),   # breastplate — large flat -> densest
    (0.92, 0.58, 0.36, 0.46, 2.4, 2),   # shield — large flat -> dense
    (0.45, 0.46, 0.42, 0.34, 0.7, 1),   # pauldron — small, ridged -> sparse/small
    (0.73, 0.17, 0.50, 0.54, 1.3, 2),   # helm — mid, curved crown -> medium
    (0.74, 0.50, 0.30, 0.95, 0.5, 1),   # sword — thin edge -> very sparse/small
    (0.30, 0.55, 0.40, 0.45, 1.1, 2),   # belly/body that peeks past armour
]


def _fry_texture_by_plate(out, *, total_spots, total_crackle, pad, body_rect,
                          seed=0x5C0FFEE):
    """Crispy spots + crackle distributed BY PLATE SIZE: each region gets spots
    proportional to its area*weight, scattered within its footprint, clamped to
    the silhouette so nothing spills past the edge (no shell). Small/curved
    pieces get fewer, smaller spots so they read as crisp, not noisy, at 1x."""
    w, h = out.get_size()
    tex = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(seed)

    # area*weight per region drives the spot/crackle split.
    boxes = []
    wsum = 0.0
    for fx, fy, rw, rh, weight, smax in _PLATE_REGIONS:
        # region box in the padded sprite's pixel space (centred on _P anchor).
        cx = pad + fx * body_rect[2]
        cy = pad + fy * body_rect[3]
        bw = rw * body_rect[2]
        bh = rh * body_rect[3]
        bx = cx - bw / 2
        by = cy - bh / 2
        a = bw * bh * weight
        boxes.append((bx, by, bw, bh, smax, a))
        wsum += a

    for bx, by, bw, bh, smax, a in boxes:
        n = max(1, int(round(total_spots * a / wsum)))
        for _ in range(n):
            px = int(bx + rng.random() * bw)
            py = int(by + rng.random() * bh)
            px = max(0, min(w - 1, px))
            py = max(0, min(h - 1, py))
            pygame.draw.circle(tex, _SPOT, (px, py), rng.randint(1, smax))
        nc = max(0, int(round(total_crackle * a / wsum)))
        for _ in range(nc):
            x1 = int(max(2, min(w - 12, bx + rng.random() * bw)))
            y1 = int(max(2, min(h - 12, by + rng.random() * bh)))
            dx, dy = rng.randint(5, 11), rng.randint(-5, 5)
            pygame.draw.line(tex, _DARK, (x1, y1), (x1 + dx, y1 + dy), 2)
            pygame.draw.line(tex, _LIGHT, (x1 - 1, y1 - 1), (x1 + dx - 1, y1 + dy - 1), 1)

    tex.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(tex, (0, 0))


def _sheen_upper(sprite, top_col, bot_col, top_a, bot_a):
    """Grease gloss anchored UPPER-LEFT to match the fried parrot's highlight
    (bright breast peak sits up-left of body centre). A strong soft top lobe on
    the upper-facing surfaces (top of helm / shoulder of shield / sword spine)
    and a faint lower lobe — peak pulled down from #4 so it's wet gloss, not hot
    plastic. Masked to the silhouette (on-surface, no halo)."""
    w, h = sprite.get_size()
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    # upper-left lobe (matches parrot light angle)
    pygame.draw.ellipse(ov, (*top_col, top_a),
                        (int(w * 0.10), int(-h * 0.10), int(w * 0.62), int(h * 0.60)))
    # faint lower fill
    pygame.draw.ellipse(ov, (*bot_col, bot_a),
                        (int(w * 0.12), int(h * 0.50), int(w * 0.78), int(h * 0.56)))
    ov.blit(ks._amask(sprite), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(ov, (0, 0))
    return sprite


def _belly_glow(out, alpha):
    """Subtle warm 'juicy inside' glow, LOW and CENTRED, masked to the body so it
    never rings the outside (a halo re-reads as a shell)."""
    w, h = out.get_size()
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 200, 104, alpha),
                        (int(w * 0.26), int(h * 0.50), int(w * 0.40), int(h * 0.30)))
    glow.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(glow, (0, 0))


def _contour(out, col, alpha):
    """A thin 1px darker-golden line ON the outer silhouette (NOT a ring around
    it) so the knight read survives a bright sheen on a night sky. Traces the
    alpha mask's outline and draws a 1px polyline on the perimeter pixels, so it
    sits ON the knight rather than adding a craggy ring outside it (no shell)."""
    mask = pygame.mask.from_surface(out, 40)
    line = pygame.Surface(out.get_size(), pygame.SRCALPHA)
    for comp in mask.connected_components():
        pts = comp.outline(1)
        if len(pts) >= 2:
            pygame.draw.lines(line, (*col, alpha), True, pts, 1)
    # clamp to the silhouette so the closing segments never cut across a gap
    # outside the body.
    line.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(line, (0, 0))


# ── THE HYBRID deep-fry (this is the canonical candidate to wire into _deep_fry)
def hybrid_fry(frame, *, mult, add, spots, crackle, sheen_top, sheen_bot,
               top_a, bot_a, belly_a, contour_col, contour_a):
    """#2 golden-brown recolor + plate-distributed texture + #4's sheen/belly
    glow layered on, tuned per the round-2 directives. NO shell."""
    out = ks._recolor(frame, mult, add=add)
    # body rect = the un-padded base frame, centred in the padded sprite.
    bw, bh = parrot._get_frames()[0].get_size()
    pad = ks._PAD
    body_rect = (pad, pad, bw, bh)
    _fry_texture_by_plate(out, total_spots=spots, total_crackle=crackle,
                          pad=pad, body_rect=body_rect)
    _belly_glow(out, belly_a)
    _sheen_upper(out, sheen_top, sheen_bot, top_a, bot_a)
    _contour(out, contour_col, contour_a)
    return out


def _plump(frame, scale):
    w, h = frame.get_size()
    return pygame.transform.smoothscale(frame, (round(w * scale), round(h * scale)))


# ── three tuned settings (lighter sheen / target / richer) ───────────────────
# Shared golden-brown floor: #2's mult, add nudged ~5% warmer toward amber
# (more red/green relative to blue) and NOT as dark as #3.
_BASE_MULT = (214, 142, 46)          # ~5% warmer/amber vs #2's (210,138,42)
_BASE_ADD = (44, 22, 2)              # #2's add, hair warmer
_SPOTS = 70
_CRACKLE = 24
_CONTOUR = (150, 92, 28)             # darker golden, on-silhouette
_CONTOUR_A = 150

SETTINGS = {
    # peak specular pulled ~25-30% under #4 (#4 was top_a=104/bot_a=60).
    "1.13x  (lighter sheen)": dict(
        mult=_BASE_MULT, add=_BASE_ADD, spots=_SPOTS, crackle=_CRACKLE,
        sheen_top=(255, 240, 184), sheen_bot=(244, 198, 112),
        top_a=66, bot_a=42, belly_a=46,
        contour_col=_CONTOUR, contour_a=_CONTOUR_A, plump=1.13),
    "1.15x  (TARGET)": dict(
        mult=_BASE_MULT, add=_BASE_ADD, spots=_SPOTS, crackle=_CRACKLE,
        sheen_top=(255, 240, 188), sheen_bot=(244, 200, 116),
        top_a=74, bot_a=46, belly_a=54,
        contour_col=_CONTOUR, contour_a=_CONTOUR_A, plump=1.15),
    "1.17x  (richer)": dict(
        mult=_BASE_MULT, add=_BASE_ADD, spots=_SPOTS, crackle=_CRACKLE,
        sheen_top=(255, 242, 192), sheen_bot=(246, 202, 120),
        top_a=80, bot_a=50, belly_a=62,
        contour_col=_CONTOUR, contour_a=_CONTOUR_A, plump=1.17),
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


# ── sky backdrops (busy day + night) so the 1x read is tested on both ────────
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

_FONT = os.path.join(_ROOT, "game", "assets", "LiberationSans-Bold.ttf")
font = pygame.font.Font(_FONT, 22)
fsmall = pygame.font.Font(_FONT, 15)
ftitle = pygame.font.Font(_FONT, 30)

GAME_SCALE = 1.7
ZOOM_SCALE = 3.6

MARGIN = 24
HEADER = 116
ROW_H = 320
# columns: steel ref | day-sky fried | night-sky fried | zoom
CELLS = 4
CELL_W = 200
COL_W = CELL_W * CELLS
ROW_LBL = 30

sheet_w = COL_W + MARGIN * 2
sheet_h = HEADER + ROW_H * len(SETTINGS) + MARGIN * 2 + 70   # +70 for parrot strip


def scaled(spr, sc):
    w, h = spr.get_size()
    return pygame.transform.smoothscale(spr, (round(w * sc), round(h * sc)))


sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill(BG)

# Header
sheet.blit(ftitle.render("FRIED KNIGHT  —  round 2  (hybrid: #2 base + #4 sheen/belly)", True, INK), (MARGIN, 18))
sheet.blit(fsmall.render("#2 golden-brown recolor + plate-distributed texture, #4 grease-sheen "
                         "(peak -28%) + low belly-glow layered on. Even tone, no shell.",
                         True, SUB), (MARGIN, 54))
sheet.blit(fsmall.render("Per row: plain steel  |  fried on busy DAY sky  |  fried on NIGHT sky  |  zoom. "
                         "Fried PARROT bottom-right for consistency.",
                         True, SUB), (MARGIN, 76))


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
    sheet.blit(font.render(name, True, ACC if "TARGET" in name else INK),
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

# ── bottom consistency strip: fried parrot next to the TARGET fried knight ───
strip_y = HEADER + len(SETTINGS) * ROW_H + 8
strip = pygame.Rect(MARGIN, strip_y, COL_W, 60)
pygame.draw.rect(sheet, PANEL, strip, border_radius=10)
sheet.blit(fsmall.render("consistency check  —  fried parrot  vs  fried knight (target), same fry recipe",
                         True, SUB), (strip.x + 12, strip.y + 6))
pf = scaled(fried_parrot, 1.1)
sheet.blit(pf, (strip.x + 360, strip.y + strip.h // 2 - pf.get_height() // 2))
kf = scaled(make_hybrid(SETTINGS["1.15x  (TARGET)"]), 1.0)
sheet.blit(kf, (strip.x + 460, strip.y + strip.h // 2 - kf.get_height() // 2))

out_path = os.path.join(_ROOT, "docs", "fried_knight", "round_2.png")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
