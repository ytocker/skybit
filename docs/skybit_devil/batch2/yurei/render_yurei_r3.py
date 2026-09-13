"""
Yurei — the trailing-hem white vengeful ghost  [COOL GLOW: BLUE-CYAN HITODAMA]

Review-sheet renderer (headless). Draws the ONE locked concept from
batch2/brainstorm_locked15.md: a pale oval face curtained by long straight
black hair, huge sorrowful droop-eyes, a white burial kimono tapering into a
legless translucent wisp tail, two limp dangling hands palms-down at the
wrists, plus a hovering BLUE-CYAN hitodama soul-flame; mirrored into its
hitodama lantern-pole prop->pillar — all at large + 32px scales on one
labelled sheet.

House grammar followed verbatim: chibi proportions, FLAT saturated fills +
hard ink keylines, form via the dark-core -> flat-fill -> top-left rim-sheen
TRIAD, silhouette POP via a 1px outline grown from the alpha mask,
supersampled then smoothscaled down. PINNED PALETTE hexes are used exactly so
the hitodama stays a distinctly BLUE-CYAN cool glow (never traded with
Kitsune's mint-green), and the mournful FACE-under-hair read keeps it clear of
Hollow's faceless hood.

Round 2 resolves the AD critique, headlined by the face: the whole reason
Yurei isn't batch-1's faceless Hollow is a FACE that must survive 32px. So the
droop-eyes are rebuilt as real positive DARKER shapes (large downturned ink
ovals with a bright lower-lid sheen so they read as eyes, not socket shadow),
a clear downturned mouth + brow are added, and the hair-curtains are opened
wider at the cheeks so a stranger reads "sad ghost face" at true gameplay
scale. The hitodama is demoted to a SINGLE smaller accent at hand height so
the face wins the focal contest; the limp hands are pushed out past the kimono
outline as dark notches; and the wisp is resolved into smooth fading lobes
rather than a torn hem.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (verbatim from the locked brief) ──────────────────────────
KIMONO      = (236, 238, 240)   # pale-white kimono base
KIMONO_SH   = (168, 182, 196)   # cool-blue shade (dark-core)
HAIR        = ( 34,  32,  40)   # ink-black hair accent
HITODAMA    = (120, 206, 232)   # BLUE-CYAN hitodama glow (the blue cool glow)
LAVENDER    = (184, 182, 212)   # faint-lavender rim
SOCKET      = ( 70,  78,  96)   # deep-shadow socket
INK         = ( 26,  28,  34)   # keyline
SHEEN       = (248, 250, 252)   # top-left rim-sheen

# derived working tones (kept inside the pinned families)
HAIR_SH     = ( 18,  16,  24)   # deepest hair core
HAIR_HI     = ( 60,  62,  78)   # cool sheen sliver on the hair
HITO_CORE   = (224, 248, 255)   # white-hot soul-flame core
HITO_DEEP   = ( 56, 150, 200)   # bluer deep edge of the flame
SKIN        = (224, 230, 236)   # faintly cooler-than-kimono pallid face
SKIN_SH     = (176, 190, 206)   # face dark-core hollow
# the EYE ink: darker than the socket so the eyes read as positive features
# (not ambient shadow). Deepened ~15% from round 2 so the two eye-marks are the
# LAST features to survive the final downsample at true 32px.
EYE_INK     = ( 30,  32,  46)   # deep cool eye-mass (a touch warmer than hair)
EYE_DEEP    = ( 16,  18,  28)   # eye core / lash line (deepened for 32px contrast)
# a NEUTRAL cool-grey/white lower-lid catch — deliberately NOT cyan. The cyan
# must belong to the hitodama alone, else the brightest cyan on the figure is
# her eyes and she reads demonic/glowing-eyed rather than wistful.
LID_SHEEN   = (206, 214, 224)   # neutral cool-grey lower-lid sheen (no cyan)
POLE_WOOD   = (150, 140, 132)   # weathered wood lantern-pole (cool-grey neutral)
POLE_SH     = (104,  98,  96)
POLE_HI     = (196, 190, 184)
PAPER       = (228, 232, 236)   # paper lantern-frame panel

SS = 4   # supersample factor


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def grow_outline(src, color=INK, grow=1):
    """1px (post-downscale) ink keyline grown from the alpha mask, the way the
    house silhouette-POP works. Done at supersample scale then carried down by
    the smoothscale, so we grow by `grow*SS` here."""
    g = grow * SS
    mask = pygame.mask.from_surface(src)
    out_surf = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    w, h = src.get_size()
    canvas = pygame.Surface((w + 2 * g, h + 2 * g), pygame.SRCALPHA)
    for dx in range(-g, g + 1):
        for dy in range(-g, g + 1):
            if dx * dx + dy * dy <= g * g:
                canvas.blit(out_surf, (g + dx, g + dy))
    canvas.blit(src, (g, g))
    return canvas, g


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


def hitodama(surf, cx, cy, r, with_glow=True):
    """The signature BLUE-CYAN soul-flame: a teardrop flame-bulb with a wispy
    tail flicking up, triad-lit (deep-blue core / cyan fill / white-hot
    top-left sheen) and wrapped in an additive blue-cyan halo. This is the
    single most load-bearing colour cue separating Yurei from Kitsune."""
    U = SS
    if with_glow:
        glow = radial_glow(int(r + 11 * U), HITODAMA, alpha_center=185, falloff=2.1)
        surf.blit(glow, (cx - glow.get_width() // 2, cy - glow.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)
    # teardrop body: round bulb with a flickering tail rising off the top
    body = [
        (cx, cy - int(r * 2.0)),                       # tail tip (rises up)
        (cx - int(r * 0.42), cy - int(r * 0.9)),
        (cx - r, cy - int(r * 0.1)),
        (cx - int(r * 0.78), cy + int(r * 0.78)),
        (cx, cy + r),
        (cx + int(r * 0.78), cy + int(r * 0.78)),
        (cx + r, cy - int(r * 0.1)),
        (cx + int(r * 0.42), cy - int(r * 0.9)),
    ]
    deep = [(x + int(1.5 * U), y + int(1.5 * U)) for (x, y) in body]
    pygame.draw.polygon(surf, HITO_DEEP, deep)
    pygame.draw.polygon(surf, HITODAMA, body)
    # top-left white-hot rim-sheen + inner core spark
    pygame.draw.polygon(surf, HITO_CORE, [
        (cx, cy - int(r * 1.7)),
        (cx - int(r * 0.36), cy - int(r * 0.7)),
        (cx - int(r * 0.6), cy + int(r * 0.1)),
        (cx - int(r * 0.18), cy - int(r * 0.1)),
    ])
    pygame.draw.circle(surf, HITO_CORE, (cx - r // 4, cy - r // 6), int(r * 0.32))
    pygame.draw.circle(surf, SHEEN, (cx - r // 3, cy - r // 4), int(r * 0.14))


# ─────────────────────────────────────────────────────────────────────────────
#  THE CREATURE — built large (supersampled), then outlined + downscaled.
#  Tall, narrow, top-weighted (face+hair) tapering to a legless wisp.
#  Origin frame ~ 156w x 214h (creature units), scaled by SS.
# ─────────────────────────────────────────────────────────────────────────────

def build_yurei(target_h=200):
    """Return a SRCALPHA surface of Yurei at roughly `target_h` px tall (the
    hitodama glow extends a little beyond the body)."""
    U = SS
    W, H = 156 * U, 214 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    # ---- KIMONO BODY + LEGLESS WISP TAIL (drawn first, behind hair/arms) ----
    # White burial kimono: shoulders down to a soft bell, then dissolving into
    # smooth tapering lobes. The earlier jagged hem read as torn cloth; here
    # the bottom is resolved into a few rounded fading tongues so it reads as a
    # ghost drifting into nothing (wistful), not shredded gore.
    # The earlier hem had a jagged left step that read as torn cloth. Resolved
    # here into smooth symmetric rounded tongues that ease down to the tip so
    # she reads as "drifting into nothing" (wistful), never shredded.
    kimono = P([
        (-30, 70), (-37, 98), (-34, 126), (-38, 150),
        (-32, 164), (-24, 174),                            # smooth left lobe
        (-18, 182), (-12, 178),                            # left tongue notch eased
        (-6, 188), (0, 194),                               # central tongue
        (6, 188), (12, 178), (18, 182),                    # right tongue (mirrored)
        (24, 174), (32, 164), (38, 150), (34, 126), (37, 98), (30, 70),
    ])
    kimono_shade = [(x + 3 * U, y + 3 * U) for (x, y) in kimono]
    pygame.draw.polygon(s, KIMONO_SH, kimono_shade)
    pygame.draw.polygon(s, KIMONO, kimono)

    # left-over-right burial collar fold (the funerary tell) as a dark-core seam
    pygame.draw.polygon(s, KIMONO_SH, P([
        (-16, 72), (0, 96), (16, 72), (10, 70), (0, 86), (-10, 70),
    ]))
    pygame.draw.polygon(s, lerp(KIMONO_SH, SOCKET, 0.35), P([
        (-12, 74), (0, 94), (4, 90), (-6, 74),
    ]))

    # dark-core valley down the kimono centre (flat triad panel)
    pygame.draw.polygon(s, KIMONO_SH, P([
        (-9, 96), (-15, 140), (-9, 176), (0, 190),
        (9, 176), (15, 140), (9, 96),
    ]))

    # the wisp tail FADES rather than tears: three stacked lobes losing opacity
    # toward the tip (stepped alpha over hard flat fills — still procedural, no
    # soft gradient). Reads "dissolving into nothing", not a ragged shred.
    for (y0, y1, half, alpha) in [
        (150, 186, 30, 205), (164, 196, 20, 145), (178, 204, 11, 90),
    ]:
        lobe = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        # rounded, symmetric fading tongue (more apex samples = no hard notch)
        pygame.draw.polygon(lobe, (*lerp(KIMONO, LAVENDER, 0.4), alpha), P([
            (-half, y0), (-int(half * 0.62), y1 - 9), (-int(half * 0.26), y1 - 2),
            (0, y1),
            (int(half * 0.26), y1 - 2), (int(half * 0.62), y1 - 9), (half, y0),
        ]))
        s.blit(lobe, (0, 0))

    # top-left rim-sheen sliver down the kimono's left edge
    pygame.draw.polygon(s, SHEEN, P([
        (-30, 72), (-36, 98), (-32, 126), (-38, 150),
        (-31, 153), (-27, 126), (-30, 98), (-24, 73),
    ]))

    # ---- LIMP DANGLING ARMS + HANDS (palms-down at the wrists) --------------
    # Long flowing kimono sleeves hang from the shoulders; pallid hands droop
    # limp from the wrists. The hands are pushed OUTBOARD of the kimono bell so
    # they break the silhouette as distinct dark notches at 32px (a key
    # separator from any smooth hooded shape).
    for sx in (-1, 1):
        sleeve = P([
            (sx * 28, 74), (sx * 46, 92), (sx * 50, 126),
            (sx * 44, 150), (sx * 30, 146), (sx * 24, 112), (sx * 22, 84),
        ])
        pygame.draw.polygon(s, KIMONO_SH, [(x + 2 * U, y + 2 * U) for (x, y) in sleeve])
        pygame.draw.polygon(s, KIMONO, sleeve)
        # sleeve-mouth dark-core hollow (where the hand emerges) — a deep notch
        pygame.draw.polygon(s, SOCKET, P([
            (sx * 48, 150), (sx * 52, 130), (sx * 42, 138), (sx * 36, 150),
        ]))
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 28, 76), (sx * 44, 92), (sx * 42, 104),
                (sx * 30, 90), (sx * 26, 80),
            ]))
        # limp hand drooping palm-down, set OUTBOARD past the kimono edge so it
        # protrudes as its own dark-rimmed notch in the outline
        hand = P([
            (sx * 47, 150), (sx * 56, 156), (sx * 58, 172),
            (sx * 51, 182), (sx * 41, 178), (sx * 39, 160),
        ])
        # a deep cool shade UNDER the hand reads as the gap that detaches the
        # notch from the body at small scale
        pygame.draw.polygon(s, SOCKET, [(x + 1 * U, y + 3 * U) for (x, y) in hand])
        pygame.draw.polygon(s, SKIN_SH, [(x + 1 * U, y + 1 * U) for (x, y) in hand])
        pygame.draw.polygon(s, SKIN, hand)
        # slack drooping fingers hanging off the knuckle line
        for fi in range(3):
            fx = sx * (43 + fi * 6)
            pygame.draw.polygon(s, SKIN_SH, P([
                (fx, 174), (fx + sx * 5, 174), (fx + sx * 2, 188 - fi * 3),
            ]))
            pygame.draw.polygon(s, SKIN, P([
                (fx, 174), (fx + sx * 3, 174), (fx + sx * 1, 186 - fi * 3),
            ]))

    # ---- PALE FACE (drawn before hair-curtains so hair frames it) -----------
    # Small oval pallid face, faintly cooler than the kimono. Widened a touch
    # so more face survives between the (opened) hair-curtains.
    face = P([
        (-21, 14), (-23, 31), (-18, 47), (-9, 57), (0, 59),
        (9, 57), (18, 47), (23, 31), (21, 14), (13, 6), (0, 4), (-13, 6),
    ])
    pygame.draw.polygon(s, SKIN_SH, [(x + 2 * U, y + 3 * U) for (x, y) in face])
    pygame.draw.polygon(s, SKIN, face)
    # top-left rim-sheen on the brow
    pygame.draw.polygon(s, SHEEN, P([
        (-20, 14), (-21, 29), (-13, 16), (-2, 8), (-11, 8),
    ]))
    # cheek dark-core hollows (gaunt, sorrowful)
    for sx in (-1, 1):
        pygame.draw.polygon(s, SKIN_SH, P([
            (sx * 18, 37), (sx * 20, 45), (sx * 11, 53), (sx * 10, 43),
        ]))

    # ---- THE FACE FEATURES — the headline 32px fix -------------------------
    # Sorrowful brows: short downward-sloping ink dashes over the eyes give the
    # face an unmistakable "sad" cant even when the eyes themselves blur down.
    for sx in (-1, 1):
        pygame.draw.polygon(s, EYE_DEEP, P([
            (sx * 4, 23), (sx * 15, 26), (sx * 16, 29), (sx * 4, 27),
        ]))

    # huge sorrowful droop-eyes rebuilt as REAL POSITIVE DARK SHAPES: large
    # downturned ink ovals (darker than the surrounding socket so they read as
    # eyes, not ambient shadow) with a bright lower-lid sheen + a cool catch so
    # the eye lifts off the face at true 32px. This is the whole reason Yurei
    # isn't Hollow.
    for sx in (-1, 1):
        eye_cx = cx + int(sx * 9.5 * U)
        eye_cy = int(35 * U)
        # soft socket bed behind the eye so the white face frames the dark mass
        pygame.draw.ellipse(s, lerp(SOCKET, SKIN, 0.35),
                            (eye_cx - int(8 * U), eye_cy - int(6 * U),
                             int(15 * U), int(13 * U)))
        # the eye itself: a big downturned oval, outer corner dropping down/out
        eye = [
            (eye_cx - int(sx * 7 * U), eye_cy - int(3 * U)),   # inner-top
            (eye_cx + int(sx * 5 * U), eye_cy - int(5 * U)),   # toward outer-top
            (eye_cx + int(sx * 7 * U), eye_cy + int(4 * U)),   # outer corner DROOPS
            (eye_cx + int(sx * 2 * U), eye_cy + int(7 * U)),   # bottom
            (eye_cx - int(sx * 6 * U), eye_cy + int(5 * U)),   # inner-bottom
        ]
        pygame.draw.polygon(s, EYE_INK, eye)
        # darkest lash core along the upper lid
        pygame.draw.polygon(s, EYE_DEEP, [
            (eye_cx - int(sx * 7 * U), eye_cy - int(3 * U)),
            (eye_cx + int(sx * 5 * U), eye_cy - int(5 * U)),
            (eye_cx + int(sx * 4 * U), eye_cy - int(2 * U)),
            (eye_cx - int(sx * 6 * U), eye_cy - int(1 * U)),
        ])
        # NEUTRAL cool-grey lower-lid sheen — the 1px lighter catch that says
        # "EYE" at 1x WITHOUT any cyan. Sad ghost = dark mournful eyes, not lit
        # eyes; the cyan stays unique to the hitodama soul-flame.
        pygame.draw.polygon(s, LID_SHEEN, [
            (eye_cx + int(sx * 6 * U), eye_cy + int(4 * U)),
            (eye_cx + int(sx * 2 * U), eye_cy + int(7 * U)),
            (eye_cx - int(sx * 5 * U), eye_cy + int(5 * U)),
            (eye_cx - int(sx * 5 * U), eye_cy + int(6 * U)),
            (eye_cx + int(sx * 2 * U), eye_cy + int(8 * U)),
            (eye_cx + int(sx * 6 * U), eye_cy + int(5 * U)),
        ])

    # tiny nose shadow
    pygame.draw.polygon(s, SKIN_SH, P([(0, 43), (-3, 49), (3, 49)]))
    # RESTORED downturned mournful mouth (lost in round 2) — a clear, deepened
    # frown so the lower face completes the SAD read, not just "startled". A
    # cool-blue-shade under-shadow seats it, an ink crescent dips at the
    # CORNERS (the downturn), and a faint lower-lip catch closes it. This is the
    # beat that tips the oval from "a face" to "a SAD face".
    pygame.draw.polygon(s, KIMONO_SH, P([
        (-8, 51), (0, 53), (8, 51), (9, 56), (0, 60), (-9, 56),
    ]))
    # the frown ink: corners ride UP-and-out, centre dips DOWN -> a downturn
    pygame.draw.polygon(s, EYE_INK, P([
        (-8, 51), (-4, 52), (0, 55), (4, 52), (8, 51),
        (7, 53), (0, 58), (-7, 53),
    ]))
    pygame.draw.polygon(s, EYE_DEEP, P([
        (-7, 52), (0, 55), (7, 52), (5, 53), (0, 56), (-5, 53),
    ]))
    # faint neutral lower-lip catch (no cyan)
    pygame.draw.polygon(s, LID_SHEEN, P([
        (-6, 57), (0, 60), (6, 57), (4, 58), (0, 60), (-4, 58),
    ]))

    # ---- LONG STRAIGHT BLACK HAIR-CURTAINS (hard triad panels) --------------
    # Centre-parted, draping straight down BOTH sides past the shoulders. Per
    # the AD note the inner edges are pulled ~12% WIDER apart at the cheeks so
    # the pale face is clearly framed (not pinched shut) — a stranger must read
    # "sad face under hair", never "faceless hood".
    # crown cap + part
    pygame.draw.polygon(s, HAIR, P([
        (-22, 16), (-24, 2), (-13, -8), (0, -11), (13, -8),
        (24, 2), (22, 16), (11, 6), (0, 4), (-11, 6),
    ]))
    for sx in (-1, 1):
        curtain = P([
            (sx * 22, 8), (sx * 31, 26), (sx * 33, 64),
            (sx * 29, 104), (sx * 25, 134), (sx * 17, 150),
            (sx * 14, 132), (sx * 16, 96), (sx * 18, 56),   # inner edge held off the cheek
            (sx * 17, 30), (sx * 11, 16),
        ])
        # hair dark-core bed
        pygame.draw.polygon(s, HAIR_SH, [(x + 2 * U, y + 2 * U) for (x, y) in curtain])
        pygame.draw.polygon(s, HAIR, curtain)
        # a few straight strand-seams (flat triad grooves, not soft form)
        for k in range(3):
            ox = sx * (18 + k * 5)
            pygame.draw.line(s, HAIR_SH,
                             (cx + int(ox * U), int((20 + k * 4) * U)),
                             (cx + int((ox + sx * 3) * U), int((132 - k * 6) * U)),
                             max(1, int(1.4 * U)))
        # cool top-left sheen sliver on the outer left curtain
        if sx == -1:
            pygame.draw.polygon(s, HAIR_HI, P([
                (sx * 22, 10), (sx * 30, 28), (sx * 31, 60),
                (sx * 27, 60), (sx * 26, 28), (sx * 19, 12),
            ]))
        # LAVENDER spectral rim catch along the outer hair edge (top-left per the
        # triad) — lifted a touch from round 2 so she reads gentle-spectral off a
        # dark night sky, never grim. Slightly thicker + carried lower.
        pygame.draw.line(s, LAVENDER,
                         (cx + int(sx * 31 * U), int(20 * U)),
                         (cx + int(sx * 27 * U), int(120 * U)),
                         max(1, int(2.1 * U)))
    # face-framing inner wisps falling over the temples — kept narrow and held
    # off the eyes so they don't re-pinch the face shut
    for sx in (-1, 1):
        pygame.draw.polygon(s, HAIR, P([
            (sx * 11, 8), (sx * 18, 14), (sx * 17, 34),
            (sx * 13, 46), (sx * 10, 34), (sx * 9, 16),
        ]))

    # ---- HOVERING HITODAMA SOUL-FLAME ---------------------------------------
    # Demoted to a SINGLE smaller blue-cyan soul-flame drifting at hand height
    # so the face wins the focal contest; the hitodama is the second read + the
    # obvious prop->pillar tie. (Round 1's three flames out-shouted the face.)
    hitodama(s, cx + int(58 * U), int(150 * U), int(7 * U))

    # ---- ink keyline grown from the alpha mask + downscale ------------------
    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


# ─────────────────────────────────────────────────────────────────────────────
#  THE PROP -> PILLAR — hitodama soul-flame LANTERN-POLE.
#  Slim banded wooden pole = repeatable body; a hovering blue-white hitodama
#  soul-flame in a paper frame = gap-edge cap drifting at the gap.
# ─────────────────────────────────────────────────────────────────────────────

def _pole_body(s, cx, P, top_y, bot_y):
    """Repeatable slim banded pole shaft (shared by prop + pillar)."""
    U = SS
    pw = 7
    shaft = [(cx - pw * U, int(top_y * U)), (cx + pw * U, int(top_y * U)),
             (cx + pw * U, int(bot_y * U)), (cx - pw * U, int(bot_y * U))]
    pygame.draw.polygon(s, POLE_SH, [(x + 2 * U, y) for (x, y) in shaft])
    pygame.draw.polygon(s, POLE_WOOD, shaft)
    # top-left sheen column
    pygame.draw.rect(s, POLE_HI,
                     (cx - pw * U, int(top_y * U), int(2.2 * U),
                      int((bot_y - top_y) * U)))
    # slim banding (the repeatable banding for the pillar body)
    for by in range(int(top_y) + 10, int(bot_y), 20):
        pygame.draw.rect(s, POLE_SH,
                         (cx - pw * U, by * U, pw * 2 * U, int(3 * U)))
        pygame.draw.rect(s, POLE_HI,
                         (cx - pw * U, by * U, pw * 2 * U, int(1.0 * U)))


def _lantern_frame(s, cx, ocy, P, glow_dir=1):
    """Paper lantern-frame box holding a blue-cyan hitodama at its heart.
    `glow_dir` flips the flame tail up (+1, prop) or lets the cap hang the
    flame into the gap (-1, pillar) — same construction, mirrored seat."""
    U = SS
    # paper frame: a soft-cornered box with thin wood ribs, glowing from within
    fw, fh = 18, 22
    box = [(cx - fw * U, int((ocy - fh) * U)), (cx + fw * U, int((ocy - fh) * U)),
           (cx + fw * U, int((ocy + fh) * U)), (cx - fw * U, int((ocy + fh) * U))]
    pygame.draw.polygon(s, POLE_SH, [(x + 2 * U, y + 2 * U) for (x, y) in box])
    # paper panels tinted by the soul-flame within
    pygame.draw.polygon(s, lerp(PAPER, HITODAMA, 0.35), box)
    pygame.draw.polygon(s, lerp(PAPER, HITODAMA, 0.12),
                        [(cx - fw * U, int((ocy - fh) * U)),
                         (cx - int(fw * 0.2) * U, int((ocy - fh) * U)),
                         (cx - int(fw * 0.2) * U, int((ocy + fh) * U)),
                         (cx - fw * U, int((ocy + fh) * U))])
    # wood top & bottom caps of the lantern frame
    for yy in (ocy - fh, ocy + fh):
        pygame.draw.rect(s, POLE_WOOD,
                         (cx - int((fw + 3) * U), int(yy * U) - int(2 * U),
                          int((fw + 3) * 2 * U), int(5 * U)))
        pygame.draw.rect(s, POLE_HI,
                         (cx - int((fw + 3) * U), int(yy * U) - int(2 * U),
                          int((fw + 3) * 2 * U), int(1.4 * U)))
    # vertical paper ribs
    for rx in (-9, 0, 9):
        pygame.draw.line(s, POLE_SH,
                         (cx + int(rx * U), int((ocy - fh + 2) * U)),
                         (cx + int(rx * U), int((ocy + fh - 2) * U)),
                         max(1, int(1.2 * U)))
    # the BLUE-CYAN hitodama burning inside the frame
    flame = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    hr = int(8 * U)
    if glow_dir > 0:
        hitodama(flame, cx, int(ocy * U) + int(2 * U), hr)
    else:
        # mirror: flame tail flicks downward into the gap
        tmp = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        hitodama(tmp, cx, flame.get_height() // 2, hr)
        tmp = pygame.transform.flip(tmp, False, True)
        oy = int(ocy * U) - flame.get_height() // 2 - int(2 * U)
        flame.blit(tmp, (0, oy))
    s.blit(flame, (0, 0))


def build_pole(target_h=210):
    """The prop: slim banded wooden lantern-pole topped by a paper-framed
    blue-cyan hitodama soul-flame drifting at the crown."""
    U = SS
    W, H = 64 * U, 232 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    _pole_body(s, cx, P, top_y=56, bot_y=226)
    _lantern_frame(s, cx, ocy=34, P=P, glow_dir=1)

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


def build_pillar(target_h=210):
    """Mirror the pole prop into a clean repeatable PILLAR: the banded pole
    repeats as the body, the paper-framed hitodama lantern is the detachable
    gap-edge cap drifting at the gap. Shown as a top cap so the gap is at the
    bottom (the way Big Reapy's bone-bident mirrors)."""
    U = SS
    W, H = 64 * U, 232 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    # repeatable pole body filling from the top down to the gap line
    _pole_body(s, cx, P, top_y=0, bot_y=170)
    # detachable gap-edge cap at the BOTTOM: paper lantern with the hitodama
    # hanging its flame down into the gap
    _lantern_frame(s, cx, ocy=196, P=P, glow_dir=-1)

    outlined, _ = grow_outline(s, INK, grow=1)
    ow, oh = outlined.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        outlined, (max(1, int(ow * scale)), max(1, int(oh * scale))))


