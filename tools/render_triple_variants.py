"""Five pure-dollar-sign variants — preview only.

User feedback: drop the gold coin disc entirely; the icon should be just
the `$` glyph in different finishings. Each variant is a draw function
with the same signature as the existing
`game.dollar_coin_glyphs.draw_coin_font_bold`:

    fn(surf, cx, cy, pulse=0.0)

Centred on (cx, cy). No background disc — every variant is a bare glyph,
sized to match the previous icon's footprint so collision/HUD layout
stay aligned. Imported by `tools/render_triple_gameplay.py`. Does NOT
modify any game module.
"""
import math
import pygame


# ── Palette ─────────────────────────────────────────────────────────────────
BILL_GREEN_LITE = (110, 210, 140)
BILL_GREEN      = ( 75, 165, 105)
BILL_GREEN_MID  = ( 55, 135,  85)
BILL_GREEN_DK   = ( 35, 100,  65)
BILL_GREEN_DEEP = ( 20,  60,  40)
GOLD_HI         = (255, 232, 130)
GOLD_BODY       = (255, 200,  40)
GOLD_LO         = (190, 130,  20)
NEON_CORE       = (180, 255, 200)
NEON_GLOW       = ( 80, 220, 130)
NEAR_BLACK      = ( 12,  16,  22)
WHITE           = (255, 255, 255)


def _font(size):
    """Bold sans glyph font. Cached per (size) by pygame."""
    return pygame.font.SysFont(None, size, bold=True)


def _glyph_mask(size, glyph="$"):
    """Render the `$` glyph onto a tight RGBA surface where the glyph is
    opaque white and the rest is transparent. Used as a multiply mask for
    gradient/foil fills."""
    f = _font(size)
    img = f.render(glyph, True, (255, 255, 255))
    # Convert to SRCALPHA so we can use it as a multiply mask.
    out = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    out.blit(img, (0, 0))
    return out


def _blit_glyph(surf, text, size, center, color):
    """Render a glyph at `size` and centre-blit it on `surf`."""
    img = _font(size).render(text, True, color)
    r = img.get_rect(center=center)
    surf.blit(img, r.topleft)


# ── V1 — original green (the current $ minus the coin) ─────────────────────
def draw_v1_plain_green(surf, cx, cy, pulse=0.0):
    """The current dollar sign with the gold disc removed. Same green fill,
    same dark-green 1-px outline, same 28-pt font as draw_coin_font_bold."""
    size = 30
    # Dark outline drawn 8-direction so the glyph stays readable on dark sky.
    out = _font(size).render("$", True, BILL_GREEN_DK)
    fill = _font(size).render("$", True, BILL_GREEN)
    r = fill.get_rect(center=(cx, cy + 1))
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(fill, r.topleft)


# ── V2 — bold stamp (heavy outline + drop shadow) ──────────────────────────
def draw_v2_stamp(surf, cx, cy, pulse=0.0):
    """Heavier weight: thicker dark outline + soft drop shadow gives the
    glyph a banknote-stamp impression. Reads as currency at any size."""
    size = 32
    shadow = _font(size).render("$", True, NEAR_BLACK)
    shadow.set_alpha(140)
    sh_rect = shadow.get_rect(center=(cx + 2, cy + 3))
    surf.blit(shadow, sh_rect.topleft)

    out = _font(size).render("$", True, BILL_GREEN_DEEP)
    fill = _font(size).render("$", True, BILL_GREEN_LITE)
    r = fill.get_rect(center=(cx, cy + 1))
    # 2-px outline on all 8 directions for a chunky stamp feel.
    for ox in (-2, -1, 0, 1, 2):
        for oy in (-2, -1, 0, 1, 2):
            if ox == 0 and oy == 0:
                continue
            if abs(ox) == 2 and abs(oy) == 2:
                continue   # skip corners → rounded outline
            surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(fill, r.topleft)


