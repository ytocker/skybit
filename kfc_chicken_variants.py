"""
Crispy fried chicken — 4 coating variants for comparison.
Run from repo root: python kfc_chicken_variants.py
"""
import os, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.parrot import _aaellipse, _add_outline, _WING_ANGLES, SPRITE_W, SPRITE_H
from game.draw import BIRD_BEAK, BIRD_BEAK_D, WHITE

os.makedirs("screenshots", exist_ok=True)

BG = (15, 10, 30)


# ── Shared helpers ────────────────────────────────────────────────────────────

def _crackle(surf, lines, dark, light):
    for x1, y1, x2, y2 in lines:
        pygame.draw.line(surf, dark,  (x1,   y1  ), (x2,   y2  ), 1)
        pygame.draw.line(surf, light, (x1-1, y1-1), (x2-1, y2-1), 1)


def _bumpy_ring(surf, cx, cy, rx, ry, color, bumps, bump_r):
    """Draw an ellipse outline with small circles protruding outward."""
    for i in range(bumps):
        a = 2 * math.pi * i / bumps
        bx = int(cx + (rx + bump_r * 0.6) * math.cos(a))
        by = int(cy + (ry + bump_r * 0.6) * math.sin(a))
        pygame.draw.circle(surf, color, (bx, by), bump_r)


# ── Variant A — heavy spots + dark crust ring ─────────────────────────────────
def build_A(wing_angle_deg):
    G = (210, 138, 42); D = (148, 82, 18); L = (238, 178, 72); S = (110, 55, 8)
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    for i, c in enumerate([(148,82,18),(178,108,28),(208,138,42),(228,162,58)]):
        pygame.draw.polygon(surf, c, [(2+i*3,26+i*2),(14+i,24+i),(20+i,30+i*2),(6+i*3,36+i*2)])
    pygame.draw.line(surf, D, (4,27),(18,31),1); pygame.draw.line(surf, D, (6,33),(20,35),1)
    _aaellipse(surf,(80,40,4),(34,36),23,17)
    _aaellipse(surf,(110,60,8),(33,35),22,16)   # dark crust ring
    _aaellipse(surf,G,(32,33),20,14)
    _aaellipse(surf,L,(29,28),14,9)
    _aaellipse(surf,(242,190,80),(27,39),13,7)
    _aaellipse(surf,D,(32,45),18,5)
    for px,py,pr in ((20,30,3),(37,27,3),(43,35,3),(24,39,2),(38,39,2),
                     (28,34,2),(32,26,2),(44,30,2),(16,37,2),(34,42,2),
                     (40,24,2),(22,43,2),(46,37,1),(18,33,1),(36,43,1)):
        pygame.draw.circle(surf, S, (px,py), pr)
    _crackle(surf,[(14,30,23,25),(37,25,47,30),(15,39,25,44),(40,38,50,33),(22,34,31,29),(34,39,43,36)],D,L)
    sheen=pygame.Surface((30,7),pygame.SRCALPHA); pygame.draw.ellipse(sheen,(255,225,145,130),sheen.get_rect()); surf.blit(sheen,(17,20))
    # wing
    w=pygame.Surface((54,54),pygame.SRCALPHA)
    pygame.draw.polygon(w,(0,0,0,110),[(24,26),(48,12),(52,30),(36,46),(18,40)])
    pygame.draw.polygon(w,G,[(24,24),(46,11),(50,28),(34,44),(18,38)])
    pygame.draw.polygon(w,D,[(24,24),(34,44),(18,38)])
    for px,py,pr in ((38,18,2),(46,23,2),(28,34,2),(42,30,2)): pygame.draw.circle(w,S,(px,py),pr)
    pygame.draw.line(w,D,(26,25),(44,17),2); pygame.draw.line(w,D,(28,32),(46,26),2); pygame.draw.line(w,L,(25,24),(43,15),1)
    surf.blit(pygame.transform.rotate(w,wing_angle_deg),pygame.transform.rotate(w,wing_angle_deg).get_rect(center=(34,27)).topleft)
    # head
    _aaellipse(surf,(95,50,6),(49,23),13,12); _aaellipse(surf,G,(48,21),13,12)
    _aaellipse(surf,L,(45,24),5,4); _aaellipse(surf,(232,172,68),(47,15),8,4)
    for px,py,pr in ((52,18,2),(45,22,2),(51,25,1)): pygame.draw.circle(surf,S,(px,py),pr)
    pygame.draw.circle(surf,WHITE,(51,20),4); pygame.draw.circle(surf,(15,15,25),(52,20),2); pygame.draw.circle(surf,WHITE,(53,18),1)
    beak=[(55,21),(61,24),(58,28),(52,26)]; pygame.draw.polygon(surf,BIRD_BEAK,beak); pygame.draw.polygon(surf,BIRD_BEAK_D,beak,1)
    pygame.draw.line(surf,(255,230,150),(55,22),(59,24),1); pygame.draw.line(surf,BIRD_BEAK_D,(52,24),(58,25),1)
    for lx,ly,ex,ey in ((27,46,20,56),(37,46,44,56)):
        pygame.draw.line(surf,D,(lx,ly),(ex,ey),6); pygame.draw.line(surf,G,(lx-1,ly-1),(ex-1,ey-1),4)
        pygame.draw.line(surf,L,(lx-2,ly-2),(ex-2,ey-2),1)
        pygame.draw.circle(surf,G,(ex,ey),5); pygame.draw.circle(surf,D,(ex,ey),5,1); pygame.draw.circle(surf,WHITE,(ex,ey),2)
    return surf


