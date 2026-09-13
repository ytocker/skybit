"""Rough blackout-massing thumbnail strip for the epic-boss brainstorm.

Solid-silhouette ONLY — proves each direction's blackout read is distinct in
kind (proportion, stance, prop axis). This is not finished art; it exists so the
art-director can cull on silhouette before any concept is rendered for real.
The clown's whole lineage (plum/lime barber-twist scepter, grinning marotte,
ruff/bells/cap) is deliberately absent from every massing here."""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.font.init()

CELL_W, CELL_H = 240, 320
COLS, ROWS = 4, 2
PAD = 8
LABEL_H = 30
W = COLS * CELL_W + PAD * (COLS + 1)
H = ROWS * (CELL_H + LABEL_H) + PAD * (ROWS + 1)

BG = (150, 150, 160)        # neutral grey so the black massing reads clean
SIL = (16, 14, 20)          # near-black silhouette
FONT = pygame.font.SysFont("dejavusans", 15, bold=True)
SMALL = pygame.font.SysFont("dejavusans", 11)


def poly(s, pts, col=SIL):
    pygame.draw.polygon(s, col, [(int(x), int(y)) for x, y in pts])


def circ(s, x, y, r, col=SIL):
    pygame.draw.circle(s, col, (int(x), int(y)), int(r))


def ellipse(s, cx, cy, rx, ry, col=SIL):
    pygame.draw.ellipse(s, col, (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


# Each builder draws a SOLID-BLACK rough massing into a CELL_W x CELL_H surface,
# centred on cx. The prop axis is drawn as the tall vertical it must become.

def horned_warlord(s, cx):
    # Squat, MASSIVE-shouldered horned devil; immense ram horns sweeping wide;
    # a war-maul held vertical. Bottom-heavy triangle, very wide top.
    base = 300
    # legs (squat, digitigrade)
    poly(s, [(cx-46, base), (cx-22, base), (cx-18, 230), (cx-44, 232)])
    poly(s, [(cx+46, base), (cx+22, base), (cx+18, 230), (cx+44, 232)])
    # huge torso wedge, widest at shoulders
    poly(s, [(cx-90, 120), (cx+90, 120), (cx+50, 240), (cx-50, 240)])
    # head between shoulders
    circ(s, cx, 110, 30)
    # ram horns curling DOWN and out (wide spiral)
    for sgn in (-1, 1):
        pts = []
        for k in range(14):
            a = k / 13.0
            ang = sgn * (a * 3.4)
            r = 16 + a * 40
            pts.append((cx + sgn*26 + math.cos(ang)*r, 96 + math.sin(ang*0.8)*r))
        for k in range(13, -1, -1):
            a = k / 13.0
            ang = sgn * (a * 3.4)
            r = 16 + a * 40 - 12
            pts.append((cx + sgn*26 + math.cos(ang)*r, 96 + math.sin(ang*0.8)*r))
        poly(s, pts)
    # war-maul (vertical haft + heavy double-ended head -> mirrors well)
    hx = cx + 96
    pygame.draw.rect(s, SIL, (hx-5, 40, 10, 270))
    poly(s, [(hx-26, 40), (hx+26, 40), (hx+20, 80), (hx-20, 80)])   # top block head
    poly(s, [(hx-22, 268), (hx+22, 268), (hx+16, 304), (hx-16, 304)])  # bottom block


def gaunt-reaper(s, cx):
    pass
