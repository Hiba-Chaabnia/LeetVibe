-- ============================================================
-- LeetVibe — Migration 002: user_solutions table
-- Run this in: Supabase Dashboard → SQL Editor → New query
-- ============================================================

-- Stores the user's passing code for each solved problem.
-- Uses upsert on (user_id, problem_slug) so re-submitting updates
-- the stored code rather than inserting a duplicate.

create table public.user_solutions (
    id           uuid        default gen_random_uuid() primary key,
    user_id      uuid        references auth.users(id) on delete cascade not null,
    problem_slug text        not null,
    difficulty   text,
    code         text        not null default '',
    solved_at    timestamptz default now() not null,
    updated_at   timestamptz default now() not null,
    unique(user_id, problem_slug)
);

alter table public.user_solutions enable row level security;

create policy "select own" on public.user_solutions
    for select using (auth.uid() = user_id);

create policy "insert own" on public.user_solutions
    for insert with check (auth.uid() = user_id);

create policy "update own" on public.user_solutions
    for update using (auth.uid() = user_id);

create policy "delete own" on public.user_solutions
    for delete using (auth.uid() = user_id);
