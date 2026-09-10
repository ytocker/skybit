"""Basketball player skin — 4 team palettes chosen by the player at unlock.

Variants (index → team name):
  0 — THE LAKER    purple / gold
  1 — THE BULL     red / white
  2 — THE CELTIC   green / gold
  3 — THE WARRIOR  blue / gold
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game import store_data


# ── shared draw helpers ──────────────────────────────────────────────────────

def _draw_kit(surf, BCX, BCY,
              jersey, jersey_d, jersey_h,
              trim, trim_d,
              num_col, num_d, number,
              shoe, shoe_d, shoe_ac,
              band_accent=None):
    bm = band_accent if band_accent is not None else jersey

    # Save face before any jersey drawing so it can be restored on top.
    face_x = HX - 9
    face_y = CROWN_Y - 1
    face_w = min(surf.get_width() - face_x, 28)
    face_h = HY + 12 - face_y
    face_rect = pygame.Rect(face_x, face_y, face_w, face_h)
    face_backup = surf.subsurface(face_rect).copy()

    # Chest panel
    _poly(surf, jersey, [
        (BCX-13, BCY-4),  (BCX+13, BCY-4),
        (BCX+12, BCY+14), (BCX-12, BCY+14),
    ])
    _poly(surf, jersey_d, [
        (BCX-13, BCY-4),  (BCX-9,  BCY-4),
        (BCX-9,  BCY+14), (BCX-12, BCY+14),
    ])
    pygame.draw.line(surf, jersey_h, (BCX+9, BCY-3), (BCX+9, BCY+12), 2)

    # Left strap
    _poly(surf, jersey, [
        (BCX-12, BCY-4), (BCX-7, BCY-4),
        (BCX-5, BCY-12), (BCX-10, BCY-12),
    ])
    pygame.draw.line(surf, jersey_d, (BCX-12, BCY-4), (BCX-10, BCY-12), 1)
    # Right strap
    _poly(surf, jersey, [
        (BCX+7,  BCY-4), (BCX+12, BCY-4),
        (BCX+10, BCY-12), (BCX+5, BCY-12),
    ])
    pygame.draw.line(surf, jersey_h, (BCX+11, BCY-4), (BCX+9, BCY-12), 1)

    # Armhole shadow arcs
    pygame.draw.arc(surf, jersey_d, (BCX+3,  BCY-8, 12, 12), -0.9, 1.3, 2)
    pygame.draw.arc(surf, jersey_d, (BCX-15, BCY-8, 12, 12),  1.8, 4.0, 2)

    # U-neckline trim
    pygame.draw.lines(surf, trim, False,
                      [(BCX-5, BCY-12), (BCX-1, BCY-9),
                       (BCX+3, BCY-9),  (BCX+6, BCY-12)], 2)

    # Number — visible chest runs x=19..38; midpoint=28 = BCX-4
    _draw_number(surf, BCX - 4, BCY + 5, number, num_col, num_d)

    # Hem piping
    pygame.draw.line(surf, trim, (BCX-11, BCY+13), (BCX+11, BCY+13), 1)

    # Wristband
    wrx, wry = BCX + 12, BCY + 8
    pygame.draw.line(surf, trim_d, (wrx-3, wry+4), (wrx+5, wry-2), 6)
    pygame.draw.line(surf, trim,   (wrx-3, wry+4), (wrx+5, wry-2), 4)
    pygame.draw.line(surf, jersey, (wrx-2, wry+3), (wrx+4, wry-2), 1)

    # Shoes
    for fx in (26, 34):
        pygame.draw.rect(surf, shoe_d, (fx-4, HY+22, 9, 6), border_radius=2)
        pygame.draw.rect(surf, shoe,   (fx-4, HY+21, 9, 4), border_radius=2)
        pygame.draw.line(surf, shoe_ac, (fx-3, HY+23), (fx+4, HY+23), 1)
        pygame.draw.line(surf, shoe_d,  (fx-4, HY+27), (fx+5, HY+27), 2)
        pygame.draw.line(surf, trim,    (fx-3, HY+21), (fx+1, HY+21), 1)

    # Restore face on top of all jersey elements
    surf.blit(face_backup, face_rect.topleft)

    # Headband — drawn after face restore so it sits on the forehead
    by = CROWN_Y + 5
    pygame.draw.line(surf, trim_d, (HX-12, by+1), (HX+13, by),   7)
    pygame.draw.line(surf, trim,   (HX-12, by),   (HX+13, by-1), 5)
    pygame.draw.line(surf, bm,     (HX-11, by),   (HX+12, by-1), 2)
    pygame.draw.line(surf, trim,   (HX-10, by-2), (HX+5,  by-2), 1)
    pygame.draw.circle(surf, bm, (HX-12, by), 3)
    pygame.draw.line(surf, jersey_d, (HX-13, by+2), (HX-16, by+5), 2)


def _draw_number(surf, cx, cy, number, col, shadow):
    digits = number.strip()
    if len(digits) == 1:
        _draw_digit(surf, cx, cy, digits[0], col, shadow, scale=0.85)
    elif len(digits) == 2:
        _draw_digit(surf, cx-4, cy, digits[0], col, shadow, scale=0.75)
        _draw_digit(surf, cx+4, cy, digits[1], col, shadow, scale=0.75)


def _draw_digit(surf, cx, cy, d, col, shad, scale=1.0):
    w = int(5 * scale)
    h = int(8 * scale)
    t = max(2, int(3 * scale))

    def seg(x0, y0, x1, y1):
        pygame.draw.line(surf, shad, (cx+x0+1, cy+y0+1), (cx+x1+1, cy+y1+1), t)
        pygame.draw.line(surf, col,  (cx+x0,   cy+y0),   (cx+x1,   cy+y1),   t)

    if d == '0':
        seg(-w,-h,+w,-h); seg(+w,-h,+w,+h)
        seg(+w,+h,-w,+h); seg(-w,+h,-w,-h)
    elif d == '1':
        seg(-1,-h,-1,+h); seg(-w,-h,-1,-h)
    elif d == '2':
        seg(-w,-h,+w,-h); seg(+w,-h,+w, 0)
        seg(+w, 0,-w, 0); seg(-w, 0,-w,+h); seg(-w,+h,+w,+h)
    elif d == '3':
        seg(-w,-h,+w,-h); seg(+w,-h,+w,+h)
        seg(-w, 0,+w, 0); seg(-w,+h,+w,+h)
    elif d == '4':
        seg(-w,-h,-w, 0); seg(-w, 0,+w, 0); seg(+w,-h,+w,+h)
    elif d == '5':
        seg(+w,-h,-w,-h); seg(-w,-h,-w, 0)
        seg(-w, 0,+w, 0); seg(+w, 0,+w,+h); seg(+w,+h,-w,+h)
    elif d == '6':
        seg(+w,-h,-w,-h); seg(-w,-h,-w,+h)
        seg(-w, 0,+w, 0); seg(+w, 0,+w,+h); seg(+w,+h,-w,+h)
    elif d == '7':
        seg(-w,-h,+w,-h); seg(+w,-h,-w,+h)
    elif d == '8':
        seg(-w,-h,+w,-h); seg(+w,-h,+w,+h)
        seg(-w, 0,+w, 0); seg(-w,+h,+w,+h); seg(-w,-h,-w,+h)
    elif d == '9':
        seg(-w,-h,+w,-h); seg(+w,-h,+w,+h)
        seg(-w, 0,+w, 0); seg(-w,-h,-w, 0); seg(+w,+h,-w,+h)


# ── variant painters ─────────────────────────────────────────────────────────

_BCX, _BCY = 32, 52

_PUR   = (106,  45, 168);  _PUR_D  = ( 74,  28, 122);  _PUR_H  = (140,  80, 206)
_RED   = (200,  20,  30);  _RED_D  = (140,  12,  18);  _RED_H  = (220,  55,  65)
_GRN   = (  0, 128,  55);  _GRN_D  = (  0,  88,  38);  _GRN_H  = ( 30, 165,  85)
_BLU   = ( 30,  60, 160);  _BLU_D  = ( 18,  38, 110);  _BLU_H  = ( 60, 100, 210)
_GOLD  = (235, 180,   0);  _GOLD_D = (165, 120,   0)
_CGD   = (200, 160,  10);  _CGD_D  = (140, 110,   5)
_WHITE = (242, 242, 242);  _WHITE_D = (196, 196, 204)


def _paint_laker(surf, _a):
    _draw_kit(surf, _BCX, _BCY,
              jersey=_PUR,   jersey_d=_PUR_D,   jersey_h=_PUR_H,
              trim=_WHITE,   trim_d=_WHITE_D,
              num_col=_WHITE, num_d=_PUR_D, number="8",
              shoe=_WHITE,   shoe_d=_WHITE_D,   shoe_ac=_GOLD)


def _paint_bull(surf, _a):
    _draw_kit(surf, _BCX, _BCY,
              jersey=_RED,   jersey_d=_RED_D,   jersey_h=_RED_H,
              trim=_WHITE,   trim_d=_WHITE_D,
              num_col=_WHITE, num_d=_RED_D, number="3",
              shoe=_WHITE,   shoe_d=_WHITE_D,   shoe_ac=_RED)


def _paint_celtic(surf, _a):
    _draw_kit(surf, _BCX, _BCY,
              jersey=_GRN,   jersey_d=_GRN_D,   jersey_h=_GRN_H,
              trim=_CGD,     trim_d=_CGD_D,
              num_col=_CGD,  num_d=_GRN_D, number="3",
              shoe=_WHITE,   shoe_d=_WHITE_D,   shoe_ac=_CGD)


def _paint_warrior(surf, _a):
    _draw_kit(surf, _BCX, _BCY,
              jersey=_BLU,   jersey_d=_BLU_D,   jersey_h=_BLU_H,
              trim=_GOLD,    trim_d=_GOLD_D,
              num_col=_GOLD, num_d=_BLU_D, number="3",
              shoe=_WHITE,   shoe_d=_WHITE_D,   shoe_ac=_GOLD,
              band_accent=_BLU)


# ── module API ────────────────────────────────────────────────────────────────

_POOL = (
    _make_skin(_paint_laker),    # 0
    _make_skin(_paint_bull),     # 1
    _make_skin(_paint_celtic),   # 2
    _make_skin(_paint_warrior),  # 3
)
POOL_SIZE = len(_POOL)

# Names + identity colours for the in-store variant picker swatches.
VARIANT_NAMES  = ["THE LAKER", "THE BULL", "THE CELTIC", "THE WARRIOR"]
VARIANT_JERSEY = [_PUR,  _RED,  _GRN,  _BLU]
VARIANT_TRIM   = [_WHITE, _WHITE, _CGD, _GOLD]
VARIANT_NUMBER = ["8",   "3",   "3",   "3"]

_chosen = None


def sync_from_store() -> None:
    """Read the persisted variant index and lock in the matching design."""
    global _chosen
    idx = store_data.skin_variant("skin_basketball")
    if idx is None or not (0 <= int(idx) < POOL_SIZE):
        idx = 0
    _chosen = _POOL[int(idx)]


def get_basketball_parrot(frame_idx: int, tilt_deg: float):
    global _chosen
    if _chosen is None:
        sync_from_store()
    return _chosen(frame_idx, tilt_deg)


BUILDERS = {"skin_basketball": get_basketball_parrot}
