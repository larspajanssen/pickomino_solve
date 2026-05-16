from pickomino_solver.main import Action, serialize_results


def test_serialize_results_handles_none_and_numeric_values():
    results: list[tuple[Action, float]] = [
        (Action(type="Roll", value=None), 9.75),
        (Action(type="SaveDice", value=5), 8.25),
        (Action(type="Stop", value=None), 7.0),
    ]

    assert serialize_results(results) == [
        {"action": "Roll None", "expected_value": 9.75},
        {"action": "SaveDice 5", "expected_value": 8.25},
        {"action": "Stop None", "expected_value": 7.0},
    ]
