"""5-design picker for V1 ('Bucket Party') celebration of 3,000 games.

Each variant is a 360x640 portrait PNG, all explicitly headlined with
"3,000 GAMES PLAYED!" but using a different celebration motif so the
five reads distinctly from one another:

    v1a Birthday Bucket    multicolor balloons + party hat on Pip
                           + four "3"/"0" digit candles spelling 3000
    v1b Fireworks Show     night-sky multi-burst fireworks + Pip
                           flying through them + smaller bucket
                           anchored at the bottom
    v1c Disco Bucket       disco ball + multi-color light beams +
                           checkered dance floor + rainbow-striped
                           bucket + music notes
    v1d Banner Drop        huge unfurled banner across the top with
                           hanging tassels + Pip popping out of the
                           bucket like a jack-in-the-box + dual
                           confetti cannons firing in
    v1e Trophy Pedestal    Pip on a gold pedestal holding a small
                           bucket trophy overhead, golden-hour sun
                           rays, "Champion of the skies" framing

Run from the repo root:

    PYTHONPATH=. python tools/render_3k_v1_picker.py

Output:
    docs/celebrations/3k_games/v1_picker/v1a.png .. v1e.png
    docs/celebrations/3k_games/v1_picker/compare.png
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game import parrot
from game import biome as _biome
from game.draw import COIN_GOLD, get_sky_surface_biome
from game.pillar_kfc import KFC_RED, KFC_RED_D, KFC_WHITE


# --- Palette ---------------------------------------------------------------

OUTLINE   = (24, 12, 6)
GOLD_HI   = (255, 240, 160)
GOLD_MID  = (252, 206,  72)
GOLD_LO   = (220, 160,  30)
GOLD_DK   = (158,  98,  12)

BALLOON_COLORS = ((242,  90,  90),   # red
                  (252, 206,  56),   # yellow
                  ( 90, 200,  80),   # green
                  ( 90, 160, 250),   # blue
                  (236, 110, 220),   # pink
                  (170, 110, 240))   # purple

FIREWORK_COLORS = ((255, 110,  90), (255, 220,  90),
                   (140, 230, 255), (200, 130, 255),
                   (150, 255, 160))

DISCO_BEAM_COLS = ((255, 110, 200), (110, 240, 255),
                   (255, 200,  90), (180, 255, 110))


# --- Fonts -----------------------------------------------------------------

def _font(size, bold=True):
    fname = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
    return pygame.font.Font(os.path.join("game", "assets", fname), size)


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


# --- Text helpers ----------------------------------------------------------

def draw_outlined_text(surf, text, center, *, size, fill, outline=OUTLINE,
                       outline_w=4, shadow=True, sparkles=0):
    font = _font(size, bold=True)
    text_surf = font.render(text, True, fill)
    tw, th = text_surf.get_size()
    cx, cy = center
    layer = pygame.Surface((tw + outline_w * 4, th + outline_w * 4),
                           pygame.SRCALPHA)
    outline_surf = font.render(text, True, outline)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx * dx + dy * dy <= outline_w * outline_w:
                layer.blit(outline_surf,
                           (outline_w * 2 + dx, outline_w * 2 + dy))
    layer.blit(text_surf, (outline_w * 2, outline_w * 2))
    if shadow:
        dark = font.render(text, True, (0, 0, 0))
        dark.set_alpha(140)
        surf.blit(dark,
                  (cx - layer.get_width() // 2 + outline_w * 2 + 2,
                   cy - layer.get_height() // 2 + outline_w * 2 + 3))
    rect = layer.get_rect(center=(cx, cy))
    surf.blit(layer, rect.topleft)
    if sparkles:
        rng = random.Random(hash(text) & 0xffff)
        for _ in range(sparkles):
            sx = rng.randint(rect.left - 6, rect.right + 6)
            sy = rng.randint(rect.top - 6, rect.bottom + 6)
            r = rng.randint(2, 4)
            pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
            pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
            pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                               max(1, r - 2))
    return rect


def draw_tagline(surf, text, y, *, size=18, color=(255, 255, 255)):
    font = _font(size, bold=True)
    out = font.render(text, True, OUTLINE)
    fill = font.render(text, True, color)
    cx = W // 2
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                surf.blit(out, (cx - out.get_width() // 2 + dx, y + dy))
    surf.blit(fill, (cx - fill.get_width() // 2, y))


# --- Bucket helper (reused by all 5) ---------------------------------------

def draw_bucket(surf, rect, *, label_text=None, rainbow=False,
                stripe_count=7, shade_cylinder=True):
    """Striped trapezoid bucket. Returns (rim_rect, body_poly)."""
    cx = rect.centerx
    bw_top = rect.width
    bw_bot = max(int(rect.width * 0.72), 60)
    tl = (cx - bw_top // 2, rect.top)
    tr = (cx + bw_top // 2, rect.top)
    br = (cx + bw_bot // 2, rect.bottom)
    bl = (cx - bw_bot // 2, rect.bottom)
    poly = [tl, tr, br, bl]
    # Drop shadow underneath
    sh = pygame.Surface((bw_bot + 60, 22), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 110), sh.get_rect())
    surf.blit(sh, (cx - sh.get_width() // 2, rect.bottom - 8))
    # Outline + white base
    pygame.draw.polygon(surf, OUTLINE,
                        [(px, py + 2) for (px, py) in poly])
    pygame.draw.polygon(surf, KFC_WHITE, poly)
    # Stripes
    for i in range(stripe_count):
        u0 = (i + 0.12) / stripe_count
        u1 = (i + 0.58) / stripe_count
        if rainbow:
            base = ((242, 90, 90), (250, 160, 60), (252, 206, 56),
                    (90, 200, 80), (90, 160, 250), (170, 110, 240),
                    (236, 110, 220))[i % 7]
        else:
            base = KFC_RED
        # Cylinder shading by horizontal position
        u_mid = (u0 + u1) / 2
        if shade_cylinder:
            if u_mid < 0.25:
                sd = +25
            elif u_mid < 0.5:
                sd = +8
            elif u_mid < 0.75:
                sd = -12
            else:
                sd = -32
            c = _shade(base, sd)
        else:
            c = base
        sx0_top = tl[0] + (tr[0] - tl[0]) * u0
        sx1_top = tl[0] + (tr[0] - tl[0]) * u1
        sx0_bot = bl[0] + (br[0] - bl[0]) * u0
        sx1_bot = bl[0] + (br[0] - bl[0]) * u1
        pygame.draw.polygon(
            surf, c,
            [(sx0_top, tl[1]), (sx1_top, tl[1]),
             (sx1_bot, br[1]), (sx0_bot, br[1])])
    pygame.draw.polygon(surf, OUTLINE, poly, 3)
    # Top rim band
    rim = pygame.Rect(tl[0] - 4, tl[1] - 8, bw_top + 8, 16)
    pygame.draw.rect(surf, OUTLINE, rim.inflate(2, 2), border_radius=6)
    pygame.draw.rect(surf, KFC_RED_D, rim, border_radius=6)
    pygame.draw.rect(surf, KFC_RED, rim.inflate(-6, -4), border_radius=4)
    # Inner shadow line
    pygame.draw.line(surf, _shade(KFC_RED_D, -30),
                     (tl[0] + 4, tl[1] + 1),
                     (tr[0] - 4, tl[1] + 1), 2)
    if label_text:
        # Gold-foil label band on the front of the bucket
        lw, lh = 170, 36
        label = pygame.Rect(cx - lw // 2,
                            (tl[1] + br[1]) // 2 - lh // 2,
                            lw, lh)
        pygame.draw.rect(surf, OUTLINE, label.inflate(6, 6),
                         border_radius=6)
        pygame.draw.rect(surf, KFC_RED_D, label.inflate(4, 4),
                         border_radius=6)
        pygame.draw.rect(surf, KFC_RED, label.inflate(2, 2),
                         border_radius=5)
        # Gold body
        gold_rect = label.inflate(-6, -6)
        for y in range(gold_rect.height):
            u = y / max(1, gold_rect.height - 1) * 4
            stops = (GOLD_HI, GOLD_MID, GOLD_LO, GOLD_DK, (70, 38, 4))
            i0 = int(u)
            i1 = min(i0 + 1, 4)
            t = u - i0
            c = tuple(int(stops[i0][k] + (stops[i1][k] - stops[i0][k]) * t)
                      for k in range(3))
            pygame.draw.line(surf, c,
                              (gold_rect.x, gold_rect.y + y),
                              (gold_rect.right, gold_rect.y + y))
        pygame.draw.rect(surf, OUTLINE, gold_rect, border_radius=4, width=2)
        # Embossed text
        fnt = _font(18, bold=True)
        eng_dk = fnt.render(label_text, True, GOLD_DK)
        eng_hi = fnt.render(label_text, True, (255, 248, 220))
        surf.blit(eng_dk,
                  (label.centerx - eng_dk.get_width() // 2 + 1,
                   label.centery - eng_dk.get_height() // 2 + 1))
        surf.blit(eng_hi,
                  (label.centerx - eng_hi.get_width() // 2 - 1,
                   label.centery - eng_hi.get_height() // 2 - 1))
    return rim, poly


# --- Specific celebration elements -----------------------------------------

def make_cylindrical_candle(digit, *, body_h=70, body_w=24,
                             wax_color=(248, 240, 220),
                             stripe_color=(242, 60, 70),
                             digit_color=(40, 30, 20)):
    """Build a STANDALONE birthday number-candle sprite shaped like a
    real birthday candle: a vertical wax cylinder with the digit
    printed on its face, a spiral stripe wrapping the wax, a wick
    rising from the top, and a flame burning on the wick.

    Returns a Surface whose:
        - top    = tip of the flame
        - bottom = bottom of the wax cylinder
        - centre = wick

    Caller blits with `midbottom=(cx, target_y)` to plant the candle
    base at target_y.
    """
    WICK_H = 8
    FLAME_H = 22

    # Sprite layout: flame on top, then wick, then cylindrical body
    sprite_w = body_w + 14   # margin for flame width + outline
    sprite_h = FLAME_H + WICK_H + body_h
    sprite = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)
    cx = sprite_w // 2

    body_top = FLAME_H + WICK_H
    body_bot = body_top + body_h

    # ---- Cylindrical body: rounded-top rectangle with side-shading ----
    body_rect = pygame.Rect(cx - body_w // 2, body_top, body_w, body_h)
    # Drop shadow
    sh = pygame.Rect(body_rect.x + 2, body_rect.y + 3,
                     body_rect.width, body_rect.height)
    pygame.draw.rect(sprite, (0, 0, 0, 90), sh,
                     border_top_left_radius=body_w // 2,
                     border_top_right_radius=body_w // 2)
    # Outline
    pygame.draw.rect(sprite, OUTLINE, body_rect.inflate(4, 4),
                     border_top_left_radius=body_w // 2 + 2,
                     border_top_right_radius=body_w // 2 + 2)
    # Wax base color
    pygame.draw.rect(sprite, _shade(wax_color, -30),
                     body_rect.inflate(2, 2),
                     border_top_left_radius=body_w // 2 + 1,
                     border_top_right_radius=body_w // 2 + 1)
    pygame.draw.rect(sprite, wax_color, body_rect,
                     border_top_left_radius=body_w // 2,
                     border_top_right_radius=body_w // 2)
    # Side highlights (cylinder shading)
    hl = pygame.Rect(body_rect.x + 3, body_rect.y + 6,
                     max(2, body_w // 4), body_h - 12)
    pygame.draw.rect(sprite, _shade(wax_color, +35), hl,
                     border_radius=hl.width // 2)
    # Side shadow on the right
    rsh = pygame.Rect(body_rect.right - 5, body_rect.y + 6,
                      3, body_h - 12)
    pygame.draw.rect(sprite, _shade(wax_color, -35), rsh,
                     border_radius=2)

    # ---- Spiral stripe wrapping the cylinder ----
    # Drawn as a few diagonal slashes across the body face
    n_stripes = 5
    for i in range(n_stripes):
        y0 = body_top + body_h * (0.10 + i * 0.18)
        y1 = y0 + 6
        x0 = body_rect.x + 3
        x1 = body_rect.right - 3
        if y0 > body_bot - 4 or y1 > body_bot - 2:
            continue
        pts = [(x0, y0), (x1, y0 + 3),
               (x1, y0 + 7), (x0, y0 + 4)]
        pygame.draw.polygon(sprite, stripe_color, pts)
        # Subtle dark line along the bottom edge of the stripe
        pygame.draw.line(sprite, _shade(stripe_color, -40),
                         (x0, y0 + 4), (x1, y0 + 7), 1)

    # ---- Digit printed on the front face: BIG, vivid, chunky outline ----
    fnt = _font(int(body_h * 0.72), bold=True)
    d_dark = fnt.render(digit, True, OUTLINE)
    d_fill = fnt.render(digit, True, digit_color)
    d_w, d_h = d_fill.get_size()
    dx = cx - d_w // 2
    dy = body_top + (body_h - d_h) // 2
    # Thick 3-px outline ring around the digit so it pops off any
    # background colour (wax or stripe)
    for ox in range(-3, 4):
        for oy in range(-3, 4):
            if ox * ox + oy * oy <= 9:
                sprite.blit(d_dark, (dx + ox, dy + oy))
    sprite.blit(d_fill, (dx, dy))

    # ---- Wick rooted INTO the top of the wax ----
    wick_root_y = body_top + 2   # 2 px inside the wax
    wick_tip_y = wick_root_y - WICK_H
    pygame.draw.line(sprite, OUTLINE,
                     (cx, wick_root_y), (cx, wick_tip_y), 3)

    # ---- Flame burning ON the wick tip ----
    flame_mid_y = wick_tip_y - 8
    for r_g, a_g in ((18, 60), (12, 110), (7, 170)):
        halo = pygame.Surface((r_g * 2, r_g * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 200, 80, a_g), (r_g, r_g), r_g)
        sprite.blit(halo, (cx - r_g, flame_mid_y - r_g))
    flame_outer = [(cx, wick_tip_y - 18),
                    (cx - 7, wick_tip_y),
                    (cx + 7, wick_tip_y)]
    pygame.draw.polygon(sprite, (180, 50, 20), flame_outer)
    flame_mid = [(cx, wick_tip_y - 13),
                  (cx - 5, wick_tip_y),
                  (cx + 5, wick_tip_y)]
    pygame.draw.polygon(sprite, (250, 160, 30), flame_mid)
    flame_inner = [(cx, wick_tip_y - 9),
                    (cx - 3, wick_tip_y),
                    (cx + 3, wick_tip_y)]
    pygame.draw.polygon(sprite, (255, 220, 100), flame_inner)
    pygame.draw.polygon(sprite, (255, 255, 230),
                        [(cx, wick_tip_y - 5),
                         (cx - 2, wick_tip_y),
                         (cx + 2, wick_tip_y)])

    # Crop sprite to exact bounds (top = flame tip, bottom = wax base)
    return sprite


def make_frosting_drip_band(width, *, color=(255, 255, 255),
                             height=24, n_drips=6):
    """A band of white frosting drips - chunky icing dripping down
    from a fixed top edge. Designed to sit on top of the bucket's
    rim band so the bucket reads as a cake.

    Returns a Surface of size (width, height + 12 px tail), with the
    top edge being the flat icing line. Caller positions with
    `topleft=(rim.x, rim.bottom - 4)` so the icing flows over the rim
    onto the bucket body.
    """
    band = pygame.Surface((width + 4, height + 14), pygame.SRCALPHA)
    bx = 2
    # Top icing line (chunky white rectangle)
    top_strip = pygame.Rect(bx, 0, width, height // 2)
    pygame.draw.rect(band, OUTLINE, top_strip.inflate(2, 2),
                     border_top_left_radius=4,
                     border_top_right_radius=4)
    pygame.draw.rect(band, _shade(color, -25), top_strip.inflate(0, 0),
                     border_top_left_radius=4,
                     border_top_right_radius=4)
    pygame.draw.rect(band, color,
                     pygame.Rect(top_strip.x + 2, top_strip.y + 1,
                                 top_strip.width - 4, top_strip.height - 2),
                     border_top_left_radius=3,
                     border_top_right_radius=3)
    # Highlight along the very top
    pygame.draw.line(band, (255, 255, 255),
                     (top_strip.x + 4, top_strip.y + 2),
                     (top_strip.right - 4, top_strip.y + 2), 2)

    # Drip blobs hanging from the bottom of the icing band
    rng = random.Random(width * 7)
    for i in range(n_drips):
        u = (i + 0.5) / n_drips
        dx = int(bx + width * u)
        dh = rng.randint(height // 2 + 4, height + 10)
        dw = rng.randint(14, 22)
        drip = pygame.Rect(dx - dw // 2, top_strip.bottom - 4,
                            dw, dh - top_strip.height + 4)
        # Drip body
        pygame.draw.rect(band, OUTLINE, drip.inflate(2, 2),
                         border_bottom_left_radius=dw // 2,
                         border_bottom_right_radius=dw // 2)
        pygame.draw.rect(band, _shade(color, -25),
                         drip.inflate(0, 0),
                         border_bottom_left_radius=dw // 2,
                         border_bottom_right_radius=dw // 2)
        pygame.draw.rect(band, color,
                         pygame.Rect(drip.x + 2, drip.y, drip.width - 4,
                                     drip.height - 2),
                         border_bottom_left_radius=dw // 2 - 2,
                         border_bottom_right_radius=dw // 2 - 2)
        # Highlight on the lit side
        pygame.draw.rect(band, (255, 255, 255),
                         pygame.Rect(drip.x + 3, drip.y + 2, 3,
                                     drip.height - 6),
                         border_radius=2)
    return band


def _find_head_crown(sprite):
    """Walk down the sprite's alpha and return (x, y) of the visible
    head crown: the centre-x of the topmost row whose alpha-mass is
    big enough to be the bird's head shape (not stray sparkle pixels).
    """
    w, h = sprite.get_size()
    THRESH = 30
    MIN_RUN = 4   # need a connected run of >= this many non-transparent pxs
    for y in range(h):
        # Find the longest run of alpha>THRESH pixels in this row
        best_run_start = -1
        best_run_len = 0
        run_start = -1
        run_len = 0
        for x in range(w):
            if sprite.get_at((x, y))[3] > THRESH:
                if run_start < 0:
                    run_start = x
                    run_len = 1
                else:
                    run_len += 1
                if run_len > best_run_len:
                    best_run_len = run_len
                    best_run_start = run_start
            else:
                run_start = -1
                run_len = 0
        if best_run_len >= MIN_RUN:
            cx = best_run_start + best_run_len // 2
            return (cx, y)
    return (w // 2, 0)


def make_pip_with_hat(*, frame=0, tilt=18, scale=1.4,
                      hat_color1=(242, 90, 90),
                      hat_color2=(252, 206, 56),
                      hat_tilt=-4):
    """Build a STANDALONE sprite of Pip wearing the party hat, hat-
    on-head correctly. Returns a single Surface that can be blitted as
    one unit anywhere on the celebration image.

    The parrot sprite is supersampled (rendered at 3x then smoothscaled
    down to the target size) for visibly sharper edges than a direct
    smoothscale would give - the 3x downscale acts as a low-pass
    filter against the source's aliased pixel edges.
    """
    pip_native = parrot.get_parrot(frame, tilt)
    nw, nh = pip_native.get_size()
    # Supersample up 3x, then down to target (SS pass smooths edges)
    super_sprite = pygame.transform.smoothscale(
        pip_native, (nw * 3, nh * 3))
    pip_scaled = pygame.transform.smoothscale(
        super_sprite, (int(nw * scale), int(nh * scale)))
    # Find Pip's actual head crown by alpha-walking the scaled sprite
    crown_local = _find_head_crown(pip_scaled)
    # Build the hat at the requested colors / tilt
    hat = _build_hat_layer(hat_color1, hat_color2, hat_tilt)
    # Composite Pip + hat onto an oversized canvas so the hat doesn't
    # clip. Hat brim should land 4 px below the crown so it visibly
    # seats DOWN on the head feathers rather than perching on top.
    top_pad = max(0, hat.get_height() - crown_local[1] + 4)
    side_pad = max(0, hat.get_width() // 2 - crown_local[0] + 4)
    canvas_w = pip_scaled.get_width() + side_pad * 2
    canvas_h = pip_scaled.get_height() + top_pad
    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    # Pip goes at (side_pad, top_pad)
    pip_x = side_pad
    pip_y = top_pad
    canvas.blit(pip_scaled, (pip_x, pip_y))
    # Hat brim anchor in canvas coords: at the crown pixel, +4 px down
    brim_canvas = (pip_x + crown_local[0], pip_y + crown_local[1] + 4)
    hat_rect = hat.get_rect(center=brim_canvas)
    canvas.blit(hat, hat_rect.topleft)
    return canvas


def _build_hat_layer(color1, color2, tilt_deg):
    """Internal: build the rotation-padded hat layer used by both
    make_pip_with_hat and the standalone draw_party_hat helper."""
    CONE_W = 54
    CONE_H = 54
    PAD_X = 8
    PAD_TOP = 4
    layer_w = CONE_W + PAD_X * 2
    layer_h = CONE_H + PAD_TOP + 2
    layer = pygame.Surface((layer_w, layer_h), pygame.SRCALPHA)
    apex = (PAD_X + CONE_W // 2, PAD_TOP)
    brim_y = PAD_TOP + CONE_H
    bl = (PAD_X + 4, brim_y)
    br = (PAD_X + CONE_W - 4, brim_y)
    # Shadow under cone
    sh_pts = [(apex[0] + 2, apex[1] + 3),
              (bl[0] + 2, bl[1] + 1),
              (br[0] + 2, br[1] + 1)]
    pygame.draw.polygon(layer, (0, 0, 0, 90), sh_pts)
    # Stripes
    for i in range(9):
        u0 = i / 9
        u1 = (i + 1) / 9
        x0_l = bl[0] + (apex[0] - bl[0]) * u0
        x1_l = bl[0] + (apex[0] - bl[0]) * u1
        x0_r = br[0] + (apex[0] - br[0]) * u0
        x1_r = br[0] + (apex[0] - br[0]) * u1
        y0 = bl[1] + (apex[1] - bl[1]) * u0
        y1 = bl[1] + (apex[1] - bl[1]) * u1
        c = color1 if i % 2 == 0 else color2
        pygame.draw.polygon(layer, c,
                            [(x0_l, y0), (x0_r, y0),
                             (x1_r, y1), (x1_l, y1)])
    pygame.draw.polygon(layer, OUTLINE, [apex, bl, br], 3)
    pygame.draw.circle(layer, OUTLINE, apex, 8)
    pygame.draw.circle(layer, (255, 250, 230), apex, 7)
    pygame.draw.circle(layer, (255, 255, 255),
                       (apex[0] - 2, apex[1] - 2), 3)
    pygame.draw.line(layer, OUTLINE, (bl[0] - 2, brim_y),
                     (br[0] + 2, brim_y), 4)
    pygame.draw.line(layer, (255, 255, 255), bl, br, 3)
    # Symmetric padding below the brim so the brim is at the layer
    # CENTRE - pygame.transform.rotate rotates around the centre, so
    # the brim stays at the centre of the rotated bbox.
    extra_below = brim_y - (layer_h - brim_y)
    if extra_below > 0:
        pad_layer = pygame.Surface(
            (layer_w, layer_h + extra_below), pygame.SRCALPHA)
        pad_layer.blit(layer, (0, 0))
        layer = pad_layer
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    return layer


def draw_party_hat(surf, head_top, *, color1=(242, 90, 90),
                   color2=(252, 206, 56), tilt_deg=-6):
    """Stand-alone helper: builds the hat layer + blits at head_top.
    Equivalent to make_pip_with_hat for callers that already have Pip
    placed and only want a hat overlay.
    """
    layer = _build_hat_layer(color1, color2, tilt_deg)
    rect = layer.get_rect(center=head_top)
    surf.blit(layer, rect.topleft)


def draw_balloon(surf, cx, cy, *, color, tilt_deg=0, size=26, sway=0):
    """Balloon with knot + curly string."""
    layer = pygame.Surface((size + 6, size * 2 + 30), pygame.SRCALPHA)
    bx, by = (layer.get_width() // 2, size // 2 + 4)
    # Balloon body (slightly oval)
    bw = size
    bh = int(size * 1.15)
    rect = pygame.Rect(bx - bw // 2, by - bh // 2, bw, bh)
    pygame.draw.ellipse(layer, OUTLINE, rect.inflate(4, 4))
    pygame.draw.ellipse(layer, _shade(color, -30), rect.inflate(2, 2))
    pygame.draw.ellipse(layer, color, rect)
    # Highlight on upper-left
    hl = pygame.Rect(rect.x + 3, rect.y + 3, rect.width // 3, rect.height // 3)
    pygame.draw.ellipse(layer, _shade(color, +60), hl)
    pygame.draw.ellipse(layer, (255, 255, 255), hl.inflate(-3, -3))
    # Knot (little triangle below)
    knot_pts = [(bx - 4, rect.bottom - 1),
                (bx + 4, rect.bottom - 1),
                (bx, rect.bottom + 6)]
    pygame.draw.polygon(layer, OUTLINE, knot_pts)
    pygame.draw.polygon(layer, _shade(color, -40), knot_pts)
    # Curly string
    string_top = (bx, rect.bottom + 6)
    pts = []
    for i in range(20):
        t = i / 19
        sx = bx + math.sin(t * 6 + sway) * 4 * (1 - t * 0.5)
        sy = rect.bottom + 6 + t * (layer.get_height() - rect.bottom - 8)
        pts.append((sx, sy))
    pygame.draw.lines(layer, OUTLINE, False,
                      [(p[0] + 1, p[1]) for p in pts], 2)
    pygame.draw.lines(layer, (40, 40, 40), False, pts, 1)
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    surf.blit(layer, (cx - layer.get_width() // 2,
                       cy - bh // 2 - 8))


def make_number_candle(digit, *, height=60,
                        body_color=(242, 60, 70),
                        hi_color=(255, 160, 170)):
    """Build a STANDALONE number-candle sprite (digit-shaped wax body +
    wick + flame on top). Returns a Surface whose:

        - top edge = tip of the flame
        - bottom edge = bottom of the digit ink
        - centre x = wick / centre of digit

    Caller blits the result with `midbottom=(cx, rim_y)` to plant the
    candle on the cake rim. Push it down a few px and re-paint a strip
    of the rim back on top for the "plunged into cake" effect.
    """
    # ---- Render digit + outline + highlight ----
    fnt = _font(height, bold=True)
    body = fnt.render(digit, True, body_color)
    out_glyph = fnt.render(digit, True, OUTLINE)
    hi_glyph = fnt.render(digit, True, hi_color)
    bw, bh = body.get_size()
    PAD = 4
    digit_canvas = pygame.Surface((bw + PAD * 2, bh + PAD * 2),
                                   pygame.SRCALPHA)
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx * dx + dy * dy <= 9:
                digit_canvas.blit(out_glyph, (PAD + dx, PAD + dy))
    digit_canvas.blit(body, (PAD, PAD))
    # Highlight pass alpha-masked to digit shape
    hi_layer = pygame.Surface(digit_canvas.get_size(), pygame.SRCALPHA)
    hi_layer.blit(hi_glyph, (PAD - 2, PAD - 2))
    body_mask = pygame.Surface(digit_canvas.get_size(), pygame.SRCALPHA)
    body_mask.blit(body, (PAD, PAD))
    hi_layer.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    digit_canvas.blit(hi_layer, (0, 0))

    # Visible glyph ink top / bottom inside digit_canvas
    glyph_top_in_canvas = PAD + int(bh * 0.08)
    glyph_bot_in_canvas = PAD + bh

    # ---- Sizes for wick + flame ----
    WICK_H = 6
    FLAME_H = 22

    # ---- Final composite sprite ----
    sprite_w = digit_canvas.get_width() + 8   # extra px for flame width
    sprite_h = FLAME_H + WICK_H + (PAD + bh - glyph_top_in_canvas)
    sprite = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)
    sprite_cx = sprite_w // 2

    # Where the digit canvas TOP lands inside the sprite. We want:
    #   sprite top   = top of flame
    #   sprite y at FLAME_H + WICK_H = top of digit GLYPH INK
    #   -> canvas_top_y_in_sprite = FLAME_H + WICK_H - glyph_top_in_canvas
    canvas_top_y_in_sprite = FLAME_H + WICK_H - glyph_top_in_canvas

    # Drop shadow behind the digit
    shadow_surf = out_glyph.copy()
    shadow_surf.set_alpha(110)
    sprite.blit(shadow_surf,
                 (sprite_cx - digit_canvas.get_width() // 2 + PAD + 3,
                  canvas_top_y_in_sprite + PAD + 4))
    sprite.blit(digit_canvas,
                (sprite_cx - digit_canvas.get_width() // 2,
                 canvas_top_y_in_sprite))

    # Wick - rooted INTO the top of the digit ink
    wick_root_y = canvas_top_y_in_sprite + glyph_top_in_canvas + 3
    wick_tip_y = wick_root_y - WICK_H - 3
    pygame.draw.line(sprite, OUTLINE,
                     (sprite_cx, wick_root_y),
                     (sprite_cx, wick_tip_y), 3)

    # Flame halo
    flame_mid_y = wick_tip_y - 8
    for r_g, a_g in ((16, 60), (11, 110), (7, 170)):
        halo = pygame.Surface((r_g * 2, r_g * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 200, 80, a_g), (r_g, r_g), r_g)
        sprite.blit(halo, (sprite_cx - r_g, flame_mid_y - r_g))
    # Flame body layers - bottom at wick_tip_y exactly
    flame_outer = [(sprite_cx, wick_tip_y - 18),
                    (sprite_cx - 7, wick_tip_y),
                    (sprite_cx + 7, wick_tip_y)]
    pygame.draw.polygon(sprite, (180, 50, 20), flame_outer)
    flame_mid = [(sprite_cx, wick_tip_y - 13),
                  (sprite_cx - 5, wick_tip_y),
                  (sprite_cx + 5, wick_tip_y)]
    pygame.draw.polygon(sprite, (250, 160, 30), flame_mid)
    flame_inner = [(sprite_cx, wick_tip_y - 9),
                    (sprite_cx - 3, wick_tip_y),
                    (sprite_cx + 3, wick_tip_y)]
    pygame.draw.polygon(sprite, (255, 220, 100), flame_inner)
    pygame.draw.polygon(sprite, (255, 255, 230),
                        [(sprite_cx, wick_tip_y - 5),
                         (sprite_cx - 2, wick_tip_y),
                         (sprite_cx + 2, wick_tip_y)])

    # CROP the sprite's bottom so the bottom-most row is the digit-ink
    # baseline (allows clean `midbottom=` placement). The canvas has
    # PAD px below the glyph; the sprite's actual bottom row is at
    # canvas_top_y_in_sprite + PAD + bh. Trim anything below that.
    actual_h = canvas_top_y_in_sprite + PAD + bh
    final = pygame.Surface((sprite_w, actual_h), pygame.SRCALPHA)
    final.blit(sprite, (0, 0))
    return final


def draw_firework_burst(surf, cx, cy, *, color, r=70, n_arms=14, seed=0):
    """Radial spark pattern with a bright core."""
    rng = random.Random(seed)
    # Bright core
    for rg, a in ((28, 80), (18, 140), (10, 220)):
        glow = pygame.Surface((rg * 2, rg * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color, a), (rg, rg), rg)
        surf.blit(glow, (cx - rg, cy - rg))
    # Spark arms
    for i in range(n_arms):
        ang = (i + rng.uniform(-0.1, 0.1)) * 2 * math.pi / n_arms
        L = r * rng.uniform(0.7, 1.0)
        ex = cx + math.cos(ang) * L
        ey = cy + math.sin(ang) * L
        # Tapered streak: thicker near center
        for k in range(5):
            t0 = k / 5
            t1 = (k + 1) / 5
            a = int(255 * (1 - t0))
            w = max(1, 4 - k)
            x0 = cx + (ex - cx) * t0
            y0 = cy + (ey - cy) * t0
            x1 = cx + (ex - cx) * t1
            y1 = cy + (ey - cy) * t1
            pygame.draw.line(surf, (*color, a),
                              (x0, y0), (x1, y1), w)
        # Tip dot
        pygame.draw.circle(surf, color, (int(ex), int(ey)), 2)
        pygame.draw.circle(surf, (255, 255, 255), (int(ex), int(ey)), 1)
    # Trailing dots (drift)
    for _ in range(8):
        ang = rng.uniform(0, 2 * math.pi)
        d = r * rng.uniform(0.4, 1.1)
        x = cx + math.cos(ang) * d
        y = cy + math.sin(ang) * d
        pygame.draw.circle(surf, color, (int(x), int(y)), 2)


def draw_disco_ball(surf, cx, cy, r):
    """Reflective disco ball with grid facets + bright highlight."""
    # Mounting string
    pygame.draw.line(surf, OUTLINE, (cx, 0), (cx, cy - r), 2)
    pygame.draw.line(surf, (200, 200, 220), (cx + 1, 0), (cx + 1, cy - r), 1)
    # Shadow
    sh = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 90), (r + 2, r + 2), r + 1)
    surf.blit(sh, (cx - r - 2 + 2, cy - r - 2 + 2))
    # Ball base
    pygame.draw.circle(surf, OUTLINE, (cx, cy), r + 1)
    # Radial purple-blue gradient body
    body = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for y in range(r * 2):
        u = y / max(1, r * 2 - 1)
        c = (int(180 + (110 - 180) * u),
             int(170 + (140 - 170) * u),
             int(220 + (200 - 220) * u))
        dx = math.sqrt(max(0, r * r - (y - r) ** 2))
        pygame.draw.line(body, c, (r - dx + 1, y + 1), (r + dx + 1, y + 1))
    surf.blit(body, (cx - r, cy - r))
    # Facet grid (lat/long)
    for ang_deg in range(0, 180, 22):
        ang = math.radians(ang_deg)
        x1 = cx + math.cos(ang) * r
        y1 = cy + math.sin(ang) * r * 0.4
        x2 = cx - math.cos(ang) * r
        y2 = cy - math.sin(ang) * r * 0.4
        pygame.draw.line(surf, (90, 70, 130), (x1, y1), (x2, y2), 1)
    for v in (-r * 0.6, -r * 0.3, 0, r * 0.3, r * 0.6):
        # Latitude ellipse arc - draw thin ellipse
        h_arc = max(2, abs(r * 0.4 - abs(v) * 0.6))
        arc_rect = pygame.Rect(cx - r, cy + v - h_arc // 2,
                                r * 2, max(2, int(h_arc)))
        pygame.draw.arc(surf, (90, 70, 130), arc_rect, 0, math.pi, 1)
    # Bright facet highlights (random sparkly squares)
    rng = random.Random(11)
    for _ in range(24):
        ang = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, r - 4)
        x = int(cx + math.cos(ang) * d)
        y = int(cy + math.sin(ang) * d * 0.85)
        s = rng.choice((2, 3, 3))
        pygame.draw.rect(surf, (220, 230, 255),
                          pygame.Rect(x - s // 2, y - s // 2, s, s))
    # Specular crescent (upper-left)
    spec = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(spec, (255, 255, 255, 200), (r, r), r - 2)
    pygame.draw.rect(spec, (0, 0, 0, 0),
                      pygame.Rect(r, r, r, r))
    surf.blit(spec, (cx - r, cy - r))


def draw_disco_beam(surf, anchor, *, color, ang_rad, half_spread=0.06,
                    length=400, alpha=80):
    """Single beam of coloured light from anchor at angle ang_rad."""
    ax, ay = anchor
    pts = [
        anchor,
        (ax + math.cos(ang_rad - half_spread) * length,
         ay + math.sin(ang_rad - half_spread) * length),
        (ax + math.cos(ang_rad + half_spread) * length,
         ay + math.sin(ang_rad + half_spread) * length),
    ]
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*color, alpha), pts)
    surf.blit(layer, (0, 0))


def draw_music_note(surf, cx, cy, color, *, tilt_deg=0):
    layer = pygame.Surface((28, 38), pygame.SRCALPHA)
    # Note head (oval)
    pygame.draw.ellipse(layer, OUTLINE, pygame.Rect(2, 22, 14, 12))
    pygame.draw.ellipse(layer, color, pygame.Rect(3, 23, 12, 10))
    pygame.draw.ellipse(layer, _shade(color, 60),
                        pygame.Rect(4, 24, 6, 4))
    # Stem
    pygame.draw.line(layer, OUTLINE, (16, 28), (16, 6), 3)
    pygame.draw.line(layer, color, (16, 28), (16, 6), 2)
    # Flag
    flag_pts = [(16, 6), (26, 14), (20, 22), (16, 16)]
    pygame.draw.polygon(layer, OUTLINE,
                        [(p[0] + 1, p[1]) for p in flag_pts])
    pygame.draw.polygon(layer, color, flag_pts)
    if tilt_deg:
        layer = pygame.transform.rotate(layer, tilt_deg)
    surf.blit(layer, (cx - layer.get_width() // 2,
                       cy - layer.get_height() // 2))


def draw_confetti_cannon(surf, base, angle_deg, *, color=(120, 120, 130)):
    """Cone-shape cannon spitting confetti along `angle_deg`."""
    ax, ay = base
    ang = math.radians(angle_deg)
    # Cannon body (truncated cone polygon)
    fwd = (math.cos(ang), math.sin(ang))
    nrm = (-fwd[1], fwd[0])
    L = 60
    base_w = 16
    tip_w = 24
    pts = [
        (ax - nrm[0] * base_w, ay - nrm[1] * base_w),
        (ax + nrm[0] * base_w, ay + nrm[1] * base_w),
        (ax + fwd[0] * L + nrm[0] * tip_w,
         ay + fwd[1] * L + nrm[1] * tip_w),
        (ax + fwd[0] * L - nrm[0] * tip_w,
         ay + fwd[1] * L - nrm[1] * tip_w),
    ]
    pygame.draw.polygon(surf, OUTLINE,
                        [(p[0] + 2, p[1] + 2) for p in pts])
    pygame.draw.polygon(surf, _shade(color, -40), pts)
    pygame.draw.polygon(surf, color, [(p[0], p[1] - 2) for p in pts])
    pygame.draw.polygon(surf, OUTLINE, pts, 2)
    # Confetti shower along the angle
    rng = random.Random(int(ax * 7 + ay))
    cone_cols = ((242, 90, 90), (252, 206, 56), (90, 200, 80),
                 (90, 160, 250), (236, 110, 220))
    for _ in range(60):
        d = rng.uniform(L, 400)
        offset_n = rng.uniform(-d * 0.18, d * 0.18)
        px = ax + fwd[0] * d + nrm[0] * offset_n
        py = ay + fwd[1] * d + nrm[1] * offset_n
        if not (0 <= px < W and 0 <= py < H):
            continue
        c = rng.choice(cone_cols)
        w_ = rng.choice((4, 5))
        h_ = rng.choice((7, 9))
        piece = pygame.Surface((w_ + 2, h_ + 2), pygame.SRCALPHA)
        pygame.draw.rect(piece, OUTLINE,
                          pygame.Rect(0, 0, w_ + 2, h_ + 2),
                          border_radius=2)
        pygame.draw.rect(piece, c,
                          pygame.Rect(1, 1, w_, h_), border_radius=2)
        ang_p = rng.uniform(-60, 60)
        rot = pygame.transform.rotate(piece, ang_p)
        surf.blit(rot, (px - rot.get_width() // 2,
                          py - rot.get_height() // 2))
    # Flash at the muzzle
    muz_x = ax + fwd[0] * L
    muz_y = ay + fwd[1] * L
    for rg, a in ((22, 80), (14, 140), (8, 220)):
        flash = pygame.Surface((rg * 2, rg * 2), pygame.SRCALPHA)
        pygame.draw.circle(flash, (255, 240, 180, a), (rg, rg), rg)
        surf.blit(flash, (muz_x - rg, muz_y - rg))


def draw_confetti(surf, *, n_back=80, n_front=30, seed=11):
    rng = random.Random(seed)
    cols = ((242, 90, 90), (90, 200, 80), (90, 160, 250),
            (252, 206, 56), (236, 110, 220), (250, 130, 60))
    for _ in range(n_back):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        c = rng.choice(cols)
        r = rng.choice((1, 1, 2))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*c, 160), (r + 1, r + 1), r)
        surf.blit(s, (x, y))
    for _ in range(n_front):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        c = rng.choice(cols)
        w_ = rng.choice((4, 5, 6))
        h_ = rng.choice((8, 10, 12))
        ang = rng.uniform(-45, 45)
        piece = pygame.Surface((w_ + 4, h_ + 4), pygame.SRCALPHA)
        pygame.draw.rect(piece, OUTLINE,
                          pygame.Rect(2, 2, w_, h_), border_radius=2)
        pygame.draw.rect(piece, c,
                          pygame.Rect(3, 3, w_ - 2, h_ - 2),
                          border_radius=2)
        rot = pygame.transform.rotate(piece, ang)
        surf.blit(rot, (x - rot.get_width() // 2,
                          y - rot.get_height() // 2))


def draw_streamer(surf, p0, p1, p2, color, *, width=5):
    pts = []
    for i in range(25):
        t = i / 24
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((int(x), int(y)))
    pygame.draw.lines(surf, OUTLINE, False, pts, width + 2)
    pygame.draw.lines(surf, color, False, pts, width)
    pygame.draw.lines(surf, (255, 255, 255, 180), False,
                      [(x, y - 1) for (x, y) in pts], max(1, width // 3))


def draw_horizontal_banner(surf, top_y, *, w, h, text, color=KFC_RED,
                            text_color=GOLD_HI, font_size=28):
    """Wide horizontal banner across the canvas with hanging tassels."""
    band = pygame.Rect((W - w) // 2, top_y, w, h)
    # Body shadow
    pygame.draw.rect(surf, (0, 0, 0, 110),
                      band.inflate(8, 8).move(3, 5), border_radius=6)
    # Outline
    pygame.draw.rect(surf, OUTLINE, band.inflate(6, 6), border_radius=6)
    pygame.draw.rect(surf, _shade(color, -40), band.inflate(4, 4),
                      border_radius=6)
    pygame.draw.rect(surf, color, band.inflate(2, 2), border_radius=6)
    # Inner gold band
    inner = band.inflate(-6, -10)
    pygame.draw.rect(surf, GOLD_DK, inner.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, GOLD_MID, inner, border_radius=4)
    pygame.draw.rect(surf, GOLD_HI,
                      pygame.Rect(inner.x + 4, inner.y + 4,
                                  inner.width - 8, max(3, inner.height // 4)),
                      border_radius=3)
    # Hanging tassels at the ends (notched parallelogram)
    for sgn, ax_ in ((-1, band.left), (1, band.right)):
        tip = h // 2
        tail = [
            (ax_, band.top),
            (ax_ + sgn * tip, band.top + h // 2),
            (ax_, band.bottom),
            (ax_ - sgn * tip // 2, band.centery),
        ]
        pygame.draw.polygon(surf, OUTLINE,
                             [(p[0] + sgn * 2, p[1]) for p in tail])
        pygame.draw.polygon(surf, _shade(color, -50), tail)
        pygame.draw.polygon(surf, color,
                             [(p[0], p[1] + 1) for p in tail])
    # Hanging rope segments above the banner
    for x in (band.left + 22, band.right - 22):
        pygame.draw.line(surf, (60, 40, 12),
                          (x, 0), (x, band.top), 3)
    # Text
    fnt = _font(font_size, bold=True)
    out_txt = fnt.render(text, True, OUTLINE)
    fill_txt = fnt.render(text, True, text_color)
    cx = band.centerx
    cy = band.centery
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if dx or dy:
                surf.blit(out_txt, (cx - out_txt.get_width() // 2 + dx,
                                     cy - out_txt.get_height() // 2 + dy))
    surf.blit(fill_txt, (cx - fill_txt.get_width() // 2,
                          cy - fill_txt.get_height() // 2))


# --- Backgrounds -----------------------------------------------------------

def night_sky(phase=0.05):
    buckets = _biome.PHASE_BUCKETS
    pal = _biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(W, H, H, pal, int(phase * buckets))
    return sky, pal


def warm_radial_bg(surf, cx, cy):
    """Warm radial glow centered on (cx, cy) - party stage feel."""
    surf.fill((28, 16, 48))
    for r, a in ((400, 24), (300, 36), (220, 52), (150, 80), (90, 110)):
        glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 200, 110, a), (r, r), r)
        surf.blit(glow, (cx - r, cy - r))


def starfield(surf, n=40, seed=7):
    rng = random.Random(seed)
    for _ in range(n):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, int(H * 0.65))
        r = rng.choice((1, 1, 1, 2))
        a = rng.randint(120, 255)
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (r + 1, r + 1), r)
        surf.blit(s, (x, y))


# ===========================================================================
# V1a - BIRTHDAY BUCKET
# ===========================================================================

def draw_v1a(surf):
    warm_radial_bg(surf, W // 2, H // 2 + 50)

    # Headline at top: "3000 GAMES PLAYED!"
    draw_outlined_text(surf, "3,000 GAMES", (W // 2, 50),
                        size=44, fill=COIN_GOLD, outline_w=5, sparkles=8)
    draw_outlined_text(surf, "PLAYED!", (W // 2, 100),
                        size=44, fill=KFC_RED, outline_w=5, sparkles=0)

    # Balloons floating up (back layer, behind bucket)
    balloon_specs = [
        (40,  240,  BALLOON_COLORS[0],  -8),
        (90,  180,  BALLOON_COLORS[3],   6),
        (260, 200,  BALLOON_COLORS[4],  -4),
        (310, 270,  BALLOON_COLORS[2],   8),
        (20,  340,  BALLOON_COLORS[5],   0),
        (340, 350,  BALLOON_COLORS[1],  -6),
    ]
    for cx_b, cy_b, col, tilt in balloon_specs:
        draw_balloon(surf, cx_b, cy_b, color=col, tilt_deg=tilt, size=28,
                     sway=cx_b * 0.1)

    # Streamers
    draw_streamer(surf, (-20, 140), (W // 2, 250), (W + 20, 130),
                  (252, 206, 56), width=5)
    draw_streamer(surf, (-10, 220), (W // 2 + 30, 320), (W + 10, 230),
                  (236, 110, 220), width=4)

    # Bucket
    bucket_rect = pygame.Rect(W // 2 - 130, 360, 260, 230)
    rim, _ = draw_bucket(surf, bucket_rect, label_text="3,000 GAMES")

    # Pip-with-hat flying ABOVE the pink streamer (pink one arcs the
    # lowest, peaking around y=220 at the edges). Pre-built sprite via
    # make_pip_with_hat - supersampled for sharper edges. Positioned
    # so the pom-pom of his hat clears the "PLAYED!" headline (which
    # ends around y=130).
    pip_sprite = make_pip_with_hat(frame=1, tilt=0, scale=1.5,
                                    hat_color1=(242, 90, 90),
                                    hat_color2=(252, 206, 56),
                                    hat_tilt=0)
    pip_rect = pip_sprite.get_rect(midbottom=(W // 2, 290))
    surf.blit(pip_sprite, pip_rect.topleft)

    # Four CYLINDRICAL birthday candles "3 0 0 0" on the cake top -
    # cylindrical wax stick with vivid digit + diagonal stripe + wick
    # + flame. Pip no longer overlaps them, so all four read cleanly.
    digits = ("3", "0", "0", "0")
    candle_xs = [bucket_rect.left + bucket_rect.width * u
                  for u in (0.16, 0.39, 0.61, 0.84)]
    stripe_colors = ((242,  60,  70),
                     (252, 200,  56),
                     ( 90, 200,  80),
                     ( 90, 160, 250))
    candle_sprites = [
        make_cylindrical_candle(
            d, body_h=66, body_w=24,
            wax_color=(252, 244, 226),
            stripe_color=col,
            digit_color=col)
        for d, col in zip(digits, stripe_colors)
    ]
    for cx_d, sprite in zip(candle_xs, candle_sprites):
        rect = sprite.get_rect(midbottom=(int(cx_d), rim.top))
        surf.blit(sprite, rect.topleft)
    # Sparkles around the Pip sprite
    rng = random.Random(7)
    for _ in range(8):
        sx = rng.randint(pip_rect.left - 16, pip_rect.right + 16)
        sy = rng.randint(pip_rect.top, pip_rect.bottom)
        r = rng.randint(2, 4)
        pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
        pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                            max(1, r - 2))

    # Confetti (on top of everything)
    draw_confetti(surf, n_back=80, n_front=24, seed=3)

    draw_tagline(surf, "Happy 3,000th! Cake's on us. Keep flying.",
                  H - 28, size=15)


# ===========================================================================
# V1b - FIREWORKS SHOW
# ===========================================================================

def draw_v1b(surf):
    # Deep night sky
    surf.fill((10, 8, 38))
    # Sky gradient: dark top to slightly lighter at bottom (city horizon)
    for y in range(H):
        u = y / (H - 1)
        c = (int(10 + (40 - 10) * u),
             int(8 + (28 - 8) * u),
             int(38 + (60 - 38) * u))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))
    starfield(surf, n=60, seed=2)

    # Multiple fireworks bursts at varying sizes / positions
    bursts = [
        (90,  170, FIREWORK_COLORS[0], 80, 18, 1),
        (270, 130, FIREWORK_COLORS[2], 70, 16, 2),
        (180, 260, FIREWORK_COLORS[1], 90, 20, 3),
        (300, 340, FIREWORK_COLORS[3], 55, 14, 4),
        (50,  340, FIREWORK_COLORS[4], 50, 12, 5),
    ]
    for cx_b, cy_b, col, r, n_arms, seed in bursts:
        draw_firework_burst(surf, cx_b, cy_b, color=col, r=r,
                             n_arms=n_arms, seed=seed)

    # Banner at top
    draw_outlined_text(surf, "3,000 GAMES", (W // 2, 56),
                        size=42, fill=COIN_GOLD, outline_w=5, sparkles=10)
    draw_outlined_text(surf, "PLAYED!", (W // 2, 102),
                        size=42, fill=(255, 110, 110), outline_w=5)

    # Bucket - smaller, anchored at bottom
    bucket_rect = pygame.Rect(W // 2 - 90, H - 230, 180, 180)
    rim, _ = draw_bucket(surf, bucket_rect, label_text="3,000", stripe_count=5)

    # Pip flying mid-frame (above the bucket), large + tilted - halo
    # FIRST, then Pip on top so his colours stay vivid.
    pip = parrot.get_parrot(0, 20)
    pip_scaled = pygame.transform.smoothscale(
        pip, (int(pip.get_width() * 1.6),
              int(pip.get_height() * 1.6)))
    pip_x = W // 2 - pip_scaled.get_width() // 2 - 8
    pip_y = H // 2 + 30
    # Soft warm halo behind Pip (drawn BEFORE Pip)
    halo_r = 80
    halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
    for r_g, a_g in ((80, 50), (60, 90), (40, 130)):
        pygame.draw.circle(halo, (255, 220, 130, a_g),
                            (halo_r, halo_r), r_g)
    surf.blit(halo,
              (pip_x + pip_scaled.get_width() // 2 - halo_r,
               pip_y + pip_scaled.get_height() // 2 - halo_r))
    surf.blit(pip_scaled, (pip_x, pip_y))

    # Sparkles
    rng = random.Random(11)
    for _ in range(40):
        sx = rng.randint(0, W - 1)
        sy = rng.randint(0, H - 1)
        r = rng.choice((1, 1, 2))
        pygame.draw.circle(surf, (255, 255, 255), (sx, sy), r)

    draw_tagline(surf, "Keep the fireworks going.",
                  H - 28, size=16, color=(255, 220, 160))


# ===========================================================================
# V1c - DISCO BUCKET
# ===========================================================================

def draw_v1c(surf):
    # Deep purple background
    for y in range(H):
        u = y / (H - 1)
        c = (int(40 + (90 - 40) * u),
             int(20 + (40 - 20) * u),
             int(80 + (120 - 80) * u))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))

    # Light beams from the disco ball (drawn behind ball)
    ball_cx, ball_cy = W // 2, 110
    for i in range(8):
        ang = i * math.pi / 4 + 0.2
        col = DISCO_BEAM_COLS[i % 4]
        draw_disco_beam(surf, (ball_cx, ball_cy),
                         color=col, ang_rad=ang,
                         half_spread=0.08, length=500, alpha=70)

    # Disco ball
    draw_disco_ball(surf, ball_cx, ball_cy, 40)

    # Checkered dance floor (perspective: trapezoid receding to back)
    floor_top_y = H - 130
    floor_layer = pygame.Surface((W, H - floor_top_y), pygame.SRCALPHA)
    n_rows = 6
    for row in range(n_rows):
        u0 = row / n_rows
        u1 = (row + 1) / n_rows
        y0 = u0 * (H - floor_top_y)
        y1 = u1 * (H - floor_top_y)
        # Trapezoid width (narrow back -> wide front)
        x0_l = W // 2 - (40 + (W // 2 - 40) * u0)
        x0_r = W // 2 + (40 + (W // 2 - 40) * u0)
        x1_l = W // 2 - (40 + (W // 2 - 40) * u1)
        x1_r = W // 2 + (40 + (W // 2 - 40) * u1)
        # 6 columns of tiles
        n_cols = 6
        for col in range(n_cols):
            v0 = col / n_cols
            v1 = (col + 1) / n_cols
            px0_top = x0_l + (x0_r - x0_l) * v0
            px1_top = x0_l + (x0_r - x0_l) * v1
            px0_bot = x1_l + (x1_r - x1_l) * v0
            px1_bot = x1_l + (x1_r - x1_l) * v1
            light = (row + col) % 2 == 0
            c = (220, 220, 230) if light else (40, 30, 60)
            pygame.draw.polygon(floor_layer, c,
                                 [(px0_top, y0), (px1_top, y0),
                                  (px1_bot, y1), (px0_bot, y1)])
    surf.blit(floor_layer, (0, floor_top_y))

    # Bucket - centered, rainbow stripes
    bucket_rect = pygame.Rect(W // 2 - 105, 250, 210, 210)
    rim, _ = draw_bucket(surf, bucket_rect, label_text="3,000",
                          rainbow=True, stripe_count=7)

    # Music notes floating
    note_specs = [
        (60,  220, (252, 206, 56),   8),
        (300, 200, (90, 200, 80),   -12),
        (40,  330, (110, 240, 255),  4),
        (320, 360, (236, 110, 220), -8),
        (180, 180, (255, 255, 255),  16),
    ]
    for nx, ny, col, tilt in note_specs:
        draw_music_note(surf, nx, ny, col, tilt_deg=tilt)

    # Pip dancing on top
    pip = parrot.get_parrot(0, -22)
    pip_scaled = pygame.transform.smoothscale(
        pip, (int(pip.get_width() * 1.3),
              int(pip.get_height() * 1.3)))
    pip_x = W // 2 - pip_scaled.get_width() // 2 - 6
    pip_y = rim.top - pip_scaled.get_height() + 18
    surf.blit(pip_scaled, (pip_x, pip_y))

    # Headline
    draw_outlined_text(surf, "3,000 GAMES", (W // 2, 50),
                        size=44, fill=(255, 110, 200), outline_w=5,
                        sparkles=8)
    draw_outlined_text(surf, "PLAYED!", (W // 2, 100),
                        size=44, fill=(110, 240, 255), outline_w=5)

    draw_tagline(surf, "Keep the party going.", H - 28, size=16,
                  color=(255, 220, 250))


# ===========================================================================
# V1d - BANNER DROP
# ===========================================================================

def draw_v1d(surf):
    # Bright cheerful blue sky background
    for y in range(H):
        u = y / (H - 1)
        c = (int(90 + (160 - 90) * u),
             int(180 + (220 - 180) * u),
             int(240 + (255 - 240) * u))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))

    # Banner unfurled across the top
    draw_horizontal_banner(surf, 30,
                            w=W - 32, h=84,
                            text="3,000 GAMES PLAYED!",
                            color=KFC_RED, text_color=GOLD_HI,
                            font_size=26)

    # Streamers hanging from banner
    for x_a, x_b in ((70, 50), (W - 70, W - 50),
                     (150, 130), (W - 150, W - 130)):
        draw_streamer(surf, (x_a, 120), ((x_a + x_b) // 2, 200), (x_b, 320),
                       random.Random(x_a).choice(BALLOON_COLORS), width=4)

    # Bucket at center-low
    bucket_rect = pygame.Rect(W // 2 - 100, 380, 200, 210)
    rim, _ = draw_bucket(surf, bucket_rect, label_text="3,000 PARTY",
                          stripe_count=7)

    # Confetti cannons firing diagonally from each side
    draw_confetti_cannon(surf, (-10, H - 100), -30)
    draw_confetti_cannon(surf, (W + 10, H - 100), 210)

    # Pip popping out of the bucket
    pip = parrot.get_parrot(0, 0)
    pip_scaled = pygame.transform.smoothscale(
        pip, (int(pip.get_width() * 1.5),
              int(pip.get_height() * 1.5)))
    pip_x = W // 2 - pip_scaled.get_width() // 2
    pip_y = rim.top - pip_scaled.get_height() + 12
    surf.blit(pip_scaled, (pip_x, pip_y))
    # "POP!" speech bubble next to Pip
    pop_layer = pygame.Surface((60, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(pop_layer, OUTLINE,
                        pygame.Rect(0, 0, 60, 32))
    pygame.draw.ellipse(pop_layer, KFC_WHITE,
                        pygame.Rect(2, 2, 56, 28))
    pop_fnt = _font(22, bold=True)
    pop_t = pop_fnt.render("POP!", True, KFC_RED)
    pop_layer.blit(pop_t, ((60 - pop_t.get_width()) // 2,
                            (32 - pop_t.get_height()) // 2))
    # Tail pointing to Pip
    pygame.draw.polygon(pop_layer, OUTLINE,
                        [(5, 28), (15, 32), (20, 28)])
    pygame.draw.polygon(pop_layer, KFC_WHITE,
                        [(7, 28), (15, 30), (18, 28)])
    surf.blit(pop_layer,
              (pip_x + pip_scaled.get_width() - 14, pip_y - 18))

    # Sparkles
    rng = random.Random(15)
    for _ in range(15):
        sx = rng.randint(40, W - 40)
        sy = rng.randint(150, H - 50)
        r = rng.randint(2, 4)
        pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
        pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                            max(1, r - 2))

    # Confetti
    draw_confetti(surf, n_back=50, n_front=18, seed=4)

    draw_tagline(surf, "The bucket. The bird. The legend.",
                  H - 28, size=16, color=(255, 255, 255))


# ===========================================================================
# V1e - TROPHY PEDESTAL
# ===========================================================================

def draw_v1e(surf):
    # Golden-hour gradient
    for y in range(H):
        u = y / (H - 1)
        c = (int(60 + (255 - 60) * u),
             int(40 + (180 - 40) * u),
             int(80 + (90 - 80) * u))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))

    # Radial sun rays from the centre of the pedestal area
    ray_origin = (W // 2, 280)
    rays_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    n_rays = 16
    for i in range(n_rays):
        ang = i * 2 * math.pi / n_rays
        L = 500
        spread = 0.06
        pts = [
            ray_origin,
            (ray_origin[0] + math.cos(ang - spread) * L,
             ray_origin[1] + math.sin(ang - spread) * L),
            (ray_origin[0] + math.cos(ang + spread) * L,
             ray_origin[1] + math.sin(ang + spread) * L),
        ]
        a = 50 if i % 2 == 0 else 30
        pygame.draw.polygon(rays_layer, (255, 240, 180, a), pts)
    surf.blit(rays_layer, (0, 0))

    # Pedestal at the bottom - tall and gold tiered with engraved plaque
    ped_top = H - 240
    ped_w_top = 200
    ped_w_bot = 240
    pts_ped = [
        (W // 2 - ped_w_top // 2, ped_top),
        (W // 2 + ped_w_top // 2, ped_top),
        (W // 2 + ped_w_bot // 2, ped_top + 150),
        (W // 2 - ped_w_bot // 2, ped_top + 150),
    ]
    pygame.draw.polygon(surf, OUTLINE, [(p[0], p[1] + 2) for p in pts_ped])
    pygame.draw.polygon(surf, GOLD_DK,
                         [(p[0], p[1] + 1) for p in pts_ped])
    pygame.draw.polygon(surf, GOLD_MID, pts_ped)
    # Top rim of pedestal (bright lit edge)
    pygame.draw.polygon(surf, GOLD_HI,
                         [(W // 2 - ped_w_top // 2 + 6, ped_top + 4),
                          (W // 2 + ped_w_top // 2 - 6, ped_top + 4),
                          (W // 2 + ped_w_top // 2 - 6, ped_top + 16),
                          (W // 2 - ped_w_top // 2 + 6, ped_top + 16)])
    # Pedestal base (wider lower step)
    base = pygame.Rect(W // 2 - 145, ped_top + 150, 290, 42)
    pygame.draw.rect(surf, OUTLINE, base.inflate(6, 4), border_radius=4)
    pygame.draw.rect(surf, GOLD_DK, base.inflate(4, 2), border_radius=4)
    pygame.draw.rect(surf, GOLD_MID, base, border_radius=4)
    # Engraved plaque on the pedestal face
    plaque = pygame.Rect(W // 2 - 100, ped_top + 50, 200, 70)
    pygame.draw.rect(surf, OUTLINE, plaque.inflate(4, 4), border_radius=4)
    pygame.draw.rect(surf, (50, 28, 8), plaque, border_radius=4)
    pl_fnt = _font(20, bold=True)
    pl1 = pl_fnt.render("3,000 GAMES", True, GOLD_HI)
    pl2 = pl_fnt.render("PLAYED!", True, GOLD_HI)
    surf.blit(pl1, (plaque.centerx - pl1.get_width() // 2,
                     plaque.y + 8))
    surf.blit(pl2, (plaque.centerx - pl2.get_width() // 2,
                     plaque.y + 36))

    # Big BUCKET trophy sitting on TOP of the pedestal - the bucket IS
    # the trophy, with a gold ribbon banner draped across it.
    bucket_rect = pygame.Rect(W // 2 - 90, ped_top - 170, 180, 170)
    rim, _ = draw_bucket(surf, bucket_rect, label_text=None, stripe_count=7)
    # Drop a tiny crown on top of the bucket rim
    cr_cx = W // 2
    cr_y = rim.top - 12
    crown_pts = [
        (cr_cx - 22, cr_y + 12), (cr_cx - 22, cr_y + 2),
        (cr_cx - 11, cr_y + 8), (cr_cx, cr_y - 8),
        (cr_cx + 11, cr_y + 8), (cr_cx + 22, cr_y + 2),
        (cr_cx + 22, cr_y + 12),
    ]
    pygame.draw.polygon(surf, OUTLINE,
                        [(p[0], p[1] + 1) for p in crown_pts])
    pygame.draw.polygon(surf, GOLD_LO,
                        [(p[0], p[1]) for p in crown_pts])
    pygame.draw.polygon(surf, GOLD_HI,
                        [(cr_cx - 20, cr_y + 4),
                         (cr_cx, cr_y - 6),
                         (cr_cx + 20, cr_y + 4),
                         (cr_cx + 14, cr_y + 6),
                         (cr_cx, cr_y + 2),
                         (cr_cx - 14, cr_y + 6)])
    # Crown jewels
    pygame.draw.circle(surf, OUTLINE, (cr_cx, cr_y - 4), 4)
    pygame.draw.circle(surf, KFC_RED, (cr_cx, cr_y - 4), 3)
    pygame.draw.circle(surf, (255, 255, 255), (cr_cx, cr_y - 5), 1)
    for jx in (cr_cx - 11, cr_cx + 11):
        pygame.draw.circle(surf, OUTLINE, (jx, cr_y + 8), 3)
        pygame.draw.circle(surf, (90, 160, 250), (jx, cr_y + 8), 2)

    # Pip flying excitedly NEXT to the bucket-trophy (his award!)
    pip = parrot.get_parrot(0, 24)
    pip_scaled = pygame.transform.smoothscale(
        pip, (int(pip.get_width() * 1.4),
              int(pip.get_height() * 1.4)))
    pip_x = W // 2 + 70
    pip_y = bucket_rect.centery - pip_scaled.get_height() // 2 - 12
    # Drop shadow
    psh = pygame.Surface((pip_scaled.get_width() + 16, 18),
                          pygame.SRCALPHA)
    pygame.draw.ellipse(psh, (0, 0, 0, 90), psh.get_rect())
    surf.blit(psh, (pip_x - 8,
                      pip_y + pip_scaled.get_height() - 8))
    surf.blit(pip_scaled, (pip_x, pip_y))

    # Sparkles thick around the bucket-trophy
    rng = random.Random(13)
    for _ in range(22):
        sx = rng.randint(W // 2 - 130, W // 2 + 130)
        sy = rng.randint(150, ped_top + 10)
        r = rng.randint(2, 5)
        pygame.draw.circle(surf, OUTLINE, (sx, sy), r + 1)
        pygame.draw.circle(surf, GOLD_HI, (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1),
                            max(1, r - 2))

    # Headline
    draw_outlined_text(surf, "3,000 GAMES", (W // 2, 50),
                        size=44, fill=GOLD_HI, outline_w=5, sparkles=10)
    draw_outlined_text(surf, "PLAYED!", (W // 2, 100),
                        size=44, fill=KFC_RED, outline_w=5)

    draw_tagline(surf, "Champion of the skies.",
                  H - 28, size=18, color=(255, 240, 200))


# --- Variant registry + main -----------------------------------------------

VARIANTS = (
    ("v1a", "V1a Birthday Bucket",  draw_v1a),
    ("v1b", "V1b Fireworks Show",   draw_v1b),
    ("v1c", "V1c Disco Bucket",     draw_v1c),
    ("v1d", "V1d Banner Drop",      draw_v1d),
    ("v1e", "V1e Trophy Pedestal",  draw_v1e),
)


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((W, H))
    out_dir = os.path.join("docs", "celebrations", "3k_games", "v1_picker")
    os.makedirs(out_dir, exist_ok=True)

    frames = {}
    for key, label, fn in VARIANTS:
        screen.fill((0, 0, 0))
        fn(screen)
        frames[key] = screen.copy()
        path = os.path.join(out_dir, f"{key}.png")
        pygame.image.save(screen, path)
        print(f"saved {path}  ({label})")

    # 5-column compare strip
    GAP, LABEL_H, PAD = 14, 30, 18
    cell_w, cell_h = W, H
    canvas_w = cell_w * len(VARIANTS) + GAP * (len(VARIANTS) - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    label_font = pygame.font.SysFont(None, 22, bold=True)
    for i, (key, label, _) in enumerate(VARIANTS):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        pygame.draw.rect(canvas, (60, 70, 100),
                         pygame.Rect(x - 1, y - 1, cell_w + 2, cell_h + 2),
                         width=1)
        canvas.blit(frames[key], (x, y))
        lbl = label_font.render(label, True, (30, 35, 55))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2,
                          y + cell_h + 8))
    out_path = os.path.join(out_dir, "compare.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  {canvas.get_size()}")


if __name__ == "__main__":
    sys.exit(main() or 0)
