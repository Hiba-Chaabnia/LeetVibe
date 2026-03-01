"""LeetVibe config — parse config.yaml + .env once at startup."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import yaml

_ROOT = Path(__file__).parent.parent
_CONFIG_PATH = _ROOT / "config.yaml"
_LEETVIBE_HOME = Path.home() / ".leetvibe"
_USER_ENV_PATH = _LEETVIBE_HOME / ".env"   # persistent, user-level
_LOCAL_ENV_PATH = _ROOT / ".env"            # project-level dev fallback


def needs_setup() -> bool:
    """Return True if MISTRAL_API_KEY is not yet available."""
    load_dotenv(_USER_ENV_PATH, override=False)
    load_dotenv(_LOCAL_ENV_PATH, override=False)
    return not os.environ.get("MISTRAL_API_KEY", "").strip()


def _expand(value: str) -> str:
    """Expand ${VAR} placeholders via os.environ."""
    return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), ""), value)


@dataclass
class Config:
    mistral_api_key: str
    mistral_model: str
    elevenlabs_api_key: str
    elevenlabs_voice_id: str
    wandb_api_key: str
    wandb_project: str
    wandb_entity: str


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
        elevenlabs_api_key=_get("elevenlabs", "api_key") or os.environ.get("ELEVENLABS_API_KEY", ""),
        elevenlabs_voice_id=_get("elevenlabs", "voice_id", "EXAVITQu4vr4xnSDxMaL"),
        wandb_api_key=_get("wandb", "api_key") or os.environ.get("WANDB_API_KEY", ""),
        wandb_project=_get("wandb", "project", "leetvibe"),
        wandb_entity=_get("wandb", "entity") or os.environ.get("WANDB_ENTITY", ""),
    )
