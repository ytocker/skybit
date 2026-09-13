"""Production FLYING TOASTER store skin — round-2 build (single design).

A secret ultra-premium ABSURD flyer: the player's flapping bird becomes a
chrome toaster with little wings — the classic After Dark gag. The build
animates over the 4 base wing poses (`parrot._WING_ANGLES`) and is rotated by
the bird's dive/climb tilt by the shared getter factory.

Round 1 shipped 5 explorations; the art-director picked V5 NOIR CHROME as the
only candidate that still reads as a toaster at 40px, then asked for ONE
converged build. This module is that build:

  * NOIR CHROME body (matte black + chrome rail) — the silhouette that
    survives the downscale on a bright DAY sky.
  * SOFT feathered "After Dark" wings (V1's rounded fan, drawn in chrome-white
    so they still read on a night sky) — the whole gag is *soft bird wings on
    a chrome toaster*, so the wings must read bird, never swept-jet.
  * A thick warm ember slot — the night-side signature, one continuous hot bar.
  * Two gold toast slices held fully inside the top edge across all 4 frames.

Contract (mirrors game/animal_skins.py so this lifts straight into a
production game/animal_toaster.py later):

  * `build_toaster(wing_angle_deg) -> pygame.Surface`  draws one flat frame
    on a 64×84 SRCALPHA canvas; collision stays the fixed 14px circle at the
    BODY centre (32,44), independent of the sprite, so the toaster body mass
    sits on the base bird's body anchor for fairness.
  * `get_toaster = _make_prebuilt_skin(build_toaster)` — cached
    `(frame_idx, tilt_deg) -> Surface` getter.
  * `BUILDERS = {"skin_toaster": get_toaster}` — the production key.

North star: "a skin lives or dives at 40px in motion." The BODY is the read;
the gold-toast-on-chrome contrast is the colour pop that must survive the
downscale on day AND night.
"""
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (toast pops above the body, wings swing wide) ───────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for popping toast + wing arcs
DY          = 12                # body offset down into the tall canvas

# Toaster body centre at the base bird body anchor → (32, 44).
BCX, BCY = 32, 32 + DY
# Top of the chrome body (where the slot + toast live).
TOP_Y    = BCY - 14


# ── shared factory (local copy of animal_skins._make_prebuilt_skin) ──────────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


# ── tiny shared drawing helpers ──────────────────────────────────────────────
def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(angle_deg):
    """Map a wing angle to a 0..1 'wing is up' factor. _WING_ANGLES runs
    50→-40, so this drives the wing spread and the toast bob (mid-pop)."""
    return (angle_deg + 40) / 90.0


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


# ═════════════════════════════════════════════════════════════════════════════
# NOIR CHROME · production palette
# Matte-black body so the silhouette pops on a bright pale-blue DAY sky;
# chrome rail + warm ember slot so it pops at NIGHT.
# ═════════════════════════════════════════════════════════════════════════════
_BLK   = (52, 56, 66)
_BLKD  = (28, 30, 38)
_BLKH  = (96, 102, 116)
# Belly is pushed darker/cooler than the lit body so the lower silhouette
# stays crisp against the brightest day sky (was reading washed-out before).
_BLKB  = (20, 22, 30)
_CHRM  = (200, 208, 220)
_CHRD  = (120, 128, 142)
_CHRH  = (250, 254, 255)

_GOLD  = (244, 190, 92)
_GLDD  = (180, 120, 48)
_GLDH  = (255, 230, 150)
# Crust pushed cool-dark: doubles as the deuteranope seam between the gold
# toast base and the orange ember slot so the two warm bands never merge.
_CRST  = (104, 64, 30)

# Ember: a continuous hot bar warmed toward gold so it reads as ONE element,
# not a thin orange line, at 40px. Restraint — a tight 1px bloom, no halo.
_EMBER  = (255, 176, 70)
_EMBERH = (255, 224, 150)
_EMBERG = (255, 150, 56)          # the 1px bloom edge

# Chrome-white feathered wing — V1's value language so it reads as a soft
# bird wing, kept mid-grey/chrome-white so it survives on the night sky.
_WING  = (224, 230, 240)
_WINGD = (138, 146, 162)
_WINGH = (252, 255, 255)


