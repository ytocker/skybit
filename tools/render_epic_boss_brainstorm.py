"""Rough blackout-silhouette massing strip for the late-game EPIC boss brainstorm.

WHY: distinctness is the hard gate, and silhouette is the first thing the
art-director culls on — so this strip shows ONLY solid-black massing (no
detail, no palette) to prove each direction reads blackout-distinct from the
others and from the round/bouncy chibi clown. These are rough thumbnails, not
finished art."""
import os
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()

W, H = 1480, 560
CELL_W = W // 8
BG = (232, 236, 242)
GRID = (208, 214, 222)
INK = (24, 24, 30)
LABEL = (40, 40, 48)

surf = pygame.Surface((W, H))
surf.fill(BG)

font = pygame.font.SysFont("dejavusans", 17, bold=True)
small = pygame.font.SysFont("dejavusans", 13)


def poly(pts, col=INK):
    pygame.draw.polygon(surf, col, pts)


def blob(cx, cy, rx, ry):
    pygame.draw.ellipse(surf, INK, (cx - rx, cy - ry, rx * 2, ry * 2))


def shaft(cx, top, bot, w):
    pygame.draw.rect(surf, INK, (cx - w // 2, top, w, bot - top))


# ground line for scale reference per cell
GROUND = 470


def cell(i, name):
    x0 = i * CELL_W
    pygame.draw.rect(surf, GRID, (x0, 0, CELL_W, H), 1)
    pygame.draw.line(surf, GRID, (x0 + 12, GROUND), (x0 + CELL_W - 12, GROUND), 1)
    lab = font.render(name, True, LABEL)
    surf.blit(lab, (x0 + (CELL_W - lab.get_width()) // 2, H - 34))
    return x0 + CELL_W // 2


# clown scale reference (small round chibi) drawn faint in each cell base
def clown_ref(cx):
    ref = (150, 156, 168)
    pygame.draw.circle(surf, ref, (cx + 52, GROUND - 26), 22)        # round head
    pygame.draw.ellipse(surf, ref, (cx + 34, GROUND - 18, 38, 30))   # round body


# 0 ── ash-titan : squat volcanic colossus, monolith
cx = cell(0, "ash-titan")
clown_ref(cx)
poly([(cx - 60, GROUND), (cx - 70, GROUND - 120), (cx - 30, GROUND - 200),
      (cx + 30, GROUND - 205), (cx + 72, GROUND - 118), (cx + 62, GROUND)])  # boulder torso
blob(cx, GROUND - 230, 46, 40)                                    # craggy head
poly([(cx - 78, GROUND - 150), (cx - 110, GROUND - 60), (cx - 70, GROUND - 70)])  # slab arm
poly([(cx + 78, GROUND - 150), (cx + 112, GROUND - 60), (cx + 72, GROUND - 70)])
shaft(cx + 118, GROUND - 320, GROUND, 26)                          # monolith maul

# 1 ── frost-lich : tall gaunt undead king, soul-standard
cx = cell(1, "frost-lich")
clown_ref(cx)
shaft(cx, GROUND - 360, GROUND - 40, 30)                           # gaunt robe column
poly([(cx - 46, GROUND), (cx - 30, GROUND - 250), (cx + 30, GROUND - 250),
      (cx + 46, GROUND)])                                          # flared robe hem
blob(cx, GROUND - 300, 30, 34)                                     # skull
poly([(cx - 60, GROUND - 300), (cx - 30, GROUND - 360), (cx - 30, GROUND - 290)])  # crown spike
poly([(cx + 60, GROUND - 300), (cx + 30, GROUND - 360), (cx + 30, GROUND - 290)])
shaft(cx + 70, GROUND - 380, GROUND, 14)                           # standard pole
blob(cx + 70, GROUND - 380, 22, 24)                                # soul-orb head

# 2 ── storm-wyrm : sprawling serpentine dragon, lightning-glaive
cx = cell(2, "storm-wyrm")
clown_ref(cx)
pts = []
import math
for t in range(0, 40):
    a = t / 39
    sx = cx - 90 + a * 180
    sy = GROUND - 120 + math.sin(a * 7) * 70
    pts.append((sx, sy - 16))
for t in range(39, -1, -1):
    a = t / 39
    sx = cx - 90 + a * 180
    sy = GROUND - 120 + math.sin(a * 7) * 70
    pts.append((sx, sy + 16))
poly(pts)                                                          # coiling body band
blob(cx + 92, GROUND - 150, 34, 26)                                # wedge head
poly([(cx + 70, GROUND - 175), (cx + 120, GROUND - 230), (cx + 100, GROUND - 165)])  # horn
shaft(cx - 96, GROUND - 320, GROUND, 12)                           # glaive haft

# 3 ── chained-warden : hulking demon-knight, greatsword-monolith
cx = cell(3, "chained-warden")
clown_ref(cx)
poly([(cx - 70, GROUND), (cx - 64, GROUND - 170), (cx - 88, GROUND - 210),
      (cx - 40, GROUND - 200), (cx, GROUND - 230), (cx + 40, GROUND - 200),
      (cx + 88, GROUND - 210), (cx + 64, GROUND - 170), (cx + 70, GROUND)])  # broad pauldroned torso
blob(cx, GROUND - 250, 26, 28)                                     # helm
shaft(cx + 96, GROUND - 350, GROUND - 10, 30)                      # greatsword blade
poly([(cx + 81, GROUND - 350), (cx + 111, GROUND - 350), (cx + 96, GROUND - 380)])  # blade tip

# 4 ── horned-sovereign : the devil lead, grand trident
cx = cell(4, "horned-sovereign")
clown_ref(cx)
poly([(cx - 54, GROUND), (cx - 64, GROUND - 150), (cx - 20, GROUND - 215),
      (cx + 20, GROUND - 215), (cx + 64, GROUND - 150), (cx + 54, GROUND)])  # V-taper torso
blob(cx, GROUND - 250, 30, 32)                                     # head
poly([(cx - 30, GROUND - 270), (cx - 78, GROUND - 360), (cx - 18, GROUND - 290)])  # sweeping horn
poly([(cx + 30, GROUND - 270), (cx + 78, GROUND - 360), (cx + 18, GROUND - 290)])
poly([(cx - 80, GROUND - 150), (cx - 150, GROUND - 110), (cx - 80, GROUND - 110)])  # bat wing hint
poly([(cx + 80, GROUND - 150), (cx + 150, GROUND - 110), (cx + 80, GROUND - 110)])
shaft(cx + 92, GROUND - 380, GROUND, 14)                           # trident shaft
poly([(cx + 78, GROUND - 360), (cx + 106, GROUND - 360), (cx + 92, GROUND - 410)])  # prongs

# 5 ── deep-leviathan : bloated abyssal sea-titan, barbed harpoon
cx = cell(5, "deep-leviathan")
clown_ref(cx)
blob(cx - 6, GROUND - 120, 86, 96)                                 # bulbous mass
poly([(cx - 70, GROUND - 60), (cx - 130, GROUND - 30), (cx - 70, GROUND - 10)])  # fin
poly([(cx + 70, GROUND - 60), (cx + 130, GROUND - 30), (cx + 70, GROUND - 10)])
poly([(cx - 50, GROUND - 200), (cx - 30, GROUND - 250), (cx - 10, GROUND - 200)])  # tendrils up
poly([(cx + 10, GROUND - 200), (cx + 30, GROUND - 250), (cx + 50, GROUND - 200)])
shaft(cx + 96, GROUND - 360, GROUND, 12)                           # harpoon
poly([(cx + 88, GROUND - 360), (cx + 104, GROUND - 360), (cx + 96, GROUND - 392)])

# 6 ── cerberus-warden : tripartite hellhound, bone-totem leash-pole
cx = cell(6, "cerberus-warden")
clown_ref(cx)
poly([(cx - 90, GROUND), (cx - 100, GROUND - 90), (cx - 40, GROUND - 130),
      (cx + 40, GROUND - 130), (cx + 100, GROUND - 90), (cx + 90, GROUND)])  # low quadruped mass
blob(cx - 56, GROUND - 150, 26, 24)                                # head L
blob(cx, GROUND - 165, 28, 26)                                     # head C
blob(cx + 56, GROUND - 150, 26, 24)                                # head R
poly([(cx - 110, GROUND), (cx - 130, GROUND - 50), (cx - 116, GROUND)])  # haunch
shaft(cx + 120, GROUND - 330, GROUND, 16)                          # bone totem pole

# 7 ── reaper-shade : tall hooded specter, great-scythe
cx = cell(7, "reaper-shade")
clown_ref(cx)
poly([(cx - 40, GROUND), (cx - 52, GROUND - 200), (cx - 18, GROUND - 300),
      (cx + 18, GROUND - 300), (cx + 52, GROUND - 200), (cx + 40, GROUND)])  # tall draped column
poly([(cx - 30, GROUND - 290), (cx, GROUND - 360), (cx + 30, GROUND - 290)])  # peaked hood
shaft(cx - 70, GROUND - 380, GROUND, 12)                           # scythe snath
poly([(cx - 70, GROUND - 380), (cx + 10, GROUND - 410), (cx - 64, GROUND - 360)])  # curved blade

title = pygame.font.SysFont("dejavusans", 24, bold=True).render(
    "EPIC EVENT-BOSS  —  brainstorm massing (solid-black silhouette read only; faint grey = clown scale ref)",
    True, LABEL)
surf.blit(title, (16, 12))

out = "/home/user/skybit/docs/epic_boss/brainstorm.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(surf, out)
print("wrote", out)
