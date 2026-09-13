"""Look-dev sheet for the Skybit DEVIL boss — GROUP A take A8 "SOULFORGE".

A sooty BLACKSMITH-DEVIL skull who hammers souls on an anvil: death at the
forge. The identity is a stocky-WORKMAN build (the set's only one) reading
"skull" first, "devil" second — via two flat FILED HORN-STUMPS on the brow
(Hellboy's signature trimmed-down circular stumps, NOT pointed horns) and ONE
absurdly oversized stone gauntlet-FIST (Hellboy's "Right Hand of Doom") gripping
a sledgehammer. A leather ox-blood apron, contained forge-orange sparks.

House style this obeys (the Big-Reapy / warren-clown grammar):
  - CHIBI-STOCKY proportions — broad soot skull, tiny apron body, one giant mitt.
  - FLAT fills + hard 1-2px ink keylines (28,22,30). No within-shape gradients,
    no soft/feathered edges, no bevels, no realistic shading.
  - Form via the triad (`_triad_circle`): dark-core ring -> flat fill -> top-left
    rim sheen. The soot skull + iron hammer read sculpted-but-flat.
  - Silhouette POP via a post-pass 1px ink outline grown from the alpha mask
    (the parrot `_add_outline` recipe).
  - SUPERSAMPLE then smoothscale.

Palette discipline (the per-pick guardrail): SOOT-charcoal skull on COOL
iron/anvil greys — deliberately NOT Brimstone's all-over magma. The forge-orange
is a CONTAINED accent (socket coals + flying sparks + a hot seam at the hammer
strike), never a lava wash. That contained-glow + cool-iron split is the
separator from the magma boulder-skull.

Prop -> pillar mirror: the SLEDGEHAMMER. The banded iron HAFT is the tileable
PILLAR BODY (riveted grip-bands = banding); the heavy anvil-shaped HAMMER-HEAD
is the detachable TOP CAP that rides the gap-edge only, sparks flying INTO the
gap off the striking face. Mirrors top<->bottom into a clean vertical iron post.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/render_skybit_devil_soulforge.py
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── "soot & forge" palette (take A8) ─────────────────────────────────────────
# SOOT-charcoal skull DOMINANT, shaded toward COOL iron-grey (never magma). The
# iron hammer is one value-step cooler/lighter so the prop separates from the
# skull. Forge-orange is a CONTAINED accent only — socket coals, flying sparks,
# and the hot strike seam — so the figure never becomes a lava wash. The dark
# socket/keyline SHAPE must read in grayscale; the ember is never the only cue.
SOOT        = (64, 58, 62)      # soot-charcoal skull fill
SOOT_DK     = (40, 36, 42)      # dark-core ring / under-shade
SOOT_SHEEN  = (104, 100, 108)   # cool top-left rim sheen (iron-grey, not warm)
TOOTH       = (210, 204, 196)   # ash-grey tooth band (dirty bone, sooted)
TOOTH_DK    = (120, 116, 120)   # tooth separators / under-shade

IRON        = (118, 116, 126)   # iron-grey hammer / haft fill
IRON_DK     = (70, 70, 80)      # iron dark-core / groove
IRON_SHEEN  = (176, 178, 188)   # cool steel rim sheen
RIVET       = (150, 150, 160)   # rivet stud highlight

STONE       = (96, 92, 96)      # the stone gauntlet-fist (cool grey rock)
STONE_DK    = (58, 54, 60)
STONE_SHEEN = (140, 138, 146)
STONE_CRACK = (44, 40, 46)      # crack seams in the rock fist

APRON       = (120, 52, 40)     # leather ox-blood apron
APRON_DK    = (82, 34, 28)      # apron dark-core / fold groove
APRON_SHEEN = (162, 84, 64)     # apron top-left rim
STRAP       = (58, 40, 34)      # apron strap leather

EMBER       = (255, 128, 36)    # forge-orange spark / socket-coal (the ONLY hot hue)
EMBER_HOT   = (255, 232, 180)   # white-hot pinprick point
BRASS       = (196, 144, 52)    # lone small buckle glint (muted, not a 2nd warm family)

INK         = (28, 22, 30)      # the house keyline


def _triad_circle(surf, cx, cy, r, col, *, sheen=True):
    """The house form triad on a circle: dark-core ring -> flat fill -> top-left
    rim sheen. Gives the soot skull sculpted volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -28), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(1, int(r - max(1, r * 0.07))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, 34),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


