"""Round-2 finals for the main-menu PROFILE entry.

Round 1 explored five ways to turn the Profile menu item into a live
character card showing Pip's CURRENT look (the base parrot drawn by
game.entities.Bird) with a folded-in "records inside" Awards cue. The
art-director culled to two leads; this sheet matures ONLY those two in
full menu context, side by side:

  A · FRAMED PORTRAIT  — a bust in a gilded, press-bevelled gold frame.
  B · AVATAR MEDALLION — a bust in a scalloped cameo ring (a portrait
                         frame, deliberately NOT a milled coin).

Both carry an explicit tap cue and a records badge that can never be
mistaken for a currency counter (violet ground + tiny trophy + count,
never gold-on-gold). Each is composited into a real 360x640 menu mock
(SKYBIT hero, standing Pip, scarlet START, STORE / TOP 10 / SETTINGS
chips) so it's judged in context. A second row crops each card at TRUE
1x off the rendered menu — the busy night-sky legibility proof — and
magnifies it 3x for detail.
"""
import os
import math
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

pygame.init()
pygame.display.set_mode((8, 8))

from game.config import W, H
from game import parrot
from game.entities import Bird
from game.draw import WHITE, NEAR_BLACK, lerp_color
from game.hud import (
    _font, _outlined_text, _pill_btn, _volume_panel, _tracked_label,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _draw_trophy, _draw_gear, _coin_icon,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE, _ORANGE_BORDER,
    _PANEL_DARK, _PANEL_LIGHTER, _AWSTAR_HI, _NIGHT_DEEP,
)

# A representative animation phase: draw_menu pulses the START pill's
# tappability glow at sin(title_t * 3.6); freezing near the crest shows
# each Profile frame carrying that same "tap me" halo at its brightest.
T = 0.55
GLOW = 0.5 + 0.5 * math.sin(T * 3.6)          # 0..1 tap-glow pulse
STARS = [(int(37 * i * 1.7 % W), int(23 + 71 * i * 1.3 % 210),
          1 + (i % 2), i * 0.9) for i in range(26)]

# Mid-step gold between _GOLD_DEEP and _GOLD_BRIGHT — the inner value
# step that turns a flat gold border into a struck, gilded one.
_GOLD_MID = (212, 160, 44)
# Records-badge ground: a deep violet, chosen so the folded-in Awards
# cue can never read as gold currency and never clash with the scarlet
# START / banner. A tiny trophy + count sits on it.
_REC_GROUND = (96, 46, 150)
_REC_GROUND_D = (58, 24, 96)


