"""
Render round_2.png for all 5 first-life hurt concepts.
Each round 2 is the round 1 design plus targeted polish:
  ruffled-feathers — bright edge-glint line on long spike tip
  black-eye        — outer bruise ring +1 px; brighter highlight catch
  plucked-notch    — shaft line on the loose feather for feather barb read
  cinch-band       — stitch dots on both hem edges (not just top)
  favoured-leg     — talon glint on trailing leg tip for visual anchor
"""
import importlib.util, os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
import numpy as np

FIRST_LIFE = "/home/user/skybit/docs/hurt-parrot-v5-first-life"
HURT_ANGLES = (10, -5, -20, -35)


def _load(slug):
    path = os.path.join(FIRST_LIFE, slug, "design.py")
    spec = importlib.util.spec_from_file_location("design_" + slug.replace("-", "_"), path)
    m    = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _strip(frames, scale, gap, bg):
    fw, fh = frames[0].get_size()
    w = len(frames) * fw * scale + (len(frames) - 1) * gap
    s = pygame.Surface((int(w), int(fh * scale)))
    s.fill(bg)
    for i, f in enumerate(frames):
        s.blit(pygame.transform.scale(f, (int(fw * scale), int(fh * scale))),
               (i * (int(fw * scale) + gap), 0))
    return s


def _save(canvas_surf, slug):
    out = os.path.join(FIRST_LIFE, slug, "round_2.png")
    pygame.image.save(canvas_surf, out)
    w, h = canvas_surf.get_size()
    print(f"  {slug}: saved {w}x{h} -> {out}")
    return out


def _layout(frames, label_text, slug):
    """Standard sheet layout matching round_1 sheets."""
    NIGHT, DAY = (8, 8, 20), (100, 160, 220)
    margin, gap = 20, 10
    row1  = _strip(frames, 4, gap, NIGHT)
    row2  = _strip(frames, 2, gap, NIGHT)
    row3a = _strip(frames, 1, gap, DAY)
    row3b = _strip(frames, 1, gap, (5, 8, 30))
    label_h, pad3 = 30, 12
    cw = margin * 2 + max(row1.get_width(), row2.get_width())
    ch = (margin + row1.get_height() + gap + row2.get_height() + gap
          + row3a.get_height() + pad3 * 2 + label_h + margin)
    canvas = pygame.Surface((cw, ch))
    canvas.fill(NIGHT)
    canvas.blit(row1, (margin, margin))
    y = margin + row1.get_height() + gap
    canvas.blit(row2, (margin, y))
    y += row2.get_height() + gap
    for i, (panel, bg) in enumerate(((row3a, DAY), (row3b, (5, 8, 30)))):
        px = margin + i * (panel.get_width() + pad3 * 2 + gap * 2)
        pygame.draw.rect(canvas, bg, (px, y, panel.get_width() + pad3 * 2,
                                      panel.get_height() + pad3 * 2))
        canvas.blit(panel, (px + pad3, y + pad3))
    y += row3a.get_height() + pad3 * 2
    try:
        font  = pygame.font.SysFont("dejavusans", 17)
        small = pygame.font.SysFont("dejavusans", 12)
    except Exception:
        font = small = pygame.font.Font(None, 17)
    canvas.blit(small.render("1x on day sky", True, (10, 20, 40)),
                (margin + pad3, y - pad3 + 1))
    canvas.blit(small.render("1x on night sky", True, (200, 205, 230)),
                (margin + row3a.get_width() + pad3 * 3 + gap * 2, y - pad3 + 1))
    lbl = font.render(label_text, True, (225, 225, 245))
    canvas.blit(lbl, (margin, ch - margin - lbl.get_height() + 4))
    return canvas


# ── 1. ruffled-feathers ──────────────────────────────────────────────────────
def _render_ruffled():
    m = _load("ruffled-feathers")

    SPIKE_HL = (245, 160, 160)  # warm light on the raised tip — not pure white

    def _build_r2(angle):
        surf = m._build_frame(angle)
        # Edge-glint: 1 px bright line along the outer left face of the long spike.
        # Drawn after the head so it reads on top of the dark ellipse boundary.
        pygame.draw.line(surf, SPIKE_HL, (36, 13), (39, 20), 1)
        return surf

    raw    = [_build_r2(a) for a in HURT_ANGLES]
    frames = [m._add_outline(f) for f in raw]
    canvas = _layout(frames, "ruffled-feathers — round 2   (4x / 2x / 1x day + night)",
                     "ruffled-feathers")
    _save(canvas, "ruffled-feathers")


