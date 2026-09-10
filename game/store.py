"""
Coin Store — spend banked coins on cosmetics.

Reached from the menu's STORE pill (STATE_STORE). The wallet that backs it
(game/store_data.py) banks each run's coins at death, so the balance shown
here grows as the player flies.

This module owns the whole frame for STATE_STORE. The App's `_render` hands
it the screen surface; the App's `_flap_input` routes taps *into*
`handle_tap`, which returns an action token ("back" / None) — the store is
interactive, so taps are dispatched here rather than blanket-dismissing the
screen like the one-tap help explainer.

Visual language ("Obsidian & Gold", art-director locked spec B+): obsidian
top-lit cards on a night-sky gradient, a fine gold inner bezel, a rarity
SHELF-LIGHT BAR glowing up from each card base (the primary tier cue), a small
inset faceted GEM badge (secondary), the procedural thumbnail on a clean dark
inset disc, and a luxe gold balance capsule. Rarity reads by HUE *and* VALUE so
the four tiers + the mystery state stay colourblind-safe.
"""
from __future__ import annotations

import math
import pygame

from game.config import W, H
from game.hud import _font, _draw_overlay_stars, \
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game.draw import UI_CREAM, NEAR_BLACK, WHITE, rounded_rect, lerp_color
from game.powerup_help import _seeded_stars
from game import parrot
from game import store_catalog
from game import store_data
from game import store_cards
from game import store_design
from game.surprise_box_variants import _draw_qmark
from game.store_hub import CLOSED_GROUPS as _STORE_CLOSED, title_wordmark

# Card grid metrics (2 columns). Thumbnails are pre-rendered once so the
# per-frame cost is a flat blit rather than eight smoothscales.
_CARD_W = 162
_CARD_H = 100
_GAP = 8
_GRID_TOP = 116        # leaves room for the title + balance + tab bar above
_PER_PAGE = 8          # 2 columns x 4 rows; each tab pages independently

_TAB_Y = 92            # tab-bar centre line
_TABS = tuple(
    (lbl, g) for lbl, g in (
        ("COSTUMES", "costume"), ("PARROTS", "parrot"),
        ("ANIMALS", "animal"), ("SHOES", "shoes"), ("HATS", "hats"),
        ("SHADES", "shades"), ("PARCELS", "parcels"),
    )
    if g not in _STORE_CLOSED
)
# Stall group -> tab index, so a tap on a lagoon-hub stall lands on that
# category's grid. Only open stalls appear; closed ones are excluded so the
# tab bar never shows an empty category.
_GROUP_TAB = {g: i for i, (_label, g) in enumerate(_TABS)}

# Night-sky gradient stops the obsidian cards were tuned against.
_BG_STOPS = ((8, 8, 24), (12, 12, 36), (18, 16, 48), (24, 20, 58))

# Obsidian card body stops — near-black, subtly top-lit (never rarity-tinted).
_OBS_TOP = (26, 24, 32)
_OBS_BOT = (9, 8, 15)

# ── rarity language (locked spec) ────────────────────────────────────────────
# The four tiers + the mystery state separate by HUE *and* VALUE so they survive
# grayscale (colourblind-safe). Both the shelf-bar and the gem pull the same
# per-tier triplet so a card reads as one jewel. Grayscale ladder (gem luma):
# epic < common < rare < legendary < mystery — five separable steps, brightest
# reserved for the un-tiered mystery.
_RARITY = {
    "common":    {"gem": (208, 178, 132), "glow": (196, 162, 110), "deep": (96, 74, 44)},
    "rare":      {"gem": (96, 196, 240),  "glow": (64, 172, 230),  "deep": (20, 78, 116)},
    "epic":      {"gem": (190, 104, 236), "glow": (170, 78, 232),  "deep": (70, 28, 104)},
    "legendary": {"gem": (255, 168, 56),  "glow": (255, 138, 30),  "deep": (132, 64, 10)},
}
# MYSTERY (secret ???): neutral iridescent silver — highest value, no saturated
# hue, so it claims NO tier and never collides with RARE's blue.
_MYSTERY = {"gem": (214, 218, 224), "glow": (176, 196, 214), "deep": (78, 84, 98)}

# Unified chip family: one pill silhouette + hairline rim for every state; only
# the fill + content differ. The can't-afford "locked" chip is dark cool slate-
# blue (never warm gold) so it can't be mistaken for the EQUIP chip.
_CHIP_STATES = {
    "price":    {"fg": _GOLD_PALE,     "bg": _GOLD_DEEP,     "rim": (*_GOLD_BRIGHT, 150)},
    "equip":    {"fg": UI_CREAM,       "bg": (96, 74, 24),   "rim": (*_GOLD_BRIGHT, 150)},
    "equipped": {"fg": (10, 30, 14),   "bg": (84, 196, 112), "rim": (200, 255, 210, 200)},
    "locked":   {"fg": (150, 166, 190), "bg": (40, 46, 62),  "rim": (88, 102, 132, 180)},
}


# ── cached primitives (the store is a menu screen; cache the heavy builds) ────
_panel_cache: dict = {}
_disc_cache: dict = {}
_bg_cache: dict = {}   # keyed (W, H) — gradient is constant, stars overlay live
_shelf_cache: dict = {}
_coin_cache: dict = {}


def _vgrad_panel(w, h, radius, top, bot, alpha=255):
    """Rounded vertical-gradient panel (top brighter), corner-masked. Cached by
    args — every card shares one body surface, so this builds once."""
    key = (w, h, radius, top, bot, alpha)
    cached = _panel_cache.get(key)
    if cached is not None:
        return cached
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(top, bot, y / max(1, h - 1))
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _panel_cache[key] = body
    return body