# ── Pip bust ────────────────────────────────────────────────────────────────
# A cropped head+chest of the ACTUAL base parrot, framed inside a soft
# night-sky window so it reads as "a portrait of your character" rather
# than a second full-body Pip or a macro of one goggle eye. Head center
# sits at sprite (38, 23); a lower anchor pushes the head into the upper
# third so the chest reads below it.
def parrot_bust(w, h, shape="rrect", radius=12, zoom=1.7,
                anchor=(0.5, 0.4)):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Deep-sky backdrop so the portrait window isn't a bald cutout — a
    # vertical navy wash with a warm crown glow behind Pip's head.
    for yy in range(h):
        t = yy / max(1, h - 1)
        surf.fill(lerp_color((30, 26, 74), (10, 6, 34), t),
                  (0, yy, w, 1))
    crown = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.circle(crown, (90, 74, 150, 90),
                       (int(w * anchor[0]), int(h * 0.3)), int(w * 0.55))
    surf.blit(crown, (0, 0))

    src = parrot.get_parrot(1, 0)
    sw, sh = src.get_size()
    scale = w * zoom / sw
    big = pygame.transform.smoothscale(src, (int(sw * scale),
                                             int(sh * scale)))
    bx = int(w * anchor[0] - 38 * scale)
    by = int(h * anchor[1] - 23 * scale)
    surf.blit(big, (bx, by))

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    if shape == "circle":
        pygame.draw.circle(mask, (255, 255, 255, 255),
                           (w // 2, h // 2), min(w, h) // 2)
    else:
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                         border_radius=radius)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return surf


def tap_glow(surf, rect, shape="rrect", radius=14, strength=1.0):
    """Gold halo whose alpha rides the START-pill sin(t*3.6) pulse, so the
    Profile card reads as tappable chrome rather than passive scenery."""
    pad = 12
    glow = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2),
                          pygame.SRCALPHA)
    for k in range(pad, 0, -1):
        a = int(strength * (52 + 40 * GLOW) * k / pad / 3.4)
        gr = pygame.Rect(pad - k, pad - k,
                         rect.width + k * 2, rect.height + k * 2)
        if shape == "circle":
            pygame.draw.circle(glow, (*_GOLD_BRIGHT, a), glow.get_rect().center,
                               rect.width // 2 + k)
        else:
            pygame.draw.rect(glow, (*_GOLD_BRIGHT, a), gr,
                             border_radius=radius + k)
    surf.blit(glow, (rect.x - pad, rect.y - pad))


def records_badge(surf, cx, cy):
    """The folded-in Awards cue: a violet chip with a tiny trophy + count.
    Deliberately NOT a gold roundel — a distinct shape AND colour so it
    reads as 'records inside', never as a coin / currency counter."""
    w, hh = 30, 17
    r = pygame.Rect(int(cx - w / 2), int(cy - hh / 2), w, hh)
    sh = pygame.Surface((w + 4, hh + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 130), sh.get_rect(), border_radius=8)
    surf.blit(sh, (r.x - 1, r.y + 1))
    pygame.draw.rect(surf, _REC_GROUND_D, r, border_radius=8)
    pygame.draw.rect(surf, _REC_GROUND, r.inflate(-2, -2), border_radius=7)
    pygame.draw.rect(surf, _GOLD_BRIGHT, r, width=1, border_radius=8)
    _draw_trophy(surf, r.left + 9, r.centery, 5)
    f = _font(11, True)
    img = f.render("3", True, _GOLD_PALE)
    surf.blit(img, img.get_rect(center=(r.right - 8, r.centery)))


def tri(surf, cx, cy, size, color):
    """Right-pointing chevron — the vendored font has no glyph, so the
    'tap through' cue is drawn as a small filled triangle."""
    pygame.draw.polygon(surf, color, [(cx - size // 2, cy - size),
                                      (cx + size // 2, cy),
                                      (cx - size // 2, cy + size)])


# ── Shared menu mock ─────────────────────────────────────────────────────────
def menu_base():
    """The live menu minus its bottom trio: night sky, mountains, SKYBIT
    hero, standing Pip, START. Each finalist overlays its own Profile card
    plus the STORE / TOP 10 / SETTINGS chip row."""
    surf = pygame.Surface((W, H)).convert_alpha()
    for yy in range(H):
        t = yy / (H - 1)
        surf.fill(lerp_color((90, 150, 205), (196, 168, 150), t), (0, yy, W, 1))
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 150))
    surf.blit(dim, (0, 0))
    _draw_overlay_stars(surf, STARS, T)
    _draw_mountain_silhouette(surf, alpha=180)

    Bird().draw(surf)

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
    freed slot becomes STORE (Pip's re-skin shop). Profile shows the
    RESULT of a re-skin; STORE does the re-skinning — no duplication."""
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


# Both finalists live in the clear strip ABOVE the SKYBIT title (top
# y=86), so the corner character-card never crosses the wordmark.

# ── Finalist A — Framed portrait ─────────────────────────────────────────────
# A bust in a gilded double-gold frame: rim-light on top, an inner value
# step so the gold matches the HUD/coin family, corner studs, a
# press-bevel + PROFILE ▸ nameplate for the tap cue, and a violet
# records badge nudged clear of the top-right stud.
def finalist_framed(surf):
    fr = pygame.Rect(14, 10, 92, 84)
    tap_glow(surf, fr, radius=13)
    sh = pygame.Surface((fr.w + 10, fr.h + 10), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), sh.get_rect(), border_radius=16)
    surf.blit(sh, (fr.x - 3, fr.y + 4))

    # Gilding: deep base → mid value step → bright bevel band, then a pale
    # top rim-light and a dark bottom/right press-bevel so the frame reads
    # as struck gold catching light, not a flat gold rectangle.
    pygame.draw.rect(surf, _GOLD_DEEP, fr, border_radius=13)
    pygame.draw.rect(surf, _GOLD_MID, fr.inflate(-3, -3), border_radius=12)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-5, -5), width=3,
                     border_radius=11)
    pygame.draw.line(surf, _GOLD_PALE, (fr.left + 6, fr.top + 3),
                     (fr.right - 6, fr.top + 3), 2)          # top rim-light
    pygame.draw.line(surf, _GOLD_PALE, (fr.left + 3, fr.top + 6),
                     (fr.left + 3, fr.top + 30), 2)          # left rim-light
    pygame.draw.line(surf, _GOLD_DEEP, (fr.left + 8, fr.bottom - 3),
                     (fr.right - 3, fr.bottom - 3), 2)       # press-bevel foot
    pygame.draw.line(surf, _GOLD_DEEP, (fr.right - 3, fr.top + 10),
                     (fr.right - 3, fr.bottom - 3), 2)       # press-bevel side

    # Portrait window — bust pulled back so head+chest reads.
    win = pygame.Rect(fr.x + 9, fr.y + 9, fr.w - 18, 48)
    bust = parrot_bust(win.w, win.h, radius=7, zoom=1.6, anchor=(0.5, 0.44))
    surf.blit(bust, win.topleft)
    pygame.draw.rect(surf, _GOLD_DEEP, win, width=2, border_radius=7)
    pygame.draw.line(surf, (255, 255, 255, 40), (win.left + 3, win.top + 2),
                     (win.right - 3, win.top + 2), 1)        # glass sheen

    for cx, cy in ((fr.left + 8, fr.top + 8), (fr.left + 8, fr.bottom - 8),
                   (fr.right - 8, fr.bottom - 8)):
        pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), 3)
        pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), 3, 1)
    # Top-right stud, then the records badge nudged up-and-out so the two
    # gold-ish elements never collide.
    pygame.draw.circle(surf, _GOLD_PALE, (fr.right - 8, fr.top + 8), 3)
    pygame.draw.circle(surf, _GOLD_DEEP, (fr.right - 8, fr.top + 8), 3, 1)

    # Engraved PROFILE nameplate as a tappable row: label + chevron.
    plate = pygame.Rect(fr.left + 7, win.bottom + 4, fr.w - 14, 15)
    pygame.draw.rect(surf, (18, 12, 40), plate, border_radius=5)
    pygame.draw.rect(surf, _GOLD_DEEP, plate, width=1, border_radius=5)
    _tracked_label(surf, "PROFILE", (plate.centerx - 5, plate.centery), 10,
                   color=_GOLD_PALE, track=2, alpha=240)
    tri(surf, plate.right - 7, plate.centery, 4, _GOLD_PALE)

    records_badge(surf, fr.right + 3, fr.top - 4)


# ── Finalist B — Avatar medallion ────────────────────────────────────────────
# A cameo portrait: a scalloped gold frame (NOT a milled coin rim) around
# a violet portrait mat and Pip's bust, a swallowtail PROFILE ▸ banner
# tucked under the ring foot, and a violet records badge at upper-right.
def finalist_medallion(surf):
    cx, cy, R = 58, 46, 34
    ring_rect = pygame.Rect(cx - R, cy - R, R * 2, R * 2)
    tap_glow(surf, ring_rect, shape="circle", radius=R, strength=1.1)
    pygame.draw.circle(surf, (0, 0, 0, 120), (cx + 1, cy + 3), R + 2)

    # Cameo edge — a dozen rounded ornamental knobs read as a carved
    # portrait frame. Kept to 12 (not a fine bead rim) so it neither
    # shimmers at 1x like a milled coin nor reads as gear teeth.
    NB = 12
    for i in range(NB):
        a = i / NB * math.tau
        pygame.draw.circle(surf, _GOLD_DEEP,
                           (int(cx + R * math.cos(a)),
                            int(cy + R * math.sin(a))), 5)
    for i in range(NB):
        a = i / NB * math.tau
        pygame.draw.circle(surf, _GOLD_BRIGHT,
                           (int(cx + (R - 0.5) * math.cos(a)),
                            int(cy + (R - 0.5) * math.sin(a))), 3)
    # Gilded body with an inner value step and a top rim-light arc.
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), R)
    pygame.draw.circle(surf, _GOLD_MID, (cx, cy), R - 2)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), R - 5)
    pygame.draw.arc(surf, _GOLD_PALE,
                    pygame.Rect(cx - R + 3, cy - R + 3, (R - 3) * 2, (R - 3) * 2),
                    math.radians(35), math.radians(160), 2)   # top rim-light
    pygame.draw.arc(surf, _GOLD_DEEP,
                    pygame.Rect(cx - R + 3, cy - R + 3, (R - 3) * 2, (R - 3) * 2),
                    math.radians(215), math.radians(340), 2)  # press-bevel

    # Violet portrait mat — the single strongest "portrait, not coin" signal.
    pygame.draw.circle(surf, (74, 42, 116), (cx, cy), R - 9)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), R - 9, 1)

    bd = (R - 13) * 2
    bust = parrot_bust(bd, bd, shape="circle", zoom=1.42, anchor=(0.5, 0.44))
    surf.blit(bust, (cx - bd // 2, cy - bd // 2))

    # Swallowtail PROFILE banner tucked under the ring foot (ring shrunk so
    # the banner sits below it rather than colliding).
    ban = pygame.Rect(cx - 42, cy + R - 5, 84, 18)
    pygame.draw.rect(surf, (168, 34, 30), ban, border_radius=6)
    pygame.draw.rect(surf, _GOLD_BRIGHT, ban, width=1, border_radius=6)
    pygame.draw.polygon(surf, (120, 20, 18),
                        [(ban.left, ban.top), (ban.left - 7, ban.top),
                         (ban.left, ban.centery)])
    pygame.draw.polygon(surf, (120, 20, 18),
                        [(ban.right, ban.top), (ban.right + 7, ban.top),
                         (ban.right, ban.centery)])
    _tracked_label(surf, "PROFILE", (ban.centerx - 4, ban.centery), 10,
                   color=(255, 244, 224), track=2, alpha=255)
    tri(surf, ban.right - 8, ban.centery, 4, _GOLD_PALE)

    records_badge(surf, cx + R - 1, cy - R + 5)


FINALISTS = [
    ("A · FRAMED PORTRAIT", finalist_framed, pygame.Rect(6, 2, 118, 100)),
    ("B · AVATAR MEDALLION", finalist_medallion, pygame.Rect(10, 2, 116, 106)),
]


def build_panel(draw_fn):
    surf = menu_base()
    draw_fn(surf)
    bottom_chips(surf)
    return surf


def main():
    pad, gap, hdr = 18, 16, 46
    cols = len(FINALISTS)
    sheet_w = pad * 2 + cols * W + (cols - 1) * gap

    panels = [(label, build_panel(fn), crop) for label, fn, crop in FINALISTS]

    # Proof band: for each finalist, a TRUE 1x crop off the rendered menu
    # (busy night sky) and a 3x magnification below it.
    proof_hdr = 30
    lab1x, lab3x = 20, 20
    crop_h = max(c.h for _, _, c in FINALISTS)
    proof_band = proof_hdr + lab1x + crop_h + 10 + lab3x + crop_h * 3 + pad
    sheet_h = pad + hdr + H + gap + proof_band

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 18, 34))

    title_f = _font(26, True)
    t = title_f.render(
        "SKYBIT · Profile menu-entry — Round 2 · two finalists",
        True, (240, 224, 180))
    sheet.blit(t, (pad, 10))

    lab_f = _font(18, True)
    small_f = _font(14, True)

    # Row 1 — full menu mocks.
    x = pad
    y = pad + hdr
    for label, panel, _crop in panels:
        pygame.draw.rect(sheet, (8, 5, 20), (x - 2, y - 2, W + 4, H + 4))
        sheet.blit(panel, (x, y))
        li = lab_f.render(label, True, (250, 236, 190))
        sheet.blit(li, li.get_rect(midtop=(x + W // 2, pad + 16)))
        x += W + gap

    # Row 2 — 1x + 3x legibility proof, one column per finalist.
    py0 = y + H + gap
    ph = title_f.render("TRUE 1× ON NIGHT SKY  ·  3× DETAIL BELOW",
                        True, (220, 206, 168))
    sheet.blit(ph, (pad, py0))
    col_w = (sheet_w - pad * 2 - gap) // 2
    for idx, (label, panel, crop) in enumerate(panels):
        cx0 = pad + idx * (col_w + gap)
        cyy = py0 + proof_hdr
        one = panel.subsurface(crop).copy()
        # 1x crop, framed.
        l1 = small_f.render(f"{label.split(' · ')[0]}  —  1×", True,
                            (236, 222, 180))
        sheet.blit(l1, (cx0, cyy))
        cyy += lab1x
        pygame.draw.rect(sheet, (8, 5, 20),
                         (cx0 - 1, cyy - 1, crop.w + 2, crop.h + 2))
        sheet.blit(one, (cx0, cyy))
        cyy += crop.h + 10
        # 3x magnification (nearest — shows the real pixels a phone renders).
        l3 = small_f.render("3× detail", True, (236, 222, 180))
        sheet.blit(l3, (cx0, cyy))
        cyy += lab3x
        big = pygame.transform.scale(one, (crop.w * 3, crop.h * 3))
        pygame.draw.rect(sheet, (8, 5, 20),
                         (cx0 - 1, cyy - 1, crop.w * 3 + 2, crop.h * 3 + 2))
        sheet.blit(big, (cx0, cyy))

    out = os.path.join(os.path.dirname(__file__), "round_2.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
