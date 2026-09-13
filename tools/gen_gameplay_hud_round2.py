"""Round-2 refinement of the in-gameplay HUD (STATE_PLAY), direction C only.

The user locked direction C ("Adventure Plaques" — carved wood + parchment
with gold rope-band/rivet edges) from round 1 and asked for four changes:
  1. Remove ALL cast/drop shadows (flat silhouette; keep only the carved bevel
     that comes from gradients + inner light).
  2. Move the SCORE plaque and the POWER-UP TIMER bar WAY up near the top edge,
     out of the central play corridor; drop/minimize the rope hangers.
  3. PAUSE: larger PILL (rounded-rect, wider than tall, >=52px tall tap target),
     wood/parchment with a gold rope-band rim — not the round medallion.
  4. COIN counter: re-theme to a small carved-wood/parchment rope-band plaque
     (same family as the score), not a plain navy chip.

Three proportion micro-variants so the user can lock the layout:
  V1 = baseline refined C
  V2 = score pushed even higher / smaller
  V3 = a wider/taller pause pill

Composited at 4x supersample then smoothscaled (the project's crisp-edge trick,
as in powerup_help._dark_panel) so rope rim / bevel don't pixel-step. Each is
drawn over a REAL seeded gameplay backdrop with the live HUD suppressed, so the
plaques are judged over both bright sky and dark pillars.

Standalone review tooling — does NOT touch game/hud.py or game/scenes.py.
Run from repo root: python tools/gen_gameplay_hud_round2.py
Output: docs/gameplay_hud/round_2.png
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import math
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
    _GOLD_BRIGHT, _GOLD_MUTED, _GOLD_DEEP, _GOLD_PALE, _RED_OUTLINE,
    _SCARLET_TOP, _SCARLET_BOT, _PANEL_DARK, _NIGHT_DEEP,
)
from game.draw import (
    lerp_color, UI_CREAM, UI_GOLD, UI_ORANGE, UI_RED, WHITE, NEAR_BLACK,
)
from game.powerup_help import _powerup_icon

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "round_2.png")

# Representative live values the brief asked for.
SCORE = "12"
COINS = 7
PU_KIND = "magnet"
PU_REMAIN = 5.5
PU_TOTAL = MAGNET_DURATION  # 8.0

SS = 4  # supersample factor — composite big, smoothscale to native.

# Adventure-plaque tones: warm carved wood, parchment cream, gold rope.
_WOOD_LT = (96, 62, 34)
_WOOD_MD = (70, 44, 24)
_WOOD_DK = (44, 27, 14)
_PARCH_LT = (236, 214, 164)
_PARCH_DK = (198, 168, 112)


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
    surface is scaled back to native (the round-1 band read as a plain double
    rim — bumping the strand contrast + pitch is what makes the braid legible).
    A thin pale inner thread closes the bevel. Drawn on the supersampled surf."""
    pygame.draw.rect(ss, _GOLD_DEEP, (0, 0, ow, oh), width=width_n,
                     border_radius=orad)
    # Braided twist-strands: bright diagonal ticks marching along each run,
    # pitched at ~45deg, spaced so a couple of strands survive per native pixel.
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
    # thin bright inner thread closes off the bevel
    pygame.draw.rect(ss, (*_GOLD_BRIGHT, 220),
                     (width_n, width_n, ow - 2 * width_n, oh - 2 * width_n),
                     width=SS, border_radius=max(1, orad - width_n))


def _rivets(ss, ow, oh, m):
    for px, py in ((m, m), (ow - m, m), (m, oh - m), (ow - m, oh - m)):
        pygame.draw.circle(ss, _GOLD_DEEP, (px, py), 3 * SS)
        pygame.draw.circle(ss, _GOLD_BRIGHT, (px, py), 3 * SS, SS)
        pygame.draw.circle(ss, _GOLD_PALE, (px - SS, py - SS), SS)