# ─────────────────────────────────────────────────────────────────────────────
#  SHEET COMPOSITION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    SHEET_W, SHEET_H = 760, 580
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    # neutral-cool review backdrop so the pale-white + blue-cyan read honestly
    for y in range(SHEET_H):
        t = y / SHEET_H
        sheet.fill(lerp((38, 42, 54), (20, 24, 34), t), (0, y, SHEET_W, 1))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    tiny = pygame.font.SysFont("dejavusans", 11)

    def label(txt, x, y, f=small, col=(230, 236, 244)):
        sheet.blit(f.render(txt, True, (0, 0, 0)), (x + 1, y + 1))
        sheet.blit(f.render(txt, True, col), (x, y))

    label("YUREI  (round 3 / final)  — trailing-hem white vengeful ghost  [BLUE-CYAN HITODAMA]",
          16, 12, font)
    label("round-3 fixes: CYAN eye-glints KILLED (eyes plain dark + neutral lid-catch, cyan now hitodama-only)  ·  downturned SAD mouth RESTORED  ·  eye darks +15%  ·  wisp softened  ·  lavender rim lifted",
          16, 36, tiny, (176, 196, 216))

    # large creature
    big = build_yurei(target_h=320)
    bx = 36
    by = 70
    sheet.blit(big, (bx, by))
    label("creature (large)", bx + big.get_width() // 2 - 42, by + big.get_height() + 4)

    # 32px creature: 3x nearest-neighbor zoom + true 32px swatch side by side
    small_creat = build_yurei(target_h=32)
    sy = by + big.get_height() + 26
    zoom = pygame.transform.scale(small_creat,
                                  (small_creat.get_width() * 3,
                                   small_creat.get_height() * 3))
    zx = bx + 8
    sheet.blit(zoom, (zx, sy))
    sheet.blit(small_creat, (zx + zoom.get_width() + 16, sy + zoom.get_height() - 32))
    label("32px read (3x + actual)", zx, sy + zoom.get_height() + 4, tiny)

    # a tight FACE crop (5x) so the headline fix is auditable at a glance
    face32 = build_yurei(target_h=32)
    # crop the upper ~45% (the face/hair region) and blow it up
    fw, fh = face32.get_width(), face32.get_height()
    crop = face32.subsurface((0, 0, fw, int(fh * 0.48))).copy()
    face_zoom = pygame.transform.scale(crop, (crop.get_width() * 6, crop.get_height() * 6))
    fzx = zx + zoom.get_width() + 60
    fzy = sy
    sheet.blit(face_zoom, (fzx, fzy))
    label("face @32px (6x crop)", fzx, fzy + face_zoom.get_height() + 4, tiny,
          (150, 220, 232))

    # large pole prop
    pole = build_pole(target_h=360)
    stx = 332
    sty = 70
    sheet.blit(pole, (stx, sty))
    label("hitodama lantern-pole (prop)", stx - 18, sty + pole.get_height() + 2, tiny)

    # mirrored pillar
    pill = build_pillar(target_h=360)
    px = 442
    sheet.blit(pill, (px, sty))
    label("-> PILLAR mirror", px - 2, sty + pill.get_height() + 2, tiny)
    label("(repeatable pole +", px - 2, sty + pill.get_height() + 16, tiny,
          (160, 184, 210))
    label(" hitodama gap cap)", px - 2, sty + pill.get_height() + 28, tiny,
          (160, 184, 210))

    # 32px pole + pillar reads
    pole32 = build_pole(target_h=32)
    pill32 = build_pillar(target_h=32)
    z2 = pygame.transform.scale(pole32,
                                (pole32.get_width() * 3, pole32.get_height() * 3))
    z3 = pygame.transform.scale(pill32,
                                (pill32.get_width() * 3, pill32.get_height() * 3))
    zy = 76
    zx2 = 562
    sheet.blit(z2, (zx2, zy))
    sheet.blit(z3, (zx2 + z2.get_width() + 24, zy))
    sheet.blit(pole32, (zx2 + 6, zy + z2.get_height() + 8))
    sheet.blit(pill32, (zx2 + z2.get_width() + 30, zy + z2.get_height() + 8))
    label("32px pole / pillar", zx2, zy + z2.get_height() + 34, tiny)

    # palette swatch strip
    swatches = [
        ("kimono", KIMONO), ("kimono-sh", KIMONO_SH), ("hair", HAIR),
        ("hitodama", HITODAMA), ("lavender", LAVENDER), ("socket", SOCKET),
        ("ink", INK), ("sheen", SHEEN),
    ]
    swx, swy = 562, 378
    for i, (nm, col) in enumerate(swatches):
        ry = swy + i * 22
        pygame.draw.rect(sheet, col, (swx, ry, 26, 18))
        pygame.draw.rect(sheet, (10, 10, 14), (swx, ry, 26, 18), 1)
        label(nm, swx + 32, ry + 3, tiny)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
