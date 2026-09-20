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

After that, the thing standing between here and "shipped" is **durable identity** — the
one requirement behind "coins counted per user," and the one the current architecture
cannot satisfy at all. Browser-written storage is erased by iOS Safari after seven days
away, taking the player's ID with it, which makes a server-side copy of the data useless
on its own. The fix is a server-set cookie on a real domain, and it is why these games
have their own domain in the first place. See *The player record*.

Alongside that: a PWA shell and deploy wiring.

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

### 3. The player ID is not durable — P0 for the link

Identity today is a UUID written by JavaScript into `localStorage`, with no server
involvement. The `profiles` table is anon-key read/write with an unconditional check — the
schema's own comment concedes that any client can read or overwrite any row.

**Impact.** This is the actual blocker on "coins counted per user," and it is worse than
it looks. Script-written storage — `localStorage`, IndexedDB, `document.cookie` — is
**deleted by iOS Safari after seven days without a visit**. No clearing, no private mode,
no user action: a casual player who returns after two weeks is wiped.

And because the *ID* is stored the same fragile way as the data, putting the data on a
server does not help on its own. The row survives; nobody can prove it's theirs. An
orphaned row and a lost player are the same outcome.

**Fix.** A server-set cookie on a real first-party domain. See *The player record*.

### 4. The record has nowhere durable to live — P0 for the link

Achievements mirror to Supabase; the wallet does not. But the deeper issue is that there
is no server-held record at all — only browser-local copies with a best-effort backup,
reachable solely from the browser that wrote them.

**Fix.** Make the server the source of truth and the browser a cache, rather than syncing
two peers. See below.

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

The requirement, stated plainly: **a player opens the link, plays, leaves, comes back a
month later on the same device, and their coins, purchases and achievements are still
there — having never signed up, never been prompted, never been asked to remember
anything.**

This is a solved, ordinary pattern for casual web games. It is also not achievable with
the architecture the game has today, for a reason that is easy to miss.

### Why browser storage alone cannot do it

Everything the game currently persists is written by JavaScript: `localStorage`, and
`document.cookie` if it were used. **iOS Safari deletes all script-written storage after
seven days without a visit.** Not on clearing data, not in private mode — automatically,
for an ordinary player who simply didn't come back that week.

The trap is that this applies to the *player's ID* as much as to the data. Move the data
to a server and the row survives, but the returning player can no longer prove which row
is theirs. An orphaned row and a wiped player are indistinguishable from the player's
side.

So the durability problem is not "where does the data live." It is **"what carries the
identity, and does that thing survive."**

### What works: a server-set cookie on your own domain

A cookie set by a **server**, via a `Set-Cookie` response header on a genuine first-party
domain, is exempt from the seven-day cap. It persists up to **400 days** — the ceiling
Chrome enforces too, so that is the practical maximum everywhere.

Crucially, **the cookie is refreshed on every visit**, so the clock restarts each time the
player returns. Only continuous absence beyond the cap loses it. A month away is nothing.

This is why these games have their own domain. It is not branding. On a shared host such
as `*.github.io`, the game shares an origin with every other project on that host and
cannot own its cookie properly. **A domain is a functional prerequisite of durable
identity, not a polish item.**

### The design

1. **A real domain**, over HTTPS.
2. **One small serverless endpoint.** On a request with no cookie it mints a UUID and
   replies with `Set-Cookie: player=<uuid>; Max-Age=<400d>; HttpOnly; Secure;
   SameSite=Lax`. Every subsequent request carries it automatically, with no client code
   involved. `HttpOnly` also means page scripts cannot read or forge it.
3. **The server holds the record** — coin balance, owned items, equipped slots,
   achievements, lifetime stats — keyed by that ID.
4. **The game fetches on load and writes on change** through that endpoint.
5. **`localStorage` becomes a cache only.** It makes startup instant and keeps the game
   playable offline, but it is never the source of truth. When the two disagree, the
   server wins.

The player's experience is that the link simply remembers them. No login, no prompt, no
code to keep.

### What this simplifies

