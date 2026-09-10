# Skybit — Supabase / Leaderboard DB Notes

Context and open decisions around the v5 database split. Read this before
deploying v5 or touching the leaderboard / telemetry tables.

## The problem

v5 is a **harder game** than the live v4. Its scores are not comparable to
v4's, so mixing both versions into one leaderboard would be misleading — a
v5 player and a v4 player competing on the same board aren't playing the
same game.

The same comparability question applies to the **`plays` telemetry table**
(per-run analytics): once v5 ships, rows from v4 and v5 land in the same
table with no way to tell them apart, which muddies any version-over-version
analysis in the Streamlit dashboard.

## What we did — leaderboard (DONE)

The leaderboard is now **version-aware**:

- **`scores_v5`** — new table. v5 reads *and* writes this. It is the
  **CURRENT** board in-game.
- **`scores`** — the original v4 table. v5 treats it as **read-only LEGACY**
  and never writes to it. The live v4 board is left completely untouched and
  becomes a naturally-frozen hall of fame once v4 is retired. (An explicit
  freeze — revoking anon insert on `scores` — is optional and out of scope.)
- In-game UI: a tabbed **CURRENT / LEGACY** leaderboard (deliberately
  labelled by recency, not version numbers).

Schema for the new table lives in [`schema_v5.sql`](./schema_v5.sql).
`scores_v5` mirrors `scores` exactly (anon read+write under RLS).

### Required deploy step (one-time, manual)

`schema_v5.sql` is a **reference doc — not run by any build step.** Before /
at v5 go-live, paste it into the **Supabase dashboard SQL editor** once to
create `scores_v5` and its RLS policies. If you skip this, v5 score writes
will fail.

## What we deferred — `plays` telemetry (PARKED)

Decision: **leave `plays` unchanged for now; revisit at v5 go-live.** No
telemetry code changed on this branch — the leaderboard split is independent
of it.

### The timing gotcha (read before go-live)

The cleanest moment to tag telemetry by version is **at the v5 deploy
itself** — add the version column *and* ship v5's version stamp together, so
the **first v5 row is already tagged**. Rows that land before the stamp
exists can't be retro-labeled: they'd be `NULL` and are only
distinguishable from genuine v4 rows by date. So this must happen **before,
or in the same push as, the v5 cutover** — not after.

It's a small change (~15 min) when you're ready:

1. `alter table public.plays add column version text;` (in Supabase).
2. One line in `inject_theme.py` to stamp the running version onto each
   telemetry POST.
3. One filter in the Streamlit analytics dashboard to split by version.

## Status summary

| Item | State |
| --- | --- |
| Leaderboard version split (`scores_v5` + read-only legacy `scores`) | ✅ Done, QA'd, on `v5_skybit_leaderboard` |
| Run `schema_v5.sql` in Supabase dashboard | 📋 Pending — one-time manual step at/before go-live |
| `plays` telemetry version tagging | ⏸️ Parked — do before/at v5 cutover (see timing gotcha) |
