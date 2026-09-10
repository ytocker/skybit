-- Skybit Supabase schema (reference doc — not run automatically by any
-- build step). Apply by pasting into the Supabase dashboard SQL editor.
--
-- Two tables, both written from the browser using the project's anon
-- key. The leaderboard (`scores`) is read+write by anonymous users; the
-- telemetry table (`plays`) is write-only for anon and read-only via the
-- dashboard / service-role key.


-- ── Leaderboard ─────────────────────────────────────────────────────────────
-- Powered by inject_theme.py's lbSubmitStart / lbFetchStart JS bridge and
-- game/leaderboard.py's async wrappers. One row per top-10 submission.

create table if not exists public.scores (
    name  text not null,
    score int  not null
);

alter table public.scores enable row level security;

create policy "anon insert scores"
    on public.scores for insert
    to anon with check (true);

create policy "anon read scores"
    on public.scores for select
    to anon using (true);


-- ── Per-run telemetry ───────────────────────────────────────────────────────
-- Powered by inject_theme.py's skyLogPlayStart JS bridge and
-- game/play_log.py's log_run(world). One row per completed run, fired
-- fire-and-forget from scenes._on_death().
--
-- device_id is an anonymous UUID generated client-side and persisted in
-- localStorage (key: skybit_device_id). No IP, no user-agent, no PII.

create table if not exists public.plays (
    id          bigint generated always as identity primary key,
    device_id   uuid          not null,
    played_at   timestamptz   not null default now(),
    score       int           not null,
    duration_s  int           not null,
    coins       int           not null,
    pillars     int           not null,
    near_misses int           not null,
    powerups    jsonb         not null,
    -- Null on a normal row. Set by leaderboard.submit when a top-10 submit
    -- is dropped, naming the gate that rejected it so the loss is traceable
    -- from the DB. See setup_leaderboard.sql for the diagnostic query.
    submit_error text
);

alter table public.plays enable row level security;

create policy "anon insert plays"
    on public.plays for insert
    to anon with check (true);

-- No SELECT policy for anon — the game never reads this table. Use the
-- service-role key (or the dashboard) for analytics queries.

-- Recommended indexes (apply once the table has volume):
--   create index plays_played_at_idx on public.plays (played_at desc);
--   create index plays_device_id_idx on public.plays (device_id);


-- ── Player profile backup ────────────────────────────────────────────────────
-- Powered by inject_theme.py's profile_push / profile_pull JS bridge and
-- game/achievements.py's _cloud_push / sync_cloud. One row per device holding a
-- mirror of the local profile blob (achievements + lifetime stats + coin wallet
-- + owned/equipped store items). The device copy in localStorage is always
-- authoritative; this is a backup + the foundation for a future login-based
-- cross-device sync.
--
-- device_id is the same anon UUID as plays (localStorage key skybit_device_id).
-- payload is the whole {v, mtime, unlocked, life, wallet, inventory} blob as
-- jsonb, so new profile sections need NO schema change here.
--
-- SECURITY NOTE: all clients share the anon key, so RLS cannot isolate rows
-- per device server-side — anon can technically read/overwrite any row. The
-- device_id is an unguessable random UUID and the blob is non-PII game progress
-- (same posture as the public leaderboard). True per-account isolation requires
-- real auth (a later change).

create table if not exists public.profiles (
    device_id  uuid        primary key,
    payload    jsonb       not null,
    updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

-- Insert + update together give anon an upsert (Prefer: resolution=
-- merge-duplicates on the device_id primary key); select lets a returning
-- player restore their backup.
create policy "anon insert profiles"
    on public.profiles for insert
    to anon with check (true);

create policy "anon update profiles"
    on public.profiles for update
    to anon using (true) with check (true);

create policy "anon read profiles"
    on public.profiles for select
    to anon using (true);
