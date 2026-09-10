"""Figure B — the eight CLASSIC/SIMPLE skulls on their own, each shown as a true
~24px chip read + an x3 zoom, tagged with its GLOBAL ID (#23..#30, the classic
block of the combined skulls_individual figure) so it cross-references Figure A.

The classic-8 are the plain-bone counterpart to new8: same draw() contract, but a
timeless simple-skull register (no horns/fangs/gems) — distinct by silhouette,
proportion and bone condition.

Run headless: SDL_VIDEODRIVER=dummy python3 docs/skull_king_stack/classic8/build_showcase.py
"""
import os, sys, importlib.util
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

HERE = os.path.dirname(os.path.abspath(__file__))

# slug, module file, chip r_frac, chip cy_frac, global ID, one-line thesis
SPEC = [
    ("round-cap",        "render_round_cap.py",        0.30, 0.46, 23, "the platonic round anchor"),
    ("egg-dome",         "render_egg_dome.py",         0.28, 0.50, 24, "tall high-domed cranium"),
    ("broad-zygo",       "render_broad_zygo.py",       0.27, 0.50, 25, "wide flaring cheekbones"),
    ("square-jaw",       "render_square_jaw.py",       0.27, 0.46, 26, "round vault over square jaw"),
    ("calvaria",         "render_calvaria.py",         0.32, 0.46, 27, "jawless, flat tooth-shelf"),
    ("gaunt-hollow",     "render_gaunt_hollow.py",     0.29, 0.48, 28, "sunken temple-waist gaunt"),
    ("child-skull",      "render_child_skull.py",      0.30, 0.48, 29, "huge vault, tiny low face"),
    ("flat-brow-robust", "render_flat_brow_robust.py", 0.30, 0.50, 30, "low flat-topped, shelf brow"),
]


def load(slug, fname):
    spec = importlib.util.spec_from_file_location("sc_" + slug.replace("-", "_"),
                                                  os.path.join(HERE, slug, fname))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def chip(draw, r_frac, cy_frac, cw=116, ch=132, ssr=6):
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * r_frac) * ssr
    sline = (int(min(cw, ch) * r_frac) / 12.0) * ssr
    draw(big, cw * ssr // 2, int(ch * ssr * cy_frac), r, sline, False)
    return sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)


cw, ch = 116, 132
cols, pad, head, lab = 4, 18, 86, 44
cellw = cw + 40                      # chip + x3 strip side-by-side
rows = 2
W = cols * cellw + (cols + 1) * pad
H = head + rows * (ch + lab + pad) + pad
sheet = pygame.Surface((W, H)); sheet.fill(sk.BG)
sheet.blit(sk.font(26).render("CLASSIC-8 skulls — the new plain/simple skulls (IDs #23–#30)", True, sk.LABEL), (pad, 16))
sheet.blit(sk.font(15).render("true ~24px chip (left) + x3 zoom · the timeless plain-bone counterpart to new8 · distinct by silhouette / proportion / condition", True, sk.LABEL_DIM), (pad, 50))

for i, (slug, fname, rf, cyf, gid, thesis) in enumerate(SPEC):
    m = load(slug, fname)
    c = chip(m.draw, rf, cyf)
    z = pygame.transform.scale(pygame.transform.smoothscale(c, (24, 27)), (24 * 3, 27 * 3))
    r_i, c_i = divmod(i, cols)
    x = pad + c_i * (cellw + pad)
    y = head + r_i * (ch + lab + pad)
    pygame.draw.rect(sheet, sk.PANEL, (x - 6, y - 6, cellw + 12, ch + 12))
    sheet.blit(c, (x, y))
    sheet.blit(z, (x + cw + 8, y + ch - 81))
    sheet.blit(sk.font(16).render(f"#{gid}  {slug}", True, sk.LABEL), (x, y + ch + 6))
    sheet.blit(sk.font(12).render(thesis, True, sk.LABEL_DIM), (x, y + ch + 26))

out = os.path.join(HERE, "showcase.png")
pygame.image.save(sheet, out)
print("WROTE", out, sheet.get_size())
