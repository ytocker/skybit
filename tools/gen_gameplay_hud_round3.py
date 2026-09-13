"""Round-3 FINAL refinement of the in-gameplay HUD (STATE_PLAY), direction C.

Locks round-2's V3 ("Adventure Plaques" — carved wood + parchment with gold
rope-band/rivet edges, flat / no shadows) and resolves the last two notes:

  1. CLEAR THE CENTRAL PLAY CORRIDOR. The pillar descends through the top
     centre, so the score plaque and timer can't live in that lane.
       - SCORE plaque stays top-CENTRE (conventional for a flyer) but is pushed
         fully UP into the title band so its lowest pixel sits within the top
         ~56px — above where the player reads the incoming gap.
       - TIMER bar no longer spans the centre: shortened to ~120px and
         LEFT-anchored under the top-left coin plaque (left third), so it never
         crosses the corridor.
  2. SEPARATE THE TIMER FROM THE GOLD COIN ECONOMY. The fill sits in a recessed
     NAVY track (#1a2740) so in peripheral vision the bar can't be mistaken for
     an in-play gold coin or a lit pillar edge; the gold/amber fill keeps its
     dark outline. (Proven against a 1x in-play coin in the inset.)
  3. SCORE LEGIBILITY OVER A BROWN PILLAR. The carved-wood field is darkened
     ~10% and the numerals brightened to near-white cream so "12" holds on the
     worst-case pillar backdrop, not just bright sky.
  4. LOCKED V3 DIMS: pause PILL 84x54 top-RIGHT inset 10px (wood + gold rope rim
     + carved double-bar glyph); coin plaque top-LEFT; score plaque at V3 size;
     all flat (no shadows).

Composited at 4x supersample then smoothscaled (the project's crisp-edge trick,
as in powerup_help._dark_panel). The HUD is drawn over a REAL seeded gameplay
backdrop with the live HUD suppressed, so the plaques are judged over both
bright sky and dark pillars.

Standalone review tooling — does NOT touch game/. Run from repo root:
    python tools/gen_gameplay_hud_round3.py
Output: docs/gameplay_hud/round_3.png
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import random

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game.config import W, H, MAGNET_DURATION
from game.scenes import App, STATE_PLAY
from game.world import World
from game.hud import (
    _font, _coin_icon,
    _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE,
)
from game.draw import (
    lerp_color, UI_CREAM, UI_GOLD, UI_ORANGE, UI_RED,
)
from game.powerup_help import _powerup_icon

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "round_3.png")

# Representative live values the brief asked for.
SCORE = "12"
COINS = 7
PU_KIND = "magnet"
PU_REMAIN = 5.5
PU_TOTAL = MAGNET_DURATION  # 8.0

SS = 4  # supersample factor — composite big, smoothscale to native.

# Adventure-plaque tones: warm carved wood, parchment cream, gold rope.
# The score field is darkened ~10% from round 2 so cream numerals hold their
# contrast even when a brown pillar (not bright sky) is the backdrop.
_WOOD_LT = (96, 62, 34)
_WOOD_MD = (70, 44, 24)
_WOOD_DK = (44, 27, 14)
_WOOD_SCORE_LT = (86, 55, 29)   # ~10% darker than _WOOD_LT
_WOOD_SCORE_DK = (33, 20, 10)   # ~10% darker than _WOOD_DK
_PARCH_LT = (236, 214, 164)
_PARCH_DK = (198, 168, 112)
# Brighter-than-pale cream for the score value: near-white so the number does
# not lean only on the gold rim over the worst-case pillar.
_SCORE_CREAM = (255, 246, 214)

# Recessed navy timer track — deliberately OUTSIDE the gold coin economy so the
# bar can never read as an in-play coin or a lit pillar edge in periphery.
_NAVY_TRACK_TOP = (30, 44, 72)   # ~#1e2c48
_NAVY_TRACK_BOT = (16, 24, 44)   # ~#10182c (anchored near the briefed #1a2740)


# ── Backdrop: a real seeded gameplay frame with the HUD suppressed ──────────
def build_backdrop():
    """Run a short seeded sim that threads pillars, then render the live App in
    STATE_PLAY with draw_play monkeypatched out, so the plaques sit over a clean
    playfield (sky + pillars + coins + bird). Returns a 360x640 surf."""
    best = None
    for seed in range(60):
        random.seed(seed)
        app = App()
        if hasattr(app, "_splash_covering"):
            app._splash_covering = False
        w = World()
        w.ready_t = 0.0
        w.flap()
        app.world = w
        app.state = STATE_PLAY
        dt = 1 / 60
        for _ in range(int(7.0 / dt)):
            target = H * 0.45
            ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
            if ahead:
                target = min(ahead, key=lambda p: p.x).gap_y - 12
            if w.bird.y > target:
                w.flap()
            w.update(dt)
            if w.game_over:
                break
        on_screen_coin = any(0 < c.x < W for c in w.coins)
        if (not w.game_over and w.score >= 3 and on_screen_coin
                and 140 < w.bird.y < 470):
            best = (app, w)
            break
        if best is None and not w.game_over and w.score >= 2:
            best = (app, w)
    app, w = best
    app.hud.draw_play = lambda *a, **k: None
    app._render()
    return app.screen.copy()


# ── shared supersampled-surface helpers ─────────────────────────────────────
def _ss_surf(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _blit_ss(dst, ss, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(ss, (w, h)), (x, y))


def _vgrad_rounded(surf, rect, top, bot, radius, alpha=255):
    """Vertical gradient clipped to a rounded rect, drawn onto a SUPERSAMPLED
    `surf` whose pixel size is ``SS`` x the given native ``rect``."""
    ow, oh = rect.width * SS, rect.height * SS
    orad = radius * SS
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(top, bot, t)
        pygame.draw.line(body, (*c, alpha), (0, yy), (ow - 1, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (rect.x * SS, rect.y * SS))


def _timer_colors(frac):
    """Gold -> orange -> red fill pair as the buff depletes (mirrors hud)."""
    if frac > 0.5:
        return UI_GOLD, UI_ORANGE
    if frac > 0.25:
        t = (frac - 0.25) / 0.25
        return lerp_color(UI_ORANGE, UI_GOLD, t), lerp_color(UI_RED, UI_ORANGE, t)
    return UI_RED, (180, 20, 20)


def _outlined(surf, txt, center, size, fill, outline, px):
    """8-direction outline, no drop shadow (flat silhouette per the brief)."""
    f = _font(size, True)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    for ox, oy in ((-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)):
        surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)
    return r


def _rope_band(ss, ow, oh, orad, width_n):
    """Twisted gold rope rim: an outer deep-gold band carrying a chain of
    bright diagonal twist-strands that read as braided rope even after the
    surface is scaled back to native. A thin pale inner thread closes the
    bevel. Drawn on the supersampled surf."""
    pygame.draw.rect(ss, _GOLD_DEEP, (0, 0, ow, oh), width=width_n,
                     border_radius=orad)
    strand_w = max(SS, width_n // 3)
    pitch = max(4 * SS, width_n)
    inset = width_n // 2
    for x in range(orad, ow - orad, pitch):
        pygame.draw.line(ss, (*_GOLD_PALE, 230),
                         (x, inset), (x + width_n, width_n - inset // 2), strand_w)
        pygame.draw.line(ss, (*_GOLD_PALE, 230),
                         (x, oh - inset), (x + width_n, oh - width_n + inset // 2),
                         strand_w)
    for y in range(orad, oh - orad, pitch):
        pygame.draw.line(ss, (*_GOLD_PALE, 230),
                         (inset, y), (width_n - inset // 2, y + width_n), strand_w)
        pygame.draw.line(ss, (*_GOLD_PALE, 230),
                         (ow - inset, y), (ow - width_n + inset // 2, y + width_n),
                         strand_w)
    pygame.draw.rect(ss, (*_GOLD_BRIGHT, 220),
                     (width_n, width_n, ow - 2 * width_n, oh - 2 * width_n),
                     width=SS, border_radius=max(1, orad - width_n))


def _rivets(ss, ow, oh, m):
    for px, py in ((m, m), (ow - m, m), (m, oh - m), (ow - m, oh - m)):
        pygame.draw.circle(ss, _GOLD_DEEP, (px, py), 3 * SS)
        pygame.draw.circle(ss, _GOLD_BRIGHT, (px, py), 3 * SS, SS)
        pygame.draw.circle(ss, _GOLD_PALE, (px - SS, py - SS), SS)


def _wood_plaque(surf, rect, radius, parchment=False, band=4, rivets=True,
                 wood_top=None, wood_bot=None):
    """Carved-wood (or parchment) plaque with a gold rope-band rim and rivets.
    NO drop shadow — relief comes only from the body gradient, an inner carved
    groove, and the inner-light highlight on the rope. Flat silhouette.
    ``wood_top``/``wood_bot`` override the wood tones (the score plaque runs a
    ~10% darker field so cream numerals hold over a brown pillar)."""
    ss = _ss_surf(rect.width, rect.height)
    ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
    if parchment:
        top, bot = _PARCH_LT, _PARCH_DK
    else:
        top = wood_top or _WOOD_LT
        bot = wood_bot or _WOOD_DK
    _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height), top, bot,
                   radius, alpha=252)
    # top inner-light sheen reads as a rounded, lit upper edge (no offset cast)
    sheen = pygame.Surface((ow, oh), pygame.SRCALPHA)
    sh_h = int(oh * 0.4)
    lit = (255, 246, 220) if parchment else (150, 108, 66)
    for yy in range(sh_h):
        a = int(70 * (1 - yy / sh_h))
        pygame.draw.line(sheen, (*lit, a), (orad, yy + band * SS),
                         (ow - orad, yy + band * SS))
    smask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(sheen, (0, 0))
    # wood grain / parchment mottling
    rng = random.Random(rect.x * 13 + rect.y)
    for _ in range(int(rect.width * 0.5)):
        yy = rng.randint(2 * SS, oh - 2 * SS)
        a = rng.randint(14, 34)
        col = (150, 120, 70) if parchment else (30, 18, 8)
        pygame.draw.line(ss, (*col, a), (orad, yy), (ow - orad, yy))
    # carved inner groove (recessed engraving field)
    pygame.draw.rect(ss, (0, 0, 0, 110),
                     (band * SS, band * SS, ow - 2 * band * SS, oh - 2 * band * SS),
                     width=2 * SS, border_radius=max(1, orad - band * SS))
    # gold rope-band rim
    _rope_band(ss, ow, oh, orad, band * SS)
    if rivets:
        _rivets(ss, ow, oh, 8 * SS)
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def _pause_pill(surf, rect, radius):
    """Wood pause pill (wider than tall) with a gold rope-band rim and a pair of
    parchment-pale pause bars. NO drop shadow. Locked at 84x54."""
    ss = _ss_surf(rect.width, rect.height)
    ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
    _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height),
                   _WOOD_LT, _WOOD_DK, radius, alpha=252)
    # top inner-light sheen
    sheen = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(int(oh * 0.45)):
        a = int(70 * (1 - yy / (oh * 0.45)))
        pygame.draw.line(sheen, (150, 108, 66, a), (orad, yy + 3 * SS),
                         (ow - orad, yy + 3 * SS))
    smask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(sheen, (0, 0))
    # carved groove + rope-band rim
    pygame.draw.rect(ss, (0, 0, 0, 110),
                     (4 * SS, 4 * SS, ow - 8 * SS, oh - 8 * SS),
                     width=2 * SS, border_radius=max(1, orad - 4 * SS))
    _rope_band(ss, ow, oh, orad, 4 * SS)
    # carved double-bar pause glyph, scaled to the pill height
    bw = max(4, rect.height // 5) * SS
    bh = int(rect.height * 0.46) * SS
    gap = max(4, rect.height // 8) * SS
    midx, midy = ow // 2, oh // 2
    for bx in (midx - gap - bw, midx + gap):
        pygame.draw.rect(ss, _GOLD_PALE, (bx, midy - bh // 2, bw, bh),
                         border_radius=2 * SS)
        pygame.draw.rect(ss, _GOLD_DEEP, (bx, midy - bh // 2, bw, bh),
                         width=SS, border_radius=2 * SS)
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def _coins_plaque(surf, top_y=10, h=34, font_px=19):
    """Parchment + gold rope coin counter, top-LEFT (V3). Returns its rect so
    the timer row can left-anchor under it in the same column."""
    ct = f"x{COINS}"
    cw = _font(font_px, True).size(ct)[0] + 48
    cp = pygame.Rect(10, top_y, cw, h)
    _wood_plaque(surf, cp, 9, parchment=True, band=3, rivets=False)
    _coin_icon(surf, cp.x + 20, cp.centery, 10)
    ci = _font(font_px, True).render(ct, True, _WOOD_DK)
    surf.blit(ci, ci.get_rect(midleft=(cp.x + 34, cp.centery)))
    return cp


def _score_plaque(surf):
    """Top-CENTRE score, pushed fully into the top ~56px band, with a darkened
    carved-wood field + near-white cream numerals for pillar legibility."""
    sf = _font(38, True)
    sw = max(sf.size(SCORE)[0] + 52, 92)
    # y=6, h=46 -> bottom edge at 52, inside the top ~56px so it clears the
    # incoming-gap reading zone in the central corridor.
    sp = pygame.Rect((W - sw) // 2, 6, sw, 46)
    _wood_plaque(surf, sp, 11, wood_top=_WOOD_SCORE_LT, wood_bot=_WOOD_SCORE_DK)
    _outlined(surf, SCORE, sp.center, 36, _SCORE_CREAM, _WOOD_DK, 2)
    return sp


def _timer_row(surf, left_x, top_y, bar_w=120, bar_h=16, icon=28):
    """Wood icon medallion + recessed NAVY track with a gold->red fill, LEFT-
    anchored so it stays in the left third and never crosses the corridor.
    Returns the track rect (for the worst-case zoom crop)."""
    frac = PU_REMAIN / PU_TOTAL
    # wood icon medallion (small, round — matches the carved family)
    ic = pygame.Rect(left_x, top_y - (icon - bar_h) // 2, icon, icon)
    n2 = icon * SS
    chip = _ss_surf(icon, icon)
    for r in range(n2 // 2, 0, -1):
        t = 1 - r / (n2 / 2)
        pygame.draw.circle(chip, lerp_color(_WOOD_LT, _WOOD_DK, t),
                           (n2 // 2, n2 // 2), r)
    pygame.draw.circle(chip, _GOLD_DEEP, (n2 // 2, n2 // 2), n2 // 2, 2 * SS)
    pygame.draw.circle(chip, _GOLD_BRIGHT, (n2 // 2, n2 // 2), n2 // 2 - SS, SS)
    _blit_ss(surf, chip, ic.x, ic.y, icon, icon)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 8)
    # recessed NAVY track with a thin gold rope rim — navy keeps the bar OUT of
    # the gold coin economy so it can't be mistaken for a coin in periphery.
    bx = ic.right + 6
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    _vgrad_rounded(track, pygame.Rect(0, 0, bar_w, bar_h),
                   _NAVY_TRACK_TOP, _NAVY_TRACK_BOT, bar_h // 2, alpha=250)
    pygame.draw.rect(track, _GOLD_DEEP, (0, 0, bar_w * SS, bar_h * SS),
                     width=2 * SS, border_radius=bar_h * SS // 2)
    pygame.draw.rect(track, (*_GOLD_BRIGHT, 150),
                     (SS, SS, bar_w * SS - 2 * SS, bar_h * SS - 2 * SS),
                     width=SS, border_radius=bar_h * SS // 2)
    _blit_ss(surf, track, tr.x, tr.y, bar_w, bar_h)
    fhi, flo = _timer_colors(frac)
    fillw = int((bar_w - 6) * frac)
    if fillw > 4:
        # gold/amber fill keeps a dark outline so it reads as a buff meter, not
        # a flat coin-coloured slab, against the navy track.
        fill = _ss_surf(fillw, bar_h - 6)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h - 6), fhi, flo,
                       (bar_h - 6) // 2)
        pygame.draw.rect(fill, (*_WOOD_DK, 235),
                         (0, 0, fillw * SS, (bar_h - 6) * SS),
                         width=SS, border_radius=(bar_h - 6) * SS // 2)
        _blit_ss(surf, fill, bx + 3, tr.y + 3, fillw, bar_h - 6)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (bx + bar_w // 2, tr.centery), 11,
              _PARCH_LT, _WOOD_DK, 1)
    return tr


# ── 1x in-play coin (for the do-they-blend inset) ────────────────────────────
def _draw_inplay_coin(surf, cx, cy):
    """Blit the REAL cached in-world coin face at its native 1x size so the
    inset proves the navy-tracked timer doesn't read like an on-screen coin."""
    from game.entities import _get_coin_face
    from game.config import COIN_R
    face = _get_coin_face()
    d = COIN_R * 2 + 4
    img = pygame.transform.smoothscale(face, (d, d))
    surf.blit(img, img.get_rect(center=(cx, cy)))
    return d


