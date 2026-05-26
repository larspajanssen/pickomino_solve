import logging
from typing import Any, Sequence, TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pickomino_solver import compute_state_scores

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Request(BaseModel):
    """Request payload for the solver API.

    Attributes:
        hand: Frequency vector of length 6 for saved dice in hand. Index 0 is
            face value 1, and index 5 is face value 6.
        dice_throw: Optional frequency vector of length 6 for the current throw.
            Uses the same index-to-face mapping as `hand`.
    """

    hand: list[int] = []
    tiles: list[int]
    dice_throw: list[int] | None = None


class Action(TypedDict):
    type: str  # e.g., "Roll", "SaveDice", "Stop", "Bust"
    value: int | None


@app.post("/api/run")
def run(req: Request):
    """Compute ranked action expected values for the given game state.

    Args:
        req: Solver request containing frequency-vector dice state.

    Returns:
        dict[str, list[dict[str, Any]]]: Serialized action rankings keyed by
            `"actions"`.
    """
    results = compute_state_scores(req.hand, req.dice_throw, req.tiles)
    return {"actions": serialize_results(results)}


def serialize_results(
    results: Sequence[tuple[Action, float]],
) -> list[dict[str, Any]]:
    """Convert solver actions to JSON-friendly dictionaries.

    Args:
        results: Sequence of `(action, expected_value)` tuples from the solver.

    Returns:
        list[dict[str, Any]]: Action entries with string labels and expected
            values.
    """
    serialized: list[dict[str, Any]] = []
    for action, expected_value in results:
        if isinstance(action, dict):
            action_type = action["type"]
            action_value = action.get("value", "")
        else:
            action_type = getattr(action, "action_type")
            action_value = getattr(action, "dice_value", "")

        serialized.append(
            {
                "action": f"{action_type} {action_value if action_value else ''}",
                "expected_value": expected_value,
            }
        )
    return serialized
