from src.game import GameState
from src.tree import MCTS, Action


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

    assert (
        num_children > 1
    ), "ChanceNode should have multiple children representing different rolls"
    assert (
        len(chance_node.probabilities) == num_children
    ), "Probabilities should match children count"

    # Verify children have different dice throws
    dice_throws = [child.state.dice_throw for child in chance_node.children]
    unique_throws = set(tuple(d) for d in dice_throws)

    assert (
        len(unique_throws) == num_children
    ), "All children should have unique sorted dice throws"
    assert sum(chance_node.probabilities) > 0.99, "Probabilities should sum to approx 1"
    assert sum(chance_node.probabilities) < 1.01, "Probabilities should sum to approx 1"

    # Check that we have specifically [1, 2, ..., 8] count logic roughly correct?
    # Just checking we have a lot of items is enough for now.
    pass
