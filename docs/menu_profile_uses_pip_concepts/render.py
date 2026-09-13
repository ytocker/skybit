"""Round 2 — mature the two leading Profile-entry treatments side by side.

Round 1 explored five ways to turn the ALREADY-standing Pip (drawn live
via game.entities.Bird — never a second parrot) into the menu's Profile
button. The art-director culled three (spotlight-ring implied character
swapping, the tap bubble read as a dismissable coach-mark, the dashed
hotspot read as an empty slot) and asked to mature the two leaders:

  A · FRAMED-IN-PLACE   — a gilded hollow frame + vignette wraps the live
                          diorama; the scene itself becomes the card.
  B · NAMEPLATE STANDEE — Pip's snow diorama sits on an engraved brass
                          PROFILE plinth; the whole standee is the button.

Both keep PROFILE labels GOLD (scarlet stays reserved for START alone),
fold the old Awards cue into a violet records badge anchored INSIDE the
card's interior top-right (clear of the subtitle), and ride the same
sin(T*3.6) tap-glow the START pill uses. Each finalist is composited into
a full 360x640 menu mock, and a TRUE 1x proof crop of each card on the
night sky confirms the badge, PROFILE label and glow at native scale.
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
# rides it at sin(title_t * 3.6)); every Profile treatment shows the same
# "tap me" halo at its brightest so tappability is judged fairly.
T = 0.55
GLOW = 0.5 + 0.5 * math.sin(T * 3.6)          # 0..1 tap-glow pulse
STARS = [(int(37 * i * 1.7 % W), int(23 + 71 * i * 1.3 % 210),
          1 + (i % 2), i * 0.9) for i in range(26)]

# Mid-value gold between DEEP and BRIGHT — the inner step that turns a
# flat gold edge into a struck, gilded bevel (matches the HUD gold family).
_GOLD_MID = (212, 160, 44)
# Records badge ground: a deep violet so the folded-in Awards cue can
# never read as gold currency and never clash with the scarlet START.
_REC_GROUND = (96, 46, 150)
_REC_GROUND_D = (58, 24, 96)


# ── The live diorama (reused Pip, no second parrot) ──────────────────────────
def diorama_rects():
    """House + standing-Pip footprints at their REAL menu positions, so
    every treatment frames exactly what the running menu draws."""
    house = _intro.get_sprite("skyhouse_post")
    hw, hh = house.get_size()
    hx = int(W * 0.30) - hw // 2
    hy = int(H * 0.42) - hh // 2
    house_r = pygame.Rect(hx, hy, hw, hh)
    # Bird sits at (BIRD_X, H*0.42) ~ (90, 269); its sprite is ~64 px and
    # the parcel hangs a touch below, so extend the footprint downward.
    bird_r = pygame.Rect(90 - 34, int(H * 0.42) - 34, 68, 84)
    return house_r, bird_r, (house, hx, hy)


def draw_diorama(surf):
    """Blit the post-house then the LIVE Bird — the exact menu composition."""
    _house, hx, hy = diorama_rects()[2]
    surf.blit(_house, (hx, hy))
    Bird().draw(surf)


# ── Shared cues ──────────────────────────────────────────────────────────────
def tap_glow(surf, rect, shape="rrect", radius=16, strength=1.0):
    """Gold halo whose alpha rides the START-pill sin(t*3.6) pulse so the
    treatment reads as tappable chrome, not passive scenery."""
    pad = 14
    glow = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2),
                          pygame.SRCALPHA)
    for k in range(pad, 0, -1):
        a = int(strength * (48 + 40 * GLOW) * k / pad / 3.6)
        gr = pygame.Rect(pad - k, pad - k,
                         rect.width + k * 2, rect.height + k * 2)
        if shape == "ellipse":
            pygame.draw.ellipse(glow, (*_GOLD_BRIGHT, a), gr)
        else:
            pygame.draw.rect(glow, (*_GOLD_BRIGHT, a), gr,
                             border_radius=radius + k)
    surf.blit(glow, (rect.x - pad, rect.y - pad))


def records_badge(surf, cx, cy):
    """The folded-in Awards cue: a violet chip with a legible gold trophy
    and a small superscript count. Deliberately NOT a gold roundel — a
    distinct shape AND colour so it reads as 'records inside', never as a
    coin. The trophy is bumped to ~7px (was a 5px blob) and the count sits
    as a raised superscript so the icon, not the number, carries the read."""
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
    surf.blit(img, img.get_rect(center=(r.right - 8, r.top + 6)))


def tri(surf, cx, cy, size, color):
    """Right-pointing chevron — the vendored font has no such glyph, so
    the 'tap through' cue is a small filled triangle."""
    pygame.draw.polygon(surf, color, [(cx - size // 2, cy - size),
                                      (cx + size // 2, cy),
                                      (cx - size // 2, cy + size)])


# ── Shared menu mock ─────────────────────────────────────────────────────────
def menu_base(under_fn=None):
    """The live menu: night sky, mountains, SKYBIT hero, the standing Pip
    at the post-house, and START. `under_fn` paints treatment art that
    must sit BEHIND Pip (plinths) before the diorama."""
    surf = pygame.Surface((W, H)).convert_alpha()
    for yy in range(H):
        t = yy / (H - 1)
        surf.fill(lerp_color((90, 150, 205), (196, 168, 150), t), (0, yy, W, 1))
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 150))
    surf.blit(dim, (0, 0))
    _draw_overlay_stars(surf, STARS, T)
    _draw_mountain_silhouette(surf, alpha=180)

    if under_fn is not None:
        under_fn(surf)

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
    """STORE · TOP 10 · SETTINGS — Awards has folded into Profile, so the
    freed slot becomes STORE (Pip's re-skin shop)."""
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


def dio_region(pad=14):
    house_r, bird_r, _ = diorama_rects()
    return house_r.union(bird_r).inflate(pad * 2, pad * 2)


# ── Finalist A — FRAMED-IN-PLACE ─────────────────────────────────────────────
# A gilded HOLLOW frame wraps the live diorama and a vignette dims the band
# around it, so the standing-Pip scene itself becomes the character card.
# Round-2 fixes: the records badge moves fully INSIDE the interior top-right
# corner (was colliding with the subtitle); the outer wall is thinned ~2px
# and the vignette lifted so the frame reads like a jewel, not a lead box.
def concept_framed(surf):
    fr = dio_region(pad=12)
    fr.height += 14                       # room for the nameplate rail

    # Vignette: dim a band AROUND the card, then punch the frame interior
    # back to clear so the eye is pulled to the diorama-as-card. Lifted a
    # touch from round 1 so the interior reads as the lit jewel. Clipped to
    # the card's vertical band so the wordmark + START stay fully lit.
    band_top = fr.top - 12
    band_h = fr.height + 24
    vig = pygame.Surface((W, band_h), pygame.SRCALPHA)
    vig.fill((4, 2, 16, 108))
    pygame.draw.rect(vig, (0, 0, 0, 0),
                     fr.inflate(-6, -6).move(0, -band_top),
                     border_radius=16)
    surf.blit(vig, (0, band_top))

    tap_glow(surf, fr, radius=18, strength=1.05)
    sh = pygame.Surface((fr.w + 12, fr.h + 12), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), sh.get_rect(), border_radius=20)
    surf.blit(sh, (fr.x - 4, fr.y + 5))

    # Hollow beveled gilding — nested rect BORDERS (interior stays clear so
    # the live Pip shows through): deep base → mid step → bright bevel, with
    # a pale top rim-light and a dark press-bevel foot. Outer wall thinned
    # from 11 to 9 px so the frame jewels rather than boxes the diorama.
    pygame.draw.rect(surf, _GOLD_DEEP, fr, width=9, border_radius=18)
    pygame.draw.rect(surf, _GOLD_MID, fr.inflate(-5, -5), width=5,
                     border_radius=15)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-9, -9), width=2,
                     border_radius=12)
    pygame.draw.line(surf, _GOLD_PALE, (fr.left + 12, fr.top + 3),
                     (fr.right - 12, fr.top + 3), 2)
    pygame.draw.line(surf, _GOLD_DEEP, (fr.left + 12, fr.bottom - 3),
                     (fr.right - 12, fr.bottom - 3), 2)

    for cx, cy in ((fr.left + 9, fr.top + 9), (fr.right - 9, fr.top + 9),
                   (fr.left + 9, fr.bottom - 9),
                   (fr.right - 9, fr.bottom - 9)):
        pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), 3)
        pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), 3, 1)

    # Engraved PROFILE nameplate on the bottom rail (gold — scarlet stays
    # reserved for START — with a tap chevron).
    plate = pygame.Rect(fr.centerx - 52, fr.bottom - 20, 104, 17)
    pygame.draw.rect(surf, (18, 12, 40), plate, border_radius=6)
    pygame.draw.rect(surf, _GOLD_DEEP, plate, width=1, border_radius=6)
    _tracked_label(surf, "PROFILE", (plate.centerx - 6, plate.centery), 11,
                   color=_GOLD_PALE, track=2, alpha=245)
    tri(surf, plate.right - 8, plate.centery, 4, _GOLD_PALE)

    # Records badge tucked INSIDE the interior top-right corner, sitting on
    # the diorama a clear ~8 px below the subtitle baseline.
    records_badge(surf, fr.right - 28, fr.top + 17)


