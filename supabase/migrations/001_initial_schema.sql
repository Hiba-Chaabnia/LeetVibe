-- ============================================================
-- LeetVibe — Initial Schema
-- Run this in: Supabase Dashboard → SQL Editor → New query
-- ============================================================


-- ── 1. user_problems ─────────────────────────────────────────
-- Tracks which problems each user has solved.

create table public.user_problems (
    id           uuid        default gen_random_uuid() primary key,
    user_id      uuid        references auth.users(id) on delete cascade not null,
    problem_slug text        not null,
    difficulty   text,
    solved_at    timestamptz default now() not null,
    unique(user_id, problem_slug)
);

alter table public.user_problems enable row level security;
create policy "select own" on public.user_problems for select using (auth.uid() = user_id);
create policy "insert own" on public.user_problems for insert with check (auth.uid() = user_id);
create policy "update own" on public.user_problems for update using (auth.uid() = user_id);


-- ── 2. chat_sessions ─────────────────────────────────────────
-- One conversation slot per user × problem × mode (learn / coach).
-- Resetting a conversation clears its messages and increments reset_count.

create table public.chat_sessions (
    id           uuid        default gen_random_uuid() primary key,
    user_id      uuid        references auth.users(id) on delete cascade not null,
    problem_slug text        not null,
    difficulty   text,
    mode         text        not null check (mode in ('learn', 'coach')),
    reset_count  integer     default 0 not null,
    created_at   timestamptz default now() not null,
    updated_at   timestamptz default now() not null,
    unique(user_id, problem_slug, mode)
);

alter table public.chat_sessions enable row level security;
create policy "select own" on public.chat_sessions for select using (auth.uid() = user_id);
create policy "insert own" on public.chat_sessions for insert with check (auth.uid() = user_id);
create policy "update own" on public.chat_sessions for update using (auth.uid() = user_id);
create policy "delete own" on public.chat_sessions for delete using (auth.uid() = user_id);


-- ── 3. chat_messages ─────────────────────────────────────────
-- Every individual message turn in a session, stored in the exact
-- format vibe_agent.py uses for self._messages (role, content, tool_calls).
-- Messages are immutable — reset = delete all rows for a session.

create table public.chat_messages (
    id           uuid        default gen_random_uuid() primary key,
    session_id   uuid        references public.chat_sessions(id) on delete cascade not null,
    seq          integer     not null,        -- explicit ordering (0, 1, 2…) set by the app
    role         text        not null check (role in ('system', 'user', 'assistant', 'tool')),
    content      text        not null default '',
    tool_calls   jsonb,                       -- assistant role: Mistral tool_calls array
    tool_call_id text,                        -- tool role: which assistant call this result belongs to
    tool_name    text,                        -- tool role: name of the tool that was called
    created_at   timestamptz default now() not null
);

alter table public.chat_messages enable row level security;

-- Access is checked through session ownership, not a direct user_id column
create policy "select own" on public.chat_messages for select
    using (exists (
        select 1 from public.chat_sessions s
        where s.id = session_id and s.user_id = auth.uid()
    ));
create policy "insert own" on public.chat_messages for insert
    with check (exists (
        select 1 from public.chat_sessions s
        where s.id = session_id and s.user_id = auth.uid()
    ));
create policy "delete own" on public.chat_messages for delete
    using (exists (
        select 1 from public.chat_sessions s
        where s.id = session_id and s.user_id = auth.uid()
    ));


-- ── 4. feedback ──────────────────────────────────────────────
-- User-submitted feedback. Immutable once submitted (no update policy).
-- session_id and user_id use ON DELETE SET NULL so feedback is kept
-- even if the user or session is deleted.

create table public.feedback (
    id           uuid        default gen_random_uuid() primary key,
    user_id      uuid        references auth.users(id) on delete set null,
    type         text        not null check (type in (
                                 'bug',               -- something crashed or broke
                                 'wrong_solution',    -- AI gave an incorrect solution
                                 'wrong_complexity',  -- AI complexity analysis was wrong
                                 'poor_explanation',  -- AI explanation was unclear or unhelpful
                                 'false_test_result', -- test runner passed/failed incorrectly
                                 'feature_request',   -- suggest something new
                                 'ui_issue',          -- interface is confusing or broken
                                 'general',           -- anything else
                                 'praise'             -- positive feedback
                             )),
    message      text        not null,
    session_id   uuid        references public.chat_sessions(id) on delete set null,
    problem_slug text,
    app_version  text,
    status       text        not null default 'new' check (status in ('new', 'reviewed', 'resolved')),
    created_at   timestamptz default now() not null
);

alter table public.feedback enable row level security;
create policy "insert own" on public.feedback for insert with check (auth.uid() = user_id);
create policy "select own" on public.feedback for select using (auth.uid() = user_id);


-- ── 5. problem_notes ─────────────────────────────────────────
-- User's personal markdown notes per problem, separate from the AI chat.

create table public.problem_notes (
    id           uuid        default gen_random_uuid() primary key,
    user_id      uuid        references auth.users(id) on delete cascade not null,
    problem_slug text        not null,
    content      text        not null default '',
    updated_at   timestamptz default now() not null,
    unique(user_id, problem_slug)
);

alter table public.problem_notes enable row level security;
create policy "select own" on public.problem_notes for select using (auth.uid() = user_id);
create policy "insert own" on public.problem_notes for insert with check (auth.uid() = user_id);
create policy "update own" on public.problem_notes for update using (auth.uid() = user_id);
create policy "delete own" on public.problem_notes for delete using (auth.uid() = user_id);


-- ── 6. bookmarks ─────────────────────────────────────────────
-- Problems the user saves for later review.

create table public.bookmarks (
    id           uuid        default gen_random_uuid() primary key,
    user_id      uuid        references auth.users(id) on delete cascade not null,
    problem_slug text        not null,
    difficulty   text,
    created_at   timestamptz default now() not null,
    unique(user_id, problem_slug)
);

alter table public.bookmarks enable row level security;
create policy "select own" on public.bookmarks for select using (auth.uid() = user_id);
create policy "insert own" on public.bookmarks for insert with check (auth.uid() = user_id);
create policy "delete own" on public.bookmarks for delete using (auth.uid() = user_id);


-- ── 7. user_stats ────────────────────────────────────────────
-- Pre-aggregated stats per user. Updated on each solve to avoid
-- computing streaks and totals live on every screen load.

create table public.user_stats (
    user_id          uuid    primary key references auth.users(id) on delete cascade,
    total_solved     integer default 0 not null,
    easy_solved      integer default 0 not null,
    medium_solved    integer default 0 not null,
    hard_solved      integer default 0 not null,
    current_streak   integer default 0 not null,
    longest_streak   integer default 0 not null,
    last_active_date date,
    total_sessions   integer default 0 not null,
    updated_at       timestamptz default now() not null
);

alter table public.user_stats enable row level security;
create policy "select own" on public.user_stats for select using (auth.uid() = user_id);
create policy "insert own" on public.user_stats for insert with check (auth.uid() = user_id);
create policy "update own" on public.user_stats for update using (auth.uid() = user_id);