def _coin_glyph(surf, cx, cy, r):
    """The one coin used everywhere (price chip, balance, modal): a flat-gold
    disc with a single diagonal bevel + a stamped "$" — no gear teeth (those
    read as muddy noise at chip scale). Cached per radius."""
    key = int(r)
    face = _coin_cache.get(key)
    if face is None:
        d = r * 2
        face = pygame.Surface((d + 2, d + 2), pygame.SRCALPHA)
        c = r + 1
        for yy in range(d + 2):
            for xx in range(d + 2):
                dx, dy = xx - c, yy - c
                if dx * dx + dy * dy > r * r:
                    continue
                diag = (dx + dy) / (2 * r) + 0.5
                col = lerp_color((255, 230, 150), (188, 132, 30),
                                 max(0.0, min(1.0, diag)) ** 0.85)
                face.set_at((xx, yy), (*col, 255))
        pygame.draw.circle(face, (*_GOLD_DEEP, 230), (c, c), r, 1)
        hl = pygame.Surface((d + 2, d + 2), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 250, 220, 220), (c, c),
                           max(1, r - 2), max(1, r // 6))
        for yy in range(d + 2):
            for xx in range(d + 2):
                if (xx - c) + (yy - c) > -r * 0.45:
                    hl.set_at((xx, yy), (0, 0, 0, 0))
        face.blit(hl, (0, 0))
        sf = _font(max(9, int(r * 1.5)), True)
        face.blit(sf.render("$", True, (120, 80, 16)),
                  sf.render("$", True, (120, 80, 16)).get_rect(center=(c, c)))
        sg2 = sf.render("$", True, (255, 238, 180))
        face.blit(sg2, sg2.get_rect(center=(c, c - 1)))
        _coin_cache[key] = face
    surf.blit(face, face.get_rect(center=(cx, cy)))


def _soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=6):
    """Layered additive bloom — cheap (no per-pixel) so elements emit light."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.7)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def _drop_shadow(surf, rect, radius, blur=6, alpha=120, dy=4):
    """Soft drop shadow under a card."""
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 2 / blur * 2.2)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy, rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
        surf.blit(s, r.topleft)


def _inset_disc(surf, cx, cy, r, tint=(6, 6, 12)):
    """A clean dark inset disc for the thumbnail (never rarity-tinted). Cached."""
    key = (r, tint)
    disc = _disc_cache.get(key)
    if disc is None:
        disc = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        for i in range(r, 0, -1):
            c = lerp_color((30, 28, 40), tint, (i / r) ** 1.3)
            pygame.draw.circle(disc, (*c, 255), (r + 1, r + 1), i)
        pygame.draw.circle(disc, (0, 0, 0, 130), (r + 1, r + 1), r, 2)
        pygame.draw.circle(disc, (*_GOLD_DEEP, 60), (r + 1, r + 1), r - 1, 1)
        _disc_cache[key] = disc
    surf.blit(disc, (cx - r - 1, cy - r - 1))


def _shelf_bar(surf, rect, tier, intensity=1.0, mystery=False):
    """The rarity SHELF-LIGHT BAR along the card base — an additive horizontal
    gradient strip in the tier colour that glows UP into the body like a vitrine
    light. PRIMARY rarity cue. Cached per (width, tier)."""
    bw = rect.w - 28
    key = (bw, "mystery" if mystery else tier, round(intensity, 2))
    pair = _shelf_cache.get(key)
    if pair is None:
        pal = _MYSTERY if mystery else _RARITY[tier]
        glow, gem = pal["glow"], pal["gem"]
        wash_h = int(10 * intensity) + 6
        wash = pygame.Surface((bw, wash_h), pygame.SRCALPHA)
        peak = int(22 * intensity) + 8
        for y in range(wash_h):
            f = 1.0 - y / wash_h
            a = int(peak * f ** 2.6)
            if a <= 0:
                continue
            for seg in range(0, bw, 2):
                hx = abs(seg - bw / 2) / (bw / 2)
                ha = int(a * (1.0 - 0.6 * hx ** 2))
                if ha > 0:
                    wash.set_at((seg, wash_h - 1 - y), (*glow, ha))
                    if seg + 1 < bw:
                        wash.set_at((seg + 1, wash_h - 1 - y), (*glow, ha))
        core = pygame.Surface((bw, 3), pygame.SRCALPHA)
        for sx in range(bw):
            hx = abs(sx - bw / 2) / (bw / 2)
            c = lerp_color(lerp_color(gem, WHITE, 0.4), pal["deep"], hx ** 1.4)
            a = int(255 * (1.0 - 0.4 * hx ** 2))
            for sy in range(3):
                core.set_at((sx, sy), (*c, a))
        mask = pygame.Surface((bw, 3), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bw, 3), border_radius=1)
        core.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pair = (wash, core, wash_h)
        _shelf_cache[key] = pair
    wash, core, wash_h = pair
    bx = rect.x + 14
    by = rect.bottom - 8
    surf.blit(wash, (bx, by - wash_h + 3), special_flags=pygame.BLEND_ADD)
    surf.blit(core, (bx, by))


def _gold_leaf(surf, cx, cy, sx):
    """A tiny two-leaf gold sprig flourish for LEGENDARY cards only (faint)."""
    leaf = pygame.Surface((20, 16), pygame.SRCALPHA)
    pygame.draw.line(leaf, (*_GOLD_DEEP, 170), (10, 14), (10, 3), 1)
    pygame.draw.ellipse(leaf, (*_GOLD_BRIGHT, 150), (4, 4, 7, 9))
    pygame.draw.ellipse(leaf, (*_GOLD_BRIGHT, 150), (10, 5, 7, 9))
    if sx < 0:
        leaf = pygame.transform.flip(leaf, True, False)
    surf.blit(leaf, (cx - 10, cy - 6))


def _gem(surf, cx, cy, r, tier, t=0.0, inset=True, mystery=False):
    """Faceted rarity gem badge inset in the card corner — a three-value cut
    (lit TL, mid right, shaded BL, darker BR shadow facet) + a white specular
    pip, seated in a dark keyline well. SECONDARY rarity marker."""
    pal = _MYSTERY if mystery else _RARITY[tier]
    base, glow, deep = pal["gem"], pal["glow"], pal["deep"]
    if inset:
        seat = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(seat, (0, 0, 0, 150), (r + 4, r + 4), r + 3)
        pygame.draw.circle(seat, (*_GOLD_DEEP, 90), (r + 4, r + 4), r + 3, 1)
        surf.blit(seat, (cx - r - 4, cy - r - 4))
    _soft_glow(surf, cx, cy, int(r * 1.5), glow,
               int(70 + 30 * (0.5 + 0.5 * math.sin(t * 3))), layers=4)
    top, bot = (cx, cy - r), (cx, cy + r)
    left, right = (cx - r, cy), (cx + r, cy)
    ctr = (cx, cy)
    if mystery:
        f1 = lerp_color((196, 214, 226), (214, 202, 224), 0.5)
        hi, mid = lerp_color(f1, WHITE, 0.55), f1
        sh = lerp_color(f1, deep, 0.45)
        dk = lerp_color(deep, NEAR_BLACK, 0.25)
    else:
        hi, mid = lerp_color(base, WHITE, 0.5), base
        sh = lerp_color(base, deep, 0.5)
        dk = lerp_color(deep, NEAR_BLACK, 0.3)
    pygame.draw.polygon(surf, hi, [top, left, ctr])
    pygame.draw.polygon(surf, mid, [top, right, ctr])
    pygame.draw.polygon(surf, sh, [left, bot, ctr])
    pygame.draw.polygon(surf, dk, [right, bot, ctr])
    pygame.draw.polygon(surf, lerp_color(deep, NEAR_BLACK, 0.45),
                        [top, right, bot, left], width=1)
    pr = max(1, r // 4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 245), (pr + 1, pr + 1), pr)
    surf.blit(pip, (cx - pr - r // 3, cy - pr - r // 3), special_flags=pygame.BLEND_ADD)


def _gold_rule(surf, x0, x1, y, peak=170):
    """A soft gold GRADIENT rule — bright at centre, fading at both ends."""
    w = x1 - x0
    line = pygame.Surface((w, 3), pygame.SRCALPHA)
    for sx in range(w):
        hx = abs(sx - w / 2) / (w / 2)
        a = int(peak * (1.0 - hx ** 1.6))
        if a <= 0:
            continue
        line.set_at((sx, 1), (*_GOLD_BRIGHT, a))
        line.set_at((sx, 0), (*_GOLD_PALE, a // 2))
        line.set_at((sx, 2), (*_GOLD_DEEP, a // 2))
    surf.blit(line, (x0, y - 1))


def _confirm_tier_banner(big, cx, cy, w_log, h_log, tier_word, pal):
    """Lozenge rarity banner for the confirm popup — matches the item card style:
    outward-pointed ends, tier gradient, dark embedded tier word."""
    m = store_cards.m
    f = store_cards.font(h_log * 0.58)
    tw = store_cards._glyph_base(tier_word, f, m(1.4)).get_width()
    pad = m(16)
    w = min(m(w_log), tw + pad * 2)
    h = m(h_log)
    pt = h // 2
    x0, y0 = m(cx) - w // 2, m(cy) - h // 2
    poly = [(0, h // 2), (pt, 0), (w - pt, 0),
            (w, h // 2), (w - pt, h), (pt, h)]
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = store_cards.vgrad_stops(w, h, 0,
                                   [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                                   255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(big, NEAR_BLACK, abspoly, width=max(1, m(1.4)))
    store_cards.plain_text(big, tier_word, f, (m(cx), m(cy)), (14, 12, 26),
                           shadow_a=0, tracking=m(1.4), weight=m(0.7))


def _gradient_text(surf, txt, font_obj, center, top, bot, outline=None, shadow=True):
    """Vertical gold-gradient text with optional outline + drop shadow."""
    base = font_obj.render(txt, True, WHITE)
    w, h = base.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        pygame.draw.line(grad, lerp_color(top, bot, y / max(1, h - 1)),
                         (0, y), (w, y))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
    if outline:
        out = font_obj.render(txt, True, outline)
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                       (-2, -2), (2, -2), (-2, 2), (2, 2)):
            surf.blit(out, (r.x + ox, r.y + oy))
    if shadow:
        sh = font_obj.render(txt, True, NEAR_BLACK)
        sh.set_alpha(150)
        surf.blit(sh, (r.x + 1, r.y + 2))
    surf.blit(grad, r.topleft)
    return r


def _lock_glyph(surf, cx, cy, col):
    """Tiny padlock for the can't-afford chip — body + shackle."""
    rounded_rect(surf, pygame.Rect(cx - 4, cy - 1, 8, 6), 2, col)
    pygame.draw.arc(surf, col, (cx - 3, cy - 6, 6, 8), 0.2, math.pi - 0.2, 2)
    surf.set_at((cx, cy + 2), (24, 28, 38))


