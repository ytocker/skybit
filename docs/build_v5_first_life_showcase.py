"""
7-panel showcase: ORIGINAL · 5 first-life concepts · LAST LIFE (ace-headwrap)
Output: docs/hurt-parrot-v5-first-life/showcase.png
"""
import os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import numpy as np
import pygame
from PIL import Image, ImageDraw, ImageFont
pygame.init()

from game.config import W, H
import game.parrot as parrot

REPO      = "/home/user/skybit"
FIRST     = os.path.join(REPO, "docs", "hurt-parrot-v5-first-life")
LAST_LIFE = os.path.join(REPO, "docs", "hurt-parrot-v5-plus2", "ace-headwrap", "round_2.png")

# Sheet crop constants (must match what the agents produced)
FRAME_X0 = 20
FRAME_Y0 = 20
FRAME_W4 = 272   # 68 px × 4 frames (outlined 64+4 pad → 68)
FRAME_H4 = 256   # 64 px × 4 frames

PANEL_W = 200
PANEL_H = 355
MARGIN  = 20
GAP     = 8
HDR_H   = 44
FTR_H   = 36
BG      = (8, 8, 20)
N       = 7

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FTR_H + MARGIN

SLUGS = [
    "ruffled-feathers",
    "black-eye",
    "plucked-notch",
    "cinch-band",
    "favoured-leg",
]

ACCENTS = [
    (160, 220, 160),   # panel 1: ORIGINAL — green
    (255, 210,  80),   # ruffled-feathers — amber
    (200, 140, 255),   # black-eye — purple
    (100, 210, 255),   # plucked-notch — sky-blue
    (255, 200, 100),   # cinch-band — gold
    (120, 220, 160),   # favoured-leg — teal-green
    (255, 130,  80),   # LAST LIFE — orange
]

LABELS = [
    ("ORIGINAL",        "clean — 2 lives"),
    ("ruffled-feathers","nape spikes"),
    ("black-eye",       "bruise under lens"),
    ("plucked-notch",   "torn wing notch"),
    ("cinch-band",      "belly gauze wrap"),
    ("favoured-leg",    "tucked curled leg"),
    ("LAST LIFE",       "ace-headwrap"),
]


def _font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _crop_sheet(path):
    """Crop the hero frame (top-left) from a 4× strip sheet."""
    img = Image.open(path).convert("RGBA")
    crop = img.crop((FRAME_X0, FRAME_Y0, FRAME_X0 + FRAME_W4, FRAME_Y0 + FRAME_H4))
    return crop


def _letterbox(img, pw, ph, bg):
    """Scale img to fit pw×ph preserving aspect ratio, centred on bg."""
    iw, ih = img.size
    scale = min(pw / iw, ph / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (pw, ph), (*bg, 255))
    out.paste(resized, ((pw - nw) // 2, (ph - nh) // 2))
    return out


def _original_panel():
    """Render the clean parrot hero frame at 4× scale."""
    sprite  = parrot.get_parrot(0, 10.0)
    outlined = parrot._add_outline(sprite)
    sw, sh  = outlined.get_size()
    surf4   = pygame.transform.scale(outlined, (sw * 4, sh * 4))
    arr     = pygame.surfarray.array3d(surf4)
    alpha   = pygame.surfarray.array_alpha(surf4)
    rgba    = np.dstack([arr, alpha]).transpose(1, 0, 2)
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def main():
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (*BG, 255))
    draw   = ImageDraw.Draw(canvas)
    hdr_f  = _font(18, bold=True)
    ttl_f  = _font(15, bold=True)
    sub_f  = _font(11)

    hdr = "HURT PARROT  ·  THREE STATES  ·  CLEAN → HURT → LAST LIFE"
    bb  = draw.textbbox((0, 0), hdr, font=hdr_f)
    draw.text(((CANVAS_W - (bb[2] - bb[0])) // 2,
               MARGIN + (HDR_H - (bb[3] - bb[1])) // 2),
              hdr, font=hdr_f, fill=(255, 235, 200, 255))

    panel_top = MARGIN + HDR_H + GAP

    for idx in range(N):
        x0     = MARGIN + idx * (PANEL_W + GAP)
        accent = ACCENTS[idx]
        title, sublabel = LABELS[idx]

        if idx == 0:
            pil = _original_panel()
        elif idx <= 5:
            slug = SLUGS[idx - 1]
            pil  = _crop_sheet(os.path.join(FIRST, slug, "round_2.png"))
        else:
            pil = _crop_sheet(LAST_LIFE)

        panel = _letterbox(pil, PANEL_W, PANEL_H, BG)
        canvas.paste(panel, (x0, panel_top))

        draw.rectangle([x0 - 1, panel_top - 1, x0 + PANEL_W, panel_top + PANEL_H],
                       outline=accent, width=2)

        fy = panel_top + PANEL_H + 5
        bb = draw.textbbox((0, 0), title, font=ttl_f)
        tw = bb[2] - bb[0]
        draw.text((x0 + (PANEL_W - tw) // 2, fy), title, font=ttl_f,
                  fill=(*accent, 255))
        fy += (bb[3] - bb[1]) + 4
        bb2 = draw.textbbox((0, 0), sublabel, font=sub_f)
        draw.text((x0 + (PANEL_W - (bb2[2] - bb2[0])) // 2, fy),
                  sublabel, font=sub_f, fill=(190, 190, 210, 255))

    out_path = os.path.join(FIRST, "showcase.png")
    canvas.save(out_path)
    print(f"Saved {CANVAS_W}x{CANVAS_H} -> {out_path}")

    # Sanity check: no blank panels
    arr_full = np.array(canvas)
    for idx in range(N):
        x0     = MARGIN + idx * (PANEL_W + GAP)
        region = arr_full[panel_top:panel_top + PANEL_H, x0:x0 + PANEL_W, :3]
        count  = int(np.any(region != np.array(BG), axis=2).sum())
        print(f"  panel {idx + 1} ({LABELS[idx][0]}): {count} non-bg px")
        assert count > 500, f"panel {idx+1} appears blank: {count}"
    print("All panels populated.")


if __name__ == "__main__":
    main()
