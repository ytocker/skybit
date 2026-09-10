"""The real choice for fitting the wreath in the badge:
ROW A  as-is  (core R=0.46 fills the badge → laurel spills past the bounds, clips at 44px)
ROW B  fitted (core R=0.36 → the SAME original design sits fully inside the badge)
Uses the ORIGINAL fame_wreath / shame_wreath unchanged; only the core scale differs."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame; pygame.init(); pygame.font.init()
import game.achievement_icons as ai
from tools.badge_rings.concepts import fame_wreath, shame_wreath
SS=ai._SS
def font(p): return pygame.font.SysFont(None,p,bold=True)
def medal(fn,glyph,badge,core,margin=0.46):
    canvas=int(badge*(1+2*margin)); px=canvas*SS; c=px//2
    s=pygame.Surface((px,px),pygame.SRCALPHA)
    fn(s,c,c,int(badge*SS*core),glyph)
    img=pygame.transform.smoothscale(s,(canvas,canvas))
    b0=int(badge*margin); pygame.draw.rect(img,(232,72,72),(b0,b0,badge,badge),2)
    return img
def chip(fn,glyph,core,size=44):
    px=size*SS; c=px//2; s=pygame.Surface((px,px),pygame.SRCALPHA)
    fn(s,c,c,int(px*core),glyph); return pygame.transform.smoothscale(s,(size,size))
badge=140; M=0.46; cv=int(badge*(1+2*M))
def row(y,out,title,core,col):
    out.blit(font(24).render(title,True,col),(20,y))
    for i,(fn,gk,lab) in enumerate(((fame_wreath,"pillar_100","FAME"),(shame_wreath,"goose_egg","SHAME"))):
        x=20+i*(cv+150)
        out.blit(medal(fn,gk,badge,core),(x,y+30))
        out.blit(chip(fn,gk,core),(x+cv+12,y+30+cv//2-22))
        out.blit(font(14).render("44px",True,(176,172,196)),(x+cv+14,y+30+cv//2+24))
W=(cv+150)*2-30; H=(cv+70)*2+60
out=pygame.Surface((W,H))
for yy in range(H): out.fill((16,14,28),(0,yy,W,1))
out.blit(font(26).render("WREATH FIT — core scale (red = badge bounds)",True,(236,232,244)),(20,10))
row(50,out,"A · AS-IS  core 0.46 (medal fills badge, laurel clips)",0.46,(222,120,120))
row(50+cv+70,out,"B · FITTED  core 0.36 (same design, full wreath inside)",0.36,(150,210,150))
pygame.image.save(out,"docs/wreath_final/fit_options.png"); print("saved",out.get_size())