# ── V3 — gold luxury (vertical gradient + dark outline) ────────────────────
def draw_v3_gold(surf, cx, cy, pulse=0.0):
    """Same `$` shape, but filled with a vertical gold gradient instead of
    green. Premium-currency feel. The glyph mask is multiplied against a
    pre-built gradient strip so the gold transition is smooth."""
    size = 32
    mask = _glyph_mask(size)
    mw, mh = mask.get_size()

    # Vertical gold gradient — light at top, deeper at bottom.
    grad = pygame.Surface((mw, mh), pygame.SRCALPHA)
    for yy in range(mh):
        t = yy / max(1, mh - 1)
        if t < 0.45:
            u = t / 0.45
            col = (
                int(GOLD_HI[0]   + (GOLD_BODY[0] - GOLD_HI[0])   * u),
                int(GOLD_HI[1]   + (GOLD_BODY[1] - GOLD_HI[1])   * u),
                int(GOLD_HI[2]   + (GOLD_BODY[2] - GOLD_HI[2])   * u),
                255,
            )
        else:
            u = (t - 0.45) / 0.55
            col = (
                int(GOLD_BODY[0] + (GOLD_LO[0]   - GOLD_BODY[0]) * u),
                int(GOLD_BODY[1] + (GOLD_LO[1]   - GOLD_BODY[1]) * u),
                int(GOLD_BODY[2] + (GOLD_LO[2]   - GOLD_BODY[2]) * u),
                255,
            )
        pygame.draw.line(grad, col, (0, yy), (mw, yy))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Dark outline behind the gradient fill so it pops on any background.
    out_img = _font(size).render("$", True, (95, 60, 0))
    r = grad.get_rect(center=(cx, cy + 1))
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(out_img, (r.x + ox, r.y + oy))
    surf.blit(grad, r.topleft)


# ── V4 — embossed 3D (highlight + body + shadow layers) ────────────────────
def draw_v4_embossed(surf, cx, cy, pulse=0.0):
    """Three-layer embossed green: dark shadow offset down-right, mid-tone
    body, bright highlight offset up-left. Gives the bare glyph
    surprising volume without any background disc."""
    size = 32
    shadow = _font(size).render("$", True, BILL_GREEN_DEEP)
    body   = _font(size).render("$", True, BILL_GREEN)
    hi     = _font(size).render("$", True, BILL_GREEN_LITE)
    r = body.get_rect(center=(cx, cy + 1))

    surf.blit(shadow, (r.x + 2, r.y + 2))
    surf.blit(body,   (r.x,     r.y))
    surf.blit(hi,     (r.x - 1, r.y - 1))


# ── V5 — neon glow (soft halo + bright core) ───────────────────────────────
def draw_v5_neon(surf, cx, cy, pulse=0.0):
    """Bright cyan-green core with a soft outer halo. Glow alpha pulses
    with `pulse` so it feels lit from inside. Arcade / retro feel."""
    size = 30
    breathe = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse * 2.0))

    # Halo: render the glyph multiple times at increasing offsets with
    # decreasing alpha. Cheap fake-blur that reads as glow.
    halo_color = NEON_GLOW
    halo_layers = (
        (5, int(50 * breathe)),
        (3, int(90 * breathe)),
        (2, int(130 * breathe)),
    )
    glyph_halo = _font(size).render("$", True, halo_color)
    r = glyph_halo.get_rect(center=(cx, cy + 1))
    for radius, alpha in halo_layers:
        layer = glyph_halo.copy()
        layer.set_alpha(alpha)
        for ang in range(0, 360, 45):
            ox = int(math.cos(math.radians(ang)) * radius)
            oy = int(math.sin(math.radians(ang)) * radius)
            surf.blit(layer, (r.x + ox, r.y + oy))

    # Core — bright cyan-green at full alpha.
    core = _font(size).render("$", True, NEON_CORE)
    surf.blit(core, r.topleft)
    # Tiny white sheen at the centre — sells the "lit up" look.
    sheen = _font(size).render("$", True, WHITE)
    sheen.set_alpha(140)
    surf.blit(sheen, (r.x, r.y - 1))


VARIANTS = {
    1: ("1 — plain green",      draw_v1_plain_green),
    2: ("2 — bold stamp",       draw_v2_stamp),
    3: ("3 — gold luxury",      draw_v3_gold),
    4: ("4 — embossed 3D",      draw_v4_embossed),
    5: ("5 — neon glow",        draw_v5_neon),
}
