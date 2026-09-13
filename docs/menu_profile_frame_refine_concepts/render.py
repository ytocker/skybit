"""Round 2 — mature the chosen FRAMED-IN-PLACE Profile entry.

Round 1 explored five subtler-frame treatments over a single, permanently
dimmed dusk sky. The art-director returned ITERATE: keep going with the
double-rule jewel edge (Option 1) as the winner and the inset matte
(Option 3) as the safe alternate, cull the rest, and — critically — PROVE
the hairline frame + PROFILE label at the DAY extreme, since the live menu
rides a 5-minute day/night cycle and round 1 never showed the bright end.

This sheet ships THREE matured cards, each a full 360x640 menu mock over
the real DUSK biome sky, plus a paired row of TRUE 1x proof crops — every
card rendered once over dusk and once over the brightest MIDDAY biome sky
(the DAY keyframe in game/biome.py) so we can confirm the gilt survives
where the sky is loudest:

  A · HYBRID WINNER   Option 1 hardened — double-rule jewel edge (outer
                      _GOLD_MID + inner _GOLD_BRIGHT, ~6px air gap) with a
                      THIN dark scrim hint just inside the inner rule as
                      contrast insurance; PROFILE (13) on a struck cartouche
                      that carries a pale top rim-light like the STORE chips.
  B · INSET MATTE     Option 3 unchanged — a soft dark inner mat does the
                      contrast work under a single bright hairline rim;
                      PROFILE ENGRAVED (14, +1px for the engraving cost).
  C · JEWEL + PLATE   Option 1's double-rule jewel edge carrying a small
                      beveled brass PROFILE nameplate (from Option 5)
                      instead of a cartouche.

Shared with round 1: the live standing Pip IS the button (no second
parrot), PROFILE stays GOLD (scarlet is reserved for START), a violet
records badge tucks into the top-right interior, and the sin(T*3.6)
START-pill pulse drives every card's tap-glow.
"""
import os
import math
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

pygame.init()
pygame.display.set_mode((8, 8))

from game.config import W, H
from game import parrot  # noqa: F401  (ensures the macaw sprite cache is warm)
from game.entities import Bird
from game import intro as _intro
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _pill_btn, _volume_panel, _tracked_label,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _draw_trophy, _draw_gear, _coin_icon,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _ORANGE_BORDER, _AWSTAR_HI,
)

# Freeze near the crest of the START pill's tappability pulse (draw_menu
# rides it at sin(title_t * 3.6)) so every card shows its tap-glow halo at
# the same brightness and tappability is judged fairly.
T = 0.55
GLOW = 0.5 + 0.5 * math.sin(T * 3.6)          # 0..1 tap-glow pulse
STARS = [(int(37 * i * 1.7 % W), int(23 + 71 * i * 1.3 % 210),
          1 + (i % 2), i * 0.9) for i in range(26)]

# Mid-value gold — the outer step that turns a flat edge into a struck
# bevel against the brighter inner rule (matches the HUD gold family).
_GOLD_MID = (212, 160, 44)
# Records badge ground: a deep violet so the folded-in Awards cue can
# never read as gold currency and never clash with the scarlet START.
_REC_GROUND = (96, 46, 150)
_REC_GROUND_D = (58, 24, 96)

# ── The two sky extremes the frame must survive ──────────────────────────────
# Pulled from game/biome.py keyframes: DUSK (0.5125) is the mood the menu
# usually sits in; DAY (0.0) is the brightest the cycle ever gets — the real
# stress test for a thin gold hairline, which round 1 never showed.
DUSK_SKY = dict(top=(25, 20, 70), mid=(70, 45, 130), bot=(170, 95, 140),
                horizon=(255, 150, 140), mtn_alpha=195, stars=True,
                dim=(8, 3, 30, 78))
DAY_SKY = dict(top=(40, 110, 200), mid=(90, 170, 230), bot=(170, 220, 245),
               horizon=(255, 240, 200), mtn_alpha=150, stars=False,
               dim=(255, 250, 236, 8))


