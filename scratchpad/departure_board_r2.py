import os, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import numpy as np
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (cabochon, cabochon_glass, blit_thumb,
    vgrad_stops, vgrad, soft_glow, drop_shadow, bevel_rim, top_sheen,
    plain_text, price_chip,
    CARD_T, CARD_B, CABO_LO, CABO_HI, CARD_RING_DEEP, CARD_RING_BRIGHT, m)
from game.hud import _font


# The stock additive gloss clips to a white slab at popup scale; the eased
# version stays a translucent sheen.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

# A softer cabochon specular so the disc highlight lands near ~200, not 250.
sc.CABO_SPEC_A = 88


# ── palette ─────────────────────────────────────────────────────────────────
pal = {"gem": (255, 202, 104), "glow": (255, 168, 58), "deep": (150, 92, 22)}
WARM_SAFE = (60, 40, 12)

POP_W, POP_H = 210, 300
CARD_RAD = 16


# ── luminance cap so the header glyphs win the hierarchy ──────────────────────
def cap_region(surf, rect, maxv):
    """Clamp every RGB channel in a rect so nothing there out-shines the header.
    Alpha is untouched, so the rounded-card clip that follows still reads."""
    x0, y0, w, h = rect
    arr = pygame.surfarray.pixels3d(surf)
    x1, y1 = min(x0 + w, arr.shape[0]), min(y0 + h, arr.shape[1])
    x0, y0 = max(0, x0), max(0, y0)
    np.minimum(arr[x0:x1, y0:y1], maxv, out=arr[x0:x1, y0:y1])
    del arr