def _feather_wing(angle_deg, sgn, base, dark, light, scale=1.0):
    """A little feathered bird wing — three rounded primary feathers fanning
    out (V1's shape language). Soft round lobes, NO swept-jet rake: the whole
    gag is bird wings on a chrome box, so this must read BIRD, not aero. Kept
    chrome-white so the soft span still pops on a dark night sky."""
    w = pygame.Surface((40, 36), pygame.SRCALPHA)
    # Three overlapping rounded feather lobes, rising toward the tip.
    for lx, ly, lw, lh in ((10, 16, 13, 8), (18, 12, 13, 8), (26, 10, 12, 7)):
        _aaellipse(w, dark, (lx + 1, ly + 1), lw, lh)
        _aaellipse(w, base, (lx, ly), lw, lh)
    # Bright leading edge along the top of the fan sells the chrome sheen.
    pygame.draw.line(w, light, (10, 12), (32, 7), 2)
    # Rounded shoulder root keeps the wing attached to the body softly.
    _aaellipse(w, base, (10, 18), 6, 7)
    if scale != 1.0:
        sz = (max(1, int(40 * scale)), max(1, int(36 * scale)))
        w = pygame.transform.smoothscale(w, sz)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def _toast(surf, cx, top_y, w, h, *, gold, gold_d, gold_h, crust):
    """One slice of toast: warm-gold body, darker crust rim, a bright top
    bevel. The gold-on-chrome contrast is the whole skin's colour tell, so the
    crust rim keeps the slice legible at 40px when the body goes mirror-grey,
    and the dark crust base doubles as the seam against the warm ember slot."""
    half = w // 2
    pts = [
        (cx - half, top_y + h),
        (cx - half, top_y + 5),
        (cx - half + 2, top_y + 1),
        (cx - 2, top_y),
        (cx + 2, top_y),
        (cx + half - 2, top_y + 1),
        (cx + half, top_y + 5),
        (cx + half, top_y + h),
    ]
    pygame.draw.polygon(surf, crust, pts)
    inner = [(x - (1 if x < cx else -1) if abs(x - cx) > 2 else x, y + 1)
             for x, y in pts]
    pygame.draw.polygon(surf, gold, inner)
    pygame.draw.line(surf, gold_h, (cx - half + 3, top_y + 3),
                     (cx + half - 3, top_y + 3), 2)
    pygame.draw.polygon(surf, gold_d, pts, 1)


