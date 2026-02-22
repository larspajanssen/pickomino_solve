import asyncio
import logging
import math
import threading
from typing import Any, Self, Sequence

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, model_validator

from . import MCTS, GameState, ResultAction

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
    hand: list[int] = []
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
    mcts = MCTS(game_state, c_param=200 * math.sqrt(2))

    actions = mcts.run(
        num_simulations=req.num_simulations, thinking_time=req.thinking_time
    )

    return {"actions": serialize_mcts_results(actions)}


def serialize_mcts_results(results: Sequence[ResultAction]) -> list[dict[str, Any]]:
    """
    Converts MCTS result actions to strings for JSON serialization.

    Args:
        results: Sequence of result dictionaries from MCTS.

    Returns:
        List of dictionaries with stringified actions.
    """
    serializable_results = []
    for r in results:
        res_copy = dict(r)
        res_copy["action"] = str(res_copy["action"])
        serializable_results.append(res_copy)
    return serializable_results


async def handle_websocket_cancellation(
    websocket: WebSocket, cancellation_token: threading.Event
) -> None:
    """
    Listens for cancellation messages on a WebSocket.

    Args:
        websocket: The active WebSocket connection.
        cancellation_token: Event to signal cancellation.
    """
    try:
        while True:
            msg = await websocket.receive_json()
            if msg.get("type") == "cancel":
                logging.info("Cancellation requested via WebSocket")
                cancellation_token.set()
                break
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected while listening for cancel")
        cancellation_token.set()
    except Exception as e:
        logging.error(f"Error in cancel listener: {e}")
        cancellation_token.set()


@app.websocket("/ws/simulation")
async def websocket_simulation(websocket: WebSocket) -> None:
    """
    Handles interactive MCTS simulations over WebSocket.

    Args:
        websocket: The active WebSocket connection.
    """
    await websocket.accept()
    logging.info("WebSocket connection accepted")
    cancellation_token = threading.Event()
    loop = asyncio.get_event_loop()

    cancel_listener = asyncio.create_task(
        handle_websocket_cancellation(websocket, cancellation_token)
    )

    try:
        data = await websocket.receive_json()
        req = MCTSRequest(**data)
        game_state = GameState(hand=req.hand, dice_throw=req.dice_throw)
        mcts = MCTS(game_state, c_param=200 * math.sqrt(2))

        def progress_callback(results: Sequence[ResultAction]) -> None:
            serializable = serialize_mcts_results(results)
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({"type": "progress", "actions": serializable}),
                loop,
            )

        def run_sync() -> list[ResultAction]:
            return mcts.run(
                num_simulations=req.num_simulations,
                thinking_time=req.thinking_time,
                callback=progress_callback,
                cancellation_token=cancellation_token,
            )

        final_results = await loop.run_in_executor(None, run_sync)
        serializable_final = serialize_mcts_results(final_results)
        await websocket.send_json({"type": "complete", "actions": serializable_final})
        logging.info("Simulation complete, sent results")

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
    except Exception as e:
        logging.error(f"Error in WebSocket simulation: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        cancellation_token.set()
        cancel_listener.cancel()
        try:
            await cancel_listener
        except asyncio.CancelledError:
            pass
        logging.info("WebSocket simulation resources cleaned up")