# ── split-flap character tile ─────────────────────────────────────────────────
def flap_cell(surf, x, y, w, h, letter, affordable):
    """One departure-board character tile. The mid-height fold seam — top half
    lighter, bottom half darker, a dark seam groove with a bright lip below it —
    is what makes the row read as mechanical split-flap and not a rounded chip.
    The glyph spans the seam (never split) and is the brightest thing on screen."""
    if affordable:
        top_c = (52, 46, 70)          # top leaf catches more light
        bot_c = (30, 26, 44)          # bottom leaf falls into shadow
        seam_dark = (11, 9, 18)
        seam_lip = (74, 66, 92)
        glyph_c = (252, 232, 186)     # bright warm gold, luminance ~233
        frame_c = (8, 8, 14)
        top_glint = (86, 76, 104)
    else:
        top_c = (46, 50, 68)          # drained cold blue-grey leaves
        bot_c = (28, 31, 46)
        seam_dark = (12, 14, 22)
        seam_lip = (60, 66, 86)
        glyph_c = (176, 190, 214)     # cold, dimmer glyph
        frame_c = (8, 9, 16)
        top_glint = (66, 72, 92)
    seam_y = h // 2
    rad = 3
    # top leaf (rounded only on the top corners so the seam edge stays square)
    pygame.draw.rect(surf, top_c, (x, y, w, seam_y),
                     border_top_left_radius=rad, border_top_right_radius=rad)
    # bottom leaf (rounded only on the bottom corners)
    pygame.draw.rect(surf, bot_c, (x, y + seam_y, w, h - seam_y),
                     border_bottom_left_radius=rad, border_bottom_right_radius=rad)
    # a hair of top-edge glint sells the leaf catching light from above
    pygame.draw.line(surf, top_glint, (x + 2, y + 1), (x + w - 3, y + 1))
    # the fold: a dark groove at the midpoint, a bright lip just under it
    pygame.draw.line(surf, seam_dark, (x, y + seam_y), (x + w - 1, y + seam_y))
    pygame.draw.line(surf, seam_lip, (x, y + seam_y + 1), (x + w - 1, y + seam_y + 1))
    # black tile frame — the gaps between Solari tiles
    pygame.draw.rect(surf, frame_c, (x, y, w, h), width=1,
                     border_radius=rad)
    # glyph, spanning the seam
    gf = _font(int(h * 0.72), True)
    g = gf.render(letter, True, glyph_c)
    surf.blit(g, g.get_rect(center=(x + w // 2, y + h // 2)))


def flap_row(surf, word, cx, top_y, cell_w, cell_h, gap, affordable):
    n = len(word)
    total = n * cell_w + (n - 1) * gap
    x = cx - total // 2
    for ch in word:
        flap_cell(surf, x, top_y, cell_w, cell_h, ch, affordable)
        x += cell_w + gap
    return pygame.Rect(cx - total // 2, top_y, total, cell_h)


# ── the item disc ─────────────────────────────────────────────────────────────
def _disc(sid="skin_classic", r=38, cap=200):
    DS = r * 2 + 40
    ss = pygame.Surface((DS, DS), pygame.SRCALPHA)
    c = DS // 2
    cabochon(ss, c, c, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=18)
    try:
        blit_thumb(ss, sid, c, c, int(r * 1.5))
    except Exception:
        pygame.draw.circle(ss, (*pal["gem"], 255), (c, c), int(r * 0.7))
    cabochon_glass(ss, c, c, r, tint=pal["gem"])
    disc = pygame.transform.smoothscale(ss, (r * 2, r * 2))
    # cap the disc so its specular sits just below the header glyphs
    arr = pygame.surfarray.pixels3d(disc)
    np.minimum(arr, cap, out=arr)
    del arr
    return disc


# ── header emitter panel ──────────────────────────────────────────────────────
def _header(surf, rect, word, affordable):
    """The dominant split-flap board that owns the top ~40% and wins the
    luminance read. A recessed dark board carries the LEGENDARY tile row; a low
    warm under-glow proves the board is lit without lifting the cell faces above
    the glyphs."""
    if affordable:
        board = vgrad_stops(rect.w, rect.h, 6,
                            [(0.0, (26, 22, 40)), (1.0, (16, 13, 28))], 255)
    else:
        board = vgrad_stops(rect.w, rect.h, 6,
                            [(0.0, (24, 26, 42)), (1.0, (15, 17, 30))], 255)
    surf.blit(board, rect.topleft)
    # inset top shadow so the board reads recessed into the card
    ins = pygame.Surface((rect.w, 8), pygame.SRCALPHA)
    for y in range(8):
        a = int(120 * (1 - y / 8))
        pygame.draw.line(ins, (0, 0, 0, a), (0, y), (rect.w, y))
    surf.blit(ins, (rect.x, rect.y))
    # low warm under-glow behind the tile row (safe warm, kept dim)
    if affordable:
        soft_glow(surf, rect.centerx, rect.y + int(rect.h * 0.56),
                  int(rect.w * 0.44), WARM_SAFE, 46, layers=5)
    # board caption above the tiles
    cap_c = (196, 150, 78) if affordable else (150, 158, 178)
    plain_text(surf, "NOW BOARDING", _font(11, True),
               (rect.centerx, rect.y + 22), cap_c, shadow_a=110, tracking=3,
               weight=m(0.6))
    # the hero tile row
    cell_w, cell_h, gap = 18, 56, 2
    n = len(word)
    total = n * cell_w + (n - 1) * gap
    row_top = rect.y + rect.h - cell_h - 18
    flap_row(surf, word, rect.centerx, row_top, cell_w, cell_h, gap, affordable)
    # a thin board lip under the tiles
    lip_c = (150, 120, 60) if affordable else (96, 104, 126)
    pygame.draw.line(surf, lip_c,
                     (rect.centerx - total // 2, row_top + cell_h + 6),
                     (rect.centerx + total // 2, row_top + cell_h + 6))


# ── base-row action buttons ───────────────────────────────────────────────────
def _confirm(surf, rect, radius, affordable):
    drop_shadow(surf, rect, radius, blur=5, alpha=110, dy=2)
    if affordable:
        # a deliberately restrained gold so CONFIRM stays under the disc read
        surf.blit(vgrad_stops(rect.w, rect.h, radius,
                  [(0.0, (206, 158, 78)), (1.0, (150, 100, 34))], 255,
                  gamma=1.05), rect.topleft)
        top_sheen(surf, rect, radius, int(rect.h * 0.4), peak=22)
        bevel_rim(surf, rect, radius, (78, 46, 8), (236, 206, 150, 200), w=2)
        tc, key = (34, 22, 6), None
    else:
        surf.blit(vgrad_stops(rect.w, rect.h, radius,
                  [(0.0, (78, 82, 100)), (1.0, (44, 48, 64))], 255), rect.topleft)
        bevel_rim(surf, rect, radius, (16, 18, 28), (132, 140, 160, 190), w=2)
        tc, key = (196, 202, 218), None
    plain_text(surf, "CONFIRM", _font(14, True), rect.center, tc, shadow_a=0,
               tracking=1, weight=m(0.6), keyline=key)


def _cancel(surf, rect, radius, affordable):
    ghost = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(ghost, (18, 16, 30, 210), ghost.get_rect(), border_radius=radius)
    edge = (196, 158, 96, 60) if affordable else (150, 158, 178, 70)
    pygame.draw.rect(ghost, edge, ghost.get_rect(), width=1, border_radius=radius)
    surf.blit(ghost, rect.topleft)
    tc = (196, 184, 156) if affordable else (176, 184, 202)
    plain_text(surf, "CANCEL", _font(14, True), rect.center, tc, shadow_a=90,
               tracking=1, weight=m(0.5))


# ── popup ─────────────────────────────────────────────────────────────────────
def build_popup(affordable):
    pop = pygame.Surface((POP_W, POP_H), pygame.SRCALPHA)
    cx = POP_W // 2

    pop.blit(vgrad(POP_W, POP_H, CARD_RAD, CARD_T, CARD_B, 255, gamma=1.15), (0, 0))

    # header board across the top ~40%
    hdr = pygame.Rect(9, 9, POP_W - 18, 120)
    _header(pop, hdr, "LEGENDARY", affordable)

    # item disc, framed like a board window directly below the tiles. Halo is
    # suppressed — the disc is lit by the board above, it does not self-emit.
    disc_cy = 173
    disc_r = 38
    win = pygame.Rect(cx - 44, 130, 88, 86)
    pop.blit(vgrad_stops(win.w, win.h, 8,
             [(0.0, (20, 17, 34)), (1.0, (12, 10, 24))], 255), win.topleft)
    wins = pygame.Surface((win.w, 8), pygame.SRCALPHA)
    for y in range(8):
        pygame.draw.line(wins, (0, 0, 0, int(110 * (1 - y / 8))), (0, y), (win.w, y))
    pop.blit(wins, win.topleft)
    key_c = (150, 120, 60) if affordable else (86, 94, 116)
    pygame.draw.rect(pop, key_c, win, width=1, border_radius=8)

    disc = _disc(r=disc_r, cap=200 if affordable else 168)
    pop.blit(disc, disc.get_rect(center=(cx, disc_cy)))
    if not affordable:
        cold = pygame.Surface((disc_r * 2, disc_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(cold, (58, 84, 140, 104), (disc_r, disc_r), disc_r)
        pop.blit(cold, cold.get_rect(center=(cx, disc_cy)))

    # base row: price flap-tag centred, then two full-width buttons — no dead cell
    price_chip(pop, cx, 231, "12,000", m(12), affordable=affordable)
    pad, gap = 12, 10
    bw = (POP_W - pad * 2 - gap) // 2
    by, bh = 251, 32
    _cancel(pop, pygame.Rect(pad, by, bw, bh), 16, affordable)
    _confirm(pop, pygame.Rect(POP_W - pad - bw, by, bw, bh), 16, affordable)

    # cap the whole lower third so price + buttons sit under the disc read
    cap_region(pop, (4, 216, POP_W - 8, POP_H - 216), 190 if affordable else 182)

    # inner keyline + card bevel, inside the silhouette
    pygame.draw.rect(pop, (*CARD_RING_BRIGHT, 60),
                     pygame.Rect(4, 4, POP_W - 8, POP_H - 8), width=1,
                     border_radius=CARD_RAD - 3)
    pygame.draw.rect(pop, (4, 5, 16), pop.get_rect(), width=2, border_radius=CARD_RAD)
    bevel_rim(pop, pop.get_rect(), CARD_RAD, CARD_RING_DEEP,
              (*CARD_RING_BRIGHT, 210), w=2)

    # clip to the rounded card silhouette
    mask = pygame.Surface((POP_W, POP_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=CARD_RAD)
    pop.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return pop


# ── showcase canvas ───────────────────────────────────────────────────────────
CW, CH = 500, 380
canvas = pygame.Surface((CW, CH))
canvas.fill((8, 8, 20))

title_f = _font(15, True)
tsurf = title_f.render("DEPARTURE-BOARD  ·  confirm purchase v3  ·  r2", True,
                       (150, 150, 170))
canvas.blit(tsurf, tsurf.get_rect(center=(CW // 2, 20)))

py = 44
for px, aff, cap in ((32, True, "AFFORDABLE"), (258, False, "CAN'T AFFORD")):
    rect = pygame.Rect(px, py, POP_W, POP_H)
    drop_shadow(canvas, rect, CARD_RAD, blur=14, alpha=150, dy=6)
    if aff:
        # the board's bloom spilling onto the scrim past the card edge
        soft_glow(canvas, rect.centerx, rect.y + 60, 96, (26, 16, 5), 54, layers=5)
    pop = build_popup(aff)
    canvas.blit(pop, rect.topleft)
    cs = _font(12, True).render(cap, True, (190, 190, 205) if aff else (150, 152, 168))
    canvas.blit(cs, cs.get_rect(center=(rect.centerx, rect.bottom + 14)))

out = "/home/user/skybit/docs/confirm_purchase_v3/departure-board/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
