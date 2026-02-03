import logging
import math
from typing import Self

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, model_validator
from src import MCTS, GameState

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


class MCTSRequest(BaseModel):
    hand: list[int] | None = []
    dice_throw: list[int] | None = None
    num_simulations: int | None = None
    thinking_time: float | None = None

    @model_validator(mode="after")
    def check_stopping_condition(self) -> Self:
        if self.num_simulations is None and self.thinking_time is None:
            raise ValueError(
                "Either num_simulations or thinking_time must be provided."
            )
        return self


@app.post("/api/run_mcts")
def run_mcts(req: MCTSRequest):
    game_state = GameState(hand=req.hand, dice_throw=req.dice_throw)
    mcts = MCTS(game_state, c_param=200 * math.sqrt(2))  # Adjust c_param as needed

    actions = mcts.run(
        num_simulations=req.num_simulations, thinking_time=req.thinking_time
    )

    # Ensure actions are serializable
    for action in actions:
        action["action"] = str(action.get("action", ""))
    return {"actions": actions}