# ── Variant B — lumpy batter silhouette ──────────────────────────────────────
def build_B(wing_angle_deg):
    G=(210,138,42); D=(130,68,10); L=(245,185,72); S=(95,45,5)
    surf=pygame.Surface((SPRITE_W,SPRITE_H),pygame.SRCALPHA)
    for i,c in enumerate([(148,82,18),(178,108,28),(208,138,42),(228,162,58)]):
        pygame.draw.polygon(surf,c,[(2+i*3,26+i*2),(14+i,24+i),(20+i,30+i*2),(6+i*3,36+i*2)])
    _aaellipse(surf,(75,38,3),(34,36),24,18)
    # Lumpy outer batter silhouette — circles around the body edge
    _bumpy_ring(surf,32,33,21,15,D,14,4)
    _bumpy_ring(surf,32,33,21,15,G,14,3)
    _aaellipse(surf,G,(32,33),20,14)
    _aaellipse(surf,L,(29,27),15,10)
    _aaellipse(surf,(242,190,80),(27,39),13,7)
    _aaellipse(surf,D,(32,46),19,5)
    for px,py,pr in ((20,30,3),(37,27,3),(43,35,3),(24,39,3),(38,39,2),
                     (28,34,2),(32,26,2),(44,30,3),(16,37,2),(34,42,2),
                     (40,24,2),(22,43,2),(47,38,2),(13,34,2),(36,44,2)):
        pygame.draw.circle(surf,S,(px,py),pr)
    _crackle(surf,[(14,30,23,25),(37,25,47,30),(15,39,25,44),(40,38,50,33),(22,34,31,29),(34,39,43,36),(20,42,28,38)],D,L)
    sheen=pygame.Surface((30,7),pygame.SRCALPHA); pygame.draw.ellipse(sheen,(255,225,145,130),sheen.get_rect()); surf.blit(sheen,(17,20))
    w=pygame.Surface((54,54),pygame.SRCALPHA)
    pygame.draw.polygon(w,(0,0,0,110),[(24,26),(48,12),(52,30),(36,46),(18,40)])
    _bumpy_ring(w,34,28,16,16,D,10,3)
    pygame.draw.polygon(w,G,[(24,24),(46,11),(50,28),(34,44),(18,38)])
    pygame.draw.polygon(w,D,[(24,24),(34,44),(18,38)])
    for px,py,pr in ((38,18,2),(46,23,2),(28,34,2),(42,30,2),(32,20,2)): pygame.draw.circle(w,S,(px,py),pr)
    pygame.draw.line(w,D,(26,25),(44,17),2); pygame.draw.line(w,L,(25,24),(43,15),1)
    surf.blit(pygame.transform.rotate(w,wing_angle_deg),pygame.transform.rotate(w,wing_angle_deg).get_rect(center=(34,27)).topleft)
    _aaellipse(surf,(90,48,5),(49,23),14,13); _bumpy_ring(surf,48,21,12,11,D,10,3)
    _aaellipse(surf,G,(48,21),13,12); _aaellipse(surf,L,(45,24),5,4); _aaellipse(surf,(232,172,68),(47,15),8,4)
    for px,py,pr in ((52,18,2),(45,22,2),(51,25,1),(48,28,1)): pygame.draw.circle(surf,S,(px,py),pr)
    pygame.draw.circle(surf,WHITE,(51,20),4); pygame.draw.circle(surf,(15,15,25),(52,20),2); pygame.draw.circle(surf,WHITE,(53,18),1)
    beak=[(55,21),(61,24),(58,28),(52,26)]; pygame.draw.polygon(surf,BIRD_BEAK,beak); pygame.draw.polygon(surf,BIRD_BEAK_D,beak,1)
    pygame.draw.line(surf,(255,230,150),(55,22),(59,24),1); pygame.draw.line(surf,BIRD_BEAK_D,(52,24),(58,25),1)
    for lx,ly,ex,ey in ((27,46,20,56),(37,46,44,56)):
        pygame.draw.line(surf,D,(lx,ly),(ex,ey),7); pygame.draw.line(surf,G,(lx-1,ly-1),(ex-1,ey-1),5)
        pygame.draw.line(surf,L,(lx-2,ly-2),(ex-2,ey-2),1)
        _bumpy_ring(surf,ex,ey,5,5,D,6,3)
        pygame.draw.circle(surf,G,(ex,ey),5); pygame.draw.circle(surf,D,(ex,ey),5,1); pygame.draw.circle(surf,WHITE,(ex,ey),2)
    return surf


