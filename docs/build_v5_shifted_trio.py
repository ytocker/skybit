"""
6-panel comparison: ORIGINAL · bandaged-cheek · field-dressed · gauze-gorget · splinted-tail · belly-strapped
Output: docs/hurt-parrot-v5-shifted-showcase.png
Separator lines after panels 1 and 3 mark the existing/new boundary.
"""
import importlib.util, os, sys
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

import numpy as np
import pygame
from PIL import Image, ImageDraw, ImageFont
pygame.init()

REPO     = "/home/user/skybit"
SCALE    = 8
SPRITE_W = 68
SPRITE_H = 64
PANEL_W  = SPRITE_W * SCALE   # 544
PANEL_H  = SPRITE_H * SCALE   # 512
GAP      = 12
MARGIN   = 20
HDR_H    = 60
FTR_H    = 80
BG       = (8, 8, 20)

N_PANELS = 7
CANVAS_W = MARGIN + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FTR_H + MARGIN


def _add_outline(src, outline_color=(20, 12, 18, 220)):
    pad = 2
    w, h = src.get_size()
    mask = pygame.mask.from_surface(src, threshold=8)
    sil  = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    out  = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _load_module(path):
    spec = importlib.util.spec_from_file_location("design", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _surf_to_pil(surf):
    arr   = pygame.surfarray.array3d(surf)
    alpha = pygame.surfarray.array_alpha(surf)
    return Image.fromarray(np.dstack([arr, alpha]).transpose(1, 0, 2), "RGBA")


def _panel_image(outlined_surf):
    scaled = pygame.transform.scale(outlined_surf, (PANEL_W, PANEL_H))
    return _surf_to_pil(scaled)


def _get_original():
    import game.parrot as p
    return _add_outline(p._build_frame(10))


def _get_v5(slug):
    mod = _load_module(f"{REPO}/docs/hurt-parrot-v5/{slug}/design.py")
    return _add_outline(mod._build_hurt_frame(10))


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


PANELS = [
    ("original",       "ORIGINAL",            _get_original,                         (140, 200, 140), ""),
    ("bandaged-cheek", "bandaged-\ncheek",     lambda: _get_v5("bandaged-cheek"),     (255, 210,  80), "V5"),
    ("field-dressed",  "field-\ndressed",      lambda: _get_v5("field-dressed"),      (255, 210,  80), "V5"),
    ("gauze-gorget",   "gauze-\ngorget",       lambda: _get_v5("gauze-gorget"),       (100, 200, 255), "V5 NEW"),
    ("splinted-tail",  "splinted-\ntail",      lambda: _get_v5("splinted-tail"),      (100, 200, 255), "V5 NEW"),
    ("belly-strapped",      "belly-\nstrapped",      lambda: _get_v5("belly-strapped"),      (100, 200, 255), "V5 NEW"),
    ("field-dressed-plus",  "field-dressed-\nplus",  lambda: _get_v5("field-dressed-plus"),  (255, 210,  80), "V5"),
]

# Separator after panel index 0 (after ORIGINAL) and after panel index 2 (after field-dressed)
SEPARATORS = {0, 2}


def main():
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (*BG, 255))
    draw   = ImageDraw.Draw(canvas)

    hdr_font  = _font(22, bold=True)
    id_font   = _font(24, bold=True)
    slug_font = _font(18, bold=False)
    sub_font  = _font(13, bold=False)

    title = "HURT PARROT · LAST LIFE · ORIGINAL · EXISTING V5 · NEW SHIFTED CONCEPTS"
    bbox  = draw.textbbox((0, 0), title, font=hdr_font)
    draw.text(((CANVAS_W - (bbox[2] - bbox[0])) // 2,
               MARGIN + (HDR_H - (bbox[3] - bbox[1])) // 2),
              title, font=hdr_font, fill=(255, 235, 200, 255))

    panel_top = MARGIN + HDR_H + GAP

    for idx, (key, label, loader, name_color, version_tag) in enumerate(PANELS):
        x0 = MARGIN + idx * (PANEL_W + GAP)

        outlined  = loader()
        pil_panel = _panel_image(outlined)
        cell = Image.new("RGBA", (PANEL_W, PANEL_H), (*BG, 255))
        cell.paste(pil_panel, (0, 0), pil_panel)
        canvas.paste(cell, (x0, panel_top))

        # Separator lines after panels 0 and 2 (marking existing/new boundary)
        if idx in SEPARATORS:
            lx = x0 + PANEL_W + GAP // 2
            draw.line([(lx, panel_top - 4), (lx, panel_top + PANEL_H + 4)],
                      fill=(180, 80, 220, 220), width=3)

        id_label = str(idx + 1)
        id_bb    = draw.textbbox((0, 0), id_label, font=id_font)
        id_w, id_h = id_bb[2] - id_bb[0], id_bb[3] - id_bb[1]
        id_y = panel_top + PANEL_H + 6
        draw.text((x0 + (PANEL_W - id_w) // 2, id_y),
                  id_label, font=id_font, fill=(220, 220, 240, 255))

        slug_y = id_y + id_h + 6
        lines  = label.split("\n")
        line_h = slug_font.size + 2
        for li, ln in enumerate(lines):
            bb = draw.textbbox((0, 0), ln, font=slug_font)
            draw.text((x0 + (PANEL_W - (bb[2] - bb[0])) // 2, slug_y + li * line_h),
                      ln, font=slug_font, fill=(*name_color, 255))

        tag_y = slug_y + len(lines) * line_h + 2
        if version_tag:
            bb3 = draw.textbbox((0, 0), version_tag, font=sub_font)
            draw.text((x0 + (PANEL_W - (bb3[2] - bb3[0])) // 2, tag_y),
                      version_tag, font=sub_font, fill=(120, 120, 150, 255))

    out_path = os.path.join(REPO, "docs", "hurt-parrot-v5-shifted-showcase.png")
    canvas.save(out_path)
    print(f"Saved {CANVAS_W}x{CANVAS_H} -> {out_path}")

    for idx, (key, _, _, _, _) in enumerate(PANELS):
        x0     = MARGIN + idx * (PANEL_W + GAP)
        region = canvas.crop((x0, panel_top, x0 + PANEL_W, panel_top + PANEL_H))
        count  = int(np.any(np.array(region)[:, :, :3] != np.array(BG), axis=2).sum())
        print(f"  panel {idx+1} ({key}): {count} non-bg pixels  [{'OK' if count > 200 else 'BLANK'}]")

    assert all(
        int(np.any(
            np.array(canvas.crop((MARGIN + i * (PANEL_W + GAP), panel_top,
                                  MARGIN + i * (PANEL_W + GAP) + PANEL_W,
                                  panel_top + PANEL_H)))[:, :, :3]
            != np.array(BG), axis=2
        ).sum()) > 200
        for i in range(N_PANELS)
    ), "One or more panels appear blank"

    print("All panels populated. Done.")


if __name__ == "__main__":
    main()
