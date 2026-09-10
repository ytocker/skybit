"""Render docs/dead_pip_v3/round_3_options.png — decision sheet.

Round 2 shipped three palettes (E, B, C) into the game. The user is happy
with E (NIGHT-VAPOR) but said B and C "look bad" with their current eye
treatment. The locked direction for round 3:

  "I still want the sunglasses on. Another option is that they fall off
  and the eyes of parrot will be Xs. Show me versions with and without
  for both designs."

So this sheet is a COMPARISON, not a re-design: five panels — E baseline
(unchanged ship lead), then B and C each shown twice (sunglasses-ON with
refined cartoon-dead signals, and sunglasses-OFF with bold X-eyes).

Nothing here mutates game-time code. The script only re-uses the existing
palette dicts P_NIGHTVAPOR, P_CHARTREUSE, P_BRUISE and the existing
builders. ON variants paint extra cartoon-dead overlays (limp tongue,
cracked-lens fork, slanted brow). OFF variants pass draw_lenses=False so
the lens area becomes bare head_main skin, then stamp 3 px X-eyes plus
the same tongue droop. A faint fallen-aviator silhouette sits below each
OFF panel as an extra storytelling beat (subtle so it never competes
with the parrot).
"""
import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.parrot import SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline
from game.dollar_parrot_ghost import _build_parrot_with_palette
from game.dollar_parrot_dead import (
    P_NIGHTVAPOR, P_CHARTREUSE, P_BRUISE,
    LENS_L, LENS_R, TOXIC_AURA,
    build_nightvapor_dead,
)
from game.draw import blit_glow


# ── output target ────────────────────────────────────────────────────────────

OUT_PATH = pathlib.Path(__file__).parent.parent / "docs" / "dead_pip_v3" / "round_3_options.png"

BG_CHARCOAL = (40, 40, 48)
PANEL_BG    = (28, 28, 36)
PANEL_EDGE  = (70, 70, 84)
TEXT_HI     = (235, 240, 250)
TEXT_LO     = (170, 175, 190)
GOLD        = (235, 200, 90)
RIBBON_BG   = (50, 50, 60)

# Single neutral wing pose so reviewers compare like-for-like across panels.
WING_ANGLE = _WING_ANGLES[1]   # 20°

# Beak bottom-point anchor — `dollar_parrot_ghost._build_parrot_with_palette`
# draws the beak polygon (55,21)-(61,24)-(58,28)-(52,26); the tongue hangs
# from the lower vertex (58, 28).
BEAK_BOTTOM = (58, 28)

ZOOM = 3   # native sprite is 64×60 → panel sprite area is 192×180.


# ── small text helper using bundled font ─────────────────────────────────────

def _font(size: int) -> pygame.font.Font:
    """Bundled bold ttf — the only font we ship — keeps every sheet on-brand."""
    path = pathlib.Path(__file__).parent.parent / "game" / "assets" / "LiberationSans-Bold.ttf"
    return pygame.font.Font(str(path), size)


def _text(surf, msg, center, size=14, color=TEXT_HI, shadow=True):
    f = _font(size)
    img = f.render(msg, True, color)
    rect = img.get_rect(center=center)
    if shadow:
        sh = f.render(msg, True, (0, 0, 0))
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect.topleft)


# ── shared cartoon-dead overlays ────────────────────────────────────────────

