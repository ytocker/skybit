"""
3-panel progression: ORIGINAL · FIRST HIT · LAST LIFE
Renders the three parrot damage states side by side at 4× scale.
Output: docs/hurt-parrot-v5-first-life/first-hit-comparison.png
"""
import importlib.util, os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import numpy as np
import pygame
from PIL import Image, ImageDraw, ImageFont
pygame.init()

import game.parrot as parrot

REPO      = "/home/user/skybit"
FIRST_HIT = os.path.join(REPO, "docs", "hurt-parrot-v5-first-life", "first-hit", "design.py")
LAST_LIFE = os.path.join(REPO, "docs", "hurt-parrot-v5-plus2", "ace-headwrap", "round_2.png")

# Sheet crop: 4× hero frame (top-left of the filmstrip)
FRAME_X0, FRAME_Y0 = 20, 20
FRAME_W4, FRAME_H4 = 272, 256   # 68×4, 64×4

PANEL_W = 220
PANEL_H = 390
MARGIN  = 28
GAP     = 20
HDR_H   = 54
FTR_H   = 56
BG      = (8, 8, 20)
N       = 3

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FTR_H + MARGIN

PANELS = [
    # (title, sublabel, accent)
    ("ORIGINAL",   "2 lives · clean",            (160, 220, 160)),
    ("FIRST HIT",  "1 life · bandaids + 1 crack", (255, 210,  80)),
    ("LAST LIFE",  "0 lives · full ace-headwrap", (255, 130,  80)),
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
    img  = Image.open(path).convert("RGBA")
    return img.crop((FRAME_X0, FRAME_Y0, FRAME_X0 + FRAME_W4, FRAME_Y0 + FRAME_H4))


def _letterbox(img, pw, ph):
    iw, ih = img.size
    scale  = min(pw / iw, ph / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (pw, ph), (*BG, 255))
    out.paste(resized, ((pw - nw) // 2, (ph - nh) // 2))
    return out


def _sprite_to_pil_4x(sprite):
    outlined = parrot._add_outline(sprite)
    sw, sh   = outlined.get_size()
    surf4    = pygame.transform.scale(outlined, (sw * 4, sh * 4))
    arr      = pygame.surfarray.array3d(surf4)
    alpha    = pygame.surfarray.array_alpha(surf4)
    rgba     = np.dstack([arr, alpha]).transpose(1, 0, 2)
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def _load_design(path):
    spec = importlib.util.spec_from_file_location("fh_design", path)
    m    = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    fh_mod = _load_design(FIRST_HIT)

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (*BG, 255))
    draw   = ImageDraw.Draw(canvas)
    hdr_f  = _font(20, bold=True)
    ttl_f  = _font(17, bold=True)
    sub_f  = _font(13)

    hdr = "HURT PARROT  ·  DAMAGE PROGRESSION"
    bb  = draw.textbbox((0, 0), hdr, font=hdr_f)
    draw.text(((CANVAS_W - (bb[2] - bb[0])) // 2,
               MARGIN + (HDR_H - (bb[3] - bb[1])) // 2),
              hdr, font=hdr_f, fill=(255, 245, 220, 255))

    panel_top = MARGIN + HDR_H + GAP

    for idx, (title, sublabel, accent) in enumerate(PANELS):
        x0 = MARGIN + idx * (PANEL_W + GAP)

        if idx == 0:
            pil = _sprite_to_pil_4x(parrot.get_parrot(0, 10.0))
        elif idx == 1:
            frame = fh_mod._build_hurt_frame(10)
            outlined = fh_mod._add_outline(frame)
            sw, sh = outlined.get_size()
            surf4  = pygame.transform.scale(outlined, (sw * 4, sh * 4))
            arr    = pygame.surfarray.array3d(surf4)
            alpha  = pygame.surfarray.array_alpha(surf4)
            rgba   = np.dstack([arr, alpha]).transpose(1, 0, 2)
            pil    = Image.fromarray(rgba.astype(np.uint8), "RGBA")
        else:
            pil = _crop_sheet(LAST_LIFE)

        panel = _letterbox(pil, PANEL_W, PANEL_H)
        canvas.paste(panel, (x0, panel_top))

        draw.rectangle([x0 - 1, panel_top - 1, x0 + PANEL_W, panel_top + PANEL_H],
                       outline=accent, width=2)

        fy = panel_top + PANEL_H + 8
        bb = draw.textbbox((0, 0), title, font=ttl_f)
        tw = bb[2] - bb[0]
        draw.text((x0 + (PANEL_W - tw) // 2, fy), title, font=ttl_f,
                  fill=(*accent, 255))
        fy += (bb[3] - bb[1]) + 6
        bb2 = draw.textbbox((0, 0), sublabel, font=sub_f)
        draw.text((x0 + (PANEL_W - (bb2[2] - bb2[0])) // 2, fy),
                  sublabel, font=sub_f, fill=(200, 200, 220, 255))

    out_path = os.path.join(REPO, "docs", "hurt-parrot-v5-first-life",
                            "first-hit-comparison.png")
    canvas.save(out_path)
    print(f"Saved {CANVAS_W}x{CANVAS_H} -> {out_path}")

    arr_full = np.array(canvas)
    for idx, (title, _, _) in enumerate(PANELS):
        x0  = MARGIN + idx * (PANEL_W + GAP)
        reg = arr_full[panel_top:panel_top + PANEL_H, x0:x0 + PANEL_W, :3]
        cnt = int(np.any(reg != np.array(BG), axis=2).sum())
        print(f"  panel {idx+1} ({title}): {cnt} non-bg px")
        assert cnt > 500, f"panel {idx+1} blank"
    print("Done.")


if __name__ == "__main__":
    main()
