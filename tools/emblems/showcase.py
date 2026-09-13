"""Combined showcase of all 57 bespoke achievement emblems, grouped by category.
Run headless: SDL_VIDEODRIVER=dummy python tools/emblems/showcase.py
"""
import pygame; pygame.init(); pygame.font.init()
import game.achievement_icons as ai
from game import achievements as ach

CATS = [(c, ach.BY_CAT[c], 'gold') for c in ach.CATEGORY_ORDER] + \
       [(c, ach.BY_CAT_SHAME[c], 'tarnished') for c in ach.SHAME_CATEGORY_ORDER]
BADGE, COLS, PAD, LBL = 84, 6, 14, 16
font = pygame.font.SysFont(None, 17, bold=True)
hfont = pygame.font.SysFont(None, 22, bold=True)
cellw = BADGE + PAD
cellh = BADGE + LBL + PAD
# pre-measure height
rows_total = 0
for _, items, _ in CATS:
    rows_total += 1  # header
    rows_total += (len(items) + COLS - 1) // COLS
W = COLS * cellw + PAD
H = rows_total * 0  # computed below
y = PAD
# first pass compute height
yy = PAD
for name, items, tone in CATS:
    yy += 30
    nrows = (len(items) + COLS - 1) // COLS
    yy += nrows * cellh
H = yy + PAD
surf = pygame.Surface((W, H))
surf.fill((14, 12, 28))
y = PAD
for name, items, tone in CATS:
    hdr = hfont.render(f"{name}  ({len(items)})", True, (230, 200, 120) if tone=='gold' else (200, 150, 110))
    surf.blit(hdr, (PAD, y)); y += 30
    for i, a in enumerate(items):
        col = i % COLS; row = i // COLS
        cx = PAD + col * cellw
        cy = y + row * cellh
        b = ai.get_badge(a.id, BADGE, True, False, tone)
        surf.blit(b, (cx, cy))
        lab = font.render(a.id[:13], True, (200, 200, 220))
        surf.blit(lab, (cx + (BADGE-lab.get_width())//2, cy + BADGE - 2))
    y += ((len(items) + COLS - 1)//COLS) * cellh
pygame.image.save(surf, 'docs/emblems/showcase.png')
print('showcase.png', surf.get_size())