def _draw_tongue(body, palette_key):
    """Limp pill-shaped tongue hanging straight down from the beak's lower
    vertex. Anchored at BEAK_BOTTOM (58, 28). Sized 3 px × 6 px so it reads
    at native resolution without overrunning the chest band.

    Palette B sells "freshly KO'd" with sickly red; C sells "long dead" with
    a bruised maroon. Both get a 1 px outline below + 1 px highlight on top
    so the pill has visible volume at native scale and at the 3× zoom.
    """
    if palette_key == "B":
        body_col = (180, 50, 50)
        edge_col = (90, 25, 25)
        glint    = (240, 160, 160)
    else:
        body_col = (140, 40, 60)
        edge_col = (70, 20, 30)
        glint    = (210, 140, 150)

    ax, ay = BEAK_BOTTOM
    # 3 px wide tongue, dropping ay+1 → ay+6 so it appears to drape over
    # the lower beak line rather than sit beside it.
    rect = pygame.Rect(ax - 1, ay + 1, 3, 6)
    pygame.draw.rect(body, body_col, rect, border_radius=1)
    # 1 px shadow line at the bottom — gives the pill apparent weight.
    pygame.draw.line(body, edge_col, (rect.x, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), 1)
    # 1 px top highlight — moisture / lip cue.
    pygame.draw.line(body, glint, (rect.x + 1, rect.y + 1), (rect.right - 2, rect.y + 1), 1)


def _draw_cracked_lens(body, palette_key):
    """Tiny Y-shaped fork inside each lens — implies the shades took a hit
    rather than being a totally fresh stamp on top. 1 px white stroke + 1 px
    lens_frame-coloured drop-shadow offset (1, 1) so the crack reads as
    catching light, not floating.
    """
    if palette_key == "B":
        shadow = (70, 90, 20)
    else:
        shadow = (95, 60, 115)

    # Y-fork segments around each lens centre. Origin = bottom of the Y;
    # arms branch up-left and up-right; trunk drops down-right one pixel.
    for cx, cy in (LENS_L, LENS_R):
        # Shadow pass — 1 px down-right
        pygame.draw.line(body, shadow, (cx + 1, cy - 1), (cx - 1, cy - 3), 1)   # up-left arm
        pygame.draw.line(body, shadow, (cx + 1, cy - 1), (cx + 3, cy - 3), 1)   # up-right arm
        pygame.draw.line(body, shadow, (cx + 1, cy - 1), (cx + 2, cy + 2), 1)   # trunk
        # Highlight pass — bright white above the shadow
        pygame.draw.line(body, (255, 255, 255), (cx, cy - 2), (cx - 2, cy - 4), 1)
        pygame.draw.line(body, (255, 255, 255), (cx, cy - 2), (cx + 2, cy - 4), 1)
        pygame.draw.line(body, (255, 255, 255), (cx, cy - 2), (cx + 1, cy + 1), 1)


def _draw_slanted_brow(body, palette_key):
    """Comic 'angry/distressed' brow line slanting OUTWARD from the lens
    inner edge — left brow rises up-and-left, right brow rises up-and-right.

    Drawn in each palette's lens_frame colour so the brow harmonises with the
    sunglasses rim rather than feeling like a foreign stamp.
    """
    if palette_key == "B":
        col = (70, 90, 20)
    else:
        col = (95, 60, 115)

    # Left brow — from inner-top of left lens (LENS_L.x+1, LENS_L.y-4)
    # going up-and-left to (LENS_L.x-3, LENS_L.y-6). 2 px wide so it carries
    # at native size without dominating the head.
    lx, ly = LENS_L
    pygame.draw.line(body, col, (lx + 2, ly - 4), (lx - 3, ly - 6), 2)
    # Right brow — from inner-top of right lens going up-and-right
    rx, ry = LENS_R
    pygame.draw.line(body, col, (rx - 1, ry - 4), (rx + 4, ry - 6), 2)


