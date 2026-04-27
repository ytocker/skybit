"""KFC powerup — 5 design variants. Run from repo root.
Produces screenshots/kfc_v1.png … kfc_v5.png
"""
import os, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()

OUT = "screenshots"
os.makedirs(OUT, exist_ok=True)

KR  = (244,   0,  39)   # KFC brand red
KRD = (120,   0,  20)   # dark red
K   = ( 14,  14,  14)   # near-black
W   = (255, 255, 255)   # white
S   = (255, 232, 205)   # skin tone
H   = (245, 245, 245)   # hair white (slightly warm)
G   = (228, 175,  45)   # gold (for V4 trim)
BG  = ( 12,   8,  38)   # game dark background


# ─────────────────────────────────────────────────────────────────────────────
# Each draw_vN(surf, cx, cy, sz, pulse) paints one sprite.
# sz ≈ MUSHROOM_R (half-size). All coords relative to (cx, cy).
# ─────────────────────────────────────────────────────────────────────────────

def _shadow(surf, cx, cy, sz):
    sh = pygame.Surface((sz * 3, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 65), sh.get_rect())
    surf.blit(sh, (cx - sz * 3 // 2, cy + sz + 1))

def _colonel(surf, cx, cy, sz, hair_top_y, white_l, white_r):
    """Draw Colonel Sanders elements inside the white zone.
    hair_top_y: y of the very top of the white area.
    white_l/white_r: x bounds of white zone.
    """
    zone_w = white_r - white_l
    fc_x = (white_l + white_r) // 2          # face center x
    hair_h = max(3, sz // 3)

    # White hair — swept-up arc
    pygame.draw.ellipse(surf, H,
        (white_l + 1, hair_top_y,
         zone_w - 2, hair_h * 2))

    # Face oval (skin)
    fy = hair_top_y + hair_h + max(2, sz // 4)
    frx = max(3, zone_w // 4)
    fry = max(4, sz // 3)
    pygame.draw.ellipse(surf, S,
        (fc_x - frx, fy - fry, frx * 2, fry * 2))

    # Glasses — two black circles + bridge
    gr  = max(1, frx // 2)
    g_y = fy - 1
    pygame.draw.circle(surf, K, (fc_x - gr - 1, g_y), gr + 1)
    pygame.draw.circle(surf, K, (fc_x + gr + 1, g_y), gr + 1)
    # Lens shine (tiny white arc inside each lens)
    pygame.draw.circle(surf, (90, 90, 90), (fc_x - gr - 2, g_y - 1), max(1, gr - 1))
    pygame.draw.circle(surf, (90, 90, 90), (fc_x + gr,     g_y - 1), max(1, gr - 1))
    # Bridge
    pygame.draw.line(surf, K, (fc_x - 1, g_y), (fc_x + 1, g_y), 1)

    # Goatee — pointed white triangle below chin
    chin_y = fy + fry
    gt_h   = max(3, sz // 4)
    pygame.draw.polygon(surf, H,
        [(fc_x - gt_h + 1, chin_y),
         (fc_x + gt_h - 1, chin_y),
         (fc_x,            chin_y + gt_h)])
    # Subtle goatee outline so it shows on white background
    pygame.draw.polygon(surf, (195, 190, 185),
        [(fc_x - gt_h + 1, chin_y),
         (fc_x + gt_h - 1, chin_y),
         (fc_x,            chin_y + gt_h)], 1)

    # Bow tie — two filled black triangles + centre knot
    bt_y  = chin_y - 2
    bt_hw = max(3, frx - 1)
    bt_hh = max(2, sz // 7)
    pygame.draw.polygon(surf, K,
        [(fc_x - 1, bt_y),
         (fc_x - bt_hw, bt_y - bt_hh),
         (fc_x - bt_hw, bt_y + bt_hh)])
    pygame.draw.polygon(surf, K,
        [(fc_x + 1, bt_y),
         (fc_x + bt_hw, bt_y - bt_hh),
         (fc_x + bt_hw, bt_y + bt_hh)])
    pygame.draw.circle(surf, K, (fc_x, bt_y), max(1, bt_hh // 2))


def _kfc_text(surf, cx, bottom_y, zone_w):
    """Render tiny 'KFC' label centred at cx, above bottom_y."""
    fnt = pygame.font.Font(None, max(10, zone_w // 3))
    lbl = fnt.render("KFC", True, K)
    surf.blit(lbl, (cx - lbl.get_width() // 2,
                    bottom_y - lbl.get_height()))


# ── V1: Faithful Trapezoid Badge ─────────────────────────────────────────────
def draw_v1(surf, cx, cy, sz, pulse=0.0):
    _shadow(surf, cx, cy, sz)

    tw = sz + 2          # top half-width
    bw = sz - 3          # bottom half-width
    bh = sz + 1          # half-height
    pts = [(cx-tw, cy-bh), (cx+tw, cy-bh),
           (cx+bw, cy+bh), (cx-bw, cy+bh)]

    # Red fill + dark outline
    pygame.draw.polygon(surf, KRD, [(p[0]+1, p[1]+1) for p in pts])
    pygame.draw.polygon(surf, KR,  pts)

    # Side red stripes (narrow) — draw white centre over the red
    stripe = max(3, sz // 5)
    wl = cx - tw + stripe
    wr = cx + tw - stripe
    wp = [(wl, cy-bh+1), (wr, cy-bh+1),
          (wr - (tw-bw)*stripe//sz, cy+bh-1),
          (wl + (tw-bw)*stripe//sz, cy+bh-1)]
    pygame.draw.polygon(surf, W, wp)

    # Colonel Sanders in white zone
    _colonel(surf, cx, cy, sz, cy - bh + 1, wl, wr)

    # "KFC" label at badge bottom
    _kfc_text(surf, cx, cy + bh - 1, wr - wl)


# ── V2: Circle Medallion ─────────────────────────────────────────────────────
def draw_v2(surf, cx, cy, sz, pulse=0.0):
    _shadow(surf, cx, cy, sz)

    # Pulsing aura
    pa = max(0, int(30 + 20 * math.sin(pulse * 2)))
    aura = pygame.Surface(((sz+6)*2, (sz+6)*2), pygame.SRCALPHA)
    pygame.draw.circle(aura, (*KR, pa), (sz+6, sz+6), sz+6)
    surf.blit(aura, (cx-sz-6, cy-sz-6))

    # Red circle + dark outline
    pygame.draw.circle(surf, KRD, (cx, cy), sz + 1)
    pygame.draw.circle(surf, KR,  (cx, cy), sz)

    # White upper face zone
    face_h = sz + sz // 2
    pygame.draw.ellipse(surf, W,
        (cx - sz, cy - sz, sz * 2, face_h))

    # Colonel face
    _colonel(surf, cx, cy, sz, cy - sz + 1, cx - sz + 2, cx + sz - 2)

    # Red bottom arc with "KFC"
    pygame.draw.ellipse(surf, KR,
        (cx - sz, cy + sz // 3, sz * 2, sz + sz // 2))
    fnt = pygame.font.Font(None, max(10, sz // 2 + 2))
    lbl = fnt.render("KFC", True, W)
    surf.blit(lbl, (cx - lbl.get_width() // 2, cy + sz // 2))


# ── V3: Bold Chunky Icon ──────────────────────────────────────────────────────
def draw_v3(surf, cx, cy, sz, pulse=0.0):
    _shadow(surf, cx, cy, sz)

    tw = sz + 3
    bw = sz - 2
    bh = sz + 2
    pts = [(cx-tw, cy-bh), (cx+tw, cy-bh),
           (cx+bw, cy+bh), (cx-bw, cy+bh)]
    pygame.draw.polygon(surf, KRD, [(p[0]+1, p[1]+1) for p in pts])
    pygame.draw.polygon(surf, KR,  pts)

    # Wider white zone (bold look = more face room)
    stripe = max(2, sz // 6)
    wl = cx - tw + stripe
    wr = cx + tw - stripe
    wp = [(wl, cy-bh+1), (wr, cy-bh+1),
          (wr - (tw-bw)*stripe//sz, cy+bh-1),
          (wl + (tw-bw)*stripe//sz, cy+bh-1)]
    pygame.draw.polygon(surf, W, wp)

    # Hair (larger bump)
    zw = wr - wl
    pygame.draw.ellipse(surf, H,
        (wl + 1, cy - bh + 1, zw - 2, sz // 2 + 4))

    # Face
    fc_x = cx
    fy = cy - sz // 5
    frx = max(4, zw // 4 + 1)
    fry = max(5, sz // 3 + 1)
    pygame.draw.ellipse(surf, S, (fc_x-frx, fy-fry, frx*2, fry*2))

    # THICK glasses (2px outline)
    gr = max(2, frx // 2)
    g_y = fy - 1
    pygame.draw.circle(surf, K, (fc_x - gr - 1, g_y), gr + 1, 2)
    pygame.draw.circle(surf, K, (fc_x + gr + 1, g_y), gr + 1, 2)
    pygame.draw.line(surf, K, (fc_x - 1, g_y), (fc_x + 1, g_y), 2)

    # Prominent goatee
    chin_y = fy + fry
    gt_h   = max(5, sz // 3)
    pygame.draw.polygon(surf, H,
        [(fc_x - gt_h, chin_y),
         (fc_x + gt_h, chin_y),
         (fc_x, chin_y + gt_h + 2)])
    pygame.draw.polygon(surf, (185, 180, 175),
        [(fc_x - gt_h, chin_y),
         (fc_x + gt_h, chin_y),
         (fc_x, chin_y + gt_h + 2)], 1)

    # THICK bow tie
    bt_y  = chin_y - 2
    bt_hw = max(4, frx)
    bt_hh = max(3, sz // 6)
    pygame.draw.polygon(surf, K,
        [(fc_x - 1, bt_y),
         (fc_x - bt_hw - 1, bt_y - bt_hh - 1),
         (fc_x - bt_hw - 1, bt_y + bt_hh + 1)])
    pygame.draw.polygon(surf, K,
        [(fc_x + 1, bt_y),
         (fc_x + bt_hw + 1, bt_y - bt_hh - 1),
         (fc_x + bt_hw + 1, bt_y + bt_hh + 1)])
    pygame.draw.circle(surf, K, (fc_x, bt_y), max(2, bt_hh // 2 + 1))

    _kfc_text(surf, cx, cy + bh - 1, wr - wl)


# ── V4: Heraldic Shield + Gold trim ──────────────────────────────────────────
def draw_v4(surf, cx, cy, sz, pulse=0.0):
    _shadow(surf, cx, cy, sz + 1)

    # Pulsing gold aura
    pa = max(0, int(28 + 20 * math.sin(pulse * 1.8)))
    aura = pygame.Surface(((sz+6)*2, (sz+6)*2), pygame.SRCALPHA)
    pygame.draw.circle(aura, (*G, pa), (sz+6, sz+6), sz+6)
    surf.blit(aura, (cx-sz-6, cy-sz-6))

    sw  = sz + 2
    sh  = sz + 3
    shield = [
        (cx - sw, cy - sh),
        (cx + sw, cy - sh),
        (cx + sw, cy + 1),
        (cx,      cy + sh + 2),
        (cx - sw, cy + 1),
    ]
    pygame.draw.polygon(surf, KRD, [(p[0]+1, p[1]+1) for p in shield])
    pygame.draw.polygon(surf, KR,  shield)
    pygame.draw.polygon(surf, G,   shield, 2)  # gold trim

    # White inner field
    m = 3
    inner = [
        (cx - sw + m, cy - sh + m),
        (cx + sw - m, cy - sh + m),
        (cx + sw - m, cy + 1 - m // 2),
        (cx,          cy + sh + 2 - m),
        (cx - sw + m, cy + 1 - m // 2),
    ]
    pygame.draw.polygon(surf, W, inner)

    # Colonel face spanning the white inner field
    il = cx - sw + m + 1
    ir = cx + sw - m - 1
    top_y = cy - sh + m

    zw = ir - il
    fc_x = cx
    hair_h = max(3, sz // 3)
    pygame.draw.ellipse(surf, H,
        (il + 1, top_y, zw - 2, hair_h * 2))

    fy = top_y + hair_h + max(2, sz // 5)
    frx = max(3, zw // 5)
    fry = max(4, sz // 3)
    pygame.draw.ellipse(surf, S, (fc_x-frx, fy-fry, frx*2, fry*2))

    gr  = max(1, frx // 2)
    g_y = fy - 1
    pygame.draw.circle(surf, K, (fc_x - gr - 1, g_y), gr + 1)
    pygame.draw.circle(surf, K, (fc_x + gr + 1, g_y), gr + 1)
    pygame.draw.line(surf, K, (fc_x - 1, g_y), (fc_x + 1, g_y), 1)

    chin_y = fy + fry
    gt_h   = max(3, sz // 4)
    pygame.draw.polygon(surf, H,
        [(fc_x - gt_h + 1, chin_y),
         (fc_x + gt_h - 1, chin_y),
         (fc_x,            chin_y + gt_h)])
    pygame.draw.polygon(surf, (195, 190, 185),
        [(fc_x - gt_h + 1, chin_y),
         (fc_x + gt_h - 1, chin_y),
         (fc_x,            chin_y + gt_h)], 1)

    bt_y  = chin_y - 2
    bt_hw = max(3, frx - 1)
    bt_hh = max(2, sz // 7)
    pygame.draw.polygon(surf, K,
        [(fc_x - 1, bt_y), (fc_x - bt_hw, bt_y - bt_hh), (fc_x - bt_hw, bt_y + bt_hh)])
    pygame.draw.polygon(surf, K,
        [(fc_x + 1, bt_y), (fc_x + bt_hw, bt_y - bt_hh), (fc_x + bt_hw, bt_y + bt_hh)])
    pygame.draw.circle(surf, K, (fc_x, bt_y), max(1, bt_hh // 2))


# ── V5: Retro Horizontal Stripe ───────────────────────────────────────────────
def draw_v5(surf, cx, cy, sz, pulse=0.0):
    _shadow(surf, cx, cy, sz)

    bw = sz + 2
    bh = sz + 2
    rect = pygame.Rect(cx - bw, cy - bh, bw * 2, bh * 2)
    br   = 5

    # White base
    pygame.draw.rect(surf, KRD, rect.inflate(2, 2), border_radius=br + 1)
    pygame.draw.rect(surf, W,   rect,               border_radius=br)

    # Horizontal red/white stripes on bottom half
    n_stripes = 5
    stripe_start = cy
    stripe_end   = cy + bh - 1
    sh = max(1, (stripe_end - stripe_start) // n_stripes)
    for i in range(n_stripes):
        sy = stripe_start + i * sh
        c  = KR if i % 2 == 0 else W
        sr = pygame.Rect(cx - bw + 1, sy, (bw - 1) * 2, sh + 1)
        pygame.draw.rect(surf, c, sr.clip(rect.inflate(-2, -2)))

    # White top half (colonel area)
    top_rect = pygame.Rect(cx - bw + 1, cy - bh + 1, (bw - 1) * 2, bh)
    pygame.draw.rect(surf, W, top_rect)

    # Colonel face in upper half
    _colonel(surf, cx, cy, sz,
             cy - bh + 2, cx - bw + 3, cx + bw - 3)

    # "KFC" in the stripe area (white text on red stripe)
    fnt = pygame.font.Font(None, max(10, sz // 2 + 2))
    lbl = fnt.render("KFC", True, W)
    surf.blit(lbl, (cx - lbl.get_width() // 2,
                    stripe_start + sh // 2 - lbl.get_height() // 2))


# ─────────────────────────────────────────────────────────────────────────────
# Render each variant into its own PNG
# ─────────────────────────────────────────────────────────────────────────────
VARIANTS = [
    ("V1 — Faithful Trapezoid Badge   (red|white|red stripes)", draw_v1, "kfc_v1.png"),
    ("V2 — Circle Medallion           (coin-style)",            draw_v2, "kfc_v2.png"),
    ("V3 — Bold Chunky Icon           (thick outlines)",        draw_v3, "kfc_v3.png"),
    ("V4 — Heraldic Shield + Gold     (crest style)",           draw_v4, "kfc_v4.png"),
    ("V5 — Retro Horizontal Stripes   (apron style)",           draw_v5, "kfc_v5.png"),
]

SZ     = 16          # sprite half-size  (matches MUSHROOM_R + 2)
ZOOM   = 4           # scale factor for visibility
SP_W   = (SZ * 2 + 8) * ZOOM   # sprite cell width  after zoom
SP_H   = (SZ * 2 + 12) * ZOOM  # sprite cell height after zoom
N_COL  = 3           # sprites per row
GAP    = 10
PW     = N_COL * SP_W + (N_COL - 1) * GAP + 30
PH     = SP_H + 50

PULSES = [0.0, math.pi * 0.6, math.pi * 1.4]   # 3 animation phases

for title, fn, fname in VARIANTS:
    panel = pygame.Surface((PW, PH))
    panel.fill(BG)
    for gy in range(12, PH, 24):
        for gx in range(12, PW, 24):
            pygame.draw.circle(panel, (22, 16, 52), (gx, gy), 1)

    hdr = pygame.font.Font(None, 18)
    lbl = hdr.render(title, True, (200, 175, 115))
    panel.blit(lbl, (PW // 2 - lbl.get_width() // 2, 7))

    for col, pulse in enumerate(PULSES):
        # Scratch surface — big enough for sprite + drop shadow
        scratch = pygame.Surface((SZ * 2 + 8, SZ * 2 + 12), pygame.SRCALPHA)
        fn(scratch, SZ + 4, SZ + 4, SZ, pulse)
        zoomed = pygame.transform.scale(
            scratch, (scratch.get_width() * ZOOM, scratch.get_height() * ZOOM))

        x = 15 + col * (SP_W + GAP)
        y = 28
        panel.blit(zoomed, (x, y))

        # Small pulse label
        sub = hdr.render(f"phase {col+1}/3", True, (110, 100, 75))
        panel.blit(sub, (x + SP_W // 2 - sub.get_width() // 2, y + SP_H + 2))

    out = os.path.join(OUT, fname)
    pygame.image.save(panel, out)
    print(f"  saved {fname}")

pygame.quit()
print("Done.")