def _triad_rect(surf, rect, col, ss, *, radius=0, sheen=True):
    """Triad on a rounded rect: dark-core fill -> flat inset fill -> top-left edge
    sheen. The iron-and-stone workman primitive."""
    pygame.draw.rect(surf, _shade_c(col, -34), rect, border_radius=radius)
    pygame.draw.rect(surf, col, rect.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(0, radius - int(ss)))
    if sheen:
        pygame.draw.line(surf, _shade_c(col, 40),
                         (rect.left + int(2 * ss), rect.top + int(2 * ss)),
                         (rect.left + int(2 * ss), rect.bottom - int(3 * ss)),
                         max(1, int(1.6 * ss)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot `_add_outline` recipe). Returns a padded surface."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── the filed horn-stumps (Hellboy tell) ─────────────────────────────────────

def _horn_stumps(surf, cx, cy, r, ss):
    """Two flat-topped cylindrical FILED HORN-STUMPS on the brow — Hellboy's
    signature trimmed-down circular stumps, deliberately NOT pointed horns. Drawn
    as short upright drums with a flat sawn-off top ring (concentric rings show the
    filed cross-section), seated low + wide on the cranium so they read as part of
    the skull, not a hat. Bone-pale on top of the soot so they catch the light."""
    # ~18% larger + seated prouder than round 1 so the named devil-primitive
    # actually reads at 1x — these are the thing that says "devil," so they cannot
    # vanish into the cranium sheen.
    stub_dx = r * 0.52
    stub_w = r * 0.50
    stub_h = r * 0.48
    for s in (-1, 1):
        sx = cx + s * stub_dx
        # The drum body — a short cylinder rising off the brow.
        body = pygame.Rect(0, 0, int(stub_w), int(stub_h))
        body.center = (int(sx), int(cy - stub_h * 0.38))
        pygame.draw.rect(surf, SOOT_DK, body, border_radius=max(2, int(stub_w * 0.30)))
        pygame.draw.rect(surf, _shade_c(SOOT, 20), body.inflate(-int(2 * ss), -int(2 * ss)),
                         border_radius=max(1, int(stub_w * 0.26)))
        # The flat SAWN-OFF top: a wide ellipse cap (the filed cross-section). The
        # bone face is pushed a CLEAR value step LIGHTER than the cool cranium sheen
        # (SOOT_SHEEN ~104) so the flat cut-bone disc pops off the soot — the "filed,
        # not pointed" tell. Concentric rings read it as a cut cross-section.
        top = pygame.Rect(0, 0, int(stub_w * 1.02), int(stub_w * 0.50))
        top.center = (int(sx), int(cy - stub_h * 0.86))
        pygame.draw.ellipse(surf, INK, top)
        pygame.draw.ellipse(surf, (214, 206, 192), top.inflate(-int(2 * ss), -int(2 * ss)))
        pygame.draw.ellipse(surf, (176, 166, 150), top.inflate(-int(7 * ss), -int(3 * ss)))
        pygame.draw.ellipse(surf, (138, 128, 114), top.inflate(-int(13 * ss), -int(6 * ss)))
        # A cool rim-sheen tick on the lit side of the drum.
        pygame.draw.line(surf, SOOT_SHEEN,
                         (int(sx - stub_w * 0.34), int(cy - stub_h * 0.62)),
                         (int(sx - stub_w * 0.34), int(cy - stub_h * 0.14)),
                         max(1, int(1.4 * ss)))


# ── the soot blacksmith-skull face ───────────────────────────────────────────

def _skull_face(surf, cx, cy, r, ss, *, night=False):
    """The broad soot blacksmith-skull. A wide cranium (wider than tall — workman
    heft, NOT Big Reapy's tall dome), filed horn-stumps on the brow, ONE squinting
    eye (lining up the swing) + one open coal-eye, a small nose hole, a tooth band
    with a tongue-TIP poking out the corner in concentration. Soot fill on cool
    iron shading; the eyes are forge-coals (the only glow on the face)."""
    # Broad cranium — drawn as a squashed ellipse so the skull reads stocky/wide.
    dome = pygame.Rect(0, 0, int(r * 2.12), int(r * 1.94))
    dome.center = (int(cx), int(cy))
    pygame.draw.ellipse(surf, SOOT_DK, dome)
    pygame.draw.ellipse(surf, SOOT, dome.inflate(-int(2.2 * ss), -int(2.2 * ss)))
    # Top-left rim sheen on the dome (cool, so the soot reads iron-lit not warm).
    sh = dome.inflate(-int(r * 0.5), -int(r * 0.5))
    sh.move_ip(-int(r * 0.20), -int(r * 0.22))
    pygame.draw.ellipse(surf, _shade_c(SOOT, 30), sh,)
    pygame.draw.ellipse(surf, SOOT, sh.inflate(-int(3 * ss), -int(3 * ss)))

    # Square-off jaw: a rounded trapezoid hung under the dome so the lower face
    # blocks into a heavy workman chin (a skull, broad + square, not a ball).
    jaw_top = cy + r * 0.34
    jaw_bot = cy + r * 1.02
    jaw = [
        (cx - r * 0.86, jaw_top),
        (cx - r * 0.64, jaw_bot),
        (cx + r * 0.64, jaw_bot),
        (cx + r * 0.86, jaw_top),
    ]
    pygame.draw.polygon(surf, SOOT_DK, [(int(x), int(y)) for x, y in jaw])
    inset = [(cx - r * 0.79, jaw_top + ss), (cx - r * 0.58, jaw_bot - ss),
             (cx + r * 0.58, jaw_bot - ss), (cx + r * 0.79, jaw_top + ss)]
    pygame.draw.polygon(surf, SOOT, [(int(x), int(y)) for x, y in inset])
    # Re-stamp the dome so the jaw seam tucks under it.
    pygame.draw.ellipse(surf, SOOT, dome.inflate(-int(2.2 * ss), -int(2.2 * ss)))
    pygame.draw.ellipse(surf, _shade_c(SOOT, 30), sh)
    pygame.draw.ellipse(surf, SOOT, sh.inflate(-int(3 * ss), -int(3 * ss)))

    # The filed horn-stumps on the brow (drawn over the cranium). Kept HIGHER on
    # the brow so the filed cut-bone tops are an upper-face event, not lost in sheen.
    _horn_stumps(surf, cx, cy - r * 0.58, r, ss)

    # — Eyes: TWO matched soot sockets so the skull keeps bilateral symmetry. The
    #   LEFT (s == -1) eye SQUINTS to a scrunched lidded slit — he's lining up the
    #   swing — while the RIGHT is a wide-open round socket. Both are DARK INK
    #   CAVITIES first; forge-orange is only a tiny contained coal + a white-hot
    #   PINPRICK point (never a filled disc), so orange is the smallest warm area on
    #   the figure. The dark socket SHAPE carries the read in grayscale; the asymmetry
    #   is "scrunched aiming eye vs wide eye," never "big glow vs nothing."
    eye_dx = r * 0.44
    eye_dy = -r * 0.02
    sock_r = r * 0.27
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        squint = (s < 0)
        # A small CONTAINED ember halo — ~half the round-1 radius so it's only a
        # whisper of warmth around the coal, never a headlight. Night nudges it just
        # enough to keep the coal alive on a dark sky.
        halo_a = 150 if night else 100
        halo_r = sock_r * (1.0 if night else 0.72)
        glow = make_glow_surface(int(halo_r), EMBER, alpha_center=halo_a, falloff=2.4)
        gy_off = sock_r * 0.10 if squint else sock_r * 0.20
        surf.blit(glow, (int(ex - halo_r - 1), int(ey + gy_off - halo_r - 1)),
                  special_flags=pygame.BLEND_ADD)
        if squint:
            # The scrunched aiming eye: a dark ink socket matched in SIZE to the open
            # one, but read as a closed lidded slit — a lid-crease arc above + a low
            # crescent cavity below, with a small coal glint pinched in the slit so it
            # reads as a live winking eye, not a missing socket.
            sock = pygame.Rect(0, 0, int(sock_r * 2.0), int(sock_r * 2.0))
            sock.center = (int(ex), int(ey))
            # The dark cavity, clipped to the lower crescent by the lid above it.
            lid_y = ey - sock_r * 0.18
            crescent = pygame.Rect(int(ex - sock_r), int(lid_y),
                                   int(sock_r * 2.0), int(sock_r * 1.3))
            pygame.draw.ellipse(surf, INK, crescent)
            pygame.draw.ellipse(surf, SOOT_DK, crescent.inflate(-int(2 * ss), -int(2 * ss)))
            # The drooped lid + crease line riding over the cavity (the "scrunched
            # shut" tell — a bold dark arc the width of the socket).
            pygame.draw.line(surf, SOOT_DK,
                             (int(ex - sock_r * 0.96), int(lid_y + sock_r * 0.06)),
                             (int(ex + sock_r * 0.96), int(lid_y - sock_r * 0.10)),
                             max(2, int(2.4 * ss)))
            pygame.draw.line(surf, _shade_c(SOOT, 18),
                             (int(ex - sock_r * 0.86), int(lid_y - sock_r * 0.18)),
                             (int(ex + sock_r * 0.86), int(lid_y - sock_r * 0.30)),
                             max(1, int(1.4 * ss)))
            # A small coal glint pinched low in the slit (point-sized).
            pygame.draw.circle(surf, EMBER,
                               (int(ex - s * sock_r * 0.10), int(ey + sock_r * 0.44)),
                               max(1, int(sock_r * 0.24)))
            pygame.draw.circle(surf, EMBER_HOT,
                               (int(ex - s * sock_r * 0.10), int(ey + sock_r * 0.40)),
                               max(1, int(sock_r * 0.12)))
        else:
            # The wide-open socket: a deep ink cavity (grayscale-legible) holding a
            # small low coal + a single white-hot PINPRICK point — not a glowing disc.
            pygame.draw.circle(surf, INK, (int(ex), int(ey)), int(sock_r))
            pygame.draw.circle(surf, SOOT_DK, (int(ex), int(ey)),
                               int(sock_r), max(1, int(2 * ss)))
            # A small contained coal pooled low in the cavity (not filling it).
            pygame.draw.circle(surf, _shade_c(EMBER, -30),
                               (int(ex), int(ey + sock_r * 0.34)),
                               max(1, int(sock_r * 0.36)))
            pygame.draw.circle(surf, EMBER,
                               (int(ex), int(ey + sock_r * 0.34)),
                               max(1, int(sock_r * 0.24)))
            # The white-hot PINPRICK: a tiny eager point high + inward, the catch-
            # light of a live eye (a point, never a wide core).
            pygame.draw.circle(surf, EMBER_HOT,
                               (int(ex - s * sock_r * 0.18), int(ey - sock_r * 0.06)),
                               max(1, int(sock_r * 0.16)))
            # High bowed-UP bone brow-ridge over the open eye — lifted, surprised-
            # cute, never the angry inner-down V.
            pygame.draw.arc(surf, _shade_c(SOOT, 26),
                            (int(ex - sock_r * 1.25), int(ey - sock_r * 1.7),
                             int(sock_r * 2.5), int(sock_r * 1.7)),
                            math.radians(20), math.radians(160), max(2, int(2.2 * ss)))

    # — Nose: a small upturned triangle hole between+below the sockets.
    nose_y = cy + r * 0.38
    nose = [(cx, nose_y - r * 0.10), (cx - r * 0.10, nose_y + r * 0.12),
            (cx + r * 0.10, nose_y + r * 0.12)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])

    # — The grin: a short tooth band on a bowed-UP smile-seat, with a TONGUE-TIP
    #   poking out the right corner (concentration, lining up the blow). A small
    #   even tooth row = focused workman, not a horror rictus.
    grin_y = cy + r * 0.66
    grin_hw = r * 0.52
    grin_h = r * 0.30
    bow_amp = grin_h * 0.55

    def _bow(x_rel):
        return bow_amp * (x_rel * x_rel)

    seat_top, seat_bot = [], []
    n = 16
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * grin_hw
        yt = grin_y - _bow(xr)
        seat_top.append((x, yt))
        seat_bot.append((x, yt + grin_h))
    seat = seat_top + seat_bot[::-1]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in seat])

    # The tongue-tip — a bigger, higher-contrast red lobe poking up over the right
    # corner of the seat, the "tip out in concentration" beat. Enlarged + brighter
    # so it reads as a tongue at 1x, not a stray red pixel.
    t_x = cx + grin_hw * 0.66
    t_y = grin_y - _bow(0.66) + grin_h * 0.18
    tongue = pygame.Rect(0, 0, int(r * 0.32), int(r * 0.28))
    tongue.center = (int(t_x), int(t_y))
    pygame.draw.ellipse(surf, (130, 30, 46), tongue)
    pygame.draw.ellipse(surf, (224, 86, 104), tongue.inflate(-int(2 * ss), -int(2 * ss)))
    pygame.draw.line(surf, (130, 30, 46), (int(t_x), int(t_y - r * 0.08)),
                     (int(t_x), int(t_y + r * 0.08)), max(1, int(1.4 * ss)))

    # Tooth band — THREE bold sooted teeth on the smile-curve (low-count so the grin
    # survives 1x instead of muddying into a dark smear).
    teeth = 3
    gap = grin_hw * 0.14
    tw = (grin_hw * 2.0 - gap * (teeth - 1)) / teeth
    th = grin_h * 0.74
    for i in range(teeth):
        tx = -grin_hw + i * (tw + gap)
        xr = (tx + tw * 0.5) / grin_hw
        ty = grin_y - _bow(xr) + ss
        rect = pygame.Rect(int(cx + tx + ss), int(ty), int(tw - ss), int(th))
        pygame.draw.rect(surf, TOOTH, rect, border_radius=max(1, int(1.8 * ss)))
        pygame.draw.rect(surf, TOOTH_DK, rect, max(1, int(1.4 * ss)),
                         border_radius=max(1, int(1.8 * ss)))


