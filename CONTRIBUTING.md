# 🤝 Contributing to LeetVibe

Thanks for your interest in making LeetVibe better! Contributions of all kinds are welcome — bug reports, feature ideas, code, and especially new Playbook content.


## 🐛 Reporting Bugs & Suggesting Features

Open an issue on the [issue tracker](https://github.com/Hiba-Chaabnia/LeetVibe/issues). For bugs, please include:

- Your OS and terminal emulator (LeetVibe is a full-screen TUI — rendering issues are often terminal-specific)
- Python version (`python --version`) and LeetVibe version (`pip show leetvibe`)
- Steps to reproduce, and what you expected vs. what happened
- Any traceback shown when the app exits


## 🛠️ Development Setup

**Requirements:** Python 3.11+ and [uv](https://docs.astral.sh/uv/) ≥ 0.6.0

```bash
git clone https://github.com/Hiba-Chaabnia/LeetVibe.git
cd LeetVibe
uv sync
```

Copy `.env.example` to `.env` and fill in your keys:

```
MISTRAL_API_KEY=your_key_here      # required — https://console.mistral.ai
ELEVENLABS_API_KEY=your_key_here   # optional — voice narration only
```

Model and voice settings live in `config.yaml` at the repo root (committed — no secrets), and take effect on the next launch:

```yaml
mistral:
  model: "mistral-large-latest"
  qa_model: "mistral-small-latest"   # used by ConceptAgent for follow-up Q&A

elevenlabs:
  voice_id: "EXAVITQu4vr4xnSDxMaL"
  enabled: true
```

Then run the app:

```bash
uv run leetvibe
```

Before diving in, read the [Architecture Deep Dive](docs/ARCHITECTURE.md) — it opens with a system diagram and a map of the codebase, then covers the agent loop, system prompts, and voice pipeline internals. In short: screens live in `leetvibe/ui/screens/`, the AI agents in `leetvibe/ai/agent.py`, and their tool skills in `leetvibe/ai/skills/`.


## 📖 Contributing a Playbook Topic

The Playbook's 52 algorithm topics live in `leetvibe/data/topics/`, one module per topic. Each module exposes a `TOPIC` dict that must follow the schema the playbook UI depends on:

- **Required fields:** `title`, `slug`, `recognize`, `intuition`, `diagram`, `patterns`, `variants`, `pitfalls`, `edge_cases`, `confusion`, `follow_up_questions`, `time`, `space`
- **Bullet fields** (`intuition`, `variants`, `pitfalls`, `edge_cases`, `follow_up_questions`) must start each line with a `•` bullet
- `confusion` is a box-drawn table distinguishing the pattern from its look-alikes

The easiest way to get the shape right is to copy an existing topic (e.g. `two_pointers.py`) and rewrite its content. When adding a **new** topic (rather than improving an existing one), also register it in `TOPIC_META` in `leetvibe/data/topics/_metadata.py` (category, tier, and parent topic).

Before opening a PR, launch the app and open your topic in the Playbook to confirm every section renders correctly.


## 🔀 Pull Requests

1. Fork the repo and create a branch off `main`
2. Keep each PR focused on one change
3. Follow the existing commit style — [Conventional Commits](https://www.conventionalcommits.org/) with a scope, e.g.:
   - `feat(playbook): add segment tree lazy propagation variant`
   - `fix(ui): prevent crash when notes panel is empty`
4. Describe **what** the change does and **why** in the PR body; add a screenshot or recording for UI changes

Match the style of the surrounding code — the project has no enforced linter, so consistency with what's already there is the rule.

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
