-- Skybit v5 leaderboard schema (reference doc — not run automatically by
-- any build step). Apply by pasting into the Supabase dashboard SQL editor.
--
-- v5 is a harder game than the live v4, so its scores are not comparable to
-- the existing `scores` table. v5 reads+writes its own `scores_v5` table for
-- the CURRENT board, and treats the original `scores` table as a read-only
-- LEGACY (previous-version) board. v5 never writes to `scores`, so the live
-- v4 board is left completely untouched and becomes a naturally-frozen hall
-- of fame once v4 is retired. (An explicit freeze later — revoking anon
-- insert on `scores` — is optional and out of scope here.)
--
-- Mirrors public.scores exactly (see schema.sql): anon read+write under RLS.

create table if not exists public.scores_v5 (
    name  text not null,
    score int  not null
);

alter table public.scores_v5 enable row level security;

create policy "anon insert scores_v5"
    on public.scores_v5 for insert
    to anon with check (true);

create policy "anon read scores_v5"
    on public.scores_v5 for select
    to anon using (true);

grant usage on schema public to anon, authenticated;
grant select, insert on table public.scores_v5 to anon, authenticated;