# ── the stocky apron body + giant stone fist ─────────────────────────────────

def _apron_body(surf, cx, neck_y, w, h, ss):
    """The stocky blacksmith body under the broad skull: a heavy leather ox-blood
    APRON (a wide bib tapering to a square hem), brass buckle, crossed neck straps,
    and tiny stub legs in boots. Built BROAD (workman heft) so it reads stocky, the
    opposite mass-language to the gaunt reapers. Triad-shaded ox-blood leather."""
    hem_y = neck_y + h
    # Apron bib — wide at the shoulders, squaring to a heavy hem (a slab of leather).
    body = [
        (cx - w * 0.46, neck_y),
        (cx - w * 0.60, neck_y + h * 0.30),
        (cx - w * 0.66, hem_y),
        (cx + w * 0.66, hem_y),
        (cx + w * 0.60, neck_y + h * 0.30),
        (cx + w * 0.46, neck_y),
    ]
    pygame.draw.polygon(surf, APRON_DK, [(int(x), int(y)) for x, y in body])
    inner = [(cx - w * 0.42, neck_y + ss), (cx - w * 0.55, neck_y + h * 0.30),
             (cx - w * 0.60, hem_y - ss), (cx + w * 0.60, hem_y - ss),
             (cx + w * 0.55, neck_y + h * 0.30), (cx + w * 0.42, neck_y + ss)]
    pygame.draw.polygon(surf, APRON, [(int(x), int(y)) for x, y in inner])
    # Top-left rim sheen down the lit leather edge.
    pygame.draw.line(surf, APRON_SHEEN,
                     (int(cx - w * 0.46), int(neck_y + h * 0.10)),
                     (int(cx - w * 0.58), int(hem_y - ss)), max(2, int(2.0 * ss)))
    # A worn fold groove + a scorch scuff so the leather reads used, not flat.
    pygame.draw.line(surf, APRON_DK,
                     (int(cx + w * 0.10), int(neck_y + h * 0.32)),
                     (int(cx + w * 0.16), int(hem_y - ss)), max(1, int(1.6 * ss)))
    scuff = pygame.Rect(0, 0, int(w * 0.20), int(h * 0.14))
    scuff.center = (int(cx - w * 0.18), int(neck_y + h * 0.58))
    pygame.draw.ellipse(surf, _shade_c(APRON, -22), scuff)

    # Crossed leather neck straps over the shoulders.
    for s in (-1, 1):
        pygame.draw.line(surf, STRAP,
                         (int(cx + s * w * 0.40), int(neck_y - h * 0.04)),
                         (int(cx - s * w * 0.12), int(neck_y + h * 0.20)),
                         max(2, int(3 * ss)))

    # Dark-IRON buckle at mid-bib — muted to iron (NOT brass) so forge-orange is the
    # ONLY "hot" hue on the figure; a single small brass dot is the lone metal glint,
    # the value break on the dark leather without a second warm-metal family.
    buckle = pygame.Rect(0, 0, int(w * 0.22), int(h * 0.16))
    buckle.center = (int(cx), int(neck_y + h * 0.40))
    pygame.draw.rect(surf, IRON_DK, buckle, border_radius=max(1, int(2 * ss)))
    pygame.draw.rect(surf, _shade_c(IRON, -8), buckle.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(1, int(2 * ss)))
    pygame.draw.line(surf, IRON_SHEEN,
                     (int(buckle.left + 2 * ss), int(buckle.top + 2 * ss)),
                     (int(buckle.left + 2 * ss), int(buckle.bottom - 2 * ss)),
                     max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, BRASS, buckle.center, max(1, int(h * 0.030)))

    # Tiny stub legs in heavy boots peeking under the hem (small = the chibi gag
    # against the big body + giant fist).
    for s in (-1, 1):
        lx = cx + s * w * 0.30
        leg = pygame.Rect(0, 0, int(w * 0.18), int(h * 0.16))
        leg.midtop = (int(lx), int(hem_y - ss))
        pygame.draw.rect(surf, STRAP, leg, border_radius=max(1, int(2 * ss)))
        boot = pygame.Rect(0, 0, int(w * 0.26), int(h * 0.12))
        boot.midtop = (int(lx + w * 0.02), int(leg.bottom - ss))
        pygame.draw.rect(surf, INK, boot, border_radius=max(1, int(3 * ss)))
        pygame.draw.rect(surf, _shade_c(IRON, -20), boot.inflate(-int(2 * ss), -int(3 * ss)),
                         border_radius=max(1, int(2 * ss)))


