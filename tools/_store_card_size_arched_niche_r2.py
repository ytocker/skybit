"""arched-niche card concept, round 2 — pointed Gothic/tombstone crown.

Round 1 read as a stretched dome: a semicircular crown and a sill that
collided with the ribbon, plus a hairline bezel. Round 2 raises the sill
clear of the ribbon, swaps the semicircle for a POINTED arch (two curved
sides cusping at a centered apex), fattens the gold bezel so a real band
survives the smoothscale to 1x, and deepens the interior toward the base
so the character reads as lit inside an alcove.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
import math
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

CARD_W_SS, CARD_H_SS = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324, 200
inset = sc.m(sc._INSET)
rect_ss = pygame.Rect(inset, inset, CARD_W_SS - 2 * inset, CARD_H_SS - 2 * inset)

# ── Arch geometry (SS coords) ───────────────────────────────────────────────
CX = 162
ARCH_W = 120
SHOULDER_Y = 70                 # springline: vertical sides meet the curved crown
SILL_Y = 118                    # raised from 160 so ribbon/name stay clear below
APEX_Y = 10                     # tip of the pointed crown
LEFT_X = CX - ARCH_W // 2       # 102
RIGHT_X = CX + ARCH_W // 2      # 222
# Bezier control pulled onto the centerline below the apex so both crown
# sides arrive vertical and cusp into a genuine point (not a rounded dome).
CTRL_Y = 44


def _bez(p0, cpt, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * cpt[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * cpt[1] + t * t * p2[1])


def _left_crown_pts(n=26):
    p0, cpt, p2 = (LEFT_X, SHOULDER_Y), (CX, CTRL_Y), (CX, APEX_Y)
    return [_bez(p0, cpt, p2, i / n) for i in range(n + 1)]


def _silhouette():
    """Full pointed-arch outline, clockwise from bottom-left."""
    left = _left_crown_pts()
    right = [(2 * CX - x, y) for (x, y) in reversed(left)]  # mirror the crown
    return ([(LEFT_X, SILL_Y), (LEFT_X, SHOULDER_Y)]
            + left + right
            + [(RIGHT_X, SHOULDER_Y), (RIGHT_X, SILL_Y)])


def _left_edge_x():
    """Left silhouette edge x per integer scanline y (crown curve + straight side)."""
    edge = {}
    for y in range(SHOULDER_Y, SILL_Y + 1):
        edge[y] = LEFT_X
    # Crown is monotonic in y (SHOULDER_Y down to APEX_Y); invert by dense sampling.
    for i in range(801):
        x, y = _bez((LEFT_X, SHOULDER_Y), (CX, CTRL_Y), (CX, APEX_Y), i / 800)
        yy = int(round(y))
        if yy in edge:
            edge[yy] = min(edge[yy], x) if yy > SHOULDER_Y else x
        edge[yy] = x if yy not in edge else (x if yy < SHOULDER_Y else edge[yy])
    return edge


def _inset_points(points, d, centroid):
    out = []
    for x, y in points:
        dx, dy = centroid[0] - x, centroid[1] - y
        n = math.hypot(dx, dy) or 1.0
        out.append((x + dx / n * d, y + dy / n * d))
    return out


def draw_arch_niche_on(surf):
    points = _silhouette()
    centroid = (CX, (SHOULDER_Y + SILL_Y) // 2)

    # ── 1. Silhouette mask ─────────────────────────────────────────────────
    mask = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)

    # ── 2. Interior gradient — lit alcove: light top, deep base + edges ─────
    body = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    TOP = (48, 54, 96)      # boosted upper zone so the character pops
    BOT = (5, 6, 18)        # deepened base beyond the stock glass low
    top_y, bot_y = APEX_Y, SILL_Y
    span = bot_y - top_y
    edge = _left_edge_x()
    for y in range(top_y, bot_y + 1):
        frac = (y - top_y) / span
        c = [TOP[i] * (1 - frac) + BOT[i] * frac for i in range(3)]
        # Deepen the bottom 30% (shoulder→sill) for alcove floor shadow.
        if frac > 0.7:
            k = 1 - 0.42 * (frac - 0.7) / 0.3
            c = [v * k for v in c]
        lx = edge.get(y, LEFT_X)
        rx = 2 * CX - lx
        col = tuple(int(v) for v in c)
        pygame.draw.line(body, (*col, 255), (int(lx), y), (int(rx), y))
        # Center core lifted a touch → reads as light falling into the niche.
        if rx - lx > 44:
            core = tuple(min(255, int(v * 1.14)) for v in c)
            pygame.draw.line(body, (*core, 255),
                             (int(lx) + 20, y), (int(rx) - 20, y))
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, 0))

    # ── 3. Tier aura behind the niche ──────────────────────────────────────
    glow = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    gcy = (APEX_Y + SILL_Y) // 2
    grad_r = 78
    for i in range(grad_r, 0, -3):
        pygame.draw.circle(glow, (100, 80, 40, int(34 * i / grad_r)),
                           (CX, gcy), i)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # ── 4. Hero thumbnail clipped to the arch ──────────────────────────────
    HERO_PX = 100
    hero = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.blit_thumb(hero, 'skin_mummy', CX, 66, HERO_PX)
    hero.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hero, (0, 0))

    # ── 5. Upper-left glint riding the crown curve ─────────────────────────
    sheen = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    for i, (x, y) in enumerate(_left_crown_pts()):
        if y > SHOULDER_Y - 8:
            continue
        a = int(70 * (1 - i / 26))
        if a > 4:
            pygame.draw.circle(sheen, (255, 248, 220, a), (int(x), int(y)), 3)
    surf.blit(sheen, (0, 0))

    # ── 6. Bold gold bezel: dark keyline, fat gold band, pale glint ────────
    key = _inset_points(points, -1.0, centroid)
    gold = _inset_points(points, 3.0, centroid)
    glint = _inset_points(points, 7.0, centroid)
    pygame.draw.polygon(surf, (*sc.CARD_RING_DEEP, 210), key, 2)
    pygame.draw.polygon(surf, (*sc.CARD_RING_BRIGHT, 230), gold, 6)
    pygame.draw.polygon(surf, (255, 246, 200, 110), glint, 2)


def render_baseline():
    sc._card_cache.clear()
    surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.draw_card(surf, 'skin_mummy', rect_ss, equipped=False, secret=False)
    return surf


def render_concept():
    sc._card_cache.clear()
    orig = (sc.cabochon, sc.cabochon_glass, sc.soft_glow, sc.blit_thumb)
    sc.cabochon = lambda *a, **kw: None
    sc.cabochon_glass = lambda *a, **kw: None
    sc.soft_glow = lambda *a, **kw: None
    sc.blit_thumb = lambda *a, **kw: None

    surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.draw_card(surf, 'skin_mummy', rect_ss, equipped=False, secret=False)

    (sc.cabochon, sc.cabochon_glass, sc.soft_glow, sc.blit_thumb) = orig
    sc._card_cache.clear()

    draw_arch_niche_on(surf)
    return surf


# ── Render + comparison sheet ───────────────────────────────────────────────
round1_ss = None  # concept-vs-concept not needed; show baseline vs new
baseline_ss = render_baseline()
concept_ss = render_concept()

GAP, PAD, LABEL_H, HEADER_H = 8, 16, 28, 40
sheet_w = PAD * 2 + 2 * CARD_W_SS + GAP
sheet_h = PAD * 2 + HEADER_H + LABEL_H + CARD_H_SS + GAP + LABEL_H + sc.CARD_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

fl = hud_font(14)
fh = hud_font(17)

title = fh.render("arched-niche round 2  ·  pointed crown, raised sill, bold bezel",
                  True, (240, 224, 180))
sheet.blit(title, (sheet_w // 2 - title.get_width() // 2,
                   (HEADER_H - title.get_height()) // 2))

for i, (lbl_text, s) in enumerate([
    ("BASELINE (2x)", baseline_ss),
    ("ARCHED-NICHE R2 (2x)", concept_ss),
]):
    x = PAD + i * (CARD_W_SS + GAP)
    lbl = fl.render(lbl_text, True, (200, 210, 228))
    sheet.blit(lbl, (x + CARD_W_SS // 2 - lbl.get_width() // 2, PAD + HEADER_H))
    sheet.blit(s, (x, PAD + HEADER_H + LABEL_H))

y1x = PAD + HEADER_H + LABEL_H + CARD_H_SS + GAP + LABEL_H
row_lbl = fl.render("at 1x  (162x100 final size)", True, (180, 180, 200))
sheet.blit(row_lbl, (PAD, y1x - LABEL_H))
for i, s in enumerate([baseline_ss, concept_ss]):
    x = PAD + i * (CARD_W_SS + GAP)
    small = pygame.transform.smoothscale(s, (sc.CARD_W, sc.CARD_H))
    sheet.blit(small, (x, y1x))

out = "docs/store_card_size/arched_niche/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
