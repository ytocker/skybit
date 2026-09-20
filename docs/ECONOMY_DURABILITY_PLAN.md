# Skybit — Economy Durability Implementation Plan

**As of 2026-09-20 · branch `app_wrapup`**

`WRAPUP_STATUS.md` says *what* is broken. This says *how* to fix it.

---

## The goal

A player opens the link, plays, earns coins, buys a skin, closes the tab. Weeks later they
open the same link and their balance, their purchases and their achievements are still
there — having never signed up, never been prompted, never been asked to remember
anything.

Three decisions frame everything below:

| Decision | Choice |
|---|---|
| Backend | **All-Supabase** — Edge Function + Postgres |
| Staging | **PoC first**, durability after |
| Scope | **One unified player record** — coins, purchases, equips, achievements |

---

## The one idea

A wallet integer **cannot be merged**. Coins go up and down, so when two copies disagree
there is no rule that recovers the truth: take the higher and a purchase was free, take the
lower and the earnings vanish, take the newer and it depends on clock skew.

Store two monotonic counters instead, and derive:

```
earned  += n          on every credit      # only ever grows
spent   += n          on every debit       # only ever grows
wallet   = max(0, earned - spent)
```

Both inputs only increase, so merging is element-wise maximum and re-derive. That single
change makes the whole record reconcilable — offline play, two open tabs, native desktop,
and the one-time migration all resolve correctly without losing or duplicating a coin.

This is exactly the idea already sketched in `achievements.coin_balance`. **Adopt the idea,
delete that code** — see Phase 2.

---

## Phase 1 — PoC

**Goal: the economy loop is playable. ~20 lines. Ships alone, needs no domain, no endpoint,
no schema change.**

### 1a. The missing bridge cases

`inject_theme.py` — `store_data` already calls `sk("store_load")` and `sk("store_save")`,
but the dispatcher implements neither and falls through to `default: return null`. Every
purchase is wiped on reload.

Add a `STORE_KEY = 'skybit_store'` constant and `storeLoad` / `storeSave`, cloned from the
`achLoad` / `achSave` pair directly above them — the synchronous localStorage pattern, not
the async Supabase one. Then two dispatcher cases beside the existing `ach_*` arms.

Update the authoritative action list in the module docstring at the top of the file.

**The Python side needs no change.** It already speaks this protocol correctly.

### 1b. The load/save hazard — do this *before* 1c

`game/store_data.py`: `_load_web` returns `_default_state()` on *any* failure, and `load()`
caches whatever it gets for the rest of the session. So one transient read failure, plus the
next write, silently persists zeros over a real wallet.

It's dormant only because nothing currently calls the mutation path. **The faucet in 1c is
what arms it**, so the guard lands first.

Change `_load_web` and `_load_native` to return `None` on failure. `load()` assigns
`_STATE` only on success. `save()` already no-ops when `_STATE is None` — that *is* the
guard. A failed read then simply retries on the next `_ensure()`.

Distinguish carefully:
- bridge returned an empty string → genuinely new player → defaults, cache them
- bridge threw, or is absent → failure → `None`, retry later

### 1c. The coin faucet

`game/scenes.py`, in `_on_death`. Bank once per run, after the `achievements.evaluate_run`
block and before `self._stats_t = 0.0`, inside the existing `demo is None` guard and a
try/except:

```
store_data.add_coins(getattr(self.world, "coin_count", 0) or 0)
```

- **After `evaluate_run`** so coin-count achievements still see an untouched run.
- **Not** in `world.py` where `coin_count` increments — that's the hot path, and banking
  there means a storage write per coin.
- **Not** gated on the plausibility check, which lives on the leaderboard submit path.
  These coins buy cosmetics for yourself; gating would silently zero legitimate runs.
- **1:1 with `coin_count`.** The HUD shows a coin count during the run; any other rate
  reads as a bug. Tune through catalog prices, never a hidden multiplier.

Double-banking is already structurally prevented — `_on_death` fires once on the
`game_over` transition and immediately leaves `STATE_PLAY`, and `_restart()` builds a fresh
`World()`. Add a `_coins_banked` flag on the world anyway as cheap insurance.

### 1d. The daily reward