def _stone_fist(surf, cx, cy, r, ss):
    """The oversized stone gauntlet-FIST — Hellboy's "Right Hand of Doom" recast as
    a forge-fist. A big blocky three-knuckle stone hand (THREE fat fingers, the
    Hellboy tell) gripping the hammer haft, deliberately too big for the body. Cool
    grey rock with crack seams + the triad so it reads carved stone, not flesh."""
    # The blocky hand mass — a fat rounded slab.
    hand = pygame.Rect(0, 0, int(r * 2.0), int(r * 1.7))
    hand.center = (int(cx), int(cy))
    pygame.draw.rect(surf, STONE_DK, hand, border_radius=max(3, int(r * 0.36)))
    pygame.draw.rect(surf, STONE, hand.inflate(-int(2.4 * ss), -int(2.4 * ss)),
                     border_radius=max(2, int(r * 0.32)))
    # Three fat knuckle bumps along the top (THREE fingers — the Hellboy tell).
    for i, fx in enumerate((-0.55, 0.0, 0.55)):
        kx = cx + fx * r * 1.0
        kr = r * 0.40
        pygame.draw.circle(surf, STONE_DK, (int(kx), int(hand.top + kr * 0.5)), int(kr))
        pygame.draw.circle(surf, STONE, (int(kx), int(hand.top + kr * 0.5)),
                           max(1, int(kr - ss)))
        # A crack seam between knuckles.
        pygame.draw.line(surf, STONE_CRACK,
                         (int(kx + r * 0.30), int(hand.top + kr * 0.2)),
                         (int(kx + r * 0.34), int(cy + r * 0.2)), max(1, int(1.4 * ss)))
    # A thumb wrapping over the front (toward the haft).
    thumb = pygame.Rect(0, 0, int(r * 0.7), int(r * 0.9))
    thumb.center = (int(cx + r * 0.7), int(cy + r * 0.2))
    pygame.draw.rect(surf, STONE_DK, thumb, border_radius=max(2, int(r * 0.28)))
    pygame.draw.rect(surf, STONE, thumb.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(1, int(r * 0.24)))
    # Top-left rim sheen on the rock + a couple of carved crack seams.
    pygame.draw.line(surf, STONE_SHEEN,
                     (int(hand.left + r * 0.20), int(hand.top + r * 0.30)),
                     (int(hand.left + r * 0.20), int(hand.bottom - r * 0.30)),
                     max(1, int(1.8 * ss)))
    pygame.draw.line(surf, STONE_CRACK,
                     (int(cx - r * 0.3), int(cy + r * 0.5)),
                     (int(cx + r * 0.2), int(cy + r * 0.7)), max(1, int(1.4 * ss)))


