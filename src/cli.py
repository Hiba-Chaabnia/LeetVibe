"""
LeetVibe CLI - AI Pair Programming for LeetCode
Powered by Mistral AI | Built for the Mistral AI Worldwide Hackathon 2026
"""

from __future__ import annotations

import os
import sys

# Force UTF-8 output on Windows so Rich box-drawing chars render correctly.
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

import click


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("0.1.0", prog_name="leetvibe")
def cli() -> None:
    """LeetVibe — AI Pair Programming for LeetCode, powered by Mistral."""
    from .config import needs_setup

    if needs_setup():
        from .setup.onboarding import run_onboarding
        if not run_onboarding():
            click.echo("Setup cancelled. Run `leetvibe` again to get started.")
            return

    from .textual_ui.app import LeetVibeApp
    LeetVibeApp().run()


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
