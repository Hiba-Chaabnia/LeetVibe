# Changelog

All notable changes to LeetVibe are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/).

> **Note:** the latest release published to PyPI is **0.1.1**. Versions 0.1.2–0.1.8 exist in this repository but have not been published yet.


## [0.1.8] — 2026-03-29

### Added
- Playbook topics deeply enriched — intuition, ASCII diagrams, variants, pitfalls, edge cases, confusion tables, and interviewer follow-up questions for all 52 patterns
- Per-topic AI chat (`E`) with history that persists across sessions
- Inline notes panel (`N`), saved per topic
- DOCX export of all topics and notes (`X`)

## [0.1.7] — 2026-03-26

### Changed
- Multi-agent architecture: `VibeAgent` (learn/coach), `InterviewAgent` (mock interviews), `ConceptAgent` (follow-up Q&A on `mistral-small`)
- LLM optimisations: tool-result compression, complexity-analysis caching, sliding-window interview context

### Removed
- Auto-narration in Learn and Pair Programming modes — voice is now Interview-only

## [0.1.6] — 2026-03-25

### Added
- Category and tier filters plus free-text search in the Playbook

### Changed
- Playbook UI overhauled; topics migrated to a structured pattern format

## [0.1.5] — 2026-03-24

### Changed
- Package layout restructured into the `leetvibe/` package; styles cleaned up

## [0.1.4] — 2026-03-23

### Added
- Algorithm Playbook — in-terminal reference guide covering 50+ patterns

## [0.1.3] — 2026-03-19

### Changed
- UI polish, onboarding wizard overhaul, cloud sync improvements

## [0.1.2] — 2026-03-18

### Changed
- Auth and progress sync migrated to Firebase Auth + Firestore

## [0.1.1] — 2026-03-02

Initial public release on PyPI — AI pair-programming TUI for LeetCode: Mistral-powered Learn, Pair Programming, and Interview sessions, problem browser, in-terminal code editor with live test results, ElevenLabs voice narration, and onboarding wizard.