def _chip(surf, cx, cy, text, state, coin=False, h=24, lock=False):
    """The single chip silhouette for all states: pill body (gradient), hairline
    rim, optional coin glyph or lock, centred on (cx, cy)."""
    sp = _CHIP_STATES[state]
    f = _font(max(12, int(h * 0.56)), True)
    timg = f.render(text, True, sp["fg"])
    coin_d = int(h * 0.62)
    pre_w = (coin_d + 4) if coin else (12 if lock else 0)
    pad = 12
    w = pre_w + timg.get_width() + pad * 2
    chip = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    surf.blit(_vgrad_panel(w, h, h // 2, lerp_color(sp["bg"], WHITE, 0.18),
                           sp["bg"]), chip.topleft)
    sheen_peak = 28 if state == "locked" else 46
    sheen = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    for y in range(h // 2):
        pygame.draw.line(sheen, (255, 255, 255, int(sheen_peak * (1 - y / (h // 2)))),
                         (0, y), (w - 6, y))
    smask = pygame.Surface((w - 6, h // 2), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(), border_radius=h // 2)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, (chip.x + 3, chip.y + 2))
    pygame.draw.rect(surf, sp["rim"], chip, width=1, border_radius=h // 2)
    x = chip.x + pad
    if coin:
        _coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
        x += coin_d + 4
    elif lock:
        _lock_glyph(surf, x + 4, cy, sp["fg"])
        x += 12
    surf.blit(timg, timg.get_rect(midleft=(x, cy)))
    return chip


def _draw_chevron(surf, rect, direction) -> None:
    """A small ``<`` / ``>`` scroll affordance at a tab-strip edge."""
    cx, cy = rect.center
    d = direction
    pts = [(cx - 2 * d, cy - 5), (cx + 3 * d, cy), (cx - 2 * d, cy + 5)]
    pygame.draw.lines(surf, (*_GOLD_PALE, 220), False, pts, 2)



def _slot_of(sid: str) -> str:
    """The equip slot a store card belongs to (its catalog ``kind``), so the
    equipped-accent + tap-to-equip logic works for parcels as well as skins."""
    if sid == store_catalog.PARCEL_BASE:
        return "parcel"
    if sid == store_catalog.BASE_SKIN or not store_catalog.exists(sid):
        return "skin"
    return store_catalog.kind(sid)


class StoreScene:
    _TAP_SLOP = 8   # px total horizontal move below which a press/release is a tap
    _SWIPE_MIN = 40  # px net horizontal displacement required to commit a page flip

    def __init__(self) -> None:
        self.t = 0.0
        # Two-level store: open onto the lagoon "hub" (a stall per category);
        # tapping a stall drills into that category's "category" grid. The hub's
        # heavy procedural backdrop is built lazily on first hub render so the
        # store-open transition isn't blocked, and is then cached process-wide.
        self.view = "hub"
        self.hub: object | None = None
        self._stars = _seeded_stars()
        self.back_rect: "pygame.Rect | None" = None
        self.item_rects: "dict[str, pygame.Rect]" = {}
        self.prev_rect: "pygame.Rect | None" = None
        self.next_rect: "pygame.Rect | None" = None
        self.tab_rects: "list[pygame.Rect]" = []
        self.tab_scroll = 0.0  # horizontal pan of the scrollable tab strip
        self.tab_chev_l: "pygame.Rect | None" = None
        self.tab_chev_r: "pygame.Rect | None" = None
        self._tab_vp = pygame.Rect(12, _TAB_Y - 13, W - 24, 26)
        self._tab_widths: "list[int]" = []
        self._tab_gap = 6
        self._toast = ("", 0.0)  # (text, seconds remaining)
        # Pending buy-confirmation: the sid awaiting a CONFIRM/CANCEL, plus the
        # modal's hit rects. Coins are never spent until CONFIRM, so a stray tap
        # on an unowned card can't drain the wallet by accident.
        self._confirm: "str | None" = None
        self._confirm_panel: "pygame.Rect | None" = None
        self.confirm_yes_rect: "pygame.Rect | None" = None
        self.confirm_no_rect: "pygame.Rect | None" = None
        # Variant picker (shown before the confirm modal for multi-look skins).
        self._variant_pick: "str | None" = None
        self._variant_choice: int = 0
        self._variant_swatch_rects: "list" = []
        self._variant_ok_rect: "pygame.Rect | None" = None
        self._variant_cancel_rect: "pygame.Rect | None" = None
        self._variant_panel: "pygame.Rect | None" = None
        store_data.load()
        store_cards.clear_cache()
        # Per-tab skin lists, cheapest first. PARROTS/SHADES/PARCELS are fronted
        # by a free DEFAULT card so the player can always revert.
        self._lists: "dict[str, list[str]]" = {}
        for label, g in _TABS:
            ids = sorted(store_catalog.ids_of_group(g), key=store_catalog.cost)
            if g in ("parrot", "shades"):
                ids = [store_catalog.BASE_SKIN] + ids
            elif g == "parcels":
                ids = [store_catalog.PARCEL_BASE] + ids
            self._lists[g] = ids
        self.tab = 0
        self.page = 0
        self._swipe_active = False
        self._swipe_x_start = 0
        self._swipe_x_last = 0
        self._swipe_moved = 0

    def _cur_ids(self) -> list:
        return self._lists[_TABS[self.tab][1]]

    @property
    def n_pages(self) -> int:
        return max(1, (len(self._cur_ids()) + _PER_PAGE - 1) // _PER_PAGE)

    @staticmethod
    def _disp_name(sid: str) -> str:
        return "DEFAULT" if sid in (store_catalog.BASE_SKIN,
                                    store_catalog.PARCEL_BASE) \
            else store_catalog.name(sid)

    def update(self, dt: float) -> None:
        self.t += dt
        text, ttl = self._toast
        if ttl > 0.0:
            self._toast = (text, max(0.0, ttl - dt))

    def _flash(self, text: str) -> None:
        self._toast = (text, 1.6)

    # ── swipe / pointer ───────────────────────────────────────────────────────
    def pointer_down(self, pos: tuple) -> None:
        self._swipe_active = True
        self._swipe_x_start = self._swipe_x_last = pos[0]
        self._swipe_moved = 0

    def pointer_move(self, pos: tuple) -> None:
        if not self._swipe_active:
            return
        self._swipe_moved += abs(pos[0] - self._swipe_x_last)
        self._swipe_x_last = pos[0]

    def pointer_up(self) -> bool:
        """Return True if the gesture was a tap (caller should dispatch handle_tap)."""
        if not self._swipe_active:
            return True
        self._swipe_active = False
        if self._swipe_moved < self._TAP_SLOP:
            return True  # tap — caller calls handle_tap
        if (self.view == "category"
                and self._variant_pick is None
                and self._confirm is None):
            dx = self._swipe_x_last - self._swipe_x_start
            if dx < -self._SWIPE_MIN:          # left swipe → next page / next tab
                if self.page < self.n_pages - 1:
                    self.page += 1
                elif self.tab < len(_TABS) - 1:
                    self.tab += 1
                    self.page = 0
            elif dx > self._SWIPE_MIN:         # right swipe → prev page / prev tab
                if self.page > 0:
                    self.page -= 1
                elif self.tab > 0:
                    self.tab -= 1
                    self.page = self.n_pages - 1  # land on last page of prev tab
        return False  # swipe consumed; do not also dispatch a tap

    # ── rendering ────────────────────────────────────────────────────────────
    def render(self, surf: pygame.Surface) -> None:
        if self.view == "hub":
            self._render_hub(surf)
        else:
            self._render_category(surf)

    def _render_hub(self, surf: pygame.Surface) -> None:
        """The lagoon stilt-market landing: the cached procedural scene owns the
        STORE wordmark + balance capsule, so the chrome here is just the BACK
        affordance (which exits the store from the hub)."""
        if self.hub is None:
            from game.store_hub import LagoonHub
            self.hub = LagoonHub()
        self.hub.render(surf, store_data.balance(), self.t)
        self._draw_back(surf)

    def _render_category(self, surf: pygame.Surface) -> None:
        self._draw_bg(surf)
        self._draw_title(surf)
        self._draw_balance(surf, y=16)
        self._draw_tabs(surf)

        base_x = (W - (_CARD_W * 2 + _GAP)) // 2
        self.item_rects = {}
        ids = self._cur_ids()
        page_skins = ids[self.page * _PER_PAGE:(self.page + 1) * _PER_PAGE]
        if not page_skins:
            msg = _font(16, True).render("COMING SOON", True, _GOLD_PALE)
            msg.set_alpha(200)
            surf.blit(msg, msg.get_rect(center=(W // 2, _GRID_TOP + 150)))
        for idx, sid in enumerate(page_skins):
            x = base_x + (idx % 2) * (_CARD_W + _GAP)
            y = _GRID_TOP + (idx // 2) * (_CARD_H + _GAP)
            rect = pygame.Rect(x, y, _CARD_W, _CARD_H)
            self.item_rects[sid] = rect
            self._draw_card(surf, sid, rect)

        grid_bot = _GRID_TOP + 4 * (_CARD_H + _GAP)
        self._draw_page_controls(surf, base_x, grid_bot - 4, _CARD_W * 2 + _GAP)

        self._draw_toast(surf)
        self._draw_back(surf)
        # Modals overlay everything else when active.
        self._draw_variant_picker(surf)
        self._draw_confirm(surf)

    def _draw_bg(self, surf) -> None:
        key = (W, H)
        bg = _bg_cache.get(key)
        if bg is None:
            bg = pygame.Surface((W, H))
            n = len(_BG_STOPS)
            for y in range(H):
                f = y / (H - 1)
                seg = min(n - 2, int(f * (n - 1)))
                local = (f * (n - 1)) - seg
                pygame.draw.line(bg, lerp_color(_BG_STOPS[seg], _BG_STOPS[seg + 1],
                                                local), (0, y), (W - 1, y))
            _bg_cache[key] = bg
        surf.blit(bg, (0, 0))
        _draw_overlay_stars(surf, self._stars, self.t + 1.4)

    def _draw_title(self, surf) -> None:
        _SS = 2
        strip_h = 72
        bw, bh = W * _SS, strip_h * _SS
        big = pygame.Surface((bw, bh), pygame.SRCALPHA)
        title_wordmark(big, "STORE", (bw // 2, bh // 2), 42, tracking=8)
        surf.blit(pygame.transform.smoothscale(big, (W, strip_h)),
                  (0, 38 - strip_h // 2))

    def _draw_balance(self, surf, y) -> None:
        """Gold capsule + gradient-gold digits in the top-right corner.
        Uses the real gameplay parrot-medallion coin (no $ glyph, rope rim)."""
        val = f"{store_data.balance():,}"
        vf = _font(18, True)
        vimg_w = vf.size(val)[0]
        coin_d, gap_coin, pad = 20, 7, 6
        w = coin_d + gap_coin + vimg_w + pad * 2
        cap = pygame.Rect(0, y - 14, w, 28)
        cap.right = W - 4
        _drop_shadow(surf, cap, 14, blur=4, alpha=90)
        surf.blit(_vgrad_panel(cap.w, cap.h, 14, (44, 32, 18), (20, 14, 8), 252),
                  cap.topleft)
        pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1,
                         border_radius=13)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190), cap, width=1, border_radius=14)
        x = cap.x + pad
        store_cards.coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
        x += coin_d + gap_coin
        _gradient_text(surf, val, vf, (x + vimg_w // 2, y),
                       (255, 246, 196), (236, 170, 60), shadow=True)

    def _draw_tabs(self, surf) -> None:
        """Horizontally scrollable tab strip. Active tab gets a warm-gold
        gradient pill-capsule; inactive tabs show a faint gold wash + dim
        label. With more tabs than fit the strip clips to a viewport flanked
        by ``< >`` chevrons; switching resets that tab to page 1 and scrolls
        it into view."""
        f = _font(12, True)
        pad, gap = 11, 6
        widths = [f.size(label)[0] + 2 * pad for label, _g in _TABS]
        content_w = sum(widths) + gap * (len(_TABS) - 1)
        full_vp = pygame.Rect(12, _TAB_Y - 13, W - 24, 26)
        overflow = content_w > full_vp.width
        chev = 18 if overflow else 0
        vp = pygame.Rect(full_vp.x + chev, full_vp.y, full_vp.width - 2 * chev, 26)
        max_scroll = max(0, content_w - vp.width)
        self.tab_scroll = max(0.0, min(self.tab_scroll, float(max_scroll)))
        self._tab_vp, self._tab_widths, self._tab_gap = vp, widths, gap

        # Center the group when all tabs fit (no overflow / dead air on right).
        x_offset = (vp.width - content_w) // 2 if not overflow else 0

        prev_clip = surf.get_clip()
        surf.set_clip(vp)
        self.tab_rects = []

        # Two passes: inactive wash first, active pill on top so the bright
        # capsule and its dark label are never obscured by a neighbour's wash.
        active_r = None
        cx = 0
        for i, (label, _g) in enumerate(_TABS):
            w = widths[i]
            r = pygame.Rect(round(vp.x + x_offset + cx - self.tab_scroll), _TAB_Y - 13, w, 26)
            self.tab_rects.append(r)
            if i == self.tab:
                active_r = r
            else:
                wash = r.inflate(-2, -4)
                # Inactive wash via SRCALPHA temp surface — draw.rect with an
                # alpha colour on an opaque surface discards the alpha silently.
                tmp = pygame.Surface((wash.width, wash.height), pygame.SRCALPHA)
                pygame.draw.rect(tmp, (*_GOLD_PALE, 38),
                                 (0, 0, wash.width, wash.height), width=0, border_radius=11)
                pygame.draw.rect(tmp, (*_GOLD_DEEP, 70),
                                 (0, 0, wash.width, wash.height), width=1, border_radius=11)
                surf.blit(tmp, wash.topleft)
                timg = f.render(label, True, _GOLD_PALE)
                timg.set_alpha(190)
                surf.blit(timg, timg.get_rect(center=r.center))
            cx += w + gap

        if active_r is not None:
            label = _TABS[self.tab][0]
            cap = active_r.inflate(-2, -4)
            _drop_shadow(surf, cap, 11, blur=3, alpha=100)
            surf.blit(_vgrad_panel(cap.w, cap.h, 11, (248, 202, 92), (214, 154, 46), 242),
                      cap.topleft)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), cap, width=1, border_radius=11)
            # Inner highlight on top edge reads as a lit bevel.
            pygame.draw.line(surf, (*_GOLD_PALE, 60),
                             (cap.x + 6, cap.y + 1), (cap.right - 6, cap.y + 1))
            timg = f.render(label, True, NEAR_BLACK)
            surf.blit(timg, timg.get_rect(center=active_r.center))

        surf.set_clip(prev_clip)

        self.tab_chev_l = self.tab_chev_r = None
        if overflow and self.tab_scroll > 1:
            self.tab_chev_l = pygame.Rect(full_vp.x, full_vp.y, chev, 26)
            _draw_chevron(surf, self.tab_chev_l, -1)
        if overflow and self.tab_scroll < max_scroll - 1:
            self.tab_chev_r = pygame.Rect(full_vp.right - chev, full_vp.y, chev, 26)
            _draw_chevron(surf, self.tab_chev_r, 1)

    def _scroll_tab_into_view(self, i: int) -> None:
        """Pan the strip so tab ``i`` is fully visible (used on tab select)."""
        if not getattr(self, "_tab_widths", None):
            return
        x = sum(self._tab_widths[:i]) + self._tab_gap * i
        w = self._tab_widths[i]
        if x < self.tab_scroll:
            self.tab_scroll = float(x)
        elif x + w > self.tab_scroll + self._tab_vp.width:
            self.tab_scroll = float(x + w - self._tab_vp.width)

    def _draw_card(self, surf, sid: str, rect: pygame.Rect) -> None:
        """Constellation jewel card (indigo body + gold bevel, glass cabochon
        thumb, faceted tier gem, notched rarity ribbon, cream name, price/EQUIPPED
        chip). The card is static per (sid, equipped, masked) state, so it is
        supersampled + cached once in game/store_cards.py and blitted here."""
        owned = store_data.is_owned(sid)
        equipped = (store_data.equipped(_slot_of(sid)) == sid)
        surf.blit(store_cards.render_card(sid, equipped=equipped, owned=owned),
                  rect.topleft)

    def _state_chip(self, surf, sid, cx, cy, owned, equipped, secret, h=24) -> None:
        """The actionable state line: EQUIPPED / EQUIP / price / can't-afford,
        in the one unified chip silhouette."""
        if equipped:
            _chip(surf, cx, cy, "EQUIPPED", "equipped", h=h)
            return
        if owned and not secret:
            _chip(surf, cx, cy, "EQUIP", "equip", h=h)
            return
        price = store_catalog.cost(sid)
        if store_data.balance() >= price:
            _chip(surf, cx, cy, f"{price:,}", "price", coin=True, h=h)
        else:
            _chip(surf, cx, cy, f"{price:,}", "locked", lock=True, h=h)

    def _draw_page_controls(self, surf, x, y, w) -> None:
        """‹  PAGE n/N  › — tap arrows to flip pages. Hidden when it all fits."""
        self.prev_rect = self.next_rect = None
        if self.n_pages <= 1:
            return
        cy = y + 11
        lbl = _font(12, True).render(f"PAGE  {self.page + 1} / {self.n_pages}",
                                     True, _GOLD_PALE)
        surf.blit(lbl, lbl.get_rect(center=(x + w // 2, cy)))
        self.prev_rect = self._arrow(surf, x + 24, cy, "<", self.page > 0)
        self.next_rect = self._arrow(surf, x + w - 24, cy, ">",
                                     self.page < self.n_pages - 1)

    def _arrow(self, surf, cx, cy, glyph, enabled) -> "pygame.Rect | None":
        r = pygame.Rect(0, 0, 46, 30)
        r.center = (cx, cy)
        surf.blit(_vgrad_panel(r.w, r.h, 11, (44, 34, 20) if enabled else (44, 40, 50),
                               (24, 18, 10) if enabled else (28, 24, 32)), r.topleft)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190) if enabled else (88, 80, 90),
                         r, width=1, border_radius=11)
        g = _font(17, True).render(glyph, True,
                                   _GOLD_PALE if enabled else (140, 132, 146))
        surf.blit(g, g.get_rect(center=(cx, cy - 1)))
        return r if enabled else None

    def _draw_back(self, surf) -> None:
        r = pygame.Rect(0, 0, 160, 36)
        r.center = (W // 2, H - 26)
        _drop_shadow(surf, r, 18, blur=4, alpha=90)
        surf.blit(_vgrad_panel(r.w, r.h, 18, (40, 32, 56), (22, 16, 38), 240),
                  r.topleft)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 185), r, width=1, border_radius=18)
        timg = _font(18, True).render("BACK", True, _GOLD_PALE)
        surf.blit(timg, timg.get_rect(center=r.center))
        self.back_rect = r

    def _draw_toast(self, surf) -> None:
        text, ttl = self._toast
        if ttl <= 0.0 or not text:
            return
        alpha = int(255 * min(1.0, ttl / 0.4))  # fade out over the last 0.4 s
        timg = _font(15, True).render(text, True, _GOLD_BRIGHT)
        timg.set_alpha(alpha)
        bg = pygame.Rect(0, 0, timg.get_width() + 28, 30)
        bg.center = (W // 2, H - 70)
        panel = pygame.Surface(bg.size, pygame.SRCALPHA)
        rounded_rect(panel, panel.get_rect(), 15, (20, 12, 40),
                     alpha=min(220, alpha))
        pygame.draw.rect(panel, (*_GOLD_BRIGHT, min(150, alpha)),
                         panel.get_rect(), width=1, border_radius=15)
        surf.blit(panel, bg.topleft)
        surf.blit(timg, timg.get_rect(center=bg.center))

    def _draw_variant_picker(self, surf) -> None:
        """Team-picker modal shown before the confirm step for multi-look skins."""
        self._variant_swatch_rects = []
        self._variant_ok_rect = None
        self._variant_cancel_rect = None
        self._variant_panel = None
        sid = self._variant_pick
        if sid is None:
            return

        from game import skin_basketball as _sb

        scrim = pygame.Surface((W, H), pygame.SRCALPHA)
        scrim.fill((4, 4, 10, 180))
        surf.blit(scrim, (0, 0))

        pw, ph = 272, 340
        panel = pygame.Rect((W - pw) // 2, (H - ph) // 2, pw, ph)
        self._variant_panel = panel
        _drop_shadow(surf, panel, 18, blur=8, alpha=170)
        surf.blit(_vgrad_panel(pw, ph, 18, (28, 24, 38), (12, 10, 22), 255),
                  panel.topleft)
        pygame.draw.rect(surf, lerp_color(_GOLD_BRIGHT, NEAR_BLACK, 0.45), panel,
                         width=2, border_radius=18)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 230), panel.inflate(-2, -2),
                         width=1, border_radius=16)

        cx = panel.centerx
        head = _font(13, True).render("CHOOSE YOUR TEAM", True, _GOLD_PALE)
        surf.blit(head, head.get_rect(center=(cx, panel.y + 22)))
        _gold_rule(surf, panel.x + 28, panel.right - 28, panel.y + 38)

        # 2×2 swatch grid
        sw, sh = 112, 72
        gutter = 10
        gx0 = cx - sw - gutter // 2
        gx1 = cx + gutter // 2
        gy0 = panel.y + 52
        gy1 = gy0 + sh + gutter

        positions = [(gx0, gy0), (gx1, gy0), (gx0, gy1), (gx1, gy1)]
        for i, (bx, by) in enumerate(positions):
            rect = pygame.Rect(bx, by, sw, sh)
            self._variant_swatch_rects.append(rect)
            col  = _sb.VARIANT_JERSEY[i]
            trim = _sb.VARIANT_TRIM[i]
            name = _sb.VARIANT_NAMES[i]
            num  = _sb.VARIANT_NUMBER[i]

            # Background fill
            surf.blit(_vgrad_panel(sw, sh, 8,
                                   lerp_color(col, (255, 255, 255), 0.18),
                                   lerp_color(col, (0,   0,   0),   0.35)),
                      rect.topleft)

            # Border — gold + thick if selected, dim otherwise
            if i == self._variant_choice:
                pygame.draw.rect(surf, _GOLD_BRIGHT, rect, width=3, border_radius=8)
                pygame.draw.rect(surf, (*_GOLD_BRIGHT, 120),
                                 rect.inflate(4, 4), width=2, border_radius=10)
            else:
                pygame.draw.rect(surf, lerp_color(col, (200, 200, 220), 0.4),
                                 rect, width=1, border_radius=8)

            # Jersey number swatch (small coloured rectangle)
            num_col = trim
            nf = _font(22, True)
            nt = nf.render(num, True, num_col)
            nt.set_alpha(200)
            surf.blit(nt, nt.get_rect(center=(rect.x + 22, rect.centery)))

            # Team name
            tf = _font(11, True)
            tt = tf.render(name, True, trim)
            surf.blit(tt, tt.get_rect(midleft=(rect.x + 38, rect.centery - 8)))

            # Sub-label: "LAKER" / "BULL" etc. (shorter, dimmer)
            sub = name.replace("THE ", "")
            sf = _font(10, False)
            st2 = sf.render(sub, True, lerp_color(trim, (180, 170, 190), 0.45))
            surf.blit(st2, st2.get_rect(midleft=(rect.x + 38, rect.centery + 8)))

        # CANCEL / SELECT buttons
        bw, bh, bgutter = 100, 38, 16
        bby = panel.bottom - 30
        nx = cx - (bw * 2 + bgutter) // 2
        cancel = pygame.Rect(nx, bby - bh // 2, bw, bh)
        ok     = pygame.Rect(nx + bw + bgutter, bby - bh // 2, bw, bh)

        surf.blit(_vgrad_panel(bw, bh, bh // 2, (70, 62, 80), (44, 38, 56)),
                  cancel.topleft)
        pygame.draw.rect(surf, (126, 116, 138), cancel, width=1,
                         border_radius=bh // 2)
        ct = _font(14, True).render("CANCEL", True, UI_CREAM)
        surf.blit(ct, ct.get_rect(center=cancel.center))
        self._variant_cancel_rect = cancel

        bglow = pygame.Surface((bw + 10, bh + 10), pygame.SRCALPHA)
        for k in range(4, 0, -1):
            pygame.draw.rect(bglow, (255, 200, 80, int(22 * k / 4)),
                             (5 - k, 5 - k, bw + 2 * k, bh + 2 * k),
                             border_radius=bh // 2 + k)
        surf.blit(bglow, (ok.x - 5, ok.y - 5), special_flags=pygame.BLEND_ADD)
        surf.blit(_vgrad_panel(bw, bh, bh // 2,
                               lerp_color(_GOLD_BRIGHT, WHITE, 0.2), _GOLD_DEEP),
                  ok.topleft)
        pygame.draw.rect(surf, _GOLD_PALE, ok, width=1, border_radius=bh // 2)
        yt = _font(14, True).render("SELECT  ▶", True, (40, 24, 8))
        surf.blit(yt, yt.get_rect(center=ok.center))
        self._variant_ok_rect = ok

    def _handle_variant_tap(self, pos) -> None:
        if pos is None:
            self._variant_pick = None
            return None
        # Tap a swatch → update selection
        for i, rect in enumerate(self._variant_swatch_rects):
            if rect.collidepoint(pos):
                self._variant_choice = i
                return None
        if self._variant_ok_rect and self._variant_ok_rect.collidepoint(pos):
            # Advance to the standard confirm modal with the chosen variant
            self._confirm = self._variant_pick
            self._variant_pick = None
            return None
        if self._variant_cancel_rect and self._variant_cancel_rect.collidepoint(pos):
            self._variant_pick = None
            return None
        # Tap outside the panel dismisses
        if self._variant_panel and not self._variant_panel.collidepoint(pos):
            self._variant_pick = None
        return None

    def _draw_confirm(self, surf) -> None:
        """Buy-confirmation modal: scrim + fig-E halo-badge popup — overhanging
        cabochon disc with spotlight halo, corner gem pair, name above rarity
        banner, tier-coloured CONFIRM pill, muted CANCEL pill below."""
        self._confirm_panel = None
        self.confirm_yes_rect = self.confirm_no_rect = None
        sid = self._confirm
        if sid is None:
            return

        scrim = pygame.Surface((W, H), pygame.SRCALPHA)
        scrim.fill((4, 4, 10, 180))
        surf.blit(scrim, (0, 0))

        secret = store_catalog.is_secret(sid) and not store_data.is_owned(sid)
        tier = store_catalog.rarity(sid)
        pal = (store_cards.MYSTERY if secret
               else store_cards.RARITY.get(tier, store_cards.RARITY["common"]))
        tier_word = "MYSTERY" if secret else tier.upper()
        name = "???" if secret else self._disp_name(sid)
        price = store_catalog.cost(sid)

        # Popup metrics (logical px, SS=2 double-res surface).
        POP_W, POP_H = 260, 442
        CX = POP_W // 2
        SS = store_cards.SS
        m = store_cards.m

        design = store_design.DESIGN     # None = "classic"
        CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 10, 240, 127, 299, 23
        R_HERO, DISC_CY = 53, 135
        GEM_R, GEM_CY = 14, 152
        # base/chosen tuck the corner gems to the frame
        GEM_L_X, GEM_R_X = (35, 225) if design else (43, 217)
        NAME_FS, Y_NAME = 45, (store_design.NAME_ZONE_C if design else 213)
        Y_BANNER, BANNER_W, BANNER_H = 402, 140, 23
        affordable = store_data.balance() >= price
        SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
        CHIP_CY = 247
        BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
        BUY_CX = CX - (BTN_W + BTN_GAP) // 2
        CAN_CX = CX + (BTN_W + BTN_GAP) // 2
        _hair_pos = [None]

        big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

        # ── card body ─────────────────────────────────────────────────────────
        rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
        rad = m(CARD_RAD)
        store_cards.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
        big.blit(store_cards.vgrad_stops(
            rect.w, rect.h, rad,
            [(0.0, store_cards.CARD_T), (1.0, store_cards.CARD_B)], 255, gamma=1.15),
            rect.topleft)
        store_cards.top_sheen(big, rect, rad, m(30), peak=56)
        pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
        if design is None:
            # stock ring + tray hairline; base/chosen draw their own frame
            # AFTER the shelf so its full perimeter survives (see below)
            store_cards.bevel_rim(big, rect, rad, store_cards.CARD_RING_DEEP,
                                  (*store_cards.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
            tray = rect.inflate(-m(8), -m(8))
            pygame.draw.rect(big, (*store_cards.CARD_RING_BRIGHT, 55), tray,
                             width=max(1, m(1)), border_radius=rad - m(3))
        else:
            # B5 constellation-web behind gems/name/hero, clipped to the body
            design["bg_hook"](big)

        # ── corner gem pair ───────────────────────────────────────────────────
        store_cards.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                              pal["gem"], pal["deep"])
        store_cards.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                              pal["gem"], pal["deep"])

        # ── name (above banner): shrink to floor, wrap to 2 lines if needed ──
        _MIN_FS = 24
        _nfs    = NAME_FS
        _nfnt   = store_cards.font(_nfs)
        _mw     = m(CARD_W - 20)
        while store_cards._glyph_base(name, _nfnt, 0).get_width() > _mw and _nfs > _MIN_FS:
            _nfs -= 1
            _nfnt = store_cards.font(_nfs)
        if store_cards._glyph_base(name, _nfnt, 0).get_width() <= _mw:
            store_cards.plain_text(big, name, _nfnt,
                                   (m(CX), m(Y_NAME)), (250, 248, 240),
                                   shadow_a=160, weight=m(0.9),
                                   keyline=(6, 6, 16), kw=m(1.0))
        else:
            _words = name.split()
            _best  = max(1, len(_words) // 2)
            for _i in range(1, len(_words)):
                _a = ' '.join(_words[:_i]); _b = ' '.join(_words[_i:])
                if max(store_cards._glyph_base(_a, _nfnt, 0).get_width(),
                       store_cards._glyph_base(_b, _nfnt, 0).get_width()) <= _mw:
                    _best = _i
            _a = ' '.join(_words[:_best]); _b = ' '.join(_words[_best:])
            if design is None:
                _disc_bot_ss = m(DISC_CY + R_HERO) + m(6)
                _cy1 = _disc_bot_ss + _nfnt.get_height() // 2
            else:
                # zone-centred: the 2-line block keeps its centre at Y_NAME
                _cy1 = m(Y_NAME) - int(_nfnt.get_height() * 1.15) // 2
            _cy2 = _cy1 + int(_nfnt.get_height() * 1.15)
            store_cards.plain_text(big, _a, _nfnt,
                                   (m(CX), _cy1), (250, 248, 240),
                                   shadow_a=160, weight=m(0.9),
                                   keyline=(6, 6, 16), kw=m(1.0))
            store_cards.plain_text(big, _b, _nfnt,
                                   (m(CX), _cy2), (250, 248, 240),
                                   shadow_a=160, weight=m(0.9),
                                   keyline=(6, 6, 16), kw=m(1.0))
            Y_BANNER = max(Y_BANNER,
                           (_cy2 + _nfnt.get_height() // 2) // SS + 10 + BANNER_H // 2)

        # (rarity banner drawn after the shelf — FINAL_SPEC draw-order fix)

        # ── shelf + action helpers ─────────────────────────────────────────────
        def _padlock(surf, cx, cy, h, color):
            bw, bh = int(h * 0.92), int(h * 0.60)
            body = pygame.Rect(0, 0, bw, bh)
            body.center = (cx, cy + int(h * 0.20))
            pygame.draw.rect(surf, color, body,
                             border_radius=max(1, int(h * 0.14)))
            sr = int(h * 0.30)
            arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
            pygame.draw.arc(surf, color, arc,
                            math.radians(15), math.radians(165),
                            max(1, int(h * 0.17)))
            kh = pygame.Rect(0, 0,
                             max(1, int(h * 0.16)), max(1, int(h * 0.22)))
            kh.center = (cx, body.centery + int(h * 0.02))
            pygame.draw.rect(surf, (10, 14, 26), kh, border_radius=1)

        def _btn(rect, label, locked=False, is_cancel=False):
            rad = m(BTN_RAD)
            if locked:
                stops   = [(0.0, (58, 60, 74)), (1.0, (40, 42, 54))]
                lab_col = (150, 152, 162)
                sheen   = 10
            elif is_cancel:
                stops   = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
                lab_col = (150, 155, 200)
                sheen   = 14
            else:
                stops   = [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))]
                lab_col = (200, 205, 240)
                sheen   = 22
            store_cards.drop_shadow(big, rect, rad, blur=m(3), alpha=100, dy=m(2))
            big.blit(store_cards.vgrad_stops(rect.w, rect.h, rad, stops, 255),
                     rect.topleft)
            store_cards.top_sheen(big, rect, rad, m(12), peak=sheen)
            if locked:
                store_cards.bevel_rim(big, rect, rad, (20, 18, 36, 180),
                                      (130, 124, 160, 200), w=max(1, m(1.2)))
            else:
                rim_w = m(2.2) if is_cancel else m(2.0)
                store_cards.bevel_rim(big, rect, rad, store_cards.CARD_RING_DEEP,
                                      (*store_cards.CARD_RING_BRIGHT, 230),
                                      w=max(1, rim_w))
            font_px  = 13 if is_cancel else 14
            lab_font = store_cards.font(font_px)
            if locked:
                lw     = lab_font.size(label)[0]
                lock_h = m(11)
                lock_w = int(lock_h * 0.92)
                inner  = m(4)
                grp    = lock_w + inner + lw
                gx     = rect.centerx - grp // 2
                _padlock(big, gx + lock_w // 2, rect.centery, lock_h, lab_col)
                store_cards.plain_text(big, label, lab_font,
                                       (gx + lock_w + inner + lw // 2, rect.centery),
                                       lab_col, shadow_a=0, weight=m(0.6))
            else:
                store_cards.plain_text(big, label, lab_font, rect.center, lab_col,
                                       shadow_a=110, weight=m(0.8),
                                       keyline=(8, 6, 20), kw=m(0.9))

        def _chip(cx, cy):
            CHIP_W, CHIP_H, CHIP_RAD = 88, 26, 8
            chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
            chip.center = (cx, cy)
            crad = m(CHIP_RAD)
            store_cards.drop_shadow(big, chip, crad, blur=m(3), alpha=80, dy=m(2))
            face_stops = ([(0.0, (40, 42, 74)), (1.0, (26, 28, 54))] if affordable
                          else [(0.0, (40, 42, 62)), (1.0, (28, 28, 46))])
            big.blit(store_cards.vgrad_stops(chip.w, chip.h, crad, face_stops, 255),
                     chip.topleft)
            store_cards.top_sheen(big, chip, crad, m(9), peak=30 if affordable else 14)
            if affordable:
                store_cards.bevel_rim(big, chip, crad, store_cards.CARD_RING_DEEP,
                                      (*store_cards.CARD_RING_BRIGHT, 200),
                                      w=max(1, m(1.4)))
            else:
                store_cards.bevel_rim(big, chip, crad, (44, 58, 58, 200),
                                      (110, 130, 130, 160), w=max(1, m(1.2)))
            txt      = f"{price:,}"
            num_font = store_cards.font(18)
            coin_r   = m(11)
            gap      = m(4)
            num_w    = num_font.size(txt)[0]
            total    = coin_r * 2 + gap + num_w
            left     = cx - total // 2
            coin_cx  = left + coin_r
            num_cx   = left + coin_r * 2 + gap + num_w // 2
            if affordable:
                store_cards.coin_glyph(big, coin_cx, cy, coin_r)
                num_col  = (236, 240, 232)
                hy_ss    = (cy + num_font.get_ascent() - num_font.size(txt)[1] // 2 + m(3)) / SS
                x0_ss    = (num_cx - num_w // 2) / SS
                x1_ss    = (num_cx + num_w // 2) / SS
                _hair_pos[0] = (x0_ss, x1_ss, hy_ss)
            else:
                pygame.draw.circle(big, (120, 122, 138), (coin_cx, cy), coin_r)
                num_col = (140, 144, 152)
            store_cards.plain_text(big, txt, num_font, (num_cx, cy + m(1)), num_col,
                                   shadow_a=0, weight=m(0.7))

        # ── shelf ─────────────────────────────────────────────────────────────
        shelf_rect  = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
        shelf_rad   = m(CARD_RAD)
        shelf_stops = ([(0.0, (34, 36, 72)), (0.5, (22, 24, 54)), (1.0, (12, 14, 36))] if affordable
                       else [(0.0, (32, 34, 56)), (0.5, (22, 22, 44)), (1.0, (12, 12, 30))])
        shelf = store_cards.vgrad_stops(
            shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
        smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                         border_bottom_left_radius=shelf_rad,
                         border_bottom_right_radius=shelf_rad)
        shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        store_cards.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
        lip = (115, 106, 140) if affordable else (62, 62, 86)
        pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
        seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
        for _yy in range(m(6)):
            _a = int(120 * (1 - _yy / m(6)))
            pygame.draw.line(seat, (0, 0, 0, _a), (0, _yy), (shelf_rect.w - 1, _yy))
        big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
        big.blit(shelf, shelf_rect.topleft)
        wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
        if wall_draw_h > 0:
            wall_w = m(SHELF_X - CARD_X)
            for _col_fn, _bx in [
                (lambda xx: (130, 120, 165, int(50 * xx / max(1, wall_w - 1))),
                 m(CARD_X)),
                (lambda xx: (0, 0, 0, int(50 * (1 - xx / max(1, wall_w - 1)))),
                 m(SHELF_X + SHELF_W)),
            ]:
                _wall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
                for _xx in range(wall_w):
                    pygame.draw.line(_wall, _col_fn(_xx),
                                     (_xx, 0), (_xx, wall_draw_h - 1))
                big.blit(_wall, (_bx, m(SHELF_Y)))

        if design is not None:
            # the design perimeter lands after the shelf/walls so its full
            # outline survives them
            design["frame_hook"](big, rect, rad)

        # ── price chip + buy / cancel buttons ─────────────────────────────────
        if design is None:
            _chip(m(CX), m(CHIP_CY))
            buy_r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
            buy_r.center = (m(BUY_CX), m(BTN_CY))
            can_r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
            can_r.center = (m(CAN_CX), m(BTN_CY))
            _btn(buy_r, "BUY", locked=not affordable)
            _btn(can_r, "CANCEL", is_cancel=True)
        else:
            store_design.draw_bullion_chip(big, price,
                                           store_design.chip_cy(name))
            design["buttons"](big, affordable=affordable)

        # ── bottom gem pair (drawn on top of shelf) ───────────────────────────
        # gems keep their tier colour regardless of balance — only the BUY
        # button carries the can't-afford signal
        BOT_GEM_CY = 402
        for _gx in [m(GEM_L_X), m(GEM_R_X)]:
            store_cards._alpha_aura(big, _gx, m(BOT_GEM_CY), m(16),
                                    pal["glow"], peak=60, layers=14)
            store_cards.facet_gem(big, _gx, m(BOT_GEM_CY), m(GEM_R),
                                  pal["gem"], pal["deep"])

        # ── overhanging disc + spotlight halo (crowns the card) ───────────────
        cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
        _aura = (store_design.smooth_aura if design is not None
                 else store_cards._alpha_aura)
        _aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"],
              peak=95, layers=24)
        _aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"],
              peak=70, layers=12)
        store_cards.cabochon(big, cx_ss, cy_ss, r_ss,
                             store_cards.CABO_LO, store_cards.CABO_HI,
                             ring=pal["gem"], ring_a=50)
        if secret:
            _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK,
                        thick=5)
        else:
            store_cards.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
        store_cards.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])
        if design is not None:
            store_design.hero_circle(big, cx_ss, cy_ss, r_ss, design["ring"])

        # ── rarity banner (topmost, above the shelf — FINAL_SPEC fix) ────────
        _confirm_tier_banner(big, CX, Y_BANNER, BANNER_W, BANNER_H, tier_word, pal)

        # ── downscale and composite onto screen ───────────────────────────────
        pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
        if affordable and _hair_pos[0] is not None:
            x0, x1, hy = _hair_pos[0]
            pygame.draw.line(pop, store_cards.CARD_RING_BRIGHT,
                             (int(round(x0)), int(round(hy))),
                             (int(round(x1)), int(round(hy))), 1)
        px = (W - POP_W) // 2
        py = 40
        self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
        surf.blit(pop, (px, py))

        # Hit rects in screen space (logical coords map 1:1 post-downscale).
        _hit_h = 42 if design is not None else BTN_H   # design buttons are taller
        self.confirm_yes_rect = pygame.Rect(
            px + BUY_CX - BTN_W // 2, py + BTN_CY - _hit_h // 2,
            BTN_W, _hit_h)
        self.confirm_no_rect = pygame.Rect(
            px + CAN_CX - BTN_W // 2, py + BTN_CY - _hit_h // 2,
            BTN_W, _hit_h)

    # ── input ────────────────────────────────────────────────────────────────
    def handle_tap(self, pos) -> "str | None":
        # While the buy-confirmation is up it is modal: only its own buttons
        # (and a tap on the scrim, which cancels) are hit-testable.
        if self._variant_pick is not None:
            return self._handle_variant_tap(pos)
        if self._confirm is not None:
            return self._handle_confirm_tap(pos)
        # Device back / escape steps OUT one level: category -> hub -> exit store.
        if pos is None:
            if self.view == "category":
                self.view = "hub"
                return None
            return "back"
        if self.view == "hub":
            return self._handle_hub_tap(pos)
        # BACK from a category returns to the hub, not all the way out, so the
        # lagoon stays the store's home.
        if self.back_rect and self.back_rect.collidepoint(pos):
            self.view = "hub"
            return None
        if self.tab_chev_l and self.tab_chev_l.collidepoint(pos):
            self.tab_scroll = max(0.0, self.tab_scroll - self._tab_vp.width * 0.6)
            return None
        if self.tab_chev_r and self.tab_chev_r.collidepoint(pos):
            self.tab_scroll += self._tab_vp.width * 0.6
            return None
        for i, r in enumerate(self.tab_rects):
            # Only count taps inside the viewport so a pill peeking under a
            # chevron isn't selectable by its hidden edge.
            if r.collidepoint(pos) and self._tab_vp.collidepoint(pos):
                if i != self.tab:
                    self.tab = i
                    self.page = 0  # each tab starts at its first page
                    self._scroll_tab_into_view(i)
                return None
        if self.prev_rect and self.prev_rect.collidepoint(pos):
            self.prev_rect = self.next_rect = None  # consume rects so a same-frame echo can't re-fire
            self.page = max(0, self.page - 1)
            return None
        if self.next_rect and self.next_rect.collidepoint(pos):
            self.prev_rect = self.next_rect = None  # consume rects so a same-frame echo can't re-fire
            self.page = min(self.n_pages - 1, self.page + 1)
            return None
        for sid, rect in self.item_rects.items():
            if rect.collidepoint(pos):
                self._tap_item(sid)
                return None
        return None

    def _handle_hub_tap(self, pos) -> "str | None":
        # On the lagoon hub BACK exits the store; a stall drills into its
        # category. The hub may not be built yet on a stray first-frame tap.
        if self.back_rect and self.back_rect.collidepoint(pos):
            return "back"
        if self.hub is None:
            return None
        for group, r in self.hub.stall_rects.items():
            if r.collidepoint(pos):
                # Shut stalls (bamboo blind) are inert: a tap is a silent no-op,
                # never routing into the category or flashing a message.
                if group in self.hub.CLOSED_GROUPS:
                    return None
                self.tab = _GROUP_TAB[group]
                self.page = 0  # each category opens on its first page
                self._scroll_tab_into_view(self.tab)
                self.view = "category"
                return None
        return None

    def _tap_item(self, sid: str) -> None:
        if store_data.equipped(_slot_of(sid)) == sid:
            return  # already worn
        if store_data.is_owned(sid):
            # Equipping a look already owned is free + reversible, so it stays a
            # one-tap action; only a coin-spending purchase needs confirming.
            store_data.equip(sid)
            store_cards.clear_cache()  # EQUIPPED state moved between two cards
            self._flash(self._disp_name(sid) + " EQUIPPED")
            return
        # Unowned: multi-variant skins show a team picker first.
        if sid == "skin_basketball":
            self._variant_pick = sid
            self._variant_choice = 0
            return
        self._confirm = sid

    def _handle_confirm_tap(self, pos) -> None:
        if pos is None:                       # device back / escape cancels
            self._confirm = None
            return None
        if self.confirm_yes_rect and self.confirm_yes_rect.collidepoint(pos):
            self._commit_purchase()
            return None
        if self.confirm_no_rect and self.confirm_no_rect.collidepoint(pos):
            self._confirm = None
            return None
        # A tap on the dimmed scrim (outside the panel) dismisses; a tap inside
        # the panel that misses both buttons is ignored.
        if self._confirm_panel and not self._confirm_panel.collidepoint(pos):
            self._confirm = None
        return None

    def _commit_purchase(self) -> None:
        sid, self._confirm = self._confirm, None
        if sid is None:
            return
        ok, reason = store_data.try_purchase(sid)
        if ok:
            # Auto-equip a fresh unlock so the player immediately sees their
            # new bird — the satisfying payoff of the purchase.
            store_data.equip(sid)
            if sid == "skin_jet_fighter":
                # Bind the preview to the design just rolled for this unlock so
                # the card shows the actual jet, not a stale lazy default.
                from game import animal_jet_fighter
                animal_jet_fighter.sync_from_store()
            if sid == "parcel_whiskey":
                # Same: bind the mystery whiskey to the dram just rolled.
                from game import parcel_whiskey
                parcel_whiskey.sync_from_store()
            elif sid == "skin_sun":
                # Bind the preview to the sun design just rolled at this unlock.
                from game import animal_sun
                animal_sun.sync_from_store()
            elif sid == "skin_basketball":
                from game import skin_basketball
                store_data.set_skin_variant(sid, self._variant_choice)
                skin_basketball.sync_from_store()
            # Ownership + balance + EQUIPPED all changed: rebuild the cards (this
            # one reveals if it was a masked secret, and now reads EQUIPPED).
            store_cards.clear_cache()
            self._flash("UNLOCKED!  " + self._disp_name(sid))
        elif reason == "insufficient":
            self._flash("NEED MORE COINS")

