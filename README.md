# 🎯 LeetVibe

> **Your AI pair programmer for LeetCode — powered by Mistral Vibe**

Stop grinding alone. LeetVibe puts a senior engineer in your terminal who can teach, coach, or interview you — depending on how much help you want today.

---

## 🎬 Demo

### Full App Demo

[![LeetVibe Demo](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)

> Click the thumbnail to watch the full demo on YouTube.

### ⚙️ Onboarding Setup

![LeetVibe Onboarding](assets/onboarding.gif)

---

## 🧠 How It Works

LeetVibe is built on **Mistral Vibe** — an autonomous AI agent that doesn't just answer questions, it reasons, runs code, measures complexity, and explains its thinking step by step. Every session is a live conversation: you can ask follow-up questions, push back, or go deeper at any point.

**Three modes. Three different relationships with the AI.**

```mermaid
graph LR
    You(["🧑‍💻 You"]) --> Learn["🎓 Learn\nWatch Vibe solve it"]
    You --> Pair["🤝 Pair Programming\nVibe reviews your attempt"]
    You --> Interview["🎤 Interview\nAlex tests you live"]

    Learn & Pair --> Agent["🤖 Mistral Vibe\nmistral-large-latest"]
    Interview --> Alex["🎙️ Alex\nAI interviewer"]
    Alex --> Agent

    Agent --> Tools["🔧 Agent Tools"]
    Tools --> RunCode["▶ run_code\nexecute & test"]
    Tools --> Complexity["📊 analyze_complexity\nAST inspection"]
    Tools --> Explain["📖 explain_approach\nalgorithm walkthrough"]

    Agent --> Voice["🔊 ElevenLabs\nvoice narration"]
```

---

## 🎓 Learn Mode

*"Teach me how to solve this."*

Mistral Vibe takes the wheel. It walks through the problem using a strict **7-step workflow** — reasoning out loud, running real code, and narrating every decision. You watch, listen, and absorb.

| Step | What Vibe Does |
|------|---------------|
| 1️⃣ Understand | Restates the problem, identifies edge cases and algorithm family |
| 2️⃣ Brute Force | Writes the simplest correct solution and runs it against test cases |
| 3️⃣ Analyse | Calls `analyze_complexity` — "This is O(n²) because of the nested loops" |
| 4️⃣ Key Insight | Names the one idea that eliminates the bottleneck |
| 5️⃣ Optimal | Writes the optimised solution and validates it with `run_code` |
| 6️⃣ Compare | "We improved from O(n²) → O(n) by eliminating redundant lookups" |
| 7️⃣ Walkthrough | Calls `explain_approach` for a structured pattern breakdown |

> Vibe never skips a step, even for trivial problems. If a test fails, it debugs and fixes before moving on.

---

## 🤝 Pair Programming Mode

*"Review my attempt and guide me to the optimal."*

You write first. Vibe reviews. It follows a **6-step coaching workflow** designed to push you toward the answer — not hand it to you.

| Step | What Vibe Does |
|------|---------------|
| 1️⃣ Test | Runs your code: "Your solution passes 3/5 test cases" |
| 2️⃣ Diagnose | Points to exact lines — bugs, inefficiencies, edge case gaps |
| 3️⃣ Analyse | Measures your complexity: "Your solution is O(n²) because..." |
| 4️⃣ Hint | Nudges without revealing: "What data structure gives O(1) lookup?" |
| 5️⃣ Optimal | Only now reveals the full solution with line-by-line explanation |
| 6️⃣ Compare | Side-by-side: your approach vs optimal, with the key insight named |

---

## 🎤 Interview Mode

*"Test me like it's a real interview."*

Meet **Alex** — a senior software engineer who conducts 30-minute mock technical interviews. No hints unless you're stuck. No code written for you. Just a realistic conversation.

**Alex's rules:**
- 🤝 Greets you once, states the problem, asks for your approach
- 🔍 Probes with *"What's the time complexity?"* / *"Any edge cases?"* / *"Can you do better?"*
- 💡 Gives **one small hint** if you're stuck, then waits
- ✅ Closes with brief feedback on correctness, complexity, and one thing to improve
- 🔇 Never re-introduces himself on follow-up turns
- 🚫 Never writes code, never reveals the optimal solution unprompted

His opening monologue plays as speech via ElevenLabs so the session feels live from the first second.

---

## 🆚 Mode Comparison

| | 🎓 Learn | 🤝 Pair Programming | 🎤 Interview |
|---|---|---|---|
| Who codes first | Vibe | You | — (verbal only) |
| Tools enabled | ✅ run_code, complexity, explain | ✅ run_code, complexity, explain | ❌ none |
| Voice narration | ✅ auto after each step | ✅ on demand | ✅ opening monologue |
| Follow-up chat | ✅ | ✅ | ✅ |
| Gives hints | — | ✅ Socratic nudges | ✅ one hint only |
| Reveals optimal | ✅ always | ✅ after coaching | ❌ never |
| Response length | Long — full explanations | Long — detailed review | Short — 2–4 sentences |

---

## ✨ More Features

- 📚 **Challenge browser** — filter by difficulty, topic, or solved status; free-text search across hundreds of LeetCode problems
- ✏️ **Inline code editor** — write Python in the terminal with syntax highlighting and run it against the problem's test cases without leaving the app
- 📋 **Live test results** — pass/fail output per test case shown immediately
- 💡 **Solution tab** — reference solutions when they exist in the problem data
- 📊 **Statistics screen** — session counts, solved problem tracking, progress over time
- ☁️ **Cloud sync** — optional account (email/password or Google OAuth) to persist progress across machines
- 🧙 **Onboarding wizard** — first-run setup collects API keys and account details interactively; nothing to configure by hand

---

## 🚀 Getting Started

### Install from PyPI

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

---

### Install from Source

**Requirements:** Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/hibachaabnia/leetvibe.git
cd leetvibe
uv sync
uv run leetvibe
```

For local development, copy `.env.exemple` to `.env` and fill in your keys:

```
MISTRAL_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here   # optional
```

---

## 🗺️ Navigation

```mermaid
flowchart TD
    Launch(["▶ leetvibe"])
    Launch --> Check{"MISTRAL_API_KEY\nset?"}
    Check -- "No — first run" --> Onboard
    Check -- "Yes" --> Home

    subgraph Onboard["🧙 Onboarding Wizard"]
        W["Welcome"] --> AK["Mistral API Key"]
        AK --> EL["ElevenLabs Key\n(optional)"]
        EL --> AC["Account Setup\n(optional)"]
    end

    Onboard --> Home["🏠 Home"]

    Home -- "1 · Learn" --> LL["Challenge List"]
    Home -- "2 · Pair" --> CL["Challenge List"]
    Home -- "3 · Interview" --> IL["Challenge List"]
    Home -- "4 · Stats" --> Stats["📊 Statistics"]
    Home -- "5 · Account" --> Login["🔐 Login / Sign Up"]
    Login -- result --> Home

    LL & CL --> Detail["Challenge Detail\ncode editor + tests"]
    Detail -- "Submit" --> Session["💬 Agent Session\nstreaming chat"]
    IL --> Session

    Session -- "Esc" --> CL2["Challenge List"]
    Detail -- "Esc" --> CL2
    CL2 -- "Esc" --> Home
```

**Keyboard shortcuts:**

| Key | Action |
|-----|--------|
| `1`–`6` | Home screen quick-select |
| `Enter` | Open / confirm |
| `Esc` | Go back |
| `Ctrl+D` | Toggle description panel (+ Alex's opening in Interview) |
| `Ctrl+V` | Toggle voice narration |
| `Ctrl+C` | Copy last code block |
| `Ctrl+Q` | Quit from anywhere |

---

## 🏗️ Architecture

```mermaid
graph TD
    User(["🧑‍💻 User"])

    subgraph TUI["Textual TUI"]
        Home["🏠 Home"]
        ChallengeList["📋 Challenge List"]
        Detail["✏️ Challenge Detail"]
        AgentSession["💬 Agent Session"]
        Stats["📊 Statistics"]
        Login["🔐 Login"]
    end

    subgraph Agent["AI Agent — vibe_agent.py"]
        VibeAgent["🤖 VibeAgent\nstreaming tool-calling loop"]
    end

    subgraph Skills["🔧 MCP Skills — skills/"]
        TestRunner["▶ test_runner"]
        Complexity["📊 complexity_analyzer"]
        Teaching["📖 teaching_mode"]
        Voice["🔊 voice_narrator"]
    end

    subgraph External["☁️ External Services"]
        MistralAPI["Mistral AI API"]
        ElevenLabsAPI["ElevenLabs API"]
        SupabaseDB["Supabase"]
    end

    Problems[("📁 problems/\nJSON files")]
    Audio["🔊 System Audio"]

    User --> Home
    Home --> ChallengeList & Stats & Login
    ChallengeList --> Detail & AgentSession
    Detail --> AgentSession

    AgentSession --> VibeAgent
    VibeAgent --> MistralAPI
    VibeAgent --> TestRunner & Complexity & Teaching & Voice

    Voice --> ElevenLabsAPI --> Audio
    Login & Stats & ChallengeList --> SupabaseDB
    ChallengeList --> Problems
```

**Project layout:**

```
leetvibe/
├── cli.py                    Entry point
├── config.py                 Loads config.yaml + .env
├── vibe_agent.py             Mistral agent — streaming tool-calling loop
├── challenge_loader.py       Reads problem JSONs from problems/
├── code_runner.py            Sandboxed Python test execution
├── cloud/
│   ├── auth.py               Supabase auth (email + Google OAuth)
│   └── db.py                 Cloud sync — solved slugs, sessions
└── textual_ui/
    ├── screens/              home, challenge_list, challenge_detail,
    │                         agent_session, stats, login
    └── widgets/              banner, challenge_table, status_bar

skills/
├── test_runner/              Execute code against test cases
├── complexity_analyzer/      AST-based O(n) analysis
├── teaching_mode/            Algorithm pattern explanations
└── voice_narrator/           ElevenLabs TTS playback

problems/
├── easy/ · medium/ · hard/   Challenge JSON files
```

---

## ⚙️ How Mistral Vibe Powers LeetVibe

Every session runs through `VibeAgent` — a hand-rolled tool-calling loop built directly on Mistral's streaming API. No LangChain, no wrappers. Just raw streaming with full control over what renders in the terminal.

### The Agent Loop

```mermaid
flowchart TD
    Start(["solve_streaming(challenge, mode)"])

    Start --> SelectPrompt{mode?}
    SelectPrompt -- "learn" --> SP["📜 SYSTEM_PROMPT\n7-step workflow"]
    SelectPrompt -- "coach" --> CP["📜 COACH_PROMPT\nreview + guide"]
    SelectPrompt -- "interview" --> IP["📜 INTERVIEW_PROMPT\nmock interviewer"]

    SP & CP --> BuildMsg["Build messages\n+ tools enabled"]
    IP --> BuildMsgNoTools["Build messages\ntools disabled"]

    BuildMsg & BuildMsgNoTools --> Stream

    subgraph Loop["🔁 Tool-calling Loop — max 20 turns"]
        Stream["client.chat.stream(messages, tools)"]
        Collect["Collect response\ntext → yield to TUI live\ntool calls → accumulate"]
        Stream --> Collect
        Collect --> HasTools{"Tool calls?"}

        HasTools -- "No" --> Save["Append to history → exit"]
        HasTools -- "Yes" --> Exec["Execute tool\ndirect Python import"]
        Exec --> AppendResult["Append result to history"]
        AppendResult --> Stream
    end

    Save --> Done(["✅ Session complete"])
```

### System Prompts

Each mode gets a completely different personality baked into the system prompt:

- 📜 **`SYSTEM_PROMPT`** — instructs Vibe to follow the 7-step workflow exactly, think out loud before every code block, and never skip a step even for trivial problems. Uses Rich markup (`[bold]`, `[dim]`) rendered directly by Textual.
- 📜 **`COACH_PROMPT`** — instructs Vibe to test the user's code first, be specific about buggy lines, give Socratic hints before revealing anything, and frame all feedback as encouragement.
- 📜 **`INTERVIEW_PROMPT`** — instructs Alex to speak in 2–4 sentences only, never re-introduce himself, never write code, and give exactly one hint when the candidate is stuck. Tool calls are **disabled entirely** in this mode.

### Agent Tools

| 🔧 Tool | Skill | What It Does |
|---------|-------|-------------|
| `run_code` | `test_runner` | Executes Python code against test cases in a sandboxed namespace with stdlib pre-imported. Returns pass/fail per case. |
| `analyze_complexity` | `complexity_analyzer` | Walks the AST — counts loop nesting depth, detects sorting calls, memoization decorators, and dynamic allocations. Returns `{time, space, explanation}`. |
| `explain_approach` | `teaching_mode` | Generates a structured 6-step walkthrough for 15+ algorithm patterns (two-pointer, DP, sliding window, BFS, heap, trie…). |

### Full Session Flow

```mermaid
sequenceDiagram
    participant U as 🧑‍💻 User
    participant UI as AgentSession
    participant A as VibeAgent
    participant M as Mistral API
    participant S as MCP Skills
    participant EL as ElevenLabs

    U->>UI: Select challenge (Learn mode)
    UI->>A: solve_streaming(challenge, mode="learn")
    A->>M: chat.stream(messages, tools=_TOOLS)

    loop Streaming
        M-->>A: text chunk
        A-->>UI: yield → rendered live in terminal
    end

    M-->>A: tool_call: run_code(code, snippet)
    A->>S: test_runner.run_code()
    S-->>A: {all_passed: true, cases: [...]}
    A->>M: append result → continue

    M-->>A: tool_call: analyze_complexity(code)
    A->>S: complexity_analyzer.analyze_complexity()
    S-->>A: {time: "O(n)", space: "O(1)"}
    A->>M: append result → continue

    M-->>A: tool_call: explain_approach(...)
    A->>S: teaching_mode.explain_approach()
    S-->>A: structured walkthrough text
    A->>M: append result → continue

    M-->>A: final text (no tool calls)
    A->>A: save to message history
    A->>EL: narrate(explanation, voice_type="mentor")
    EL-->>U: 🔊 audio playback
```

---

## 🔊 How ElevenLabs Powers the Voice

Voice narration is handled by the `voice_narrator` skill. It converts text to raw PCM audio via ElevenLabs and plays it directly through `sounddevice` — no ffmpeg required.

### Voice Personas

| Persona | Voice | Used In |
|---------|-------|---------|
| `mentor` | Sarah | Learn — calm, instructive |
| `coach` | Adam | Pair Programming — encouraging |
| `excited` | Elli | High-energy moments |

### Audio Pipeline

```mermaid
sequenceDiagram
    participant A as VibeAgent
    participant VN as voice_narrator
    participant EL as ElevenLabs API
    participant SD as sounddevice

    A->>VN: narrate(text, voice_type="mentor")
    VN->>EL: text_to_speech.convert()<br/>model=eleven_flash_v2_5 · format=pcm_22050
    EL-->>VN: raw PCM bytes (22050 Hz, 16-bit)
    VN->>VN: np.frombuffer(bytes, dtype=np.int16)
    Note over VN: Acquire _AUDIO_LOCK<br/>prevents overlapping playback
    VN->>SD: sd.play(audio_array, samplerate=22050)
    SD-->>VN: sd.wait()
    VN-->>A: "playing X.Xs of audio"
    Note over VN,SD: Navigating away → stop_playback()<br/>calls sd.stop() → playback ends immediately
```

**Two playback modes:**
- 🔄 `narrate()` — fires a background thread, returns immediately. Used during agent tool loops so the AI keeps going while audio plays.
- ⏸️ `narrate_blocking()` — blocks until audio finishes. Used for Alex's interview opening so the session feels live before you type.

---

## 🔐 Auth Flow

Optional cloud account to sync your progress. Two sign-in methods via Supabase:

```mermaid
sequenceDiagram
    participant User
    participant App as LeetVibe TUI
    participant Auth as cloud/auth.py
    participant Supabase
    participant Browser
    participant Pages as GitHub Pages (OAuth relay)

    rect rgb(30, 30, 60)
        Note over User,Supabase: 📧 Email / Password
        User->>App: Enter email + password
        App->>Auth: sign_in(email, password)
        Auth->>Supabase: auth.sign_in_with_password()
        Supabase-->>Auth: {access_token, refresh_token}
        Auth->>Auth: save → ~/.leetvibe/session.json
        Auth-->>App: AuthResult(ok=True)
    end

    rect rgb(20, 50, 30)
        Note over User,Pages: 🌐 Google OAuth
        User->>App: Click "Sign in with Google"
        App->>Auth: start_google_auth()
        Auth->>Auth: bind ephemeral port on 127.0.0.1
        Auth->>Supabase: sign_in_with_oauth(provider="google")
        Supabase-->>Auth: OAuth URL
        Auth->>Auth: start one-shot HTTP callback server
        App->>Browser: open OAuth URL
        User->>Browser: complete Google sign-in
        Browser->>Pages: redirect with tokens
        Pages->>Auth: POST → http://127.0.0.1:{port}/result
        Auth->>Supabase: set_session(tokens)
        Auth->>Auth: save → ~/.leetvibe/session.json
        Auth-->>App: AuthResult(ok=True)
    end
```

---

## 🔧 Configuration

`config.yaml` (committed — no secrets):
```yaml
mistral:
  model: "mistral-large-latest"

elevenlabs:
  voice_id: "EXAVITQu4vr4xnSDxMaL"
  enabled: true
```

`~/.leetvibe/.env` (created by the wizard — never committed):
```
MISTRAL_API_KEY=your_key
ELEVENLABS_API_KEY=your_key    # optional
```

The config loader checks `~/.leetvibe/.env` → project `.env` → environment variables, in that order.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `mistralai` | Mistral AI SDK — streaming chat + tool calling |
| `elevenlabs` | Text-to-speech |
| `textual` | Terminal UI framework |
| `sounddevice` + `numpy` | PCM audio playback |
| `supabase` | Auth + cloud sync |
| `mcp` | MCP skill server infrastructure |
| `python-dotenv` · `pyyaml` | Config loading |
| `click` | CLI entry point |
| `rich` | Terminal formatting |

---

## 📄 License

MIT © 2026 Hiba Chaabnia
