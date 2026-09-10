"""Combined showcase of all 10 round-3 pillar finals (temple-mills + totems).

One at-a-glance figure: two labeled rows (TEMPLE-MILLS, JAPANESE TOTEMS), five
cells each, every cell baked IDENTICALLY (same MARGIN gutters, same tall daytime
gap, same crop) so the finals compare fairly as upright hero towers over a
daytime sky.

Each concept lives in its own standalone render.py with a `candidate_*` fn of
the shipped `(surf, top_rect, bot_rect, palette, seed)` shape. The temple-mill
slug dirs use hyphens, so every module is loaded by FILE PATH via importlib and
only its own candidate fn is reused — nothing is re-implemented here.

Run:  python docs/pillar_landmarks/render_showcase_v3.py
Out:  docs/pillar_landmarks/showcase_v3.png
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, PIPE_W
from game import biome

# ── identical bake geometry for every cell (mirrors render_pagoda_comparison) ──
MARGIN = 64                        # eave/ornament gutter, matches entities.Pipe
CACHE_W = PIPE_W + MARGIN * 2      # captures sideways overhang
CACHE_H = GROUND_Y
PHASE = 0.30                       # daytime so every body reads clearly

# Tall gap so the full upright tower shows top finial → plinth in one crop.
GAP_Y, GAP_H = 130, 130
BOT_TOP = int(GAP_Y + GAP_H / 2)
TIP_Y = BOT_TOP - 10               # a little sky headroom above the finial
BASE_Y = GROUND_Y + 8              # a hair of ground below the plinth
TOWER_H = BASE_Y - TIP_Y

# (slug, render.py subpath, candidate fn name, one-line thesis, is_seed)
# Each row leads with the ORIGINAL design (is_seed=True) the family was seeded
# from — badged "SEED", not numbered — so the 10 finals still read #1..#10.
TEMPLE_MILLS = [
    ("waterwheel-mill", "windmills/waterwheel-mill/render.py",
     "candidate_waterwheel_mill",
     "original — brick cone + water-wheel", True),
    ("vane-star-mill", "temple_mills/vane-star-mill/render.py",
     "candidate_vane_star_mill",
     "brick ziggurat + gilded pinwheel star"),
    ("sail-fan-mill", "temple_mills/sail-fan-mill/render.py",
     "candidate_sail_fan_mill",
     "brick cone + scalloped canvas sail-fan"),
    ("phoenix-vane-mill", "temple_mills/phoenix-vane-mill/render.py",
     "candidate_phoenix_vane_mill",
     "brick spire + gilt phoenix weathervane"),
    ("parasol-crown-mill", "temple_mills/parasol-crown-mill/render.py",
     "candidate_parasol_crown_mill",
     "brick pedestal + spinning lacquer parasol"),
    ("streamer-whirl-mill", "temple_mills/streamer-whirl-mill/render.py",
     "candidate_streamer_whirl_mill",
     "brick pavilion + prayer-streamer whirl"),
]
JAPANESE_TOTEMS = [
    ("moai_ancestor", "totems/moai_ancestor/render.py",
     "candidate_moai_ancestor",
     "original — gaunt basalt ancestor heads", True),
    ("oni_kanabo", "japanese_totems/oni_kanabo/render.py",
     "candidate_oni_kanabo",
     "stacked Oni demon masks, iron horns"),
    ("tengu_yamabushi", "japanese_totems/tengu_yamabushi/render.py",
     "candidate_tengu_yamabushi",
     "stacked long-nosed Tengu masks"),
    ("kitsune_inari", "japanese_totems/kitsune_inari/render.py",
     "candidate_kitsune_inari",
     "stacked white fox masks"),
    ("kappa_suijin", "japanese_totems/kappa_suijin/render.py",
     "candidate_kappa_suijin",
     "stacked kappa water-imp masks"),
    ("daruma_gankake", "japanese_totems/daruma_gankake/render.py",
     "candidate_daruma_gankake",
     "stacked lacquer Daruma dolls"),
]
FAR_EAST_LANDMARKS = [
    ("oriental_pearl", "far_east_landmarks/oriental_pearl/render.py",
     "candidate_oriental_pearl",
     "Oriental Pearl — pearls on a tripod spire"),
    ("petronas_twins", "far_east_landmarks/petronas_twins/render.py",
     "candidate_petronas_twins",
     "Petronas Towers — twin shafts + skybridge"),
    ("marina_bay_boat", "far_east_landmarks/marina_bay_boat/render.py",
     "candidate_marina_bay_boat",
     "Marina Bay Sands — boat deck on legs"),
    ("himeji_heron", "far_east_landmarks/himeji_heron/render.py",
     "candidate_himeji_heron",
     "Himeji — white heron castle keep"),
    ("potala_fortress", "far_east_landmarks/potala_fortress/render.py",
     "candidate_potala_fortress",
     "Potala Palace — red-and-white fortress"),
    ("angkor_lotus", "far_east_landmarks/angkor_lotus/render.py",
     "candidate_angkor_lotus",
     "Angkor Wat — lotus-bud sanctuary tower"),
]

# Colorway rows: same geometry, palette-swapped. Entry[4] is an explicit badge
# tag (a string) → drawn as a muted grey chip, NOT numbered. The base cell tags
# its showcase number (#14 / #16); the recolors tag their colour word.
_HIM = "far_east_landmarks/himeji_heron/render.py"
HIMEJI_COLORWAYS = [
    ("himeji-white", _HIM, "candidate_himeji_heron", "original White Heron", "#14"),
    ("himeji-crow", _HIM, "candidate_himeji_crow", "black lacquer (Matsumoto)", "black"),
    ("himeji-vermilion", _HIM, "candidate_himeji_vermilion", "shrine-red lacquer", "red"),
    ("himeji-gilt", _HIM, "candidate_himeji_gilt", "gold leaf (Kinkaku)", "gold"),
    ("himeji-azure", _HIM, "candidate_himeji_azure", "blue celadon tile", "blue"),
    ("himeji-sakura", _HIM, "candidate_himeji_sakura", "cherry-blossom pink", "pink"),
]
_ANG = "far_east_landmarks/angkor_lotus/render.py"
ANGKOR_COLORWAYS = [
    ("angkor-sandstone", _ANG, "candidate_angkor_lotus", "original grey-gold sandstone", "#16"),
    ("angkor-rose", _ANG, "candidate_angkor_rose", "rose sandstone (Banteay Srei)", "rose"),
    ("angkor-basalt", _ANG, "candidate_angkor_basalt", "near-black basalt", "basalt"),
    ("angkor-jade", _ANG, "candidate_angkor_jade", "jungle jade-green", "jade"),
    ("angkor-gilt", _ANG, "candidate_angkor_gilt", "gold-leaf prasat", "gilt"),
    ("angkor-sunset", _ANG, "candidate_angkor_sunset", "laterite sunset red", "sunset"),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _load_candidate(subpath: str, fn_name: str, slug: str):
    """Load one concept's render.py by FILE PATH (slugs contain hyphens, so a
    package import won't do) and return only its own candidate fn."""
    path = _HERE / subpath
    mod_name = "concept_" + slug.replace("-", "_")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, fn_name)


