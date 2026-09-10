"""Render docs/dead_pip_v3/round_2.png — Round 2 of the dead-Pip v3 redesign.

Round 1 verdict: ITERATE. The lead palette E (NIGHT-VAPOR DARK) was kept,
but two mechanical fixes are folded in here:
  - Tighter pupil glow (the previous bar of yellow blurred into one
    bright horizontal stripe at native scale).
  - Faint sickly aura DRAWN BEFORE the body, so the body sits on top
    of the halo and the halo only reads as an outer "wrongness" cue.

Alternates B (CHARTREUSE ECTOPLASM) and C (WITHERED BRUISE) are polished
so the user keeps real options:
  - B differentiated from the existing ghost-Pip ECTOPLASM palette by
    pushing the chartreuse hotter / more yellow + adding the same toxic
    aura as E (so B and E read as palette siblings).
  - C's X-strokes thinned to 1 px in the lens-frame colour, and the chest
    band's value pulled down ~15% so the head reads before the chest.

Off-track Round 1 candidates A (ASHEN) and D (FADING SCARLET) are
deliberately dropped from this sheet.

The cross-fade strip at the bottom is re-rendered against the tightened
E build — and the aura alpha now scales with t so early frames don't
look "haunted while still alive."
"""
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.parrot import SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _build_frame
from game.draw import blit_glow, UI_GOLD, UI_CREAM


# ── output target ────────────────────────────────────────────────────────────

OUT_PATH = pathlib.Path(__file__).parent.parent / "docs" / "dead_pip_v3" / "round_2.png"
BG_DAWN  = (38, 44, 66)
CARD_BG  = (24, 28, 42)
CARD_EDGE = (60, 68, 90)
TEXT_HI  = (235, 240, 250)
TEXT_LO  = (165, 175, 195)

# Neutral wing pose — matches Round 1 so reviewers compare like-for-like.
WING_ANGLE = _WING_ANGLES[1]   # 20°

# Lens centres in body-surface space — same as parrot-ghost eye code uses.
LENS_L = (46, 20)
LENS_R = (56, 19)

# Shared toxic aura colour — locks E and B into the same "wrongness" family.
TOXIC_AURA = (90, 220, 80)


def _font(size: int) -> pygame.font.Font:
    """Bundled Bold font is the only ttf we ship; use it for all UI text."""
    path = pathlib.Path(__file__).parent.parent / "game" / "assets" / "LiberationSans-Bold.ttf"
    return pygame.font.Font(str(path), size)


def _text(surf, msg, pos, size=14, color=TEXT_HI, shadow=True):
    f = _font(size)
    img = f.render(msg, True, color)
    if shadow:
        sh = f.render(msg, True, (0, 0, 0))
        surf.blit(sh, (pos[0] + 1, pos[1] + 1))
    surf.blit(img, pos)
    return img.get_size()


# ── PALETTE E — NIGHT-VAPOR DARK (ship lead) ────────────────────────────────
# Dark poisoned spectre — palette unchanged from Round 1. The two fixes are
# in build_nightvapor_dead below: tighter pupil + single faint outer aura.

P_NIGHTVAPOR = _pal(
    tail=[(28, 35, 30), (40, 50, 40), (55, 70, 50), (70, 90, 55)],
    tail_line=(15, 22, 18),
    body_shadow=(12, 18, 18),
    body_main=(40, 55, 45),
    body_chest=(60, 80, 55),
    body_belly=(85, 110, 70),
    sheen=(160, 200, 120, 90),
    wing_main=(30, 25, 55),
    wing_dark=(12, 10, 28),
    wing_tip=(70, 95, 50),
    wing_secondary=None,
    wing_highlight=(160, 200, 110),
    head_shadow=(15, 22, 22),
    head_main=(45, 60, 50),
    head_cheek=(65, 85, 60),
    head_crown=(80, 105, 70),
    lens_frame=(120, 170, 60),
    lens_body=(8, 12, 8),
    lens_tint=None,
    lens_glint=None,         # replaced below — tight glowing pupils
    beak_main=(85, 95, 60),
    beak_dark=(35, 40, 25),
    beak_gloss=(160, 190, 110),
    foot=(20, 28, 22),
)

