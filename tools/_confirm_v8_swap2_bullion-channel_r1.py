#!/usr/bin/env python3
"""bullion-channel · confirm_purchase_v8 · swap-round-2

Zone A is a full-width near-black enamel trough milled into the card body:
the bevel's bright lip sits on the LOWER-INNER edge (light rising from the
cut) so the bar reads RECESSED, not raised. Tier identity is carried only by
the facet_gem rivets at each end + their aura — the enamel body is identical
on every tier, so the coin-gold numeral never collides with tier colour.
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1,1))
import game.store_cards as sc
from game.store_cards import vgrad_stops, plain_text, m, SS, font, CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image, ImageDraw

# mandatory gloss_sweep patch — BLEND_ADD must be masked to the rounded rect
# or the dark enamel field blows out to white at the corners.
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
CHIP_CY = 247; Y_BANNER = 402; BOT_GEM_CY = 402
SHELF_X,SHELF_Y,SHELF_W,SHELF_H = 17,335,226,91
BTN_W,BTN_H,BTN_RAD,BTN_CY,BTN_GAP = 99,31,12,360,10
BUY_CX = CX-(BTN_W+BTN_GAP)//2; CAN_CX = CX+(BTN_W+BTN_GAP)//2

def card_body(big):
    rect = pygame.Rect(m(CARD_X),m(CARD_TOP_Y),m(CARD_W),m(CARD_H)); rad = m(CARD_RAD)
    sc.drop_shadow(big,rect,rad,blur=m(8),alpha=165,dy=m(4))
    big.blit(vgrad_stops(rect.w,rect.h,rad,[(0.0,CARD_T),(1.0,CARD_B)],255,gamma=1.15),rect.topleft)
    sc.top_sheen(big,rect,rad,m(30),peak=56)
    pygame.draw.rect(big,(4,5,16),rect,width=max(1,m(2)),border_radius=rad)
    sc.bevel_rim(big,rect,rad,CARD_RING_DEEP,(*CARD_RING_BRIGHT,230),w=max(1,m(1.9)))
    tray = rect.inflate(-m(8),-m(8))
    pygame.draw.rect(big,(*CARD_RING_BRIGHT,55),tray,width=max(1,m(1)),border_radius=rad-m(3))

def corner_gems(big,pal):
    sc.facet_gem(big,m(GEM_L_X),m(GEM_CY),m(GEM_R),pal["gem"],pal["deep"])
    sc.facet_gem(big,m(GEM_R_X),m(GEM_CY),m(GEM_R),pal["gem"],pal["deep"])

def name_text(big,name):
    nfs=45; nfnt=font(nfs); mw=m(CARD_W-20)
    while sc._glyph_base(name,nfnt,0).get_width()>mw and nfs>24:
        nfs-=1; nfnt=font(nfs)
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
    for yy in range(m(6)):
        pygame.draw.line(seat,(0,0,0,int(120*(1-yy/m(6)))),(0,yy),(shelf_rect.w-1,yy))
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

# ── Zone A: bullion-channel — recessed near-black enamel trough ────────────────

def zone_a_chip(big, price_str, pal):
    """Full-width trough milled into the card body. The bright bevel lip is on
    the LOWER edge and a hard shadow sits under the TOP edge, so light appears
    to rise from inside the cut — the bar reads recessed, not raised. Enamel
    body is tier-agnostic; the facet_gem rivets at each end carry tier."""
    r = pygame.Rect(m(20), m(227), m(220), m(40))  # x=20..240, cy=247
    radius = m(6)

    # Subtle drop shadow — a cut channel barely lifts off the card.
    sc.drop_shadow(big, r, radius, blur=m(3), alpha=60, dy=m(1))

    # Near-black enamel fill — identical on every tier.
    stops = [(0.0,(24,22,44)), (0.5,(18,16,36)), (1.0,(12,10,28))]
    big.blit(vgrad_stops(r.w, r.h, radius, stops), r.topleft)

    # RECESSED gloss: light pools at the BOTTOM of the trough, not the top.
    gloss = pygame.Surface(r.size, pygame.SRCALPHA)
    h = r.h
    for y_off in range(h):
        a = int(18 * (y_off / h) ** 1.5)
        pygame.draw.line(gloss, (a,a,a,255), (0, y_off), (r.w, y_off))
    sm = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255,255,255,255), sm.get_rect(), border_radius=radius)
    gloss.blit(sm, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(gloss, r.topleft, special_flags=pygame.BLEND_ADD)

    # Inner shadow under the TOP edge — the overhang above a milled cut.
    top_shadow = pygame.Surface(r.size, pygame.SRCALPHA)
    band = max(1, min(m(8), h))
    for y_off in range(band):
        a = int(90 * (1 - y_off / band))
        pygame.draw.line(top_shadow, (0,0,0,a), (0, y_off), (r.w, y_off))
    big.blit(top_shadow, r.topleft)

    # Bevel: dark outer keyline, bright gold lip, then dim the TOP half so the
    # only bright bevel survives on the lower-inner edge.
    pygame.draw.rect(big, (6,4,16), r, width=max(1,m(1.6)), border_radius=radius)
    sc.bevel_rim(big, r, radius, (6,4,16), (*CARD_RING_BRIGHT, 180), w=max(1,m(1.4)))
    top_mask = pygame.Surface((r.w, r.h//2), pygame.SRCALPHA)
    top_mask.fill((0,0,0,80))
    big.blit(top_mask, r.topleft)

    # Tier facet_gem rivets at each end — sole tier signal in Zone A.
    for rx in (m(20 + 14), m(240 - 14)):
        sc.facet_gem(big, rx, m(247), m(8), pal["gem"], pal["deep"])
        sc._alpha_aura(big, rx, m(247), m(12), pal["glow"], peak=50, layers=6)

    # Coin + price inline, centred in the trough. LIGHT text on dark enamel.
    sc.coin_glyph(big, m(CX-40), m(247), m(12))
    plain_text(big, price_str, font(20), (m(CX+10), m(247)), (236,240,232),
               shadow_a=100, weight=m(1.0), keyline=(8,6,18), kw=m(1.2))

# ── Zone B: rarity ribbon lozenge ─────────────────────────────────────────────

def zone_b_banner(big, tier_word, pal):
    """Diamond-ended machined-metal lozenge; bottom gems cap its ends."""
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(146), pal)

# ── render loop ───────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price_str, pal):
    big = pygame.Surface((POP_W*SS,POP_H*SS),pygame.SRCALPHA)
    card_body(big); corner_gems(big,pal); name_text(big,NAMES[tier_word])
    zone_a_chip(big,price_str,pal)
    shelf_and_buttons(big)
    zone_b_banner(big,tier_word,pal)
    bottom_gems(big,pal); hero_disc(big,sid,pal)
    return pygame.transform.smoothscale(big,(POP_W,POP_H))

MARGIN,HEAD,GAP = 20,58,12
STRIP_W = MARGIN*2+len(TIERS)*(POP_W+GAP)-GAP; STRIP_H = HEAD+POP_H+MARGIN
strip = Image.new("RGB",(STRIP_W,STRIP_H),(8,8,20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN,18),"bullion-channel · swap-round-2 · round_1",fill=(232,226,208))
for i,(tw,sid,ps,pal) in enumerate(TIERS):
    pop=render_popup(tw,sid,ps,pal)
    pil=Image.frombytes("RGB",(POP_W,POP_H),pygame.image.tostring(pop,"RGB"))
    x=MARGIN+i*(POP_W+GAP); strip.paste(pil,(x,HEAD))
    idr.text((x+POP_W//2,HEAD+POP_H+6),tw,fill=(180,176,210),anchor="mt")
out=strip.resize((STRIP_W*2,STRIP_H*2),Image.LANCZOS)
import pathlib; pathlib.Path("/home/user/skybit/docs/confirm_purchase_v8/swap-round-2/bullion-channel").mkdir(parents=True,exist_ok=True)
OUT="/home/user/skybit/docs/confirm_purchase_v8/swap-round-2/bullion-channel/round_1.png"
out.save(OUT); print(f"saved {out.size[0]}×{out.size[1]}  →  {OUT}")
