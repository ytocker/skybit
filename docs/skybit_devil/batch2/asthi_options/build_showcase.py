"""Assemble the 5-option Asthi-Dakini showcase — one labeled tile per version.

Compositing only (no new design): each version's matured hero is scaled into a
tile in a single comparison row, with a header (v# + slug) and a one-line thesis
caption, so the five read side-by-side for a pick. Heroes already sit on their own
vertical gradient; we letterbox each onto a neutral tile at a common height.
"""

import os
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))

# version dir, label, thesis — matured final hero per version
VERSIONS = [
    ("ancestor-choir",      "v1 · ANCESTOR-CHOIR",   "round_2_hero.png",
     "mid-chant: singing open jaws + lidded eyes; cyan pooled inside sockets"),
    ("wrathful-grin",       "v2 · WRATHFUL-GRIN",    "round_3_hero.png",
     "bared-fang fury (rictus/snarl/roar), battle-scarred; cyan wrath-embers"),
    ("gem-eyed-oracle",     "v3 · GEM-EYED-ORACLE",  "round_2_hero.png",
     "jewelled cyan cabochon eyes — the most cyan in the skulls"),
    ("verdigris-reliquary", "v4 · VERDIGRIS-RELIQUARY", "round_2_hero.png",
     "aged temple bronze + green patina; icy gems pop against the court"),
    ("dawn-lotus-court",    "v5 · DAWN-LOTUS-COURT", "round_2_hero.png",
     "warm rose-gold + sparing lotus-pink marks; cyan cool blessing-drops"),
]

TILE_W = 300
TILE_H = 400
PAD = 18
MARGIN = 34
HEAD_H = 40
CAP_H = 62
TITLE_H = 64

BG = (40, 44, 56)
TILE_BG = (22, 26, 40)
FRAME = (150, 152, 162)
TITLE_COL = (240, 240, 236)
HEAD_COL = (250, 224, 150)
CAP_COL = (206, 210, 220)


def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.size(t)[0] <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))

    n = len(VERSIONS)
    sheet_w = MARGIN * 2 + n * TILE_W + (n - 1) * PAD
    sheet_h = MARGIN + TITLE_H + HEAD_H + TILE_H + CAP_H + MARGIN
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 30, bold=True)
    f_head = pygame.font.SysFont("dejavusans", 18, bold=True)
    f_cap = pygame.font.SysFont("dejavusans", 13)

    title = f_title.render(
        "ASTHI-DAKINI — 5 distinct versions  (shared base: necklace hero gem, "
        "smaller third-eye, hand-skulls = crown size)",
        True, TITLE_COL)
    if title.get_width() > sheet_w - 2 * MARGIN:
        title = pygame.font.SysFont("dejavusans", 24, bold=True).render(
            "ASTHI-DAKINI — 5 distinct versions", True, TITLE_COL)
    sheet.blit(title, (MARGIN, MARGIN + (TITLE_H - title.get_height()) // 2))

    grid_top = MARGIN + TITLE_H
    for i, (slug, label, hero, thesis) in enumerate(VERSIONS):
        x = MARGIN + i * (TILE_W + PAD)
        # header
        h = f_head.render(label, True, HEAD_COL)
        sheet.blit(h, (x + (TILE_W - h.get_width()) // 2,
                       grid_top + (HEAD_H - h.get_height()) // 2))
        # tile
        ty = grid_top + HEAD_H
        rect = pygame.Rect(x, ty, TILE_W, TILE_H)
        pygame.draw.rect(sheet, TILE_BG, rect)
        pygame.draw.rect(sheet, FRAME, rect, 3)
        img = pygame.image.load(os.path.join(HERE, slug, hero)).convert_alpha()
        iw, ih = img.get_size()
        s = min((TILE_W - 12) / iw, (TILE_H - 12) / ih)
        scaled = pygame.transform.smoothscale(img, (int(iw * s), int(ih * s)))
        sheet.blit(scaled, (rect.centerx - scaled.get_width() // 2,
                            rect.centery - scaled.get_height() // 2))
        # caption
        cy = ty + TILE_H + 6
        for li, line in enumerate(wrap(thesis, f_cap, TILE_W - 6)):
            c = f_cap.render(line, True, CAP_COL)
            sheet.blit(c, (x + (TILE_W - c.get_width()) // 2, cy + li * 16))

    out = os.path.join(HERE, "showcase.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