# ── the sledgehammer prop (and its pillar-tile components) ────────────────────

def _hammer_haft(surf, cx, top_y, bot_y, hw, ss):
    """The iron HAFT = the tileable PILLAR BODY: a riveted iron post banded with
    grip-wraps. Drawn as a cool iron bar with hard dark groove-bands and a row of
    rivet studs down the lit edge, sized so only a few bands stack across a
    gameplay-height pillar so the banding read SURVIVES smoothscale. No head here;
    the hammer-head is the detachable top cap."""
    length = bot_y - top_y
    # The base iron bar with the triad.
    bar = pygame.Rect(int(cx - hw), int(top_y), int(2 * hw), int(length))
    pygame.draw.rect(surf, IRON_DK, bar)
    pygame.draw.rect(surf, IRON, bar.inflate(-int(2 * ss), 0))
    pygame.draw.line(surf, IRON_SHEEN,
                     (int(cx - hw * 0.55), int(top_y)),
                     (int(cx - hw * 0.55), int(bot_y)), max(1, int(1.8 * ss)))
    # Chunky grip-bands: a few wide leather wraps with a rivet stud each, spaced so
    # ~3-4 stack across a pillar (bold enough to survive the 1x downscale).
    band_h = max(int(20 * ss), int(hw * 2.2))
    n = max(2, round(length / band_h))
    band_h = length / n
    for i in range(n):
        by = top_y + i * band_h + band_h * 0.30
        band = pygame.Rect(int(cx - hw * 1.06), int(by), int(2 * hw * 1.06), int(band_h * 0.40))
        pygame.draw.rect(surf, STRAP, band, border_radius=max(1, int(2 * ss)))
        pygame.draw.line(surf, _shade_c(STRAP, 26),
                         (band.left + ss, band.top + ss),
                         (band.right - ss, band.top + ss), max(1, int(ss)))
        # Rivet stud on the lit edge of the band.
        rv = (int(cx - hw * 0.4), int(by + band_h * 0.20))
        pygame.draw.circle(surf, IRON_DK, rv, max(1, int(hw * 0.26)))
        pygame.draw.circle(surf, RIVET, (rv[0] - int(ss), rv[1] - int(ss)),
                           max(1, int(hw * 0.16)))


