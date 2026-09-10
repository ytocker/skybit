"""Compose the clown-event bone-column showcase: the five matured finals
stacked with a title banner and per-concept caption (thesis + ship status),
so the columns can be compared and picked at a glance."""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (slug, display name, one-line thesis, sheet path)
CONCEPTS = [
    ("skull-stupa", "1 - SKULL-STUPA (stacked totem)",
     "Discrete bone drums stacked tier-on-tier; the one awake gold-lamp skull frames the gap.",
     "docs/clown_bone_columns/skull-stupa/round_2.png"),
    ("marrow-skewer", "2 - MARROW-SKEWER (spike-threaded)",
     "Vertebrae & skulls beaded on an unbroken gold marrow-spike; barbed point caps the lane.",
     "docs/clown_bone_columns/marrow-skewer/round_2.png"),
    ("rib-cage", "3 - RIB-CAGE (hybrid)",
     "Continuous spine + grouped curved rib-lobes; locked Asthi gem-ring skull cap.",
     "docs/clown_bone_columns/rib-cage/round_2.png"),
    ("bone-plate-slab", "4 - BONE-PLATE SLAB (fused mass)",
     "Tessellated cranial-plate fortress wall; boss-skull keystone. The honest solid column.",
     "docs/clown_bone_columns/bone-plate-slab/round_2.png"),
    ("bone-candle", "5 - BONE-CANDLE (melted drip)",
     "Slumped wax shaft, cosmetic drip-lobes, cyan soul-flame sconce. The organic outlier.",
     "docs/clown_bone_columns/bone-candle/round_2.png"),
]

W = 1040                  # common content width
PAD = 20
HEAD_H = 64               # per-concept caption band
BG = (24, 22, 28)
BANNER = (16, 14, 20)
INK = (236, 230, 222)
SUB = (176, 170, 182)
GOLD = (212, 176, 92)
SHIP = (120, 196, 138)


def font(sz, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


F_TITLE = font(30, bold=True)
F_NAME = font(21, bold=True)
F_THESIS = font(15)
F_SHIP = font(14, bold=True)

# Scale each sheet to the common content width.
scaled = []
for slug, name, thesis, rel in CONCEPTS:
    im = Image.open(os.path.join(ROOT, rel)).convert("RGB")
    h = round(im.height * (W - 2 * PAD) / im.width)
    scaled.append(im.resize((W - 2 * PAD, h), Image.LANCZOS))

TITLE_H = 84
total_h = TITLE_H + sum(HEAD_H + s.height + PAD for s in scaled) + PAD
canvas = Image.new("RGB", (W, total_h), BG)
d = ImageDraw.Draw(canvas)

# Title banner.
d.rectangle([0, 0, W, TITLE_H], fill=BANNER)
d.text((PAD, 16), "CLOWN-EVENT BONE COLUMNS", font=F_TITLE, fill=INK)
d.text((PAD, 52), "Five ship-ready obstacle columns - tied to the Skull-King / Citipati / Asthi bone roster",
       font=F_THESIS, fill=SUB)

y = TITLE_H + PAD
for (slug, name, thesis, rel), s in zip(CONCEPTS, scaled):
    # Caption band.
    d.rectangle([PAD, y, W - PAD, y + HEAD_H], fill=BANNER)
    d.line([PAD, y, PAD, y + HEAD_H], fill=GOLD, width=3)
    d.text((PAD + 14, y + 8), name, font=F_NAME, fill=GOLD)
    ship = "SHIP-READY"
    sw = d.textlength(ship, font=F_SHIP)
    d.text((W - PAD - sw - 14, y + 10), ship, font=F_SHIP, fill=SHIP)
    d.text((PAD + 14, y + 36), thesis, font=F_THESIS, fill=SUB)
    y += HEAD_H
    canvas.paste(s, (PAD, y))
    y += s.height + PAD

out = os.path.join(ROOT, "docs/clown_bone_columns/showcase.png")
canvas.save(out)
print("wrote", out, canvas.size)
