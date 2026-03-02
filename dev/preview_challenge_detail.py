"""Preview ChallengeDetailScreen in isolation.

Run with:
    textual run --dev dev/preview_challenge_detail.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.challenge_loader import Challenge
from textual.app import App
from src.textual_ui.screens.challenge_detail import ChallengeDetailScreen

# ── Fixture challenge ──────────────────────────────────────────────────────────
FIXTURE = Challenge(
    id="1",
    title="Two Sum",
    difficulty="Easy",
    description=(
        "Given an array of integers `nums` and an integer `target`, "
        "return indices of the two numbers such that they add up to `target`.\n\n"
        "You may assume that each input would have **exactly one solution**."
    ),
    hints=["Try using a hash map.", "One pass is enough."],
    topics=["Array", "Hash Table"],
    python_snippet=(
        "class Solution:\n"
        "    def twoSum(self, nums: list[int], target: int) -> list[int]:\n"
        "        pass\n"
    ),
    python_solution=(
        "class Solution:\n"
        "    def twoSum(self, nums: list[int], target: int) -> list[int]:\n"
        "        seen = {}\n"
        "        for i, n in enumerate(nums):\n"
        "            if target - n in seen:\n"
        "                return [seen[target - n], i]\n"
        "            seen[n] = i\n"
    ),
    test_cases=[["[2,7,11,15]", "9"], ["[3,2,4]", "6"]],
    expected_outputs=["[0,1]", "[1,2]"],
    has_solutions=True,
)

ALL_CHALLENGES = [FIXTURE]


class PreviewApp(App):
    CSS_PATH = Path(__file__).parent.parent / "src/textual_ui/app.tcss"

    def on_mount(self) -> None:
        self.push_screen(
            ChallengeDetailScreen(
                challenge=FIXTURE,
                challenges=ALL_CHALLENGES,
                index=0,
                mode="learn",
            )
        )


if __name__ == "__main__":
    PreviewApp().run()
