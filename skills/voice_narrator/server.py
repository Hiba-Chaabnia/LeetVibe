"""MCP skill: voice_narrator — ElevenLabs TTS narration."""


import os
import sys
import threading
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("voice_narrator")

_VOICE_MAP = {
    "mentor": "EXAVITQu4vr4xnSDxMaL",
    "coach": "pNInz6obpgDQGcFmaJgB",
    "excited": "TxGEqnHWrfWFTfGW9XjX",
}


@mcp.tool()
def narrate(text: str, voice_type: str = "mentor") -> str:
    """Convert text to speech via ElevenLabs and play it aloud.

    voice_type: mentor | coach | excited
    Returns a status string describing what was played.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        return "skipped: ELEVENLABS_API_KEY not set"

    voice_id = _VOICE_MAP.get(voice_type, _VOICE_MAP["mentor"])

    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import play

        client = ElevenLabs(api_key=api_key)
        audio_gen = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_flash_v2_5",
        )
        # Materialise the generator so we can measure and replay it
        audio_bytes = b"".join(audio_gen)

        # Play in a daemon thread so the MCP server stays responsive
        def _play() -> None:
            try:
                play(audio_bytes)
            except Exception:
                pass

        t = threading.Thread(target=_play, daemon=True)
        t.start()
        duration = len(audio_bytes) / 16000
        return f"playing {duration:.1f}s of audio"
    except Exception as exc:
        return f"error: {exc}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