def build_nightvapor_dead(angle_deg, aura_scale=1.0):
    """Dark poisoned spectre, P_POSSESSED-style eye recipe (radius 5, alpha
    220, 2 px disc, 1 px highlight) but retinted poison yellow-green.

    `aura_scale` lets the cross-fade strip fade the halo proportionally
    with t — at t≤0.33 the aura is barely there, so the bird doesn't
    look "haunted while still alive."
    """
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Single faint sickly halo — matches P_WRAITH's aura recipe so the
    # body still pops on bright skies but the glow never overwhelms it.
    aura_alpha = max(0, min(255, int(110 * aura_scale)))
    if aura_alpha > 0:
        blit_glow(out, 32, 30, 24, TOXIC_AURA, alpha=aura_alpha)
    body = _build_parrot_with_palette(angle_deg, P_NIGHTVAPOR)
    out.blit(body, (0, 0))
    # Tight glowing pupils — mirrors P_POSSESSED's recipe verbatim, but
    # retinted to a poisonous yellow-green core. Radius 5 + 2 px disc
    # leaves a visible ring of dark `lens_body` around each pupil so the
    # two eyes never blob into one bar at native scale.
    for ex, ey in (LENS_L, LENS_R):
        blit_glow(out, ex, ey, 5, (180, 230, 80), alpha=220)
        pygame.draw.circle(out, (210, 245, 110), (ex, ey), 2)
        pygame.draw.circle(out, (245, 255, 200), (ex - 1, ey - 1), 1)
    return out


# ── PALETTE B — CHARTREUSE ECTOPLASM (alternate, pushed hotter) ─────────────
# Round 1 B sat too close to the ghost-Pip ECTOPLASM palette (mint green).
# Here we push the chartreuse hotter and yellower — `body_main=(190,220,70)`
# instead of mint — and reuse the same TOXIC_AURA as E so B reads as E's
# sibling, not the ghost-Pip's sibling.

P_CHARTREUSE = _pal(
    tail=[(110, 140, 25), (150, 175, 35), (185, 205, 50), (215, 225, 75)],
    tail_line=(70, 90, 20),
    body_shadow=(85, 105, 25),
    body_main=(190, 220, 70),
    body_chest=(210, 230, 95),
    body_belly=(225, 235, 130),
    sheen=(245, 250, 180, 120),
    wing_main=(140, 165, 35),
    wing_dark=(65, 85, 15),
    wing_tip=(210, 225, 70),
    wing_secondary=(230, 235, 110),
    wing_highlight=(240, 240, 160),
    head_shadow=(90, 110, 30),
    head_main=(195, 220, 75),
    head_cheek=(215, 230, 100),
    head_crown=(225, 235, 130),
    lens_frame=(70, 90, 20),       # dark sunken rim
    lens_body=(10, 18, 8),         # near-black socket
    lens_tint=None,
    lens_glint=None,               # no glint — empty socket
    beak_main=(190, 180, 60),
    beak_dark=(105, 95, 20),
    beak_gloss=(230, 225, 140),
    foot=(70, 85, 20),
)

