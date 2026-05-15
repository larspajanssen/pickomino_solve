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
    hand: list[int] = []
    dice_throw: list[int] | None = None


class Action(TypedDict):
    type: str  # e.g., "Roll", "SaveDice", "Stop", "Bust"
    value: int | None


@app.post("/api/run")
def run_mcts(req: Request):
    results = compute_state_scores(req.hand, req.dice_throw)
    return {"actions": serialize_mcts_results(results)}


def serialize_mcts_results(
    results: Sequence[tuple[Action, float]],
) -> list[dict[str, Any]]:
    """
    Converts MCTS result actions to strings for JSON serialization.

    Args:
        results: Sequence of result dictionaries from MCTS.

    Returns:
        List of dictionaries with stringified actions.
    """
    return [
        {
            "action": f"{action['type']} {action.get('value', '')}",
            "expected_value": expected_value,
        }
        for (action, expected_value) in results
    ]
