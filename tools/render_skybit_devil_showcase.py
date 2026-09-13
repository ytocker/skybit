"""Assemble the Skybit DEVIL roster into ONE matched-scale sheet.

Composition only — every figure is pulled from its OWN final renderer module so
each character's settled design, palette, and proportions are preserved exactly;
nothing here re-draws or re-styles a devil. Big Reapy anchors the top as the
original; the five "more devilish" Big Reapy reinterpretations follow on row 1,
and the five house-style Skybit devils on row 2.

Each figure renders on its own native canvas, auto-cropped to its tight opaque
bbox, then scaled so every figure stands at ONE matched reference height on a
SHARED per-row ground line. Matching by full opaque bbox keeps a prop-heavy
take (Twinface's pole, Pyrecrown's candle crown) from rendering huge and a squat
take from rendering tiny — the playful chibi mass differences survive, but no
figure is mis-sized by a differing internal canvas or clipped by its tall props.
Run headless:

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python \
        tools/render_skybit_devil_showcase.py
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

# The original anchor + each devil straight from its final renderer.
from tools.render_skybit_reaper_big_reapy import build_big_reapy
from tools.render_skybit_devil_brimstone import build_brimstone
from tools.render_skybit_devil_clovenpate import build_clovenpate
from tools.render_skybit_devil_twinface import render_boss as twinface_render_boss
from tools.render_skybit_devil_soulforge import build_soulforge
from tools.render_skybit_devil_pyrecrown import build_pyrecrown
from tools.render_skybit_devil_lil_nick import build_lil_nick
from tools.render_skybit_devil_ao_oni import build_ao_oni
from tools.render_skybit_devil_baalgoat import build_baalgoat
from tools.render_skybit_devil_glitchfiend import build_glitchfiend
from tools.render_skybit_devil_implet import build_implet


# Neutral studio panel — a soft cool-grey gradient so every palette reads true.
BG_TOP = (212, 218, 228)
BG_BOT = (180, 188, 200)
GROUND = (150, 158, 170)
LABEL = (28, 24, 34)
HEADER = (60, 30, 40)


def _crop(surf):
    """Tight crop to the opaque bbox so canvas padding never skews the matched-
    scale normalization (some renderers pad generously for tall props)."""
    rect = surf.get_bounding_rect(min_alpha=8)
    if rect.width == 0 or rect.height == 0:
        rect = surf.get_rect()
    out = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    out.blit(surf, (0, 0), rect)
    return out


# ── per-figure loaders ───────────────────────────────────────────────────────
# Most renderers expose build_<slug>(scale, ss) -> (surface, feet_y); we keep
# only the surface and re-derive the seat from the cropped opaque bbox. Two
# differ: build_implet returns a bare surface, and Twinface exposes render_boss
# (out_h, ss) instead of a scale-based builder. All three resolve to a cropped
# RGBA surface here.

def _from_build(build_fn):
    """build_<slug>(scale, ss) returning (surface, feet_y) — keep the surface."""
    res = build_fn(scale=1.0, ss=3)
    surf = res[0] if isinstance(res, tuple) else res
    return _crop(surf)


def _from_surface(build_fn):
    """A builder that returns a bare surface (no feet_y)."""
    return _crop(build_fn(scale=1.0, ss=3))


def _twinface_figure():
    # Twinface has no scale-based builder; render_boss takes a target height.
    return _crop(twinface_render_boss(300, 3, wink=True))


def _bg_panel(w, h):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        surf.fill((int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t),
                   int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t),
                   int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)),
                  (0, y, w, 1))
    return surf


# ── layout constants ─────────────────────────────────────────────────────────
REF_H = 280          # matched reference height for every figure's opaque bbox
PAD = 44             # outer margin
COL_GAP = 28         # gap between columns
TITLE_H = 70
HEADER_H = 34        # per-row header label band
LABEL_H = 34         # per-figure name band
GROUND_PAD = 26      # gap between ground line and name label
ROW_GAP = 30         # gap between a row's label band and the next row's header
TOP_MARGIN = 24      # headroom above each row's figures so tall props don't clip


def _normalize(fig):
    scale = REF_H / fig.get_height()
    nw = max(1, int(fig.get_width() * scale))
    nh = max(1, int(fig.get_height() * scale))
    return pygame.transform.smoothscale(fig, (nw, nh))


def main():
    pygame.init()
    pygame.font.init()

    rows = [
        ("ORIGINAL — BIG REAPY", [
            ("BIG REAPY", _from_build(build_big_reapy)),
        ]),
        ("MORE DEVILISH (Big Reapy reinterpreted)", [
            ("BRIMSTONE", _from_build(build_brimstone)),
            ("CLOVENPATE", _from_build(build_clovenpate)),
            ("TWINFACE", _twinface_figure()),
            ("SOULFORGE", _from_build(build_soulforge)),
            ("PYRECROWN", _from_build(build_pyrecrown)),
        ]),
        ("DEVIL — Skybit style", [
            ("LIL NICK", _from_build(build_lil_nick)),
            ("AO-ONI", _from_build(build_ao_oni)),
            ("BAALGOAT", _from_build(build_baalgoat)),
            ("GLITCHFIEND", _from_build(build_glitchfiend)),
            ("IMPLET", _from_surface(build_implet)),
        ]),
    ]

    # Matched scale: normalize every figure's opaque height to REF_H.
    rows = [(hdr, [(lbl, _normalize(fig)) for lbl, fig in cells])
            for hdr, cells in rows]

    # Column metric is the widest figure across ALL rows so columns align and
    # every figure sits at the same matched scale on its row's ground line.
    fig_max_w = max(f.get_width() for _, cells in rows for _, f in cells)
    col_w = fig_max_w + COL_GAP
    max_cols = max(len(cells) for _, cells in rows)
    panel_w = PAD * 2 + col_w * max_cols

    # One stacked block per row: header band, figure band (TOP_MARGIN + REF_H),
    # ground line, name band.
    row_block_h = HEADER_H + TOP_MARGIN + REF_H + GROUND_PAD + LABEL_H
    panel_h = TITLE_H + PAD + len(rows) * row_block_h + (len(rows) - 1) * ROW_GAP + PAD

    sheet = _bg_panel(panel_w, panel_h)

    # Title strip.
    title_band = pygame.Surface((panel_w, TITLE_H), pygame.SRCALPHA)
    title_band.fill((26, 18, 24, 238))
    sheet.blit(title_band, (0, 0))
    tfont = pygame.font.SysFont("dejavusans", 32, bold=True)
    title = tfont.render("SKYBIT — DEVIL ROSTER", True, (250, 226, 220))
    sheet.blit(title, ((panel_w - title.get_width()) // 2,
                       (TITLE_H - title.get_height()) // 2))

    hfont = pygame.font.SysFont("dejavusans", 21, bold=True)
    lfont = pygame.font.SysFont("dejavusans", 18, bold=True)

    y = TITLE_H + PAD
    for hdr, cells in rows:
        # Row header label.
        htxt = hfont.render(hdr, True, HEADER)
        sheet.blit(htxt, (PAD, y + (HEADER_H - htxt.get_height()) // 2))

        ground_y = y + HEADER_H + TOP_MARGIN + REF_H
        # Shared ground line for this row.
        pygame.draw.line(sheet, GROUND, (PAD // 2, ground_y),
                         (panel_w - PAD // 2, ground_y), 3)

        # Center the row's figures as a group so a short row (the anchor) reads
        # as deliberately centered rather than left-stacked.
        n = len(cells)
        row_w = col_w * n
        x0 = (panel_w - row_w) // 2

        for i, (label, fig) in enumerate(cells):
            col_x = x0 + i * col_w
            fx = col_x + (col_w - fig.get_width()) // 2
            fy = ground_y - fig.get_height()
            # Soft contact shadow so figures read as standing, not floating.
            sh_w = max(20, int(fig.get_width() * 0.6))
            shadow = pygame.Surface((sh_w, 14), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (40, 30, 38, 75), shadow.get_rect())
            sheet.blit(shadow, (col_x + (col_w - sh_w) // 2, ground_y - 7))
            sheet.blit(fig, (fx, fy))

            txt = lfont.render(label, True, LABEL)
            sheet.blit(txt, (col_x + (col_w - txt.get_width()) // 2,
                             ground_y + GROUND_PAD))

        y += row_block_h + ROW_GAP

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "skybit_devil")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "showcase.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