def _draw_x_eyes(body, palette_key):
    """Bold cartoon X-eyes painted ON the bare head_main skin (the OFF
    builders pass draw_lenses=False so this is the visible eye treatment).

    Two 3 px-wide ink strokes per eye spanning ±4 px from the lens centre,
    then a 1 px highlight slash offset (-1, -1) along each ink stroke in
    head_crown colour so the X reads as drawn into the skin rather than
    stamped on top.
    """
    if palette_key == "B":
        ink_col   = (70, 90, 20)
        glint_col = (225, 235, 130)   # P_CHARTREUSE head_crown
    else:
        ink_col   = (95, 60, 115)
        glint_col = (175, 185, 110)   # P_BRUISE head_crown

    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.line(body, ink_col, (cx - 4, cy - 4), (cx + 4, cy + 4), 3)
        pygame.draw.line(body, ink_col, (cx - 4, cy + 4), (cx + 4, cy - 4), 3)
        # Highlight slash sits up-and-left of each ink stroke — sells volume.
        pygame.draw.line(body, glint_col, (cx - 4, cy - 5), (cx + 3, cy + 2), 1)
        pygame.draw.line(body, glint_col, (cx - 4, cy + 3), (cx + 3, cy - 4), 1)


# ── per-variant builders ────────────────────────────────────────────────────
# Each returns an OUTLINED surface (drop-shadow + body outline). The
# `_add_outline()` call is the LAST step before we ship the sprite to the
# panel-composite pass, exactly like build_dead_variant_frames does in
# game.dollar_parrot_dead.

def _aura(out, alpha=110):
    """Shared toxic aura — same recipe as build_chartreuse_dead so all B/C
    variants stay in the E-family 'wrongness' palette.
    """
    blit_glow(out, 32, 30, 24, TOXIC_AURA, alpha=alpha)


def build_b_sunglasses_on(angle):
    """B refined — aviators stay on, plus cracked-lens fork + slanted brows
    + limp tongue droop so the dead read no longer relies on a single dark
    socket dot.
    """
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _aura(out)
    body = _build_parrot_with_palette(angle, P_CHARTREUSE, draw_lenses=True)
    _draw_slanted_brow(body, "B")
    _draw_cracked_lens(body, "B")
    _draw_tongue(body, "B")
    out.blit(body, (0, 0))
    return _add_outline(out)


def build_b_sunglasses_off(angle):
    """B shades-off — sunglasses gone (bare head skin shows through the
    lens area), replaced with bold cartoon X-eyes + the same tongue droop.
    """
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _aura(out)
    body = _build_parrot_with_palette(angle, P_CHARTREUSE, draw_lenses=False)
    _draw_x_eyes(body, "B")
    _draw_tongue(body, "B")
    out.blit(body, (0, 0))
    return _add_outline(out)


def build_c_sunglasses_on(angle):
    """C refined — sunglasses kept, cracked-lens fork + slanted brows +
    limp maroon tongue. C's lens body is sickly green in P_BRUISE so the
    crack reads brightly against it.
    """
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _aura(out)
    body = _build_parrot_with_palette(angle, P_BRUISE, draw_lenses=True)
    _draw_slanted_brow(body, "C")
    _draw_cracked_lens(body, "C")
    _draw_tongue(body, "C")
    out.blit(body, (0, 0))
    return _add_outline(out)


def build_c_sunglasses_off(angle):
    """C shades-off — eggplant X-eyes painted on the bare bruise-coloured
    head, same maroon tongue droop. C's head_main is a desaturated lavender
    so the dark X-ink lands with strong contrast.
    """
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    _aura(out)
    body = _build_parrot_with_palette(angle, P_BRUISE, draw_lenses=False)
    _draw_x_eyes(body, "C")
    _draw_tongue(body, "C")
    out.blit(body, (0, 0))
    return _add_outline(out)


def build_e_baseline(angle):
    """Untouched ship lead — re-uses the already-shipped E builder verbatim
    so this panel is the literal in-game sprite, not a rebuilt mock.
    """
    return _add_outline(build_nightvapor_dead(angle))


# ── fallen-aviators silhouette (decorative under-panel cue) ─────────────────

