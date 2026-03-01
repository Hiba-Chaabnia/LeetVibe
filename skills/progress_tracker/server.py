"""MCP skill: progress_tracker — log learning sessions to Weights & Biases."""


import os
import sys
import time
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("progress_tracker")


@mcp.tool()
def log_session(
    problem_id: str,
    problem_title: str,
    difficulty: str,
    solved: bool,
    time_seconds: int,
    approaches_tried: int,
    final_complexity: str,
    hints_used: bool,
) -> str:
    """Log a completed learning session to Weights & Biases.

    Returns: "Logged to W&B run <run_id>" or an error/skip message.
    """
    api_key = os.environ.get("WANDB_API_KEY", "")
    if not api_key:
        return "skipped: WANDB_API_KEY not set"

    try:
        import wandb

        wandb.login(key=api_key, relogin=True)
        run = wandb.init(
            project=os.environ.get("WANDB_PROJECT", "leetvibe"),
            entity=os.environ.get("WANDB_ENTITY") or None,
            name=f"{problem_title}-{int(time.time())}",
            tags=[difficulty.lower(), "leetvibe", "ai-session"],
            config={
                "problem_id": problem_id,
                "problem_title": problem_title,
                "difficulty": difficulty,
                "algorithm": final_complexity,
            },
            reinit="finish_previous",
        )
        wandb.log(
            {
                "solved": int(solved),
                "time_seconds": time_seconds,
                "approaches_tried": approaches_tried,
                "hints_used": int(hints_used),
                "final_complexity": final_complexity,
            }
        )
        run_id = run.id
        wandb.finish(quiet=True)
        return f"Logged to W&B run {run_id}"
    except Exception as exc:
        return f"error logging to W&B: {exc}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
