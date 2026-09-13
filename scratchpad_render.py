import os, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (cabochon, cabochon_glass, blit_thumb, facet_gem,
    chip_body_stops, chip_body, vgrad_stops, vgrad, soft_glow, drop_shadow,
    bevel_rim, top_sheen, plain_text, price_chip, _glyph_base, font, m, SS)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK

# The shipped gloss_sweep clamps alpha via BLEND_RGBA_MIN on a white-alpha mask;
# on gold stock the additive white streak reads harsh, so use the softer fix.
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

# ── flight-clearance palette ──────────────────────────────────────────────────
GOLD_A_STOPS = [(0.00,(244,192,88)),(0.32,(228,162,56)),(0.66,(196,124,34)),(1.00,(150,92,18))]
GOLD_RIM_DK = (86, 50, 8)
GOLD_RIM_BR = (255, 240, 190)
pal = {"gem": (255, 202, 104), "glow": (255, 168, 58), "deep": (150, 92, 22)}

# warm ticket stock (affordable) vs washed-out cold stub (can't-afford)
STOCK_WARM = [(0.0, (208, 156, 46)), (0.5, (186, 130, 34)), (1.0, (140, 90, 18))]
STOCK_COLD = [(0.0, (120, 124, 138)), (0.5, (96, 100, 116)), (1.0, (64, 68, 84))]

POP_W, POP_H = 232, 292
CARD_RAD = 15
R_DISC = 44
CX = POP_W // 2
CY_DISC = 148

STAMP_INK_WARM = (108, 30, 12)
STAMP_INK_COLD = (60, 64, 80)


def _perf_row(surf, y, x0, x1, ink):
    """A dotted tear-off perforation across the stub — the boarding-ticket read."""
    x = x0
    step = m(7)
    while x <= x1:
        pygame.draw.circle(surf, ink, (x, y), max(1, m(1.3)))
        x += step


def _side_notches(surf, body, ink_bg, n=9):
    """Punched notches down the LEFT edge = the ticket's tear-off spine. Cut by
    painting bg-coloured discs so the stock reads perforated, not printed-on."""
    top = body.y + m(10)
    span = body.h - m(20)
    for i in range(n):
        yy = int(top + span * i / (n - 1))
        pygame.draw.circle(surf, ink_bg, (body.x, yy), m(3))


