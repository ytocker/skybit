"""Clean review harness for the classic-8 skulls. Renders every concept's draw()
into one contact sheet: per skull a ~180px hero, the true 24px chip blown up x4,
and a clean blackout silhouette — laid out so nothing overlaps (the per-module
_panel crowds the hero into the blackout, which misreads as a detached mass).

Run headless: SDL_VIDEODRIVER=dummy python3 docs/skull_king_stack/classic8/_review.py
"""
import os, sys, importlib.util
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

HERE = os.path.dirname(os.path.abspath(__file__))

# slug, module file, chip r_frac, chip cy_frac, global ID (classic block = 23..30)
SPEC = [
    ("round-cap",       "render_round_cap.py",        0.30, 0.46, 23),
    ("egg-dome",        "render_egg_dome.py",         0.28, 0.50, 24),
    ("broad-zygo",      "render_broad_zygo.py",       0.27, 0.50, 25),
    ("square-jaw",      "render_square_jaw.py",       0.27, 0.46, 26),
    ("calvaria",        "render_calvaria.py",         0.32, 0.46, 27),
    ("gaunt-hollow",    "render_gaunt_hollow.py",     0.29, 0.48, 28),
    ("child-skull",     "render_child_skull.py",      0.30, 0.48, 29),
    ("flat-brow-robust", "render_flat_brow_robust.py", 0.30, 0.50, 30),
]


def load(slug, fname):
    spec = importlib.util.spec_from_file_location("rv_" + slug.replace("-", "_"),
                                                  os.path.join(HERE, slug, fname))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def chip(draw, r_frac, cy_frac, cw=116, ch=132, ssr=6):
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * r_frac) * ssr
    sline = (int(min(cw, ch) * r_frac) / 12.0) * ssr
    draw(big, cw * ssr // 2, int(ch * ssr * cy_frac), r, sline, False)
    return sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)


def cell(slug, gid, draw, r_frac, cy_frac):
    cw, ch = 116, 132
    pad = 14
    W, H = 180 + 24 * 4 + 24 * 4 + pad * 5, ch + 44
    c = pygame.Surface((W, H)); c.fill(sk.PANEL)
    c.blit(sk.font(17).render(f"#{gid}  {slug}", True, sk.LABEL), (pad, 6))
    # hero ~180px (clean, on its own)
    hero = pygame.Surface((180, 180), pygame.SRCALPHA)
    draw(hero, 90, int(180 * (cy_frac - 0.04)), 56, 56 / 12.0, False)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    c.blit(hero, (pad, 32))
    # true 24px chip blown x4
    ck = chip(draw, r_frac, cy_frac)
    ck24 = pygame.transform.smoothscale(ck, (24, int(24 * ch / cw)))
    x = pad + 180 + pad
    c.blit(pygame.transform.scale(ck24, (24 * 4, int(24 * ch / cw) * 4)), (x, 32))
    c.blit(sk.font(12).render("chip x4", True, sk.LABEL_DIM), (x, 32 + ch))
    # clean blackout silhouette
    mask = pygame.mask.from_surface(ck24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    x2 = x + 24 * 4 + pad
    c.blit(pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4)), (x2, 32))
    c.blit(sk.font(12).render("blackout", True, sk.LABEL_DIM), (x2, 32 + ch))
    return c


cells = [cell(slug, gid, load(slug, fn).draw, rf, cyf) for (slug, fn, rf, cyf, gid) in SPEC]
cw_, ch_ = cells[0].get_size()
cols, gap, head = 2, 16, 56
rows = (len(cells) + cols - 1) // cols
W = cols * cw_ + (cols + 1) * gap
H = head + rows * (ch_ + gap)
sheet = pygame.Surface((W, H)); sheet.fill(sk.BG)
sheet.blit(sk.font(24).render("CLASSIC-8 skulls — round 2 (clean review)", True, sk.LABEL), (gap, 16))
for i, c in enumerate(cells):
    r_i, c_i = divmod(i, cols)
    sheet.blit(c, (gap + c_i * (cw_ + gap), head + r_i * (ch_ + gap)))
out = os.path.join(HERE, "_contact_round2.png")
pygame.image.save(sheet, out)
print("WROTE", out, sheet.get_size())
