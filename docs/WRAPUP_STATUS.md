# Skybit — Wrap-Up Status

**As of 2026-09-20 · branch `app_wrapup` (from `v5_integration`)**

The goal is to finish Skybit as two shippable products: a **public online link** and an
**app**, with **coins counted per user so the store works**.

This document is the gap list and the steps to close it. It is high level by intent — it
names what is broken, why it matters, and roughly what the fix involves. It is not an
implementation spec.

---

## The short version

Skybit is much closer to shippable than 95k LOC suggests. The game is finished, and so is
the store — catalog, UI, purchase flow, tests, all of it.

But **the store is dead on arrival**, for two small reasons:

1. **No coins ever enter the wallet.** The banking function is never called from gameplay.
2. **On the web build, the wallet doesn't persist at all.** Purchases vanish on reload.

Between them these are roughly fifteen lines of code, and they convert about eight
thousand lines of already-written, already-tested store code from dead weight into the
game's retention loop. **Nothing else in this document has that ratio. Do them first, do
them alone, and verify in a real browser before touching anything else.**

After that, three things stand between here and "shipped": real per-user identity (which
is what "coins per user" actually requires), a PWA shell, and deploy wiring.

---

## Where Skybit stands

Genuinely finished:

- **The game.** Physics, difficulty ramp, the 2-lives system, 11 power-ups with score
  gates and upgrade-replacement, the secret tier behind the genie lamp, the clown
  gauntlet, the treasure-box finale, skateboard trick detection. This is a complete game,
  not a prototype.
- **The store — everything except the money.** `game/store_data.py` (atomic purchase,
  five equip slots, skin variants), `game/store_catalog.py` (dozens of priced items),
  and the UI across `store.py`, `store_hub.py` (a procedural lagoon stilt-market),
  `store_cards.py`, `store_skins.py`, `wardrobe_screen.py`. Covered by `tests/test_store.py`.
- **Already phone-shaped.** The display is portrait 9:16, with real touch handling in
  every scene. No re-layout is needed for mobile.
- **CI discipline.** Per-branch pytest gate, minimal-source staging, and a 5 MB bundle
  ceiling that the build currently clears by a wide margin.
- **Telemetry and analytics.** Per-run logging to Supabase, plus a Streamlit dashboard
  with retention, session depth, power-up efficacy and a coin-economy trend.

The remaining work is narrow. It is listed below.

---

## The gaps

### 1. The coin economy has no faucet — P0

`add_coins()` and `claim_daily()` in `game/store_data.py` are called only from
`tests/test_store.py`. Nothing in `world.py`, `scenes.py` or `main.py` ever calls either.
`DAILY_REWARD` in `game/config.py` is dead config.

**Impact.** The wallet starts at zero and can never increase. Every item in the catalog is
permanently unaffordable. In-run coins feed the HUD, achievements, telemetry and the
plausibility check — but never bank.

**Fix.** Bank the run's coin count once at run end, in `_on_death` in `game/scenes.py`,
after achievements are evaluated so coin-count badges still see an untouched run. Guard
against double-banking. Not per-pickup — that would mean a storage write per coin. Not
gated on the plausibility check either; that guards the public leaderboard, and gating
coins on it would silently zero legitimate runs, which is the worst bug class available
here.

**Rate: 1:1.** The HUD shows a coin count during the run. If the wallet moves by a
different number, players read it as a bug. Tune the economy through catalog prices, never
a hidden multiplier.

### 2. The store does not persist on the web — P0

`game/store_data.py` saves and loads through the JS bridge actions `store_load` and
`store_save`. The dispatcher in `inject_theme.py` implements neither — both fall through
to its default case and return null.

**Impact.** On the browser build, which is the primary target, the wallet and every
purchase are silently wiped on each page load. Native works, because it writes a JSON
file — which is why this has gone unnoticed.

**Fix.** Add the two missing cases, mirroring the `ach_load` / `ach_save` pattern already
in that file. The Python side needs no change; it already speaks this protocol.

### 3. No real per-user identity — P1

Identity today is a UUID in `localStorage`. There is no auth. The `profiles` table is
anon-key read/write with an unconditional check — the schema's own comment concedes that
any client can read or overwrite any row, and that true per-account isolation requires
real auth.

**Impact.** This is the actual blocker on "coins counted per user." A rewritable
browser-local UUID is not a user. It is lost on clearing site data, in private windows,
and on every other device.

**Fix.** Supabase anonymous sign-in, which yields a durable user and a JWT claim usable in
row-level security. Keep the existing UUID purely as a migration key. Later, linking an
email or Google identity upgrades that same user in place, so no data migration is needed
to add real accounts.

