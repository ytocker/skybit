"""3-up comparison: the base config vs the two element placements.

- BASE        : faceted cut-gem third-eye + faceted gem in the necklace.
- RING EYE    : concentric-ring third-eye (earlier shape, no aura) + smaller faceted
                gem in the necklace heart.
- SWITCHED    : the two swapped — faceted gem third-eye (brightest) + ring in necklace.
Compositing only.
"""

import os
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = [
    (os.path.join(HERE, "..", "asthi_options", "_base", "round_10_hero.png"),
     "BASE", "faceted third-eye  ·  faceted necklace gem"),
    (os.path.join(HERE, "round_1_hero.png"),
     "RING EYE", "ring third-eye (no aura)  ·  smaller gem in necklace"),
    (os.path.join(HERE, "round_1_switch_hero.png"),
     "SWITCHED", "faceted gem third-eye  ·  ring in necklace heart"),
    (os.path.join(HERE, "round_1_switchbig_hero.png"),
     "SWITCHED + BIG", "LARGER faceted gem third-eye  ·  ring in necklace"),
]

PANEL_W, PANEL_H = 330, 440
PAD, MARGIN, HEAD_H, CAP_H = 22, 30, 44, 52
BG = (40, 44, 56)
PANEL_BG = (22, 26, 40)
FRAME = (150, 152, 162)
HEAD_COL = (250, 224, 150)
CAP_COL = (210, 214, 224)


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
    pygame.init(); pygame.font.init(); pygame.display.set_mode((1, 1))
    n = len(PANELS)
    W = MARGIN * 2 + PANEL_W * n + PAD * (n - 1)
    H = MARGIN + HEAD_H + PANEL_H + CAP_H + MARGIN
    sheet = pygame.Surface((W, H)); sheet.fill(BG)
    f_head = pygame.font.SysFont("dejavusans", 22, bold=True)
    f_cap = pygame.font.SysFont("dejavusans", 13)
    for i, (path, head, cap) in enumerate(PANELS):
        x = MARGIN + i * (PANEL_W + PAD)
        h = f_head.render(head, True, HEAD_COL)
        sheet.blit(h, (x + (PANEL_W - h.get_width()) // 2,
                       MARGIN + (HEAD_H - h.get_height()) // 2))
        ty = MARGIN + HEAD_H
        rect = pygame.Rect(x, ty, PANEL_W, PANEL_H)
        pygame.draw.rect(sheet, PANEL_BG, rect)
        pygame.draw.rect(sheet, FRAME, rect, 3)
        img = pygame.image.load(path).convert_alpha()
        iw, ih = img.get_size()
        sc = min((PANEL_W - 14) / iw, (PANEL_H - 14) / ih)
        im = pygame.transform.smoothscale(img, (int(iw * sc), int(ih * sc)))
        sheet.blit(im, (rect.centerx - im.get_width() // 2, rect.centery - im.get_height() // 2))
        cy = ty + PANEL_H + 7
        for li, line in enumerate(wrap(cap, f_cap, PANEL_W)):
            c = f_cap.render(line, True, CAP_COL)
            sheet.blit(c, (x + (PANEL_W - c.get_width()) // 2, cy + li * 16))
    out = os.path.join(HERE, "compare.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
