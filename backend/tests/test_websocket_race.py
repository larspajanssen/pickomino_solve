import pytest
from fastapi.testclient import TestClient

from pickomino_solver.main import app


def test_websocket_simulation_race_condition():
    client = TestClient(app)
    for i in range(20):
        with client.websocket_connect("/ws/simulation") as websocket:
            # Sending simulation parameters
            payload = {"hand": [1, 2, 3], "dice_throw": [4, 5], "num_simulations": 10}
            websocket.send_json(payload)

            try:
                # Use a timeout if possible, but TestClient doesn't easily support it on receive
                # Instead we rely on it eventually finishing or the test failing if it hangs
                data = websocket.receive_json()
                assert data["type"] in ["progress", "complete"], (
                    f"Iteration {i} failed: {data}"
                )
            except Exception as e:
                pytest.fail(f"Iteration {i} failed to receive response: {e}")


def test_websocket_cancellation():
    client = TestClient(app)
    with client.websocket_connect("/ws/simulation") as websocket:
        payload = {
            "hand": [1, 2, 3],
            "num_simulations": 1000,  # Large number to ensure it doesn't finish immediately
            "thinking_time": 10.0,
        }
        websocket.send_json(payload)

        # Send cancel message immediately
        websocket.send_json({"type": "cancel"})

        # Wait for messages and eventually a "complete" or just closure
        # Note: Depending on timing, we might see progress or just the final result
        received_complete = False
        for _ in range(10):  # Receive a few messages
            try:
                data = websocket.receive_json()
                if data["type"] == "complete":
                    received_complete = True
                    break
            except Exception:
                break

        # Even if cancelled, it should eventually return a complete message or close
        # (The actual fix ensures it doesn't hang)
        assert received_complete