The earlier draft of this document designed for two peer copies reconciling — merge rules,
grow-only counters, per-install accounting, last-write-wins on equips. **With one
server-held record, none of that is needed.** There is a single copy and a single writer,
so there is nothing to merge.

Two things are still worth keeping from that thinking:

- **Derive the balance from an append-only ledger** rather than storing a mutable integer.
  Each credit and debit is a row — `+120 run_reward`, `+75 daily`, `−280 purchase`. Balance
  is their sum. This is how financial systems work, and it buys the traceability the brief
  asked for: a player-facing history, a reconstructable balance when something goes wrong,
  and real source/sink data for tuning the economy. A bare integer discards all of that the
  moment it is wrong.
- **Idempotency keys on writes.** A run ends, the network retries, the player is credited
  twice. Each transaction carries a client-generated id and the server ignores repeats.
  Non-optional once writes cross a network.

### Honest limits

These apply to every no-login game, including the ones this pattern is modelled on:

- **A different browser or device is a different player.** Cookies don't travel. Only a
  login fixes this, and a login is out of scope by decision.
- **Clearing cookies loses the record.** That is a deliberate act and rare — unlike
  Safari's automatic seven-day purge, which is the failure actually worth engineering
  against.
- **Private windows start fresh every time.**

For a free game with a cosmetic-only economy these are acceptable. What is not acceptable
is silent loss for a player who did nothing wrong, and the server cookie removes exactly
that case.

Two hedges worth taking anyway, both free:

- **Offer a backup link at a moment of investment** — after a first purchase or a
  milestone, never at first launch. One tap to copy a URL carrying the ID. Most players
  will never see it; it exists for the invested few. Do not *ask* players to save anything.
- **Keep re-earning fast.** A wipe should be a shrug, not a reason to quit. This argues
  against long grinds at the top of the price curve while durability is imperfect.

### Where to run it

**Cloudflare Workers** is the natural home: 100k requests/day free, and no auto-pause.
**Supabase Edge Functions** also work (500k invocations/month free) and the project is
already on Supabase — but free Supabase projects pause after seven days without traffic,
which would silently take the game offline unless a scheduled ping keeps them warm. This
repo already runs GitHub Actions, so that ping is cheap if this route is taken.

Either way the running cost is zero. The domain, roughly $10–15/year, is the only real
expense in the whole design — and it is the part that buys the durability.

### Sequence

1. **Register the domain and point the deploy at it.** A prerequisite, not polish.
2. **Stand up the identity endpoint** — mint and refresh the cookie, read and write the
   record.
3. **Fix the web bridge** (gap 2) so the client can persist at all.
4. **Wire the coin faucet** (gap 1) — after step 2, so coins are born durable instead of
   being migrated later.
5. **Move the record server-side**, with `localStorage` demoted to a cache.
6. **Add the ledger and the in-game history view.**

Steps 3 and 4 remain the fifteen-line fix and can ship before the rest. Doing step 1 and 2
first is what makes them permanent rather than provisional.

---

## Two tracks to done

### Track A — the online link

**Goal:** a public URL good enough to submit to a casual-games portal.

1. **Register the domain and deploy to it.** Everything durable depends on this, and it is
   also what makes the URL shareable as a product rather than a project path.
2. Wire this branch into the deploy workflow.
3. Build the PWA shell — manifest, icons, service worker, portrait lock. Installing also
   exempts the game from Safari's storage purge, so this hardens identity as well.
4. Fix boot UX. The real review risk is not file size, it is the Python-runtime boot
   pause. A loading screen that looks like a hang fails review regardless of correctness.
   Measure time-to-interactive on a mid-range Android before submitting.
5. Submit. **CrazyGames first** — open intake, review in a day or two, non-exclusive, so
   it forecloses nothing. **Poki is invite-only**; apply in parallel and do not sequence on
   it.