def bake_tower(fn, seed: int) -> pygame.Surface:
    """Bake one concept's full pillar pair, crop the upright ground tower.

    Identical geometry for every concept so the finals compare fairly."""
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    palette = biome.palette_for_phase(PHASE)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, int(GAP_Y - GAP_H / 2))
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    fn(surf, top_rect, bot_rect, palette, seed)
    tower = pygame.Surface((CACHE_W, TOWER_H), pygame.SRCALPHA)
    tower.blit(surf, (0, 0), pygame.Rect(0, TIP_Y, CACHE_W, TOWER_H))
    return tower


def cell_background(w: int, h: int, pal) -> pygame.Surface:
    """Daytime sky gradient with a thin ground band at the tower's base."""
    cell = pygame.Surface((w, h))
    sky_h = h - 14
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal["sky_top"], pal["horizon"], t), (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal["ground_top"], pal["ground_mid"], t),
                         (0, y), (w, y))
    return cell


def _wrap(font, text, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if font.size(trial)[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _painted_pixels(tower: pygame.Surface) -> int:
    """Count non-transparent pixels — proves a tower actually painted in a cell."""
    n = 0
    w, h = tower.get_width(), tower.get_height()
    for x in range(w):
        for y in range(h):
            if tower.get_at((x, y))[3] > 0:
                n += 1
    return n


def main() -> None:
    pal = biome.palette_for_phase(PHASE)

    cw, ch = CACHE_W, TOWER_H
    cols = 6                            # leading SEED cell + 5 finals per row
    pad = 12
    thesis_font = pygame.font.SysFont(None, 16)
    slug_font = pygame.font.SysFont(None, 20)
    thesis_lines_max = 2
    thesis_line_h = thesis_font.get_height()
    caption_h = 22 + thesis_lines_max * thesis_line_h  # slug + up to 2 thesis lines

    head_h = 56
    row_header_h = 30
    cell_block_h = ch + caption_h
    rows = [("TEMPLE-MILLS", TEMPLE_MILLS),
            ("JAPANESE TOTEMS", JAPANESE_TOTEMS),
            ("FAR-EAST LANDMARKS", FAR_EAST_LANDMARKS),
            ("#14 HIMEJI — COLORWAYS", HIMEJI_COLORWAYS),
            ("#16 ANGKOR — COLORWAYS", ANGKOR_COLORWAYS)]
    sheet_w = pad + cols * (cw + pad)
    sheet_h = (head_h + pad
               + (row_header_h + cell_block_h + pad) * len(rows))
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    title = pygame.font.SysFont(None, 32)
    sub = pygame.font.SysFont(None, 19)
    row_font = pygame.font.SysFont(None, 26, bold=True)
    serial = pygame.font.SysFont(None, 24, bold=True)

    sheet.blit(title.render(
        "Skybit — temple-mills + totems + Far-East landmarks",
        True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render(
        "16 finals (#1-16) + 2 seed originals + colorway rows for #14 Himeji & "
        "#16 Angkor  ·  identical daytime bake (phase 0.30)",
        True, (170, 172, 182)), (pad, 38))

    counts = {}
    final_n = 0                        # running #N for finals only (seeds excluded)
    y_row = head_h + pad
    for row_label, concepts in rows:
        sheet.blit(row_font.render(row_label, True, (255, 224, 150)), (pad, y_row + 4))
        y_cells = y_row + row_header_h
        for c, entry in enumerate(concepts):
            slug, subpath, fn_name, thesis = entry[:4]
            tag = entry[4] if len(entry) > 4 else None
            fn = _load_candidate(subpath, fn_name, slug)
            if tag is None:                       # a numbered final
                final_n += 1
                badge_text, seed, muted = f"#{final_n}", 13 + final_n, False
            elif tag is True:                     # a SEED original
                badge_text, seed, muted = "SEED", 13, True
            else:                                 # explicit chip: #14/#16 ref or colour
                badge_text, seed, muted = str(tag), 13, True
            tower = bake_tower(fn, seed=seed)
            counts[slug] = _painted_pixels(tower)

            x = pad + c * (cw + pad)
            cell = cell_background(cw, ch, pal)
            cell.blit(tower, (0, 0))
            sheet.blit(cell, (x, y_cells))
            pygame.draw.rect(sheet, (60, 62, 72), (x, y_cells, cw, ch), 1)

            # Badge, top-left: gold "#N" for finals, muted grey "SEED" for originals.
            fg = (232, 234, 240) if muted else (24, 25, 30)
            bg = (86, 90, 102) if muted else (255, 224, 150)
            num = serial.render(badge_text, True, fg)
            bw, bh = num.get_width() + 12, num.get_height() + 6
            badge = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(badge, bg, badge.get_rect(), border_radius=6)
            badge.blit(num, (6, 3))
            sheet.blit(badge, (x + 4, y_cells + 4))

            # Caption: slug then wrapped thesis, below the tower.
            cy = y_cells + ch + 3
            sheet.blit(slug_font.render(slug, True, (255, 224, 150)), (x + 2, cy))
            ty = cy + 20
            for line in _wrap(thesis_font, thesis, cw - 4)[:thesis_lines_max]:
                sheet.blit(thesis_font.render(line, True, (196, 198, 208)), (x + 2, ty))
                ty += thesis_line_h
        y_row = y_cells + cell_block_h + pad

    out = _HERE / "showcase_v3.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print("per-cell painted-pixel counts:")
    for i, (slug, n) in enumerate(counts.items(), 1):
        print(f"  #{i:2d} {slug:20s} {n:6d} px  [{'OK' if n > 500 else 'EMPTY'}]")


if __name__ == "__main__":
    main()