`claim_daily()` and `DAILY_REWARD = 75` exist and are tested, but nothing calls them.

Claim once per app start rather than per run, and show a "+75" toast on the title screen so
the grant is visible. A silent credit teaches the player nothing. Add a pip on the STORE
button when `daily_available()`.

Note it keys off local `time.strftime`, so a device clock change can re-trigger it.
Accepted — the economy is client-authoritative by decision.

### 1e. Tests

Extend `tests/test_store.py`, reusing its `STORE_FILE` monkeypatch + `_reset_for_test()`
setup:

- banked coins raise the balance by exactly the run's count
- `add_coins(0)` and negatives are no-ops
- `claim_daily` twice in one day grants once
- **a raising `_load_native` leaves `_STATE is None` and `save()` writes nothing** — the
  regression guard for 1b

Then add `tests/test_bridge_contract.py`: assert every action named in the `inject_theme.py`
docstring appears in the dispatcher, and vice versa. **That test alone would have caught the
shipped bug.**

### Verify Phase 1

Native first — it needs no pygbag build. Play, note the HUD coin count, die, open the
store, confirm the balance rose by exactly that, buy a skin, relaunch, confirm it persisted
to `skybit_store.json`.

Then the browser, which is where the real bug was: build with pygbag, play, buy, **hard
reload**, confirm it all survived. Native passing proves nothing here.

---

## Phase 2 — the unified record

**Goal: one record, one save path, still entirely local. No network change.**

### Wrap, don't replace

`store_data` has 34 production call sites across `store.py`, `store_cards.py`,
`wardrobe_screen.py`, `scenes.py` and four skin modules. Renaming them buys nothing and
risks a lot.

**Keep every public API exactly as it is.** Only the bottom changes — `_load_web`,
`_save_web`, `_load_native`, `_save_native` delegate to a new layer. Same for
`achievements`.

### Two new modules

- **`game/player_state.py`** — the envelope: shape, defaults, and a pure `merge(a, b)`.
  No I/O at all, which is what makes it trivially testable.
- **`game/player_store.py`** — the adapter: `read() -> dict | None`, `write(env) -> None`,
  and `async sync() -> None`.

### The envelope

```json
{
  "v": 2,
  "pid": "<uuid or empty>",
  "mtime": 1758300000.0,
  "store": {
    "earned": 0, "spent": 0,
    "owned": [],
    "equipped_skin": "...", "equipped_pillar": null, "equipped_ground": null,
    "equipped_trail": null, "equipped_parcel": "...",
    "last_daily": "", "skin_variants": {}
  },
  "ach": { "badges": {}, "life": {}, "mtime": 0 }
}
```

`wallet` is gone as stored state — it is derived from `earned - spent`.

### Settings stay out

`game/prefs.py` is untouched. Mute is a property of the *device* — a phone on silent and a
desktop with speakers want different answers — and losing it costs the player nothing.
Syncing it would produce surprising behaviour for no benefit. Zero work, and it's the right
call.

### Delete the dormant economy API

`achievements.coin_balance`, `spend_coins`, `owns`, `grant_item`, `equip` and the
`wallet` / `inventory` sections have no production callers. Leaving them means two sources
of truth for coins.

**Keep `life.total_coins`** — 99 badges depend on it.

Leave the persisted keys in existing save blobs and let the coercion ignore them; those
blobs are already live on real devices, so dropping fields risks a migration incident for
no gain.

### Promote `_merge`

`achievements._merge` is genuinely good and should not be rewritten. Move it into
`player_state` and extend it with a per-section policy:

| Field | Policy |
|---|---|
| `ach.badges` | union, earliest timestamp |
| `ach.life.*` | element-wise max |
| `store.earned`, `store.spent` | element-wise max → wallet derived |
| `store.owned` | set union — purchases are never revoked |
| `store.equipped_*`, `skin_variants` | last-write-wins by envelope `mtime` |
| `store.last_daily` | **max** of the two dates — blocks a double claim |

Merge is still needed even with one server copy: native has no server at all, the web build
plays offline and reconnects, two tabs can race, and migration reconciles three sources.

---

## Phase 3 — durability

**Goal: the record survives device storage being wiped. Blocked on the domain.**