def build_chartreuse_dead(angle_deg):
    """Hot toxic chartreuse + hollow sockets + shared E-family aura."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Shared toxic aura — same colour + alpha as E so the two read as
    # siblings in the "dead-bird" family, not as the ghost-Pip sibling.
    blit_glow(out, 32, 30, 24, TOXIC_AURA, alpha=110)
    body = _build_parrot_with_palette(angle_deg, P_CHARTREUSE)
    # Deepen the sockets a hair so the hollow read holds against the bright
    # yellow-chartreuse body. Drawn on the body surface, palette colours
    # only — no per-pixel tinting, no sub-canvas icon stamp.
    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.circle(body, (5, 10, 5), (cx, cy), 3)
        # Tiny rim shadow at top — gives the socket apparent depth
        pygame.draw.line(body, (45, 60, 20), (cx - 2, cy - 2), (cx + 2, cy - 2), 1)
    out.blit(body, (0, 0))
    return out


# ── PALETTE C — WITHERED BRUISE (alternate, polished) ───────────────────────
# Two fixes vs Round 1:
#   - Chest band pulled down ~15% (multiplied by 0.85) so the head reads
#     first instead of competing with the bright chartreuse belly.
#   - X-strokes thinned to 1 px and re-coloured to a dimmer lens_frame
#     purple so the X reads as part of the lens, not as a pasted sticker.

# Round 1 chest/belly values, multiplied by 0.85 — keeps the bruise hue
# but pulls value down so the head sits above the chest in the visual
# hierarchy.
def _dim(rgb, k=0.85):
    return tuple(max(0, min(255, int(c * k))) for c in rgb)

P_BRUISE = _pal(
    tail=[(80, 50, 95), (110, 75, 105), (155, 145, 90), (190, 200, 100)],
    tail_line=(50, 28, 65),
    body_shadow=(55, 30, 75),
    body_main=(110, 90, 110),
    body_chest=_dim((150, 145, 105)),     # was (150,145,105) — dimmed 15%
    body_belly=_dim((180, 190, 110)),     # was (180,190,110) — dimmed 15%
    sheen=(200, 200, 140, 80),            # sheen alpha pulled too
    wing_main=(70, 45, 90),
    wing_dark=(35, 18, 55),
    wing_tip=(160, 170, 80),
    wing_secondary=(195, 200, 95),
    wing_highlight=(215, 220, 130),
    head_shadow=(60, 35, 80),
    head_main=(115, 95, 115),
    head_cheek=(150, 140, 105),
    head_crown=(175, 185, 110),
    lens_frame=(95, 60, 115),            # dimmer purple — X will sit IN this
    lens_body=(170, 180, 100),           # sickly green lens body
    lens_tint=None,
    lens_glint=None,
    beak_main=(135, 120, 80),
    beak_dark=(60, 40, 30),
    beak_gloss=(190, 185, 120),
    foot=(50, 28, 65),
)

def build_bruise_dead(angle_deg):
    """Bruised eggplant + dimmed chest band, slim 1 px X in lens-frame purple."""
    body = _build_parrot_with_palette(angle_deg, P_BRUISE)
    # Slim X — 1 px, in lens_frame purple. Reads as engraved into the
    # lens body rather than stamped on top of it.
    x_ink = (95, 60, 115)
    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.line(body, x_ink, (cx - 3, cy - 3), (cx + 3, cy + 3), 1)
        pygame.draw.line(body, x_ink, (cx - 3, cy + 3), (cx + 3, cy - 3), 1)
    return body


# ── panel registry ───────────────────────────────────────────────────────────
# E first — it's the ship lead. B and C below — kept as alternates.

PANELS = [
    ("E. NIGHT-VAPOR DARK",
     "LEAD — dark poisoned spectre. Tighter pupil glow + faint sickly aura drawn before the body.",
     build_nightvapor_dead, True),
    ("B. CHARTREUSE ECTOPLASM",
     "Alternate — hot yellow-chartreuse hollow-socket palette + shared E-family toxic aura.",
     build_chartreuse_dead, False),
    ("C. WITHERED BRUISE",
     "Alternate — eggplant + chartreuse bruise palette, slim 1 px X in lens-frame purple, chest band dimmed.",
     build_bruise_dead, False),
]


# ── layout helpers ───────────────────────────────────────────────────────────

NATIVE = (SPRITE_W + 4, SPRITE_H + 4)   # outlined body padded by _add_outline
ZOOM   = 4
ZOOMED = (NATIVE[0] * ZOOM, NATIVE[1] * ZOOM)

PANEL_W = 1200
PANEL_H = 200
PANEL_PAD = 16
PANEL_GAP = 12


def _panel_card(label, blurb, build_fn, is_lead):
    """One panel: native sprite (left), 4× zoom (right), header text on top."""
    card = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(card, CARD_BG, card.get_rect(), border_radius=10)
    pygame.draw.rect(card, CARD_EDGE, card.get_rect(), width=1, border_radius=10)

    # Header — lead panel gets a gold LEAD badge on the right so it scans first
    _text(card, label, (PANEL_PAD, 10), size=18, color=UI_GOLD)
    _text(card, blurb, (PANEL_PAD, 34), size=13, color=TEXT_LO)
    if is_lead:
        badge_w = 90
        badge_rect = pygame.Rect(PANEL_W - PANEL_PAD - badge_w, 12, badge_w, 22)
        pygame.draw.rect(card, (90, 70, 25), badge_rect, border_radius=4)
        pygame.draw.rect(card, UI_GOLD, badge_rect, width=1, border_radius=4)
        f = _font(13)
        img = f.render("SHIP LEAD", True, UI_GOLD)
        sh = f.render("SHIP LEAD", True, (0, 0, 0))
        r = img.get_rect(center=badge_rect.center)
        card.blit(sh, (r.x + 1, r.y + 1))
        card.blit(img, r.topleft)

    # Build sprite — _add_outline so dead-Pip pops on the teal card
    sprite = _add_outline(build_fn(WING_ANGLE))
    sw, sh = sprite.get_size()
    zoomed = pygame.transform.scale(sprite, (sw * ZOOM, sh * ZOOM))

    # Native swatch (dawn-teal patch) on the left
    art_y = 60
    sw_box = pygame.Rect(PANEL_PAD, art_y, sw + 16, sh + 16)
    pygame.draw.rect(card, BG_DAWN, sw_box, border_radius=6)
    pygame.draw.rect(card, CARD_EDGE, sw_box, width=1, border_radius=6)
    card.blit(sprite, (sw_box.x + 8, sw_box.y + 8))
    _text(card, "1x native", (sw_box.x, sw_box.bottom + 4), size=10, color=TEXT_LO, shadow=False)

    # 4× zoom box on the right
    zoom_box = pygame.Rect(PANEL_PAD + sw_box.w + 28, art_y, zoomed.get_width() + 16, zoomed.get_height() + 16)
    pygame.draw.rect(card, BG_DAWN, zoom_box, border_radius=6)
    pygame.draw.rect(card, CARD_EDGE, zoom_box, width=1, border_radius=6)
    card.blit(zoomed, (zoom_box.x + 8, zoom_box.y + 8))
    _text(card, f"{ZOOM}x zoom (palette + eye detail)", (zoom_box.x, zoom_box.bottom + 4),
          size=10, color=TEXT_LO, shadow=False)

    return card


def _crossfade_strip(width):
    """3-frame cross-fade preview rebuilt against the TIGHTENED E sprite.

    The aura alpha scales with `t` inside the dead sprite so early
    frames (t ≤ 0.33) don't look "haunted while still alive" — the
    halo grows in proportion to the cross-fade.
    """
    height = 280
    strip = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(strip, CARD_BG, strip.get_rect(), border_radius=10)
    pygame.draw.rect(strip, CARD_EDGE, strip.get_rect(), width=1, border_radius=10)

    _text(strip, "3-frame cross-fade preview — t = 33%, 67%, 100% (palette E, tightened)",
          (PANEL_PAD, 10), size=16, color=UI_CREAM)
    _text(strip, "Aura alpha fades in proportion to t so the bird never looks haunted while still alive.",
          (PANEL_PAD, 32), size=12, color=TEXT_LO)

    alive = _add_outline(_build_frame(WING_ANGLE))

    frames = [
        (0.33, "t = 33%"),
        (0.67, "t = 67%"),
        (1.00, "t = 100%"),
    ]

    col_w = width // 3
    for col, (t, label) in enumerate(frames):
        cx = col * col_w + col_w // 2

        # Aura scales with t — early frames keep the halo near zero so the
        # bird doesn't pre-emptively announce it's dying.
        dead_full = _add_outline(build_nightvapor_dead(WING_ANGLE, aura_scale=t))

        # Composite alive + (dead at alpha t)
        comp = pygame.Surface(alive.get_size(), pygame.SRCALPHA)
        comp.blit(alive, (0, 0))
        dead = dead_full.copy()
        dead.set_alpha(int(255 * t))
        comp.blit(dead, (0, 0))

        nw, nh = comp.get_size()
        zoomed = pygame.transform.scale(comp, (nw * ZOOM, nh * ZOOM))

        native_box = pygame.Rect(cx - (nw + 16) // 2, 58, nw + 16, nh + 16)
        pygame.draw.rect(strip, BG_DAWN, native_box, border_radius=6)
        pygame.draw.rect(strip, CARD_EDGE, native_box, width=1, border_radius=6)
        strip.blit(comp, (native_box.x + 8, native_box.y + 8))

        zw, zh = zoomed.get_size()
        zoom_box = pygame.Rect(cx - (zw + 16) // 2, native_box.bottom + 8, zw + 16, zh + 16)
        pygame.draw.rect(strip, BG_DAWN, zoom_box, border_radius=6)
        pygame.draw.rect(strip, CARD_EDGE, zoom_box, width=1, border_radius=6)
        strip.blit(zoomed, (zoom_box.x + 8, zoom_box.y + 8))

        f = _font(14)
        img = f.render(label, True, UI_GOLD)
        sh_img = f.render(label, True, (0, 0, 0))
        r = img.get_rect(center=(cx, zoom_box.bottom + 14))
        strip.blit(sh_img, (r.x + 1, r.y + 1))
        strip.blit(img, r.topleft)

    return strip


# ── main render ──────────────────────────────────────────────────────────────

def render():
    title_h = 90
    panels_h = (PANEL_H + PANEL_GAP) * len(PANELS) - PANEL_GAP
    strip_h = 280
    margin_x = 20
    margin_top = 14
    margin_bot = 22
    gap = 24

    total_w = PANEL_W + margin_x * 2
    total_h = title_h + margin_top + panels_h + gap + strip_h + margin_bot

    surf = pygame.Surface((total_w, total_h))
    surf.fill(BG_DAWN)

    # Title bar
    title_rect = pygame.Rect(0, 0, total_w, title_h)
    pygame.draw.rect(surf, (28, 32, 50), title_rect)
    pygame.draw.line(surf, CARD_EDGE, (0, title_h - 1), (total_w, title_h - 1), 1)

    title_font = _font(26)
    sub_font   = _font(15)
    title_str = "DEAD PIP v3 — Round 2 (tightened lead + polished alternates)"
    sub_str   = "E is the ship lead. B and C are alternates. A and D dropped."
    title_img = title_font.render(title_str, True, UI_GOLD)
    title_sh  = title_font.render(title_str, True, (0, 0, 0))
    sub_img   = sub_font.render(sub_str, True, TEXT_HI)
    sub_sh    = sub_font.render(sub_str, True, (0, 0, 0))

    tx = total_w // 2 - title_img.get_width() // 2
    surf.blit(title_sh, (tx + 2, 18))
    surf.blit(title_img, (tx, 16))
    sx = total_w // 2 - sub_img.get_width() // 2
    surf.blit(sub_sh, (sx + 1, 56))
    surf.blit(sub_img, (sx, 55))

    # Panel column
    py = title_h + margin_top
    for label, blurb, fn, is_lead in PANELS:
        card = _panel_card(label, blurb, fn, is_lead)
        surf.blit(card, (margin_x, py))
        py += PANEL_H + PANEL_GAP

    # Cross-fade strip
    strip = _crossfade_strip(PANEL_W)
    surf.blit(strip, (margin_x, py - PANEL_GAP + gap))

    return surf


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = render()
    pygame.image.save(out, str(OUT_PATH))
    print(f"wrote {OUT_PATH}  ({out.get_width()}x{out.get_height()})")


if __name__ == "__main__":
    main()
