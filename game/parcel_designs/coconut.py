"""COCONUT DRINK — tropical-lagoon refresher parcel cosmetic.

A round brown COCONUT cracked open at the top, with a striped STRAW poking up
and a tiny cocktail UMBRELLA — the two beats that say "drink" rather than just
"ball". The identity is the contrast of three masses: a dark spherical coconut,
a pale cut-flesh cap where it's opened, and the bright straw+umbrella crown
rising out of it. No other parcel is a round tropical vessel, so the circle plus
the umbrella silhouette carries the read before colour even resolves.

22px read tradeoffs (WHY): at true size the coconut is reduced to ONE bold
filled circle with a single shading crescent — micro fibre texture just turns to
mud, so the volume is sold by a dark lower-shade arc and a small top highlight
instead. The cut-open top is a flat pale ellipse seated ON the sphere so the
"opened" read survives the downscale without a fussy rim. The straw is held
2px-thick with two hard red bands (a striped diagonal collapses at 22px) and is
tilted so it stays a distinct stroke against the umbrella rather than fusing into
it. The umbrella is a small flat fan of two pink tones with a centre pole — kept
compact and pulled toward centre so the gameplay rotozoom never clips it as the
crown swings out across Pip's bank arc. A baked dark outline (inflated, drawn
first) carries the round shape on bright DAY sky; a warm sand keyline rim inside
is the NIGHT lifeline; everything is held off the surface edges so the straw and
umbrella never clip under rotation.
"""
import pygame

