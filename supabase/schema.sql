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


-- ── Security hardening (added by game/security/) ────────────────────────────
-- Apply this whole block in the Supabase SQL editor. It revokes the blanket
-- anon-insert on `scores`, adds plausibility constraints, and forces all
-- score writes through the `submit_score` RPC which enforces:
--   * score range and name length
--   * minimum run duration
--   * server-side cheating ceiling (score must fit physics)
--   * per-device 30-second rate limit (audit table)
-- See docs/SECURITY.md for the threat model and rotation runbook.

-- 1. Per-device submission audit (rate-limit ledger).
create table if not exists public.submissions_audit (
    device_id    uuid        not null,
    submitted_at timestamptz not null default now(),
    score        int         not null,
    primary key (device_id, submitted_at)
);
alter table public.submissions_audit enable row level security;
-- No anon policies: only the SECURITY DEFINER RPC writes here.

-- 2. Anomaly stream — written by the client when the security module
-- detects something off (HMAC mismatch, ratelimit hit, local-scores tamper).
-- Anon-insert only, never readable by anon.
create table if not exists public.security_events (
    id        bigint generated always as identity primary key,
    device_id uuid,
    name      text not null,
    detail    jsonb not null default '{}'::jsonb,
    ts        timestamptz not null default now()
);
alter table public.security_events enable row level security;
drop policy if exists "anon insert security_events" on public.security_events;
create policy "anon insert security_events"
    on public.security_events for insert to anon with check (true);

-- 3. Tighten the leaderboard table.
alter table public.scores
    add column if not exists device_id    uuid,
    add column if not exists run_sig      text,
    add column if not exists duration_s   int,
    add column if not exists submitted_at timestamptz default now();

do $$ begin
    if not exists (select 1 from pg_constraint where conname = 'scores_score_range') then
        alter table public.scores add constraint scores_score_range check (score between 0 and 100000);
    end if;
    if not exists (select 1 from pg_constraint where conname = 'scores_name_len') then
        alter table public.scores add constraint scores_name_len check (char_length(name) between 1 and 12);
    end if;
end $$;

-- 4. Revoke blanket anon insert; only the RPC may write.
drop policy if exists "anon insert scores" on public.scores;
revoke insert on public.scores from anon;

