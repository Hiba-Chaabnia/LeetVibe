# Changelog

All notable changes to LeetVibe are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/).

> **Note:** the latest release published to PyPI is **0.1.1**. Versions 0.1.2–0.2.0 exist in this repository but have not been published yet: with major migrations still in flight, releasing would have shipped unstable builds. These changes are instead being held until they are stable and will ship together as one substantial release — **0.2.0**.


## [0.2.0] — 2026-07-20

### Added
- `run_code` executes in an isolated, timed-out subprocess (`run_tests_with_timeout`) — an infinite loop in AI- or user-written code is killed after 10s instead of hanging the session; results now report expected vs. actual output per test case
- Cloud sync hardened: a local offline retry queue (`~/.leetvibe/pending_sync.json`) replays failed message saves at next startup, and sessions are stamped with a prompt fingerprint (`workflow_version`) so a resumed session saved under an old prompt is detected as stale and reset instead of replayed against a contract the model no longer follows
- `ConfirmModal` — a shared yes/no confirmation dialog for destructive actions
- `docs/ARCHITECTURE.md`, `CONTRIBUTING.md`, and `PYPI.md` — internal architecture deep-dive, contribution guide, and a dedicated PyPI-facing readme

### Changed
- Learn/Pair agent workflow restructured: 7 steps (Understand → First Pass → Spot the Bottleneck → The Insight → Optimize → Measure the Gain → Takeaway), each ending its session with a crisp takeaway, one open question for the follow-up chat, and a hidden `Pattern: <slug>` line for mnemonic generation
- Agent responses are markdown-only now (`**bold**`, `` `code` ``) instead of Rich markup tags — `ui/markup.py` normalises whatever slips through regardless
- `ProblemDetailScreen` rebuilt as `ProblemWorkspaceScreen` — a LeetCode-style two-panel layout with a custom top bar
- Chat rendering unified: agent session and Playbook chat now share `ui/widgets/chat_bubbles.py` and `ui/markup.py` instead of separate renderers

### Removed
- The `teaching_mode`/`explain_approach` skill — a tool round-trip whose result was never shown or parsed; the model now ends its session with a plain synthesis paragraph instead

## [0.1.9] — 2026-03-31

### Added
- Automatic update check on launch — a toast notifies when a newer version is available on PyPI
- This changelog

### Changed
- UI code modularized: app entry points moved to `ui/apps/`, and the large screens split into packages (`problem/`, `agent/`, `playbook/`)
- Auth flow (choice / login / signup / Google) extracted into a shared `ui/screens/auth/` package, reused by both onboarding and Home → Account
- `leetvibe --version` now reports the installed package version instead of a hardcoded one
- Packaging metadata cleaned up: dedicated PyPI readme (`PYPI.md`), SPDX license declaration, corrected GitHub repository URLs

### Removed
- Dead code: session logging, orphaned notes modal, legacy login screen, and the unused `pydantic` dependency

## [0.1.8] — 2026-03-29

### Added
- Playbook topics deeply enriched — intuition, ASCII diagrams, variants, pitfalls, edge cases, confusion tables, and interviewer follow-up questions for all 52 patterns
- Per-topic AI chat (`E`) with history that persists across sessions
- Inline notes panel (`N`), saved per topic
- DOCX export of all topics and notes (`X`)

## [0.1.7] — 2026-03-26

### Changed
- Multi-agent architecture: `VibeAgent` (learn/pair), `InterviewAgent` (mock interviews), `ConceptAgent` (follow-up Q&A on `mistral-small`)
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