**Known risks.** GitHub Pages cannot set custom headers, which matters both for COOP/COEP
(confirm the build doesn't need them) and for the identity endpoint, which must live
somewhere that can set cookies — a Worker or an edge function, not the static host.
Portals may also need the backend host allowlisted.

Note that on a portal the game is framed under *their* domain, so the cookie is theirs to
scope, not yours. Portal traffic should use the portal's own account and cloud-save SDK
where one exists; your domain remains the durable home for direct traffic.

**Shipped means:** a stable URL on your own domain that a player can leave for a month,
return to, and find their coins and purchases intact — verified on iOS Safari, not just
desktop Chrome.

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

## Three judgement calls worth recording

**No accounts, ever — durability comes from the cookie, not from a login.** Asking a
casual player to sign up, or to save a restore code, is friction they will not accept and
a responsibility they will not take. The server-set cookie delivers the "it just remembers
me" behaviour without either. A backup link exists only as an opportunistic offer to
already-invested players, never as a step anyone is walked through.

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
| A5 | Economy balance pass | Earned, not grindy | `game/store_catalog.py`, `config.py` | M | P0 | A2, C2 |
| B1 | Deploy wiring | Branch ships | `.github/workflows/pages.yml` | S | **P0** | — |
| B2 | PWA shell | Installable, offline | `inject_theme.py`, new assets | M | **P0** | B1 |
| B3 | Boot UX | Survives portal review | `inject_theme.py` | M | P0 | B2 |
| B4 | Portal submission | Live on CrazyGames | — (ops) | S | P1 | A, B |
| C0 | **Register the domain** | Durable identity is possible at all | DNS, deploy target | S | **P0** | — |
| C1 | Identity endpoint | Cookie minted + refreshed server-side | new serverless fn | M | **P0** | C0 |
| C2 | Server-held record | One source of truth | `store_data.py`, `achievements.py`, schema | M | **P0** | C1 |
| C3 | Retire the anon-key tables | Close the open-row hole | schema | S | P1 | C2 |
| C4 | Ledger + history view | Traceable balance | schema, store UI | M | P1 | C2 |
| C5 | Backup link offer | Safety valve for the invested | store UI | S | P2 | C1 |
| D1 | TWA + Play listing | The app | new shell | M | P1 | B2 |

**Sequence:** A1 → A4 → A2 first and alone — A4 before A2, because the faucet's first write
is what arms the reset hazard. That is the fifteen-line fix and it is worth shipping on its
own to see the store come alive.

In parallel, **C0 and C1 are the real unlock for the link version** and should start
immediately, because the domain has lead time and everything durable depends on it. C2
then moves the record server-side; once it lands, the browser copy is only a cache and the
seven-day problem is gone.

B runs alongside throughout. A5 waits for both A2 and C2, since tuning an economy against
telemetry needs the telemetry to be attributable to durable players. D follows B2.

### On the balance pass

Ship 1:1 and let the data decide. The `analytics/` dashboard already tracks a coin-economy
trend against real telemetry — tune prices against observed earn-per-run before launch,
not against a guess. At 1:1 a basic skin lands somewhere around ten to twenty runs, which
is a healthy first-unlock curve to start from.

---

## Not worth doing

- **Accounts, logins, or an OAuth provider** — ruled out by decision; the cookie covers it.
- **Asking players to save a restore code** — a casual player will not, and should not have
  to. Offer a backup link to the already-invested; never make it a step.
- **Cross-device sync, and the merge machinery it implies** — it requires a login, which is
  out of scope. One device, one record, no merge.
- **Server-validated coin earning** — see the judgement call above. Revisit only on IAP.
- **Device fingerprinting to recover a lost ID** — unreliable, privacy-hostile, and it
  would fail portal and store review.
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

Verification for the identity work has to be done where it actually fails. Desktop Chrome
will pass whatever you build, because its storage is not evicted; it proves nothing. The
real tests are:

- **iOS Safari, after the purge window.** Play, leave for more than seven days, return.
  Everything should still be there. This is the test the whole design exists to pass, and
  it cannot be shortcut — though you can approximate it by clearing script storage while
  leaving cookies intact.
- **Cookie present and durable.** Confirm the cookie is `HttpOnly` and `Secure`, that page
  scripts cannot read it, and that its expiry is pushed forward on each visit.
- **Cold load.** A browser with no cookie gets a fresh ID and a clean record — and a
  browser with one never gets a fresh ID by accident. Silently minting a second ID for an
  existing player is the failure mode that looks exactly like data loss.
