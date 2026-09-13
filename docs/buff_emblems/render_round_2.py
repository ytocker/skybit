"""Round-2 exploration sheet for Skybit's 10 active-power-up HUD emblems.

Mostly self-contained headless harness. It re-implements the round-1
supersample kit the AD praised (4x supersample, vertical-gradient shading,
top-left key light, a contact-shadow ellipse, single consistent outline
weight) and draws the round-2 emblem set on top of it. The only repo import is
the production `_draw_buff_icon`, used ONLY for the top "CURRENT" before/after
strip; if the repo isn't importable the sheet still renders the new set.

Run:  SDL_VIDEODRIVER=dummy python docs/buff_emblems/render_round_2.py
Out:  docs/buff_emblems/round_2.png

Exploration only; production hud.py is untouched.
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
# Repo root on the path so the CURRENT (production) strip can render the real
# _draw_buff_icon for the before/after comparison the AD asked us to keep.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame

pygame.init()

# Production emblem renderer + plate, used ONLY for the top "CURRENT" strip.
# Guarded so the harness stays portable if the repo can't be imported.
try:
    pygame.display.set_mode((1, 1))
    from game.hud import _na_plate, _draw_buff_icon, _NA_PAD, _ENERGY_FULL  # noqa: E402
    _HAVE_PROD = True
except Exception:  # pragma: no cover - portability guard for the harness
    _HAVE_PROD = False


# ---------------------------------------------------------------------------
# Supersample kit (mirrors hud.py conventions; kept local so the new art is
# dependency-free). All emblem art is drawn at SS scale then downsampled, so
# curves and the key-light highlight stay crisp at the 32px HUD footprint.
# ---------------------------------------------------------------------------
_SS = 4  # 4x supersample matches the production kit's quality bar


def _lerp(a, b, t):
    return a + (b - a) * t


def _mix(c1, c2, t):
    return (
        int(_lerp(c1[0], c2[0], t)),
        int(_lerp(c1[1], c2[1], t)),
        int(_lerp(c1[2], c2[2], t)),
    )


def _shade(c, f):
    # f<1 darkens, f>1 lightens; clamps to byte range.
    return (
        max(0, min(255, int(c[0] * f))),
        max(0, min(255, int(c[1] * f))),
        max(0, min(255, int(c[2] * f))),
    )


# One outline color + weight (in SS px) across the whole set for cohesion.
_OUTLINE = (28, 24, 38)
_OW = max(2, 3 * _SS // 2)  # ~1.5px at the 32px footprint


def _new_raw(size):
    return pygame.Surface((size * _SS, size * _SS), pygame.SRCALPHA)


def _vgrad_circle(surf, cx, cy, r, top, bottom):
    # Vertical gradient clipped to a circle: cheap volumetric shading that
    # reads as a top-lit sphere/disc. Drawn at SS scale.
    if r <= 0:
        return
    grad = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for y in range(r * 2):
        t = y / max(1, (r * 2 - 1))
        pygame.draw.line(grad, _mix(top, bottom, t), (0, y), (r * 2, y))
    mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (cx - r, cy - r))


def _vgrad_mask(surf, mask_pts, y0, y1, top, bottom, ellipse_rect=None):
    """Vertical gradient clipped to an arbitrary polygon (or ellipse) mask."""
    W, Hh = surf.get_size()
    band = pygame.Surface((W, Hh), pygame.SRCALPHA)
    for y in range(max(0, y0), min(Hh, y1)):
        t = (y - y0) / max(1, (y1 - y0))
        pygame.draw.line(band, _mix(top, bottom, t), (0, y), (W, y))
    mask = pygame.Surface((W, Hh), pygame.SRCALPHA)
    if ellipse_rect is not None:
        pygame.draw.ellipse(mask, (255, 255, 255, 255), ellipse_rect)
    else:
        pygame.draw.polygon(mask, (255, 255, 255, 255), mask_pts)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(band, (0, 0))


def _key_light(surf, cx, cy, r, strength=64):
    # Top-left specular bloom shared by every emblem for one light direction.
    if r <= 0:
        return
    hl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(
        hl, (255, 255, 255, strength), (int(r * 0.7), int(r * 0.62)), int(r * 0.55)
    )
    hl = pygame.transform.smoothscale(hl, (r * 2, r * 2))
    mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (cx - r, cy - r))


def _contact_shadow_small(out, size):
    # Soft ellipse under the emblem: grounds it on the plate, same for all 10.
    sh = pygame.Surface((size, size), pygame.SRCALPHA)
    w = int(size * 0.60)
    h = max(2, int(size * 0.15))
    cx = size // 2
    cy = int(size * 0.87)
    pygame.draw.ellipse(sh, (0, 0, 0, 55), (cx - w // 2, cy - h // 2, w, h))
    out.blit(sh, (0, 0))


def _finish(size, ss):
    """Downsample the SS emblem onto a size x size surface with one contact
    shadow under it (drawn first so the emblem sits on top)."""
    out = pygame.Surface((size, size), pygame.SRCALPHA)
    _contact_shadow_small(out, size)
    out.blit(pygame.transform.smoothscale(ss, (size, size)), (0, 0))
    return out


def _star(ss, cx, cy, r, color):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    pygame.draw.polygon(ss, color, pts)
    pygame.draw.polygon(ss, _OUTLINE, pts, max(2, _OW - 1))


def _arrow(ss, x1, y1, x2, y2, col):
    w = max(2, _OW)
    pygame.draw.line(ss, col, (x1, y1), (x2, y2), w)
    ang = math.atan2(y2 - y1, x2 - x1)
    h = max(4, int(_OW * 2.4))
    for da in (math.radians(150), math.radians(-150)):
        hx = x2 + math.cos(ang + da) * h
        hy = y2 + math.sin(ang + da) * h
        pygame.draw.line(ss, col, (x2, y2), (hx, hy), w)


# ---------------------------------------------------------------------------
# Function-family palette. ONE hue per function; tiers within a family are
# value/saturation steps of the SAME hue (magnet->mega, shrink->grow). This is
# the systematic fix for the two-reds / two-purples collisions.
# ---------------------------------------------------------------------------
PAL = {
    # attraction family = RED; mega tier = gold/orange body + violet aura
    "magnet_body": (216, 56, 50),
    "magnet_dark": (140, 28, 30),
    "magnet_tip": (236, 236, 240),
    "mega_body": (242, 170, 42),
    "mega_dark": (178, 106, 18),
    "mega_aura": (150, 70, 220),
    "mega_pip": (255, 244, 196),
    "mega_tip": (255, 248, 224),
    # time family = BLUE (slowmo benchmark)
    "time_face": (236, 244, 255),
    "time_rim": (72, 122, 212),
    "time_rim_d": (40, 78, 158),
    "time_hand": (28, 44, 92),
    # direction (reverse) = TEAL-GREEN, non-circular silhouette
    "rev_body": (40, 202, 168),
    "rev_dark": (16, 130, 112),
    "rev_lite": (176, 250, 232),
    # currency multiplier (triple) = GOLD/YELLOW
    "coin_face": (255, 214, 84),
    "coin_dark": (196, 142, 22),
    "coin_lite": (255, 244, 176),
    "coin_glyph": (110, 72, 6),
    # food (kfc) = KFC red bucket + warm browns
    "kfc_red": (210, 38, 40),
    "kfc_red_d": (150, 22, 26),
    "kfc_white": (248, 244, 238),
    "drum_brown": (190, 122, 60),
    "drum_brown_d": (138, 80, 36),
    "bone": (245, 238, 224),
    # phase (ghost) = cool WHITE / cyan, dimmed
    "ghost_body": (224, 232, 244),
    "ghost_body_d": (170, 188, 214),
    "ghost_edge": (150, 232, 248),
    "ghost_eye": (60, 78, 120),
    # size family = INDIGO/PURPLE; shrink = darker step, grow = brighter step
    "size_hue": (134, 98, 232),
    "size_hue_d": (84, 56, 168),
    "size_hue_l": (198, 178, 252),
    "size_fig": (120, 86, 214),
    "size_fig_d": (78, 52, 150),
    # traversal (rail) = STEEL-BLUE cart + bright AMBER track
    "rail_body": (98, 140, 198),
    "rail_body_d": (54, 88, 142),
    "rail_amber": (255, 198, 72),
    "rail_amber_d": (200, 140, 32),
}


# ---------------------------------------------------------------------------
# Emblem builders. Each returns a size x size SRCALPHA surface (contact shadow
# + emblem), drawn at SS internally.
# ---------------------------------------------------------------------------

# ---- magnet / megamagnet : a shared horseshoe ------------------------------
def _horseshoe(ss, S, body, dark, tipcol, scale=1.0):
    cx = S // 2
    cy = int(S * 0.50)
    outer = int(S * 0.34 * scale)
    inner = int(S * 0.17 * scale)
    # Gradient ring: a full top-lit disc, then carve the inner hole + the
    # downward leg gap so it reads as a U opening downward.
    ring = pygame.Surface((S, S), pygame.SRCALPHA)
    _vgrad_circle(ring, cx, cy, outer, _shade(body, 1.28), dark)
    pygame.draw.circle(ring, (0, 0, 0, 0), (cx, cy), inner)
    gap_w = int(inner * 2.0)
    pygame.draw.rect(ring, (0, 0, 0, 0), (cx - gap_w // 2, cy, gap_w, S - cy))
    ss.blit(ring, (0, 0))
    # Outline the outer silhouette.
    pygame.draw.circle(ss, _OUTLINE, (cx, cy), outer, _OW)
    # Re-stroke the inner cavity edge for a clean lip.
    pygame.draw.circle(ss, _OUTLINE, (cx, cy), inner, max(2, _OW - 1))
    # Leg tips (poles) — light bands at the bottom of each arm.
    leg_w = outer - inner
    tip_h = int(S * 0.11 * scale)
    leg_y = cy + int(S * 0.20 * scale)
    for sgn in (-1, 1):
        lx = cx + sgn * (inner + leg_w // 2)
        rect = (lx - leg_w // 2, leg_y, leg_w, tip_h)
        pygame.draw.rect(ss, tipcol, rect, border_radius=max(1, _SS))
        pygame.draw.rect(ss, _OUTLINE, rect, max(2, _OW - 1), border_radius=max(1, _SS))
    _key_light(ss, cx, cy, outer, 58)
    return cx, cy, outer


def build_magnet(size):
    ss = _new_raw(size)
    S = size * _SS
    _horseshoe(ss, S, PAL["magnet_body"], PAL["magnet_dark"], PAL["magnet_tip"])
    return _finish(size, ss)


def build_megamagnet(size):
    ss = _new_raw(size)
    S = size * _SS
    cx, cy = S // 2, int(S * 0.50)
    # Violet energy aura behind the horseshoe -> instant tier-up read.
    aura = pygame.Surface((S, S), pygame.SRCALPHA)
    for i, a in ((0, 55), (1, 100)):
        rr = int(S * (0.47 - i * 0.05))
        pygame.draw.circle(aura, (*PAL["mega_aura"], a), (cx, cy), rr, max(2, _OW))
    aura = pygame.transform.smoothscale(aura, (S, S))
    ss.blit(aura, (0, 0))
    # ~10% larger GOLD/ORANGE horseshoe (value step of the attraction hue).
    _horseshoe(ss, S, PAL["mega_body"], PAL["mega_dark"], PAL["mega_tip"], scale=1.10)
    # Bold star pip baked into the crown -> tier without "++".
    _star(ss, cx, int(S * 0.21), int(S * 0.10), PAL["mega_pip"])
    return _finish(size, ss)


# ---- slowmo : blue clock disc (AD benchmark / template) --------------------
def build_slowmo(size):
    ss = _new_raw(size)
    S = size * _SS
    cx, cy = S // 2, S // 2
    r = int(S * 0.34)
    _vgrad_circle(ss, cx, cy, r, _shade(PAL["time_rim"], 1.3), PAL["time_rim_d"])
    pygame.draw.circle(ss, _OUTLINE, (cx, cy), r, _OW)
    rf = int(r * 0.74)
    _vgrad_circle(ss, cx, cy, rf, PAL["time_face"],
                  _mix(PAL["time_face"], PAL["time_rim"], 0.25))
    pygame.draw.circle(ss, _OUTLINE, (cx, cy), rf, max(2, _OW - 1))
    # 10:10 hands read instantly as a clock.
    pygame.draw.line(ss, PAL["time_hand"], (cx, cy), (cx, cy - int(rf * 0.62)), _OW)
    pygame.draw.line(ss, PAL["time_hand"], (cx, cy),
                     (cx + int(rf * 0.5), cy + int(rf * 0.15)), _OW)
    pygame.draw.circle(ss, PAL["time_hand"], (cx, cy), max(2, _OW), 0)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        pygame.draw.line(
            ss, PAL["time_rim_d"],
            (cx + math.cos(a) * rf * 0.86, cy + math.sin(a) * rf * 0.86),
            (cx + math.cos(a) * rf * 0.98, cy + math.sin(a) * rf * 0.98),
            max(2, _OW - 1),
        )
    _key_light(ss, cx, cy, r, 64)
    return _finish(size, ss)


# ---- reverse : teal interlocking arrows, NON-circular silhouette -----------
def build_reverse(size):
    ss = _new_raw(size)
    S = size * _SS
    cx, cy = S // 2, int(S * 0.50)
    r = int(S * 0.30)
    thick = int(S * 0.13)
    # Two C-arcs chasing each other, vertically offset so the silhouette is
    # wide+oval (NOT a disc) — the key separation from slowmo.
    specs = [(+1, -int(S * 0.06), math.radians(15), math.radians(195)),
             (-1, int(S * 0.06), math.radians(195), math.radians(375))]
    for sgn, oy, start, end in specs:
        col = PAL["rev_body"] if sgn > 0 else _shade(PAL["rev_body"], 0.82)
        arc_rect = (cx - r, cy - r + oy, r * 2, r * 2)
        pygame.draw.arc(ss, col, arc_rect, start, end, thick)
    # Opposed arrow heads (left on top arc, right on bottom arc) widen it more.
    head = int(S * 0.12)
    lx, ly = cx - r + int(S * 0.02), cy - int(S * 0.06)
    pygame.draw.polygon(ss, PAL["rev_body"],
                        [(lx - head, ly), (lx + head, ly - head), (lx + head, ly + head)])
    rx, ry = cx + r - int(S * 0.02), cy + int(S * 0.06)
    pygame.draw.polygon(ss, _shade(PAL["rev_body"], 0.82),
                        [(rx + head, ry), (rx - head, ry - head), (rx - head, ry + head)])
    # Outline pass over the arcs for cohesion with the rest of the set.
    for sgn, oy, start, end in specs:
        arc_rect = (cx - r, cy - r + oy, r * 2, r * 2)
        pygame.draw.arc(ss, _OUTLINE, arc_rect, start, end, max(2, _OW - 1))
    pygame.draw.circle(ss, PAL["rev_lite"],
                       (cx - int(r * 0.3), cy - int(r * 0.5)), max(2, _OW))
    return _finish(size, ss)


# ---- triple : stacked coin edges + x3 multiplier ---------------------------
def build_triple(size):
    ss = _new_raw(size)
    S = size * _SS
    cx = S // 2
    r = int(S * 0.27)
    offs = [(-int(S * 0.10), int(S * 0.16)),
            (int(S * 0.10), int(S * 0.06)),
            (0, -int(S * 0.06))]
    for i, (dx, dy) in enumerate(offs):
        ccx, ccy = cx + dx, S // 2 + dy
        _vgrad_circle(ss, ccx, ccy, r, PAL["coin_lite"], PAL["coin_dark"])
        pygame.draw.circle(ss, _OUTLINE, (ccx, ccy), r, _OW)
        if i == len(offs) - 1:
            _key_light(ss, ccx, ccy, r, 70)
            _draw_x3(ss, ccx, ccy, r)
    return _finish(size, ss)


def _draw_x3(ss, cx, cy, r):
    g = PAL["coin_glyph"]
    w = max(2, _OW - 1)
    xx = cx - int(r * 0.34)
    s = int(r * 0.42)
    pygame.draw.line(ss, g, (xx - s, cy - s), (xx + s, cy + s), w)
    pygame.draw.line(ss, g, (xx - s, cy + s), (xx + s, cy - s), w)
    rx = cx + int(r * 0.30)
    pygame.draw.arc(ss, g, (rx - s, cy - s, s * 2, s),
                    math.radians(-150), math.radians(110), w)
    pygame.draw.arc(ss, g, (rx - s, cy, s * 2, s),
                    math.radians(-110), math.radians(150), w)


# ---- kfc : flared striped bucket + drumstick over the rim -------------------
def build_kfc(size):
    ss = _new_raw(size)
    S = size * _SS
    cx = S // 2
    top_y = int(S * 0.42)
    bot_y = int(S * 0.82)
    half_top = int(S * 0.31)   # FLARED wide at the top (chicken bucket)
    half_bot = int(S * 0.19)
    body = [(cx - half_top, top_y), (cx + half_top, top_y),
            (cx + half_bot, bot_y), (cx - half_bot, bot_y)]
    pygame.draw.polygon(ss, PAL["kfc_white"], body)
    # Three bold red stripes following the taper.
    for i in range(3):
        t = (i + 0.5) / 3
        xt = _lerp(cx - half_top, cx + half_top, t)
        xb = _lerp(cx - half_bot, cx + half_bot, t)
        pygame.draw.line(ss, PAL["kfc_red"], (xt, top_y), (xb, bot_y), int(S * 0.055))
    pygame.draw.polygon(ss, _OUTLINE, body, _OW)
    # Wide rim ellipse emphasises the flare.
    rrect = (cx - half_top, top_y - int(S * 0.06), half_top * 2, int(S * 0.12))
    pygame.draw.ellipse(ss, PAL["kfc_red"], rrect)
    pygame.draw.ellipse(ss, _OUTLINE, rrect, _OW)
    # ONE drumstick breaking the top silhouette: warm lobe + pale bone nub.
    dx = cx + int(S * 0.05)
    dy = top_y - int(S * 0.13)
    lobe_r = int(S * 0.13)
    _vgrad_circle(ss, dx, dy, lobe_r, _shade(PAL["drum_brown"], 1.25), PAL["drum_brown_d"])
    pygame.draw.circle(ss, _OUTLINE, (dx, dy), lobe_r, _OW)
    bx, by = dx + int(S * 0.05), dy - int(S * 0.11)
    pygame.draw.line(ss, PAL["bone"], (dx, dy - int(lobe_r * 0.4)), (bx, by), int(S * 0.05))
    pygame.draw.circle(ss, PAL["bone"], (bx, by), max(2, int(S * 0.04)))
    pygame.draw.circle(ss, _OUTLINE, (bx, by), max(2, int(S * 0.04)), max(2, _OW - 2))
    _key_light(ss, dx, dy, lobe_r, 55)
    return _finish(size, ss)


# ---- ghost : cool white, dimmed ~15%, faint cyan edge ----------------------
def build_ghost(size):
    ss = _new_raw(size)
    S = size * _SS
    cx = S // 2
    r = int(S * 0.27)
    top_y = int(S * 0.36)
    hem_y = int(S * 0.72)
    # Faint cool-cyan edge halo behind the body (it blooms brightest, so this
    # cools it instead of letting it go pure-white hot).
    halo = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*PAL["ghost_edge"], 80), (cx, (top_y + hem_y) // 2),
                       int(r * 1.2))
    halo = pygame.transform.smoothscale(halo, (S, S))
    ss.blit(halo, (0, 0))
    body = _shade(PAL["ghost_body"], 0.85)   # dimmed ~15%
    body_d = _shade(PAL["ghost_body_d"], 0.85)
    # Dome.
    _vgrad_circle(ss, cx, top_y, r, body, body_d)
    # Trunk under the dome.
    trunk = pygame.Surface((S, S), pygame.SRCALPHA)
    for y in range(top_y, hem_y):
        t = (y - top_y) / max(1, (hem_y - top_y))
        pygame.draw.line(trunk, _mix(body, body_d, t), (cx - r, y), (cx + r, y))
    ss.blit(trunk, (0, 0))
    # Wavy hem (3 lobes).
    lobes = 3
    for i in range(lobes):
        bx = _lerp(cx - r, cx + r, i / lobes)
        bx2 = _lerp(cx - r, cx + r, (i + 1) / lobes)
        col = body if i % 2 == 0 else body_d
        pygame.draw.ellipse(ss, col, (bx, hem_y - int(S * 0.05),
                                      bx2 - bx, int(S * 0.11)))
    # Silhouette outline: dome + sides + hem scallops.
    pygame.draw.circle(ss, _OUTLINE, (cx, top_y), r, _OW)
    pygame.draw.line(ss, _OUTLINE, (cx - r, top_y), (cx - r, hem_y), _OW)
    pygame.draw.line(ss, _OUTLINE, (cx + r, top_y), (cx + r, hem_y), _OW)
    for i in range(lobes):
        bx = _lerp(cx - r, cx + r, i / lobes)
        bx2 = _lerp(cx - r, cx + r, (i + 1) / lobes)
        pygame.draw.arc(ss, _OUTLINE, (bx, hem_y - int(S * 0.05),
                                       bx2 - bx, int(S * 0.12)),
                        math.radians(180), math.radians(360), _OW)
    # Eyes.
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.4)
        pygame.draw.ellipse(ss, PAL["ghost_eye"],
                            (ex - int(S * 0.04), top_y - int(S * 0.02),
                             int(S * 0.08), int(S * 0.11)))
    _key_light(ss, cx, top_y, r, 40)
    return _finish(size, ss)


# ---- size family : shrink (in) & grow (out) — explicit opposed pair --------
def _figure(ss, cx, cy, r, col, dark):
    # One shared base glyph: a rounded creature blob with eye dots so it never
    # reads as a coin. shrink/grow differ only in figure size + arrow dir.
    _vgrad_circle(ss, cx, cy, r, _shade(col, 1.25), dark)
    pygame.draw.circle(ss, _OUTLINE, (cx, cy), r, _OW)
    for sgn in (-1, 1):
        pygame.draw.circle(ss, _OUTLINE,
                           (cx + sgn * int(r * 0.35), cy - int(r * 0.1)),
                           max(2, int(r * 0.16)))


def build_shrink(size):
    ss = _new_raw(size)
    S = size * _SS
    cx, cy = S // 2, S // 2
    r = int(S * 0.155)            # SMALL figure
    _figure(ss, cx, cy, r, PAL["size_fig_d"], _shade(PAL["size_fig_d"], 0.7))
    d = int(S * 0.40)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        x1 = cx + math.cos(a) * d
        y1 = cy + math.sin(a) * d
        x2 = cx + math.cos(a) * (r + int(S * 0.07))
        y2 = cy + math.sin(a) * (r + int(S * 0.07))
        _arrow(ss, x1, y1, x2, y2, PAL["size_hue"])   # INWARD
    return _finish(size, ss)


def build_grow(size):
    ss = _new_raw(size)
    S = size * _SS
    cx, cy = S // 2, S // 2
    r = int(S * 0.26)             # LARGE figure
    _figure(ss, cx, cy, r, PAL["size_fig"], PAL["size_fig_d"])
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        x1 = cx + math.cos(a) * (r + int(S * 0.03))
        y1 = cy + math.sin(a) * (r + int(S * 0.03))
        x2 = cx + math.cos(a) * (r + int(S * 0.16))
        y2 = cy + math.sin(a) * (r + int(S * 0.16))
        _arrow(ss, x1, y1, x2, y2, PAL["size_hue_l"])  # OUTWARD
    return _finish(size, ss)


# ---- rail : one bright steel cart + amber track (no ore lump) ---------------
def build_rail(size):
    ss = _new_raw(size)
    S = size * _SS
    cx = S // 2
    body_top = int(S * 0.38)
    body_bot = int(S * 0.66)
    half_t = int(S * 0.30)
    half_b = int(S * 0.22)
    cart = [(cx - half_t, body_top), (cx + half_t, body_top),
            (cx + half_b, body_bot), (cx - half_b, body_bot)]
    _vgrad_mask(ss, cart, body_top, body_bot,
                _shade(PAL["rail_body"], 1.22), PAL["rail_body_d"])
    pygame.draw.polygon(ss, _OUTLINE, cart, _OW)
    # Forward chevrons on the cart imply speed (the single "idea").
    for k in range(2):
        ox = cx - int(S * 0.04) + k * int(S * 0.11)
        pygame.draw.lines(
            ss, PAL["rail_amber"], False,
            [(ox - int(S * 0.05), body_top + int(S * 0.05)),
             (ox, body_top + int(S * 0.14)),
             (ox - int(S * 0.05), body_top + int(S * 0.23))],
            max(2, _OW),
        )
    # Two wheels.
    wy = body_bot + int(S * 0.05)
    wr = int(S * 0.07)
    for sgn in (-1, 1):
        wx = cx + sgn * int(S * 0.14)
        pygame.draw.circle(ss, PAL["rail_body_d"], (wx, wy), wr)
        pygame.draw.circle(ss, _OUTLINE, (wx, wy), wr, max(2, _OW - 1))
        pygame.draw.circle(ss, _shade(PAL["rail_body"], 1.3), (wx, wy), max(2, wr // 3))
    # Bright amber rail line (brightens the whole emblem on dark sky).
    ry = wy + int(S * 0.11)
    pygame.draw.line(ss, PAL["rail_amber"], (int(S * 0.10), ry),
                     (int(S * 0.90), ry), int(S * 0.055))
    pygame.draw.line(ss, PAL["rail_amber_d"], (int(S * 0.10), ry + int(S * 0.045)),
                     (int(S * 0.90), ry + int(S * 0.045)), max(2, _OW - 1))
    _key_light(ss, cx, (body_top + body_bot) // 2, half_t, 50)
    return _finish(size, ss)


# ---------------------------------------------------------------------------
# Plate + sky backgrounds
# ---------------------------------------------------------------------------
def na_plate(size, bg=(46, 50, 64)):
    p = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = (1, 1, size - 2, size - 2)
    pygame.draw.rect(p, (*bg, 235), rect, border_radius=max(2, size // 5))
    pygame.draw.rect(p, (18, 20, 28, 255), rect, 2, border_radius=max(2, size // 5))
    pygame.draw.rect(p, (255, 255, 255, 26), (3, 3, size - 6, max(2, size // 3)),
                     border_radius=max(2, size // 6))
    return p


def day_sky(w, h):
    s = pygame.Surface((w, h))
    top, bot = (118, 196, 246), (206, 240, 252)
    for y in range(h):
        pygame.draw.line(s, _mix(top, bot, y / max(1, h - 1)), (0, y), (w, y))
    return s


def night_sky(w, h):
    import random
    s = pygame.Surface((w, h))
    top, bot = (18, 22, 46), (52, 40, 78)
    for y in range(h):
        pygame.draw.line(s, _mix(top, bot, y / max(1, h - 1)), (0, y), (w, y))
    rnd = random.Random(7)
    for _ in range(70):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, h - 1)
        b = rnd.randint(120, 230)
        s.set_at((x, y), (b, b, min(255, b + 20)))
    return s


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
BUILDERS = [
    ("magnet", build_magnet),
    ("megamagnet", build_megamagnet),
    ("slowmo", build_slowmo),
    ("reverse", build_reverse),
    ("triple", build_triple),
    ("kfc", build_kfc),
    ("ghost", build_ghost),
    ("shrink", build_shrink),
    ("grow", build_grow),
    ("rail", build_rail),
]


def _font(sz, bold=True):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _current_plate(kind, hud):
    """The real production emblem on the real slate plate, for before/after."""
    full = pygame.Surface((hud + _NA_PAD * 2, hud + _NA_PAD * 2), pygame.SRCALPHA)
    rect = pygame.Rect(_NA_PAD, _NA_PAD, hud, hud)
    _na_plate(full, rect, cut=7, round_r=7, accent=_ENERGY_FULL, glow=False)
    _draw_buff_icon(full, rect.inflate(-8, -8), kind)
    return full


def main():
    HUD = 32
    ZOOM = HUD * 6
    sheet_w = 1180
    f_title = _font(26)
    f_lbl = _font(18)
    f_small = _font(15, bold=False)

    # Pre-measure layout heights.
    header_strip_h = 40 + (HUD + _NA_PAD * 2 if _HAVE_PROD else HUD) + 26
    row_h = ZOOM + 24
    inspect_h = 40 + 2 * (HUD + 26) + 16
    sheet_h = 56 + header_strip_h + 24 + len(BUILDERS) * row_h + 40 + inspect_h + 30

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 32, 40))

    y = 16
    sheet.blit(f_title.render("Skybit buff emblems — round 2", True, (240, 240, 248)), (24, y))
    y += 40

    # ---- CURRENT (production) strip -----------------------------------------
    sheet.blit(f_lbl.render("CURRENT (production)", True, (230, 130, 120)), (24, y))
    y += 26
    gx = 24
    if _HAVE_PROD:
        for name, _ in BUILDERS:
            sheet.blit(_current_plate(name, HUD), (gx, y))
            sheet.blit(f_small.render(name, True, (160, 165, 175)),
                       (gx, y + HUD + _NA_PAD * 2 + 2))
            gx += HUD + _NA_PAD * 2 + 22
        y += HUD + _NA_PAD * 2 + 22
    else:
        sheet.blit(f_small.render("(repo not importable — CURRENT strip skipped)",
                                  True, (160, 165, 175)), (24, y))
        y += HUD + 22

    pygame.draw.line(sheet, (60, 64, 70), (24, y), (sheet_w - 24, y), 2)
    y += 16
    sheet.blit(f_lbl.render("NEW round 2 — 32px on plate (light + dark) + 6x zoom",
                            True, (150, 220, 160)), (24, y))
    y += 28

    # ---- per-emblem rows ----------------------------------------------------
    for name, builder in BUILDERS:
        emb = builder(HUD)
        sheet.blit(f_lbl.render(name, True, (236, 236, 244)),
                   (24, y + row_h // 2 - 10))
        plate_x = 190
        py = y + (row_h - HUD) // 2
        # light plate
        sheet.blit(na_plate(HUD), (plate_x, py))
        sheet.blit(emb, (plate_x, py))
        # dark plate
        sheet.blit(na_plate(HUD, bg=(24, 22, 40)), (plate_x + HUD + 14, py))
        sheet.blit(emb, (plate_x + HUD + 14, py))
        # zoom
        zx = plate_x + HUD * 2 + 70
        zy = y + (row_h - ZOOM) // 2
        pygame.draw.rect(sheet, (44, 46, 56), (zx - 6, zy - 6, ZOOM + 12, ZOOM + 12),
                         border_radius=10)
        sheet.blit(pygame.transform.scale(emb, (ZOOM, ZOOM)), (zx, zy))
        y += row_h

    # ---- inspection block : all ten at TRUE 32px over day + night ----------
    y += 16
    sheet.blit(f_lbl.render("Inspection — all ten at true 32px on busy sky",
                            True, (240, 240, 248)), (24, y))
    y += 28

    block_w = len(BUILDERS) * (HUD + 14) + 24
    bx0 = 24
    # row (a) day
    sheet.blit(day_sky(block_w, HUD + 16), (bx0, y))
    cx = bx0 + 12
    for name, builder in BUILDERS:
        sheet.blit(builder(HUD), (cx, y + 8))
        cx += HUD + 14
    sheet.blit(f_small.render("(a) day sky", True, (30, 50, 80)),
               (bx0 + block_w + 14, y + 8))
    y += HUD + 26
    # row (b) night
    sheet.blit(night_sky(block_w, HUD + 16), (bx0, y))
    cx = bx0 + 12
    for name, builder in BUILDERS:
        sheet.blit(builder(HUD), (cx, y + 8))
        cx += HUD + 14
    sheet.blit(f_small.render("(b) night sky", True, (200, 210, 230)),
               (bx0 + block_w + 14, y + 8))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
