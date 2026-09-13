import os, sys, importlib.util
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

HERE = os.path.dirname(os.path.abspath(__file__))

# slug -> (module file, draw chip params: r_frac, cy_frac) — the per-skull cell
# placement so appendage-heavy skulls fit the 116x132 chip without clipping.
SPEC = [
    ("horned-ram",     "render_horned_ram.py",      0.26, 0.50, "WILD"),
    ("antler-stag",    "render_antler_stag.py",     0.33, 0.66, "WILD"),
    ("sabertooth-maw", "render_sabertooth_maw.py",  0.34, 0.34, "WILD"),
    ("cyclops-brow",   "render_cyclops_brow.py",    0.40, 0.52, "WILD"),
    ("longjaw-relic",  "render_longjaw_relic.py",   0.40, 0.30, "RELIC"),
    ("cracked-half",   "render_cracked_half.py",    0.40, 0.52, "RELIC"),
    ("flat-slab",      "render_flat_slab.py",       0.40, 0.52, "RELIC"),
    ("keyhole-relic",  "render_keyhole_relic.py",   0.40, 0.52, "RELIC"),
]


def load(slug, fname):
    spec = importlib.util.spec_from_file_location("m_" + slug.replace("-", "_"),
                                                  os.path.join(HERE, slug, fname))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def chip(draw, r_frac, cy_frac, lit=False, cw=116, ch=132, ssr=6):
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * r_frac) * ssr
    sline = (int(min(cw, ch) * r_frac) / 12.0) * ssr
    draw(big, cw * ssr // 2, int(ch * ssr * cy_frac), r, sline, lit)
    return sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)


cw, ch = 116, 132
cols, pad, head, lab = 4, 18, 70, 40
cellw = cw + 40  # chip + 3x strip side-by-side
rows = 2
W = cols * cellw + (cols + 1) * pad
H = head + rows * (ch + lab + pad) + pad
sheet = pygame.Surface((W, H)); sheet.fill(sk.BG)
sheet.blit(sk.font(26).render("NEW-8 skulls — true ~24px chip reads (left) + 3x zoom", True, sk.LABEL), (pad, 16))
sheet.blit(sk.font(15).render("WILD: horned-ram · antler-stag · sabertooth-maw · cyclops-brow    RELIC: longjaw · cracked-half · flat-slab · keyhole", True, sk.LABEL_DIM), (pad, 46))

for i, (slug, fname, rf, cyf, flavor) in enumerate(SPEC):
    m = load(slug, fname)
    lit = flavor == "WILD"
    c = chip(m.draw, rf, cyf, lit=lit)
    z = pygame.transform.scale(pygame.transform.smoothscale(c, (24, 27)), (24 * 3, 27 * 3))
    r_i, c_i = divmod(i, cols)
    x = pad + c_i * (cellw + pad)
    y = head + r_i * (ch + lab + pad)
    col = (60, 66, 78) if flavor == "WILD" else (48, 52, 60)
    pygame.draw.rect(sheet, col, (x - 6, y - 6, cellw + 12, ch + 12))
    sheet.blit(c, (x, y))
    sheet.blit(z, (x + cw + 8, y + ch - 81))
    sheet.blit(sk.font(15).render(slug, True, sk.LABEL), (x, y + ch + 6))
    sheet.blit(sk.font(12).render("24·3", True, sk.LABEL_DIM), (x + cw + 8, y + ch + 6))

out = os.path.join(HERE, "showcase.png")
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
