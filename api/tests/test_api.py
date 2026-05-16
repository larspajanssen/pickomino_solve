from fastapi.testclient import TestClient

from pickomino_solver.main import app


def test_run_returns_serialized_actions_with_expected_value(monkeypatch):
    def fake_compute_state_scores(hand, dice_throw):
        assert hand == [1, 2, 6]
        assert dice_throw == [3, 3, 4]
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
        "/api/run", json={"hand": [1, 2, 6], "dice_throw": [3, 3, 4]}
    )
    assert response.status_code == 200
    assert response.json() == {
        "actions": [
            {"action": "Roll None", "expected_value": 12.5},
            {"action": "SaveDice 6", "expected_value": 11.0},
        ]
    }


def test_run_accepts_null_or_omitted_dice_throw(monkeypatch):
    calls = []

    def fake_compute_state_scores(hand, dice_throw):
        calls.append((hand, dice_throw))
        return []

    monkeypatch.setattr(
        "pickomino_solver.main.compute_state_scores",
        fake_compute_state_scores,
    )
    client = TestClient(app)

    null_response = client.post("/api/run", json={"hand": [6], "dice_throw": None})
    assert null_response.status_code == 200

    omitted_response = client.post("/api/run", json={"hand": [6]})
    assert omitted_response.status_code == 200

    assert calls == [([6], None), ([6], None)]


def test_run_uses_request_defaults_when_body_empty(monkeypatch):
    def fake_compute_state_scores(hand, dice_throw):
        assert hand == []
        assert dice_throw is None
        return []

    monkeypatch.setattr(
        "pickomino_solver.main.compute_state_scores",
        fake_compute_state_scores,
    )
    client = TestClient(app)

    response = client.post("/api/run", json={})
    assert response.status_code == 200
    assert response.json() == {"actions": []}