# ── The live diorama (reused Pip, no second parrot) ──────────────────────────
def diorama_rects():
    """House + standing-Pip footprints at their REAL menu positions, so
    every treatment frames exactly what the running menu draws."""
    house = _intro.get_sprite("skyhouse_post")
    hw, hh = house.get_size()
    hx = int(W * 0.30) - hw // 2
    hy = int(H * 0.42) - hh // 2
    house_r = pygame.Rect(hx, hy, hw, hh)
    bird_r = pygame.Rect(90 - 34, int(H * 0.42) - 34, 68, 84)
    return house_r, bird_r, (house, hx, hy)


def draw_diorama(surf):
    """Blit the post-house then the LIVE Bird — the exact menu composition."""
    _house, hx, hy = diorama_rects()[2]
    surf.blit(_house, (hx, hy))
    Bird().draw(surf)


def dio_region(pad=12):
    house_r, bird_r, _ = diorama_rects()
    return house_r.union(bird_r).inflate(pad * 2, pad * 2)


# ── Shared cues ──────────────────────────────────────────────────────────────
def tap_glow(surf, rect, radius=16, strength=1.0):
    """Gold halo whose alpha rides the START-pill sin(t*3.6) pulse so the
    card reads as tappable chrome, not passive scenery."""
    pad = 14
    glow = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2),
                          pygame.SRCALPHA)
    for k in range(pad, 0, -1):
        a = int(strength * (48 + 40 * GLOW) * k / pad / 3.6)
        gr = pygame.Rect(pad - k, pad - k,
                         rect.width + k * 2, rect.height + k * 2)
        pygame.draw.rect(glow, (*_GOLD_BRIGHT, a), gr, border_radius=radius + k)
    surf.blit(glow, (rect.x - pad, rect.y - pad))


def subtle_vignette(surf, fr, alpha=70, inset=6, radius=16):
    """Dim a narrow band AROUND the card then punch the interior back to
    clear, so the eye is pulled to the diorama-as-card WITHOUT dimming Pip
    or bleeding onto the wordmark / START (band is clipped to the card)."""
    band_top = fr.top - 12
    band_h = fr.height + 24
    vig = pygame.Surface((W, band_h), pygame.SRCALPHA)
    vig.fill((4, 2, 16, alpha))
    pygame.draw.rect(vig, (0, 0, 0, 0),
                     fr.inflate(-inset, -inset).move(0, -band_top),
                     border_radius=radius)
    surf.blit(vig, (0, band_top))


def records_badge(surf, cx, cy):
    """The folded-in Awards cue: a violet chip with a legible gold trophy
    and a small superscript count — a distinct shape AND colour so it reads
    as 'records inside', never as a coin. Seated so it clears the top rule."""
    w, hh = 33, 18
    r = pygame.Rect(int(cx - w / 2), int(cy - hh / 2), w, hh)
    sh = pygame.Surface((w + 4, hh + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 135), sh.get_rect(), border_radius=8)
    surf.blit(sh, (r.x - 1, r.y + 2))
    pygame.draw.rect(surf, _REC_GROUND_D, r, border_radius=8)
    pygame.draw.rect(surf, _REC_GROUND, r.inflate(-2, -2), border_radius=7)
    pygame.draw.rect(surf, _GOLD_BRIGHT, r, width=1, border_radius=8)
    _draw_trophy(surf, r.left + 12, r.centery + 1, 7)
    f = _font(10, True)
    img = f.render("3", True, _GOLD_PALE)
    # Nudged 1px off the rounded corner so the glyph doesn't kiss the bevel.
    surf.blit(img, img.get_rect(center=(r.right - 9, r.top + 6)))