# ── Variant C — extra dark crust, max contrast ────────────────────────────────
def build_C(wing_angle_deg):
    G=(215,142,38); D=(100,48,5); L=(252,200,78); S=(72,30,3)
    CRUST=(155,82,14)
    surf=pygame.Surface((SPRITE_W,SPRITE_H),pygame.SRCALPHA)
    for i,c in enumerate([(120,60,8),(158,90,18),(198,128,35),(228,162,55)]):
        pygame.draw.polygon(surf,c,[(2+i*3,26+i*2),(14+i,24+i),(20+i,30+i*2),(6+i*3,36+i*2)])
    _aaellipse(surf,(60,28,2),(35,37),25,18)
    _bumpy_ring(surf,33,34,23,17,D,16,4)
    _aaellipse(surf,CRUST,(33,34),22,16)   # very dark crust layer
    _aaellipse(surf,G,(31,32),19,13)
    _aaellipse(surf,L,(28,26),14,9)        # bright golden peak
    _aaellipse(surf,(248,198,82),(26,38),12,6)
    _aaellipse(surf,D,(32,46),20,5)
    for px,py,pr in ((18,28,4),(37,26,4),(45,35,4),(22,39,3),(40,39,3),
                     (27,34,3),(31,25,3),(45,29,3),(14,36,3),(35,43,3),
                     (41,23,2),(21,44,2),(48,38,2),(12,32,2),(36,44,2),(28,42,2)):
        pygame.draw.circle(surf,S,(px,py),pr)
    _crackle(surf,[(13,29,23,24),(37,24,48,30),(14,39,25,45),(41,38,51,33),
                   (21,33,31,28),(35,39,44,35),(19,43,28,38),(44,32,52,28)],D,L)
    sheen=pygame.Surface((28,8),pygame.SRCALPHA); pygame.draw.ellipse(sheen,(255,230,140,140),sheen.get_rect()); surf.blit(sheen,(16,19))
    w=pygame.Surface((56,56),pygame.SRCALPHA)
    pygame.draw.polygon(w,(0,0,0,120),[(24,26),(50,11),(54,31),(37,47),(17,40)])
    _bumpy_ring(w,34,28,18,17,D,12,4)
    pygame.draw.polygon(w,CRUST,[(24,24),(48,10),(52,29),(35,45),(17,38)])
    pygame.draw.polygon(w,G,[(26,24),(46,12),(50,27),(34,43),(19,37)])
    pygame.draw.polygon(w,D,[(26,24),(34,43),(19,37)])
    for px,py,pr in ((38,17,3),(47,23,3),(27,34,3),(43,30,3),(33,20,2),(40,36,2)): pygame.draw.circle(w,S,(px,py),pr)
    pygame.draw.line(w,D,(27,25),(45,16),2); pygame.draw.line(w,L,(25,24),(43,15),1)
    surf.blit(pygame.transform.rotate(w,wing_angle_deg),pygame.transform.rotate(w,wing_angle_deg).get_rect(center=(34,26)).topleft)
    _aaellipse(surf,(75,35,3),(50,23),15,13); _bumpy_ring(surf,49,22,14,13,D,11,4)
    _aaellipse(surf,CRUST,(49,22),14,13); _aaellipse(surf,G,(48,20),12,11); _aaellipse(surf,L,(45,16),7,5)
    for px,py,pr in ((53,18,3),(44,22,2),(52,26,2),(47,28,1),(55,24,1)): pygame.draw.circle(surf,S,(px,py),pr)
    pygame.draw.circle(surf,WHITE,(51,20),4); pygame.draw.circle(surf,(15,15,25),(52,20),2); pygame.draw.circle(surf,WHITE,(53,18),1)
    beak=[(55,21),(61,24),(58,28),(52,26)]; pygame.draw.polygon(surf,BIRD_BEAK,beak); pygame.draw.polygon(surf,BIRD_BEAK_D,beak,1)
    pygame.draw.line(surf,(255,230,150),(55,22),(59,24),1); pygame.draw.line(surf,BIRD_BEAK_D,(52,24),(58,25),1)
    for lx,ly,ex,ey in ((27,46,19,57),(37,46,45,57)):
        _bumpy_ring(surf,(lx+ex)//2,(ly+ey)//2,4,4,D,5,3)
        pygame.draw.line(surf,D,(lx,ly),(ex,ey),7); pygame.draw.line(surf,CRUST,(lx-1,ly-1),(ex-1,ey-1),5)
        pygame.draw.line(surf,G,(lx-2,ly-2),(ex-2,ey-2),3); pygame.draw.line(surf,L,(lx-3,ly-3),(ex-3,ey-3),1)
        _bumpy_ring(surf,ex,ey,6,6,D,7,3)
        pygame.draw.circle(surf,G,(ex,ey),6); pygame.draw.circle(surf,D,(ex,ey),6,1); pygame.draw.circle(surf,WHITE,(ex,ey),2)
    return surf


# ── Variant D — max volume, deep golden KFC style ────────────────────────────
def build_D(wing_angle_deg):
    G=(220,148,45); D=(115,58,8); L=(255,205,80); S=(82,38,4)
    OUTER=(168,95,16); INNER=(245,192,68)
    surf=pygame.Surface((SPRITE_W,SPRITE_H),pygame.SRCALPHA)
    for i,c in enumerate([(130,70,10),(165,100,22),(205,135,40),(230,165,58)]):
        pygame.draw.polygon(surf,c,[(2+i*3,25+i*2),(16+i,23+i),(22+i,29+i*2),(7+i*3,35+i*2)])
    pygame.draw.line(surf,D,(4,26),(20,30),1); pygame.draw.line(surf,D,(6,32),(22,34),1)
    _aaellipse(surf,(65,32,2),(34,35),26,19)
    _bumpy_ring(surf,33,33,24,17,D,18,5)
    _bumpy_ring(surf,33,33,24,17,OUTER,18,4)
    _aaellipse(surf,OUTER,(33,33),23,17)
    _aaellipse(surf,G,(31,31),20,14)
    _aaellipse(surf,INNER,(28,26),15,10)
    _aaellipse(surf,L,(26,23),9,6)             # very bright breast peak
    _aaellipse(surf,(248,198,78),(26,39),14,8)
    _aaellipse(surf,D,(32,47),20,5)
    for px,py,pr in ((18,27,4),(38,25,4),(46,35,4),(22,39,3),(40,40,3),
                     (27,33,3),(31,24,3),(46,28,3),(13,36,3),(35,44,3),
                     (42,22,3),(20,44,3),(49,39,2),(11,31,2),(37,45,2),
                     (26,42,2),(44,42,2),(16,42,2),(50,33,2)):
        pygame.draw.circle(surf,S,(px,py),pr)
    _crackle(surf,[(12,28,23,23),(37,23,49,29),(13,39,25,45),(41,38,52,33),
                   (20,32,31,27),(35,38,45,34),(18,43,28,38),(45,31,53,27),
                   (24,36,33,31),(38,43,47,39)],D,L)
    sheen=pygame.Surface((32,9),pygame.SRCALPHA); pygame.draw.ellipse(sheen,(255,235,148,145),sheen.get_rect()); surf.blit(sheen,(14,17))
    w=pygame.Surface((58,58),pygame.SRCALPHA)
    pygame.draw.polygon(w,(0,0,0,115),[(24,26),(50,10),(55,31),(38,48),(16,40)])
    _bumpy_ring(w,35,27,20,18,D,14,5); _bumpy_ring(w,35,27,20,18,OUTER,14,4)
    pygame.draw.polygon(w,OUTER,[(24,24),(48,10),(53,29),(36,46),(17,38)])
    pygame.draw.polygon(w,G,[(26,24),(46,12),(51,27),(34,44),(19,37)])
    pygame.draw.polygon(w,D,[(26,24),(34,44),(19,37)])
    for px,py,pr in ((39,16,3),(48,22,3),(27,33,3),(44,29,3),(33,19,2),(41,35,2),(30,25,2)): pygame.draw.circle(w,S,(px,py),pr)
    pygame.draw.line(w,D,(27,25),(46,16),2); pygame.draw.line(w,L,(25,24),(44,15),1)
    surf.blit(pygame.transform.rotate(w,wing_angle_deg),pygame.transform.rotate(w,wing_angle_deg).get_rect(center=(34,26)).topleft)
    _aaellipse(surf,(65,32,2),(50,22),16,14)
    _bumpy_ring(surf,49,21,14,13,D,12,4); _bumpy_ring(surf,49,21,14,13,OUTER,12,3)
    _aaellipse(surf,OUTER,(49,21),14,13); _aaellipse(surf,G,(48,20),12,11); _aaellipse(surf,L,(45,15),8,5); _aaellipse(surf,INNER,(44,14),5,3)
    for px,py,pr in ((54,17,3),(44,21,2),(52,26,2),(47,27,2),(56,24,1),(48,29,1)): pygame.draw.circle(surf,S,(px,py),pr)
    pygame.draw.circle(surf,WHITE,(51,19),4); pygame.draw.circle(surf,(15,15,25),(52,19),2); pygame.draw.circle(surf,WHITE,(53,17),1)
    beak=[(55,20),(62,23),(59,27),(52,25)]; pygame.draw.polygon(surf,BIRD_BEAK,beak); pygame.draw.polygon(surf,BIRD_BEAK_D,beak,1)
    pygame.draw.line(surf,(255,230,150),(55,21),(59,23),1); pygame.draw.line(surf,BIRD_BEAK_D,(52,23),(58,24),1)
    for lx,ly,ex,ey in ((27,47,18,57),(38,47,46,57)):
        for r,c in ((8,D),(6,OUTER),(4,G),(2,L)): pygame.draw.line(surf,c,(lx-8+r,ly-8+r),(ex-8+r,ey-8+r),r)
        _bumpy_ring(surf,ex,ey,7,7,D,8,4)
        pygame.draw.circle(surf,G,(ex,ey),7); pygame.draw.circle(surf,D,(ex,ey),7,1); pygame.draw.circle(surf,WHITE,(ex,ey),2)
    return surf


# ── Render comparison ─────────────────────────────────────────────────────────

builders = [("A — Heavy Spots", build_A),
            ("B — Lumpy Batter", build_B),
            ("C — Dark Crust", build_C),
            ("D — Max Coating", build_D)]

ZOOM  = 4
PAD   = 20
LABEL = 30
fw    = (SPRITE_W + 4) * ZOOM   # frame width after outline padding
fh    = (SPRITE_H + 4) * ZOOM

PW = PAD + len(builders) * (fw + PAD)
PH = LABEL + fh + PAD + 20

canvas = pygame.Surface((PW, PH))
canvas.fill(BG)

lf = pygame.font.SysFont(None, 20)

for i, (label, builder) in enumerate(builders):
    frame = _add_outline(builder(_WING_ANGLES[1]))   # mid-up wing
    zoomed = pygame.transform.scale_by(frame, ZOOM)
    x = PAD + i * (fw + PAD)
    canvas.blit(zoomed, (x, LABEL))
    txt = lf.render(label, True, (200, 180, 120))
    canvas.blit(txt, (x + fw//2 - txt.get_width()//2, LABEL + fh + 6))

out = "screenshots/kfc_crispy_variants.png"
pygame.image.save(canvas, out)
print(f"  saved {out}")
pygame.quit()