def _chrome_body(surf, cx, cy, hw, hh, *, base, dark, light, top_hi, belly,
                 corner=5):
    """A rounded-rect appliance body shaded for metal: a bright top band, a
    mid base, and a dark cool underbelly. The bright-top / dark-bottom split is
    the cheapest, most reliable 'this is shiny metal' cue at gameplay size; the
    extra-dark belly keeps the lower silhouette crisp on a bright day sky."""
    rect = pygame.Rect(cx - hw, cy - hh, hw * 2, hh * 2)
    # Cool dark underbody first (full box), then the lit body inset from below.
    pygame.draw.rect(surf, belly, rect, border_radius=corner)
    lit = pygame.Rect(cx - hw, cy - hh, hw * 2, int(hh * 1.45))
    pygame.draw.rect(surf, base, lit, border_radius=corner)
    # Bright top highlight band (the mirror catch-light).
    hi = pygame.Rect(cx - hw + 2, cy - hh + 2, hw * 2 - 4, hh)
    pygame.draw.rect(surf, light, hi, border_radius=corner)
    pygame.draw.line(surf, top_hi, (cx - hw + corner, cy - hh + 2),
                     (cx + hw - corner, cy - hh + 2), 2)
    # A vertical specular streak — the classic curved-chrome reflection.
    streak = pygame.Surface((4, hh * 2 - 4), pygame.SRCALPHA)
    streak.fill((*top_hi, 120))
    surf.blit(streak, (cx - hw // 2, cy - hh + 2))
    pygame.draw.rect(surf, dark, rect, 1, border_radius=corner)


def build_toaster(wing_angle_deg):
    """One flat NOIR CHROME frame for the given base wing angle.

    Wings stay inside the body's silhouette width (or only just break it) so
    the toaster BODY stays the dominant mass — the toaster, not the wings, is
    the read. The toast 'mid-pop' (a small jump on the flap apex) is what makes
    it read as a *flying* toaster rather than a floating one."""
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 26          # softer arc than the old swept wing
    # Mid-pop: both slices jump ~2px higher at the flap apex (f→1) and the
    # ember brightens a touch, so the appliance reads as actively flying.
    pop = int(f * 2)
    bob = int((f - 0.5) * 3)         # gentle alternating bob, tight (±1px)

    # Far wing (behind body), opposite phase for depth — tucked narrow so it
    # barely breaks the body edge.
    _rot_blit(surf, _feather_wing(14 + spread, +1, _WING, _WINGD, _WINGH,
                                  scale=0.88), (BCX + 14, BCY - 2))

    # Two gold toast slices. Top edges are clamped so the slices stay fully
    # inside the canvas top across every frame (the toast is half the tell —
    # never let it clip). h=14 from a base of TOP_Y-7 keeps the crown ≥ y=3.
    t_left_top  = TOP_Y - 7 - pop - max(0, bob)
    t_right_top = TOP_Y - 7 - pop - max(0, -bob)
    _toast(surf, BCX - 6, t_left_top, 13, 14, gold=_GOLD,
           gold_d=_GLDD, gold_h=_GLDH, crust=_CRST)
    _toast(surf, BCX + 8, t_right_top, 13, 14, gold=_GOLD,
           gold_d=_GLDD, gold_h=_GLDH, crust=_CRST)

    # Matte-black body with a chrome base rail.
    _chrome_body(surf, BCX, BCY, 18, 15, base=_BLK, dark=_BLKD,
                 light=_BLKH, top_hi=_BLKH, belly=_BLKB)
    pygame.draw.rect(surf, _CHRM, (BCX - 17, BCY + 9, 34, 5), border_radius=2)
    pygame.draw.rect(surf, _CHRD, (BCX - 17, BCY + 9, 34, 5), 1, border_radius=2)
    pygame.draw.line(surf, _CHRH, (BCX - 15, BCY + 10), (BCX + 15, BCY + 10), 1)

    # ── Ember slot: ONE thick continuous hot bar (the night-side signature) ──
    # Chrome lip frames a dark slot mouth; the 2px ember bar glows warm-gold,
    # with a tight 1px bloom and a 1px dark crust seam above it so the gold
    # toast bases never merge into the orange band (deuteranope-safe).
    pygame.draw.rect(surf, _CHRD, (BCX - 15, TOP_Y - 1, 30, 7), border_radius=2)
    pygame.draw.rect(surf, (22, 22, 26), (BCX - 13, TOP_Y, 26, 5),
                     border_radius=1)
    # 1px dark crust seam between the toast bases and the ember.
    pygame.draw.line(surf, (60, 40, 28), (BCX - 13, TOP_Y + 1),
                     (BCX + 13, TOP_Y + 1), 1)
    # Tight 1px bloom, then the 2px hot bar, then a hot highlight core.
    bright = 1 if f > 0.6 else 0     # mid-pop: glow brightens at the apex
    pygame.draw.line(surf, _EMBERG, (BCX - 12, TOP_Y + 4),
                     (BCX + 12, TOP_Y + 4), 1)
    pygame.draw.line(surf, _EMBER, (BCX - 12, TOP_Y + 3),
                     (BCX + 12, TOP_Y + 3), 2)
    pygame.draw.line(surf, _EMBERH if bright else _GLDH,
                     (BCX - 10, TOP_Y + 3), (BCX + 10, TOP_Y + 3), 1)
    pygame.draw.line(surf, _CHRH, (BCX - 14, TOP_Y - 1), (BCX + 14, TOP_Y - 1), 1)

    # Minimal chrome lever + a small ember LED dial.
    pygame.draw.line(surf, _CHRD, (BCX + 18, BCY - 3), (BCX + 22, BCY - 3), 3)
    pygame.draw.circle(surf, _CHRM, (BCX + 23, BCY - 3), 3)
    pygame.draw.circle(surf, _CHRD, (BCX + 23, BCY - 3), 3, 1)
    pygame.draw.circle(surf, _EMBER, (BCX - 8, BCY + 5), 2)
    pygame.draw.circle(surf, _CHRD, (BCX - 8, BCY + 5), 3, 1)

    # Chrome feet.
    for fx in (BCX - 11, BCX + 11):
        pygame.draw.rect(surf, _CHRD, (fx - 2, BCY + 14, 4, 4), border_radius=1)

    # Near wing (over the body) — the hero soft feather span, kept narrow and
    # set low on the flank so the black/chrome two-tone body stays the read.
    _rot_blit(surf, _feather_wing(-12 - spread, -1, _WING, _WINGD, _WINGH,
                                  scale=0.88), (BCX - 13, BCY + 2))
    return surf


get_toaster = _make_prebuilt_skin(build_toaster)


# Production registry — single converged build under the production key.
BUILDERS = {"skin_toaster": get_toaster}