# ── Finalist B — NAMEPLATE STANDEE ───────────────────────────────────────────
# Pip keeps standing exactly where he is, but the whole snow diorama now sits
# on a museum plinth: a brass box whose top edge is SEATED under the snow
# ground (drawn behind the house so the snow laps its lip) — Pip stands ON it
# rather than hovering above a detached plate. An engraved PROFILE plaque
# rides the front face; a records plaque tucks into the front bottom-right.
def _standee_under(surf):
    reg = dio_region(pad=8)
    # The house snow surface sits at screen y ~ 308-321. Seat the plinth top
    # up inside that band so the snow (drawn after, over this) laps the lip
    # and the seam disappears — the merge that turns a detached plate into a
    # stand Pip stands ON.
    pw, ph = 130, 38
    top = 311
    px = reg.centerx - pw // 2
    plinth = pygame.Rect(px, top, pw, ph)
    tap_glow(surf, plinth.inflate(8, 4), radius=10, strength=0.9)

    # Top face (parallelogram) — mostly hidden under the snow lip, but its
    # side slivers read the plinth as a solid block, not a plate.
    depth = 9
    top_face = [(plinth.left, plinth.top),
                (plinth.right, plinth.top),
                (plinth.right - depth, plinth.top - depth),
                (plinth.left + depth, plinth.top - depth)]
    pygame.draw.polygon(surf, _GOLD_MID, top_face)
    pygame.draw.polygon(surf, _GOLD_DEEP, top_face, 1)

    # Front face — the plaque body, gilded with a top sheen + foot shadow.
    pygame.draw.rect(surf, _GOLD_DEEP, plinth, border_radius=4)
    pygame.draw.rect(surf, _GOLD_MID, plinth.inflate(-4, -4), border_radius=3)
    pygame.draw.line(surf, _GOLD_PALE, (plinth.left + 6, plinth.top + 4),
                     (plinth.right - 6, plinth.top + 4), 1)
    pygame.draw.line(surf, (60, 40, 6), (plinth.left + 6, plinth.bottom - 3),
                     (plinth.right - 6, plinth.bottom - 3), 1)

    # Engraved PROFILE — dark inset on the VISIBLE lower front face (the
    # upper front is under the snow lip), left of the records plaque.
    inset = pygame.Rect(plinth.left + 10, plinth.bottom - 20, 78, 16)
    pygame.draw.rect(surf, (52, 34, 8), inset, border_radius=3)
    _tracked_label(surf, "PROFILE", (inset.centerx - 5, inset.centery), 11,
                   color=_GOLD_PALE, track=2, alpha=255)
    tri(surf, inset.right - 6, inset.centery, 4, _GOLD_PALE)

    # Records badge tucked onto the plinth's front bottom-right shoulder.
    records_badge(surf, plinth.right - 22, plinth.bottom - 12)


