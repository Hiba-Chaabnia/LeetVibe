"""Tests for src/config.py — load_config() and _expand()."""

from __future__ import annotations

import sys


# ── _expand() ────────────────────────────────────────────────────────────────


def test_expand_single_var(monkeypatch):
    monkeypatch.setenv("TEST_CONFIG_KEY", "secret123")
    from src.config import _expand
    assert _expand("${TEST_CONFIG_KEY}") == "secret123"


def test_expand_multiple_vars(monkeypatch):
    monkeypatch.setenv("PROJ", "leetvibe")
    monkeypatch.setenv("ENV", "test")
    from src.config import _expand
    assert _expand("${PROJ}-${ENV}") == "leetvibe-test"


def test_expand_missing_var_returns_empty(monkeypatch):
    monkeypatch.delenv("TOTALLY_MISSING_VAR_XYZ", raising=False)
    from src.config import _expand
    assert _expand("${TOTALLY_MISSING_VAR_XYZ}") == ""


def test_expand_no_placeholder_unchanged():
    from src.config import _expand
    assert _expand("plain-string-no-dollars") == "plain-string-no-dollars"


def test_expand_partial_braces_unchanged():
    from src.config import _expand
    # $VAR without braces should not be touched
    assert _expand("$VAR") == "$VAR"


# ── load_config() ─────────────────────────────────────────────────────────────


def test_load_config_returns_config_instance():
    from src.config import load_config, Config
    cfg = load_config()
    assert isinstance(cfg, Config)


def test_load_config_model_is_mistral_large():
    from src.config import load_config
    cfg = load_config()
    assert cfg.mistral_model == "mistral-large-latest"


def test_load_config_all_fields_are_strings():
    from src.config import load_config
    cfg = load_config()
    for field_name, value in cfg.__dict__.items():
        assert isinstance(value, str), f"Field '{field_name}' should be str, got {type(value)}"


def test_load_config_respects_env_override(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "override-key-for-test")
    from src.config import load_config
    cfg = load_config()
    assert cfg.mistral_api_key == "override-key-for-test"


def test_load_config_elevenlabs_voice_id_default():
    from src.config import load_config
    cfg = load_config()
    # The voice ID set in config.yaml should survive
    assert cfg.elevenlabs_voice_id == "EXAVITQu4vr4xnSDxMaL"


def test_load_config_wandb_project():
    from src.config import load_config
    cfg = load_config()
    assert cfg.wandb_project == "leetvibe"


# ── Config dataclass ──────────────────────────────────────────────────────────


def test_config_equality(dummy_config):
    from src.config import Config
    cfg2 = Config(
        mistral_api_key="test-mistral-key-abc123",
        mistral_model="mistral-large-latest",
        elevenlabs_api_key="test-elevenlabs-key",
        elevenlabs_voice_id="EXAVITQu4vr4xnSDxMaL",
        wandb_api_key="test-wandb-key",
        wandb_project="leetvibe-test",
        wandb_entity="test-entity",
    )
    assert dummy_config == cfg2


def test_config_fields(dummy_config):
    assert dummy_config.mistral_api_key == "test-mistral-key-abc123"
    assert dummy_config.mistral_model == "mistral-large-latest"
    assert dummy_config.elevenlabs_voice_id == "EXAVITQu4vr4xnSDxMaL"
    assert dummy_config.wandb_project == "leetvibe-test"
    assert dummy_config.wandb_entity == "test-entity"
