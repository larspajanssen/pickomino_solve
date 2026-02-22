from fastapi.testclient import TestClient

from pickomino_solver.main import app

client = TestClient(app)


def test_run_mcts_post_simulations():
    """Test the POST /api/run_mcts endpoint with num_simulations."""
    response = client.post(
        "/api/run_mcts", json={"hand": [1, 2, 3], "num_simulations": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert "actions" in data
    assert len(data["actions"]) > 0
    # Check that actions were stringified
    assert isinstance(data["actions"][0]["action"], str)


def test_run_mcts_post_time():
    """Test the POST /api/run_mcts endpoint with thinking_time."""
    response = client.post(
        "/api/run_mcts", json={"hand": [1, 1, 2], "thinking_time": 0.1}
    )
    assert response.status_code == 200
    data = response.json()
    assert "actions" in data
    assert len(data["actions"]) > 0


def test_run_mcts_post_invalid():
    """Test the POST /api/run_mcts endpoint with invalid input (no stopping condition)."""
    response = client.post("/api/run_mcts", json={"hand": [1, 2, 3]})
    # Pydantic validation error should happen
    assert response.status_code == 422


def test_websocket_simulation_flow():
    """Test the full WebSocket simulation flow."""
    with client.websocket_connect("/ws/simulation") as websocket:
        websocket.send_json(
            {
                "hand": [1, 2, 3, 4, 5, 6],
                "num_simulations": 10000,  # Large enough to ensure progress is sent
            }
        )

        messages = []
        # Receive messages until we get 'complete'
        while True:
            data = websocket.receive_json()
            messages.append(data)
            if data["type"] == "complete":
                break

        # Check that we have at least one progress message
        progress_msgs = [m for m in messages if m["type"] == "progress"]
        assert len(progress_msgs) > 0, (
            f"No progress messages. Received: {[m['type'] for m in messages]}"
        )
        assert messages[-1]["type"] == "complete"


def test_websocket_invalid_initial_message():
    """Test WebSocket error handling for invalid initial configuration."""
    with client.websocket_connect("/ws/simulation") as websocket:
        # Missing stopping condition
        websocket.send_json({"hand": [1, 2, 3]})

        data = websocket.receive_json()
        assert data["type"] == "error"
        assert "Either num_simulations or thinking_time" in data["message"]


def test_websocket_cancellation():
    """Test WebSocket cancellation mid-simulation."""
    with client.websocket_connect("/ws/simulation") as websocket:
        websocket.send_json({"hand": [1], "thinking_time": 1.0})

        # Wait for first progress
        data = websocket.receive_json()
        assert data["type"] == "progress"

        # Cancel
        websocket.send_json({"type": "cancel"})

        # Drain until stop
        final_msg = None
        for _ in range(50):  # Limit to avoid infinite loop if bug
            data = websocket.receive_json()
            if data["type"] in ["complete", "error"]:
                final_msg = data
                break

        assert final_msg is not None
        assert final_msg["type"] == "complete"
