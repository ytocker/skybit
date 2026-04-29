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
    powerups    jsonb         not null
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