# Tight tropical palette tuned so IDENTITY RIDES ON VALUE, not just hue, so the
# drink read survives grayscale. The straw is engineered to be the BRIGHTEST
# object in the sprite (a hot light-coral that desaturates to a near-white
# stroke), the umbrella is pushed DARKER than the straw with a hard value step
# between its two halves, and the husk runs a wide light->dark gradient. In
# grayscale the eye then reads three stacked values: dark husk, a bright thin
# straw, and a two-tone parasol — a drink, not a fused dark ball.
COCO = (138,  90,  52)        # coconut husk brown (mid body) — raised a notch
COCO_SHADE = ( 84,  50,  24)  # darker lower crescent — gives the sphere volume
COCO_HI = (176, 128,  86)     # broad upper-left highlight on the husk
FLESH = (244, 234, 214)       # pale cut-open top (the "opened" cue)
FLESH_SHADE = (210, 192, 162) # flesh rim shadow so the cut reads as a hollow
# Straw = the value anchor. Light coral, not deep red: its grayscale luminance
# (~0.6) tops everything but the flesh, so desaturated it stays a bright stroke.
STRAW = (252, 120, 110)       # bright coral straw — the value eye-magnet
STRAW_HI = (255, 232, 224)    # near-white band highlight (the brightest pixel)
# Umbrella halves: both DARKER (lower luminance) than the straw, with a hard
# value step between them so the parasol shows a lit/shade edge in grayscale.
UMB_A = (220, 110, 150)       # umbrella lit half  (mid value)
UMB_B = (150,  58,  98)       # umbrella shade half (clearly darker — hard step)
LEAF = ( 70, 178,  98)        # green leaf wedge — one readable garnish
OUTLINE = ( 42,  26,  14)     # dark, high-value: reads on bright day sky
KEYLINE = (236, 206, 160)     # warm sand rim — the NIGHT lifeline


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static coconut sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Coconut sphere geometry. A big bold circle held low on the surface so the
    # straw + umbrella crown has room above without clipping the surface edge
    # under the gameplay rotozoom.
    R = 13                        # coconut radius
    ccy = 27                      # coconut centre y (biased low)
    ccx = cx

    # The cut-open top: a flat pale ellipse seated on the upper sphere. Its line
    # is where the straw + umbrella emerge. Widened and nudged forward on the lit
    # (left) side so a sliver of pale rim is always visible in front of the straw
    # base — the most grayscale-safe bright mass after the straw itself.
    cut_w, cut_h = 20, 7
    cut_cy = ccy - 8
    cut_rect = pygame.Rect(ccx - cut_w // 2 - 1, cut_cy - cut_h // 2, cut_w, cut_h)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.circle(surf, OUTLINE, (ccx, ccy), R + 2)

    # --- Coconut husk body: a clear light->dark gradient so the sphere never
    # collapses to a flat dark disc. The shade crescent is pushed
    # tighter to the lower-right edge so it no longer dominates, and a broad,
    # soft upper-left highlight widens the lit zone.
    pygame.draw.circle(surf, COCO, (ccx, ccy), R)
    # Lower-right shade crescent: a darker circle shifted further off-centre so it
    # only crescents the rim, leaving most of the disc in the lighter mid-brown.
    shade = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(shade, COCO_SHADE, (ccx + 5, ccy + 6), R)
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (ccx, ccy), R)
    shade.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, 0))
    # Broad upper-left highlight (two stacked circles, the outer softer) to lift
    # and widen the lit side of the husk so the volume reads as a lit sphere.
    pygame.draw.circle(surf, COCO_HI, (ccx - 4, ccy - 4), 6)
    pygame.draw.circle(surf, FLESH_SHADE, (ccx - 5, ccy - 5), 3)

    # --- Cut-open pale top: outline ellipse, flesh fill, and a shadow rim so the
    # opening reads as a hollow the straw drinks from.
    pygame.draw.ellipse(surf, OUTLINE, cut_rect.inflate(3, 3))
    pygame.draw.ellipse(surf, FLESH, cut_rect)
    # A thin lower-rim shadow inside the flesh so it reads concave, not domed.
    inner = cut_rect.inflate(-4, -2)
    pygame.draw.arc(surf, FLESH_SHADE, inner, 3.5, 6.0, 2)

    # --- STRAW: the BRIGHTEST object in the sprite — a tilted bright coral stroke
    # rising from the flesh, engineered so that in grayscale it stays a near-white
    # stroke standing clear of the darker husk and umbrella. A continuous bright
    # core highlight runs its full length so its luminance never drops below the
    # parasol's. Tilted opposite the umbrella so the two crown elements separate.
    straw_bot = (ccx + 3, cut_cy)
    straw_top = (ccx + 9, cut_cy - 15)
    pygame.draw.line(surf, OUTLINE, straw_bot, straw_top, 5)   # baked outline
    pygame.draw.line(surf, STRAW, straw_bot, straw_top, 3)
    # A near-white core highlight down the lit edge of the straw — this is the
    # brightest stroke in the whole sprite, the value anchor for grayscale.
    pygame.draw.line(surf, STRAW_HI, (straw_bot[0] - 1, straw_bot[1] - 1),
                     (straw_top[0] - 1, straw_top[1] + 1), 1)
    pygame.draw.line(surf, STRAW_HI, (ccx + 5, cut_cy - 6),
                     (ccx + 7, cut_cy - 9), 2)

    # --- LEAF: one enlarged green wedge peeking above the rim on the RIGHT, the
    # side opposite the umbrella, so the garnish is a single readable mass instead
    # of dead weight. Drawn behind the straw base so the straw stays the hero.
    pygame.draw.polygon(surf, OUTLINE, [
        (ccx + 5, cut_cy - 2), (ccx + 13, cut_cy - 9), (ccx + 9, cut_cy - 2)])
    pygame.draw.polygon(surf, LEAF, [
        (ccx + 6, cut_cy - 2), (ccx + 12, cut_cy - 8), (ccx + 9, cut_cy - 2)])

    # --- UMBRELLA: a compact flat fan of two pinks on a short pole, pulled ~1px
    # tighter to centre and down toward the flesh line so the crown stays inside
    # the rotation envelope and never clips at extreme bank. The two halves carry
    # a HARD value step (UMB_A lit, UMB_B clearly darker) so the parasol shows a
    # lit/shade edge in grayscale — and both stay darker than the bright straw.
    fan_y = cut_cy - 8                 # the umbrella's brim line (lowered)
    apex = (ccx - 4, cut_cy - 12)      # parasol tip, tighter to centre + lower
    pole_bot = (ccx - 3, cut_cy - 1)
    pygame.draw.line(surf, OUTLINE, pole_bot, apex, 3)         # baked outline
    pygame.draw.line(surf, COCO_SHADE, pole_bot, apex, 1)
    # Fan: a symmetric outlined triangle split into a lit and a (darker) shade
    # half so it reads as a parasol with a value edge, not a flat shard.
    left = (apex[0] - 6, fan_y)
    right = (apex[0] + 6, fan_y)
    apex_pt = (apex[0], apex[1] + 1)
    pygame.draw.polygon(surf, OUTLINE, [
        (apex[0], apex[1] - 1), (left[0] - 1, fan_y + 1),
        (right[0] + 1, fan_y + 1)])
    pygame.draw.polygon(surf, UMB_A, [apex_pt, left, (apex[0], fan_y)])
    pygame.draw.polygon(surf, UMB_B, [apex_pt, (apex[0], fan_y), right])
    # A brim shadow line + a topknot so the parasol reads finished; the topknot
    # uses the bright straw colour to tie the crown together.
    pygame.draw.line(surf, UMB_B, (left[0], fan_y), (right[0], fan_y), 1)
    pygame.draw.circle(surf, STRAW_HI, (apex[0], apex[1] - 1), 1)

    # --- Warm sand keyline rim INSIDE the outline — the NIGHT lifeline that glows
    # on dark sky while staying subtle on day. Traces the coconut sphere.
    pygame.draw.circle(surf, KEYLINE, (ccx, ccy), R, 1)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
