-- Skybit leaderboard recovery SQL.
--
-- Run once in the Supabase SQL editor (Database → SQL editor) for the
-- project whose URL is in the SUPABASE_URL secret. Idempotent: safe to
-- re-run. After running, hard-refresh the deployed site to verify the
-- top-10 populates.
--
-- Why this exists: schema.sql is the canonical reference, but the live
-- database can drift (manual policy edits, dashboard changes, Supabase
-- platform default changes). When a SELECT against `scores` returns
-- 200 OK with `[]`, the most common cause is RLS without a matching
-- permissive policy for the anon role, OR missing table-level grants.
-- This file re-establishes both layers.

-- 1. Schema-level grants. Without USAGE on the schema, no role can
-- "see" tables in it.
grant usage on schema public to anon, authenticated;

-- 2. Table-level grants. Without these, RLS doesn't even get a chance
-- to evaluate -- the role is rejected at the postgres permissions
-- layer first.
grant select         on table public.scores to anon, authenticated;
grant insert         on table public.scores to anon, authenticated;
grant select, insert on table public.plays  to anon, authenticated;

-- 3. RLS policies. Drop-and-recreate is intentional -- if the policy
-- exists but is restrictive or evaluates false, an empty array is
-- exactly what the anon client sees. Recreating with a permissive
-- USING (true) for SELECT is the documented Supabase pattern for a
-- public read-only leaderboard.
alter table public.scores enable row level security;
alter table public.plays  enable row level security;

drop policy if exists "anon read scores"   on public.scores;
drop policy if exists "anon insert scores" on public.scores;
drop policy if exists "anon insert plays"  on public.plays;

create policy "anon read scores"
    on public.scores for select
    to anon, authenticated
    using (true);

create policy "anon insert scores"
    on public.scores for insert
    to anon, authenticated
    with check (true);

create policy "anon insert plays"
    on public.plays for insert
    to anon, authenticated
    with check (true);

-- 4. Sanity check. Should return one or more rows after running.
-- Comment-out before keeping this file in version control if you don't
-- want the SELECT to run on every paste.
-- select count(*) as score_rows from public.scores;
