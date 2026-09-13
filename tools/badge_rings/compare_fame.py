"""Show the Fame wreath that matches the shame comparison — real badge geometry
(R=0.46*size, red = badge bounds) — and the final matched pair (Fame + Shame
leaf-fit) at hero + 44px row size."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame; pygame.init(); pygame.font.init()
import game.achievement_icons as ai
from tools.badge_rings.concepts import fame_wreath, shame_wreath_fit
SS=ai._SS
def font(p): return pygame.font.SysFont(None,p,bold=True)
def medal_bounds(fn, glyph, badge, margin=0.46):
    canvas=int(badge*(1+2*margin)); px=canvas*SS; c=px//2
    surf=pygame.Surface((px,px),pygame.SRCALPHA); R=int(badge*SS*0.46)
    fn(surf,c,c,R,glyph)
    img=pygame.transform.smoothscale(surf,(canvas,canvas))
    b0=int(badge*margin); pygame.draw.rect(img,(232,72,72),(b0,b0,badge,badge),2)
    return img
def chip(fn, glyph, size=44):
    px=size*SS; c=px//2; s=pygame.Surface((px,px),pygame.SRCALPHA)
    fn(surf=s,cx=c,cy=c,R=int(px*0.46),glyph_key=glyph)
    return pygame.transform.smoothscale(s,(size,size))

badge=150; M=0.46; cv=int(badge*(1+2*M))
def panel(title,fn,glyph,col):
    p=pygame.Surface((cv+20, cv+120))
    for yy in range(cv+120): p.fill((24,22,38),(0,yy,cv+20,1))
    p.blit(font(22).render(title,True,col),(8,6))
    p.blit(medal_bounds(fn,glyph,badge),(10,40))
    p.blit(font(15).render("at 44px row:",True,(176,172,196)),(10,40+cv+6))
    p.blit(chip(fn,glyph),(160,40+cv-6))
    return p
out=pygame.Surface(((cv+20)*2+60, cv+150))
for yy in range(out.get_height()): out.fill((16,14,28),(0,yy,out.get_width(),1))
out.blit(font(28).render("ORIGINAL #1 WREATH  —  matched PAIR  (real badge geometry, red = bounds)",True,(236,232,244)),(20,10))
out.blit(panel("FAME  (pristine gold laurel)",fame_wreath,"pillar_100",(244,200,96)),(20,54))
out.blit(panel("SHAME  (leaf-fit, leaves inside)",shame_wreath_fit,"goose_egg",(150,210,150)),(20+cv+40,54))
pygame.image.save(out,"docs/wreath_final/pair_fit.png")
print("saved docs/wreath_final/pair_fit.png",out.get_size())
