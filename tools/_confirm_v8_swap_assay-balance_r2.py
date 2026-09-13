#!/usr/bin/env python3
"""assay-balance · confirm_purchase_v8 · swap-round-1 · round 2"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1,1))
import game.store_cards as sc
from game.store_cards import vgrad_stops, plain_text, m, SS, font, CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image, ImageDraw

def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0: continue
        pygame.draw.line(sweep, (v,v,v,255), (0,y), (rect.w,y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255,255,255,255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

TIERS = [
    ("RARE","skin_wizard","720",{"gem":(108,188,252),"glow":(60,140,230),"deep":(18,44,90)}),
    ("EPIC","skin_prism","1,400",{"gem":(194,122,248),"glow":(150,60,220),"deep":(44,10,80)}),
    ("LEGENDARY","skin_astronaut","2,600",{"gem":(255,202,104),"glow":(220,160,40),"deep":(90,50,0)}),
]
NAMES = {"RARE":"WIZARD","EPIC":"PRISM","LEGENDARY":"ASTRONAUT"}
POP_W,POP_H = 260,442; CX = 130
CARD_X,CARD_TOP_Y,CARD_W,CARD_H,CARD_RAD = 10,127,240,299,23
DISC_CY,DISC_R = 135,53
GEM_L_X,GEM_R_X,GEM_CY,GEM_R = 43,217,152,14
CHIP_CY=247; Y_BANNER=402; BOT_GEM_CY=402
SHELF_X,SHELF_Y,SHELF_W,SHELF_H = 17,335,226,91
BTN_W,BTN_H,BTN_RAD,BTN_CY,BTN_GAP = 99,31,12,360,10
BUY_CX=CX-(BTN_W+BTN_GAP)//2; CAN_CX=CX+(BTN_W+BTN_GAP)//2

def card_body(big):
    rect=pygame.Rect(m(CARD_X),m(CARD_TOP_Y),m(CARD_W),m(CARD_H)); rad=m(CARD_RAD)
    sc.drop_shadow(big,rect,rad,blur=m(8),alpha=165,dy=m(4))
    big.blit(vgrad_stops(rect.w,rect.h,rad,[(0.0,CARD_T),(1.0,CARD_B)],255,gamma=1.15),rect.topleft)
    sc.top_sheen(big,rect,rad,m(30),peak=56)
    pygame.draw.rect(big,(4,5,16),rect,width=max(1,m(2)),border_radius=rad)
    sc.bevel_rim(big,rect,rad,CARD_RING_DEEP,(*CARD_RING_BRIGHT,230),w=max(1,m(1.9)))
    tray=rect.inflate(-m(8),-m(8))
    pygame.draw.rect(big,(*CARD_RING_BRIGHT,55),tray,width=max(1,m(1)),border_radius=rad-m(3))
def corner_gems(big,pal):
    sc.facet_gem(big,m(GEM_L_X),m(GEM_CY),m(GEM_R),pal["gem"],pal["deep"])
    sc.facet_gem(big,m(GEM_R_X),m(GEM_CY),m(GEM_R),pal["gem"],pal["deep"])
def name_text(big,name):
    nfs=45; nfnt=font(nfs); mw=m(CARD_W-20)
    while sc._glyph_base(name,nfnt,0).get_width()>mw and nfs>24: nfs-=1; nfnt=font(nfs)
    plain_text(big,name,nfnt,(m(CX),m(213)),(250,248,240),shadow_a=160,weight=m(0.9),keyline=(6,6,16),kw=m(1.0))
def shelf_and_buttons(big):
    shelf_rect=pygame.Rect(m(SHELF_X),m(SHELF_Y),m(SHELF_W),m(SHELF_H)); sr=m(CARD_RAD)
    shelf=vgrad_stops(shelf_rect.w,shelf_rect.h,0,[(0.0,(34,36,72)),(0.5,(22,24,54)),(1.0,(12,14,36))],255).copy()
    smask=pygame.Surface(shelf_rect.size,pygame.SRCALPHA)
    pygame.draw.rect(smask,(255,255,255,255),smask.get_rect(),border_bottom_left_radius=sr,border_bottom_right_radius=sr)
    shelf.blit(smask,(0,0),special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf,shelf.get_rect(),0,m(20),peak=35)
    pygame.draw.line(shelf,(115,106,140),(0,0),(shelf_rect.w-1,0),max(1,m(1)))
    seat=pygame.Surface((shelf_rect.w,m(6)),pygame.SRCALPHA)
    for yy in range(m(6)): pygame.draw.line(seat,(0,0,0,int(120*(1-yy/m(6)))),(0,yy),(shelf_rect.w-1,yy))
    big.blit(seat,(shelf_rect.x,shelf_rect.y-m(6))); big.blit(shelf,shelf_rect.topleft)
    br=m(BTN_RAD)
    for cx_b,lbl,stops,lab_c,pk,rw in [
        (m(BUY_CX),"BUY",[(0.0,(38,40,84)),(1.0,(22,24,56))],(200,205,240),22,m(2.0)),
        (m(CAN_CX),"CANCEL",[(0.0,(26,28,64)),(1.0,(14,16,44))],(150,155,200),14,m(2.2)),
    ]:
        r=pygame.Rect(0,0,m(BTN_W),m(BTN_H)); r.center=(cx_b,m(BTN_CY))
        sc.drop_shadow(big,r,br,blur=m(3),alpha=100,dy=m(2))
        big.blit(vgrad_stops(r.w,r.h,br,stops,255),r.topleft)
        sc.top_sheen(big,r,br,m(12),peak=pk)
        sc.bevel_rim(big,r,br,CARD_RING_DEEP,(*CARD_RING_BRIGHT,230),w=max(1,rw))
        plain_text(big,lbl,font(14 if lbl=="BUY" else 13),r.center,lab_c,shadow_a=110,weight=m(0.8),keyline=(8,6,20),kw=m(0.9))
def bottom_gems(big,pal):
    for gx in [m(GEM_L_X),m(GEM_R_X)]:
        sc._alpha_aura(big,gx,m(BOT_GEM_CY),m(16),pal["glow"],peak=60,layers=14)
        sc.facet_gem(big,gx,m(BOT_GEM_CY),m(GEM_R),pal["gem"],pal["deep"])
def hero_disc(big,sid,pal):
    cx,cy,r=m(CX),m(DISC_CY),m(DISC_R)
    sc._alpha_aura(big,cx,cy,r+m(55),pal["glow"],peak=95,layers=24)
    sc._alpha_aura(big,cx,cy,r+m(20),pal["glow"],peak=70,layers=12)
    sc.cabochon(big,cx,cy,r,CABO_LO,CABO_HI,ring=pal["gem"],ring_a=50)
    try: sc.blit_thumb(big,sid,cx,cy,int(r*1.5))
    except: pygame.draw.circle(big,pal["gem"],(cx,cy),int(r*0.7))
    sc.cabochon_glass(big,cx,cy,r,tint=pal["gem"])

def zone_a_chip(big, price_str, pal):
    # An assayer's weighing pan: a concave bowl the coin+price rest inside.
    # Narrowed to 124px so the content group fills the tray — an empty bowl
    # reads as placeholder, a full one reads as weight. Upsized coin + text
    # make the depth metaphor land without needing a wider rim.
    PAN_W, PAN_H = 124, 28
    rect = pygame.Rect(0, 0, m(PAN_W), m(PAN_H)); rect.center = (m(CX), m(CHIP_CY))
    rad = m(8)
    big.blit(vgrad_stops(rect.w, rect.h, rad,
        [(0.0,(28,24,50)),(0.5,(44,38,72)),(1.0,(34,28,56))], 255), rect.topleft)

    # Tier-tint aura at the bowl floor — the price chip inherits the tier hue
    # so it reads as the headline beat, not a generic neutral price tag.
    cx_pan, cy_pan = m(CX), m(CHIP_CY)
    sc._alpha_aura(big, cx_pan, cy_pan + m(6), m(40), pal["glow"], peak=45, layers=8)

    # Inner-shadow lip: the pan's near rim throws shade onto the top of the bowl.
    lh = m(6)
    lip = pygame.Surface((rect.w, lh), pygame.SRCALPHA)
    for yy in range(lh):
        pygame.draw.line(lip, (6,5,14,int(90*(1-yy/lh))), (0,yy), (rect.w-1,yy))
    lmask = pygame.Surface((rect.w, lh), pygame.SRCALPHA)
    pygame.draw.rect(lmask,(255,255,255,255),lmask.get_rect(),
                     border_top_left_radius=rad,border_top_right_radius=rad)
    lip.blit(lmask,(0,0),special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(lip, rect.topleft)

    # Rim arc: warm-tinted at alpha 130 so it reads as reflected metal rim
    # highlight, not a stray specular error on the neutral bowl floor.
    arc_color = lerp_color(CARD_RING_BRIGHT, pal["gem"], 0.3)
    arc_rect = rect.inflate(-m(7), -m(6))
    pygame.draw.arc(big, (*arc_color, 130), arc_rect,
                    math.radians(20), math.radians(160), max(1, m(1)))

    sc.bevel_rim(big, rect, rad, (8,6,18), (*CARD_RING_BRIGHT,180), w=max(1,m(1)))

    # Coin + price sit as one centered group inside the bowl.
    # Upsized to font 22 and coin r=11 so the content fills the narrowed pan.
    fs = font(22)
    tw = fs.size(price_str)[0]
    coin_d, gap = m(22), m(8)
    total = coin_d + gap + tw
    start_x = m(CX) - total//2
    coin_cx = start_x + coin_d//2
    text_cx = start_x + coin_d + gap + tw//2
    cy = m(CHIP_CY)

    # Contact shadow: the coin grounds itself with a soft cast ellipse.
    sh = pygame.Surface((coin_d+m(6), m(6)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh,(0,0,0,60),sh.get_rect())
    big.blit(sh, sh.get_rect(center=(coin_cx, cy+m(7))))

    sc.coin_glyph(big, coin_cx, cy, m(11))
    plain_text(big, price_str, fs, (text_cx, cy), (236,240,232),
               shadow_a=140, weight=m(0.8), keyline=(6,6,16), kw=m(0.9))

def zone_b_banner(big, tier_word, pal):
    # Balance beam as a complete structural instrument: a short fulcrum post
    # drops from the pan underside to the shelf line (broken there so it never
    # bisects the button band), and a horizontal crossbar spans the gem seats
    # so the bottom gems read unambiguously as the beam's counterweights.

    # Fulcrum post: pan underside to shelf top only — stops at y=335.
    post_h = m(335 - 261)
    post = pygame.Surface((max(1,m(1)), post_h), pygame.SRCALPHA)
    post.fill((*CARD_RING_BRIGHT, 140))
    big.blit(post, (m(CX)-post.get_width()//2, m(261)))

    # Horizontal crossbar at the gem-seat row — connects left gem to right gem.
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 140),
                     (m(GEM_L_X), m(BOT_GEM_CY)), (m(GEM_R_X), m(BOT_GEM_CY)),
                     max(1, m(1)))

    # Reserved plaque: a compact seat that names the tier.
    # Wider radius (6) and brighter bevel (165) unified to the pan's treatment.
    PLQ_W, PLQ_H = 110, 16
    rect = pygame.Rect(0, 0, m(PLQ_W), m(PLQ_H)); rect.center = (m(CX), m(Y_BANNER))
    rad = m(6)
    big.blit(vgrad_stops(rect.w, rect.h, rad,
        [(0.0,pal["deep"]),(1.0,pal["glow"])], 255), rect.topleft)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT,165), w=max(1,m(1)))
    # Lifted to near-white so LEGENDARY gold plaque text has real contrast.
    plain_text(big, tier_word, font(10), rect.center, (238,236,228),
               shadow_a=110, weight=m(0.7), keyline=(6,6,16), kw=m(0.8))

def render_popup(tw,sid,ps,pal):
    big=pygame.Surface((POP_W*SS,POP_H*SS),pygame.SRCALPHA)
    card_body(big); corner_gems(big,pal); name_text(big,NAMES[tw])
    zone_a_chip(big,ps,pal); shelf_and_buttons(big)
    zone_b_banner(big,tw,pal); bottom_gems(big,pal); hero_disc(big,sid,pal)
    return pygame.transform.smoothscale(big,(POP_W,POP_H))

MARGIN,HEAD,GAP=20,58,12
STRIP_W=MARGIN*2+len(TIERS)*(POP_W+GAP)-GAP; STRIP_H=HEAD+POP_H+MARGIN
strip=Image.new("RGB",(STRIP_W,STRIP_H),(8,8,20))
idr=ImageDraw.Draw(strip); idr.text((MARGIN,18),"assay-balance · swap-round-1 · r2",fill=(232,226,208))
for i,(tw,sid,ps,pal) in enumerate(TIERS):
    pop=render_popup(tw,sid,ps,pal)
    pil=Image.frombytes("RGB",(POP_W,POP_H),pygame.image.tostring(pop,"RGB"))
    x=MARGIN+i*(POP_W+GAP); strip.paste(pil,(x,HEAD))
    idr.text((x+POP_W//2,HEAD+POP_H+6),tw,fill=(180,176,210),anchor="mt")
out=strip.resize((STRIP_W*2,STRIP_H*2),Image.LANCZOS)
import pathlib; pathlib.Path("/home/user/skybit/docs/confirm_purchase_v8/swap-round-1/assay-balance").mkdir(parents=True,exist_ok=True)
OUT="/home/user/skybit/docs/confirm_purchase_v8/swap-round-1/assay-balance/round_2.png"
out.save(OUT); print(f"saved {out.size[0]}×{out.size[1]}  →  {OUT}")