def _wood_plaque(surf, rect, radius, parchment=False, band=4, rivets=True):
    """Carved-wood (or parchment) plaque with a gold rope-band rim and rivets.
    NO drop shadow — the relief comes only from the body gradient, an inner
    carved groove, and the inner-light highlight on the rope. Flat silhouette."""
    ss = _ss_surf(rect.width, rect.height)
    ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
    top, bot = (_PARCH_LT, _PARCH_DK) if parchment else (_WOOD_LT, _WOOD_DK)
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
    parchment-pale pause bars. NO drop shadow."""
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
    # pause bars, scaled to the pill height
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


def _timer_row(surf, top_y, bar_w=126, bar_h=16, icon=28):
    """Wood icon medallion + carved parchment-rim track with a gold->red fill."""
    row_w = icon + 6 + bar_w
    base_x = (W - row_w) // 2
    frac = PU_REMAIN / PU_TOTAL
    # wood icon medallion (small, round — matches the carved family)
    ic = pygame.Rect(base_x, top_y - (icon - bar_h) // 2, icon, icon)
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
    # carved track with a gold rope rim
    bx = ic.right + 6
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    _vgrad_rounded(track, pygame.Rect(0, 0, bar_w, bar_h), _WOOD_DK, (28, 16, 8),
                   bar_h // 2, alpha=248)
    pygame.draw.rect(track, _GOLD_DEEP, (0, 0, bar_w * SS, bar_h * SS),
                     width=2 * SS, border_radius=bar_h * SS // 2)
    pygame.draw.rect(track, (*_GOLD_BRIGHT, 180),
                     (SS, SS, bar_w * SS - 2 * SS, bar_h * SS - 2 * SS),
                     width=SS, border_radius=bar_h * SS // 2)
    _blit_ss(surf, track, tr.x, tr.y, bar_w, bar_h)
    fhi, flo = _timer_colors(frac)
    fillw = int((bar_w - 6) * frac)
    if fillw > 4:
        fill = _ss_surf(fillw, bar_h - 6)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h - 6), fhi, flo,
                       (bar_h - 6) // 2)
        _blit_ss(surf, fill, bx + 3, tr.y + 3, fillw, bar_h - 6)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (bx + bar_w // 2, tr.centery), 11,
              _PARCH_LT, _WOOD_DK, 1)


# ── the three top-anchored proportion variants ──────────────────────────────
def _coins_plaque(surf, top_y=10, h=34, font_px=19):
    # Extra left padding clears the coin face off the rope rim; the count sits
    # in deep wood-brown so it reads as carved into the parchment.
    ct = f"x{COINS}"
    cw = _font(font_px, True).size(ct)[0] + 48
    cp = pygame.Rect(10, top_y, cw, h)
    _wood_plaque(surf, cp, 9, parchment=True, band=3, rivets=False)
    _coin_icon(surf, cp.x + 20, cp.centery, 10)
    ci = _font(font_px, True).render(ct, True, _WOOD_DK)
    surf.blit(ci, ci.get_rect(midleft=(cp.x + 34, cp.centery)))


def variant_v1(surf):
    """Baseline refined C: score + timer pushed to the top band, no shadows,
    pill pause, parchment coins plaque."""
    _coins_plaque(surf, top_y=10, h=34, font_px=19)
    # SCORE — center, near the top edge (no rope hangers at the top)
    sf = _font(38, True)
    sw = max(sf.size(SCORE)[0] + 52, 92)
    sp = pygame.Rect((W - sw) // 2, 8, sw, 46)
    _wood_plaque(surf, sp, 11)
    _outlined(surf, SCORE, sp.center, 36, _GOLD_PALE, _WOOD_DK, 2)
    # PAUSE pill (wider than tall) top-right inset
    pw, ph = 72, 48
    _pause_pill(surf, pygame.Rect(W - pw - 10, 10, pw, ph), ph // 2)
    # TIMER just beneath the score, still in the top band
    _timer_row(surf, top_y=64, bar_w=126, bar_h=16, icon=28)


def variant_v2(surf):
    """Score pushed even higher + smaller; tighter top band overall."""
    _coins_plaque(surf, top_y=8, h=32, font_px=18)
    sf = _font(32, True)
    sw = max(sf.size(SCORE)[0] + 46, 82)
    sp = pygame.Rect((W - sw) // 2, 6, sw, 40)
    _wood_plaque(surf, sp, 10)
    _outlined(surf, SCORE, sp.center, 30, _GOLD_PALE, _WOOD_DK, 2)
    pw, ph = 70, 46
    _pause_pill(surf, pygame.Rect(W - pw - 10, 8, pw, ph), ph // 2)
    _timer_row(surf, top_y=54, bar_w=124, bar_h=15, icon=26)


def variant_v3(surf):
    """Baseline geometry, but a wider/taller pause pill for a bigger tap target."""
    _coins_plaque(surf, top_y=10, h=34, font_px=19)
    sf = _font(38, True)
    sw = max(sf.size(SCORE)[0] + 52, 92)
    sp = pygame.Rect((W - sw) // 2, 8, sw, 46)
    _wood_plaque(surf, sp, 11)
    _outlined(surf, SCORE, sp.center, 36, _GOLD_PALE, _WOOD_DK, 2)
    pw, ph = 84, 54
    _pause_pill(surf, pygame.Rect(W - pw - 10, 10, pw, ph), ph // 2)
    _timer_row(surf, top_y=70, bar_w=126, bar_h=16, icon=28)


VARIANTS = [
    ("V1  Baseline refined C", "Score + timer in the top band, parchment coins",
     "Pause pill 72x48", variant_v1),
    ("V2  Score higher / smaller", "Tighter top band, score nudged to the edge",
     "Pause pill 70x46", variant_v2),
    ("V3  Wider / taller pill", "Same layout, more generous pause tap target",
     "Pause pill 84x54", variant_v3),
]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    backdrop = build_backdrop()

    pad = 18
    label_h = 60
    cols = len(VARIANTS)
    cell_w = W + pad
    sheet_w = pad + cols * cell_w
    sheet_h = pad + label_h + H + pad

    name_f = _font(17, True)
    desc_f = _font(12, True)
    callout_f = _font(13, True)
    title_f = _font(20, True)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 14, 30))

    for i, (name, desc, callout, fn) in enumerate(VARIANTS):
        x = pad + i * cell_w
        ni = name_f.render(name, True, _GOLD_BRIGHT)
        sheet.blit(ni, (x, pad + 2))
        di = desc_f.render(desc, True, UI_CREAM)
        sheet.blit(di, (x, pad + 24))
        co = callout_f.render(callout, True, UI_ORANGE)
        sheet.blit(co, (x, pad + 40))
        frame = backdrop.copy()
        fn(frame)
        fy = pad + label_h
        sheet.blit(frame, (x, fy))
        pygame.draw.rect(sheet, _GOLD_DEEP, (x, fy, W, H), 1)

    foot = title_f.render(
        "Skybit - Gameplay HUD - Round 2 - Direction C refined (no shadows, "
        "top-anchored score+timer, pill pause, parchment coins)  -  "
        "score 12 - coins x7 - magnet 5.5s/8s",
        True, _GOLD_PALE)
    final = pygame.Surface((sheet_w, sheet_h + 30))
    final.fill((12, 9, 22))
    final.blit(sheet, (0, 30))
    final.blit(foot, (pad, 8))

    pygame.image.save(final, OUT)
    print(f"saved {OUT}  ({sheet_w}x{sheet_h + 30})")


if __name__ == "__main__":
    main()
