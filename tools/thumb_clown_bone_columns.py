"""Rough brainstorm thumbnails for the clown-event bone columns.

Five DISTINCT bottom-up construction logics for a 58px bone column, sketched in
the bone-roster idiom (warm-ivory bone, ink keyline, cyan/purple wisdom gem,
gold thin-accent). These are deliberately ROUGH — silhouette + construction
read only, NOT finished art — to support the brainstorm cull.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import math
import pygame

pygame.init()

# Bone-roster palette (borrowed from the locked batch2 house style).
INK   = (28, 22, 30)
BONE  = (228, 222, 206)
BONE_DK = (150, 144, 128)
BONE_HI = (250, 247, 236)
GOLD  = (250, 205, 72)
GOLD_DK = (176, 130, 30)
CYAN  = (120, 214, 222)
CYAN_HI = (224, 252, 252)
PURPLE = (158, 120, 214)
BG = (54, 62, 78)

PW = 58
TILE_W, TILE_H = 200, 520
COLS = 5


def bone_seg(surf, cx, y, w, h):
    """A triad-lit bone capsule: dark keyline / flat fill / top-left sheen."""
    r = pygame.Rect(cx - w // 2, y, w, h)
    pygame.draw.rect(surf, INK, r.inflate(2, 2), border_radius=h // 2)
    pygame.draw.rect(surf, BONE, r, border_radius=h // 2)
    pygame.draw.rect(surf, BONE_DK, (r.x, r.bottom - h // 3, w, h // 3),
                     border_radius=h // 2)
    pygame.draw.rect(surf, BONE_HI, (r.x + 2, r.y + 2, w - 8, max(2, h // 3)),
                     border_radius=h // 3)


def skull(surf, cx, cy, r, eye=CYAN):
    pygame.draw.circle(surf, INK, (cx, cy), r + 1)
    pygame.draw.circle(surf, BONE, (cx, cy), r)
    pygame.draw.circle(surf, BONE_HI, (cx - r // 3, cy - r // 3), r // 3)
    for s in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + s * r // 2, cy - r // 5), r // 3)
        pygame.draw.circle(surf, eye, (cx + s * r // 2, cy - r // 5), max(1, r // 5))
    # jaw teeth
    for i in range(-2, 3):
        pygame.draw.line(surf, INK, (cx + i * (r // 3), cy + r // 2),
                         (cx + i * (r // 3), cy + r), 1)


def gem(surf, cx, cy, r, col=CYAN):
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, col, [(cx, cy - r + 1), (cx + r - 1, cy),
                                    (cx, cy + r - 1), (cx - r + 1, cy)])
    pygame.draw.circle(surf, CYAN_HI, (cx - 1, cy - 1), max(1, r // 3))


def label(surf, lines, x, y):
    f = pygame.font.SysFont("dejavusans", 13, bold=True)
    fs = pygame.font.SysFont("dejavusans", 10)
    surf.blit(f.render(lines[0], True, (255, 255, 255)), (x, y))
    for i, ln in enumerate(lines[1:]):
        surf.blit(fs.render(ln, True, (208, 210, 220)), (x, y + 18 + i * 13))


# ── 1. STACKED-TOTEM: charnel skull-stupa (borrows Stupika) ──────────────────
def tile_totem(s, cx):
    """Skulls + reliquary niches stacked into tapering tiers; gap edge = a wide
    lowest 'living' skull-tier with lamp-eyes facing the gap."""
    y = 60
    widths = [40, 46, 52, 58, 58, 52, 46, 40]
    for i, w in enumerate(widths):
        bone_seg(s, cx, y, w, 26)
        if i in (1, 4, 6):
            skull(s, cx, y + 13, 9)
        else:
            gem(s, cx, y + 13, 4, PURPLE if i % 2 else CYAN)
        y += 28
    # wide living gap-cap skull
    skull(s, cx, y + 4, 16, eye=GOLD)


# ── 2. SKEWER / SPIKE-THREADED: vertebrae on a bone-spike (borrows Nagaraja) ──
def tile_skewer(s, cx):
    """Loose vertebra beads + tiny skulls THREADED on a single central marrow-
    spike; the spike's barbed tip is the gap-edge cap pointing into the gap."""
    pygame.draw.line(s, GOLD_DK, (cx, 70), (cx, TILE_H - 60), 5)
    pygame.draw.line(s, GOLD, (cx, 70), (cx, TILE_H - 60), 2)
    y = 80
    while y < TILE_H - 70:
        if (y // 34) % 3 == 0:
            skull(s, cx, y, 11)
        else:
            # vertebra bead = wide flat disc with wing-process nubs
            pygame.draw.ellipse(s, INK, (cx - 19, y - 7, 38, 14))
            pygame.draw.ellipse(s, BONE, (cx - 17, y - 6, 34, 12))
            pygame.draw.ellipse(s, BONE_HI, (cx - 14, y - 5, 14, 4))
            for sx in (-1, 1):
                pygame.draw.circle(s, BONE_DK, (cx + sx * 17, y), 3)
        y += 34
    # barbed spike tip into the gap
    pygame.draw.polygon(s, BONE, [(cx, y + 26), (cx - 7, y), (cx + 7, y)])
    pygame.draw.polygon(s, INK, [(cx, y + 26), (cx - 7, y), (cx + 7, y)], 2)


# ── 3. HYBRID: ribcage-cage shaft + gem-eyed skull cap (Citipati/Asthi) ──────
def tile_ribcage(s, cx):
    """A vertical SPINE rope runs the shaft with paired curving RIBS arcing out
    to the column edge (a cage you fly past); gap edge capped by a faceted-gem
    third-eye skull set in a gold ring (the Asthi switch+big focal)."""
    pygame.draw.line(s, BONE_DK, (cx, 60), (cx, TILE_H - 40), 6)
    pygame.draw.line(s, BONE, (cx, 60), (cx, TILE_H - 40), 3)
    y = 90
    while y < TILE_H - 60:
        for sgn in (-1, 1):
            pts = [(cx, y), (cx + sgn * 22, y + 6), (cx + sgn * 26, y + 22)]
            pygame.draw.lines(s, INK, False, pts, 4)
            pygame.draw.lines(s, BONE, False, pts, 2)
        y += 26
    # gem-eyed third-eye skull cap (gold ring focal)
    cy = TILE_H - 40
    pygame.draw.circle(s, GOLD, (cx, cy), 22, 3)
    skull(s, cx, cy, 17)
    gem(s, cx, cy - 16, 6, CYAN)


# ── 4. WOVEN BONE-LATTICE: interlocked femur lattice (new logic) ─────────────
def tile_lattice(s, cx):
    """Crossed long-bones woven into an X-lattice trellis (a bone hurdle-fence),
    knuckle-knot joints pinned with gold studs; the gap edge is a horizontal
    capping femur laid across the column mouth with a skull boss centred on it."""
    y = 70
    while y < TILE_H - 60:
        for sgn in (-1, 1):
            x0 = cx - sgn * 24
            x1 = cx + sgn * 24
            pygame.draw.line(s, INK, (x0, y), (x1, y + 38), 7)
            pygame.draw.line(s, BONE, (x0, y), (x1, y + 38), 4)
            pygame.draw.line(s, BONE_HI, (x0, y), (x1, y + 38), 1)
        pygame.draw.circle(s, GOLD, (cx, y + 19), 4)   # knuckle-knot stud
        pygame.draw.circle(s, GOLD_DK, (cx, y + 19), 4, 1)
        y += 38
    # capping cross-femur + skull boss at the gap mouth
    cap = TILE_H - 50
    bone_seg(s, cx, cap, 58, 16)
    skull(s, cx, cap + 8, 12, eye=PURPLE)


# ── 5. MELTED-WAX DRIP COLUMN: candle-bone taper (new logic) ─────────────────
def tile_drip(s, cx):
    """A funereal BONE-CANDLE: a softly bulging melted-wax/bone shaft with
    sagging drip-lobes down the sides (uneven, organic — like Verdigris Drowned-
    King's slump), gold wax-runnels; the gap edge is a guttering flame-skull
    sconce — a skull whose eye-sockets gutter a cyan soul-flame into the gap."""
    pts_l, pts_r = [], []
    for i in range(0, TILE_H - 90, 6):
        yy = 70 + i
        bulge = 22 + int(math.sin(i * 0.05) * 5) + int(math.sin(i * 0.21) * 3)
        pts_l.append((cx - bulge, yy))
        pts_r.append((cx + bulge, yy))
    poly = pts_l + pts_r[::-1]
    pygame.draw.polygon(s, INK, poly)
    pygame.draw.polygon(s, BONE, [(x + (2 if x < cx else -2), y) for x, y in poly])
    # sagging drip lobes
    for i in range(80, TILE_H - 120, 46):
        sgn = -1 if (i // 46) % 2 else 1
        bulge = 22 + int(math.sin(i * 0.05) * 5)
        dx = cx + sgn * bulge
        pygame.draw.circle(s, BONE, (dx, i + 14), 6)
        pygame.draw.circle(s, INK, (dx, i + 14), 6, 1)
        pygame.draw.line(s, GOLD, (dx, i), (dx, i + 14), 2)   # gold runnel
    # guttering flame-skull sconce at the gap mouth
    cy = TILE_H - 70
    skull(s, cx, cy, 15, eye=CYAN)
    for sx in (-1, 1):
        pygame.draw.polygon(s, CYAN, [(cx + sx * 7, cy - 18), (cx + sx * 4, cy - 6),
                                      (cx + sx * 10, cy - 6)])


def main():
    sheet = pygame.Surface((TILE_W * COLS, TILE_H + 70))
    sheet.fill(BG)
    title = pygame.font.SysFont("dejavusans", 20, bold=True)
    sheet.blit(title.render("Clown-event BONE COLUMNS - 5 construction logics (ROUGH brainstorm)",
                            True, (255, 255, 255)), (16, 14))

    tiles = [
        (tile_totem,   ["1. STACKED-TOTEM", "skull-stupa tiers", "(borrows Stupika)"]),
        (tile_skewer,  ["2. SKEWER-THREADED", "vertebrae on a spike", "(borrows Nagaraja)"]),
        (tile_ribcage, ["3. HYBRID rib-cage", "spine+ribs / gem skull", "(Citipati+Asthi)"]),
        (tile_lattice, ["4. WOVEN LATTICE", "crossed-femur trellis", "(new logic)"]),
        (tile_drip,    ["5. BONE-CANDLE", "melted-wax drip taper", "(new logic)"]),
    ]
    for i, (fn, lbl) in enumerate(tiles):
        ox = i * TILE_W
        tile = sheet.subsurface((ox, 50, TILE_W, TILE_H))
        cx = TILE_W // 2
        # 58px column footprint guide
        pygame.draw.rect(tile, (90, 100, 118), (cx - PW // 2, 50, PW, TILE_H - 100), 1)
        fn(tile, cx)
        label(sheet, lbl, ox + 10, TILE_H + 8)

    out = "/home/user/skybit/docs/clown_bone_columns/brainstorm_round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
