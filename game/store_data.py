"""Persistent wallet + inventory for the coin Store.

Native play:  reads/writes a local JSON file (STORE_FILE from config).
Browser (emscripten): delegates to the closure-private ``window.__sk``
              dispatcher injected by inject_theme.py, using the synchronous
              ``store_load`` / ``store_save`` actions (localStorage is
              synchronous, so unlike the leaderboard fetch there is no
              ``*_done`` poll loop).

Cosmetics are device-local and carry no competitive weight, so — unlike
the leaderboard — the wallet is client-trusted on both targets and needs
no proof bundle or plausibility gate.

State is cached in a module-level dict and written through on every
mutation, so the hot path (rendering the store, banking coins at death)
never blocks on a per-call file/bridge round-trip beyond the initial load.
"""
from __future__ import annotations

import sys
import json
import time
import random

from game.config import STORE_FILE
from game import store_catalog

_IS_BROWSER = sys.platform == "emscripten"

_VERSION = 1

# Equip slots map one-to-one onto the cosmetic ``kind``s that can be worn.
# Boosts are consumables, not equippable, so they have no slot here.
_EQUIP_SLOTS = ("skin", "pillar", "ground", "trail", "parcel")

_STATE: "dict | None" = None  # lazy: populated on first load()


def _default_state() -> dict:
    return {
        "version": _VERSION,
        "wallet": 0,
        "owned": [],
        "equipped_skin": store_catalog.BASE_SKIN,
        "equipped_pillar": None,
        "equipped_ground": None,
        "equipped_trail": None,
        "equipped_parcel": store_catalog.PARCEL_BASE,
        "last_daily": "",
        # skin_id -> design index, for skins whose look is a random 1-of-N
        # pick locked at unlock (e.g. the secret jet fighter).
        "skin_variants": {},
    }


def _coerce(raw: "dict | None") -> dict:
    """Merge a loaded dict onto fresh defaults so a state written by an
    older build (missing keys) or a partially-corrupt file degrades to
    sane values rather than KeyError-ing the store open."""
    state = _default_state()
    if isinstance(raw, dict):
        try:
            state["wallet"] = max(0, int(raw.get("wallet", 0)))
        except (TypeError, ValueError):
            pass
        owned = raw.get("owned", [])
        if isinstance(owned, list):
            # Drop ids no longer in the catalog so a renamed item can't
            # leave a dangling entry that looks owned but can't be equipped.
            state["owned"] = [str(i) for i in owned if store_catalog.exists(str(i))]
        for key in ("equipped_skin", "equipped_pillar", "equipped_ground",
                    "equipped_trail", "equipped_parcel"):
            v = raw.get(key)
            if v is None:
                continue
            v = str(v)
            # Guard against a stale equip pointing at a skin removed/renamed in
            # a later build: fall back to the slot default so the store never
            # shows the wrong card as "equipped" while the renderer silently
            # draws the base look. (The base skin / base parcel are always valid.)
            if v not in (store_catalog.BASE_SKIN, store_catalog.PARCEL_BASE) \
                    and not store_catalog.exists(v):
                continue
            state[key] = v
        if isinstance(raw.get("last_daily"), str):
            state["last_daily"] = raw["last_daily"]
        variants = raw.get("skin_variants")
        if isinstance(variants, dict):
            for k, v in variants.items():
                k = str(k)
                if not store_catalog.exists(k):
                    continue  # drop a roll for a renamed/removed skin
                try:
                    state["skin_variants"][k] = int(v)
                except (TypeError, ValueError):
                    pass
    return state


# ── Native local-JSON helpers (mirror leaderboard._load_local/_save_local) ────

def _load_native() -> dict:
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return _coerce(json.load(f))
    except Exception:
        return _default_state()


def _save_native(state: dict) -> None:
    try:
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


# ── Browser bridge helpers ────────────────────────────────────────────────────

def _bridge():
    """Return a callable ``window.__sk`` if the JS bridge has booted, else
    None. Same getattr-based probe as leaderboard._resolve — never raises."""
    try:
        import platform as _pgb  # type: ignore
        win = getattr(_pgb, "window", None)
        if win is None:
            return None
        return getattr(win, "__sk", None)
    except Exception:
        return None


def _load_web() -> dict:
    sk = _bridge()
    if sk is None:
        return _default_state()
    try:
        raw = sk("store_load")
        if not raw:
            return _default_state()
        return _coerce(json.loads(str(raw)))
    except Exception:
        return _default_state()


def _save_web(state: dict) -> None:
    sk = _bridge()
    if sk is None:
        return  # bridge not ready: keep the in-memory wallet, retry next save
    try:
        sk("store_save", json.dumps(state, separators=(",", ":")))
    except Exception:
        pass


# ── Public API ────────────────────────────────────────────────────────────────

def load() -> None:
    """Populate the module cache. Idempotent — repeated calls are no-ops
    once loaded so callers can ``load()`` defensively before any read."""
    global _STATE
    if _STATE is not None:
        return
    _STATE = _load_web() if _IS_BROWSER else _load_native()


def save() -> None:
    if _STATE is None:
        return
    if _IS_BROWSER:
        _save_web(_STATE)
    else:
        _save_native(_STATE)


def _ensure() -> dict:
    if _STATE is None:
        load()
    return _STATE  # type: ignore[return-value]


