from src.game import Action, GameState
from src.tree import MCTS


def test_mcts_full_hand_no_index_error():
    """
    Regression test for the IndexError: list index out of range bug.
    When a hand is full (8 dice), get_available_actions should not return ROLL,
    which prevents MCTS from creating a ChanceNode with 0 possible rolls.
    """
    # Create a state with 8 dice in hand (full)
    full_hand = [1, 2, 3, 4, 5, 6, 1, 2]
    state = GameState(hand=full_hand, dice_throw=[], score=0.0)

    # 1. Verify GameState logic directly
    actions = state.get_available_actions()
    assert (
        Action(Action.ROLL) not in actions
    ), "ROLL should not be available when hand is full"
    assert Action(Action.STOP) in actions, "STOP should be available when hand is full"

    # 2. Verify MCTS can run without crash
    mcts = MCTS(state)
    # The crash used to happen during simulation/expansion phase
    # Running a reasonable number of simulations to ensure we touch all paths
    try:
        mcts.run(num_simulations=100)
    except IndexError as e:
        assert False, f"MCTS crashed with IndexError: {e}"
    except Exception as e:
        # We don't expect other exceptions but if they happen they should be caught or fail the test
        assert False, f"MCTS crashed with unexpected exception: {e}"
