#!/usr/bin/env python3
"""herald-rail · confirm_purchase_v8 · swap-round-1 · round 2"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1,1))
import game.store_cards as sc
from game.store_cards import vgrad_stops, plain_text, m, SS, font, CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image, ImageDraw

# mandatory gloss_sweep patch
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
# Note 5: cy nudged from 247 to 250 for 2-3 px more clearance below the name.
CHIP_CY = 250; Y_BANNER = 402; BOT_GEM_CY = 402
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

# ── Zone A: heraldic price rail ───────────────────────────────────────────────

def zone_a_chip(big, price_str, pal):
    """Price rail: wide gold capsule at cy=250, coin pinned to left finial,
    numeral right-aligned to right finial — fills the full 200 px span."""
    rw, rh = m(200), m(26)
    rad = rh // 2
    rect = pygame.Rect(0, 0, rw, rh); rect.center = (m(CX), m(CHIP_CY))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0,(148,118,40)),(0.5,(200,168,72)),(1.0,(120,90,28))], 255),
             rect.topleft)
    # Dominant-gold sheen + full bevel so this reads as the most-lit fixture on the card.
    sc.top_sheen(big, rect, rad, m(13), peak=50)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 240), w=max(1, m(2.0)))

    # Note 4: finials seated r=6, 4px inboard so they sit clearly ON the gold face,
    # not straddling the round cap edge where they read as noise.
    fin_r = m(6)
    for fx in (rect.left + m(4), rect.right - m(4)):
        pygame.draw.circle(big, (206, 172, 78), (fx, rect.centery), fin_r)
        pygame.draw.circle(big, (110, 82, 26), (fx, rect.centery), m(3))

    # Note 1: coin left edge pinned to left-finial zone (fixed anchor CX-80 logical),
    # numeral right edge pinned to right-finial zone (fixed anchor CX+80 logical).
    # This turns the capsule into a true rail rather than an empty field with a centred tag.
    nf = font(18)
    coin_r = m(9)
    coin_cx = m(CX - 80) + coin_r          # left edge of coin at CX-80 logical
    num_w = sc._glyph_base(price_str, nf, 0).get_width()
    num_cx = m(CX + 80) - num_w // 2       # right edge of numeral at CX+80 logical
    sc.coin_glyph(big, coin_cx, rect.centery, coin_r)
    plain_text(big, price_str, nf, (num_cx, rect.centery), (14, 12, 26),
               shadow_a=0, weight=m(0.9))

# ── Zone B: tier identification rail ─────────────────────────────────────────

def zone_b_banner(big, tier_word, pal):
    """Tier rail: slimmer capsule at cy=402 — bottom gems flank each end.
    LEGENDARY gets its own near-black-amber deep stop so it never collides
    visually with the gold Zone A above it."""
    rw, rh = m(146), m(16)
    rad = rh // 2
    rect = pygame.Rect(0, 0, rw, rh); rect.center = (m(CX), m(Y_BANNER))

    # Note 2: LEGENDARY's glow is gold-family, which would produce two gold bars
    # if we used the raw pal stops here.  Remap to a near-black-amber base with
    # a hotter ember peak so the tier rail reads clearly hotter than — not same-as
    # — the machined price gold above.
    if tier_word == "LEGENDARY":
        band_deep = (40, 22, 0)       # near-black amber
        band_glow = (255, 150, 40)    # hotter orange/ember
    else:
        band_deep = pal["deep"]
        band_glow = pal["glow"]

    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, band_deep), (1.0, band_glow)], 255), rect.topleft)
    # Muted sheen + dim rim keep this subordinate to the price rail above.
    sc.top_sheen(big, rect, rad, m(8), peak=18)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 120), w=max(1, m(1)))

    # Note 3: font bumped to 11; RARE/EPIC letter-spaced to fill ~90-100 px of
    # the 146 px span so short words don't float lost in the middle.
    # LEGENDARY is already wide enough at 11 pt.  Per-tier text colour: cream
    # for LEGENDARY to separate from the ember glow; cool silver for others.
    nf11 = font(11)
    if tier_word == "LEGENDARY":
        text_col = (255, 244, 220)   # warm cream — distinct from the ember field
        tracking = 0
    else:
        text_col = (220, 215, 200)
        # Calculate tracking so the word spans ~95 logical px (device: m(95)).
        raw_w = sc._glyph_base(tier_word, nf11, 0).get_width()
        n = len(tier_word)
        target_dev = m(95)
        tracking = max(0, (target_dev - raw_w) // max(1, n - 1))

    plain_text(big, tier_word, nf11, rect.center, text_col,
               shadow_a=90, tracking=tracking, weight=m(0.6))

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
idr.text((MARGIN,18),"herald-rail · swap-round-1 · r2",fill=(232,226,208))
for i,(tw,sid,ps,pal) in enumerate(TIERS):
    pop=render_popup(tw,sid,ps,pal)
    pil=Image.frombytes("RGB",(POP_W,POP_H),pygame.image.tostring(pop,"RGB"))
    x=MARGIN+i*(POP_W+GAP); strip.paste(pil,(x,HEAD))
    idr.text((x+POP_W//2,HEAD+POP_H+6),tw,fill=(180,176,210),anchor="mt")
out=strip.resize((STRIP_W*2,STRIP_H*2),Image.LANCZOS)
import pathlib; pathlib.Path("/home/user/skybit/docs/confirm_purchase_v8/swap-round-1/herald-rail").mkdir(parents=True,exist_ok=True)
OUT="/home/user/skybit/docs/confirm_purchase_v8/swap-round-1/herald-rail/round_2.png"
out.save(OUT); print(f"saved {out.size[0]}×{out.size[1]}  →  {OUT}")