### 4. The wallet has no cloud sync — P1

Achievements sync to Supabase. The wallet does not. Even the working native wallet is
device-local and dies with the device.

**Fix.** A sync mirroring the achievements one: push on change, pull at boot. The merge
rule matters more than the transport — take the higher balance and the **union** of owned
items, never "server wins," which would wipe purchases made during an offline session.
Sync stays best-effort and must never block a purchase.

### 5. No app packaging exists — P0 for the app track

No manifest, no service worker, no icons, no splash. The only packaging in the repo is a
PyInstaller Windows executable.

**Fix.** A PWA shell — manifest with portrait lock, icons, offline caching of the build.
This is a prerequisite for the Play Store path, not optional polish.

### 6. This branch deploys nowhere — P0

`app_wrapup` is absent from the branch list in `.github/workflows/pages.yml`. Pushes to it
currently produce no deploy.

**Fix.** Add the branch and give it a sub-path.

### 7. Two player records coexist, and the wrong one is wired up — P0

`game/achievements.py` and `game/store_data.py` each keep their own player record, in
separate storage keys, with different data models. Only the achievements one syncs to the
cloud. Only the store one is wired to the UI.

They are not redundant — **they disagree about how a balance should be stored**, and the
one that is wired up has the weaker model. See *The player record* below; this is the
section that matters most for the per-user requirement, and it corrects an earlier reading
that treated the achievements record as dead scaffolding to delete.

**Fix.** Unify onto one record with the achievements ledger semantics and the store's UI
wiring. Do not simply delete either side.

---

## The player record

The requirement is one durable, traceable record per player: how many coins they have, how
they got them, what they've unlocked, what they've bought — surviving reloads, reinstalls
and second devices. This section is the design for that, and it is the part of the wrap-up
with the most subtlety in it.

### The core problem: a balance cannot be merged

`store_data.py` stores `wallet` as a plain integer. That is the natural thing to write and
it is not safely synchronisable. Two devices, both offline:

- Device A earns 100. Its wallet says 100.
- Device B spends 100 on a skin. Its wallet says 0.

When they sync, there is no rule that recovers the truth. Take the higher value and the
purchase was free. Take the lower and the earnings vanish. Take the most recent and the
answer depends on clock skew. **A mutable balance carries no information about how it got
there, so no merge function can be correct.**

`achievements.py` already solves this, and it is the reason that record should not be
treated as dead code. It never stores a balance. It stores two grow-only counters —
lifetime coins earned, lifetime coins spent — and derives:

```
balance = coins_earned − coins_spent
```

Both inputs only ever increase, so merging is well-defined: take the element-wise maximum
of each counter and re-derive. The result is order-independent, safe to apply twice, and
cannot be corrupted by a replayed sync. The same file already applies the matching rules
to the rest of the record: unlocked achievements and owned items are grow-only sets merged
by union on earliest timestamp, and equipped slots are a mutable choice resolved
last-write-wins. That is the right model. It is simply not the one the store uses.

**So the unification runs in the direction opposite to what it first appears:** keep
`store_data.py`'s UI wiring and catalog integration, adopt `achievements.py`'s ledger
semantics, and collapse both into a single record under a single storage key with a single
sync path.

### Counting per device, not just per record

Element-wise maximum has one known flaw: concurrent earning under-counts. Earn 50 on a
phone and 50 on a laptop while both are offline, and the merge yields 50, not 100.

The fix is small — key each counter by install rather than keeping one number:

```
coins_earned: { install_a: 120, install_b: 50 }   →  total = 170
```

Merge by taking the max per install, then summing. Concurrent earning on different devices
now adds up correctly, and the merge keeps every property that made the simple counter
safe. This is a standard grow-only counter and it costs a few lines over the naive version.

The bias is worth stating plainly: this design can **under**-credit in exotic cases and can
never **over**-credit. For a cosmetics economy that is the correct direction to err.

### Traceability: the ledger

Counters give a correct total but no history, and the ask includes seeing how a balance was
arrived at. Add an append-only ledger table keyed by user: timestamp, kind
(`run_reward` / `daily` / `purchase` / `grant`), delta, item id, and the run it came from.

That buys three things at once:

- **A player-facing history** — "where did my coins go" answered in-game.
- **An independent check.** The server can sum the ledger and compare it to the client's
  reported balance. Drift is then *visible* without being *enforced* — consistent with the
  client-authoritative decision, because the ledger is an audit log, not a gate.
