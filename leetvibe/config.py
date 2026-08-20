"""LeetVibe config — parse config.yaml + .env once at startup."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values, load_dotenv, unset_key
import yaml

_ROOT = Path(__file__).parent.parent
_CONFIG_PATH = _ROOT / "config.yaml"
_LEETVIBE_HOME = Path.home() / ".leetvibe"
_USER_ENV_PATH = _LEETVIBE_HOME / ".env"   # persistent, user-level
_LOCAL_ENV_PATH = _ROOT / ".env"            # project-level dev fallback
_SETUP_MARKER = _LEETVIBE_HOME / ".setup_complete"


def needs_setup() -> bool:
    """Return True if the onboarding wizard has never been completed.

    The Mistral key is optional (Practice mode needs no AI), so this no
    longer checks for MISTRAL_API_KEY — only whether onboarding itself ran.
    Anyone upgrading from before this marker existed already has a key, so
    back-fill it instead of re-onboarding them.
    """
    if _SETUP_MARKER.exists():
        return False
    if has_mistral_key():
        mark_setup_complete()
        return False
    return True


def mark_setup_complete() -> None:
    _LEETVIBE_HOME.mkdir(parents=True, exist_ok=True)
    _SETUP_MARKER.touch()


def _has_user_key(var_name: str) -> bool:
    """Whether *var_name* is set in the user's own ~/.leetvibe/.env — read
    directly from the file rather than via os.environ, since os.environ is
    process-global and may already hold the project-level dev fallback's
    value (see load_config) from an earlier call elsewhere in the process.
    Deliberately ignores that fallback: it's for local dev convenience
    running real API calls, not something that should drive onboarding or
    menu state.
    """
    return bool(dotenv_values(_USER_ENV_PATH).get(var_name, "").strip())


def has_mistral_key() -> bool:
    return _has_user_key("MISTRAL_API_KEY")


def has_elevenlabs_key() -> bool:
    return _has_user_key("ELEVENLABS_API_KEY")


def remove_mistral_key() -> None:
    unset_key(str(_USER_ENV_PATH), "MISTRAL_API_KEY")
    os.environ.pop("MISTRAL_API_KEY", None)


def remove_elevenlabs_key() -> None:
    unset_key(str(_USER_ENV_PATH), "ELEVENLABS_API_KEY")
    os.environ.pop("ELEVENLABS_API_KEY", None)


_EXPAND_RE = re.compile(r"\$\{(\w+)\}")


def _expand(value: str) -> str:
    """Expand ${VAR} placeholders via os.environ."""
    return _EXPAND_RE.sub(lambda m: os.environ.get(m.group(1), ""), value)


@dataclass
class Config:
    mistral_api_key: str
    mistral_model: str
    mistral_qa_model: str
    elevenlabs_api_key: str
    elevenlabs_voice_id: str


def load_config() -> Config:
    """Load config from config.yaml + .env, expanding env var placeholders."""
    load_dotenv(_USER_ENV_PATH, override=False)
    load_dotenv(_LOCAL_ENV_PATH, override=False)

    raw: dict = {}
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

    def _get(section: str, key: str, default: str = "") -> str:
        val = (raw.get(section) or {}).get(key, default)
        return _expand(str(val)) if val else default

    return Config(
        mistral_api_key=_get("mistral", "api_key") or os.environ.get("MISTRAL_API_KEY", ""),
        mistral_model=_get("mistral", "model", "mistral-large-latest"),
        mistral_qa_model=_get("mistral", "qa_model", "mistral-small-latest"),
        elevenlabs_api_key=_get("elevenlabs", "api_key") or os.environ.get("ELEVENLABS_API_KEY", ""),
        elevenlabs_voice_id=_get("elevenlabs", "voice_id", "EXAVITQu4vr4xnSDxMaL"),
    )
