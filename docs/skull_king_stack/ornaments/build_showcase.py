"""Independent figure — the Skull-King's DECORATIVE elements on their own: the four
bead colours of her jewelry + small versions of her two cyan jewels, each shown as
a true ~24px chip + x3 zoom and tagged with its GLOBAL ID (#31..#36, the ornament
block of the combined skulls_individual figure) so it cross-references that figure.

Run headless: SDL_VIDEODRIVER=dummy python3 docs/skull_king_stack/ornaments/build_showcase.py
"""
import os, sys, importlib.util
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

HERE = os.path.dirname(os.path.abspath(__file__))

# fn name in render_ornaments, chip r_frac, global ID, label, one-line thesis
SPEC = [
    ("bead_white",        0.20, 31, "white bead",    "pale bone strand bead"),
    ("bead_gold",         0.20, 32, "gold pip",      "warm gold spacer-pip"),
    ("bead_cyan",         0.20, 33, "cyan bead",     "icy-cyan jewel bead"),
    ("bead_darkblue",     0.20, 34, "dark-blue bead", "dim brow-band cabochon"),
    ("gem_thirdeye",      0.32, 35, "third-eye gem", "small faceted cut-gem"),
    ("ornament_necklace", 0.34, 36, "necklace gem",  "small necklace ring-eye"),
]


def load():
    spec = importlib.util.spec_from_file_location("orn", os.path.join(HERE, "render_ornaments.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def chip(fn, r_frac, cw=116, ch=132, ssr=6):
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * r_frac) * ssr
    sline = (int(min(cw, ch) * r_frac) / 12.0) * ssr
    fn(big, cw * ssr // 2, ch * ssr // 2, r, sline)
    return sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)


m = load()
cw, ch = 116, 132
cols, pad, head, lab = 3, 24, 84, 48
cellw = cw + 48
rows = 2
W = cols * cellw + (cols + 1) * pad
H = head + rows * (ch + lab + pad) + pad
sheet = pygame.Surface((W, H)); sheet.fill(sk.BG)
sheet.blit(sk.font(22).render("SKULL-KING ornaments — beads + jewels", True, sk.LABEL), (pad, 14))
sheet.blit(sk.font(14).render("the design's own decorative elements, reused verbatim · true ~24px chip (left) + x3 zoom", True, sk.LABEL_DIM), (pad, 48))

for i, (fn, rf, gid, label, thesis) in enumerate(SPEC):
    c = chip(getattr(m, fn), rf)
    z = pygame.transform.scale(pygame.transform.smoothscale(c, (24, 27)), (24 * 3, 27 * 3))
    r_i, c_i = divmod(i, cols)
    x = pad + c_i * (cellw + pad)
    y = head + r_i * (ch + lab + pad)
    pygame.draw.rect(sheet, sk.PANEL, (x - 6, y - 6, cellw + 12, ch + 12))
    sheet.blit(c, (x, y))
    sheet.blit(z, (x + cw + 8, y + ch - 81))
    sheet.blit(sk.font(15).render(f"#{gid}  {label}", True, sk.LABEL), (x, y + ch + 6))
    sheet.blit(sk.font(11).render(thesis, True, sk.LABEL_DIM), (x, y + ch + 25))

out = os.path.join(HERE, "showcase.png")
pygame.image.save(sheet, out)
print("WROTE", out, sheet.get_size())
