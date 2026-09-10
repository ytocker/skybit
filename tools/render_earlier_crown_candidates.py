"""Decision-aid render (Stage A): show the EARLIER, single-design crown skull
(the 'skulls above the head') as it looked at each round BEFORE the high-variance
idx-table rework, so the look can be chosen by eye rather than by round id.

The crown skull was one uniform design (no idx) from round 1 through round 9 of
the mukha 'asthi_dakini' line; variance arrived at round 10. Its code changed
across six single-design rounds. Each historical render script is fully
self-contained (own palette + helpers + crown_skull) and import-safe, so we lift
each version out of git, import it under a unique name, and render its own
crown_skull faithfully (period-correct palette and all).
"""
import os, sys, math, subprocess, tempfile, importlib.util

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = "docs/skybit_devil/batch2/mukha_citipati_court/asthi_dakini/render_asthi_dakini.py"
OUT = os.path.join(ROOT, "docs/skull_king_stack")
os.makedirs(OUT, exist_ok=True)

# (round label, commit, one-line note from the commit subject) — single-design
# rounds only; round 10 (variance) is deliberately excluded.
ROUNDS = [
    ("round 1", "339cc6d", "original mukha-citipati crown skull"),
    ("round 2", "a252bbb", "value ladder, tiara-band, warm face anchor"),
    ("round 3", "4b5c753", "dim crown-centre glow; third-eye wins ladder"),
    ("round 7", "32c8e89", "rebuild from round-1; blue auras removed"),
    ("round 8", "87644e7", "warm Citipati bone skin; crown re-tuned"),
    ("round 9", "4989d9a", "bone-jewel: cyan cabochon inlay + crown echo"),
]


