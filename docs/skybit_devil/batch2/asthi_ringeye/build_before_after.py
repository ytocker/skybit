"""Simple BEFORE/AFTER for the ring-third-eye revision.

BEFORE = the shared base (faceted cut-gem third-eye + larger faceted necklace gem —
the config every prior option used). AFTER = this revision: the earlier darker-skin
round's concentric-RING third-eye shape (clean, no blue aura) + a SMALLER faceted gem
in the heart of the necklace. Compositing only.
"""

import os
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
BEFORE = os.path.join(HERE, "..", "asthi_options", "_base", "round_10_hero.png")
AFTER = os.path.join(HERE, "round_1_hero.png")

PANEL_W, PANEL_H = 360, 480
PAD, MARGIN, HEAD_H, CAP_H = 24, 30, 44, 56
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


def panel(sheet, x, img_path, head, cap, f_head, f_cap):
    h = f_head.render(head, True, HEAD_COL)
    sheet.blit(h, (x + (PANEL_W - h.get_width()) // 2, MARGIN + (HEAD_H - h.get_height()) // 2))
    ty = MARGIN + HEAD_H
    rect = pygame.Rect(x, ty, PANEL_W, PANEL_H)
    pygame.draw.rect(sheet, PANEL_BG, rect)
    pygame.draw.rect(sheet, FRAME, rect, 3)
    img = pygame.image.load(img_path).convert_alpha()
    iw, ih = img.get_size()
    sc = min((PANEL_W - 14) / iw, (PANEL_H - 14) / ih)
    im = pygame.transform.smoothscale(img, (int(iw * sc), int(ih * sc)))
    sheet.blit(im, (rect.centerx - im.get_width() // 2, rect.centery - im.get_height() // 2))
    cy = ty + PANEL_H + 8
    for i, line in enumerate(wrap(cap, f_cap, PANEL_W)):
        c = f_cap.render(line, True, CAP_COL)
        sheet.blit(c, (x + (PANEL_W - c.get_width()) // 2, cy + i * 18))


def main():
    pygame.init(); pygame.font.init(); pygame.display.set_mode((1, 1))
    W = MARGIN * 2 + PANEL_W * 2 + PAD
    H = MARGIN + HEAD_H + PANEL_H + CAP_H + MARGIN
    sheet = pygame.Surface((W, H)); sheet.fill(BG)
    f_head = pygame.font.SysFont("dejavusans", 22, bold=True)
    f_cap = pygame.font.SysFont("dejavusans", 14)
    panel(sheet, MARGIN, BEFORE, "BEFORE",
          "faceted cut-gem third-eye  ·  larger necklace gem", f_head, f_cap)
    panel(sheet, MARGIN + PANEL_W + PAD, AFTER, "AFTER",
          "concentric-ring third-eye (earlier shape, no aura)  ·  smaller gem in necklace heart",
          f_head, f_cap)
    out = os.path.join(HERE, "before_after.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