def tri(surf, cx, cy, size, color):
    """Right-pointing chevron 'tap through' cue — the vendored font has no
    such glyph, so it is a small filled triangle."""
    pygame.draw.polygon(surf, color, [(cx - size // 2, cy - size),
                                      (cx + size // 2, cy),
                                      (cx - size // 2, cy + size)])


def profile_label(surf, plate, dark_engrave=False, size=13):
    """PROFILE (gold) + a tap chevron, centred on a rail; when engraved
    directly onto a dark mat/plate, a 1px dark shadow sinks the letters."""
    lx = plate.centerx - 7
    if dark_engrave:
        _tracked_label(surf, "PROFILE", (lx, plate.centery + 1), size,
                       color=(20, 10, 4), track=2, alpha=200)
    _tracked_label(surf, "PROFILE", (lx, plate.centery), size,
                   color=_GOLD_PALE, track=2, alpha=250)
    tri(surf, plate.right - 9, plate.centery, 4, _GOLD_PALE)


# ── Card A — HYBRID WINNER (double-rule jewel edge + scrim hint) ──────────────
def card_hybrid(surf):
    fr = dio_region(pad=12)
    fr.height += 16
    subtle_vignette(surf, fr, alpha=78, inset=6, radius=14)
    tap_glow(surf, fr, radius=15, strength=0.9)

    # Contrast insurance: a THIN dark band tucked just inside the inner rule
    # — about a third the width of Card B's full mat, a hint not a box — so
    # the jewel edge still reads where the midday sky is loudest.
    scrim = pygame.Surface(fr.size, pygame.SRCALPHA)
    pygame.draw.rect(scrim, (10, 6, 26, 102),
                     scrim.get_rect().inflate(-14, -14), border_radius=9)
    pygame.draw.rect(scrim, (0, 0, 0, 0),
                     scrim.get_rect().inflate(-30, -30), border_radius=6)
    surf.blit(scrim, fr.topleft)

    # Double-rule jewel edge: mid-gold outer, bright inner, ~6px air gap.
    pygame.draw.rect(surf, _GOLD_MID, fr, width=1, border_radius=14)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-12, -12), width=1,
                     border_radius=9)
    pygame.draw.line(surf, (*_GOLD_PALE, 200), (fr.left + 16, fr.top + 2),
                     (fr.right - 16, fr.top + 2), 1)

    plate = pygame.Rect(fr.centerx - 58, fr.bottom - 20, 116, 19)
    pygame.draw.rect(surf, (16, 10, 34), plate, border_radius=9)
    pygame.draw.rect(surf, _GOLD_MID, plate, width=1, border_radius=9)
    # Pale top rim-light inside the pill so the cartouche reads as struck
    # chrome, matching the STORE/TOP 10 chips' top sheen.
    pygame.draw.line(surf, (*_GOLD_PALE, 160), (plate.left + 12, plate.top + 3),
                     (plate.right - 12, plate.top + 3), 1)
    profile_label(surf, plate, size=13)
    records_badge(surf, fr.right - 30, fr.top + 20)


# ── Card B — INSET MATTE + THIN RIM (safe-contrast alternate) ─────────────────
# Construction unchanged from round-1 Option 3: a soft translucent dark mat
# borders the interior with one bright hairline rim; PROFILE is ENGRAVED
# straight into the mat's lower band. The mat, not the metal, carries the
# contrast — so it's the safest play at the bright extreme.
def card_matte(surf):
    fr = dio_region(pad=13)
    fr.height += 18
    subtle_vignette(surf, fr, alpha=58, inset=6, radius=16)
    tap_glow(surf, fr, radius=16, strength=0.9)

    mat = pygame.Surface((fr.w, fr.h), pygame.SRCALPHA)
    pygame.draw.rect(mat, (10, 6, 26, 165), mat.get_rect(), border_radius=15)
    interior = mat.get_rect().inflate(-24, -26)
    interior.height -= 8
    interior.top -= 4
    pygame.draw.rect(mat, (0, 0, 0, 0), interior, border_radius=8)
    surf.blit(mat, fr.topleft)

    pygame.draw.rect(surf, _GOLD_BRIGHT, fr, width=1, border_radius=15)
    pygame.draw.line(surf, (*_GOLD_PALE, 150), (fr.left + 16, fr.top + 1),
                     (fr.right - 16, fr.top + 1), 1)

    band = pygame.Rect(fr.left, fr.bottom - 20, fr.w, 20)
    # +1px over Card A: engraving trades a hair of legibility for the sunk look.
    profile_label(surf, band, dark_engrave=True, size=14)
    records_badge(surf, fr.right - 30, fr.top + 20)


# ── Card C — JEWEL EDGE + BEVELED NAMEPLATE ──────────────────────────────────
# Option 1's double-rule jewel edge, but a small beveled brass PROFILE
# nameplate (lifted from round-1 Option 5) carries the label instead of a
# flat cartouche — jewel edge + plate.
def card_plate(surf):
    fr = dio_region(pad=12)
    fr.height += 20
    subtle_vignette(surf, fr, alpha=72, inset=6, radius=14)
    tap_glow(surf, fr, radius=15, strength=0.9)

    pygame.draw.rect(surf, _GOLD_MID, fr, width=1, border_radius=14)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-12, -12), width=1,
                     border_radius=9)
    pygame.draw.line(surf, (*_GOLD_PALE, 200), (fr.left + 16, fr.top + 2),
                     (fr.right - 16, fr.top + 2), 1)

    plate = pygame.Rect(fr.centerx - 60, fr.bottom - 24, 120, 22)
    sh = pygame.Surface((plate.w + 6, plate.h + 6), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 140), sh.get_rect(), border_radius=8)
    surf.blit(sh, (plate.x - 3, plate.y + 2))
    pygame.draw.rect(surf, _GOLD_DEEP, plate, border_radius=7)
    pygame.draw.rect(surf, _GOLD_MID, plate.inflate(-3, -3), border_radius=6)
    pygame.draw.line(surf, _GOLD_PALE, (plate.left + 8, plate.top + 3),
                     (plate.right - 8, plate.top + 3), 1)
    pygame.draw.line(surf, (60, 40, 6), (plate.left + 8, plate.bottom - 3),
                     (plate.right - 8, plate.bottom - 3), 1)
    inset = plate.inflate(-8, -8)
    pygame.draw.rect(surf, (30, 18, 8), inset, border_radius=4)
    profile_label(surf, inset, dark_engrave=True, size=13)
    records_badge(surf, fr.right - 30, fr.top + 20)