def _fallen_aviators(surf, center, palette_key):
    """Tiny silhouette of dropped aviator sunglasses lying tilted ~25° on the
    panel floor. Two lens_frame-coloured circles joined by a 1 px bridge,
    rotated about the centre point.

    Drawn on a small SRCALPHA scratch surface, then rotated and blitted at
    `center`. The rotation makes the spec read as "thrown / abandoned"
    rather than neatly placed.
    """
    if palette_key == "B":
        frame_col = (70, 90, 20)
    else:
        frame_col = (95, 60, 115)

    raw = pygame.Surface((34, 14), pygame.SRCALPHA)
    # Drop shadow under each lens — sells the "lying on the ground" beat.
    pygame.draw.circle(raw, (0, 0, 0, 110), (8, 9), 5)
    pygame.draw.circle(raw, (0, 0, 0, 110), (26, 9), 5)
    # Frame + black lens body — same recipe as _draw_lenses but flattened.
    pygame.draw.circle(raw, frame_col, (8, 7), 4)
    pygame.draw.circle(raw, frame_col, (26, 7), 4)
    pygame.draw.circle(raw, (12, 12, 16), (8, 7), 3)
    pygame.draw.circle(raw, (12, 12, 16), (26, 7), 3)
    pygame.draw.line(raw, frame_col, (12, 7), (22, 7), 1)
    # Tiny glints so the lying glass still reads as glass.
    pygame.draw.circle(raw, (220, 220, 230), (7, 6), 1)
    pygame.draw.circle(raw, (220, 220, 230), (25, 6), 1)

    rot = pygame.transform.rotate(raw, 22)
    rect = rot.get_rect(center=center)
    surf.blit(rot, rect.topleft)


# ── panel composition ──────────────────────────────────────────────────────

PANEL_W = 248
PANEL_H = 260   # leaves room for fallen-shades cue + label strip