def _stamp(text_big, text_small, ink, alpha):
    """Rubber-approval stamp on its own SRCALPHA surface: a double rect ring +
    a small header line + a bold verdict word, then rotated so the ink strikes
    the hero art at an angle like a real clearance stamp."""
    W, H = m(150), m(66)
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    ring = pygame.Rect(m(4), m(4), W - m(8), H - m(8))
    pygame.draw.rect(s, ink, ring, width=max(1, m(2.2)), border_radius=m(4))
    pygame.draw.rect(s, ink, ring.inflate(-m(5), -m(5)), width=max(1, m(1)),
                     border_radius=m(3))
    fs = font(9)
    plain_text(s, text_small, fs, (W // 2, m(17)), ink, shadow_a=0,
               tracking=m(2.4), weight=m(0.5))
    fb = font(21)
    plain_text(s, text_big, fb, (W // 2, m(42)), ink, shadow_a=0,
               tracking=m(2), weight=m(1.2))
    rot = pygame.transform.rotate(s, 20)
    rot.set_alpha(alpha)
    return rot


def _confirm_chip(surf, cx, cy, h, affordable):
    text = "CONFIRM"
    f = font(h * 0.46 / SS)
    nw = _glyph_base(text, f, m(1.4)).get_width()
    pad = m(20)
    w = nw + pad * 2
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if affordable:
        chip_body_stops(surf, r, h // 2, GOLD_A_STOPS, GOLD_RIM_DK, GOLD_RIM_BR,
                        gloss=64, gamma=1.04)
        col, kl = (54, 30, 4), None
    else:
        chip_body(surf, r, h // 2, (92, 98, 120), (50, 54, 74), (14, 16, 26),
                  (160, 168, 190), gloss=44)
        col, kl = (196, 202, 220), (20, 24, 38)
    plain_text(surf, text, f, r.center, col, shadow_a=0, tracking=m(1.4),
               weight=m(1.0), keyline=kl, kw=m(0.7))
    return r


def render_popup(affordable):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    body = pygame.Rect(m(8), m(8), POP_W * SS - m(16), POP_H * SS - m(16))
    rad = m(CARD_RAD)

    drop_shadow(big, body, rad, blur=m(7), alpha=155, dy=m(4))

    stops = STOCK_WARM if affordable else STOCK_COLD
    big.blit(vgrad_stops(body.w, body.h, rad, stops, 255, gamma=1.12),
             body.topleft)
    top_sheen(big, body, rad, m(26), peak=48 if affordable else 30)

    # crisp keyline under a warm bevel rim
    edge_dk = (58, 34, 6) if affordable else (18, 20, 30)
    edge_br = GOLD_RIM_BR if affordable else (176, 184, 206)
    pygame.draw.rect(big, edge_dk, body, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, body, rad, edge_dk, (*edge_br, 230), w=max(1, m(1.8)))

    # inner tray keyline so the stock reads as a printed card face
    tray = body.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*edge_br, 70), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))

    # left-spine notches (bg-coloured punch-outs)
    _side_notches(big, body, (8, 8, 20, 0))

    # ── LEGENDARY top banner — the dominant, first-read line ──────────────────
    leg_col = (52, 30, 4) if affordable else (206, 212, 228)
    leg_kl = (255, 236, 176) if affordable else (36, 40, 54)
    lf = font(29)
    while _glyph_base("LEGENDARY", lf, m(1.6)).get_width() > body.w - m(20):
        lf = font(lf.get_height() / SS - 1)
    plain_text(big, "LEGENDARY", lf, (CX * SS, body.y + m(24)), leg_col,
               shadow_a=90 if affordable else 60, tracking=m(1.6),
               weight=m(1.3), keyline=leg_kl, kw=m(0.9))
    # thin rule beneath the banner
    ry = body.y + m(40)
    pygame.draw.line(big, (*edge_dk, 180), (body.x + m(16), ry),
                     (body.right - m(16), ry), max(1, m(1)))

    # ── central medallion disc = the card's hero art ─────────────────────────
    cx, cy = CX * SS, m(CY_DISC)
    soft_glow(big, cx, cy, m(R_DISC + 5), pal["glow"],
              44 if affordable else 12, layers=9)
    from game.store_cards import CABO_LO, CABO_HI
    cabochon(big, cx, cy, m(R_DISC), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    try:
        blit_thumb(big, "skin_base", cx, cy, int(m(R_DISC) * 1.5))
    except Exception:
        pygame.draw.circle(big, (*pal["gem"], 255), (cx, cy), int(m(R_DISC) * 0.7))
    cabochon_glass(big, cx, cy, m(R_DISC), tint=pal["gem"])
    if not affordable:
        # wash the hero cold when unaffordable
        veil = pygame.Surface((m(R_DISC) * 2 + m(8), m(R_DISC) * 2 + m(8)),
                              pygame.SRCALPHA)
        pygame.draw.circle(veil, (40, 44, 60, 150),
                           (m(R_DISC) + m(4), m(R_DISC) + m(4)), m(R_DISC))
        big.blit(veil, (cx - m(R_DISC) - m(4), cy - m(R_DISC) - m(4)))

    # ── diagonal clearance stamp striking across the CENTER over the disc ────
    ink = STAMP_INK_WARM if affordable else STAMP_INK_COLD
    stamp = _stamp("CLEARED", "SKY CAPTAIN", ink, 205 if affordable else 150)
    sr = stamp.get_rect(center=(cx, cy + m(2)))
    big.blit(stamp, sr.topleft)

    # ── lower stub: perforation, price, CONFIRM ──────────────────────────────
    stub_y = body.y + m(196)
    _perf_row(big, stub_y, body.x + m(14), body.right - m(14), edge_dk)
    # notch cut-outs flanking the perforation = the tear line
    pygame.draw.circle(big, (8, 8, 20, 0), (body.x, stub_y), m(4))
    pygame.draw.circle(big, (8, 8, 20, 0), (body.right, stub_y), m(4))

    price_chip(big, cx, body.y + m(226), "12,000", m(21), affordable=affordable)
    _confirm_chip(big, cx, body.y + m(256), m(23), affordable)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── compose the two-state review canvas ───────────────────────────────────────
CANVAS_W, CANVAS_H = 500, 380
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

lab = _font(15, True)
for i, (aff, tag) in enumerate([(True, "AFFORDABLE"), (False, "CAN'T AFFORD")]):
    pop = render_popup(aff)
    half_cx = CANVAS_W // 4 + i * (CANVAS_W // 2)
    px = half_cx - POP_W // 2
    py = (CANVAS_H - POP_H) // 2 + 6
    canvas.blit(pop, (px, py))
    t = lab.render(tag, True, (210, 214, 230))
    canvas.blit(t, t.get_rect(center=(half_cx, py - 12)))

out = "/home/user/skybit/docs/confirm_purchase_v4/flight-clearance/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
