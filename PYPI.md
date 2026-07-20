<div align="center">
  <a href="https://github.com/Hiba-Chaabnia/LeetVibe">
    <img alt="LeetVibe" src="https://raw.githubusercontent.com/Hiba-Chaabnia/LeetVibe/main/assets/logo.png" width="380" />
  </a>

  <h3>Your AI pair programmer for LeetCode — a senior engineer in your terminal.</h3>

  <p>
    <a href="https://pypi.org/project/leetvibe/"><img src="https://img.shields.io/pypi/v/leetvibe" alt="PyPI" /></a>
    <a href="https://pepy.tech/project/leetvibe"><img src="https://img.shields.io/pepy/dt/leetvibe" alt="Downloads" /></a>
    <a href="https://pypi.org/project/leetvibe/"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+" /></a>
    <a href="https://github.com/Hiba-Chaabnia/LeetVibe/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT" /></a>
  </p>

  <p>
    <a href="https://github.com/Hiba-Chaabnia/LeetVibe#-quickstart">Quickstart</a> ·
    <a href="https://github.com/Hiba-Chaabnia/LeetVibe#-the-three-modes">Modes</a> ·
    <a href="https://github.com/Hiba-Chaabnia/LeetVibe#-the-playbook">Playbook</a> ·
    <a href="https://github.com/Hiba-Chaabnia/LeetVibe#-under-the-hood">Under the Hood</a> ·
    <a href="https://github.com/Hiba-Chaabnia/LeetVibe#-faq--troubleshooting">FAQ</a>
  </p>
</div>


Stop grinding alone. LeetVibe puts a senior engineer in your terminal who can teach, coach, or interview you — depending on how much help you want today.

## 🧠 Three Modes

| | 🎓 Learn | 🤝 Pair Programming | 🎤 Interview |
|---|---|---|---|
| Who codes first | Vibe | You | — (verbal only) |
| What happens | Vibe solves it live in a strict 7-step workflow — reasoning out loud, running real code, measuring complexity | Vibe tests your attempt, diagnoses exact lines, and coaches you with Socratic hints | Alex, a senior engineer, runs a realistic mock interview — with voice via ElevenLabs |
| Reveals optimal | ✅ always | ✅ after coaching | ❌ never |

Every session is a live conversation: ask follow-up questions, push back, or go deeper at any point. The AI executes your code against real test cases, measures Big-O complexity from the AST, and explains algorithm patterns step by step.



## 📖 Playbook

An in-terminal algorithm reference covering **52 patterns** — from Arrays and Binary Search to Network Flow, Segment Tree, and Digit DP. Every topic page breaks down:

- 🧠 The **intuition** behind the technique, and how to recognise when to use it
- 📐 Annotated **code templates** and their variants
- ⚠️ **Pitfalls, edge cases**, and the pattern it's most often confused with
- 🎤 The **follow-up questions** an interviewer would ask next

Ask AI about any pattern without leaving the guide, keep per-topic notes, and export it all to DOCX.

## ✨ More Features

- 📚 **Problem browser** — filter by difficulty, topic, or solved status; free-text search across 2,800+ LeetCode problems
- 💡 **Built-in solutions** — 1,900+ problems ship with a written solution and explanation; a "Has Solution" filter surfaces them
- ✏️ **Inline code editor** — write Python in the terminal and run it against the problem's test cases without leaving the app
- 📋 **Live test results** — pass/fail output per test case, run in an isolated subprocess with a timeout so an infinite loop can't hang the session
- 📊 **Statistics screen** — session counts, solved problem tracking, progress over time
- ☁️ **Cloud sync** — optional account to persist progress across machines
- 🧙 **Onboarding wizard** — first-run setup collects API keys interactively; nothing to configure by hand


## 🚀 Getting Started

Requires **Python 3.11+**.

```bash
# with uv (recommended)
uv tool install leetvibe

# with pip
pip install leetvibe
```

```bash
leetvibe
```

The onboarding wizard opens automatically on first launch. It will ask for your **Mistral API key** (required) and optionally your **ElevenLabs key** for voice narration. Keys are saved to `~/.leetvibe/.env` and never touched again.

- 🔑 Get a Mistral key: https://console.mistral.ai
- 🔊 Get an ElevenLabs key: https://elevenlabs.io *(optional)*

![LeetVibe Onboarding](https://raw.githubusercontent.com/Hiba-Chaabnia/LeetVibe/main/assets/onboarding.gif)


## 📚 Full Documentation

Architecture diagrams, the agent loop, keyboard shortcuts, and the full mode walkthroughs live in the [GitHub README](https://github.com/Hiba-Chaabnia/LeetVibe). Contributions are welcome — see the [Contribution Guide](https://github.com/Hiba-Chaabnia/LeetVibe/blob/main/CONTRIBUTING.md).


## 💬 Feedback

Found a wrong solution, an unclear explanation, or have a feature idea? Sign in and hit the **Feedback** button on any problem screen — it arrives tagged with the problem you were on. Or [open an issue](https://github.com/Hiba-Chaabnia/LeetVibe/issues) on GitHub.


## 📄 License

MIT © 2026 Hiba Chaabnia — see [LICENSE](https://github.com/Hiba-Chaabnia/LeetVibe/blob/main/LICENSE) for the full text.