def _panel(label_top, label_sub, build_fn, palette_key, draw_fallen):
    """One labelled panel: charcoal card, 3× outlined parrot, optional
    fallen-aviators cue below the parrot, then two label lines pinned to
    the bottom of the card so every panel's title-strip lines up.
    """
    card = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(card, PANEL_BG, card.get_rect(), border_radius=10)
    pygame.draw.rect(card, PANEL_EDGE, card.get_rect(), width=1, border_radius=10)

    sprite = build_fn(WING_ANGLE)
    sw, sh = sprite.get_size()                       # outlined size is 68×64
    zoomed = pygame.transform.scale(sprite, (sw * ZOOM, sh * ZOOM))
    zw, zh = zoomed.get_size()
    # Lift parrot a touch above panel centre so labels and the fallen-shades
    # cue have room below.
    art_y = 18
    card.blit(zoomed, ((PANEL_W - zw) // 2, art_y))

    # Optional fallen aviators cue — only on shades-OFF panels. Pinned to
    # a fixed Y so all four panels' baselines line up regardless of which
    # variant has the cue.
    cue_y = art_y + zh + 14
    if draw_fallen:
        _fallen_aviators(card, (PANEL_W // 2, cue_y), palette_key)

    # Label strip — pinned to panel bottom.
    _text(card, label_top, (PANEL_W // 2, PANEL_H - 28), size=14, color=GOLD)
    _text(card, label_sub, (PANEL_W // 2, PANEL_H - 12), size=11, color=TEXT_LO)
    return card


def _baseline_panel():
    """E panel — sits as a slim full-width top strip above the 2×2 grid so
    it scans as the control, not as a fifth option. Same charcoal card so
    the visual language stays unified across all five.
    """
    card_w = PANEL_W * 2 + 16
    card_h = 240
    card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card, PANEL_BG, card.get_rect(), border_radius=10)
    pygame.draw.rect(card, PANEL_EDGE, card.get_rect(), width=1, border_radius=10)

    sprite = build_e_baseline(WING_ANGLE)
    sw, sh = sprite.get_size()
    zoomed = pygame.transform.scale(sprite, (sw * ZOOM, sh * ZOOM))
    zw, zh = zoomed.get_size()
    # Centre the parrot horizontally; lift it up so labels have room.
    art_x = (card_w - zw) // 2
    art_y = 18
    card.blit(zoomed, (art_x, art_y))

    # Ribbon next to the parrot so the SHIPPED tag scans before any of the
    # candidate panels — biases the user toward weighing E as the control.
    ribbon = pygame.Rect(16, 16, 108, 24)
    pygame.draw.rect(card, RIBBON_BG, ribbon, border_radius=4)
    pygame.draw.rect(card, GOLD, ribbon, width=1, border_radius=4)
    _text(card, "SHIPPED", ribbon.center, size=13, color=GOLD)

    _text(card, "E. NIGHT-VAPOR  (baseline — unchanged)",
          (card_w // 2, card_h - 28), size=15, color=GOLD)
    _text(card, "Reference panel. The B and C candidates below are the decision.",
          (card_w // 2, card_h - 12), size=11, color=TEXT_LO)
    return card


# ── main composition ───────────────────────────────────────────────────────

def render():
    margin_x = 20
    margin_top = 14
    margin_bot = 20
    title_h = 82
    section_gap = 18
    row_gap = 16
    col_gap = 16

    grid_w = PANEL_W * 2 + col_gap
    grid_h = PANEL_H * 2 + row_gap
    baseline_h = 240
    total_w = grid_w + margin_x * 2
    total_h = title_h + margin_top + baseline_h + section_gap + grid_h + margin_bot

    surf = pygame.Surface((total_w, total_h))
    surf.fill(BG_CHARCOAL)

    # Title bar — explicit one-liner about what is being compared.
    title_rect = pygame.Rect(0, 0, total_w, title_h)
    pygame.draw.rect(surf, (24, 24, 32), title_rect)
    pygame.draw.line(surf, PANEL_EDGE, (0, title_h - 1), (total_w, title_h - 1), 1)

    title_font = _font(22)
    sub_font   = _font(13)
    title_str = "DEAD PIP v3  ·  round 3 — sunglasses-ON vs sunglasses-OFF (X-eyes)"
    sub_str   = "E baseline (shipped, top) + B and C variants (decision: which goes back into the game)."

    timg = title_font.render(title_str, True, GOLD)
    tsh  = title_font.render(title_str, True, (0, 0, 0))
    simg = sub_font.render(sub_str, True, TEXT_HI)
    ssh  = sub_font.render(sub_str, True, (0, 0, 0))

    tx = total_w // 2 - timg.get_width() // 2
    surf.blit(tsh, (tx + 2, 20))
    surf.blit(timg, (tx, 18))
    sx = total_w // 2 - simg.get_width() // 2
    surf.blit(ssh, (sx + 1, 52))
    surf.blit(simg, (sx, 51))

    # Baseline E strip
    y = title_h + margin_top
    baseline = _baseline_panel()
    surf.blit(baseline, (margin_x, y))
    y += baseline_h + section_gap

    # Grid of 4 candidate panels (B on/off + C on/off)
    panels = [
        ("B · SUNGLASSES ON",  "refined: crack + brow + tongue", build_b_sunglasses_on,  "B", False),
        ("B · SHADES OFF",     "bold X-eyes + tongue",           build_b_sunglasses_off, "B", True),
        ("C · SUNGLASSES ON",  "refined: crack + brow + tongue", build_c_sunglasses_on,  "C", False),
        ("C · SHADES OFF",     "bold X-eyes + tongue",           build_c_sunglasses_off, "C", True),
    ]
    for i, (label, sub, fn, key, fallen) in enumerate(panels):
        row = i // 2
        col = i % 2
        px = margin_x + col * (PANEL_W + col_gap)
        py = y + row * (PANEL_H + row_gap)
        surf.blit(_panel(label, sub, fn, key, fallen), (px, py))

    return surf


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = render()
    pygame.image.save(out, str(OUT_PATH))
    print(f"wrote {OUT_PATH}  ({out.get_width()}x{out.get_height()})")


if __name__ == "__main__":
    main()
