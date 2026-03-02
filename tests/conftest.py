"""Shared fixtures for the LeetVibe test suite."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the project root importable regardless of how pytest is invoked
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ── Challenge fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def two_sum():
    """A minimal Two Sum challenge used across many tests."""
    from src.challenge_loader import Challenge

    return Challenge(
        id="1",
        title="Two Sum",
        difficulty="Easy",
        description=(
            "Given an array of integers nums and an integer target, "
            "return indices of the two numbers such that they add up to target."
        ),
        python_snippet=(
            "class Solution:\n"
            "    def twoSum(self, nums: List[int], target: int) -> List[int]: "
        ),
        python_solution=(
            "class Solution:\n"
            "    def twoSum(self, nums, target):\n"
            "        seen = {}\n"
            "        for i, n in enumerate(nums):\n"
            "            if target - n in seen:\n"
            "                return [seen[target - n], i]\n"
            "            seen[n] = i\n"
        ),
        test_cases=[["[2,7,11,15]", "9"]],
        expected_outputs=["[0,1]"],
        topics=["Array", "Hash Table"],
        hints=["Try using a hash map."],
        has_solutions=True,
        solution_explanation="Use a hash map for O(n) time complexity.",
    )


@pytest.fixture
def climbing_stairs():
    """Climbing Stairs — useful for DP / recursion tests."""
    from src.challenge_loader import Challenge

    return Challenge(
        id="70",
        title="Climbing Stairs",
        difficulty="Easy",
        description="You are climbing a staircase. Each time you can climb 1 or 2 steps.",
        python_snippet="class Solution:\n    def climbStairs(self, n: int) -> int: ",
        test_cases=[["2"], ["3"]],
        expected_outputs=["2", "3"],
        topics=["Dynamic Programming"],
        has_solutions=False,
    )


# ── Config fixture ────────────────────────────────────────────────────────────


@pytest.fixture
def dummy_config():
    """A Config object with fake API keys — safe for unit tests."""
    from src.config import Config

    return Config(
        mistral_api_key="test-mistral-key-abc123",
        mistral_model="mistral-large-latest",
        elevenlabs_api_key="test-elevenlabs-key",
        elevenlabs_voice_id="EXAVITQu4vr4xnSDxMaL",
    )