# ── 2. black-eye ─────────────────────────────────────────────────────────────
def _render_black_eye():
    m = _load("black-eye")

    BRUISE_OUTER = (165, 90, 140)   # one step cooler/darker than round-1 outer ring
    HL_BRIGHT    = (220, 200, 215)  # brighter highlight catch

    def _build_r2(angle, hurt=True):
        surf = m._build_frame(angle, hurt=hurt)
        if hurt:
            # Replace the outer bruise ring with a slightly larger, higher-contrast version
            pygame.draw.ellipse(surf, BRUISE_OUTER, (37, 26, 12, 8))
            # Brighter 3 px highlight catch on upper-left rim
            pygame.draw.line(surf, HL_BRIGHT, (39, 27), (41, 27), 1)
            pygame.draw.line(surf, HL_BRIGHT, (39, 28), (40, 28), 1)
        return surf

    raw    = [_build_r2(a, hurt=True) for a in HURT_ANGLES]
    frames = [m._add_outline(f) for f in raw]
    canvas = _layout(frames, "black-eye — round 2   (4x / 2x / 1x day + night)",
                     "black-eye")
    _save(canvas, "black-eye")


# ── 3. plucked-notch ─────────────────────────────────────────────────────────
def _render_plucked():
    m = _load("plucked-notch")
    FEATHER_SHAFT = (175, 22, 22)   # darker central shaft reads as feather vane

    def _build_r2(angle, frame_index=0):
        surf = m._build_hurt_frame(angle, frame_index)
        # Center shaft line on the loose feather — barb structure at 4x
        fy = 12 + m.FEATHER_BOB[frame_index % 4]
        pygame.draw.line(surf, FEATHER_SHAFT, (6, fy + 1), (10, fy + 4), 1)
        return surf

    raw    = [_build_r2(a, i) for i, a in enumerate(HURT_ANGLES)]
    frames = [m._add_outline(f) for f in raw]
    canvas = _layout(frames, "plucked-notch — round 2   (4x / 2x / 1x day + night)",
                     "plucked-notch")
    _save(canvas, "plucked-notch")


# ── 4. cinch-band ────────────────────────────────────────────────────────────
def _render_cinch():
    m = _load("cinch-band")

    STITCH = m.STITCH
    GAUZE  = m.GAUZE

    def _build_r2(angle):
        surf = m._build_hurt_frame(angle)
        # Stitch dots on bottom hem as well as top — mirrors the existing top row
        for x in range(18, 39, 4):
            pygame.draw.circle(surf, STITCH, (x, 42), 1)
        # Small shine on the knot lump for cloth read
        pygame.draw.circle(surf, (220, 212, 195), (17, 39), 1)
        return surf

    raw    = [_build_r2(a) for a in HURT_ANGLES]
    frames = [m._add_outline(f) for f in raw]
    canvas = _layout(frames, "cinch-band — round 2   (4x / 2x / 1x day + night)",
                     "cinch-band")
    _save(canvas, "cinch-band")


# ── 5. favoured-leg ──────────────────────────────────────────────────────────
def _render_favoured():
    m = _load("favoured-leg")
    TALON_HL = (200, 160, 40)   # warm yellow-orange talon glint

    def _build_r2(angle):
        surf = m._build_hurt_frame(angle)
        # 1-px glint on trailing leg tip to anchor the eye at 1x
        pygame.draw.circle(surf, TALON_HL, (36, 52), 1)
        # Extra stitch emphasis: 2nd tick parallel to the existing one
        pygame.draw.line(surf, m.STITCH, (27, 45), (30, 45), 1)
        return surf

    raw    = [_build_r2(a) for a in HURT_ANGLES]
    frames = [m._add_outline(f) for f in raw]
    canvas = _layout(frames, "favoured-leg — round 2   (4x / 2x / 1x day + night)",
                     "favoured-leg")
    _save(canvas, "favoured-leg")


if __name__ == "__main__":
    print("Rendering round 2 sheets …")
    _render_ruffled()
    _render_black_eye()
    _render_plucked()
    _render_cinch()
    _render_favoured()
    print("Done.")