# ── Shared menu mock over a chosen biome sky ─────────────────────────────────
def sky_gradient(surf, sky):
    """A 3-stop vertical biome sky (top -> mid -> bot) with a warm horizon
    band at the base — the same shape the live menu's sky takes."""
    for yy in range(H):
        t = yy / (H - 1)
        if t < 0.55:
            c = lerp_color(sky["top"], sky["mid"], t / 0.55)
        else:
            c = lerp_color(sky["mid"], sky["bot"], (t - 0.55) / 0.45)
        surf.fill(c, (0, yy, W, 1))
    # Horizon glow so the base doesn't read as a flat block.
    hb = 90
    for yy in range(H - hb, H):
        t = (yy - (H - hb)) / hb
        c = lerp_color(sky["bot"], sky["horizon"], t * 0.6)
        surf.fill(c, (0, yy, W, 1))


def menu_base(sky):
    surf = pygame.Surface((W, H)).convert_alpha()
    sky_gradient(surf, sky)
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill(sky["dim"])
    surf.blit(dim, (0, 0))
    if sky["stars"]:
        _draw_overlay_stars(surf, STARS, T)
    _draw_mountain_silhouette(surf, alpha=sky["mtn_alpha"])

    draw_diorama(surf)

    pulse = 1.0 + math.sin(T * 2.4) * 0.04
    _outlined_text(surf, "SKYBIT", (W // 2, 126), size=int(72 * pulse), px=3)
    _outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 184),
                   size=22, px=2, shadow_offset=(2, 3))
    pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                     (W // 2 - 70, 208), (W // 2 + 70, 208), 1)

    btn_alpha = int(225 + math.sin(T * 3.6) * 30)
    _pill_btn(surf, (W // 2, 430), "START", size=24, alpha=btn_alpha,
              min_width=240, primary=True, dim=True, shadow=False)
    return surf


def bottom_chips(surf):
    """STORE · TOP 10 · SETTINGS — Awards has folded into Profile."""
    cy = H - 86
    tile_w, tgap, tile_h = 84, 8, 54
    tx = (W - (tile_w * 3 + tgap * 2)) // 2
    for label, kind in (("STORE", "coin"), ("TOP 10", "trophy"),
                        ("SETTINGS", "gear")):
        r = pygame.Rect(tx, cy - tile_h // 2, tile_w, tile_h)
        _volume_panel(surf, r, radius=13)
        if kind == "coin":
            _coin_icon(surf, r.centerx, cy - 5, 12)
        elif kind == "trophy":
            _draw_trophy(surf, r.centerx, cy - 5, 10)
        else:
            _draw_gear(surf, r.centerx, cy - 5, 12)
        _tracked_label(surf, label, (r.centerx, cy + 15), 10,
                       color=_AWSTAR_HI, track=1, alpha=210)
        tx += tile_w + tgap


# ── Assembly ─────────────────────────────────────────────────────────────────
CARDS = [
    ("A · HYBRID WINNER", card_hybrid),
    ("B · INSET MATTE + RIM", card_matte),
    ("C · JEWEL + NAMEPLATE", card_plate),
]

# True-1x proof crop around the card — captures the full jewel edge, the
# PROFILE plate and the records badge with a small margin, so frame weight
# and label legibility read at native scale over each sky.
PROOF = pygame.Rect(17, 180, 182, 196)


def build_panel(over_fn, sky):
    surf = menu_base(sky)
    over_fn(surf)
    bottom_chips(surf)
    return surf


def main():
    pad, gap = 24, 24
    hdr = 70
    lab = 30
    proof_gap = 30
    proof_lab = 24
    proof_h = PROOF.height
    n = len(CARDS)

    sheet_w = pad * 2 + n * W + (n - 1) * gap
    sheet_h = (pad + hdr + H + lab + proof_gap
               + proof_lab + proof_h + pad)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 34))

    title_f = _font(26, True)
    sub_f = _font(15, True)
    sheet.blit(title_f.render(
        "SKYBIT · Profile FRAME REFINE — Round 2 · three matured cards, "
        "proven at DUSK + MIDDAY",
        True, (240, 224, 180)), (pad, 12))
    sheet.blit(sub_f.render(
        "Full mocks over the DUSK biome sky · paired TRUE 1x proofs below "
        "confirm the hairline frame + PROFILE label survive the bright MIDDAY "
        "sky · live Pip IS the button · PROFILE stays GOLD",
        True, (198, 186, 158)), (pad, 40))

    lab_f = _font(18, True)
    proof_f = _font(13, True)

    cols = []
    x = pad
    y = pad + hdr
    for label, over_fn in CARDS:
        dusk = build_panel(over_fn, DUSK_SKY)
        midday = build_panel(over_fn, DAY_SKY)
        cols.append((label, dusk, midday, x))
        pygame.draw.rect(sheet, (8, 5, 20), (x - 2, y - 2, W + 4, H + 4))
        sheet.blit(dusk, (x, y))
        li = lab_f.render(label, True, (250, 236, 190))
        sheet.blit(li, li.get_rect(midtop=(x + W // 2, y + H + 6)))
        x += W + gap

    # Under each card, its dusk + midday proof crops sit side by side so the
    # bright-extreme survival is judged against the same card at dusk.
    py = y + H + lab + proof_gap + proof_lab
    for label, dusk, midday, px in cols:
        pair_w = PROOF.width * 2 + 8
        base_x = px + (W - pair_w) // 2
        for i, (panel, tag) in enumerate(((dusk, "DUSK"), (midday, "MIDDAY"))):
            crop = panel.subsurface(PROOF).copy()
            cx = base_x + i * (PROOF.width + 8)
            pygame.draw.rect(sheet, (40, 30, 58),
                             (cx - 2, py - 2, PROOF.width + 4, proof_h + 4))
            sheet.blit(crop, (cx, py))
            pl = proof_f.render(
                "TRUE 1× · " + label.split("·")[0].strip() + " · " + tag,
                True, (232, 214, 168))
            sheet.blit(pl, pl.get_rect(
                midbottom=(cx + PROOF.width // 2, py - 6)))

    out = os.path.join(os.path.dirname(__file__), "round_2.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