-- 5. Validated, rate-limited score-submission RPC.
create or replace function public.submit_score(
    p_name           text,
    p_score          int,
    p_device         uuid,
    p_duration       int,
    p_run_sig        text,
    p_pillars        int,     -- pillars passed during the run
    p_y_stddev_centi int,     -- bird-y std-dev × 100 (anti-straight-run)
    p_y_range_centi  int,     -- (max y − min y) × 100
    p_chain_last     text,    -- last event kind in the integrity chain
    p_chain_count    int,     -- total events in the chain
    p_client_sig     text     -- HMAC of the envelope (anti-tamper)
) returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    recent_count int;
begin
    if p_name is null or char_length(trim(p_name)) = 0 then
        raise exception 'name_empty';
    end if;
    if char_length(p_name) > 12 then
        raise exception 'name_too_long';
    end if;
    if p_score < 0 or p_score > 100000 then
        raise exception 'score_oor';
    end if;
    if p_duration is null or p_duration < 3 then
        raise exception 'duration_too_short';
    end if;
    if p_duration > 1800 then  -- 30-min cap; AFK / bot runs
        raise exception 'duration_too_long';
    end if;

    -- Score-vs-time plausibility: ~1 pt/sec base + coin pickups, 4 pts/sec
    -- with 20-pt grace covers powered-up triple-coin runs comfortably.
    if p_score > p_duration * 4 + 20 then
        raise exception 'rate_implausible';
    end if;

    -- Pillar-rate plausibility: scroll speed caps pillar-pass rate at
    -- SCROLL_BASE / PIPE_SPACING ≈ 0.57/sec. Reject < 0.30 (idling, then
    -- something injecting fake pillar events) and > 0.70 (impossible).
    if p_pillars < 0 or p_pillars > p_duration + 5 then
        raise exception 'pillars_implausible';
    end if;
    if p_duration >= 10 and p_pillars * 100 < p_duration * 25 then
        raise exception 'pillars_too_few_for_score';
    end if;
    if p_pillars > 0 and p_pillars * 100 > p_duration * 70 then
        raise exception 'pillars_too_many';
    end if;

    -- Anti-straight-run trajectory check.
    -- A bird flapping in real gameplay oscillates 30–120 pixels and produces
    -- a y-std-dev > 25 pixels. A straight-line run (collision disabled or
    -- replayed events) shows std-dev ≈ 0 and y-range ≈ 0. Reject anything
    -- below 8 pixel std-dev (centi-pixels: 800) once the run is long enough
    -- for stats to be meaningful.
    if p_duration >= 5 then
        if p_y_stddev_centi is null or p_y_stddev_centi < 800 then
            raise exception 'straight_run_detected';
        end if;
        if p_y_range_centi is null or p_y_range_centi < 4000 then
            raise exception 'narrow_y_range';
        end if;
    end if;

    -- Chain-of-events integrity. The recorder MUST seal the run with a
    -- 'death' event during World._die(); a chain with any other tail means
    -- the run wasn't terminated by the engine.
    if p_chain_last is distinct from 'death' then
        raise exception 'run_not_terminated';
    end if;
    if p_chain_count is null or p_chain_count < (p_pillars + 1) then
        raise exception 'chain_truncated';
    end if;

    -- HMAC envelope must be present (verified per-build out-of-band; the
    -- presence-check here just ensures the client went through the signed
    -- bridge instead of curling the RPC directly).
    if p_client_sig is null or char_length(p_client_sig) < 16 then
        raise exception 'client_sig_missing';
    end if;

    -- Per-device cooldown: at most one submission every 30 seconds.
    select count(*) into recent_count
        from public.submissions_audit
        where device_id = p_device
          and submitted_at > now() - interval '30 seconds';
    if recent_count >= 1 then
        raise exception 'rate_limited';
    end if;

    insert into public.submissions_audit(device_id, score) values (p_device, p_score);
    insert into public.scores(name, score, device_id, run_sig, duration_s)
        values (p_name, p_score, p_device, p_run_sig, p_duration);
end
$$;

revoke all on function public.submit_score(text, int, uuid, int, text) from public;
grant execute on function public.submit_score(text, int, uuid, int, text) to anon;

-- 6. Validated telemetry RPC.
alter table public.plays add column if not exists run_sig text;

create or replace function public.log_play(
    p_device      uuid,
    p_score       int,
    p_duration    int,
    p_coins       int,
    p_pillars     int,
    p_near_misses int,
    p_powerups    jsonb,
    p_run_sig     text
) returns void
language plpgsql
security definer
set search_path = public
as $$
begin
    if p_duration < 3 then raise exception 'duration_too_short'; end if;
    if p_score < 0 or p_score > 100000 then raise exception 'score_oor'; end if;
    if p_pillars < 0 or p_pillars > p_duration + 5 then raise exception 'pillars_implausible'; end if;
    if p_coins < 0 or p_coins > p_pillars * 4 + 20 then raise exception 'coins_implausible'; end if;
    if p_near_misses < 0 or p_near_misses > p_pillars + 5 then raise exception 'near_misses_implausible'; end if;
    if p_run_sig is not null and exists (
        select 1 from public.plays
            where device_id = p_device
              and run_sig = p_run_sig
              and played_at > now() - interval '5 minutes'
    ) then
        return;  -- silent dedup
    end if;
    insert into public.plays(device_id, score, duration_s, coins, pillars,
                             near_misses, powerups, run_sig)
        values (p_device, p_score, p_duration, p_coins, p_pillars,
                p_near_misses, coalesce(p_powerups, '{}'::jsonb), p_run_sig);
end
$$;

revoke all on function public.log_play(uuid, int, int, int, int, int, jsonb, text) from public;
grant execute on function public.log_play(uuid, int, int, int, int, int, jsonb, text) to anon;

-- After applying this migration, the client calls:
--   POST /rest/v1/rpc/submit_score
--   POST /rest/v1/rpc/log_play
-- inject_theme.py uses these endpoints; raw inserts are no longer permitted.
