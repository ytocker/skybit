"""Compare original concept-1 wreath at the REAL badge geometry (R=0.46*size):
Shame AS-IS (leaves clip past the badge edge) vs the leaf-fit variant (leaves
nestled inside). Red square = the badge bounds (what _build keeps; anything
outside is clipped at row size)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame; pygame.init(); pygame.font.init()
import game.achievement_icons as ai
from tools.badge_rings.concepts import fame_wreath, shame_wreath, shame_wreath_fit
SS=ai._SS
def font(p): return pygame.font.SysFont(None,p,bold=True)

def medal_bounds(fn, glyph, badge, margin=0.46):
    """Real geometry: R tied to the BADGE (0.46), drawn on an oversized canvas so
    overflow past the badge square is VISIBLE; red square marks the badge bounds."""
    canvas=int(badge*(1+2*margin)); px=canvas*SS; c=px//2
    surf=pygame.Surface((px,px),pygame.SRCALPHA)
    R=int(badge*SS*0.46)
    fn(surf,c,c,R,glyph)
    img=pygame.transform.smoothscale(surf,(canvas,canvas))
    b0=int(badge*margin)
    pygame.draw.rect(img,(232,72,72),(b0,b0,badge,badge),2)
    return img

def chip(fn, glyph, size=44):
    """True row result: surface == badge square, so overflow really clips."""
    px=size*SS; c=px//2; surf=pygame.Surface((px,px),pygame.SRCALPHA)
    fn(surf,c,c,int(px*0.46),glyph)
    return pygame.transform.smoothscale(surf,(size,size))

badge=150; M=0.46; cv=int(badge*(1+2*M))
W=cv*2+150; H=cv+220
s=pygame.Surface((W,H)); 
for yy in range(H): s.fill((30,28,44) if yy<46 else (20,18,32),(0,yy,W,1))
s.blit(font(30).render("ORIGINAL #1 WREATH — real badge geometry (red = badge bounds)",True,(236,232,244)),(20,12))
s.blit(font(20).render("Fame ring (reference)",True,(244,200,96)),(20,56))
s.blit(medal_bounds(fame_wreath,"pillar_100",badge),(20,80))
s.blit(font(15).render("44px:",True,(176,172,196)),(20+cv+8,80+cv//2)); s.blit(chip(fame_wreath,"pillar_100"),(20+cv+50,80+cv//2-22))
# shame pair
yb=80
xL=20; xR=20+cv+150-cv  # second column start
s.blit(font(20).render("SHAME — AS-IS (leaves clip)",True,(220,120,120)),(W//2+10,56))
s.blit(medal_bounds(shame_wreath,"goose_egg",badge),(W//2+10,80))
# row-2: fit version under fame col? lay shame as-is left, fit right
pygame.image.save(s,"docs/wreath_final/_tmp.png")
# simpler clean 2-up of the SHAME comparison + chips
def panel(title,fn,col):
    p=pygame.Surface((cv+20, cv+120))
    for yy in range(cv+120): p.fill((24,22,38),(0,yy,cv+20,1))
    p.blit(font(22).render(title,True,col),(8,6))
    p.blit(medal_bounds(fn,"goose_egg",badge),(10,40))
    p.blit(font(15).render("at 44px row:",True,(176,172,196)),(10,40+cv+6))
    p.blit(chip(fn,"goose_egg"),(150,40+cv-6))
    return p
out=pygame.Surface((( cv+20)*2+60, cv+150))
for yy in range(out.get_height()): out.fill((16,14,28),(0,yy,out.get_width(),1))
out.blit(font(28).render("ORIGINAL #1 SHAME WREATH  —  as-is  vs  leaf-fit   (red = badge bounds)",True,(236,232,244)),(20,10))
out.blit(panel("AS-IS  (leaves spill past edge)",shame_wreath,(222,120,120)),(20,54))
out.blit(panel("LEAF-FIT  (nestled inside)",shame_wreath_fit,(150,210,150)),(20+cv+40,54))
pygame.image.save(out,"docs/wreath_final/compare.png")
print("saved docs/wreath_final/compare.png",out.get_size())
