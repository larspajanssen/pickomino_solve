from fastapi.testclient import TestClient

from pickomino_solver.main import Action, app, serialize_results


def test_run_returns_serialized_actions_with_expected_value(monkeypatch):
    def fake_compute_state_scores(hand, dice_throw, tiles):
        assert hand == [1, 2, 6]
        assert dice_throw == [3, 3, 4]
        assert tiles == [22, 23]
        return [
            ({"type": "Roll", "value": None}, 12.5),
            ({"type": "SaveDice", "value": 6}, 11.0),
        ]

    monkeypatch.setattr(
        "pickomino_solver.main.compute_state_scores",
        fake_compute_state_scores,
    )
    client = TestClient(app)

    response = client.post(
        "/api/run", json={"hand": [1, 2, 6], "dice_throw": [3, 3, 4], "tiles": [22, 23]}
    )
    assert response.status_code == 200
    assert response.json() == {
        "actions": [
            {"action": "Roll", "expected_value": 12.5},
            {"action": "SaveDice 6", "expected_value": 11.0},
        ]
    }


def test_run_accepts_null_or_omitted_dice_throw(monkeypatch):
    calls = []

    def fake_compute_state_scores(hand, dice_throw, tiles):
        calls.append((hand, dice_throw, tiles))
        return []

    monkeypatch.setattr(
        "pickomino_solver.main.compute_state_scores",
        fake_compute_state_scores,
    )
    client = TestClient(app)

    null_response = client.post(
        "/api/run", json={"hand": [6], "dice_throw": None, "tiles": [22, 23]}
    )
    assert null_response.status_code == 200

    omitted_response = client.post("/api/run", json={"hand": [6], "tiles": [22, 23]})
    assert omitted_response.status_code == 200

    assert calls == [([6], None, [22, 23]), ([6], None, [22, 23])]


def test_run_uses_request_defaults_when_body_empty(monkeypatch):
    def fake_compute_state_scores(hand, dice_throw, tiles):
        assert hand == []
        assert dice_throw is None
        assert tiles == [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        return []

    monkeypatch.setattr(
        "pickomino_solver.main.compute_state_scores",
        fake_compute_state_scores,
    )
    client = TestClient(app)

    response = client.post("/api/run", json={})
    assert response.status_code == 200
    assert response.json() == {"actions": []}


def test_serialize_results_handles_none_and_numeric_values():
    results: list[tuple[Action, float]] = [
        (Action(type="Roll", value=None), 9.75),
        (Action(type="SaveDice", value=5), 8.25),
        (Action(type="Stop", value=None), 7.0),
    ]

    assert serialize_results(results) == [
        {"action": "Roll", "expected_value": 9.75},
        {"action": "SaveDice 5", "expected_value": 8.25},
        {"action": "Stop", "expected_value": 7.0},
    ]
