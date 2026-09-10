import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.font.init()

# Consistent crop around the mid-pillar cart+parrot (same pixel box in all 5).
CROP = pygame.Rect(610, 1070, 380, 340)
PANEL_W = 380
PANEL_H = 340
LABEL_H = 46

items = [
    ("1. Mine cart",         "/tmp/db_cart_01_mine.png"),
    ("2. Wagon (current)",   "/tmp/design_branch_cart_wagon.png"),
    ("3. Coal hopper",       "/tmp/db_cart_03_hopper.png"),
    ("4. Speedster",         "/tmp/db_cart_04_speedster.png"),
    ("5. Tropical",          "/tmp/db_cart_05_tropical.png"),
]

font = pygame.font.SysFont("dejavusans", 26, bold=True)
montage = pygame.Surface((PANEL_W * len(items), PANEL_H + LABEL_H))
montage.fill((24, 26, 32))

for i, (label, path) in enumerate(items):
    src = pygame.image.load(path)
    crop = src.subsurface(CROP).copy()
    crop = pygame.transform.smoothscale(crop, (PANEL_W, PANEL_H))
    x = i * PANEL_W
    montage.blit(crop, (x, LABEL_H))
    # label bar
    pygame.draw.rect(montage, (40, 44, 54), pygame.Rect(x, 0, PANEL_W, LABEL_H))
    txt = font.render(label, True, (240, 240, 245))
    montage.blit(txt, (x + (PANEL_W - txt.get_width()) // 2,
                       (LABEL_H - txt.get_height()) // 2))
    pygame.draw.rect(montage, (70, 74, 84),
                     pygame.Rect(x, 0, PANEL_W, PANEL_H + LABEL_H), 2)

pygame.image.save(montage, "/tmp/cart_options_montage.png")
print("saved /tmp/cart_options_montage.png", montage.get_size())
