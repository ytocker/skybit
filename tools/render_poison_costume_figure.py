"""Poison final-state grid for all costume-group skins.

14 rows (all CATALOG costume-group skins) × 2 columns (Normal, Poison final).
Poison column: dead P_CHARTREUSE parrot body (X-eyes) + original accessory colours.

Run from the repo root or from tools/:
    python tools/render_poison_costume_figure.py

Output: docs/poison_costume_vN.png (auto-incremented)
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.entities import Bird  # noqa: E402
from game import parrot         # noqa: E402
from game.store_skins import (_ninja_base, _viking_base, _tophat_base,    # noqa: E402
                               _viking_back, _viking_helm, _viking_face,
                               COMPOSITE_W, COMPOSITE_H)
from game.parrot import _add_outline as _parrot_add_outline              # noqa: E402

# ── Layout constants (mirror render_poison_figure.py) ────────────────────────
LABEL_W = 130
CELL_W  = 96
CELL_H  = 120
HDR_H   = 44
MARGIN  = 10
BG      = (22, 26, 36)

SKIN_ROWS = [
    ("skin_pirate",     "Pirate"),
    ("skin_cowboy",     "Cowboy"),
    ("skin_pharaoh",    "Pharaoh"),
    ("skin_crown",      "Crown"),
    ("skin_tophat",     "Gentleman"),
    ("skin_ninja",      "Ninja"),
    ("skin_viking",     "Viking"),
    ("skin_baseball",   "Baseball"),
    ("skin_tennis",     "Tennis"),
    ("skin_wizard",     "Wizard"),
    ("skin_basketball", "Basketball"),
    ("skin_mummy",      "Mummy"),
    ("skin_astronaut",  "Astronaut"),
    ("skin_pilot",      "Captain"),
]
EFF_COLS = [
    ("Normal",         "normal"),
    ("Poison (final)", "poison"),
]

N_ROWS  = len(SKIN_ROWS)
N_COLS  = len(EFF_COLS)
GRID_W  = LABEL_W + N_COLS * CELL_W
GRID_H  = HDR_H + N_ROWS * CELL_H
TITLE_H = 28
TOTAL_W = GRID_W
TOTAL_H = MARGIN + TITLE_H + GRID_H + MARGIN


# ── Body-only frames for body-recoloring costume skins ───────────────────────

_BODY_ONLY_BASES = {
    "skin_ninja":  _ninja_base,
    "skin_viking": _viking_base,
    "skin_tophat": _tophat_base,
}
_body_only_cache = {}

def _get_body_only(skin_id):
    if skin_id not in _body_only_cache:
        comp = pygame.Surface((64, 100), pygame.SRCALPHA)
        comp.blit(_BODY_ONLY_BASES[skin_id](20), (0, 20))  # frame_idx=1 → wing_angle=20
        _body_only_cache[skin_id] = _parrot_add_outline(comp)
    return _body_only_cache[skin_id]


# ── Helpers ──────────────────────────────────────────────────────────────────

def fill_sky(surf):
    w, h = surf.get_size()
    for y in range(h):
        t = y / h
        surf.fill((
            int(80  + 20 * t),
            int(130 + 20 * t),
            int(210 - 10 * t),
        ), (0, y, w, 1))


_VK_OUTLINE = (26, 20, 16, 235)


def _viking_acc_frame():
    acc = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _viking_back(acc)
    _viking_helm(acc)
    _viking_face(acc)
    return _parrot_add_outline(acc, _VK_OUTLINE)


def _poison_costume(skin_id):
    """68×104 surface: dead P_CHARTREUSE parrot (X-eyes) + accessory pixels.

    Viking: accessories rendered on a blank canvas and composited over the
    poison parrot — no body pixels, no colour-distance ambiguity.
    Other body-recoloring skins (ninja, tophat): body-only reference frame,
    threshold 80.  Remaining skins: distance from the scarlet base macaw.
    """
    PARROT_DY = 20
    dead_frame = parrot.get_poisoned_parrot(1, 0.0)
    base_frame = parrot.get_skin_frame("skin_base", 1, 0.0)
    skin_frame = parrot.get_skin_frame(skin_id, 1, 0.0)

    if skin_id == "skin_viking":
        canvas = pygame.Surface(skin_frame.get_size(), pygame.SRCALPHA)
        canvas.blit(dead_frame, (0, PARROT_DY))
        canvas.blit(_viking_acc_frame(), (0, 0))
        return canvas

    if skin_id in _BODY_ONLY_BASES:
        ref = _get_body_only(skin_id)
        def _is_acc(x, y, sr, sg, sb):
            r0, g0, b0, _ = ref.get_at((x, y))
            return abs(sr - r0) + abs(sg - g0) + abs(sb - b0) >= 80
    else:
        def _is_acc(x, y, sr, sg, sb):
            r0, g0, b0, _ = base_frame.get_at((x, y - PARROT_DY))
            return abs(sr - r0) + abs(sg - g0) + abs(sb - b0) >= 80

    canvas = pygame.Surface(skin_frame.get_size(), pygame.SRCALPHA)
    canvas.blit(dead_frame, (0, PARROT_DY))

    fw, fh = skin_frame.get_size()
    bh = base_frame.get_height()
    for x in range(fw):
        for y in range(fh):
            by = y - PARROT_DY
            sr, sg, sb, sa = skin_frame.get_at((x, y))
            if by < 0 or by >= bh:
                if sa > 0:
                    canvas.set_at((x, y), (sr, sg, sb, sa))
            else:
                _, _, _, a0 = base_frame.get_at((x, by))
                if sa > 0 and (a0 == 0 or _is_acc(x, y, sr, sg, sb)):
                    canvas.set_at((x, y), (sr, sg, sb, sa))
    return canvas


def render_cell(skin_id, effect):
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)
    if effect == "poison":
        img = _poison_costume(skin_id)
        cell.blit(img, img.get_rect(center=(CELL_W // 2, CELL_H // 2)))
    else:
        b = Bird()
        b.frame_t       = 1.0
        b.x             = CELL_W / 2
        b.y             = 48.0
        b.equipped_skin = skin_id
        b.rebuild_skin_combos()
        b.draw(cell, 0, 0)
    return cell


# ── Canvas ───────────────────────────────────────────────────────────────────

canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill(BG)

font_title = pygame.font.SysFont("monospace", 13, bold=True)
font_hdr   = pygame.font.SysFont("monospace", 11, bold=True)
font_row   = pygame.font.SysFont("monospace", 11, bold=True)

canvas.blit(
    font_title.render("Costume skins — Poison final state (parrot body only)", True, (240, 235, 180)),
    (MARGIN, MARGIN + 6),
)

hdr_top = MARGIN + TITLE_H
for ci, (label, _) in enumerate(EFF_COLS):
    cx = LABEL_W + ci * CELL_W + CELL_W // 2
    t = font_hdr.render(label, True, (220, 220, 160))
    canvas.blit(t, t.get_rect(centerx=cx, centery=hdr_top + HDR_H // 2))

pygame.draw.line(
    canvas, (90, 100, 130),
    (LABEL_W, hdr_top + HDR_H - 1),
    (LABEL_W + N_COLS * CELL_W, hdr_top + HDR_H - 1), 1,
)

grid_top = hdr_top + HDR_H
for ri, (skin_id, row_label) in enumerate(SKIN_ROWS):
    row_y = grid_top + ri * CELL_H
    lbl = font_row.render(row_label, True, (200, 200, 200))
    canvas.blit(lbl, lbl.get_rect(midright=(LABEL_W - 6, row_y + CELL_H // 2)))
    for ci, (_, effect) in enumerate(EFF_COLS):
        cell_x = LABEL_W + ci * CELL_W
        cell = render_cell(skin_id, effect)
        canvas.blit(cell, (cell_x, row_y))
        pygame.draw.rect(canvas, (50, 55, 72), (cell_x, row_y, CELL_W, CELL_H), 1)

pygame.draw.rect(
    canvas, (90, 100, 130),
    (LABEL_W, grid_top, N_COLS * CELL_W, N_ROWS * CELL_H), 2,
)

# ── Save ─────────────────────────────────────────────────────────────────────

BRANCH = "claude/v5-item-interactions-f8eeqx"
repo   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docs   = os.path.join(repo, "docs")

import re as _re
_existing = [
    int(m.group(1))
    for f in os.listdir(docs)
    for m in [_re.search(r"poison_costume_v(\d+)\.png", f)]
    if m
]
_next = (max(_existing) + 1) if _existing else 1
FILENAME   = f"poison_costume_v{_next}.png"
GITHUB_URL = f"https://github.com/ytocker/skybit/blob/{BRANCH}/docs/{FILENAME}"

out = os.path.join(docs, FILENAME)
pygame.image.save(canvas, out)
print(f"saved {TOTAL_W}x{TOTAL_H} -> {out}")
print(f"\033]8;;{GITHUB_URL}\033\\{GITHUB_URL}\033]8;;\033\\")