### 3a. The domain, and the trap that makes it load-bearing

A durable cookie must be **first-party** — set by a server on the same registrable domain
as the game. Script-written storage doesn't survive; iOS Safari deletes it after seven days
without a visit, taking the player's ID with it.

Supabase Edge Functions serve from `*.supabase.co`, which is **third-party to the game
origin — the cookie would simply be dropped.** A Supabase custom domain is a $10/month
add-on on top of the $25/month Pro plan. **$35/month to do it the obvious way.**

**The free path, which this repo is already most of the way toward:** `netlify.toml`
already exists with CSP and COOP headers, and `deploy.yml` already deploys to Netlify.
Netlify gives custom domains free and supports proxy rewrites. So:

- serve the game from the domain on Netlify
- proxy `/api/*` → the Edge Function with a `status = 200` rewrite

The browser now sees a **same-origin** request, the cookie is first-party, and the existing
CSP `connect-src 'self'` already permits it. Total cost stays the ~$11/year domain.

### 3b. The Edge Function

One function, `player`.

- `GET /api/player` → `200 {pid, v, mtime, store, ach}`, or `200 {pid, new: true}` for a
  first-time visitor. **Sets and refreshes the cookie on every call**, which is what makes
  a returning player's clock restart.
- `PUT /api/player` with `{base_mtime, store, ach}` → `204`. On `base_mtime` mismatch,
  `409` carrying the current row so the client re-merges and retries once. `429` → silent
  backoff. `5xx` → keep the local copy, no user-visible failure.
- `OPTIONS` preflight, since a JSON `PUT` is not a simple request.

Cookie: `sb_pid=<uuid>.<hmac>; Path=/; Max-Age=34560000; HttpOnly; Secure; SameSite=Lax`.
HMAC-signed with a function secret so a forged pid can't read someone else's row.
`HttpOnly` also means page scripts cannot read or tamper with it.

CORS needs `Access-Control-Allow-Credentials: true` **and an explicit origin** — `*` is
illegal alongside credentials.

### 3c. The table

```sql
create table public.players (
    pid        uuid primary key,
    payload    jsonb       not null,
    updated_at timestamptz not null default now()
);
alter table public.players enable row level security;
-- No policies. Deny-all: only the function's service-role key touches this.
```

That deny-all posture is the fix for the hole the current schema comment already concedes —
that any client sharing the anon key can read or overwrite any row.

### 3d. The client

Two new bridge actions on the **async** pattern (network, 6s `AbortController` timeout),
cloned from `doProfilePull` / `doProfilePush` and polled the way `achievements._cloud_pull`
polls: `player_pull` / `player_pull_done` / `player_pull_error`, and `player_push` /
`player_push_done`.

**The `fetch` needs `credentials: 'include'`.** This codebase has never used it — every
existing call is bearer-token only — and without it the cookie is neither sent nor stored.
This is the single easiest thing to get wrong in the whole plan.

**Leaderboard and telemetry stay direct-to-Supabase.** They carry no identity, they work
today, and routing them through the function adds invocations and a new failure mode.

### 3e. Keepalive

Free Supabase projects pause after 7 days without traffic, which would silently take the
game offline. A GitHub Actions cron every few days hitting `GET /api/player` with no cookie
(a cheap `new: true`) keeps it warm. The secrets already live there.

---

## Migration

On first web boot after Phase 3, inside `player_store.sync()`:

1. `GET /api/player`. A fresh pid if `new: true`.
2. Build a local envelope from `localStorage['skybit_store']` and `['skybit_ach']`.
3. If no `skybit_migrated` flag and `skybit_device_id` exists, do **one** legacy
   `profile_pull` and include that too.
4. `merge` all three, `PUT` with `base_mtime`, set `skybit_migrated`.

**localStorage is never cleared** — it stays the offline cache and the fallback when the
function is unreachable. Nothing duplicates, because `earned` and `spent` max-merge rather
than sum, which also makes re-running the migration harmless.

Leave `profiles` readable for a soak period, then revoke anon insert/update, then drop it.

---

## Native and offline — the seam

Exactly **one** `if _IS_BROWSER`, at the bottom of `player_store.py`, binding three names:

