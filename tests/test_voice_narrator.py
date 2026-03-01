"""Tests for skills/voice_narrator/server.py — ElevenLabs TTS narration.

ElevenLabs is mocked via sys.modules patching so tests run without a real key
and without network access.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_elevenlabs_mocks(audio_bytes: bytes = b"x" * 8000):
    """Return (mock_el_module, mock_el_client_module, mock_client_instance)."""
    mock_client_instance = MagicMock()
    mock_client_instance.text_to_speech.convert.return_value = iter([audio_bytes])

    mock_el_client_mod = MagicMock()
    mock_el_client_mod.ElevenLabs = MagicMock(return_value=mock_client_instance)

    mock_el_mod = MagicMock()
    mock_el_mod.play = MagicMock()

    return mock_el_mod, mock_el_client_mod, mock_client_instance


# ── no API key ────────────────────────────────────────────────────────────────


def test_narrate_no_api_key_returns_skip(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    from skills.voice_narrator.server import narrate
    result = narrate("Hello world")
    assert "skipped" in result.lower()
    assert "ELEVENLABS_API_KEY" in result


# ── success path (mocked ElevenLabs) ──────────────────────────────────────────


def test_narrate_success_returns_playing_string(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
    mock_el, mock_el_client, mock_instance = _make_elevenlabs_mocks(b"a" * 16000)
    monkeypatch.setitem(sys.modules, "elevenlabs", mock_el)
    monkeypatch.setitem(sys.modules, "elevenlabs.client", mock_el_client)

    from skills.voice_narrator.server import narrate
    result = narrate("Use a hash map for constant lookup.")
    assert "playing" in result


def test_narrate_calls_elevenlabs_with_correct_api_key(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "my-real-key")
    mock_el, mock_el_client, _ = _make_elevenlabs_mocks()
    monkeypatch.setitem(sys.modules, "elevenlabs", mock_el)
    monkeypatch.setitem(sys.modules, "elevenlabs.client", mock_el_client)

    from skills.voice_narrator.server import narrate
    narrate("Testing key forwarding.")
    mock_el_client.ElevenLabs.assert_called_once_with(api_key="my-real-key")


def test_narrate_mentor_voice_id(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    mock_el, mock_el_client, mock_instance = _make_elevenlabs_mocks()
    monkeypatch.setitem(sys.modules, "elevenlabs", mock_el)
    monkeypatch.setitem(sys.modules, "elevenlabs.client", mock_el_client)

    from skills.voice_narrator.server import narrate, _VOICE_MAP
    narrate("hello", voice_type="mentor")
    call_kwargs = mock_instance.text_to_speech.convert.call_args[1]
    assert call_kwargs["voice_id"] == _VOICE_MAP["mentor"]


def test_narrate_coach_voice_id(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    mock_el, mock_el_client, mock_instance = _make_elevenlabs_mocks()
    monkeypatch.setitem(sys.modules, "elevenlabs", mock_el)
    monkeypatch.setitem(sys.modules, "elevenlabs.client", mock_el_client)

    from skills.voice_narrator.server import narrate, _VOICE_MAP
    narrate("hello", voice_type="coach")
    call_kwargs = mock_instance.text_to_speech.convert.call_args[1]
    assert call_kwargs["voice_id"] == _VOICE_MAP["coach"]


def test_narrate_unknown_voice_type_falls_back_to_mentor(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    mock_el, mock_el_client, mock_instance = _make_elevenlabs_mocks()
    monkeypatch.setitem(sys.modules, "elevenlabs", mock_el)
    monkeypatch.setitem(sys.modules, "elevenlabs.client", mock_el_client)

    from skills.voice_narrator.server import narrate, _VOICE_MAP
    narrate("hello", voice_type="does-not-exist")
    call_kwargs = mock_instance.text_to_speech.convert.call_args[1]
    assert call_kwargs["voice_id"] == _VOICE_MAP["mentor"]


def test_narrate_play_is_called_in_thread(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    mock_el, mock_el_client, _ = _make_elevenlabs_mocks(b"z" * 3200)
    monkeypatch.setitem(sys.modules, "elevenlabs", mock_el)
    monkeypatch.setitem(sys.modules, "elevenlabs.client", mock_el_client)

    from skills.voice_narrator.server import narrate
    narrate("Narrate this.")
    # play() should be called by the daemon thread; give it a moment
    import time
    time.sleep(0.1)
    mock_el.play.assert_called_once()


# ── error handling ────────────────────────────────────────────────────────────


def test_narrate_elevenlabs_exception_returns_error(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")

    mock_el_client_mod = MagicMock()
    mock_el_client_mod.ElevenLabs.side_effect = RuntimeError("network down")
    mock_el_mod = MagicMock()
    monkeypatch.setitem(sys.modules, "elevenlabs", mock_el_mod)
    monkeypatch.setitem(sys.modules, "elevenlabs.client", mock_el_client_mod)

    from skills.voice_narrator.server import narrate
    result = narrate("This will fail.")
    assert "error" in result.lower()
    assert "network down" in result


# ── voice map integrity ───────────────────────────────────────────────────────


def test_voice_map_has_three_entries():
    from skills.voice_narrator.server import _VOICE_MAP
    assert set(_VOICE_MAP.keys()) == {"mentor", "coach", "excited"}


def test_voice_map_values_are_nonempty_strings():
    from skills.voice_narrator.server import _VOICE_MAP
    for key, val in _VOICE_MAP.items():
        assert isinstance(val, str) and len(val) > 0, f"Bad voice_id for {key}"
