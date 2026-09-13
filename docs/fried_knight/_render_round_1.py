"""Headless exploration sheet for the FRIED KNIGHT (KNIGHT + KFC).

Five deep-fry treatments of the steel knight, each shown at gameplay scale
DIRECTLY BESIDE the plain steel knight (same scale) for a before/after read,
plus a tight zoom. All obey the no-shell constraint: the crisp is ON the
knight (recolor + surface texture), never a separate craggy crust ring.

Run with SDL_VIDEODRIVER=dummy. Writes docs/fried_knight/round_1.png.
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


# ── reusable fry primitives (mirrors knight_skin._deep_fry, parameterised) ───
def _fry_texture(out, *, spots, crackle, spot_max, seed=0x5C0FFEE):
    """Crispy spots + crackle (dark valley + light ridge), clamped to the
    silhouette so nothing spills past the knight's edge (no shell)."""
    w, h = out.get_size()
    tex = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(seed)
    for _ in range(spots):
        pygame.draw.circle(tex, _SPOT,
                           (rng.randint(0, w - 1), rng.randint(0, h - 1)),
                           rng.randint(1, spot_max))
    for _ in range(crackle):
        x1, y1 = rng.randint(2, w - 12), rng.randint(2, h - 12)
        dx, dy = rng.randint(5, 11), rng.randint(-5, 5)
        pygame.draw.line(tex, _DARK, (x1, y1), (x1 + dx, y1 + dy), 2)
        pygame.draw.line(tex, _LIGHT, (x1 - 1, y1 - 1), (x1 + dx - 1, y1 + dy - 1), 1)
    tex.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(tex, (0, 0))


def _plump(frame, scale):
    w, h = frame.get_size()
    return pygame.transform.smoothscale(frame, (round(w * scale), round(h * scale)))


# ── candidate 1: LITE CRISP ──────────────────────────────────────────────────
# Gentle golden glaze, sparse spots, soft sheen, modest plump. Armour stays
# the most metallic-readable of the set; "lightly fried".
def fry_lite(frame):
    out = ks._recolor(frame, _GOLD, add=(60, 36, 14))   # paler, less saturated
    _fry_texture(out, spots=34, crackle=12, spot_max=2)
    ks._sheen(out, (255, 236, 172), (242, 196, 110), top_a=74, bot_a=46)
    return out


# ── candidate 2: GOLDEN BROWN (canonical KFC) ────────────────────────────────
# Matches the fried-parrot recipe richness: rich golden-brown batter, medium
# texture, juicy gloss. The honest "deep-fried the same way" baseline.
def fry_golden(frame):
    out = ks._recolor(frame, _GOLD, add=(44, 20, 2))
    _fry_texture(out, spots=70, crackle=24, spot_max=2)
    ks._sheen(out, (255, 232, 160), (238, 186, 96), top_a=64, bot_a=40)
    return out


# ── candidate 3: EXTRA CRISPY ────────────────────────────────────────────────
# Darkest/richest batter, dense spots + heavy crackle, biggest plump. Maximally
# crunchy, deep-brown ridges, well-done.
def fry_extra(frame):
    out = ks._recolor(frame, (196, 124, 36), add=(32, 12, 0))   # deeper batter
    _fry_texture(out, spots=104, crackle=34, spot_max=3)
    ks._sheen(out, (255, 224, 148), (224, 168, 80), top_a=56, bot_a=34)
    return out