| | Native | Web |
|---|---|---|
| `read()` | `SAVE_FILE` JSON | `sk('player_load')` |
| `write(env)` | file write | `sk('player_save')` |
| `async sync()` | no-op | pull → merge → push |

**The local write is synchronous and unconditional; the server is a background reconciler
that never sits on the hot path.** A network failure therefore cannot lose a coin.

Everything above that line — `store_data`, `achievements` — carries zero platform branches.
Delete the ones they have today.

---

## Testing without network

- **`merge` is pure** → test directly on dicts, in the style of `test_achievements.py`.
  Cover: earn and spend on two branches, `owned` union, `last_daily` max, equip LWW, and
  the three-way migration merge.
- **The adapter** → monkeypatch `read` / `write` to an in-memory dict, in the style of
  `test_store.py`. Test the native path for real against a temp path.
- **The contract** → dispatcher ⇄ docstring action parity, and assert the push body built
  by a pure `_build_push_body()` has the right shape.

**Do not build** a fake HTTP server, a JS test harness, or a Supabase emulator.

Add a dev dependency group to `pyproject.toml` — there is none today, and the CI container
has neither `pytest` nor `pygame`.

---

## Phases

| | Content | Effort | Verified by | Blocked on |
|---|---|---|---|---|
| **P1** | Bridge cases, hazard guard, faucet, daily, tests | ~½ day | Play in browser, buy, hard-reload, still there | — |
| **P2** | `player_state` + `player_store`, re-point store/achievements, earned/spent, delete dead API, promote merge | 1–2 days | Tests + native play | P1 |
| **P3** | Domain, Netlify proxy, Edge Function, `players` table, cookie, 2 bridge actions, migration, keepalive | 2–3 days | Clear site data in two browsers; balance returns | Domain, P2 |
| **P4** | Revoke `profiles` anon write, drop table | ~1 hr | — | P3 soak |

**Ordering constraints that matter:**

- **1b before 1c.** The guard goes in before the faucet, or the faucet's first write can
  zero a wallet.
- **P2 before P3.** P2's envelope *is* P3's payload. Building the endpoint first means
  designing it against a shape that doesn't exist yet.
- **The domain blocks only P3.** Buy it early — it has lead time — but P1 and P2 deliver a
  working, playable economy without it.

---

## Not worth building

- **Server-side coin validation** — re-implementing the anti-cheat chain server-side, in a
  second language, to stop someone granting themselves a cosmetic on their own screen. The
  written trigger to revisit is in-app purchases.
- **Accounts, logins, or link codes** — ruled out by decision.
- **Cross-device settings sync** — mute is per-device by design.
- **Leaderboard/telemetry behind the function** — they carry no identity and work today.
- **A conflict-resolution UI** — the merge is deterministic; the player never sees it.
- **An offline write queue** beyond localStorage-as-cache.
- **Supabase Auth anonymous sessions.** Tempting, and wrong here: the session JWT lives in
  localStorage, which is precisely the seven-day purge the cookie exists to dodge.

---

## Verification, end to end

Desktop Chrome will pass almost anything you build — its storage is never evicted, so it
proves nothing about durability. Test where it actually fails:

1. **Economy loop, browser.** Play → die → store shows the new balance → buy → equip →
   hard reload → everything intact.
2. **Cookie.** Present, `HttpOnly`, `Secure`, unreadable from the console, and its expiry
   moves forward on each visit.
3. **Storage wipe.** Clear localStorage/IndexedDB but keep cookies, reload — the record
   comes back from the server. This is the Safari-purge simulation and the core test of the
   whole design.
4. **iOS Safari, for real.** Play, leave more than seven days, return. The one test that
   can't be shortcut.
5. **Cold start.** A browser with no cookie gets a fresh pid and a clean record — and a
   browser *with* one never gets a fresh pid by accident. Silently minting a second id for
   an existing player is the failure that looks exactly like data loss.
6. **Conflict.** Two tabs, both buy different items, both push. Both items are owned
   afterwards and coins are deducted once each.
7. **Offline.** Kill the network mid-session, earn and spend, restore it. Nothing is lost
   and nothing double-counts.
8. **Native.** Unaffected throughout — `python main.py` still works with no network.
