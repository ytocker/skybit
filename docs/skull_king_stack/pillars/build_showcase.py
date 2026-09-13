"""The combined figure — all ten Skull-King pillar designs in one sheet: top row =
the 5 PLAIN pillars (P1-P5), bottom row = the 5 SKEWERED pillars (P6-P10), each a
pillar pair framing the gap on day sky, labelled with its name + recipe note.

Each design's recipe lives in its own module (constants TITLE/RECIPE/WITH_SKEWER/
SKEWER_STYLE/COLLAR/LEAN); this just imports them and renders via the shared engine.

Run headless: SDL_VIDEODRIVER=dummy python3 docs/skull_king_stack/pillars/build_showcase.py
"""
import os, sys, importlib.util
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pygame
import pillar_engine as PE
sk = PE.sk

# id, slug, module filename, group (original P1-P10 vs the new no-skewer P11-P20)
PILLARS = [
    (1,  "relic-reliquary-totem",        "render_relic_reliquary_totem.py",        "original"),
    (2,  "horned-warband",               "render_horned_warband.py",               "original"),
    (3,  "keystone-cairn",               "render_keystone_cairn.py",               "original"),
    (4,  "gaunt-hollow-spire",           "render_gaunt_hollow_spire.py",           "original"),
    (5,  "broken-bone-pile",             "render_broken_bone_pile.py",             "original"),
    (6,  "plain-bone-spit",              "render_plain_bone_spit.py",              "original"),
    (7,  "gold-cored-scepter",           "render_gold_cored_scepter.py",           "original"),
    (8,  "ring-eye-washer-axle",         "render_ring_eye_washer_axle.py",         "original"),
    (9,  "barbed-fang-harpoon",          "render_barbed_fang_harpoon.py",          "original"),
    (10, "bead-threaded-strand-spindle", "render_bead_threaded_strand_spindle.py", "original"),
    (11, "runt-cairn-taper",             "render_runt_cairn_taper.py",             "new"),
    (12, "thirdeye-watchtower",          "render_thirdeye_watchtower.py",          "new"),
    (13, "lopsided-fang-lean",           "render_lopsided_fang_lean.py",           "new"),
    (14, "child-relic-shrine",           "render_child_relic_shrine.py",           "new"),
    (15, "darkblue-bone-rosary",         "render_darkblue_bone_rosary.py",         "new"),
    (16, "broad-block-bastion",          "render_broad_block_bastion.py",          "new"),
    (17, "cracked-ruin-lean",            "render_cracked_ruin_lean.py",            "new"),
    (18, "palm-jewel-pagoda",            "render_palm_jewel_pagoda.py",            "new"),
    (19, "necklace-draped-warlord",      "render_necklace_draped_warlord.py",      "new"),
    (20, "mongrel-generations-totem",    "render_mongrel_generations_totem.py",    "new"),
]

HALF_H, GAP = 168, 120


def _load(slug, fname):
    spec = importlib.util.spec_from_file_location("pil_" + slug.replace("-", "_"),
                                                  os.path.join(HERE, slug, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _cell(pid, slug, mod):
    skewer = "skewer: " + mod.SKEWER_STYLE if mod.WITH_SKEWER else "no skewer"
    pair = PE.render_pair(mod.RECIPE, with_skewer=mod.WITH_SKEWER, skewer_style=mod.SKEWER_STYLE,
                          collar=mod.COLLAR, lean=mod.LEAN, half_h=HALF_H, gap=GAP,
                          margin_r=getattr(mod, "MARGIN_R", None))
    cw = max(pair.get_width() + 16, 150)
    ch = pair.get_height() + 64
    cell = pygame.Surface((cw, ch)); cell.fill(sk.PANEL)
    cell.blit(sk.font(16).render(f"P{pid}  {slug}", True, sk.LABEL), (8, 6))
    cell.blit(pair, ((cw - pair.get_width()) // 2, 28))
    cell.blit(sk.font(12).render(skewer, True, sk.LABEL_DIM), (8, ch - 22))
    return cell


cells = []
for pid, slug, fname, group in PILLARS:
    path = os.path.join(HERE, slug, fname)
    if not os.path.exists(path):
        print("MISSING", slug); continue
    cells.append((group, _cell(pid, slug, _load(slug, fname))))

# two sections (original P1-P10, new P11-P20), each wrapped at COLS per row so the
# new additions read as their own block under the existing roster
SECTIONS = [("ORIGINAL (P1-P10)", "original"), ("NEW (P11-P20) · no skewer", "new")]
COLS = 5
gap, head, rowlab = 14, 70, 28
cw = max(c.get_width() for _, c in cells)
ch = max(c.get_height() for _, c in cells)
total_rows = sum(-(-sum(1 for g, _ in cells if g == key) // COLS) for _, key in SECTIONS)
W = COLS * cw + (COLS + 1) * gap
H = head + len(SECTIONS) * rowlab + total_rows * (ch + gap) + gap
sheet = pygame.Surface((W, H)); sheet.fill(sk.BG)
sheet.blit(sk.font(26).render("SKULL-KING event — 20 stacked-skull pillar designs", True, sk.LABEL), (gap, 16))
sheet.blit(sk.font(14).render("P1-P10 = original roster · P11-P20 = new no-skewer totems · drawn from skulls #1-#30 + ornaments #31-#36", True, sk.LABEL_DIM), (gap, 46))

y = head
for label, key in SECTIONS:
    sheet.blit(sk.font(15).render(label, True, sk.LABEL_DIM), (gap, y))
    y += rowlab
    row = [c for g, c in cells if g == key]
    for i in range(0, len(row), COLS):
        x = gap
        for c in row[i:i + COLS]:
            sheet.blit(c, (x, y)); x += cw + gap
        y += ch + gap

out = os.path.join(HERE, "showcase.png")
pygame.image.save(sheet, out)
print("WROTE", out, sheet.get_size())
