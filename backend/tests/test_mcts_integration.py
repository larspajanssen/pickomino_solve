from pickomino_solver.game import GameState
from pickomino_solver.tree import MCTS, Action


def test_chance_node_implementation():
    """
    Test that the ROLL action now leads to a ChanceNode which is fully expanded
    into multiple possible outcomes.
    """
    # Start with an empty hand, so ROLL is legal
    state = GameState(hand=[])
    mcts = MCTS(state)

    # Run simulations to force expansion of ROLL
    mcts.run(num_simulations=10)

    root = mcts.root
    roll_action = Action(Action.ROLL)

    assert roll_action in root.children, "ROLL should have been expanded"
    chance_node = root.children[roll_action]

    # Verify it is a ChanceNode (duck typing or class check if importable, but we can check attributes)
    # The ChanceNode should have 'probabilities' attribute
    assert hasattr(chance_node, "probabilities"), "Child of ROLL should be a ChanceNode"
    assert hasattr(chance_node, "children"), "ChanceNode should have children"

    # With 8 dice, there are many possible sorted outcomes
    num_children = len(chance_node.children)
    print(f"Number of expanded outcomes for 8 dice: {num_children}")

    assert num_children > 1, (
        "ChanceNode should have multiple children representing different rolls"
    )
    assert len(chance_node.probabilities) == num_children, (
        "Probabilities should match children count"
    )

    # Verify children have different dice throws
    dice_throws = [child.state.dice_throw for child in chance_node.children]
    unique_throws = set(tuple(d) for d in dice_throws)

    assert len(unique_throws) == num_children, (
        "All children should have unique sorted dice throws"
    )
    assert sum(chance_node.probabilities) > 0.99, "Probabilities should sum to approx 1"
    assert sum(chance_node.probabilities) < 1.01, "Probabilities should sum to approx 1"

    # Check that we have specifically [1, 2, ..., 8] count logic roughly correct?
    # Just checking we have a lot of items is enough for now.
    pass


def test_mcts_time_limit():
    """Test that MCTS stops after approximately the specified time."""
    import time

    state = GameState(hand=[])
    mcts = MCTS(state)

    thinking_time = 0.5
    start_time = time.time()
    results = mcts.run(thinking_time=thinking_time)
    duration = time.time() - start_time

    # Check duration is roughly correct (allow some overhead)
    assert duration >= thinking_time
    # It shouldn't take TOO much longer (e.g. 0.2s overhead)
    assert duration < thinking_time + 0.2

    # Check results are returned
    assert len(results) > 0
    most_visited = max(results, key=lambda x: x["visit_count"])
    assert most_visited["visit_count"] > 0


def test_mcts_monitor_interval_simulations():
    """Test that monitoring works correctly with fixed simulations."""
    state = GameState(hand=[])
    mcts = MCTS(state)

    sims = 2000
    results = mcts.run(num_simulations=sims)

    # Check results are returned
    most_visited = max(results, key=lambda x: x["visit_count"])
    assert most_visited["visit_count"] > 0


def test_mcts_invalid_input():
    """Test that MCTS raises error if neither stop condition is provided."""
    import pytest

    state = GameState(hand=[])
    mcts = MCTS(state)

    with pytest.raises(ValueError, match="Either num_simulations or thinking_time"):
        mcts.run()


def test_mcts_callback_invocation():
    """Test that the callback is invoked during the MCTS run."""
    state = GameState(hand=[])
    mcts = MCTS(state)

    callback_calls = []

    def callback(results):
        callback_calls.append(results)

    # Using a small number of simulations but enough to trigger at least one monitor point
    mcts.run(num_simulations=100, callback=callback)

    assert len(callback_calls) > 0, "Callback should have been called at least once"
    assert "expected_score" in callback_calls[0][0]
    assert "action" in callback_calls[0][0]
    assert "visit_count" in callback_calls[0][0]
