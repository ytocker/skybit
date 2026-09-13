"""Headless review render for the `sash-accent` store-card v2 concept, round 2.

Explores the CONSTELLATION card DNA with the rarity read pulled OUT of a
centred ribbon and flown as a full-height coloured sash down the right margin,
so tier stays legible even in peripheral grid scroll. Reuses the locked
store_cards primitives so the exploration matches shipped card fidelity.

Round-2 revisions (art-director notes): the crest gem is relocated to the
top-LEFT indigo corner so it stops fighting the gold-on-gold LEGENDARY sash;
EPIC is pushed toward magenta-violet for colourblind separation from RARE blue;
the sash tier mark is enlarged to a single dark-keyed letter that reads on the
gold sash; the sash left edge gains a 2px dark keyline plus a bright body-facing
glint for a raised-ribbon read; the left-zone stack is re-centred so the disc no
longer leaves an awkward indigo channel; and a soft inner shadow inside the sash
keyline protects the disc as the value hero.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, price_chip, facet_gem, cabochon, cabochon_glass, blit_thumb,
    soft_glow, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, CREAM, GEM_R, CARD_RAD, CARD_W, CARD_H,
)

# ── panel geometry (draw the SS canvas directly — no smoothscale) ──────────────
PW, PH = CARD_W * SS, CARD_H * SS        # 324 x 200 author canvas per card


def draw_sash_card(sid, name, pal, price):
    """One sash-accent card onto its own 324x200 SRCALPHA surface."""
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    rad = m(CARD_RAD)
    rect = pygame.Rect(m(6), m(6), m(150), m(88))       # visible body 150x88
    body_x, body_y = rect.x, rect.y

    # disc re-centred in the left zone so it no longer leaves an empty indigo
    # channel between the disc and the sash
    cx_ss = body_x + m(64)
    cy_ss = body_y + m(40)
    R = 31

    # ── 1) body stack ─────────────────────────────────────────────────────────
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # neutral inner tray border (obsidian keyline under a faint gold lane)
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)
    # soft inner shadow on the body just inside the sash keyline — separates the
    # saturated sash from the disc so the disc stays the value hero
    ish_w = m(11)
    ish = pygame.Surface((ish_w, m(88)), pygame.SRCALPHA)
    for x in range(ish_w):
        a = int(78 * (x / max(1, ish_w - 1)) ** 1.7)
        pygame.draw.line(ish, (0, 0, 0, a), (x, 0), (x, m(88)))
    big.blit(ish, (body_x + m(122) - ish_w, body_y))

    # ── 2) full-height tier sash on the right 28px (top gem -> bottom deep) ─────
    sash = vgrad_stops(m(28), m(88), 0,
                       [(0.0, pal["gem"]), (0.5, pal["glow"]), (1.0, pal["deep"])],
                       255, gamma=1.0)
    big.blit(sash, (body_x + m(122), body_y))

    # ── 3) sash keyline: 2px dark contact line + a bright body-facing glint so
    #       the sash reads as a raised ribbon, not a printed band ───────────────
    pygame.draw.line(big, (4, 4, 14),
                     (body_x + m(122), body_y),
                     (body_x + m(122), body_y + m(88)), max(2, m(1.5)))
    glint = pygame.Surface((max(1, m(1)), m(88)), pygame.SRCALPHA)
    glint.fill((*pal["gem"], 90))
    big.blit(glint, (body_x + m(123), body_y))

    # ── 4) large dark-keyed tier letter on the sash — reads even on gold ───────
    tier = _TIER_FOR[sid]
    plain_text(big, tier[0], font(13), (body_x + m(136), body_y + m(44)),
               (250, 248, 230), shadow_a=0, weight=m(1.0),
               keyline=(30, 20, 8), kw=m(1.2))

    # ── 5) tier aura -> cabochon well -> skin thumbnail -> glass dome ──────────
    soft_glow(big, cx_ss, cy_ss, m(R + 3), pal["glow"], 30, layers=8)
    cabochon(big, cx_ss, cy_ss, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx_ss, cy_ss, m(R) * 1.5)
    cabochon_glass(big, cx_ss, cy_ss, m(R), tint=pal["gem"])

    # ── 6) item name below the disc, centred in the LEFT zone ─────────────────
    plain_text(big, name, font(12), (cx_ss, body_y + m(66)), CREAM,
               shadow_a=160, weight=m(0.8), keyline=(6, 6, 16), kw=m(0.8))
    # ── 7) canonical gold price chip, centred on the same left axis ───────────
    price_chip(big, cx_ss, body_y + m(78), f"{price:,}", m(18), affordable=True)

    # ── 8) crest gem MOVED to the top-LEFT indigo corner so it sits on dark
    #       indigo (not gold-on-gold on the sash) and stops fighting the sash ──
    facet_gem(big, body_x + m(15), body_y + m(15), m(10),
              pal["gem"], pal["deep"])

    # ── 9) crisp dark keyline UNDER the bright bevel, LAST, so the sash's outer
    #       corners clip cleanly into the rounded body edge ────────────────────
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big


_TIER_FOR = {
    "skin_lorikeet": "RARE",
    "skin_prism": "EPIC",
    "skin_kitsune": "LEGENDARY",
}

# EPIC is pushed toward magenta-violet (gem 180,80,255 / glow 140,40,230) so it
# separates from RARE blue under protanopia; RARE + LEGENDARY unchanged.
CARDS = [
    ("skin_lorikeet", "LORIKEET",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}, 600),
    ("skin_prism", "PRISM",
     {"gem": (180, 80, 255), "glow": (140, 40, 230), "deep": (44, 10, 80)}, 1400),
    ("skin_kitsune", "KITSUNE",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}, 3500),
]

# ── review sheet ──────────────────────────────────────────────────────────────
MARGIN, GUTTER, HEADER, FOOTER = 20, 16, 30, 26
STRIP_GAP = 14
sheet_w = MARGIN * 2 + PW * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER + PH + FOOTER + STRIP_GAP + CARD_H + FOOTER + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((22, 24, 34))

hf = font(11)
htxt = hf.render("store_card_v2 - sash-accent - round 2", True, (236, 238, 246))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER - htxt.get_height()) // 2))

ff = font(9)
sf = font(8)
strip_y = MARGIN + HEADER + PH + FOOTER + STRIP_GAP
for i, (sid, name, pal, price) in enumerate(CARDS):
    card = draw_sash_card(sid, name, pal, price)
    px = MARGIN + i * (PW + GUTTER)
    py = MARGIN + HEADER
    sheet.blit(card, (px, py))
    label = _TIER_FOR[sid]
    lt = ff.render(label, True, (214, 218, 230))
    sheet.blit(lt, (px + (PW - lt.get_width()) // 2,
                    py + PH + (FOOTER - lt.get_height()) // 2))

    # 1x strip beneath — the true in-game 162x100 card via ONE smoothscale
    small = pygame.transform.smoothscale(card, (CARD_W, CARD_H))
    sx = px + (PW - CARD_W) // 2
    sheet.blit(small, (sx, strip_y))
    st = sf.render(f"{label} @ 1x", True, (176, 182, 198))
    sheet.blit(st, (px + (PW - st.get_width()) // 2,
                    strip_y + CARD_H + (FOOTER - st.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v2/sash-accent/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
