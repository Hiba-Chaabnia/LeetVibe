"""Preview AgentSessionScreen in isolation.

Run with:
    textual run --dev dev/preview_agent_session.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.challenge_loader import Challenge
from textual.app import App
from src.textual_ui.screens.agent_session import AgentSessionScreen

FIXTURE = Challenge(
    id="1",
    title="Two Sum",
    difficulty="Easy",
    description="Given nums and target, return indices of the two numbers that add to target.",
    hints=["Use a hash map."],
    topics=["Array", "Hash Table"],
    python_snippet=(
        "class Solution:\n"
        "    def twoSum(self, nums: list[int], target: int) -> list[int]:\n"
        "        pass\n"
    ),
    test_cases=[["[2,7,11,15]", "9"]],
    expected_outputs=["[0,1]"],
    has_solutions=True,
)


class PreviewApp(App):
    CSS_PATH = Path(__file__).parent.parent / "src/textual_ui/app.tcss"

    def on_mount(self) -> None:
        self.push_screen(
            AgentSessionScreen(challenge=FIXTURE, mode="learn", user_code="")
        )


if __name__ == "__main__":
    PreviewApp().run()
