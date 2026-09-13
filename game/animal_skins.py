"""ANIMAL skins for the coin Store — from-scratch creatures.

The ANIMALS tab: nine procedural creatures (owl, toucan, penguin, bat, flamingo,
bald eagle, bee, and the premium gacha showpieces dragon + phoenix). Registered
in ``BUILDERS`` at the bottom and merged into ``parrot.get_skin_frame`` alongside
the costume/parrot-species roster. Survived a two-round graphics-designer /
art-director design loop (VERDICT: SHIP-READY); design record under
docs/creatures/round_{1,2}.{png,md}.

These are NEW from-scratch creatures (NOT the scarlet macaw + an accessory).
Each is the player's flappy bird: it animates over the 4 base wing poses
(`parrot._WING_ANGLES`) and is rotated by the bird's dive/climb tilt by the
shared getter factory.

Contract (mirrors game/store_skins.py so these lift straight into a
production game/animal_skins.py later):

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  draws one flat frame.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)` — caches 4 flat frames + a per-(frame,
    3°-bucket) rotation cache and runs each frame through `parrot._add_outline`.
  * `BUILDERS = {"skin_owl": get_owl, ...}` registry at the bottom.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre, independent of the sprite, so every creature keeps its body mass
near the base bird's body centre (~(32,32) on the 64×60 canvas) for fairness —
no oversized dragons. Creatures that need headroom (owl ear-tufts, dragon/
phoenix crest) draw on a taller composite (COMPOSITE_H) but keep the BODY at
the base anchor so the in-game center-blit rotation maths still holds.

North star, per the brief: "a skin lives or dies at 40px in motion." Every
creature leans on one bold shape + one high-contrast signature feature that
breaks the silhouette and survives the downscale.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (for crests / ear-tufts / tall beaks) ──────────────
# Body stays vertically centred at PARROT_DY so the getter's center-blit
# rotation reuses the base maths. Anchors below are in COMPOSITE space.
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for tufts / crest plumes
DY          = 12                # body offset down into the tall canvas

# Body / head anchors in composite space (base anchors + DY on y).
BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


# ── shared factory (local copy of store_skins._make_prebuilt_skin) ───────────
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


def _eye(surf, cx, cy, r, *, iris=(20, 22, 30), white=(250, 250, 245),
         glint=True):
    """A friendly googly eye: white sclera, dark iris, top-left glint."""
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    if glint:
        pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                           max(1, r // 3))


def _flap(angle_deg):
    """Map a wing angle to a 0..1 'wing is up' factor for flap-driven motion
    (legs swing, membrane stretch, antennae bob). _WING_ANGLES runs 50→-40."""
    return (angle_deg + 40) / 90.0


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


# ═════════════════════════════════════════════════════════════════════════════
# 1 · OWL — round body, huge facial disc + two enormous forward eyes, two
#     pointed ear-tufts. Signature 40px read: the wide white-ringed eyes +
#     the heart-shaped facial disc. Soft brown plush.
# ═════════════════════════════════════════════════════════════════════════════
_OWL_BODY   = (150, 110, 74)
_OWL_BODY_D = (110, 78, 50)
_OWL_BODY_H = (188, 150, 108)
_OWL_BELLY  = (224, 204, 168)
_OWL_DISC   = (236, 220, 188)
_OWL_DISC_D = (200, 178, 140)
_OWL_TUFT   = (96, 66, 42)
_OWL_BEAK   = (244, 188, 70)
_OWL_BEAK_D = (188, 132, 36)


def _owl_wing(angle_deg):
    w = pygame.Surface((44, 44), pygame.SRCALPHA)
    pts = [(22, 22), (40, 16), (40, 30), (24, 38), (14, 32)]
    pygame.draw.polygon(w, _OWL_BODY_D, pts)
    pygame.draw.polygon(w, _OWL_BODY, [(22, 22), (38, 18), (37, 28), (22, 34)])
    # Scalloped feather edge — owl tell.
    for fx in (26, 31, 36):
        pygame.draw.circle(w, _OWL_BODY_H, (fx, 32), 3)
    pygame.draw.line(w, _OWL_BODY_H, (23, 23), (37, 19), 1)
    return pygame.transform.rotate(w, angle_deg)


def build_owl(wing_angle_deg):
    surf = _new()
    # Short fanned tail.
    pygame.draw.polygon(surf, _OWL_BODY_D,
                        [(12, BCY - 4), (4, BCY + 8), (16, BCY + 12)])
    pygame.draw.polygon(surf, _OWL_BODY,
                        [(13, BCY - 2), (7, BCY + 7), (16, BCY + 10)])
    # Plump round body.
    _aaellipse(surf, _OWL_BODY_D, (BCX + 1, BCY + 1), 19, 17)
    _aaellipse(surf, _OWL_BODY, (BCX, BCY), 18, 16)
    # Speckled belly.
    _aaellipse(surf, _OWL_BELLY, (BCX - 2, BCY + 4), 12, 11)
    for sx, sy in ((28, 42), (33, 46), (26, 48), (31, 40), (35, 50)):
        pygame.draw.circle(surf, _OWL_BODY_D, (sx, sy), 1)

    # Far wing tucked behind.
    _rot_blit(surf, _owl_wing(wing_angle_deg * 0.5 - 20), (BCX + 8, BCY - 2))

    # ── BIG facial disc (heart pair of saucers) ──
    for dx in (-7, 7):
        _aaellipse(surf, _OWL_DISC_D, (HCX + dx, HCY + 1), 11, 12)
    for dx in (-7, 7):
        _aaellipse(surf, _OWL_DISC, (HCX + dx, HCY), 10, 11)
    # Ear-tufts breaking the crown.
    for sgn, ex in ((-1, HCX - 9), (1, HCX + 9)):
        pygame.draw.polygon(surf, _OWL_TUFT,
                            [(ex, CROWN_Y + 6), (ex + sgn * 3, CROWN_Y - 6),
                             (ex + sgn * 7, CROWN_Y + 4)])
    # HERO: two enormous eyes.
    for dx in (-7, 7):
        pygame.draw.circle(surf, (255, 255, 255), (HCX + dx, HCY), 7)
        pygame.draw.circle(surf, (40, 30, 24), (HCX + dx, HCY), 7, 1)
        pygame.draw.circle(surf, (24, 26, 34), (HCX + dx + 1, HCY), 4)
        pygame.draw.circle(surf, (255, 255, 255), (HCX + dx - 1, HCY - 2), 2)
    # Beak: small downward triangle between the eyes.
    pygame.draw.polygon(surf, _OWL_BEAK,
                        [(HCX - 2, HCY + 4), (HCX + 2, HCY + 4),
                         (HCX, HCY + 9)])
    pygame.draw.polygon(surf, _OWL_BEAK_D,
                        [(HCX - 2, HCY + 4), (HCX + 2, HCY + 4),
                         (HCX, HCY + 9)], 1)

    # Near wing over the body.
    _rot_blit(surf, _owl_wing(wing_angle_deg), (BCX - 4, BCY))
    # Tiny talons.
    for fx in (28, 36):
        pygame.draw.line(surf, _OWL_BEAK_D, (fx, BCY + 15),
                         (fx, BCY + 19), 2)
    return surf


get_owl = _make_prebuilt_skin(build_owl)


# ═════════════════════════════════════════════════════════════════════════════
# 2 · TOUCAN — glossy blue-black body, white bib, and a HUGE rainbow-orange
#     beak that is bigger than the head. Signature 40px read: the oversized
#     orange beak jutting forward. Toco-toucan palette.
# ═════════════════════════════════════════════════════════════════════════════
_TUC_BODY   = (32, 38, 54)
_TUC_BODY_D = (18, 22, 36)
_TUC_BODY_H = (74, 84, 110)
_TUC_BIB    = (248, 248, 240)
_TUC_BEAK1  = (255, 150, 40)        # orange
_TUC_BEAK2  = (255, 196, 60)        # yellow root
_TUC_BEAK3  = (228, 86, 48)         # red tip
_TUC_BEAK_D = (160, 70, 20)


def _tuc_wing(angle_deg):
    w = pygame.Surface((44, 44), pygame.SRCALPHA)
    pts = [(22, 22), (42, 14), (42, 30), (24, 38), (14, 32)]
    pygame.draw.polygon(w, _TUC_BODY_D, pts)
    pygame.draw.polygon(w, _TUC_BODY, [(22, 22), (40, 16), (39, 28), (22, 34)])
    pygame.draw.line(w, _TUC_BODY_H, (23, 23), (39, 17), 1)
    pygame.draw.line(w, _TUC_BODY_H, (24, 28), (38, 24), 1)
    return pygame.transform.rotate(w, angle_deg)


def build_toucan(wing_angle_deg):
    surf = _new()
    # Cocked tail.
    pygame.draw.polygon(surf, _TUC_BODY_D,
                        [(10, BCY - 6), (3, BCY + 4), (16, BCY + 6)])
    pygame.draw.polygon(surf, _TUC_BODY,
                        [(11, BCY - 4), (6, BCY + 3), (16, BCY + 4)])
    # Body.
    _aaellipse(surf, _TUC_BODY_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, _TUC_BODY, (BCX, BCY), 17, 15)
    # White bib.
    _aaellipse(surf, _TUC_BIB, (BCX + 3, BCY - 1), 11, 10)
    # Gloss sheen.
    sheen = pygame.Surface((20, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (120, 130, 160, 150), sheen.get_rect())
    surf.blit(sheen, (BCX - 12, BCY - 12))

    _rot_blit(surf, _tuc_wing(wing_angle_deg * 0.5 - 18), (BCX + 8, BCY - 2))

    # Head.
    _aaellipse(surf, _TUC_BODY_D, (HCX, HCY + 1), 11, 11)
    _aaellipse(surf, _TUC_BODY, (HCX - 1, HCY), 10, 10)
    # Eye on a pale patch (toucan blue skin around eye).
    pygame.draw.circle(surf, (120, 170, 180), (HCX, HCY - 1), 5)
    _eye(surf, HCX, HCY - 1, 4, iris=(20, 18, 24))

    # ── HERO: the enormous curved beak ──
    by = HCY - 2
    upper = [(HCX + 5, by - 5), (HCX + 30, by - 2), (HCX + 28, by + 4),
             (HCX + 6, by + 3)]
    lower = [(HCX + 6, by + 3), (HCX + 27, by + 5), (HCX + 24, by + 9),
             (HCX + 6, by + 7)]
    # Banded colour: yellow root → orange → red tip.
    pygame.draw.polygon(surf, _TUC_BEAK2, upper)
    pygame.draw.polygon(surf, _TUC_BEAK1,
                        [(HCX + 16, by - 4), (HCX + 30, by - 2),
                         (HCX + 28, by + 4), (HCX + 16, by + 3)])
    pygame.draw.polygon(surf, _TUC_BEAK3,
                        [(HCX + 26, by - 2), (HCX + 30, by - 1),
                         (HCX + 28, by + 4)])
    pygame.draw.polygon(surf, _TUC_BEAK1, lower)
    pygame.draw.polygon(surf, _TUC_BEAK_D, upper, 1)
    pygame.draw.line(surf, _TUC_BEAK_D, (HCX + 6, by + 3), (HCX + 27, by + 5), 1)
    pygame.draw.line(surf, (255, 230, 150), (HCX + 8, by - 3),
                     (HCX + 26, by - 1), 1)

    _rot_blit(surf, _tuc_wing(wing_angle_deg), (BCX - 4, BCY))
    for fx in (29, 36):
        pygame.draw.line(surf, _TUC_BEAK1, (fx, BCY + 14), (fx, BCY + 18), 2)
    return surf


get_toucan = _make_prebuilt_skin(build_toucan)


# ═════════════════════════════════════════════════════════════════════════════
# 3 · PENGUIN (Adélie) — glossy blue-black tuxedo body with the signature white
#     eye-rings and an orange beak. Signature 40px read: the dark-back/white-
#     front split + the two white eye-rings + the orange beak/feet pop. The
#     3-layer body + gloss sheen + AO chin shadow keep it premium at hero scale.
# ═════════════════════════════════════════════════════════════════════════════
_PEN_BACK    = (27, 36, 54)         # glossy blue-black
_PEN_BACK_D  = (15, 22, 38)         # deep shadow rim
_PEN_BACK_H  = (70, 85, 122)        # cool blue backlight / flipper edge
_PEN_SHEEN   = (150, 168, 210)      # soft blue gloss overlay
_PEN_BELLY   = (246, 247, 251)      # off-white belly
_PEN_BELLY_D = (208, 214, 226)      # belly undershadow
_PEN_BELLY_H = (255, 255, 255)      # belly top sheen
_PEN_RING    = (238, 240, 248)      # white eye-ring
_PEN_BEAK    = (210, 120, 50)       # warm orange beak (the one warm anchor)
_PEN_BEAK_D  = (168, 88, 28)        # lower-mandible shadow / outline
_PEN_BEAK_H  = (240, 168, 88)       # warm beak top highlight
_PEN_FOOT    = (255, 154, 60)       # foot orange
_PEN_FOOT_D  = (200, 110, 32)       # foot shadow / outline


def _pen_flipper(angle_deg):
    """Blue-black flipper with a cool leading-edge highlight (penguins flap
    flippers, not feathered wings); same angle*0.7 damping as the body flap."""
    w = pygame.Surface((34, 42), pygame.SRCALPHA)
    pts = [(18, 9), (27, 16), (22, 35), (13, 30)]
    pygame.draw.polygon(w, _PEN_BACK_D, pts)
    pygame.draw.polygon(w, _PEN_BACK, [(18, 11), (25, 17), (20, 31), (15, 27)])
    pygame.draw.line(w, _PEN_BACK_H, (18, 12), (24, 18), 1)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def build_penguin(wing_angle_deg):
    surf = _new()

    # Stubby tail — outer point kept near the body so it stays attached at flap
    # angles rather than reading as a detached spike.
    pygame.draw.polygon(surf, _PEN_BACK_D,
                        [(14, BCY + 7), (7, BCY + 13), (18, BCY + 13)])
    pygame.draw.polygon(surf, _PEN_BACK,
                        [(15, BCY + 8), (10, BCY + 12), (18, BCY + 12)])

    # 3-layer glossy blue-black egg + a cool backlight up onto the back.
    _aaellipse(surf, _PEN_BACK_D, (BCX + 1, BCY + 1), 18, 18)
    _aaellipse(surf, _PEN_BACK,   (BCX,     BCY),     17, 17)
    _aaellipse(surf, _PEN_BACK_H, (BCX - 7, BCY - 8),  5,  4)

    # Gloss-sheen overlay top-left so the back reads wet and rounded.
    sheen = pygame.Surface((22, 9), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (*_PEN_SHEEN, 110), sheen.get_rect())
    surf.blit(sheen, (BCX - 15, BCY - 14))

    # Far flipper behind.
    _rot_blit(surf, _pen_flipper(wing_angle_deg * 0.5 - 16), (BCX + 12, BCY))

    # White belly: oval + upper sheen + lower undershadow for chest volume.
    _aaellipse(surf, _PEN_BELLY,   (BCX + 1, BCY + 3), 12, 14)
    _aaellipse(surf, _PEN_BELLY_H, (BCX,     BCY - 2),  8,  6)
    _aaellipse(surf, _PEN_BELLY_D, (BCX + 1, BCY + 10), 9,  5)

    # Head dome (3-layer), merging into the body with a little neck.
    _aaellipse(surf, _PEN_BACK_D, (HCX,     HCY + 2), 12, 12)
    _aaellipse(surf, _PEN_BACK,   (HCX - 1, HCY + 1), 11, 11)
    _aaellipse(surf, _PEN_BACK_H, (HCX - 4, HCY - 3),  4,  4)

    # AO shadow under the chin where the head meets the white belly.
    sh = pygame.Surface((20, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (12, 16, 28, 90), sh.get_rect())
    surf.blit(sh, (HCX - 12, HCY + 8))

    # Two separate white eye-rings (a rim, not a white mask) with a dark gap
    # between — the Adélie tell; big r4 irises read at 40px.
    for ex in (HCX - 3, HCX + 8):
        pygame.draw.circle(surf, _PEN_RING, (ex, HCY), 5)
    _eye(surf, HCX - 3, HCY, 4, iris=(18, 16, 22))
    _eye(surf, HCX + 8, HCY, 4, iris=(18, 16, 22))

    # Short orange beak (banded + highlight), seated below the eye-line so it
    # never collides with the rings.
    beak = [(HCX + 3, HCY + 5), (HCX + 12, HCY + 7), (HCX + 3, HCY + 10)]
    pygame.draw.polygon(surf, _PEN_BEAK, beak)
    pygame.draw.polygon(surf, _PEN_BEAK_D,
                        [(HCX + 3, HCY + 8), (HCX + 12, HCY + 7),
                         (HCX + 3, HCY + 10)])
    pygame.draw.polygon(surf, _PEN_BEAK_D, beak, 1)
    pygame.draw.line(surf, _PEN_BEAK_H, (HCX + 4, HCY + 6), (HCX + 10, HCY + 7), 1)

    # Near flipper — lifted so its dark edge doesn't gash the white belly sheen.
    _rot_blit(surf, _pen_flipper(wing_angle_deg), (BCX - 7, BCY - 2))

    # Orange webbed feet with a toe split + outline.
    for fx in (27, 38):
        foot = [(fx - 3, BCY + 16), (fx + 4, BCY + 16),
                (fx + 5, BCY + 20), (fx - 4, BCY + 20)]
        pygame.draw.polygon(surf, _PEN_FOOT, foot)
        pygame.draw.polygon(surf, _PEN_FOOT_D, foot, 1)
        pygame.draw.line(surf, _PEN_FOOT_D, (fx + 1, BCY + 20), (fx + 1, BCY + 18), 1)
    return surf


get_penguin = _make_prebuilt_skin(build_penguin)


# ═════════════════════════════════════════════════════════════════════════════
# 4 · BAT — purple fuzzy body, two big leathery membrane wings that flap wide,
#     two pointed ears, cute fangs. Signature 40px read: the scalloped
#     membrane wing-span + the pointed ears. Spooky-cute.
# ═════════════════════════════════════════════════════════════════════════════
_BAT_BODY   = (104, 80, 150)
_BAT_BODY_D = (70, 50, 110)
_BAT_BODY_H = (150, 124, 200)
_BAT_MEMB   = (84, 60, 128)
_BAT_MEMB_D = (54, 38, 92)
_BAT_MEMB_H = (132, 106, 184)
_BAT_EAR    = (88, 64, 132)
_BAT_FANG   = (250, 250, 245)


def _bat_wing(angle_deg, sgn, scale=1.0):
    """Leathery scalloped membrane wing on 3 finger-struts. `scale` shrinks
    the near wing so it never crowds the face on the level frame."""
    w = pygame.Surface((52, 44), pygame.SRCALPHA)
    # Membrane with scalloped trailing edge.
    memb = [(8, 22), (24, 10), (40, 8), (50, 18), (44, 24),
            (50, 30), (40, 32), (44, 38), (30, 34), (20, 38), (8, 28)]
    pygame.draw.polygon(w, _BAT_MEMB_D, memb)
    pygame.draw.polygon(w, _BAT_MEMB,
                        [(9, 22), (24, 12), (40, 10), (47, 18),
                         (38, 30), (22, 34), (10, 27)])
    # Finger struts.
    for tx, ty in ((40, 8), (50, 18), (44, 38)):
        pygame.draw.line(w, _BAT_MEMB_D, (10, 24), (tx, ty), 2)
    pygame.draw.line(w, _BAT_MEMB_H, (11, 22), (38, 11), 1)
    if scale != 1.0:
        sz = (max(1, int(52 * scale)), max(1, int(44 * scale)))
        w = pygame.transform.smoothscale(w, sz)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_bat(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)            # 1 = wings up
    spread = (f - 0.5) * 26              # wings swing symmetrically

    # Far wing (behind body), flapped opposite the lift sense for depth.
    _rot_blit(surf, _bat_wing(20 + spread, +1), (BCX + 16, BCY - 4))

    # Small fuzzy body.
    _aaellipse(surf, _BAT_BODY_D, (BCX + 1, BCY + 1), 13, 14)
    _aaellipse(surf, _BAT_BODY, (BCX, BCY), 12, 13)
    _aaellipse(surf, _BAT_BODY_H, (BCX - 2, BCY - 3), 7, 6)
    # Fur tufts on the chest.
    for tx in (28, 32, 36):
        pygame.draw.line(surf, _BAT_BODY_D, (tx, BCY + 8), (tx, BCY + 12), 1)

    # Head with two big pointed ears.
    _aaellipse(surf, _BAT_BODY_D, (HCX, HCY + 1), 10, 10)
    _aaellipse(surf, _BAT_BODY, (HCX - 1, HCY), 9, 9)
    for sgn, ex in ((-1, HCX - 6), (1, HCX + 6)):
        pygame.draw.polygon(surf, _BAT_BODY_D,
                            [(ex - 3, CROWN_Y + 6), (ex + sgn * 2, CROWN_Y - 6),
                             (ex + 4, CROWN_Y + 6)])
        pygame.draw.polygon(surf, _BAT_EAR,
                            [(ex - 1, CROWN_Y + 5), (ex + sgn * 1, CROWN_Y - 3),
                             (ex + 3, CROWN_Y + 5)])
    # Big friendly eyes + tiny fangs.
    _eye(surf, HCX - 3, HCY, 4)
    _eye(surf, HCX + 4, HCY, 4)
    pygame.draw.polygon(surf, _BAT_FANG,
                        [(HCX - 2, HCY + 6), (HCX, HCY + 6), (HCX - 1, HCY + 9)])
    pygame.draw.polygon(surf, _BAT_FANG,
                        [(HCX + 2, HCY + 6), (HCX + 4, HCY + 6),
                         (HCX + 3, HCY + 9)])

    # Near wing (over body) — the hero span. Anchor lowered ~4px and the
    # surface shrunk ~15% so both eyes + both ears stay fully clear on the
    # level frame in every pose, matching the already-clean dive frame.
    _rot_blit(surf, _bat_wing(-10 - spread, -1, scale=0.85), (BCX - 14, BCY + 2))
    return surf


get_bat = _make_prebuilt_skin(build_bat)


# ═════════════════════════════════════════════════════════════════════════════
# 5 · FLAMINGO — hot-pink body, the iconic S-curve neck rising tall, long thin
#     legs, black-tipped down-hooked beak. Signature 40px read: the bright-pink
#     S-neck silhouette + the bent beak. Elegant + unmistakable colour.
# ═════════════════════════════════════════════════════════════════════════════
_FLA_BODY   = (255, 120, 158)
_FLA_BODY_D = (224, 84, 128)
_FLA_BODY_H = (255, 178, 200)
_FLA_NECK   = (255, 134, 170)
_FLA_LEG    = (236, 96, 130)
_FLA_BEAK   = (250, 214, 120)
_FLA_BEAK_T = (32, 30, 40)          # black tip


def _fla_wing(angle_deg):
    w = pygame.Surface((42, 40), pygame.SRCALPHA)
    pts = [(20, 20), (38, 14), (38, 28), (22, 34), (12, 28)]
    pygame.draw.polygon(w, _FLA_BODY_D, pts)
    pygame.draw.polygon(w, _FLA_BODY, [(20, 20), (36, 16), (35, 26), (20, 30)])
    pygame.draw.polygon(w, _FLA_BODY_H, [(30, 16), (38, 18), (36, 24)])
    pygame.draw.line(w, _FLA_BODY_H, (21, 21), (35, 17), 1)
    return pygame.transform.rotate(w, angle_deg)


def build_flamingo(wing_angle_deg):
    surf = _new()
    # Upswept tail plumes growing from a solid rump lobe rooted UNDER the body
    # (x~16-19) so the tail reads as attached, not a detached shard. Drawn first
    # so the body overlaps its base.
    _aaellipse(surf, _FLA_BODY_D, (19, BCY + 4), 9, 7)
    _aaellipse(surf, _FLA_BODY,   (18, BCY + 3), 8, 6)
    _aaellipse(surf, _FLA_BODY_H, (16, BCY + 1), 3, 2)
    for (rx, ry, mx, my, tx, ty) in (
        (16, BCY - 1, 10, BCY - 4, 5, BCY - 4),
        (17, BCY + 1, 10, BCY - 1, 4, BCY),
        (18, BCY + 3, 11, BCY + 2, 5, BCY + 3),
    ):
        pygame.draw.lines(surf, _FLA_BODY_D, False,
                          [(rx, ry), (mx, my), (tx, ty)], 3)
        pygame.draw.line(surf, _FLA_BODY_H, (rx, ry), (mx, my), 1)
    # Rounded body, sitting a touch lower so the neck has room.
    _aaellipse(surf, _FLA_BODY_D, (BCX + 1, BCY + 3), 16, 13)
    _aaellipse(surf, _FLA_BODY, (BCX, BCY + 2), 15, 12)
    _aaellipse(surf, _FLA_BODY_H, (BCX - 3, BCY - 1), 8, 5)

    _rot_blit(surf, _fla_wing(wing_angle_deg * 0.5 - 14), (BCX + 7, BCY - 1))

    # ── HERO: the S-curve neck sweeping up then forward ──
    neck = [(BCX + 8, BCY - 2), (BCX + 14, BCY - 12),
            (HCX - 2, CROWN_Y - 2), (HCX + 2, CROWN_Y - 4)]
    # Draw as a thick poly-line spine.
    spine = [(BCX + 9, BCY - 1), (BCX + 13, BCY - 10),
             (BCX + 12, CROWN_Y + 4), (HCX - 4, CROWN_Y),
             (HCX, CROWN_Y - 3)]
    pygame.draw.lines(surf, _FLA_NECK, False, spine, 6)
    pygame.draw.lines(surf, _FLA_BODY_H, False, spine[:3], 1)

    # Small head at the top of the S.
    hx, hy = HCX, CROWN_Y - 3
    _aaellipse(surf, _FLA_BODY, (hx, hy), 7, 6)
    _aaellipse(surf, _FLA_BODY_H, (hx - 2, hy - 1), 3, 2)
    _eye(surf, hx + 1, hy - 1, 3)
    # Down-hooked beak: yellow base, black tip.
    pygame.draw.polygon(surf, _FLA_BEAK,
                        [(hx + 4, hy - 1), (hx + 12, hy + 2),
                         (hx + 11, hy + 5), (hx + 4, hy + 3)])
    pygame.draw.polygon(surf, _FLA_BEAK_T,
                        [(hx + 10, hy + 2), (hx + 13, hy + 4),
                         (hx + 10, hy + 6)])
    pygame.draw.polygon(surf, _FLA_BODY_D,
                        [(hx + 4, hy - 1), (hx + 12, hy + 2),
                         (hx + 11, hy + 5), (hx + 4, hy + 3)], 1)

    # Near wing over body.
    _rot_blit(surf, _fla_wing(wing_angle_deg), (BCX - 3, BCY))
    # Long thin legs (one folded forward, flamingo style).
    f = _flap(wing_angle_deg)
    kx = BCX + int(2 + f * 3)
    pygame.draw.lines(surf, _FLA_LEG, False,
                      [(BCX + 2, BCY + 12), (kx, BCY + 19),
                       (kx + 5, BCY + 16)], 2)
    pygame.draw.line(surf, _FLA_LEG, (BCX + 6, BCY + 12),
                     (BCX + 7, BCY + 20), 2)
    return surf


get_flamingo = _make_prebuilt_skin(build_flamingo)


# ═════════════════════════════════════════════════════════════════════════════
# 6 · BALD EAGLE — dark-brown body, bold WHITE head, fierce hooked YELLOW
#     beak + brow. Signature 40px read: the white-head / dark-body two-tone +
#     the big yellow hooked beak. Proud + iconic.
# ═════════════════════════════════════════════════════════════════════════════
_EAG_BODY   = (78, 56, 38)
_EAG_BODY_D = (52, 36, 24)
_EAG_BODY_H = (120, 92, 60)
_EAG_HEAD   = (248, 248, 244)
_EAG_HEAD_D = (208, 210, 214)
_EAG_BEAK   = (255, 198, 56)
_EAG_BEAK_D = (200, 142, 24)
_EAG_BROW   = (150, 110, 40)


def _eag_wing(angle_deg):
    w = pygame.Surface((48, 44), pygame.SRCALPHA)
    pts = [(22, 22), (44, 12), (46, 24), (28, 36), (14, 30)]
    pygame.draw.polygon(w, _EAG_BODY_D, pts)
    pygame.draw.polygon(w, _EAG_BODY, [(22, 22), (42, 14), (42, 26), (24, 32)])
    # Splayed primary feather tips.
    for tx, ty in ((42, 14), (45, 19), (44, 25)):
        pygame.draw.polygon(w, _EAG_BODY_D,
                            [(tx - 4, ty), (tx + 3, ty - 1), (tx - 2, ty + 4)])
    pygame.draw.line(w, _EAG_BODY_H, (23, 23), (40, 16), 1)
    pygame.draw.line(w, _EAG_BODY_H, (24, 28), (38, 23), 1)
    return pygame.transform.rotate(w, angle_deg)


def build_eagle(wing_angle_deg):
    surf = _new()
    # White fanned tail.
    pygame.draw.polygon(surf, _EAG_HEAD_D,
                        [(12, BCY - 4), (2, BCY + 6), (16, BCY + 10)])
    pygame.draw.polygon(surf, _EAG_HEAD,
                        [(13, BCY - 2), (5, BCY + 5), (16, BCY + 8)])
    # Dark-brown body.
    _aaellipse(surf, _EAG_BODY_D, (BCX + 1, BCY + 1), 18, 16)
    _aaellipse(surf, _EAG_BODY, (BCX, BCY), 17, 15)
    _aaellipse(surf, _EAG_BODY_H, (BCX - 3, BCY - 3), 8, 6)
    # Feather flecks.
    for fx, fy in ((30, 44), (35, 48), (27, 50)):
        pygame.draw.line(surf, _EAG_BODY_D, (fx, fy), (fx, fy + 3), 1)

    _rot_blit(surf, _eag_wing(wing_angle_deg * 0.5 - 16), (BCX + 9, BCY - 2))

    # ── HERO: bold WHITE head ──
    _aaellipse(surf, _EAG_HEAD_D, (HCX, HCY + 1), 12, 12)
    _aaellipse(surf, _EAG_HEAD, (HCX - 1, HCY), 11, 11)
    # Fierce angled brow.
    pygame.draw.polygon(surf, _EAG_BROW,
                        [(HCX - 6, HCY - 4), (HCX + 6, HCY - 6),
                         (HCX + 6, HCY - 3), (HCX - 5, HCY - 1)])
    # Stern eye under the brow.
    pygame.draw.circle(surf, (255, 220, 120), (HCX + 2, HCY - 1), 4)
    pygame.draw.circle(surf, (24, 22, 18), (HCX + 3, HCY - 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (HCX + 1, HCY - 2), 1)

    # Big hooked yellow beak.
    pygame.draw.polygon(surf, _EAG_BEAK,
                        [(HCX + 4, HCY - 2), (HCX + 16, HCY + 1),
                         (HCX + 14, HCY + 6), (HCX + 4, HCY + 5)])
    # Down-hook.
    pygame.draw.polygon(surf, _EAG_BEAK_D,
                        [(HCX + 13, HCY + 3), (HCX + 16, HCY + 1),
                         (HCX + 13, HCY + 8)])
    pygame.draw.polygon(surf, _EAG_BEAK_D,
                        [(HCX + 4, HCY - 2), (HCX + 16, HCY + 1),
                         (HCX + 14, HCY + 6), (HCX + 4, HCY + 5)], 1)
    pygame.draw.line(surf, (255, 235, 160), (HCX + 5, HCY), (HCX + 13, HCY + 2), 1)

    _rot_blit(surf, _eag_wing(wing_angle_deg), (BCX - 5, BCY))
    # Talons.
    for fx in (28, 37):
        pygame.draw.line(surf, _EAG_BEAK, (fx, BCY + 14), (fx, BCY + 18), 2)
        pygame.draw.circle(surf, _EAG_BEAK_D, (fx, BCY + 18), 1)
    return surf


get_eagle = _make_prebuilt_skin(build_eagle)


# ═════════════════════════════════════════════════════════════════════════════
# 7 · BEE — tiny gold-and-black striped body, transparent buzzing wings (small
#     motion), big eyes, little stinger. Signature 40px read: the bold black/
#     yellow stripes + the round chubby body. The flap is a small fast buzz.
# ═════════════════════════════════════════════════════════════════════════════
_BEE_GOLD   = (255, 198, 44)
_BEE_GOLD_D = (220, 158, 20)
_BEE_GOLD_H = (255, 226, 120)
_BEE_STRIPE = (40, 36, 44)
_BEE_WING   = (210, 234, 255)
_BEE_WING_E = (150, 190, 230)


def _bee_wing(angle_deg):
    """Translucent oval wing — bee buzz is a SMALL motion, so the angle is
    damped hard."""
    w = pygame.Surface((30, 22), pygame.SRCALPHA)
    pygame.draw.ellipse(w, (*_BEE_WING, 150), (2, 4, 26, 14))
    pygame.draw.ellipse(w, (*_BEE_WING_E, 220), (2, 4, 26, 14), 1)
    pygame.draw.line(w, (*_BEE_WING_E, 180), (6, 11), (24, 9), 1)
    return pygame.transform.rotate(w, angle_deg * 0.25)   # damped buzz


def build_bee(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    # Wings buzz above the body, small flutter.
    buzz = (f - 0.5) * 10
    _rot_blit(surf, _bee_wing(30 + buzz), (BCX + 4, BCY - 12))
    _rot_blit(surf, pygame.transform.flip(_bee_wing(30 - buzz), True, False),
              (BCX - 4, BCY - 12))

    # Chubby round striped body.
    _aaellipse(surf, _BEE_GOLD_D, (BCX + 1, BCY + 1), 16, 14)
    _aaellipse(surf, _BEE_GOLD, (BCX, BCY), 15, 13)
    _aaellipse(surf, _BEE_GOLD_H, (BCX - 3, BCY - 3), 7, 4)
    # Bold black stripes wrapping the abdomen.
    for sx in (BCX - 4, BCX + 4, BCX + 12):
        pygame.draw.ellipse(surf, _BEE_STRIPE, (sx - 3, BCY - 13, 6, 26))
    # Clamp stripes to the body via a re-draw of the body rim.
    pygame.draw.ellipse(surf, _BEE_GOLD_D, (BCX - 15, BCY - 13, 30, 26), 1)
    # Stinger.
    pygame.draw.polygon(surf, _BEE_STRIPE,
                        [(BCX - 14, BCY), (BCX - 21, BCY - 2),
                         (BCX - 21, BCY + 2)])

    # Head with big eyes + tiny antennae.
    _aaellipse(surf, _BEE_STRIPE, (HCX + 4, HCY), 9, 9)
    _eye(surf, HCX + 2, HCY - 1, 4, white=(245, 245, 250))
    _eye(surf, HCX + 8, HCY - 1, 4, white=(245, 245, 250))
    # Smile.
    pygame.draw.arc(surf, (255, 220, 150),
                    (HCX, HCY + 1, 10, 8), math.radians(200),
                    math.radians(340), 2)
    # Antennae bobbing with the buzz.
    for sgn, ax in ((-1, HCX + 1), (1, HCX + 7)):
        pygame.draw.line(surf, _BEE_STRIPE, (ax, CROWN_Y + 6),
                         (ax + sgn * 2, CROWN_Y - 2 + int(buzz * 0.3)), 1)
        pygame.draw.circle(surf, _BEE_GOLD,
                           (ax + sgn * 2, CROWN_Y - 2 + int(buzz * 0.3)), 2)
    return surf


get_bee = _make_prebuilt_skin(build_bee)


# ═════════════════════════════════════════════════════════════════════════════
# 8 · DRAGON (premium gacha showpiece) — a COMPACT, cute bird-scale dragon:
#     emerald scaled body, a snouted horned head, bat-style membrane wings,
#     a spiked tail, and a tiny ember at the nostril. Signature 40px read: the
#     horned snout + scalloped wing + spiky tail ridge. Rare-feeling jewel tones.
# ═════════════════════════════════════════════════════════════════════════════
_DRG_BODY   = (64, 186, 120)
_DRG_BODY_D = (34, 140, 86)
_DRG_BODY_H = (140, 230, 170)
_DRG_BELLY  = (224, 240, 170)       # pale gold underscale
_DRG_WING   = (52, 150, 130)
_DRG_WING_D = (30, 108, 96)
_DRG_WING_H = (120, 210, 190)
_DRG_HORN   = (240, 232, 200)
_DRG_SPIKE  = (255, 214, 90)
_DRG_EMBER  = (255, 130, 50)


def _drg_wing(angle_deg, sgn, scale=1.0):
    """Membrane wing on dragon finger-struts, jewel-teal. `scale` shrinks
    the near wing so it reads as supporting mass behind the horned head."""
    w = pygame.Surface((50, 44), pygame.SRCALPHA)
    memb = [(8, 22), (26, 8), (42, 6), (48, 16), (40, 22),
            (48, 28), (36, 30), (42, 38), (26, 32), (10, 30)]
    pygame.draw.polygon(w, _DRG_WING_D, memb)
    pygame.draw.polygon(w, _DRG_WING,
                        [(9, 22), (26, 10), (42, 8), (45, 16),
                         (34, 26), (20, 30), (11, 27)])
    # Struts kept off the topmost membrane point so the rotated-open near
    # wing doesn't throw a thin dark spike up next to the horn silhouette.
    for tx, ty in ((40, 10), (48, 16), (42, 38)):
        pygame.draw.line(w, _DRG_WING_D, (10, 24), (tx, ty), 2)
    pygame.draw.line(w, _DRG_WING_H, (11, 22), (40, 11), 1)
    if scale != 1.0:
        sz = (max(1, int(50 * scale)), max(1, int(44 * scale)))
        w = pygame.transform.smoothscale(w, sz)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_dragon(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = (f - 0.5) * 24

    # Far wing behind.
    _rot_blit(surf, _drg_wing(24 + spread, +1), (BCX + 16, BCY - 6))

    # Spiked tail curling out behind, with a gold arrow tip.
    tail = [(BCX - 6, BCY + 2), (12, BCY - 4), (4, BCY + 6), (14, BCY + 8)]
    pygame.draw.polygon(surf, _DRG_BODY_D, tail)
    pygame.draw.polygon(surf, _DRG_BODY,
                        [(BCX - 6, BCY + 2), (12, BCY - 2), (8, BCY + 5)])
    pygame.draw.polygon(surf, _DRG_SPIKE,
                        [(2, BCY + 1), (9, BCY + 3), (3, BCY + 8)])

    # Compact scaled body.
    _aaellipse(surf, _DRG_BODY_D, (BCX + 1, BCY + 1), 15, 15)
    _aaellipse(surf, _DRG_BODY, (BCX, BCY), 14, 14)
    # Pale belly plates.
    _aaellipse(surf, _DRG_BELLY, (BCX - 1, BCY + 5), 9, 8)
    for by in (BCY + 1, BCY + 5, BCY + 9):
        pygame.draw.line(surf, _DRG_BODY_D, (BCX - 7, by), (BCX + 5, by), 1)
    # Scale speckles.
    for sx, sy in ((30, 38), (36, 42), (28, 44), (34, 36)):
        pygame.draw.circle(surf, _DRG_BODY_H, (sx, sy), 1)

    # Dorsal spike ridge up the back.
    for i, sy in enumerate((BCY + 6, BCY, BCY - 6)):
        h = 4 + i
        pygame.draw.polygon(surf, _DRG_SPIKE,
                            [(BCX - 12 + i * 2, sy), (BCX - 12 + i * 2, sy - h),
                             (BCX - 8 + i * 2, sy)])

    # Snouted horned head.
    _aaellipse(surf, _DRG_BODY_D, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, _DRG_BODY, (HCX - 1, HCY), 10, 9)
    _aaellipse(surf, _DRG_BODY_H, (HCX - 3, HCY - 3), 5, 3)
    # Two back-swept horns — taller (to CROWN_Y-10/-11) so the horned crown
    # always breaks ABOVE the near wing across all four flap poses. The horn
    # is the cheapest "dragon" signal at gameplay size, so it owns the top.
    for sgn, hx in ((-1, HCX - 5), (1, HCX + 4)):
        pygame.draw.polygon(surf, _DRG_BODY_D,
                            [(hx - 1, CROWN_Y + 6),
                             (hx - sgn * 3, CROWN_Y - 11),
                             (hx + 4, CROWN_Y + 5)])
        pygame.draw.polygon(surf, _DRG_HORN,
                            [(hx, CROWN_Y + 6),
                             (hx - sgn * 3, CROWN_Y - 10),
                             (hx + 3, CROWN_Y + 5)])
        # Bright tip glint so the horn point survives the downscale.
        pygame.draw.circle(surf, (255, 250, 230),
                           (hx - sgn * 3, CROWN_Y - 9), 1)
    # Snout — a BOLD, longer forward wedge (chunky, not a thin quad) with the
    # ember at the very tip, set just clear of the body ellipse so the read
    # order is horns → snout → tail spikes.
    snout = [(HCX + 3, HCY - 4), (HCX + 17, HCY - 1),
             (HCX + 17, HCY + 4), (HCX + 3, HCY + 6)]
    pygame.draw.polygon(surf, _DRG_BODY, snout)
    pygame.draw.polygon(surf, _DRG_BODY_H,
                        [(HCX + 4, HCY - 3), (HCX + 15, HCY - 1),
                         (HCX + 9, HCY + 1)])
    pygame.draw.polygon(surf, _DRG_BODY_D, snout, 1)
    # Nostril notch + glowing ember at the very tip, separated from the body.
    pygame.draw.circle(surf, _DRG_BODY_D, (HCX + 13, HCY - 1), 1)
    pygame.draw.circle(surf, (255, 90, 30), (HCX + 17, HCY + 1), 3)
    pygame.draw.circle(surf, _DRG_EMBER, (HCX + 17, HCY + 1), 2)
    pygame.draw.circle(surf, (255, 230, 140), (HCX + 17, HCY), 1)
    # Slit-pupil reptile eye.
    pygame.draw.circle(surf, (255, 220, 90), (HCX, HCY - 1), 4)
    pygame.draw.ellipse(surf, (30, 40, 30), (HCX - 1, HCY - 4, 2, 6))
    pygame.draw.circle(surf, (255, 255, 255), (HCX - 1, HCY - 2), 1)

    # Near wing — shrunk ~20% and rotated more OPEN (less horizontal) so it
    # sits as supporting mass BEHIND the spiky head/tail silhouette instead
    # of lying flat across the snout + dorsal ridge.
    _rot_blit(surf, _drg_wing(-40 - spread, -1, scale=0.8), (BCX - 11, BCY + 1))

    # Clawed feet.
    for fx in (29, 37):
        pygame.draw.line(surf, _DRG_BODY_D, (fx, BCY + 13), (fx, BCY + 17), 2)
        pygame.draw.circle(surf, _DRG_HORN, (fx, BCY + 17), 1)
    return surf


get_dragon = _make_prebuilt_skin(build_dragon)


# ═════════════════════════════════════════════════════════════════════════════
# 9 · PHOENIX (premium gacha showpiece) — a blazing firebird: molten red-orange
#     body, swept-back flame plumes for a crest and tail, gold wings with
#     ember tips, a glowing inner heat. Signature 40px read: the upswept FLAME
#     crest + the fiery red→gold gradient. The rarest, most premium look.
# ═════════════════════════════════════════════════════════════════════════════
_PHX_CORE   = (255, 226, 120)       # white-hot core
_PHX_BODY   = (255, 138, 40)
_PHX_BODY_D = (224, 78, 30)
_PHX_DEEP   = (180, 40, 36)
_PHX_GOLD   = (255, 200, 70)
_PHX_FLAME1 = (255, 92, 40)
_PHX_FLAME2 = (255, 170, 50)
_PHX_FLAME3 = (255, 230, 130)


def _phx_wing(angle_deg):
    """Flame-feathered wing: deep-red base, orange mid, gold flaming tips."""
    w = pygame.Surface((50, 46), pygame.SRCALPHA)
    base = [(22, 24), (44, 10), (48, 22), (30, 38), (14, 32)]
    pygame.draw.polygon(w, _PHX_DEEP, base)
    pygame.draw.polygon(w, _PHX_BODY, [(22, 24), (42, 13), (44, 22), (24, 34)])
    pygame.draw.polygon(w, _PHX_FLAME2, [(22, 24), (40, 16), (40, 22), (26, 30)])
    # Flaming primary tips licking up off the wing.
    for tx, ty in ((42, 12), (46, 17), (44, 23)):
        pygame.draw.polygon(w, _PHX_FLAME1,
                            [(tx - 4, ty + 2), (tx + 2, ty - 5), (tx + 1, ty + 4)])
        pygame.draw.polygon(w, _PHX_FLAME3,
                            [(tx - 1, ty + 1), (tx + 1, ty - 4), (tx + 1, ty + 2)])
    pygame.draw.line(w, _PHX_FLAME3, (23, 25), (40, 16), 1)
    return pygame.transform.rotate(w, angle_deg)


def build_phoenix(wing_angle_deg):
    surf = _new()
    # ── Upswept FLAME tail-plumes (the long firebird tail) ──
    for col, dx, dy, ln in ((_PHX_DEEP, 0, 0, 0), (_PHX_FLAME1, 1, -1, 1),
                            (_PHX_FLAME2, 2, -2, 2)):
        pygame.draw.polygon(surf, col, [
            (14 - dx, BCY + 2), (2 - dx, BCY - 8 - ln),
            (6 - dx, BCY + 2 + dy), (1 - dx, BCY + 10),
            (10 - dx, BCY + 6)])
    pygame.draw.polygon(surf, _PHX_FLAME3,
                        [(12, BCY), (5, BCY - 6), (8, BCY + 2)])

    _rot_blit(surf, _phx_wing(wing_angle_deg * 0.5 - 14), (BCX + 8, BCY - 4))

    # Molten body with a hot inner core.
    _aaellipse(surf, _PHX_DEEP, (BCX + 1, BCY + 2), 16, 15)
    _aaellipse(surf, _PHX_BODY, (BCX, BCY), 15, 14)
    _aaellipse(surf, _PHX_GOLD, (BCX - 2, BCY + 2), 9, 9)
    _aaellipse(surf, _PHX_CORE, (BCX - 3, BCY), 5, 5)

    # Head.
    _aaellipse(surf, _PHX_BODY_D, (HCX, HCY + 1), 10, 10)
    _aaellipse(surf, _PHX_BODY, (HCX - 1, HCY), 9, 9)
    _aaellipse(surf, _PHX_GOLD, (HCX - 2, HCY + 1), 5, 5)

    # ── HERO: upswept flame crest breaking high above the crown ──
    # FAT rounded flame tongues (wide base, rounded shoulders, fewer thin
    # tips) so a clear flame shape survives the 40px downscale where the old
    # thin single-poly slivers vanished. Three overlapping tongues, back to
    # front, each a deep base flank + a bright inner lick.
    def _tongue(col, bx, base_w, tip_x, tip_y, bend):
        """One rounded flame tongue: a fat teardrop sweeping up + forward."""
        pygame.draw.polygon(surf, col, [
            (bx - base_w, HCY - 3),
            (bx - base_w + 1, CROWN_Y - 2 + bend),
            (tip_x - 2, tip_y + 2),
            (tip_x, tip_y),
            (tip_x + 1, tip_y + 3),
            (bx + base_w, CROWN_Y + bend),
            (bx + base_w, HCY - 3),
        ])
    # Back tongue (deep red), tallest, sweeping back.
    _tongue(_PHX_DEEP,  HCX - 4, 4, HCX - 7, CROWN_Y - 12, -1)
    # Mid tongue (orange), tallest centre lick.
    _tongue(_PHX_FLAME1, HCX,    5, HCX + 1, CROWN_Y - 16, 0)
    # Front tongue (gold), forward-swept.
    _tongue(_PHX_FLAME2, HCX + 4, 4, HCX + 9, CROWN_Y - 11, 1)
    # Bright inner heart so the flame glows hot at its core.
    pygame.draw.polygon(surf, _PHX_FLAME3, [
        (HCX - 2, HCY - 4), (HCX, CROWN_Y - 13),
        (HCX + 2, CROWN_Y - 13), (HCX + 3, HCY - 4)])
    pygame.draw.circle(surf, (255, 248, 210), (HCX + 1, CROWN_Y - 12), 2)

    # Bright eye + golden curved beak.
    _eye(surf, HCX, HCY - 1, 4, iris=(40, 22, 16))
    pygame.draw.polygon(surf, _PHX_GOLD,
                        [(HCX + 4, HCY - 1), (HCX + 13, HCY + 1),
                         (HCX + 11, HCY + 4), (HCX + 4, HCY + 4)])
    pygame.draw.polygon(surf, _PHX_DEEP,
                        [(HCX + 4, HCY - 1), (HCX + 13, HCY + 1),
                         (HCX + 11, HCY + 4), (HCX + 4, HCY + 4)], 1)
    pygame.draw.line(surf, _PHX_FLAME3, (HCX + 5, HCY), (HCX + 11, HCY + 1), 1)

    # Near wing — flaming hero.
    _rot_blit(surf, _phx_wing(wing_angle_deg), (BCX - 4, BCY))

    # Glowing talons.
    for fx in (29, 37):
        pygame.draw.line(surf, _PHX_GOLD, (fx, BCY + 14), (fx, BCY + 18), 2)
    return surf


get_phoenix = _make_prebuilt_skin(build_phoenix)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry (liftable into game/animal_skins.py).
# Keys mirror the planned "skin"-kind ids in game.store_catalog.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_owl":      get_owl,
    "skin_toucan":   get_toucan,
    "skin_penguin":  get_penguin,
    "skin_bat":      get_bat,
    "skin_flamingo": get_flamingo,
    "skin_eagle":    get_eagle,
    "skin_bee":      get_bee,
    "skin_dragon":   get_dragon,     # premium gacha showpiece
    "skin_phoenix":  get_phoenix,    # premium gacha showpiece
}


# The v5 creature wave (axolotl … kitsune) lives one-module-per-creature so each
# creature's private helpers and palette constants stay in their own namespace —
# concatenating them into this file would collide (shared names like RIM, FUR,
# _star, _strike). Merge only each module's canonical "skin_<id>" getter; their
# exploration alt-builds are intentionally left unregistered.
for _modname in (
    "animal_axolotl", "animal_pufferfish", "animal_chameleon",
    "animal_red_panda", "animal_sugar_glider", "animal_mantis_shrimp",
    "animal_griffin", "animal_thunderbird", "animal_cosmic_jelly",
    "animal_aurora_stag", "animal_kitsune",
    # Secret ultra-premium NON-creature flyers (masked as ??? in the store).
    "animal_paper_plane", "animal_jet_fighter", "animal_ufo", "animal_toaster",
    # Secret piñata flyers (papier-mâché objects — same masked ??? tier).
    "animal_pinata_burro", "animal_pinata_cactus", "animal_pinata_parrot",
    # Mystery SUN (rolls a random one of two sun designs at unlock).
    "animal_sun",
):
    _mod = __import__("game." + _modname, fromlist=["BUILDERS"])
    BUILDERS.update({k: v for k, v in _mod.BUILDERS.items()
                     if k.startswith("skin_")})
