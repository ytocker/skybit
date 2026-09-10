"""arch-black tl3 hang-tag concept — round 2 render (obsidian arch-top boutique tag).

Standalone review harness: monkey-patches store_cards.price_chip with the
arch-black tag, renders mummy/kitsune cards in affordable + locked states, and
tiles them into docs/store_price_tl3/arch_black/round_2.png. Not wired into the
live store — exploration only.

Round-2 fixes (all art-director notes from round 1):
 1. Champagne edge hairline is now applied POST-downscale on the final 1×
    surface. The face (74×78) lived at 2× before a 0.5× smoothscale, so a
    1px arc stroke on the face became a 0.5px ghost — and the arc bounding
    rect (0,0,74,74) placed the right endpoint at x=74, one pixel outside the
    74-wide surface, causing the right shoulder to be clipped and then blended
    with the blue card bg. Post-downscale we draw at radius=18 in 1× space
    where x=41 is well inside the 162px card — no clipping, no bg-bleed.
 2. Right-edge hue fixed — all four hairline strokes now share the identical
    (210,190,150,230) champagne 4-tuple. The old right-side blue fringe was
    entirely a consequence of the clipping + smoothscale bleed fixed above.
 3. Base contrast lifted: grad_bot nudged from (22,20,26) → (36,34,42) so the
    obsidian slab sits above the deep-navy card background.
 4. Debossed inner border removed — invisible at 1× and not one of the two
    official flourishes.
 5. 1px obsidian gap ring between grommet and coin_ring: both shared y=23 and
    risked blobbing into one metallic mass; a face-coloured disc at the
    contact row visually separates them.
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font
sd.load()

# Communicates the face blit position and variant from price_chip to
# render_card_1x so the post-downscale hairline can be placed precisely.
_last_price_face: tuple | None = None


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def coin_ring(surf, cx, cy):
    r = sc.m(5)
    s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
    cc = (r+1, r+1)
    pygame.draw.circle(s, (156, 116, 58), cc, r)
    pygame.draw.circle(s, (48, 28, 10), cc, r, 1)
    pygame.draw.circle(s, (0, 0, 0, 0), cc, sc.m(3)+1)
    surf.blit(s, (cx-r-1, cy-r-1))


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    global _last_price_face
    # affordability is driven by variant here so the review sheet can force a
    # locked take regardless of the (zero) fixture wallet.
    affordable = (variant != "locked")
    text = _abbr(text)

    FACE_W = 74
    FACE_H = 78
    ARCH_R = 37  # semicircle radius = FACE_W // 2

    if affordable:
        # grad_bot lifted from (22,20,26) → (36,34,42) so the obsidian slab
        # reads above the deep-navy card background (~16 delta was invisible).
        grad_top, grad_bot = (38, 36, 42), (36, 34, 42)
        price_col = (242, 224, 178)
        steel, steel_ul, steel_lr = (150, 158, 166), (190, 198, 204), (60, 68, 76)
        base_shadow = (200, 180, 130, 80)
    else:
        grad_top, grad_bot = (34, 34, 38), (30, 30, 34)
        price_col = (140, 140, 146)
        # steel kept, brightness dropped ~20 so the locked tag reads inert.
        steel, steel_ul, steel_lr = (130, 138, 146), (170, 178, 184), (40, 48, 56)
        base_shadow = (200, 180, 130, 60)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)

    # ── near-black arch fill: 2-stop vertical gradient masked to the tombstone
    # silhouette (semicircle crown atop a flat-bottom rect). The faint 2-stop
    # cast reads as depth on an otherwise matte obsidian slab.
    grad = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    for y in range(FACE_H):
        t = y / (FACE_H - 1)
        grad.fill(lerp_color(grad_top, grad_bot, t), (0, y, FACE_W, 1))
    mask = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (ARCH_R, ARCH_R), ARCH_R)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, ARCH_R, FACE_W, FACE_H - ARCH_R),
                     border_bottom_left_radius=sc.m(4),
                     border_bottom_right_radius=sc.m(4))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    face.blit(grad, (0, 0))

    # ── FLOURISH A: champagne edge hairline is drawn AFTER the 0.5× smoothscale
    # in render_card_1x (see below). The arc bounding rect on the 74×78 face
    # placed the right endpoint at x=74 — one pixel outside the surface — which
    # was clipped and then blended with the card's blue background by
    # smoothscale, producing the asymmetric fringe seen in r1. Post-downscale
    # the hairline is applied at 1× pixel-precision with no boundary issues.

    # ── grommet (steel) centred in the arch crown; the void is a real punched
    # hole so the boutique tag reads as physically hung.
    gx, gy = ARCH_R, 14
    outer_r = sc.m(4) + 1   # = 9
    pygame.draw.circle(face, steel, (gx, gy), outer_r)
    aw = max(1, sc.m(1))
    pygame.draw.arc(face, steel_ul, (gx-outer_r, gy-outer_r, outer_r*2, outer_r*2),
                    math.pi/2, math.pi, aw)
    pygame.draw.arc(face, steel_lr, (gx-outer_r, gy-outer_r, outer_r*2, outer_r*2),
                    3*math.pi/2, 2*math.pi, aw)
    pygame.draw.circle(face, (40, 30, 18), (gx, gy), sc.m(3))
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), sc.m(2))

    # ── obsidian gap ring at the grommet-to-coin_ring contact zone.
    # Grommet outer bottom lands at y=gy+outer_r=23; coin_ring outer top also
    # at y=33-sc.m(5)=23 — they share a pixel row and risk reading as one blob.
    # A small disc in the face gradient colour breaks the joint cleanly without
    # looking like an added decoration.
    gap_y = gy + outer_r         # = 23, the contact row
    t_gap = gap_y / (FACE_H - 1)
    gap_col = lerp_color(grad_top, grad_bot, t_gap)
    pygame.draw.circle(face, gap_col, (ARCH_R, gap_y), sc.m(2))

    # ── FLOURISH B: bronze coin ring in the lower crown, byte-identical family
    # unifier. Sits below the grommet, above the price band — no overlap.
    coin_ring(face, ARCH_R, 33)

    # ── price: champagne numeral centred in the rect body with a near-black
    # keyline that bakes to a crisp dark border on the obsidian ground.
    size = 12.0
    f = sc.font(size)
    while (sc._glyph_base(text, f, 0).get_width() > 60 or f.get_height() > 18) \
            and size > 6:
        size -= 0.5
        f = sc.font(size)
    r = sc.plain_text(face, text, f, (ARCH_R, 54), price_col,
                      shadow_a=0, weight=sc.m(1.0), keyline=(12, 10, 14), kw=1)

    # champagne baseline shadow so the numerals sit ON a surface, not float.
    bl = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.line(bl, base_shadow, (r.left, r.bottom+1), (r.right, r.bottom+1), 1)
    face.blit(bl, (0, 0))

    # ── boutique tag hangs in the top-left clear zone of the 2× buffer.
    blit_x = 48 - FACE_W // 2   # = 11
    blit_y = 50 - FACE_H // 2   # = 11
    surf.blit(face, (blit_x, blit_y))

    # Store face geometry for the post-downscale hairline pass in render_card_1x.
    _last_price_face = (blit_x, blit_y, FACE_W, FACE_H, variant)
    return pygame.Rect(blit_x, blit_y, FACE_W, FACE_H)


sc.price_chip = my_price_chip


def render_card_1x(sid, variant):
    """Render one card at live 1× size.

    The hairline is applied AFTER the smoothscale so it lives at true 1×
    pixel resolution. At 2× (the face draw scale) the arc rect (0,0,74,74)
    placed the right arc endpoint outside the surface boundary, causing
    endpoint clipping that smoothscale then blended with the blue card
    background. At 1× the arc radius is 18 in a 162-wide surface so both
    endpoints sit well inside the bounds with zero clipping.
    """
    global _last_price_face
    _last_price_face = None

    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2*inset,
                       sc.CARD_H * sc.SS - 2*inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    card_1x = pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))

    if _last_price_face is not None:
        bx, by, fw, fh, var = _last_price_face
        # Map face blit position from the 2× big-canvas to 1× card coordinates.
        fx   = bx // sc.SS        # = 5
        fy   = by // sc.SS        # = 5
        fw1  = fw // sc.SS        # = 37  (face width in 1×)
        fh1  = fh // sc.SS        # = 39  (face height in 1×)
        # Use fw1-1 for the arc bounding rect width so the circle endpoint at
        # angle=0 lands at x=fx+fw1-1 (=41), well inside the 162-wide surface.
        arc_w = fw1 - 1           # = 36 → circle radius = 18
        ar    = arc_w // 2        # = 18 (arch radius in 1×)

        hair_col = (210, 190, 150, 230) if var != "locked" else (90, 90, 96, 120)

        hl = pygame.Surface((sc.CARD_W, sc.CARD_H), pygame.SRCALPHA)
        # Arc: left endpoint (fx, fy+ar) → right endpoint (fx+arc_w, fy+ar).
        # arc_w=36 keeps right endpoint at fx+36=41, which is the same x
        # as the right side-line, so the join is gapless.
        pygame.draw.arc(hl, hair_col, (fx, fy, arc_w, arc_w), 0, math.pi, 1)
        pygame.draw.line(hl, hair_col, (fx,        fy + ar), (fx,        fy + fh1 - 1), 1)
        pygame.draw.line(hl, hair_col, (fx + fw1 - 1, fy + ar), (fx + fw1 - 1, fy + fh1 - 1), 1)
        pygame.draw.line(hl, hair_col, (fx, fy + fh1 - 2), (fx + fw1 - 1, fy + fh1 - 2), 1)
        card_1x.blit(hl, (0, 0))

    return card_1x


def zoom_left(card_1x):
    crop = card_1x.subsurface((0, 0, 80, 100))
    return pygame.transform.scale(crop, (160, 200))


BG = (8, 8, 20)
PAD = 20
GAP = 12
HDR_H = 40
LABEL_H = 20
CW, CH = sc.CARD_W, sc.CARD_H

cards = {
    "mummy_aff":   render_card_1x("skin_mummy",   sc.PRICE_VARIANT),
    "mummy_lck":   render_card_1x("skin_mummy",   "locked"),
    "kitsune_aff": render_card_1x("skin_kitsune", sc.PRICE_VARIANT),
    "kitsune_lck": render_card_1x("skin_kitsune", "locked"),
}

row1_h = CH
row2_h = 200
total_w = PAD + 4*CW + 3*GAP + PAD
total_h = HDR_H + LABEL_H + row1_h + GAP + row2_h + PAD
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("arch-black · tl3 hang-tag · round 2", True, (255, 220, 80))
canvas.blit(ht, (total_w//2 - ht.get_width()//2, (HDR_H-ht.get_height())//2))

lf = hud_font(7)
card_list = [cards["mummy_aff"], cards["mummy_lck"], cards["kitsune_aff"], cards["kitsune_lck"]]
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
y1 = HDR_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD + i*(CW+GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HDR_H + (LABEL_H-lbl.get_height())//2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2×crop)"), ("mummy_lck", "mummy lck (2×crop)")]):
    x = PAD + i*(160+GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "docs/store_price_tl3/arch_black/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