- **Economy tuning data.** Sources and sinks, per player, over time — which is exactly
  what the balance pass needs and what the analytics dashboard can already consume.

Run earnings are in fact already traceable: the `plays` table records per-run coins today.
Purchases are the missing half.

### Identity: what makes it *per user*

Everything above still sits behind a rewritable browser-local UUID, which is per browser
profile, not per person. Supabase anonymous sign-in replaces it with a durable user and an
id usable in row-level security, so each player's row is genuinely theirs — closing the
hole the current schema comment openly documents. Linking an email or Google identity later
upgrades that same user in place, so adding real accounts needs no data migration and no
re-keying of anything described here.

### The reset hazards — "erased when the game loads"

This is worth being precise about, because the failure the user is guarding against is
already latent in the code and the coin fix is about to make it live.

`store_data`'s load and save are asymmetric. Save refuses to write when the bridge is
absent. **Load does not — it returns a fresh default state on any failure**, and the module
caches that for the rest of the session. So a single transient failure to read produces a
zeroed wallet in memory, and the very next mutation persists those zeros over the player's
real data. Today nothing calls the mutation path, so the bug is dormant. Wiring the coin
faucet arms it.

The rules that close this class of bug:

1. **Distinguish "empty" from "failed to load."** Only the first may be saved over. A
   failed read must mark the record unsafe to write and retry, never silently substitute
   defaults.
2. **Never let a blank record overwrite a populated one** — locally or in the cloud. A
   fresh install syncing before its first pull must not clobber the server copy.
3. **Merge on pull, never replace.** With the semantics above this is safe by
   construction; with a mutable balance it never is.
4. **Degrade, don't destroy.** Blocked storage — private windows, cleared site data — must
   fall back to in-memory for the session rather than writing a reset.
5. **Migrate additively.** Unknown fields from a newer build are preserved, not dropped, so
   a player moving between builds doesn't lose progress. The existing coercion already
   drops unknown keys; that becomes a hazard the moment two versions are live at once.

### What this looks like in sequence

1. Fix the web bridge so the record persists at all (gap 2). Nothing below is observable
   until this lands.
2. Wire the coin faucet (gap 1) — but apply hazard rule 1 first, or the faucet's first
   write can zero a wallet.
3. Collapse the two records into one, on the counter-and-ledger model.
4. Add anonymous auth and per-user row-level security.
5. Sync the unified record, merging on pull.
6. Add the ledger table and the in-game history view.

Steps 1 and 2 are the fifteen-line fix. Steps 3 through 6 are the actual per-user system,
and they are worth doing in that order — each is safe to ship on its own.

---

## Two tracks to done

### Track A — the online link

**Goal:** a public URL good enough to submit to a casual-games portal.

1. Wire this branch into the deploy workflow.
2. Build the PWA shell — manifest, icons, service worker, portrait lock.
3. Fix boot UX. The real review risk is not file size, it is the Python-runtime boot
   pause. A loading screen that looks like a hang fails review regardless of correctness.
   Measure time-to-interactive on a mid-range Android before submitting.
4. Submit. **CrazyGames first** — open intake, review in a day or two, non-exclusive, so
   it forecloses nothing. **Poki is invite-only**; apply in parallel and do not sequence on
   it.

**Known risk:** GitHub Pages cannot set COOP/COEP headers. Confirm the build does not need
them; if it does, repoint the existing Netlify workflow at this branch rather than
standing up new infrastructure. Portals may also need the Supabase host allowlisted.

**Shipped means:** a stable URL, installable, that survives a hard reload with the
player's coins and purchases intact, submitted to at least one portal.

### Track B — the app

**Goal:** a Google Play listing.

PWA → Bubblewrap/TWA. Track A already produces the PWA; the TWA adds a thin shell over the
same artifact. One build target, one deploy — and game updates ship by pushing the web
build, with no store review in the loop.

Needs: icon set including maskable, splash, portrait lock, offline-capable service worker,
Digital Asset Links on the origin for a URL-bar-free launch, a Play Console listing,
content rating, and a data-safety declaration covering the Supabase calls. The developer
account is a one-time $25.

**Shipped means:** installable from Play, launching full-screen with no browser chrome.

---

## Two judgement calls worth recording

**Client-authoritative wallet, server-durable.** Coins buy cosmetics. There is no
real-money path, no trading, no competitive advantage, and no leaderboard coupling.
Server-validating coin earning would mean re-implementing the anti-cheat chain as a
server-side function — several hundred lines, in a second language — plus a new failure
mode where a network hiccup eats a legitimate run's coins. The benefit is that a
determined attacker gets a cosmetic slightly earlier, on their own screen. Not worth it.

