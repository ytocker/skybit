"""Before/after comparison of the RUN SUMMARY screen — original layout vs.
the shipped N2 layout (3-row power-up strip + bold header-rule caption) —
across short (1-row), medium (2-row) and long (3-row) runs.

Both sides are rendered by the REAL ``HUD.draw_stats`` of their respective
code versions, so this is a faithful capture, not a re-draw. Producing the
two input dirs (run from the repo root):

    # AFTER — the current working tree (live N2):
    PYTHONPATH=. python /tmp/render_cases.py /tmp/after

    # BEFORE — a detached worktree at the commit before N2 landed:
    git worktree add --detach /tmp/sb_before <pre-N2-commit>
    (cd /tmp/sb_before && PYTHONPATH=. python /tmp/render_cases.py /tmp/before)

where render_cases.py renders {1row,2row,3row}.png at 360x640 by calling
``HUD.draw_stats`` against a mock world (score 137, best 842, 1:27, 41
coins/62%, 33 pillars, 211 flaps; 3 / 8 / 15 distinct power-ups).

Then compose the single sheet:

    python tools/gen_summary_before_after.py /tmp/before /tmp/after \\
        docs/run_summary_3row/before_after.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from game.hud import _font, _GOLD_BRIGHT, _GOLD_MUTED  # noqa: E402

PW, PH = 360, 640
CASES = [("3row", "LONG RUN · 3-ROW"),
         ("2row", "MEDIUM RUN · 2-ROW"),
         ("1row", "SHORT RUN · 1-ROW")]
# Per-cell mode tag shown beneath each panel, so the conditional layout
# switch is verifiable at a glance. Column 0 = BEFORE, column 1 = AFTER.
MODE = {
    (0, "1row"): "original layout",
    (0, "2row"): "original layout",
    (0, "3row"): "original — overflows (2-row max)",
    (1, "1row"): "original layout + new caption",
    (1, "2row"): "original layout + new caption",
    (1, "3row"): "N2 compact (3 rows fit)",
}


def main(before_dir, after_dir, out_path):
    pad, label_h, tag_h, head_h, cols = 18, 34, 26, 52, 2
    rows = len(CASES)
    sheet_w = cols * PW + (cols + 1) * pad
    sheet_h = head_h + rows * (PH + label_h + tag_h) + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 6, 20))

    # Column headers
    hf = _font(20, True)
    for ci, htext in enumerate(("BEFORE  (original)",
                                "AFTER  (conditional)")):
        cx = pad + ci * (PW + pad) + PW // 2
        col = _GOLD_MUTED if ci == 0 else _GOLD_BRIGHT
        img = hf.render(htext, True, col)
        sheet.blit(img, img.get_rect(center=(cx, head_h // 2 + 4)))

    lf = _font(14, True)
    tf = _font(12, True)
    for ri, (case, label) in enumerate(CASES):
        y0 = head_h + pad + ri * (PH + label_h + tag_h + pad)
        for ci, src in enumerate((before_dir, after_dir)):
            x0 = pad + ci * (PW + pad)
            panel = pygame.image.load(os.path.join(src, f"{case}.png"))
            cap = lf.render(label, True, _GOLD_BRIGHT)
            sheet.blit(cap, cap.get_rect(center=(x0 + PW // 2,
                                                 y0 + label_h // 2)))
            sheet.blit(panel, (x0, y0 + label_h))
            pygame.draw.rect(sheet, (60, 44, 96),
                             (x0, y0 + label_h, PW, PH), 1)
            tag = tf.render(MODE[(ci, case)], True, _GOLD_MUTED)
            sheet.blit(tag, tag.get_rect(
                center=(x0 + PW // 2, y0 + label_h + PH + tag_h // 2)))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
