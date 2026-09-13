"""RUN SUMMARY — layout suggestions that make room for THREE full rows of
power-up pills AND give the "N POWER-UPS USED" caption its own clear,
bolder band (nothing overlapping it above or below).

ROUND 2: vs. the current shipping screen, five suggestions (N1..N5) each
(a) reclaim vertical room for a third pill row, (b) reserve a clear gap
around the caption, and (c) render that caption with more presence —
bigger / brighter / heavier, with the *treatment* varied per panel so the
caption look can be chosen too. The power-up pill itself (chip_h=40, icon
30, gold border, navy gradient) is NOT touched — only the surrounding
vertical arrangement + the caption styling move.

Every panel reuses the REAL primitives from ``game/hud.py`` so the
pills/tiles/buttons/title are pixel-identical to the live screen. Panels
render at native 360x640 then upscale 2x (720x1280).

Output: docs/run_summary_3row/round2/{current,n1_lift,n2_rules,n3_bigcap,
n4_outline,n5_balanced}.png + contact_sheet.png

Run from repo root:

    PYTHONPATH=. python tools/gen_summary_3row_layouts.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game.config import W, H  # noqa: E402
from game.draw import lerp_color  # noqa: E402
from game.hud import (  # noqa: E402
    _font, _outlined_text, _score_plaque, _stat_tile_chunky,
    _pill_btn, _outline_pill_btn,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _GOLD_BRIGHT, _GOLD_MUTED, _PANEL_LIGHTER, _PANEL_DARK, _NIGHT_DEEP,
)
from game.powerup_help import _powerup_icon  # noqa: E402

SCALE = 2
NIGHT_MID = (22, 14, 58)

OUT = os.path.join(os.path.dirname(__file__), "..", "docs",
                   "run_summary_3row", "round2")
os.makedirs(OUT, exist_ok=True)

# Twinkling-star field, seeded identically to HUD.__init__ so the backdrop
# matches the live overlay screens.
import random as _random  # noqa: E402
_rng = _random.Random(42)
STARS = [
    (_rng.randint(8, W - 8), _rng.randint(8, H - 180),
     _rng.choice((1, 1, 1, 2)), _rng.uniform(0, 6.28))
    for _ in range(110)
]

# ── Shared sample run — a long run that grabbed 15 distinct power-ups, so
# all three rows are full and the "room for 3 rows" is actually shown.
DATA = dict(score=137, best=842, new_best=False,
            time_str="1:27", coin_count=41, coins_pct="62%",
            pillars=33, flaps=211)
POWERUPS = [
    ("triple", 3), ("magnet", 2), ("slowmo", 1), ("kfc", 1), ("ghost", 2),
    ("shrink", 1), ("surprise", 2), ("grow", 1), ("rail", 1), ("lottery", 1),
    ("megamagnet", 1), ("knight", 1), ("skateboard", 1), ("genie", 1),
    ("treasure", 2),
]


def _backdrop(surf):
    """Night-sky gradient + the live dim/stars/mountain treatment, so the
    standalone mockup reads like a real frozen-world stats screen."""
    for yy in range(H):
        t = yy / (H - 1)
        pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, NIGHT_MID, t),
                         (0, yy), (W, yy))
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((*_NIGHT_DEEP, 190))
    surf.blit(dim, (0, 0))
    _draw_overlay_stars(surf, STARS, 1.2)
    _draw_mountain_silhouette(surf, alpha=160)


def draw_caption(surf, text, cap_y, style):
    """Render the 'N POWER-UPS USED' line. ``style`` selects the presence
    treatment; all of the round-2 styles read brighter/heavier than the
    shipping muted caption. Returns nothing — drawn centered on cap_y."""
    if style == "current":
        # The shipping look: size 18, synthetic bold, muted gold @ 230.
        f = _font(18, True)
        f.set_bold(True)
        img = f.render(text, True, _GOLD_MUTED)
        f.set_bold(False)
        img.set_alpha(230)
        surf.blit(img, img.get_rect(center=(W // 2, cap_y)))
        return

    if style == "outline":
        # Title-family treatment: bright gold with a thin red pixel
        # outline + small drop shadow — maximum legibility over the busy
        # tiles/pills backdrop.
        _outlined_text(surf, text, (W // 2, cap_y), size=19, px=2,
                       shadow_offset=(2, 3))
        return

    # Remaining styles share a bright-gold heavy-bold core; size + accents
    # vary.
    size = 22 if style == "big" else 20
    f = _font(size, True)
    f.set_bold(True)
    img = f.render(text, True, _GOLD_BRIGHT)
    f.set_bold(False)
    rect = img.get_rect(center=(W // 2, cap_y))
    surf.blit(img, rect)

    if style == "rules":
        # Short gold divider rules flanking the text — a section-header
        # framing that gives the line clear presence without crowding it.
        margin, run = 14, 56
        ly = cap_y
        pygame.draw.line(surf, _GOLD_BRIGHT,
                         (rect.left - margin - run, ly),
                         (rect.left - margin, ly), 2)
        pygame.draw.line(surf, _GOLD_BRIGHT,
                         (rect.right + margin, ly),
                         (rect.right + margin + run, ly), 2)
    elif style == "underline":
        # Thin centered underline rule for a polished header feel.
        uw = rect.width + 24
        uy = rect.bottom + 5
        rule = pygame.Surface((uw, 2), pygame.SRCALPHA)
        rule.fill((*_GOLD_BRIGHT, 220))
        surf.blit(rule, rule.get_rect(center=(W // 2, uy)))


def _chunk_even(seq, n):
    """Split ``seq`` into ``n`` rows as evenly as possible by count, with
    any remainder loaded onto the earlier rows (top-heavy)."""
    n = min(n, len(seq)) or 1
    base, extra = divmod(len(seq), n)
    rows, i = [], 0
    for r in range(n):
        size = base + (1 if r < extra else 0)
        rows.append(seq[i:i + size])
        i += size
    return rows


def _draw_pill_rows(surf, pu, first_row_y, n_rows, pitch=48):
    """Faithful copy of the live ``draw_stats`` chip code, generalised to
    ``n_rows``. Pill geometry is unchanged: chip_h=40, icon 30, gold
    border, navy gradient, 2x supersampled rounded body."""
    chip_h = 40
    icon_size = 30
    chip_radius = chip_h // 2
    pad_l, pad_r = 3, 8
    count_font = _font(16, True)
    chips = []
    for kind, count in pu:
        tf = count_font.render(f"×{count}", True, _GOLD_BRIGHT)
        chip_w = pad_l + icon_size + 2 + tf.get_width() + pad_r
        chips.append((kind, count, chip_w, tf))

    gap = 5
    rows = _chunk_even(chips, n_rows)
    for ri, row_chips in enumerate(rows):
        row_total = (sum(c[2] for c in row_chips)
                     + gap * (len(row_chips) - 1))
        sx = (W - row_total) // 2
        y = first_row_y + ri * pitch
        for kind, count, chip_w, tf in row_chips:
            OS = 2
            ow, oh = chip_w * OS, chip_h * OS
            o_radius = chip_radius * OS
            body_big = pygame.Surface((ow, oh), pygame.SRCALPHA)
            for yy in range(oh):
                t = yy / max(1, oh - 1)
                c = lerp_color(_PANEL_LIGHTER, _PANEL_DARK, t)
                pygame.draw.line(body_big, (*c, 245), (0, yy), (ow, yy))
            mask_big = pygame.Surface((ow, oh), pygame.SRCALPHA)
            pygame.draw.rect(mask_big, (255, 255, 255, 255),
                             (0, 0, ow, oh), border_radius=o_radius)
            body_big.blit(mask_big, (0, 0),
                          special_flags=pygame.BLEND_RGBA_MIN)
            pygame.draw.rect(body_big, _GOLD_BRIGHT, (0, 0, ow, oh),
                             width=2 * OS, border_radius=o_radius)
            body = pygame.transform.smoothscale(body_big, (chip_w, chip_h))
            surf.blit(body, (sx, y - chip_h // 2))
            _powerup_icon(surf, kind,
                          sx + pad_l + icon_size // 2 + 2, y,
                          int(icon_size * 1.5))
            surf.blit(tf, tf.get_rect(midright=(sx + chip_w - pad_r, y)))
            sx += chip_w + gap


def render_summary(layout):
    """Render one 360x640 RUN SUMMARY panel from a layout dict, then return
    it upscaled to 720x1280."""
    surf = pygame.Surface((W, H))
    _backdrop(surf)

    _outlined_text(surf, "RUN  SUMMARY", (W // 2, layout["title_y"]),
                   size=34, px=3, shadow_offset=(3, 5))

    plaque = pygame.Rect(18, layout["plaque_top"], W - 36, layout["plaque_h"])
    _score_plaque(surf, plaque, DATA["score"], DATA["best"], DATA["new_best"])

    tiles = [
        ("time",   DATA["time_str"],            "TIME",    None),
        ("coin",   str(DATA["coin_count"]),      "COINS",   DATA["coins_pct"]),
        ("pillar", str(DATA["pillars"]),         "PILLARS", None),
        ("flap",   str(DATA["flaps"]),           "FLAPS",   None),
    ]
    tile_w, tile_h, tile_gap = 78, 104, 8
    total_w = len(tiles) * tile_w + (len(tiles) - 1) * tile_gap
    start_x = (W - total_w) // 2
    for i, (kind, val, lbl, sub) in enumerate(tiles):
        r = pygame.Rect(start_x + i * (tile_w + tile_gap), layout["tiles_y"],
                        tile_w, tile_h)
        _stat_tile_chunky(surf, r, kind, val, lbl, subline=sub)

    total_pu = sum(c for _, c in POWERUPS)
    draw_caption(surf, f"{total_pu}  POWER-UPS USED",
                 layout["cap_y"], layout["caption"])

    _draw_pill_rows(surf, POWERUPS, layout["pill_first_row_y"],
                    n_rows=layout.get("n_rows", 3), pitch=layout["pill_pitch"])

    _pill_btn(surf, (W // 2, layout["play_y"]), "PLAY  AGAIN",
              size=22, alpha=255, min_width=240, primary=True, dim=True,
              shadow=False)
    _outline_pill_btn(surf, (W // 2, layout["menu_y"]), "MAIN MENU",
                      size=14, min_width=130)

    return pygame.transform.smoothscale(surf, (W * SCALE, H * SCALE))


# ── ROUND 2: CURRENT (ships now) + N1..N5 ──────────────────────────────────
# pill_first_row_y is the CENTER y of the first of three rows; the block
# spans (first - 20) .. (first + 2*pitch + 20). Each layout reserves clear
# air around the caption (no overlap above from tiles / below from pills).
PANELS = [
    ("current", "CURRENT  (ships now)", dict(
        title_y=56, plaque_top=104, plaque_h=156, tiles_y=282,
        cap_y=414, caption="current",
        pill_first_row_y=444, pill_pitch=48, n_rows=2,
        play_y=568, menu_y=618)),
    ("n1_lift", "N1  ·  LIFTED STACK", dict(
        title_y=44, plaque_top=62, plaque_h=156, tiles_y=232,
        cap_y=360, caption="bold",
        pill_first_row_y=416, pill_pitch=48, n_rows=3,
        play_y=568, menu_y=618)),
    ("n2_rules", "N2  ·  HEADER RULES", dict(
        title_y=50, plaque_top=88, plaque_h=140, tiles_y=244,
        cap_y=374, caption="rules",
        pill_first_row_y=420, pill_pitch=48, n_rows=3,
        play_y=572, menu_y=618)),
    ("n3_bigcap", "N3  ·  BIG CAPTION", dict(
        title_y=50, plaque_top=80, plaque_h=156, tiles_y=252,
        cap_y=382, caption="big",
        pill_first_row_y=422, pill_pitch=48, n_rows=3,
        play_y=576, menu_y=620)),
    ("n4_outline", "N4  ·  OUTLINED CAPTION", dict(
        title_y=52, plaque_top=90, plaque_h=150, tiles_y=256,
        cap_y=388, caption="outline",
        pill_first_row_y=430, pill_pitch=44, n_rows=3,
        play_y=574, menu_y=618)),
    ("n5_balanced", "N5  ·  BALANCED + UNDERLINE  (recommended)", dict(
        title_y=50, plaque_top=86, plaque_h=146, tiles_y=246,
        cap_y=372, caption="underline",
        pill_first_row_y=418, pill_pitch=48, n_rows=3,
        play_y=576, menu_y=620)),
]


def contact_sheet(panels):
    """3-col x 2-row labelled sheet (matches the existing comparison sheets)."""
    pw, ph = W * SCALE, H * SCALE
    label_h, pad, cols = 64, 24, 3
    rows = (len(panels) + cols - 1) // cols
    sheet_w = cols * pw + (cols + 1) * pad
    sheet_h = rows * (ph + label_h) + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 6, 20))
    lf = _font(15, True)
    for i, (img, label) in enumerate(panels):
        col, row = i % cols, i // cols
        x = pad + col * (pw + pad)
        y = pad + row * (ph + label_h + pad)
        cap = lf.render(label, True, _GOLD_BRIGHT)
        sheet.blit(cap, cap.get_rect(center=(x + pw // 2, y + label_h // 2)))
        sheet.blit(img, (x, y + label_h))
    return sheet


def main():
    rendered = []
    for name, label, layout in PANELS:
        img = render_summary(layout)
        path = os.path.join(OUT, f"{name}.png")
        pygame.image.save(img, path)
        print(f"  wrote {path} ({img.get_width()}x{img.get_height()})")
        rendered.append((img, label))

    sheet = contact_sheet(rendered)
    sheet_path = os.path.join(OUT, "contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"  wrote {sheet_path} "
          f"({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    sys.exit(main() or 0)
