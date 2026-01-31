from src.game import Action, GameState


def test_dice_are_sorted():
    """Test that dice throws are always sorted to handle permutations."""
    g = GameState(hand=[])
    # Roll multiple times to ensure we don't get lucky with a random sorted roll
    for _ in range(10):
        rolled_state = g.execute_action(Action(Action.ROLL))
        assert rolled_state.dice_throw == sorted(
            rolled_state.dice_throw
        ), f"Dice throw {rolled_state.dice_throw} is not sorted"