def balance() -> int:
    return int(_ensure()["wallet"])


def add_coins(n: int) -> None:
    """Bank coins earned in a run. Negative/zero is ignored so a stray call
    can't drain the wallet — spending goes through try_spend/try_purchase."""
    n = int(n)
    if n <= 0:
        return
    st = _ensure()
    st["wallet"] = int(st["wallet"]) + n
    save()


def is_owned(item_id: str) -> bool:
    if item_id in (store_catalog.BASE_SKIN, store_catalog.PARCEL_BASE):
        return True
    return item_id in _ensure()["owned"]


def owned_ids() -> set:
    return set(_ensure()["owned"])


def skin_variant(item_id: str) -> "int | None":
    """The design index rolled for a random-look skin at unlock, or None if the
    skin has no rolled variant. Read by the art module to render the locked
    look (the same fighter every run)."""
    v = _ensure().get("skin_variants", {}).get(item_id)
    return None if v is None else int(v)


def set_skin_variant(item_id: str, idx: int) -> None:
    """Persist a player-chosen variant index for a skin (e.g. basketball team)."""
    st = _ensure()
    st.setdefault("skin_variants", {})[item_id] = int(idx)
    save()


def _roll_skin_variant(st: dict, item_id: str) -> None:
    """If a skin's look is a random 1-of-N pick locked at unlock, roll it once
    and persist the index. The pool size is owned by the art module, lazy-
    imported here so the wallet path stays pygame-free until an actual variant
    skin is unlocked."""
    pools = {
        "skin_jet_fighter": lambda: __import__(
            "game.animal_jet_fighter", fromlist=["POOL_SIZE"]).POOL_SIZE,
        "parcel_whiskey": lambda: __import__(
            "game.parcel_whiskey", fromlist=["POOL_SIZE"]).POOL_SIZE,
        "skin_sun": lambda: __import__(
            "game.animal_sun", fromlist=["POOL_SIZE"]).POOL_SIZE,
    }
    get_n = pools.get(item_id)
    if get_n is None:
        return
    try:
        st.setdefault("skin_variants", {})[item_id] = random.randrange(int(get_n()))
    except Exception:
        pass


def _slot_key(slot: str) -> str:
    return "equipped_skin" if slot == "skin" else "equipped_" + slot


def equipped(slot: str) -> "str | None":
    """The id worn in ``slot`` (one of _EQUIP_SLOTS). Skin defaults to the
    base parrot; the other slots default to None (= the run's procedural
    default look)."""
    return _ensure().get(_slot_key(slot))


def equip(item_id: str) -> bool:
    """Wear an owned cosmetic. Returns False (no change) if it isn't owned
    or its kind has no equip slot."""
    if not is_owned(item_id):
        return False
    if store_catalog.exists(item_id):
        k = store_catalog.kind(item_id)
    elif item_id == store_catalog.BASE_SKIN:
        k = "skin"
    elif item_id == store_catalog.PARCEL_BASE:
        k = "parcel"
    else:
        k = None
    if k not in _EQUIP_SLOTS:
        return False
    _ensure()[_slot_key(k)] = item_id
    save()
    return True


def try_purchase(item_id: str) -> "tuple[bool, str]":
    """Atomically buy a catalog item: validates it exists and is unowned and
    that the wallet covers the cost, then deducts + records ownership. Returns
    ``(ok, reason)`` where reason ∈ {"", "badid", "owned", "insufficient"}."""
    if not store_catalog.exists(item_id):
        return False, "badid"
    if is_owned(item_id):
        return False, "owned"
    st = _ensure()
    price = store_catalog.cost(item_id)
    if int(st["wallet"]) < price:
        return False, "insufficient"
    st["wallet"] = int(st["wallet"]) - price
    st["owned"].append(item_id)
    _roll_skin_variant(st, item_id)
    save()
    return True, ""


def try_spend(n: int) -> bool:
    """Deduct a raw coin amount (e.g. a Prize Machine roll) if affordable.
    Records no ownership — the caller decides what the spend buys."""
    n = int(n)
    st = _ensure()
    if n <= 0 or int(st["wallet"]) < n:
        return False
    st["wallet"] = int(st["wallet"]) - n
    save()
    return True


def grant(item_id: str) -> bool:
    """Add an item to the inventory without charging (Prize Machine win,
    daily-reward unlock). No-op if already owned or unknown."""
    if not store_catalog.exists(item_id) or is_owned(item_id):
        return False
    st = _ensure()
    st["owned"].append(item_id)
    _roll_skin_variant(st, item_id)
    save()
    return True


def claim_daily() -> int:
    """Grant the daily coin reward once per calendar day. Returns the amount
    credited (0 if already claimed today)."""
    from game.config import DAILY_REWARD
    today = time.strftime("%Y-%m-%d")
    st = _ensure()
    if st.get("last_daily") == today:
        return 0
    st["last_daily"] = today
    st["wallet"] = int(st["wallet"]) + int(DAILY_REWARD)
    save()
    return int(DAILY_REWARD)


def daily_available() -> bool:
    return _ensure().get("last_daily") != time.strftime("%Y-%m-%d")


def _reset_for_test() -> None:
    """Drop the cached state so a test can re-load from a freshly
    monkeypatched STORE_FILE. Test-only; not used by the game."""
    global _STATE
    _STATE = None
