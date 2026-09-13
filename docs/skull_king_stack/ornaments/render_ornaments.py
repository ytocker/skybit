"""The Skull-King's DECORATIVE elements, pulled out of the chosen design
(Asthi-Dakini SWITCHED+BIG) as standalone reference swatches: the four bead
colours of her jewelry, plus small versions of her two cyan jewels.

Every element reuses the design's OWN primitives + palette from render_switchbig,
so each swatch is identical to the same element on her body — this is a catalog of
what already exists on her, not a redesign. Design-only; never enters the bundle.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def _bead(surf, cx, cy, r, s, color, sheen):
    """One jewelry bead in the design's own bead recipe (triad_circle body + a
    single top-left sheen dot) — the exact thing bead_strand drops along a strand,
    pulled out so the catalog shows one clean bead."""
    cx, cy = int(cx), int(cy)
    sk.triad_circle(surf, color, (cx, cy), max(1, int(r)), ow=max(1, int(1.0 * s)), core=False)
    pygame.draw.circle(surf, sheen, (cx - int(r * 0.28), cy - int(r * 0.30)), max(1, int(r * 0.30)))


def bead_white(surf, cx, cy, r, s):
    """Pale bone bead — the dominant strand bead (BEAD body, near-white sheen)."""
    _bead(surf, cx, cy, r, s, sk.BEAD, sk.BEAD_BR)


def bead_gold(surf, cx, cy, r, s):
    """Warm gold spacer-pip — the hue separator threaded every few beads."""
    _bead(surf, cx, cy, r, s, sk.GOLD, sk.GOLD_BR)


def bead_cyan(surf, cx, cy, r, s):
    """Icy-cyan jewel bead — 'bluish like the gem': a domed cyan stone (CYAN over a
    CYAN_D rim, capped with a CYAN_BR glint), the bright blue of her cabochons."""
    cx, cy = int(cx), int(cy)
    pygame.draw.circle(surf, sk.INK, (cx, cy), int(r) + max(1, int(1.0 * s)))
    pygame.draw.circle(surf, sk.CYAN_D, (cx, cy), int(r))
    pygame.draw.circle(surf, sk.CYAN, (cx, cy), max(1, int(r * 0.70)))
    pygame.draw.circle(surf, sk.CYAN_BR, (cx - int(r * 0.30), cy - int(r * 0.32)), max(1, int(r * 0.26)))


def bead_darkblue(surf, cx, cy, r, s):
    """Dark teal-blue cabochon bead — the dim set-stone of the brow band: flat
    CYAN_D with the hard INK keyline (the dimmest jewel tier), a tiny rim glint."""
    sk.triad_circle(surf, sk.CYAN_D, (int(cx), int(cy)), max(1, int(r)),
                    ow=max(1, int(1.0 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, sk.CYAN, (int(cx - r * 0.28), int(cy - r * 0.30)), max(1, int(r * 0.20)))


def gem_thirdeye(surf, cx, cy, r, s):
    """A smaller version of her third-eye cut-gem — the faceted octagonal cyan
    rosette with the white-hot core (the single brightest jewel)."""
    sk.cyan_gem(surf, (int(cx), int(cy)), int(r), s, focal=True)


def ornament_necklace(surf, cx, cy, r, s):
    """A smaller version of the necklace's CENTRE ornament — the concentric ring-eye
    (cyan disc + gold iris ring + pale cyan pupil) that sits in the heart of her
    swag necklace."""
    sk.ring_eye(surf, (int(cx), int(cy)), int(r), s)