def _spark_burst(surf, cx, cy, n, spread, ss, seed):
    """A contained burst of forge-orange sparks flying off the strike — the
    CONTAINED accent that separates the soot/iron figure from a lava wash. Small
    additive glints + hot pinpricks, scattered deterministically."""
    rng = random.Random(seed)
    for _ in range(n):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(0.2, 1.0) * spread
        sx = cx + math.cos(a) * d
        sy = cy + math.sin(a) * d * 0.8
        sr = rng.uniform(1.2, 3.0) * ss
        glow = make_glow_surface(int(sr * 2.4), EMBER, alpha_center=200, falloff=2.4)
        surf.blit(glow, (int(sx - sr * 2.4 - 1), int(sy - sr * 2.4 - 1)),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, EMBER, (int(sx), int(sy)), max(1, int(sr)))
        pygame.draw.circle(surf, EMBER_HOT, (int(sx), int(sy)), max(1, int(sr * 0.5)))


def _hammer_head(surf, cx, base_y, hw, ss, *, point_up=True):
    """The anvil-shaped HAMMER-HEAD = the detachable PILLAR TOP CAP that rides the
    gap-edge only. A heavy iron double-faced block (one flat striking face, one
    slightly tapered peen) wider than the haft, with a forge-orange HOT SEAM + a
    spark burst flying off the striking face INTO the gap — the signature that
    survives the 1x downscale. `point_up` orients the head away from the haft."""
    d = -1 if point_up else 1
    head_w = hw * 4.4
    head_h = hw * 3.0
    head_off = base_y + d * head_h * 0.5
    head = pygame.Rect(0, 0, int(head_w), int(head_h))
    head.center = (int(cx), int(head_off))
    # The iron block with the triad.
    pygame.draw.rect(surf, IRON_DK, head, border_radius=max(2, int(hw * 0.4)))
    pygame.draw.rect(surf, IRON, head.inflate(-int(2.4 * ss), -int(2.4 * ss)),
                     border_radius=max(1, int(hw * 0.34)))
    # A reinforced collar band where the haft enters the head.
    collar = pygame.Rect(0, 0, int(hw * 2.4), int(head_h * 0.36))
    collar.center = (int(cx), int(base_y - d * head_h * 0.02))
    pygame.draw.rect(surf, IRON_DK, collar, border_radius=max(1, int(hw * 0.3)))
    pygame.draw.rect(surf, _shade_c(IRON, 18), collar.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(1, int(hw * 0.26)))
    # Top-left steel rim sheen on the block.
    pygame.draw.line(surf, IRON_SHEEN,
                     (int(head.left + hw * 0.5), int(head.top + hw * 0.4)),
                     (int(head.left + hw * 0.5), int(head.bottom - hw * 0.4)),
                     max(1, int(2.0 * ss)))
    # The striking FACE (the end pointing into the gap) glows with a hot forge
    # seam — the contained ember accent, never a full wash.
    face_y = head_off + d * head_h * 0.5
    face = pygame.Rect(0, 0, int(head_w * 0.78), int(hw * 0.7))
    face.center = (int(cx), int(face_y - d * hw * 0.3))
    glow = make_glow_surface(int(head_w * 0.5), EMBER, alpha_center=170, falloff=2.2)
    surf.blit(glow, (int(cx - head_w * 0.5 - 1), int(face_y - head_w * 0.5 - 1)),
              special_flags=pygame.BLEND_ADD)
    pygame.draw.rect(surf, EMBER, face, border_radius=max(1, int(hw * 0.3)))
    pygame.draw.rect(surf, EMBER_HOT, face.inflate(-int(hw * 1.2), -int(2 * ss)),
                     border_radius=max(1, int(hw * 0.2)))
    # Sparks flying off the striking face INTO the gap.
    _spark_burst(surf, cx, face_y + d * hw * 0.6, 9, head_w * 0.7, ss, seed=7)


