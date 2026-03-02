-- ============================================================
-- LeetVibe — Migration 003: remove email confirmation blockage
-- Run this in: Supabase Dashboard → SQL Editor → New query
--
-- Email confirmation has been disabled in Supabase settings.
-- This confirms all existing accounts that were created before
-- that change, removing the sign-in blockage for those users.
-- No accounts are deleted.
-- ============================================================

UPDATE auth.users
SET email_confirmed_at = now()
WHERE email_confirmed_at IS NULL;
