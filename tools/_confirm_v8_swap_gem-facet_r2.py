#!/usr/bin/env python3
"""gem-facet · confirm_purchase_v8 · swap-round-1 · round 2"""
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

# EPIC glow/deep lifted ~15 and ~10 per channel respectively so it holds
# luminance parity with RARE and LEGENDARY — the original (44,10,80) deep was
# far below the other tiers in overall value, making EPIC read as the "darkest"
# tier even though it should feel premium.
TIERS = [
    ("RARE",      "skin_wizard",    "720",   {"gem":(108,188,252),"glow":(60,140,230), "deep":(18,44,90)}),
    ("EPIC",      "skin_prism",     "1,400", {"gem":(194,122,248),"glow":(165,75,235), "deep":(54,20,90)}),
    ("LEGENDARY", "skin_astronaut", "2,600", {"gem":(255,202,104),"glow":(220,160,40), "deep":(90,50,0)}),
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
    # Cut-crystal price seat: 8-facet lozenge (4 top + 4 bottom) radiating from
    # a shared centre point. The inner 4 facets (2 per half) map to gem value so
    # Zone A mean luminance sits clearly above Zone B. Outermost 2 per half reach
    # deep. Bottom half at a 0.08 sink — barely darker, not a luminance cliff.
    cx, cy = m(CX), m(CHIP_CY)
    hw, hh = m(80), m(14)
    gem, glow, deep = pal["gem"], pal["glow"], pal["deep"]
    # sparkle halo bleeds just past the girdle so the seat reads as crystal
    sc._alpha_aura(big, cx, cy, m(94), glow, peak=35, layers=8)

    def facet_col(d):                       # d: 0 at centre (gem) .. 1 at edge (deep)
        if d < 0.5:
            return lerp_color(gem, glow, d / 0.5)
        return lerp_color(glow, deep, (d - 0.5) / 0.5)

    # 4 facets per half = 8 total. Outer tips taper to 0.9×hh; centre apex
    # reaches full hh — the silhouette stays a clean pointed lozenge.
    n = 4
    top = [(cx - hw,       cy),
           (cx - hw * 0.5, cy - hh * 0.9),
           (cx,            cy - hh),
           (cx + hw * 0.5, cy - hh * 0.9),
           (cx + hw,       cy)]
    bot = [(cx - hw,       cy),
           (cx - hw * 0.5, cy + hh * 0.9),
           (cx,            cy + hh),
           (cx + hw * 0.5, cy + hh * 0.9),
           (cx + hw,       cy)]
    C = (cx, cy)
    edge = (8, 6, 18); ew = max(1, m(1))
    # d_cap=1.0 on top → outermost 2 (tips) reach deep; d_cap=0.65 on bottom →
    # bottom outer stays well below deep so only the top tips are "the dark ones",
    # which lifts Zone A mean luminance above Zone B.
    for pts, sink, d_cap in ((top, 0.0, 1.0), (bot, 0.08, 0.65)):
        for i in range(n):
            # inner pair (i=1,2) has d_raw=0.25; outer pair (i=0,3) has d_raw=0.75.
            # linear remap so inner → 0 (gem), top outer → 1 (deep).
            d_raw = abs((i + 0.5) - n / 2) / (n / 2)
            d = min(d_cap, max(0.0, (d_raw - 0.25) / 0.5) + sink)
            tri = [C, pts[i], pts[i + 1]]
            pygame.draw.polygon(big, facet_col(d), tri)
            pygame.draw.polygon(big, edge, tri, ew)

    nf = font(18); num_w = nf.size(price_str)[0]
    coin_r = m(8); coin_d = coin_r * 2; gap = m(6)
    sx = cx - (coin_d + gap + num_w) / 2; ty = cy - m(1)
    sc.coin_glyph(big, int(sx + coin_r), int(ty), coin_r)
    # dark keyline ring so the coin reads as a distinct medallion on all tiers —
    # critical on LEGENDARY where the gold coin otherwise blends into gold facets.
    pygame.draw.circle(big, (8, 6, 18),
                       (int(sx + coin_r), int(ty)), coin_r, max(1, m(2)))
    # light numeral + dark keyline — readable on all facet luminance levels,
    # including the outer deep facets where the previous dark numeral dropped out.
    plain_text(big, price_str, nf,
               (int(sx + coin_d + gap + num_w / 2), int(ty)),
               (250, 248, 240), shadow_a=70, weight=m(0.9),
               keyline=(8, 6, 18), kw=m(1.0))


def zone_b_banner(big, tier_word, pal):
    # Faceted crystal bar: five chevron-seam bands. A thin bevel outline frames
    # the entire bar so terminal deep bands don't float against the shelf on any
    # tier (particularly EPIC where deep ≈ shelf value).
    cy = m(Y_BANNER); x0, x1 = m(43), m(217); h = m(16)
    ytop, ybot = cy - h // 2, cy + h // 2
    gem, glow, deep = pal["gem"], pal["glow"], pal["deep"]
    band_cols = [deep, glow, gem, glow, deep]; n = 5; s = m(5)
    seam_x = [x0 + (x1 - x0) * j / n for j in range(n + 1)]

    def seam(j):                             # -> (top_x, bot_x) of the cut
        if j == 0 or j == n:
            return (seam_x[j], seam_x[j])   # flat ends, tucked under the gems
        sign = 1 if j % 2 == 0 else -1
        return (seam_x[j] + sign * s, seam_x[j] - sign * s)

    edge = (8, 6, 18); ew = max(1, m(1))
    for i in range(n):
        lt, lb = seam(i); rt, rb = seam(i + 1)
        quad = [(int(lb), ybot), (int(lt), ytop), (int(rt), ytop), (int(rb), ybot)]
        pygame.draw.polygon(big, band_cols[i], quad)
        pygame.draw.polygon(big, edge, quad, ew)
    # top-edge bevel highlight sells the cut crown
    pygame.draw.line(big, lerp_color(gem, WHITE, 0.4),
                     (x0, ytop), (x1, ytop), max(1, m(1)))
    # gold bevel outline around the full bar rect so end bands separate cleanly
    # from the shelf background on all tiers
    bar_rect = pygame.Rect(int(x0), ytop, int(x1 - x0), ybot - ytop)
    sc.bevel_rim(big, bar_rect, 0, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 100),
                 w=max(1, m(1)))
    plain_text(big, tier_word, font(10), (m(CX), cy), (14, 12, 26),
               shadow_a=60, weight=m(0.8))


def render_popup(tw, sid, ps, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big); corner_gems(big, pal); name_text(big, NAMES[tw])
    zone_a_chip(big, ps, pal); shelf_and_buttons(big)
    zone_b_banner(big, tw, pal); bottom_gems(big, pal); hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))

MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "gem-facet · swap-round-1 · r2", fill=(232, 226, 208))
for i, (tw, sid, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
pathlib.Path("/home/user/skybit/docs/confirm_purchase_v8/swap-round-1/gem-facet").mkdir(
    parents=True, exist_ok=True)
OUT = "/home/user/skybit/docs/confirm_purchase_v8/swap-round-1/gem-facet/round_2.png"
out.save(OUT)
print(f"saved {out.size[0]}×{out.size[1]}  →  {OUT}")