def build_soulforge(scale=1.0, ss=3, *, night=False):
    """The full boss figure on its own transparent surface. A broad soot skull
    (~46% of total height) on a stocky apron body, ONE giant stone fist gripping a
    sledgehammer raised at the figure's right. Returns an outlined surface and the
    baseline (feet) y. `night` pushes the socket coals so the eye stays lit."""
    H = int(266 * scale)
    W = int(190 * scale)
    pad = int(76 * scale)
    surf = pygame.Surface(((W + pad * 2) * ss, (H + pad) * ss), pygame.SRCALPHA)
    cx = (W // 2 + pad) * ss

    # Broad skull occupies the top ~46% (stocky, not head-dominant like Big Reapy).
    head_band = int(H * 0.46) * ss
    skull_r = head_band * 0.44
    skull_cy = int(pad * 0.34) * ss + skull_r
    skull_cx = cx - W * 0.06 * ss          # nudge head off the hammer side

    # Stocky body below the jaw.
    neck_y = skull_cy + skull_r * 0.96
    body_w = W * 0.74 * ss
    body_h = int(H * 0.40) * ss
    feet_y = neck_y + body_h + W * 0.07 * ss

    # The sledgehammer raised at the figure's right: the haft runs up past the
    # shoulder, the head rises above the skull. The giant stone fist grips it.
    hx = cx + W * 0.40 * ss
    hhw = 8 * ss
    grip_y = neck_y + body_h * 0.10        # where the fist clamps the haft
    head_base = skull_cy - skull_r * 0.5   # the head rides above the skull
    haft_bot = feet_y + 6 * ss
    _hammer_haft(surf, hx, head_base, haft_bot, hhw, ss)
    _hammer_head(surf, hx, head_base, hhw, ss, point_up=True)

    _apron_body(surf, skull_cx, neck_y, body_w, body_h, ss)
    _skull_face(surf, skull_cx, skull_cy, skull_r, ss, night=night)

    # The giant stone fist clamps the haft last (over body + haft) so it reads as
    # the foreground mitt holding the hammer.
    _stone_fist(surf, hx - hhw * 0.4, grip_y, skull_r * 0.74, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(small), feet_y / ss


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _hammer_pillar_obstacle(height, ss, *, flip):
    """One sledgehammer PILLAR obstacle: the iron haft fills the post, the
    hammer-head cap sits at the gap end. `flip` makes the top pillar's head point
    DOWN into the gap; the bottom pillar's head points UP — proving the prop
    mirrors top<->bottom into a clean vertical iron post with the hot striking face
    + sparks flourishing into the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 9 * ss
    cap_band = int(54 * ss)
    _hammer_haft(surf, cx, 0, bh - cap_band, hw, ss)
    _hammer_head(surf, cx, bh - cap_band, hw, ss, point_up=False)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    out = _add_outline(out)
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    return s


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((34, 32, 38))
    _label(sheet, font, "SOULFORGE  —  take A8  —  soot-charcoal & forge-orange  —  round 2", 18, 12)
    _label(sheet, small,
            "the blacksmith-DEVIL skull: a broad soot skull w/ FILED HORN-STUMPS + ONE giant stone fist swinging a sledgehammer",
            18, 32, (200, 196, 210))

    # — Cell A: boss at showcase scale, on a neutral panel.
    panel = pygame.Rect(18, 56, 360, 560)
    pygame.draw.rect(sheet, (50, 48, 56), panel, border_radius=8)
    pygame.draw.rect(sheet, (88, 84, 98), panel, 2, border_radius=8)
    boss, _ = build_soulforge(scale=1.55, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 16))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)

    # — Cell B: the sledgehammer as a tileable PILLAR pair at TRUE obstacle scale.
    panelB = pygame.Rect(394, 56, 360, 560)
    bg = _sky(panelB.w, panelB.h, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (88, 84, 98), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE obstacle scale", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG                  # 82px — the real obstacle width
    slice_h = 470
    slice_x = panelB.x + 26
    slice_y = panelB.y + 46
    gap_top = 168
    gap_h = 120
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _hammer_pillar_obstacle(top_h, 3, flip=True)
    bot_pillar = _hammer_pillar_obstacle(bot_h, 3, flip=False)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (255, 255, 255), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px wide, as", slice_x - 2, slice_y + slice_h + 6, (20, 20, 30))
    _label(sheet, small, "it scrolls): riveted grip-bands", slice_x - 2, slice_y + slice_h + 22, (20, 20, 30))

    # 2x zoom of the gap so the anvil-head cap + hot strike + sparks are legible.
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    zoom_src.blit(top_pillar, (-2, -(gap_top - 70) - 2))
    zoom_src.blit(bot_pillar, (-2, gap_h + 70 - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 184
    zy = panelB.y + 70
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the gap:", zx - 4, zy - 16, (255, 255, 255))
    _label(sheet, small, "anvil-head cap, hot strike", zx - 4, zy + zh * 2 + 6, (20, 20, 30))
    _label(sheet, small, "face + sparks INTO the gap;", zx - 4, zy + zh * 2 + 22, (20, 20, 30))
    _label(sheet, small, "top<->bottom mirror", zx - 4, zy + zh * 2 + 38, (20, 20, 30))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies.
    panelC = pygame.Rect(770, 56, 392, 560)
    pygame.draw.rect(sheet, (50, 48, 56), panelC, border_radius=8)
    pygame.draw.rect(sheet, (88, 84, 98), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, _ = build_soulforge(scale=0.62, ss=3)
    boss1x_n, _ = build_soulforge(scale=0.62, ss=3, night=True)
    day = _sky(180, 250, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 250, (5, 8, 30), (15, 25, 70), (35, 55, 115))
    for sx, sy in ((24, 40), (150, 26), (96, 70), (40, 120), (160, 150), (70, 200)):
        pygame.draw.circle(night, (220, 230, 255), (sx, sy), 1)

    dy = panelC.y + 40
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2,
                        dy + 250 - boss1x.get_height() - 6))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2,
                          dy + 250 - boss1x_n.get_height() - 6))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 20, 30))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (210, 220, 255))

    # — Grayscale silhouette check (face + stumps + fist must read without ember).
    gy = dy + 270
    gray = pygame.Surface((boss1x.get_width(), boss1x.get_height()), pygame.SRCALPHA)
    gray.blit(boss1x, (0, 0))
    arr = pygame.surfarray.pixels3d(gray)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    gpanel = pygame.Rect(panelC.x + 14, gy, 360, 230)
    pygame.draw.rect(sheet, (120, 120, 128), gpanel, border_radius=6)
    sheet.blit(gray, (gpanel.centerx - gray.get_width() // 2,
                      gpanel.bottom - gray.get_height() - 8))
    _label(sheet, small, "grayscale: soot skull + filed stumps + giant fist carry the read (no ember reliance)",
            gpanel.x + 6, gpanel.y + 6, (30, 30, 30))

    # — Footer caption: the scary-cute thesis + house style + separators.
    _label(sheet, small,
           "scary-cute: tiny body, ONE absurd stone mitt; left eye squints lining up the swing, tongue-tip out in concentration.",
           18, SH - 124, (210, 206, 220))
    _label(sheet, small,
           "house style: FLAT fills, ink keyline grown from the alpha mask, dark-core->fill->top-left-sheen triad, ss=3 -> smoothscale.",
           18, SH - 104, (210, 206, 220))
    _label(sheet, small,
           "palette: soot-charcoal skull on COOL iron greys; forge-orange is a CONTAINED accent (coals + sparks + strike) — NOT Brimstone's magma wash.",
           18, SH - 84, (210, 206, 220))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "reapy_devil", "soulforge")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