def _load_round(commit):
    """Pull this commit's whole render script out of git and import it under a
    unique module name (each file is literally named render_asthi_dakini, so a
    plain import would collide / get cached)."""
    src = subprocess.check_output(["git", "show", f"{commit}:{HIST}"], cwd=ROOT)
    tmp = tempfile.NamedTemporaryFile(prefix=f"crown_{commit}_", suffix=".py",
                                      delete=False, dir=tempfile.gettempdir())
    tmp.write(src)
    tmp.close()
    name = f"asthi_hist_{commit}"
    spec = importlib.util.spec_from_file_location(name, tmp.name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _chip(mod, cell_w, cell_h, *, lit):
    """One round's crown skull on transparent ground — mirrors the existing
    figure's chip pipeline (ssr supersample → smoothscale → 1px ink outline)."""
    ssr = 6
    big = pygame.Surface((cell_w * ssr, cell_h * ssr), pygame.SRCALPHA)
    r = int(min(cell_w, cell_h) * 0.40)
    rb = r * ssr
    s = (r / 12.0) * ssr
    cx = cell_w * ssr // 2
    cy = int(cell_h * ssr * 0.52)
    mod.crown_skull(big, cx, cy, rb, s, lit=lit)
    small = pygame.transform.smoothscale(big, (cell_w, cell_h))
    return mod.grow_outline(small, mod.INK + (255,), 1)


def _label(surf, text, x, y, col=(235, 230, 222), size=15):
    f = pygame.font.SysFont("DejaVu Sans", size, bold=True)
    surf.blit(f.render(text, True, (20, 16, 22)), (x + 1, y + 1))
    surf.blit(f.render(text, True, col), (x, y))


def build():
    cw, ch = 120, 134
    pad = 16
    head = 92
    rowlab = 22
    cols = len(ROUNDS)
    W = cols * cw + (cols + 1) * pad
    stride = rowlab + ch + 104     # room for the wrapped note block under row 1
    # two chip rows (resting + lit focal) + a per-round note line beneath
    H = head + 2 * stride + 16
    sheet = pygame.Surface((W, H))
    BG = (92, 96, 108)
    sheet.fill(BG)
    _label(sheet, "EARLIER crown skull (the 'skulls above the head') — single uniform design, by round", pad, 18)
    _label(sheet, "source: mukha-citipati asthi_dakini, pre-variance (round 1-9). Pick the look you mean.", pad, 46,
           col=(190, 198, 212))

    mods = {label: _load_round(commit) for label, commit, _ in ROUNDS}

    for ri, lit in enumerate((False, True)):
        y = head + ri * stride
        tag = "RESTING (the design that fills the crown arc)" if not lit else "LIT centre-focal variant (eye glow / pip)"
        _label(sheet, tag, pad, y)
        y += rowlab
        x = pad
        for label, commit, note in ROUNDS:
            chip = _chip(mods[label], cw, ch, lit=lit)
            sheet.blit(chip, (x, y))
            _label(sheet, label, x + 6, y + ch + 2)
            if not lit:
                # wrap the note under the round label on the first row only
                words, line, ly = note.split(), "", y + ch + 22
                for w in words:
                    if len(line) + len(w) + 1 > 14:
                        _label(sheet, line, x + 6, ly, col=(186, 192, 206))
                        ly += 16
                        line = w
                    else:
                        line = (line + " " + w).strip()
                if line:
                    _label(sheet, line, x + 6, ly, col=(186, 192, 206))
            x += cw + pad

    out = os.path.join(OUT, "earlier_crown_candidates.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


def build_versions():
    """The WHOLE king-skull (full Asthi-Dakini figure) for each pre-variance
    round, side by side — so the version can be recognised in full context, not
    just by the isolated crown skull. Each round's own draw_asthi_dakini is used,
    so body, beadwork, crown and palette are all period-correct."""
    cw, ch = 330, 408
    pad = 16
    head = 92
    cols = len(ROUNDS)
    W = cols * cw + (cols + 1) * pad
    H = head + ch + 56
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 50, 66))
    _label(sheet, "EARLIER king skull (full Asthi-Dakini) — the whole design at each pre-variance round", pad, 18)
    _label(sheet, "source: mukha-citipati asthi_dakini, round 1-9. The crown skulls sit in the arc above each head.", pad, 46,
           col=(190, 198, 212))

    x = pad
    y = head
    for label, commit, note in ROUNDS:
        mod = _load_round(commit)
        # cell backdrop gradient, then the figure centred in it
        cell = pygame.Surface((cw, ch))
        for j in range(ch):
            cell.fill(mod.lerp((74, 84, 104), (40, 46, 64), j / max(1, ch - 1)), (0, j, cw, 1))
        fig = mod.render_creature_chip(cw, ch, cw // 2, int(ch * 0.53), 1.78)
        cell.blit(fig, (0, 0))
        sheet.blit(cell, (x, y))
        _label(sheet, f"{label}  —  {note}", x + 4, y + ch + 6) if len(f"{label}  —  {note}") < 40 else _label(sheet, label, x + 4, y + ch + 6)
        x += cw + pad

    out = os.path.join(OUT, "earlier_king_skull_versions.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


def build_offered():
    """Just the four offered versions (rounds 1, 7, 8, 9) rendered LARGE, so each
    full skull-king design reads clearly side by side."""
    offered = [r for r in ROUNDS if r[0] in ("round 1", "round 7", "round 8", "round 9")]
    cw, ch = 460, 600
    pad = 22
    head = 100
    cols = len(offered)
    W = cols * cw + (cols + 1) * pad
    H = head + ch + 64
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 50, 66))
    _label(sheet, "Full skull-king designs — the four versions offered", pad, 20, size=30)
    _label(sheet, "complete Asthi-Dakini figure, each rendered with its own round's code + palette", pad, 58,
           col=(190, 198, 212))

    x = pad
    y = head
    for label, commit, note in offered:
        mod = _load_round(commit)
        cell = pygame.Surface((cw, ch))
        for j in range(ch):
            cell.fill(mod.lerp((74, 84, 104), (40, 46, 64), j / max(1, ch - 1)), (0, j, cw, 1))
        fig = mod.render_creature_chip(cw, ch, cw // 2, int(ch * 0.53), 2.5)
        cell.blit(fig, (0, 0))
        sheet.blit(cell, (x, y))
        _label(sheet, label, x + 6, y + ch + 8, size=22)
        _label(sheet, note, x + 6, y + ch + 36, col=(190, 198, 212))
        x += cw + pad

    out = os.path.join(OUT, "offered_king_skull_versions.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    build()
    build_versions()
    build_offered()

