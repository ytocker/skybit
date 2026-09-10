"""Look-dev sheet for the Skybit DEVIL boss — GROUP B take B2 "BAALGOAT".

A chibi BAPHOMET: the set's only GOAT-MUZZLE face. A long indigo goat snout
(rectangular, never skull-round), two big ridged BACK-SWEPT goat horns with a
small warm CROWN-TORCH burning between them, broad flat-faceted bat wings, stub
hooved legs, and a blood-red pentagram medallion. Built bottom-up — its own goat
construction, unrelated to any skull pick in Group A.

House style this obeys (the warren-clown / Big-Reapy grammar):
  - CHIBI proportions — squat body, big dopey head, derp head-tilt.
  - FLAT fills + hard 1-2px ink keylines (22,20,30). No within-shape gradients,
    no feathered edges, no bevels, no realistic shading.
  - Form via the dark-core -> flat-fill -> top-left rim-sheen triad. The indigo
    fur reads sculpted-but-flat; the cream muzzle catches the light.
  - Silhouette POP via a post-pass 1px ink keyline grown from the alpha mask
    (the parrot `_add_outline` recipe) so the indigo never flattens on a night sky.
  - SUPERSAMPLE then smoothscale.

Set-wide guardrails honoured:
  - Baalgoat is the ONLY concept allowed a curved-horn pair (back-swept goat) — it
    OWNS that. Horns are ridged + amber, distinct from every other horn primitive.
  - The crown-torch is a small WARM CLASSIC torch (gold/amber, soft round glow) —
    deliberately NOT Glitchfiend's neon nor Pyrecrown's green soul-fire.

Prop -> pillar mirror: the externalised CROWN-TORCH POLE. The banded indigo
torch-pole is the tileable PILLAR BODY (cuff banding = the repeat); the brazier
flame-cap is the detachable gap-edge cap — flame flourishing INTO the gap. A
top/bottom flip mirrors into one clean vertical pole with a flame at each gap-edge.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/render_skybit_devil_baalgoat.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, blit_glow, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── "indigo-goat & torch-gold" palette (B2) ──────────────────────────────────
# Deep indigo/midnight fur DOMINANT (bold + saturated, never a grey realistic
# goat), a cream/ash muzzle as the lit value-pop, amber back-swept horns, a warm
# torch-gold crown-flame as the single glow accent, and a regal violet sheen +
# blood-red pentagram so the palette stays distinct from the reds/blue/green of
# the rest of Group B. The dark muzzle slots + keyline must read in grayscale too.
FUR        = (58, 52, 92)       # indigo-charcoal fur fill
FUR_DK     = (36, 32, 60)       # dark-core ring / fold grooves
FUR_SHEEN  = (120, 106, 172)    # violet top-left rim sheen
FUR_RIM    = (150, 132, 200)    # brightest violet edge catch

# Muzzle dropped ~15% off pure-cream so the goat snout stops out-shouting the
# eyes/horns and the goat read survives grayscale on its own form, not its value.
MUZZLE     = (178, 172, 186)    # ash-taupe goat muzzle fill (dropped from cream)
MUZZLE_DK  = (122, 118, 136)    # muzzle dark-core / nostril seat
MUZZLE_SH  = (210, 204, 218)    # muzzle top-left sheen (no longer near-white)

HORN       = (214, 168, 78)     # amber back-swept goat horn
HORN_DK    = (150, 110, 44)     # horn dark-core / ridge valleys
HORN_SH    = (252, 224, 150)    # horn ridge highlight

# Wings sit a clear value-step below the body FUR so the wing/body junction reads
# as a seam (not one indigo blob) at 1x — the membrane darkens behind the torso.
WING       = (40, 34, 70)       # bat-wing membrane (a step darker than fur)
WING_DK    = (24, 20, 46)       # wing dark-core / rib seats
WING_SH    = (90, 76, 138)      # wing top-left rim

EYE        = (250, 224, 96)     # sulphur-amber goat eye
EYE_SLOT   = (40, 30, 24)       # rectangular slot pupil
EYE_CATCH  = (252, 248, 240)    # bright wet-eye sheen dot (kept near-white)

TORCH      = (255, 196, 72)     # warm crown-torch flame (outer)
TORCH_HOT  = (255, 240, 196)    # torch inner hot core
TORCH_DK   = (214, 120, 36)     # torch flame base / ember root

PENTA      = (196, 40, 52)      # blood-red pentagram medallion
PENTA_DK   = (132, 24, 36)      # medallion ring shade
GOLD       = (224, 176, 70)     # medallion rim / pole cuffs
GOLD_HI    = (255, 224, 150)

INK        = (22, 20, 30)       # the house keyline


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sh=28):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Keeps volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -40), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.07))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, sh),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


def _triad_ellipse(surf, rect, col, *, sheen=True, sh=28):
    """The triad on an ellipse — used for the rectangular-ish goat muzzle so it
    reads long-and-blocky rather than skull-round."""
    x, y, w, h = rect
    pygame.draw.ellipse(surf, _shade_c(col, -40), (x, y, w, h))
    pygame.draw.ellipse(surf, col, (x + max(1, int(w * 0.05)),
                                    y + max(1, int(h * 0.05)),
                                    int(w * 0.9), int(h * 0.9)))
    if sheen:
        pygame.draw.ellipse(surf, _shade_c(col, sh),
                            (x + int(w * 0.12), y + int(h * 0.08),
                             int(w * 0.5), int(h * 0.38)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px ink keyline from the alpha mask so the silhouette POPS on any
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


# ── the warm crown-torch flame ───────────────────────────────────────────────

def _torch_flame(surf, cx, base_y, fh, ss, *, point_up=True, narrow=False):
    """A small WARM classic torch flame — a soft teardrop of gold with a warm
    round halo and a hot pale core. Deliberately rounded + warm so it never reads
    as Glitchfiend's neon spike or Pyrecrown's green soul-fire. `point_up` orients
    the teardrop tip away from the base (used both on the crown and the pillar cap,
    where the cap flame flourishes INTO the gap). `narrow` slims it to a taller
    teardrop for the crown so it reads as a flame BETWEEN the horns, not a gold
    cap fused on the cranium."""
    d = -1 if point_up else 1
    fw = fh * (0.42 if narrow else 0.62)
    # Warm round halo first (additive) so the flame glows without a hard edge. A
    # narrow crown flame gets a tighter halo so the glow doesn't bloom back into a
    # wide gold skullcap over the cranium.
    gr = fh * (0.70 if narrow else 0.95)
    glow = make_glow_surface(int(gr), TORCH, alpha_center=200, falloff=2.2)
    gy = base_y + d * fh * 0.45
    surf.blit(glow, (int(cx - gr - 1), int(gy - gr - 1)),
              special_flags=pygame.BLEND_ADD)
    # Outer flame teardrop: a wide rounded base tapering to a soft tip — flat fill,
    # NOT a jagged spike. Built as a stack of shrinking circles along the axis.
    n = 12
    for i in range(n + 1):
        t = i / n
        # Bulge low (rounded base), pinch to the tip.
        wob = math.sin(t * math.pi) * 0.5 + (1.0 - t) * 0.5
        r = max(1, fw * 0.5 * wob)
        ax = cx + math.sin(t * 6.0) * fw * 0.06 * t   # gentle warm waver
        ay = base_y + d * fh * t
        pygame.draw.circle(surf, TORCH, (int(ax), int(ay)), int(r))
    # Hot inner tongue — a smaller pale teardrop nested inside.
    for i in range(n + 1):
        t = i / n
        wob = math.sin(t * math.pi) * 0.5 + (1.0 - t) * 0.5
        r = max(1, fw * 0.30 * wob)
        ay = base_y + d * fh * (0.10 + t * 0.78)
        pygame.draw.circle(surf, TORCH_HOT, (int(cx), int(ay)), int(r))
    # Ember root at the base where it leaves the cradle/cap.
    pygame.draw.circle(surf, TORCH_DK, (int(cx), int(base_y)),
                       max(1, int(fw * 0.32)))


# ── the back-swept ridged goat horns ─────────────────────────────────────────

def _goat_horn(surf, base_x, base_y, length, ss, *, side):
    """One big BACK-SWEPT ridged goat horn — Baalgoat's owned curved-horn pair.
    Sweeps UP and OUT from the brow, then arcs BACK over the crown, tapering to a
    point. Ridge banding (the goat tell) is stamped as darker valleys across the
    arc so the horn never reads as a smooth bone tube. `side` (-1 left / +1 right)
    mirrors the sweep."""
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        # Out then back: x sweeps out early, curls back inward over the top.
        out = math.sin(min(t, 0.5) / 0.5 * math.pi * 0.5)
        back = (t * t) * 0.55 if t > 0.4 else 0.0
        px = base_x + side * (length * 0.62 * out - length * 0.30 * back)
        # Rise up then arc back-and-down a touch at the tip (back-swept).
        py = base_y - length * (1.18 * t - 0.30 * t * t)
        pts.append((px, py))
    # Dark-core -> amber fill -> ridge sheen, a fat tapering horn.
    for col, wid in ((HORN_DK, 15 * ss), (HORN, 10.5 * ss), (HORN_SH, 3 * ss)):
        for i in range(len(pts) - 1):
            t = i / (len(pts) - 1)
            w = max(1, int(wid * (1.0 - 0.66 * t)))
            a, b = pts[i], pts[i + 1]
            if col is HORN_SH:
                a = (a[0] - side * ss, a[1] - ss)
                b = (b[0] - side * ss, b[1] - ss)
            pygame.draw.line(surf, col, (int(a[0]), int(a[1])),
                             (int(b[0]), int(b[1])), w)
        for px, py in pts[::2]:
            pygame.draw.circle(surf, col, (int(px), int(py)),
                               max(1, int(w * 0.5)))
    # Ridge bands — darker valleys stamped across the lower two-thirds (the goat
    # ridge tell). Spaced along the arc, perpendicular nicks.
    for i in range(2, n - 2, 2):
        t = i / n
        if t > 0.72:
            break
        a, b = pts[i], pts[i + 1]
        rw = max(1, int(11 * ss * (1.0 - 0.6 * t)))
        # A short perpendicular dark nick = one ridge valley.
        nx, ny = (b[0] - a[0]), (b[1] - a[1])
        ln = math.hypot(nx, ny) or 1
        px, py = -ny / ln, nx / ln
        cxr, cyr = a
        pygame.draw.line(surf, HORN_DK,
                         (int(cxr - px * rw * 0.5), int(cyr - py * rw * 0.5)),
                         (int(cxr + px * rw * 0.5), int(cyr + py * rw * 0.5)),
                         max(1, int(1.6 * ss)))
    # Pointed tip nub.
    tx, ty = pts[-1]
    pygame.draw.circle(surf, HORN_DK, (int(tx), int(ty)), max(1, int(3 * ss)))
    pygame.draw.circle(surf, HORN, (int(tx), int(ty)), max(1, int(1.8 * ss)))


# ── one folded bat wing ──────────────────────────────────────────────────────

def _bat_wing(surf, hinge_x, hinge_y, span, ss, *, side):
    """One broad flat-faceted bat wing folded behind the body. A hard membrane
    fan: a few straight finger-ribs spoking out from the hinge, the membrane
    filled flat between them with scalloped bottom arcs. Kept BOLD + simple so the
    wing anchors the silhouette at 1x (the per-pick spread note: wings give the
    figure its width read)."""
    s = side
    # Finger-rib tips fanning out + down from the hinge.
    ribs = [
        (hinge_x + s * span * 0.30, hinge_y - span * 0.34),   # top short finger
        (hinge_x + s * span * 0.78, hinge_y - span * 0.12),   # upper long finger
        (hinge_x + s * span * 0.96, hinge_y + span * 0.30),   # mid finger
        (hinge_x + s * span * 0.66, hinge_y + span * 0.62),   # lower finger
        (hinge_x + s * span * 0.22, hinge_y + span * 0.70),   # bottom claw
    ]
    # Membrane polygon: hinge -> down the ribs -> back, with scalloped lower edge.
    poly = [(hinge_x, hinge_y - span * 0.30)]
    poly += ribs
    poly += [(hinge_x, hinge_y + span * 0.30)]
    poly = [(int(x), int(y)) for x, y in poly]
    pygame.draw.polygon(surf, WING_DK, poly)
    inset = [(int(hinge_x), int(hinge_y - span * 0.22))]
    inset += [(int(x - s * 2 * ss), int(y)) for x, y in ribs]
    inset += [(int(hinge_x), int(hinge_y + span * 0.24))]
    pygame.draw.polygon(surf, WING, inset)
    # Top-left rim sheen along the leading (upper) edge.
    lead = [(int(hinge_x), int(hinge_y - span * 0.26)),
            (int(ribs[0][0]), int(ribs[0][1])),
            (int(ribs[1][0]), int(ribs[1][1]))]
    pygame.draw.lines(surf, WING_SH, False, lead, max(1, int(2 * ss)))
    # Finger-rib bones spoking from the hinge (dark struts).
    for rx, ry in ribs:
        pygame.draw.line(surf, WING_DK, (int(hinge_x), int(hinge_y)),
                         (int(rx), int(ry)), max(1, int(2.4 * ss)))
        pygame.draw.circle(surf, WING_DK, (int(rx), int(ry)), max(1, int(2.4 * ss)))


# ── the blood-red pentagram medallion ────────────────────────────────────────

def _pentagram(surf, cx, cy, r, ss):
    """A small upright pentagram in a blood-red gold-rimmed disc on the chest —
    the unmistakable Baphomet/Lévi sigil. Star drawn as a 5-point line loop."""
    pygame.draw.circle(surf, GOLD, (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, PENTA_DK, (int(cx), int(cy)), max(1, int(r - 1.5 * ss)))
    pygame.draw.circle(surf, PENTA, (int(cx), int(cy)), max(1, int(r - 3 * ss)))
    pygame.draw.circle(surf, GOLD_HI, (int(cx - r * 0.3), int(cy - r * 0.3)),
                       max(1, int(r * 0.18)))
    pts = []
    for k in range(5):
        a = -math.pi / 2 + k * (2 * math.tau / 5)   # step by 2/5 turn = star
        pts.append((cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62))
    pts = [(int(x), int(y)) for x, y in pts]
    pygame.draw.lines(surf, GOLD_HI, True, pts, max(1, int(1.6 * ss)))


# ── the goat head ─────────────────────────────────────────────────────────────

def _goat_head(surf, cx, cy, r, ss, *, night=False, tilt=0.0):
    """The chibi Baphomet head: a furry indigo cranium, a LONG rectangular cream
    goat MUZZLE jutting down-forward (never skull-round), big dopey sulphur eyes
    with rectangular slot pupils, a chin beard, two back-swept ridged horns, and
    the warm crown-torch burning between the horns. `tilt` adds the goofy derp
    head-lean; `night` lifts the eye + torch so the face reads on a dark sky."""
    # Furry cranium dome.
    _triad_circle(surf, cx, cy, r, FUR)

    # Two stub fur ears poking out low at the sides (goat ears, before the horns).
    for s in (-1, 1):
        ex = cx + s * r * 0.92
        ey = cy + r * 0.18
        pts = [(cx + s * r * 0.6, cy - r * 0.05),
               (ex, ey - r * 0.18),
               (ex + s * r * 0.18, ey + r * 0.30),
               (cx + s * r * 0.55, cy + r * 0.35)]
        pygame.draw.polygon(surf, FUR_DK, [(int(x), int(y)) for x, y in pts])
        pygame.draw.polygon(surf, FUR,
                            [(int(x - s * ss), int(y)) for x, y in pts])

    # LONG goat SNOUT jutting down-FORWARD — the face identity. A real goat muzzle
    # is a long shape that TAPERS forward to a rounded tip (nostrils at the tip),
    # not a square face-plate. Built as a tapering polygon: wide where it meets the
    # cranium, narrowing to a rounded front tip, with a down-curved mouth-line. The
    # tilt leans the snout tip forward for the derp read.
    mw = r * 0.96               # width at the cranium join (the snout root)
    snout_len = r * 1.26        # how far the snout reaches down-forward
    root_y = cy + r * 0.34
    lean = tilt * r * 0.42      # derp: the tip drifts to the leading side
    tip_x = cx + lean
    tip_y = root_y + snout_len
    tip_w = mw * 0.46           # the rounded forward tip is ~half the root width
    # Dark-core silhouette (slightly larger), then the flat ash fill on top.
    def _snout(col, grow):
        return [(cx - mw * 0.5 - grow, root_y - grow * 0.5),
                (cx - tip_w * 0.5 + lean - grow * 0.4, tip_y - tip_w * 0.6),
                (tip_x - tip_w * 0.18, tip_y + grow),           # rounded tip L
                (tip_x + tip_w * 0.18, tip_y + grow),           # rounded tip R
                (cx + tip_w * 0.5 + lean + grow * 0.4, tip_y - tip_w * 0.6),
                (cx + mw * 0.5 + grow, root_y - grow * 0.5)]
    pygame.draw.polygon(surf, _shade_c(MUZZLE, -40),
                        [(int(x), int(y)) for x, y in _snout(MUZZLE, 2 * ss)])
    pygame.draw.polygon(surf, MUZZLE,
                        [(int(x), int(y)) for x, y in _snout(MUZZLE, 0)])
    # Round the very tip so it never reads as a chiselled box.
    pygame.draw.circle(surf, MUZZLE, (int(tip_x), int(tip_y - tip_w * 0.18)),
                       max(1, int(tip_w * 0.5)))
    # Top-left sheen along the upper-left of the snout (form, not a face-plate).
    pygame.draw.ellipse(surf, MUZZLE_SH,
                        (int(cx - mw * 0.40), int(root_y + snout_len * 0.06),
                         int(mw * 0.42), int(snout_len * 0.40)))

    # Two nostrils at the FRONT of the rounded tip — slim curved nostril nicks
    # flanking the tip centre (a goat nose), NOT vertical face-plate slots.
    nose_y = tip_y - tip_w * 0.30
    for s in (-1, 1):
        nx = tip_x + s * tip_w * 0.26
        pygame.draw.ellipse(surf, MUZZLE_DK,
                            (int(nx - 3.2 * ss), int(nose_y - 2.2 * ss),
                             int(6.4 * ss), int(5.2 * ss)))
        pygame.draw.ellipse(surf, EYE_SLOT,
                            (int(nx - 1.8 * ss), int(nose_y - 1.4 * ss),
                             int(3.0 * ss), int(3.4 * ss)))

    # A DOWN-CURVED mouth-line set back from the tip (the solemn goat frown). Drawn
    # as a shallow dark arc so the snout has a clear lip, not a blank plate.
    mouth_y = root_y + snout_len * 0.62
    mouth_pts = []
    for i in range(9):
        t = i / 8
        mxp = cx - mw * 0.30 + lean * 0.6 + t * mw * 0.60
        myp = mouth_y + math.sin(t * math.pi) * mw * 0.16   # bows DOWN at centre
        mouth_pts.append((int(mxp), int(myp)))
    pygame.draw.lines(surf, MUZZLE_DK, False, mouth_pts, max(1, int(2.2 * ss)))

    # Chin beard — a short stack of indigo fur tufts hanging below the snout tip.
    for k, (dx, dl) in enumerate(((-0.16, 0.9), (0.0, 1.0), (0.16, 0.85))):
        bx = tip_x + dx * mw
        by = tip_y + tip_w * 0.10
        bl = r * 0.42 * dl
        pts = [(bx - r * 0.10, by),
               (bx, by + bl),
               (bx + r * 0.10, by)]
        pygame.draw.polygon(surf, FUR_DK, [(int(x), int(y)) for x, y in pts])
        pygame.draw.polygon(surf, FUR,
                            [(int(x - ss), int(y - ss)) for x, y in pts])

    # Big dopey goat eyes high on the cranium — sulphur sclera with a horizontal
    # RECTANGULAR slot pupil (the goofy goat-pupil scary-cute lever). A touch of
    # derp via the `tilt` skewing the slot.
    for s in (-1, 1):
        ex = cx + s * r * 0.42
        ey = cy - r * 0.04
        er = r * 0.30
        if night:
            blit_glow(surf, int(ex), int(ey), int(er * 1.4), EYE, alpha=120)
        pygame.draw.circle(surf, EYE_SLOT, (int(ex), int(ey)), int(er + ss))
        pygame.draw.circle(surf, EYE, (int(ex), int(ey)), int(er))
        # Horizontal rectangular slot pupil.
        pw = er * 1.3
        ph = er * 0.46
        prect = pygame.Rect(int(ex - pw * 0.5), int(ey - ph * 0.5 + tilt * s * er * 0.3),
                            int(pw), int(ph))
        pygame.draw.rect(surf, EYE_SLOT, prect, border_radius=max(1, int(ph * 0.3)))
        # Tiny sheen dot top-left = the wet dopey catch.
        pygame.draw.circle(surf, EYE_CATCH,
                           (int(ex - er * 0.4), int(ey - er * 0.5)),
                           max(1, int(er * 0.18)))

    # Two big back-swept ridged horns from the upper brow.
    horn_len = r * 1.55
    for s in (-1, 1):
        _goat_horn(surf, cx + s * r * 0.46, cy - r * 0.62, horn_len, ss, side=s)

    # The warm crown-torch burning HIGH and CLEAR between the horns. Raised off the
    # cranium on a slim indigo stub so a band of dark cranium shows beneath the
    # flame between the horn bases — it reads as a flame RISING between the horns,
    # never as a gold skullcap fused onto the dome. A small gold cradle ring caps
    # the stub; the flame is a TALL NARROW teardrop above it.
    stub_top = cy - r * 0.98          # lifted (was -0.74) to clear the dome
    stub_len = r * 0.30
    pygame.draw.rect(surf, FUR_DK,
                     (int(cx - 2.4 * ss), int(stub_top), int(4.8 * ss), int(stub_len)),
                     border_radius=max(1, int(2 * ss)))
    # A compact gold cradle ring at the stub top (the flame's only gold seat).
    pygame.draw.circle(surf, GOLD, (int(cx), int(stub_top)), max(1, int(3.4 * ss)))
    pygame.draw.circle(surf, _shade_c(GOLD, -40), (int(cx), int(stub_top)),
                       max(1, int(3.4 * ss)), max(1, int(ss)))
    fh = r * (1.02 if not night else 1.14)
    _torch_flame(surf, cx, stub_top - 1 * ss, fh, ss, point_up=True, narrow=True)


# ── the full boss figure ──────────────────────────────────────────────────────

def build_baalgoat(scale=1.0, ss=3, *, night=False):
    """The full Baalgoat boss on its own transparent surface. A big dopey goat
    head over a squat indigo body, folded bat wings spread behind for the width
    read, a pentagram medallion at the chest, and stub hooved legs. Returns an
    outlined surface and its baseline (feet) y for placement."""
    H = int(270 * scale)
    W = int(210 * scale)
    pad = int(60 * scale)
    surf = pygame.Surface(((W + pad * 2) * ss, (H + pad) * ss), pygame.SRCALPHA)
    cx = (W // 2 + pad) * ss

    head_r = int(H * 0.20) * ss
    head_cy = int(pad * 0.5) * ss + head_r * 1.55   # leave room for horns + torch
    head_cx = cx

    body_top = head_cy + head_r * 1.55
    body_w = W * 0.50 * ss
    body_h = int(H * 0.34) * ss
    body_cy = body_top + body_h * 0.5

    # Wings FIRST (behind the body) — broad fans giving the figure its width.
    wing_span = head_r * 2.3
    for s in (-1, 1):
        _bat_wing(surf, cx + s * body_w * 0.42, body_top + body_h * 0.12,
                  wing_span, ss, side=s)

    # Squat indigo body (a rounded barrel torso) with the triad. A thicker FUR_DK
    # rim at the TOP of the torso reads as the head/body neck seam so the chibi
    # proportions don't collapse into one indigo lump at 1x (head + body share the
    # FUR fill, so they need a value-step break, not just a 1px keyline).
    brect = (int(cx - body_w * 0.5), int(body_top), int(body_w), int(body_h))
    pygame.draw.ellipse(surf, FUR_DK, brect)
    pygame.draw.ellipse(surf, FUR,
                        (brect[0] + 2 * ss, brect[1] + int(7 * ss),
                         brect[2] - 4 * ss, brect[3] - int(8 * ss)))
    pygame.draw.ellipse(surf, FUR_SHEEN,
                        (brect[0] + int(body_w * 0.16), brect[1] + int(body_h * 0.16),
                         int(body_w * 0.42), int(body_h * 0.34)))

    # Stub hooved legs peeking under the torso.
    for s in (-1, 1):
        lx = cx + s * body_w * 0.26
        ly = body_top + body_h * 0.92
        leg_h = int(H * 0.10) * ss
        pygame.draw.line(surf, FUR_DK, (int(lx), int(ly)),
                         (int(lx), int(ly + leg_h)), max(1, int(9 * ss)))
        pygame.draw.line(surf, FUR, (int(lx), int(ly)),
                         (int(lx), int(ly + leg_h)), max(1, int(5 * ss)))
        # Cloven hoof: a small split dark wedge.
        hy = ly + leg_h
        pygame.draw.polygon(surf, EYE_SLOT, [
            (int(lx - 6 * ss), int(hy)), (int(lx + 6 * ss), int(hy)),
            (int(lx + 4 * ss), int(hy + 8 * ss)), (int(lx - 4 * ss), int(hy + 8 * ss))])
        pygame.draw.line(surf, FUR_DK, (int(lx), int(hy + 1 * ss)),
                         (int(lx), int(hy + 8 * ss)), max(1, int(2 * ss)))
    feet_y = body_top + body_h * 0.92 + int(H * 0.10) * ss + 8 * ss

    # Pentagram medallion at the chest — an ACCENT emblem, trimmed ~20% so it does
    # not compete with the head as a second focal point.
    _pentagram(surf, cx, body_cy + body_h * 0.04, head_r * 0.37, ss)

    # The head LAST so muzzle + horns + torch sit over the body/wings.
    _goat_head(surf, head_cx, head_cy, head_r, ss, night=night, tilt=0.18)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(small), feet_y / ss


# ── the crown-torch POLE pillar pair (prop -> pillar mirror proof) ────────────

OVERHANG = 12


def _torch_pole_body(surf, cx, y0, y1, hw, ss):
    """The repeatable PILLAR BODY: a banded indigo torch-pole. Gold cuff bands at
    a fixed pitch are the tile repeat; the triad (dark-core stripe -> fur fill ->
    violet sheen stripe) gives the round-pole read flat."""
    # Dark-core -> fill -> sheen vertical stripes.
    pygame.draw.rect(surf, FUR_DK, (int(cx - hw), int(y0), int(hw * 2), int(y1 - y0)))
    pygame.draw.rect(surf, FUR, (int(cx - hw + 2 * ss), int(y0),
                                 int(hw * 2 - 4 * ss), int(y1 - y0)))
    pygame.draw.rect(surf, FUR_SHEEN, (int(cx - hw + 2 * ss), int(y0),
                                       max(1, int(hw * 0.5)), int(y1 - y0)))
    # Gold cuff bands at a fixed pitch = the tileable repeat. Anchored UP from the
    # gap-edge (y1) so the band rhythm meets the gap at the same offset on both the
    # top and bottom posts — the top/bottom flip then mirrors into one continuous
    # banded pole regardless of either post's length.
    pitch = 46 * ss
    yy = y1 - 22 * ss
    while yy > y0 + 6 * ss:
        pygame.draw.rect(surf, GOLD_HI, (int(cx - hw), int(yy - 2 * ss),
                                         int(hw * 2), int(2 * ss)))
        pygame.draw.rect(surf, GOLD, (int(cx - hw), int(yy), int(hw * 2), int(6 * ss)))
        pygame.draw.rect(surf, _shade_c(GOLD, -40), (int(cx - hw), int(yy + 6 * ss),
                                                     int(hw * 2), int(2 * ss)))
        yy -= pitch


def _torch_pillar_obstacle(height, ss, *, flip):
    """One crown-torch-pole PILLAR obstacle: the banded indigo POLE *is* the body
    and fills the whole post; a SMALL gap-edge cap (a slim gold cuff + a compact
    brazier rim) caps the gap end with a warm flame flourishing INTO the gap.
    `flip` makes the top pillar's flame point DOWN into the gap; the bottom's UP —
    proving the prop mirrors top<->bottom into one clean vertical banded pole with
    a flame at each gap-edge (the prop->pillar decision). The cap is now a small
    detachable flourish so the tileable body dominates even at short bottom-post
    heights."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 11 * ss
    # SMALL cap so the banded pole body always renders + tiles (was 96px = whole
    # post). The brazier rim + flame live in this band; the pole owns the rest.
    cap_band = min(int(bh * 0.42), int(30 * ss))
    bowl_y = bh - cap_band
    # Pole body fills everything above the cap edge — the tileable repeat.
    _torch_pole_body(surf, cx, 0, bowl_y, hw, ss)
    # A compact gold brazier rim seated on the pole top (small, not a bowl-blob).
    rim = [(cx - hw * 1.5, bowl_y + 9 * ss),
           (cx - hw * 1.05, bowl_y - 1 * ss),
           (cx + hw * 1.05, bowl_y - 1 * ss),
           (cx + hw * 1.5, bowl_y + 9 * ss)]
    pygame.draw.polygon(surf, _shade_c(GOLD, -40), [(int(x), int(y)) for x, y in rim])
    rim2 = [(cx - hw * 1.28, bowl_y + 8 * ss),
            (cx - hw * 0.92, bowl_y + 1 * ss),
            (cx + hw * 0.92, bowl_y + 1 * ss),
            (cx + hw * 1.28, bowl_y + 8 * ss)]
    pygame.draw.polygon(surf, GOLD, [(int(x), int(y)) for x, y in rim2])
    pygame.draw.line(surf, GOLD_HI, (int(cx - hw * 1.22), int(bowl_y + 7 * ss)),
                     (int(cx - hw * 0.85), int(bowl_y + 1 * ss)), max(1, int(2 * ss)))
    # Warm flame leaping UP out of the rim (into the gap on the un-flipped tile);
    # sized to the small cap so it stays a gap-edge accent, not a headstone.
    _torch_flame(surf, cx, bowl_y - 1 * ss, 40 * ss, ss, point_up=True)

    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    out = _add_outline(out)
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── sheet composition ──────────────────────────────────────────────────────────

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
    sheet.fill((34, 32, 46))
    _label(sheet, font, "BAALGOAT  —  GROUP B  take B2  —  indigo-goat & torch-gold  —  round 2", 18, 12)
    _label(sheet, small, "r2: forward-tapering goat SNOUT (tip nostrils + down-curved mouth, value dropped) / pole-IS-body pillar w/ small gap-edge cap / lifted crown-torch",
            18, 32, (200, 196, 210))

    # — Cell A: boss at showcase scale, on a neutral panel.
    panel = pygame.Rect(18, 56, 360, 560)
    pygame.draw.rect(sheet, (50, 48, 64), panel, border_radius=8)
    pygame.draw.rect(sheet, (90, 86, 112), panel, 2, border_radius=8)
    boss, _ = build_baalgoat(scale=1.55, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 16))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)

    # — Cell B: the crown-torch POLE as a tileable PILLAR pair, at TRUE obstacle scale.
    panelB = pygame.Rect(394, 56, 360, 560)
    bg = _sky(panelB.w, panelB.h, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (90, 86, 112), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE obstacle scale", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 470
    slice_x = panelB.x + 26
    slice_y = panelB.y + 46
    gap_top = 168
    gap_h = 120
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _torch_pillar_obstacle(top_h, 3, flip=True)
    bot_pillar = _torch_pillar_obstacle(bot_h, 3, flip=False)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (255, 255, 255), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native: the banded indigo POLE", slice_x - 2, slice_y + slice_h + 6, (20, 20, 30))
    _label(sheet, small, "IS the body; cuff bands tile the", slice_x - 2, slice_y + slice_h + 22, (20, 20, 30))
    _label(sheet, small, "mirror; small cap at each gap-edge", slice_x - 2, slice_y + slice_h + 38, (20, 20, 30))

    # 2x zoom of the GAP region so the brazier-flame cap + cuff banding is legible.
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    zoom_src.blit(top_pillar, (-2, -(gap_top - 70) - 2))
    zoom_src.blit(bot_pillar, (-2, gap_h + 70 - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 184
    zy = panelB.y + 70
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the gap:", zx - 4, zy - 16, (255, 255, 255))
    _label(sheet, small, "brazier-flame cap flares", zx - 4, zy + zh * 2 + 6, (20, 20, 30))
    _label(sheet, small, "INTO the gap; warm-gold,", zx - 4, zy + zh * 2 + 22, (20, 20, 30))
    _label(sheet, small, "no neon / no green soul-fire", zx - 4, zy + zh * 2 + 38, (20, 20, 30))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies.
    panelC = pygame.Rect(770, 56, 392, 560)
    pygame.draw.rect(sheet, (50, 48, 64), panelC, border_radius=8)
    pygame.draw.rect(sheet, (90, 86, 112), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, _ = build_baalgoat(scale=0.62, ss=3)
    boss1x_n, _ = build_baalgoat(scale=0.62, ss=3, night=True)
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

    # — Grayscale silhouette check (face must read without the torch/eye glow).
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
    _label(sheet, small, "grayscale: goat-muzzle + back-swept horns carry the read (no torch reliance)",
            gpanel.x + 6, gpanel.y + 6, (30, 30, 30))

    # — Footer captions.
    _label(sheet, small,
           "scary-cute: big dopey rectangular goat pupils + a derp head-tilt undercut the solemn occult pose — solemn-goat menace, never grim.",
           18, SH - 124, (210, 206, 220))
    _label(sheet, small,
           "house style: FLAT fills, hard ink keyline grown from the alpha mask, dark-core->fill->top-left violet sheen triad, ss=3 -> smoothscale.",
           18, SH - 104, (210, 206, 220))
    _label(sheet, small,
           "guardrails: the ONLY curved-horn pair in the set (owned); the crown-torch is WARM CLASSIC gold (no neon, no green soul-fire).",
           18, SH - 84, (210, 206, 220))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "devil", "baalgoat")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
