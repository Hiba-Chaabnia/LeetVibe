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

# Serialise all audio playback so step-7 narration and the recap never overlap
_AUDIO_LOCK = threading.Lock()


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
        import numpy as np
        import sounddevice as sd
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=api_key)
        # Request raw PCM so we don't need ffmpeg to decode MP3
        audio_gen = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_flash_v2_5",
            output_format="pcm_22050",
        )
        audio_bytes = b"".join(audio_gen)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # Play in a daemon thread; lock ensures sequential playback across callers
        def _play() -> None:
            with _AUDIO_LOCK:
                try:
                    sd.play(audio_array, samplerate=22050)
                    sd.wait()
                except Exception:
                    pass

        t = threading.Thread(target=_play, daemon=True)
        t.start()
        duration = len(audio_bytes) / (22050 * 2)
        return f"playing {duration:.1f}s of audio"
    except Exception as exc:
        return f"error: {exc}"


def narrate_blocking(text: str, voice_type: str = "mentor") -> str:
    """Convert text to speech and block the caller until playback completes.

    Unlike narrate(), this acquires _AUDIO_LOCK in the caller's thread so
    multiple sequential calls play in strict order with no overlap.
    voice_type: mentor | coach | excited
    Returns a status string.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        return "skipped: ELEVENLABS_API_KEY not set"

    voice_id = _VOICE_MAP.get(voice_type, _VOICE_MAP["mentor"])

    try:
        import numpy as np
        import sounddevice as sd
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=api_key)
        audio_gen = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_flash_v2_5",
            output_format="pcm_22050",
        )
        audio_bytes = b"".join(audio_gen)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        with _AUDIO_LOCK:
            sd.play(audio_array, samplerate=22050)
            sd.wait()

        duration = len(audio_bytes) / (22050 * 2)
        return f"played {duration:.1f}s of audio"
    except Exception as exc:
        return f"error: {exc}"


def stop_playback() -> None:
    """Stop any currently playing audio immediately."""
    try:
        import sounddevice as sd
        sd.stop()
    except Exception:
        pass


if __name__ == "__main__":
    mcp.run(transport="stdio")