def draw_hud(frame):
    """Compose the final refined direction-C HUD over a gameplay frame and
    return the key rects (coin, score, timer) for the zoom crops."""
    coin_rect = _coins_plaque(frame, top_y=10, h=34, font_px=19)
    score_rect = _score_plaque(frame)
    # PAUSE pill 84x54, top-RIGHT inset 10px (locked V3 dims).
    pw, ph = 84, 54
    _pause_pill(frame, pygame.Rect(W - pw - 10, 10, pw, ph), ph // 2)
    # TIMER left-anchored under the coin plaque, in the left third (icon starts
    # at the coin plaque's left edge); ~120px bar so it never crosses centre.
    timer_rect = _timer_row(frame, left_x=coin_rect.x, top_y=58,
                            bar_w=120, bar_h=16, icon=28)
    return coin_rect, score_rect, timer_rect


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    backdrop = build_backdrop()

    # ── main panel: full 360x640 screen with the final HUD ──────────────────
    frame = backdrop.copy()
    coin_rect, score_rect, timer_rect = draw_hud(frame)

    # ── worst-case crop: score + timer with a BROWN PILLAR behind them ──────
    # Build a flat brown-pillar field that matches the in-game pillar tone, lay
    # the same score plaque + timer over it, and zoom it so the legibility check
    # is read at the worst backdrop, not just bright sky.
    PILLAR_BROWN_TOP = (150, 108, 64)
    PILLAR_BROWN_BOT = (120, 84, 48)
    crop_src = pygame.Surface((W, 110), pygame.SRCALPHA)
    for yy in range(110):
        t = yy / 109
        pygame.draw.line(crop_src, lerp_color(PILLAR_BROWN_TOP, PILLAR_BROWN_BOT, t),
                         (0, yy), (W, yy))
    # darker pillar seams so the field looks like a real sandstone pillar body
    for sx in range(40, W, 60):
        pygame.draw.line(crop_src, (96, 66, 36), (sx, 0), (sx, 110), 2)
    _score_plaque(crop_src)
    _timer_row(crop_src, left_x=10, top_y=58, bar_w=120, bar_h=16, icon=28)
    crop = crop_src.subsurface(pygame.Rect(8, 0, W - 16, 86)).copy()
    ZC = 2
    crop_zoom = pygame.transform.smoothscale(
        crop, (crop.get_width() * ZC, crop.get_height() * ZC))

    # ── blend-test inset: 1x timer next to a 1x in-play coin ────────────────
    inset = pygame.Surface((250, 64), pygame.SRCALPHA)
    inset.fill((20, 15, 34, 255))
    pygame.draw.rect(inset, (60, 48, 90), inset.get_rect(), 1)
    _timer_row(inset, left_x=8, top_y=24, bar_w=120, bar_h=16, icon=28)
    coin_d = _draw_inplay_coin(inset, 200, 32)
    iz = 2
    inset_zoom = pygame.transform.smoothscale(
        inset, (inset.get_width() * iz, inset.get_height() * iz))

    # ── sheet layout: screen on the left, the two proof crops stacked right ──
    pad = 18
    title_h = 36
    name_f = _font(15, True)
    cap_f = _font(12, True)
    title_f = _font(19, True)

    right_w = max(crop_zoom.get_width(), inset_zoom.get_width())
    sheet_w = pad + W + pad + right_w + pad
    sheet_h = title_h + pad + max(
        H, 24 + crop_zoom.get_height() + 40 + 24 + inset_zoom.get_height()) + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 14, 30))

    ti = title_f.render(
        "Skybit - Gameplay HUD - Round 3 FINAL - Direction C (Adventure "
        "Plaques)  -  score 12 - coins x7 - magnet 5.5s/8s", True, _GOLD_PALE)
    sheet.blit(ti, (pad, 9))

    # main screen
    sx = pad
    sy = title_h + pad
    sheet.blit(frame, (sx, sy))
    pygame.draw.rect(sheet, _GOLD_DEEP, (sx, sy, W, H), 1)
    sheet.blit(name_f.render("Full screen (360x640) in context", True,
                             _GOLD_BRIGHT), (sx, title_h + 2))

    # right column: worst-case legibility crop
    rx = pad + W + pad
    ry = title_h + pad + 24
    sheet.blit(cap_f.render(
        "WORST CASE: score + timer over a BROWN PILLAR (2x crop)", True,
        UI_ORANGE), (rx, ry - 18))
    sheet.blit(crop_zoom, (rx, ry))
    pygame.draw.rect(sheet, _GOLD_DEEP,
                     (rx, ry, crop_zoom.get_width(), crop_zoom.get_height()), 1)

    # right column: blend-test inset
    iy = ry + crop_zoom.get_height() + 46
    sheet.blit(cap_f.render(
        "BLEND TEST: 1x timer (navy track) vs 1x in-play coin (2x view)", True,
        UI_ORANGE), (rx, iy - 18))
    sheet.blit(inset_zoom, (rx, iy))
    pygame.draw.rect(sheet, _GOLD_DEEP,
                     (rx, iy, inset_zoom.get_width(), inset_zoom.get_height()), 1)

    # dims footnote
    dims = (
        f"DIMS  score plaque {score_rect.width}x{score_rect.height} @ top-CENTRE "
        f"y=6 (bottom {score_rect.bottom}px, in top ~56px)   |   "
        f"timer {timer_rect.width}px bar LEFT-anchored x={timer_rect.x} "
        f"(navy track {_NAVY_TRACK_TOP}->{_NAVY_TRACK_BOT}, gold fill + dark "
        f"outline)   |   pause 84x54 top-RIGHT inset 10px   |   "
        f"coin plaque top-LEFT x=10")
    fy = iy + inset_zoom.get_height() + 16
    sheet.blit(cap_f.render(dims[:120], True, UI_CREAM), (rx, fy))
    sheet.blit(cap_f.render(dims[120:], True, UI_CREAM), (rx, fy + 16))

    pygame.image.save(sheet, OUT)
    print(f"saved {OUT}  ({sheet_w}x{sheet_h})")
    print(f"score plaque: {score_rect.width}x{score_rect.height} @ "
          f"({score_rect.x},{score_rect.y}) bottom={score_rect.bottom}")
    print(f"timer: bar {timer_rect.width}px @ x={timer_rect.x} y={timer_rect.y} "
          f"(navy {_NAVY_TRACK_TOP}->{_NAVY_TRACK_BOT})")
    print(f"in-play coin 1x diameter: {coin_d}px")


if __name__ == "__main__":
    main()
