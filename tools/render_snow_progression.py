"""ONE clean figure: Pip, snow accumulating step by step until fully covered.

Deliberately simple — no snowman, no whiteout, no side-by-side directions. Just
the parrot and a left-to-right ramp of increasing snow. The first three frames
are the REAL shipped `Bird.draw` accumulation (clean -> today's in-game max,
face still readable); the last three continue PAST today's max via the same W2
snow mound until Pip is fully buried in snow.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_progression
Output: docs/snow_full_cover/progression.png
"""
from __future__ import annotations

import os

import pygame

import tools.render_snow_fullcover as T

OUT = os.path.join(T.ROOT, "docs", "snow_full_cover", "progression.png")

# (builder, arg, caption). One monotonic ramp, no face. A clean bird, a light
# shipped dusting, then the SAME W2 snow mound deepening until Pip is buried.
# Mound steps are weighted toward the high end where most of the visible change
# happens (the face/body only disappear past ~0.5), so each step reads distinct.
STEPS = [
    (T.render_reference, 0.00, "clean"),
    (T.render_reference, 0.30, "dusting"),
    (T.render_cell, 0.15, "blanket"),
    (T.render_cell, 0.50, "settling"),
    (T.render_cell, 0.72, "half buried"),
    (T.render_cell, 0.88, "almost gone"),
    (T.render_cell, 1.00, "fully covered"),
]


def main():
    cells = [(b(a)[0], cap) for (b, a, cap) in STEPS]
    cw, ch = cells[0][0].get_size()

    gap = 26
    mtop, mbot, mside = 84, 46, gap
    cap_h = 30
    W = mside * 2 + len(cells) * cw + (len(cells) - 1) * gap
    H = mtop + ch + cap_h + mbot

    sheet = T.make_gradient_surface(
        W, H, [(0.0, (30, 35, 47)), (1.0, (19, 22, 31))])

    f_title = pygame.font.SysFont("Arial", 30, bold=True)
    f_sub = pygame.font.SysFont("Arial", 17)
    f_cap = pygame.font.SysFont("Arial", 18, bold=True)
    f_num = pygame.font.SysFont("Arial", 14, bold=True)

    sheet.blit(f_title.render(
        "Pip — snow build-up to full cover", True, (240, 244, 252)), (mside, 22))
    sheet.blit(f_sub.render(
        "left → right: snow builds up on Pip until he is fully covered.",
        True, (150, 164, 188)), (mside, 56))

    x = mside
    cy = mtop
    for i, (cell, cap) in enumerate(cells):
        panel = T.neutral_panel(cw, ch)
        # subtle frame
        pygame.draw.rect(panel, (60, 70, 90), panel.get_rect(), 1)
        panel.blit(cell, (0, 0))
        sheet.blit(panel, (x, cy))
        # number chip top-left of each frame
        sheet.blit(f_num.render(str(i + 1), True, (120, 200, 255)), (x + 8, cy + 6))
        # caption centered under the frame
        cs = f_cap.render(cap, True, (224, 232, 244))
        sheet.blit(cs, (x + cw // 2 - cs.get_width() // 2, cy + ch + 8))
        # arrow between frames
        if i < len(cells) - 1:
            ax = x + cw + gap // 2
            ay = cy + ch // 2
            pygame.draw.polygon(sheet, (90, 104, 130),
                                [(ax - 5, ay - 6), (ax + 5, ay), (ax - 5, ay + 6)])
        x += cw + gap

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print(f"saved {OUT}  ({W}x{H})")


if __name__ == "__main__":
    main()