def concept_standee(surf):
    pass  # all standee art sits behind Pip; drawn by _standee_under


# ── Assembly ─────────────────────────────────────────────────────────────────
FINALISTS = [
    ("A · FRAMED-IN-PLACE", None, concept_framed),
    ("B · NAMEPLATE STANDEE", _standee_under, concept_standee),
]

# Card region cropped for the true-1x proof strips — from just below the
# subtitle down through the card, so badge/label/glow show at native scale.
PROOF = pygame.Rect(4, 168, 212, 200)


def build_panel(under_fn, over_fn):
    surf = menu_base(under_fn)
    over_fn(surf)
    bottom_chips(surf)
    return surf


def main():
    pad, gap = 20, 26
    hdr = 66
    lab = 30
    proof_gap = 22
    proof_lab = 26
    proof_h = PROOF.height

    sheet_w = pad * 2 + 2 * W + gap
    sheet_h = (pad + hdr + H + lab + proof_gap
               + proof_lab + proof_h + pad)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 34))

    title_f = _font(26, True)
    sub_f = _font(15, True)
    sheet.blit(title_f.render(
        "SKYBIT · Profile menu-entry — Round 2 · the two matured finalists",
        True, (240, 224, 180)), (pad, 12))
    sheet.blit(sub_f.render(
        "Standing Pip IS the button (no second parrot) · PROFILE stays GOLD "
        "(scarlet = START only) · records badge inside the card · "
        "sin(T·3.6) tap-glow",
        True, (198, 186, 158)), (pad, 40))

    lab_f = _font(18, True)
    proof_f = _font(14, True)

    panels = []
    x = pad
    y = pad + hdr
    for label, under_fn, over_fn in FINALISTS:
        panel = build_panel(under_fn, over_fn)
        panels.append((label, panel, x))
        pygame.draw.rect(sheet, (8, 5, 20), (x - 2, y - 2, W + 4, H + 4))
        sheet.blit(panel, (x, y))
        li = lab_f.render(label, True, (250, 236, 190))
        sheet.blit(li, li.get_rect(midtop=(x + W // 2, y + H + 6)))
        x += W + gap

    # ── True-1x proof crops: the finalist card on the night sky at native
    # scale (subsurface of the already-1x panel — no upscale). ──────────────
    py = y + H + lab + proof_gap + proof_lab
    for label, panel, px in panels:
        crop = panel.subsurface(PROOF).copy()
        # Centre the crop under its panel column.
        cx = px + (W - PROOF.width) // 2
        pygame.draw.rect(sheet, (40, 30, 58),
                         (cx - 2, py - 2, PROOF.width + 4, proof_h + 4))
        sheet.blit(crop, (cx, py))
        pl = proof_f.render("TRUE 1× — " + label.split("·")[0].strip()
                            + " card on night sky",
                            True, (232, 214, 168))
        sheet.blit(pl, pl.get_rect(midbottom=(cx + PROOF.width // 2, py - 6)))

    out = os.path.join(os.path.dirname(__file__), "round_2.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