# ── candidate 4: JUICY GLAZE ─────────────────────────────────────────────────
# Medium batter, lighter texture but the wettest, most appetizing finish: a
# strong high grease sheen + a warm belly glow ellipse. Plumpest-looking via a
# big sheen rather than heavy spotting.
def fry_juicy(frame):
    out = ks._recolor(frame, _GOLD, add=(50, 26, 6))
    _fry_texture(out, spots=46, crackle=16, spot_max=2)
    # warm belly glow — masked to silhouette, lower-centre warmth like the
    # fried parrot's belly ellipse, kept inside the body (no halo/shell).
    w, h = out.get_size()
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 206, 110, 70),
                        (int(w * 0.22), int(h * 0.46), int(w * 0.46), int(h * 0.34)))
    glow.blit(ks._amask(out), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(glow, (0, 0))
    ks._sheen(out, (255, 244, 196), (246, 200, 116), top_a=104, bot_a=60)
    return out


# ── candidate 5: STEEL & CRUST ───────────────────────────────────────────────
# Body-focused fry: the parrot body gets fully deep-fried, but the steel armour
# + heraldry are rebuilt on top with only a warm golden glaze (not a full
# recolor), so the helm/shield/sword stay clearly steel and the knight reads
# strongest. Same plump.
def build_steel_crust_frame(base_frame):
    # Fry the bare parrot body first (canonical recipe), then armour it raw so
    # the steel pieces keep their metallic palette.
    fried_body = fry_golden(ks._recolor(base_frame, _GOLD, add=(44, 20, 2)))
    # Re-fry would double-recolor; instead deep-fry the plain parrot body once.
    char = ks._build_knight_frame(base_frame, body_recolor=False, _prebuilt_body=fried_body) \
        if "_prebuilt_body" in ks._build_knight_frame.__code__.co_varnames else None
    return char


# _build_knight_frame has no prebuilt-body hook, so replicate its compositing
# here for candidate 5 (fried body + raw steel armour + a thin warm glaze).
def steel_crust(base_frame):
    bw, bh = base_frame.get_size()
    char = pygame.Surface((bw + 2 * ks._PAD, bh + 2 * ks._PAD), pygame.SRCALPHA)
    nom = base_frame.get_rect(center=(char.get_width() // 2, char.get_height() // 2))
    # Body: deep-fried parrot skin (belly/tail that peek past the armour are crispy).
    body = ks._recolor(base_frame, _GOLD, add=(44, 20, 2))
    _fry_texture(body, spots=70, crackle=24, spot_max=2)
    ks._sheen(body, (255, 232, 160), (238, 186, 96), top_a=64, bot_a=40)
    char.blit(body, nom.topleft)
    # Steel armour on top, unmodified metal.
    ks._blit_ss(char, *ks._P(nom, 0.45, 0.62), int(nom.w * 0.5), int(nom.h * 0.30), ks._breast)
    sfx, sfy, swf, shf = ks._SHIELD_POS
    ks._blit_ss(char, *ks._P(nom, sfx, sfy), int(nom.w * swf), int(nom.h * shf), ks._shield)
    ks._blit_ss(char, *ks._P(nom, 0.45, 0.46), int(nom.w * 0.42), int(nom.h * 0.34), ks._pauldron, scale=6)
    ks._blit_ss(char, *ks._P(nom, 0.73, 0.17), int(nom.w * 0.5), int(nom.h * 0.54), ks._helm, scale=6)
    ks._blit_ss(char, *ks._P(nom, 0.74, 0.5), int(nom.w * 0.5), int(nom.h * 0.95), ks._sword)
    # Thin warm golden glaze over the WHOLE knight (a fried-oil sheen on the
    # steel — appetizing without erasing the metal). Masked to silhouette.
    w, h = char.get_size()
    glaze = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(glaze, (255, 206, 96, 40), (int(w * 0.12), int(-h * 0.08), int(w * 0.7), int(h * 0.7)))
    pygame.draw.ellipse(glaze, (210, 150, 60, 30), (int(w * 0.08), int(h * 0.5), int(w * 0.84), int(h * 0.58)))
    glaze.blit(ks._amask(char), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    char.blit(glaze, (0, 0))
    return char


# ── build all candidate frame-sets (frame index 2 = level wing, best read) ────
FRAME_IDX = 2
base_frames = parrot._get_frames()
plain_knight = ks.build_knight_frames()              # steel reference

CANDIDATES = [
    ("1  Lite Crisp",   lambda: _plump(fry_lite(ks.build_knight_frames()[FRAME_IDX]), 1.10)),
    ("2  Golden Brown", lambda: _plump(fry_golden(ks.build_knight_frames()[FRAME_IDX]), 1.15)),
    ("3  Extra Crispy", lambda: _plump(fry_extra(ks.build_knight_frames()[FRAME_IDX]), 1.18)),
    ("4  Juicy Glaze",  lambda: _plump(fry_juicy(ks.build_knight_frames()[FRAME_IDX]), 1.20)),
    ("5  Steel+Crust",  lambda: _plump(steel_crust(base_frames[FRAME_IDX]), 1.14)),
]

steel_ref = plain_knight[FRAME_IDX]


# ── sheet layout ─────────────────────────────────────────────────────────────
BG = (40, 46, 60)
PANEL = (52, 60, 78)
INK = (236, 242, 255)
SUB = (176, 186, 206)

_FONT = os.path.join(_ROOT, "game", "assets", "LiberationSans-Bold.ttf")
font = pygame.font.Font(_FONT, 22)
fsmall = pygame.font.Font(_FONT, 16)
ftitle = pygame.font.Font(_FONT, 30)

GAME_SCALE = 1.6      # gameplay-ish display size for the side-by-side pair
ZOOM_SCALE = 3.4      # tight zoom of the fried knight

COL_W = 600
ROW_H = 300
MARGIN = 24
HEADER = 90

sheet_w = COL_W + MARGIN * 2
sheet_h = HEADER + ROW_H * len(CANDIDATES) + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill(BG)

# Header
t = ftitle.render("FRIED KNIGHT  —  round 1", True, INK)
sheet.blit(t, (MARGIN, 20))
s = fsmall.render("Deep-fry the steel knight the same way the parrot is fried. "
                  "Plain steel (left) vs fried (mid) vs zoom (right). No shell.",
                  True, SUB)
sheet.blit(s, (MARGIN, 58))


def scaled(spr, sc):
    w, h = spr.get_size()
    return pygame.transform.smoothscale(spr, (round(w * sc), round(h * sc)))


def checker(surf, rect, c1, c2, n=16):
    cw = rect.w // n
    for j in range((rect.h // cw) + 1):
        for i in range(n):
            col = c1 if (i + j) % 2 == 0 else c2
            pygame.draw.rect(surf, col, (rect.x + i * cw, rect.y + j * cw, cw, cw))


for i, (name, make) in enumerate(CANDIDATES):
    y = HEADER + i * ROW_H
    panel = pygame.Rect(MARGIN, y, COL_W, ROW_H - 16)
    pygame.draw.rect(sheet, PANEL, panel, border_radius=12)

    fried = make()

    # three cells: plain steel | fried (same scale) | zoom
    cell_w = COL_W // 3
    cy = panel.y + 30

    # label
    lab = font.render(name, True, INK)
    sheet.blit(lab, (panel.x + 16, panel.y + 6))

    # cell A — plain steel knight at game scale
    a = scaled(steel_ref, GAME_SCALE)
    ax = panel.x + cell_w // 2 - a.get_width() // 2
    ay = cy + (ROW_H - 60) // 2 - a.get_height() // 2
    sheet.blit(a, (ax, ay))
    cap = fsmall.render("plain steel", True, SUB)
    sheet.blit(cap, (panel.x + cell_w // 2 - cap.get_width() // 2, panel.bottom - 26))

    # cell B — fried at the SAME game scale (before/after read)
    b = scaled(fried, GAME_SCALE)
    bx = panel.x + cell_w + cell_w // 2 - b.get_width() // 2
    by = cy + (ROW_H - 60) // 2 - b.get_height() // 2
    sheet.blit(b, (bx, by))
    cap = fsmall.render("fried (same scale)", True, (255, 214, 132))
    sheet.blit(cap, (panel.x + cell_w + cell_w // 2 - cap.get_width() // 2, panel.bottom - 26))

    # cell C — tight zoom of the fried knight on a soft checker
    z = scaled(fried, ZOOM_SCALE)
    zbox = pygame.Rect(panel.x + 2 * cell_w + 12, cy - 6, cell_w - 24, ROW_H - 60)
    prev = sheet.subsurface(zbox).copy() if False else None
    checker(sheet, zbox, (60, 68, 86), (50, 58, 74))
    zx = zbox.x + zbox.w // 2 - z.get_width() // 2
    zy = zbox.y + zbox.h // 2 - z.get_height() // 2
    # clip zoom blit to the box
    clip = sheet.get_clip()
    sheet.set_clip(zbox)
    sheet.blit(z, (zx, zy))
    sheet.set_clip(clip)
    pygame.draw.rect(sheet, (24, 28, 38), zbox, 2, border_radius=6)
    cap = fsmall.render("zoom", True, SUB)
    sheet.blit(cap, (zbox.x + zbox.w // 2 - cap.get_width() // 2, panel.bottom - 26))

out_path = os.path.join(_ROOT, "docs", "fried_knight", "round_1.png")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
