"""Size-variant sheet for the secret-tier pickup icons (knight, poison,
skateboard). Each cell is an actual rendered gameplay frame with the
candidate pickup floating next to Pip.

Output: docs/screenshots/icon_sizes/round_1.png
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y
from game.scenes import App, STATE_PLAY
from game.entities import PowerUp
from game import poison_vial, knight_skin


SIZES = (32, 40, 48, 56, 72)
LABELS = ("KNIGHT", "POISON", "SKATEBOARD")
KINDS  = ("knight", "poison", "skateboard")

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (160, 168, 180)


# ── per-kind size-overrideable icon draw ────────────────────────────────────

def _draw_skateboard_at(surf, cx, cy, native, pulse):
    """Render the 72-px skateboard icon then smoothscale to `native`."""
    import math
    p = PowerUp(36, 36, kind="skateboard")
    p.pulse = pulse
    full = pygame.Surface((96, 96), pygame.SRCALPHA)
    p._draw_skateboard_icon(full)
    # The icon recipe in _draw_skateboard_icon currently bakes a 72×72
    # surface at the icon's own (self.x, self.y) — we made our own 96×96
    # so the natural bob/halo fits without clipping. Smoothscale the
    # used 72×72 sub-region down to the candidate native footprint.
    sub = pygame.Surface((72, 72), pygame.SRCALPHA)
    sub.blit(full, (-12, -12))
    scaled = pygame.transform.smoothscale(sub, (native, native))
    surf.blit(scaled, scaled.get_rect(center=(int(cx), int(cy + math.sin(pulse * 1.0) * 2))).topleft)


def _draw_knight_at(surf, cx, cy, native, pulse):
    import math
    knight_skin.draw_shield_icon(
        surf, int(cx), int(cy + math.sin(pulse * 0.9) * 2), size=native,
    )


def _draw_poison_at(surf, cx, cy, native, pulse):
    import math
    prev_display = poison_vial.DISPLAY_PX
    prev_cache = getattr(poison_vial, "_VIAL_CACHE", None)
    poison_vial.DISPLAY_PX = native
    poison_vial._VIAL_CACHE = None
    poison_vial.draw(surf, int(cx), int(cy + math.sin(pulse * 0.9) * 2), pulse)
    poison_vial.DISPLAY_PX = prev_display
    poison_vial._VIAL_CACHE = prev_cache


DRAWERS = {
    "knight":     _draw_knight_at,
    "poison":     _draw_poison_at,
    "skateboard": _draw_skateboard_at,
}


# ── single-frame gameplay capture ───────────────────────────────────────────

def _grab_frame(kind: str, native: int) -> pygame.Surface:
    """Spin a fresh App, set state to PLAY, place a custom-sized pickup
    next to Pip, render one frame, return the screen surface."""
    # Re-create display each call so the App's pygame.display.set_mode call
    # below picks up the size cleanly (SDL_VIDEODRIVER=dummy makes this
    # cheap, no real window).
    app = App()
    app.state = STATE_PLAY
    app.world.ready_t = 0
    # Park Pip in a stable mid-screen pose so size variants are comparable.
    app.world.bird.x = 90
    app.world.bird.y = 320
    app.world.bird.vy = 0
    # Wipe seed pipes + any auto-spawned pickups so we control the frame.
    app.world.pipes.clear()
    app.world.coins.clear()
    app.world.powerups.clear()
    # Float-text from the playtest-genie force-spawn is fine to leave.
    pickup = PowerUp(220, 320, kind=kind)
    pickup.pulse = 0.0

    # Monkey-patch this pickup's draw to use the target native size.
    drawer = DRAWERS[kind]

    def _draw(self, surf):
        drawer(surf, self.x, self.y, native, self.pulse)

    pickup.draw = _draw.__get__(pickup, PowerUp)
    app.world.powerups.append(pickup)

    # One full render pass.
    app._render()
    # Copy the surface — subsequent App() calls will steal the display.
    snap = app.screen.copy()
    return snap


# ── sheet composition ───────────────────────────────────────────────────────

CROP_X = 0
CROP_Y = 230
CROP_W = W
CROP_H = 180

CELL_W = 230
CELL_H = int(CELL_W * CROP_H / CROP_W)
PAD       = 14
LABEL_COL = 110
ROW_GAP   = 14
HEADER_H  = 78


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")

    sheet_w = (PAD * 2 + LABEL_COL
               + len(SIZES) * (CELL_W + ROW_GAP) - ROW_GAP)
    sheet_h = (HEADER_H
               + len(LABELS) * (CELL_H + ROW_GAP) - ROW_GAP
               + PAD * 2)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(22, bold=True).render(
        "Secret-tier pickup icons — gameplay screenshots",
        True, LABEL)
    sheet.blit(title, (PAD, PAD))
    sub = _font(13).render(
        "Real PlayScene frames. Pip on left, pickup at the candidate size "
        "to the right. Pick a size — applies to all three.",
        True, SUB)
    sheet.blit(sub, (PAD, PAD + 28))

    # Column headers
    for col, sz in enumerate(SIZES):
        x = PAD + LABEL_COL + col * (CELL_W + ROW_GAP) + CELL_W // 2
        h_txt = _font(14, bold=True).render(f"{sz} px", True, LABEL)
        sheet.blit(h_txt, (x - h_txt.get_width() // 2, HEADER_H - 22))

    for ri, (kind, label) in enumerate(zip(KINDS, LABELS)):
        y = HEADER_H + ri * (CELL_H + ROW_GAP)
        lbl = _font(14, bold=True).render(label, True, LABEL)
        sheet.blit(lbl, (PAD, y + (CELL_H - lbl.get_height()) // 2))
        for ci, sz in enumerate(SIZES):
            x = PAD + LABEL_COL + ci * (CELL_W + ROW_GAP)
            print(f"  rendering {kind} @ {sz} px ...")
            frame = _grab_frame(kind, sz)
            crop = frame.subsurface(
                pygame.Rect(CROP_X, CROP_Y, CROP_W, CROP_H)).copy()
            frame_sm = pygame.transform.smoothscale(
                crop, (CELL_W, CELL_H))
            sheet.blit(frame_sm, (x, y))
            pygame.draw.rect(sheet, (44, 50, 60),
                             (x, y, CELL_W, CELL_H), 1)

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