**The written trigger to revisit this is in-app purchases.** If coins ever cost money, or
gate competitive content, earning must move server-side. Until then, durability is the
requirement, not validation.

**Play Store via TWA; no iOS this pass.** Apple's minimum-functionality rules treat a
WebView-wrapped web game as a rejection candidate, and the WASM runtime carries real
constraints on iOS Safari. Getting a Python-WASM game through App Review is its own
project, not a wrap-up step.

---

## Work areas

| # | Area | Goal | Files | Effort | Priority | Depends on |
|---|---|---|---|---|---|---|
| A1 | Web store persistence | Store survives reload | `inject_theme.py` | S | **P0** | — |
| A2 | Coin faucet | Wallet can grow | `game/scenes.py`, `tests/` | S | **P0** | A1 |
| A3 | Daily reward | A reason to return | `game/store_hub.py`, `game/scenes.py` | S | P0 | A2 |
| A4 | Load/save hazard guard | A failed read can't zero a wallet | `game/store_data.py` | S | **P0** | before A2 |
| A6 | Unify the player record | One record, counter + ledger model | `store_data.py`, `achievements.py` | M | P1 | A2 |
| C4 | Coin ledger + history view | Traceable balance | schema, store UI | M | P1 | C1 |
| A5 | Economy balance pass | Earned, not grindy | `game/store_catalog.py`, `config.py` | M | P0 | A2 |
| B1 | Deploy wiring | Branch ships | `.github/workflows/pages.yml` | S | **P0** | — |
| B2 | PWA shell | Installable, offline | `inject_theme.py`, new assets | M | **P0** | B1 |
| B3 | Boot UX | Survives portal review | `inject_theme.py` | M | P0 | B2 |
| B4 | Portal submission | Live on CrazyGames | — (ops) | S | P1 | A, B |
| C1 | Anonymous auth + RLS | Real per-user identity | `inject_theme.py`, schema | M | P1 | — |
| C2 | Wallet cloud sync | Survives device loss | `game/store_data.py` | M | P1 | C1 |
| C3 | Close the `profiles` hole | Per-row isolation | schema | S | P1 | C1 |
| D1 | TWA + Play listing | The app | new shell | M | P1 | B2 |
| E | Account upgrade | Portable identity | auth layer | L | P2 | C1 |

**Sequence:** A1 → A4 → A2 first, alone — A4 goes before A2, because the faucet's first
write is what arms the reset hazard. Then the rest of A and all of B in parallel. C is
independent of both and should land after A is verified. A6 and C4 together are the
per-user record described above. D follows B2. E is later.

### On the balance pass

Ship 1:1 and let the data decide. The `analytics/` dashboard already tracks a coin-economy
trend against real telemetry — tune prices against observed earn-per-run before launch,
not against a guess. At 1:1 a basic skin lands somewhere around ten to twenty runs, which
is a healthy first-unlock curve to start from.

---

## Not worth doing

- **Server-validated coin earning** — see the judgement call above. Revisit only on IAP.
- **iOS, Capacitor, Electron, Tauri** — not this pass.
- **Rewriting the anti-cheat** — it correctly scopes itself to the leaderboard.
- **Per-coin autosave** — a storage write per pickup, on the hot path.
- **Extending PyInstaller to macOS/Linux** — leave the release workflow alone.

---

## Market context

The web bundle is around half a megabyte. Poki asks for an initial download under 8 MB;
CrazyGames allows a 50 MB first playable. **Skybit clears both by more than an order of
magnitude.** That headroom is a genuine asset and worth protecting — the CI size ceiling
is the regression guard that does it.

CrazyGames has open intake, reviews in a day or two, is non-exclusive, and shares ad
revenue. Poki curates by invitation. Publishing to a portal forecloses nothing else —
Play, itch.io and Steam remain open in parallel.

The competitive risk is not size. It is the boot pause before the first frame, and it is
worth measuring on a real mid-range phone before anything is submitted.

---

## Before picking this up

This branch's container has **neither `pygame` nor `pytest` installed**, and
`pyproject.toml` declares no dev dependency group. Install both first, and consider adding
the dev group so CI and local development agree.

Verification for the economy work is specifically a **browser** test: play a run, note the
coin count, die, open the store, confirm the balance rose by exactly that much, buy
something, then **hard-reload** and confirm it all survived. Native passing proves nothing
here — native already worked.
