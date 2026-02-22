import math

from pickomino_solver.game import Action, GameState


class TestGameStateLogic:
    def test_initial_state_actions(self):
        """Test actions available at the start of a turn."""
        game = GameState(hand=[], dice_throw=None)
        actions = game.get_available_actions()

        assert len(actions) == 2
        assert Action(Action.ROLL) in actions
        assert Action(Action.STOP) in actions

    def test_roll_action_execution(self):
        """Test that executing a ROLL action produces a valid state."""
        game = GameState(hand=[])
        new_state = game.execute_action(Action(Action.ROLL))

        assert new_state is not game
        assert len(new_state.dice_throw) == 8
        assert new_state.hand == []
        # Dice should be sorted
        assert new_state.dice_throw == sorted(new_state.dice_throw)

    def test_execute_action_immutability(self):
        """
        CRITICAL: Test that execute_action does not modify the original state.
        This is the main thing we are optimizing, so valid regression test is key.
        """
        original_hand = [5]
        original_throw = [1, 2, 3]
        game = GameState(hand=list(original_hand), dice_throw=list(original_throw))

        # Save a die
        action = Action(Action.SAVE_DICE, 1)
        new_state = game.execute_action(action)

        # Check new state
        assert 1 in new_state.hand
        assert new_state.dice_throw == []

        # Check original state is UNTOUCHED
        assert game.hand == original_hand
        assert game.dice_throw == original_throw
        assert game.hand is not new_state.hand  # Must be different objects

    def test_save_dice_logic(self):
        """Test valid dice saving."""
        # Rolling [1, 1, 2, 3] with hand []
        game = GameState(hand=[], dice_throw=[1, 1, 2, 3])
        actions = game.get_available_actions()

        # Should be able to save 1, 2, or 3
        expected_actions = {
            Action(Action.SAVE_DICE, 1),
            Action(Action.SAVE_DICE, 2),
            Action(Action.SAVE_DICE, 3),
        }
        assert set(actions) == expected_actions

    def test_cannot_save_existing_die(self):
        """Test that you cannot save a die value you already have in hand."""
        # Hand has a 5. Threw [5, 5, 2]. Can only save 2.
        game = GameState(hand=[5], dice_throw=[2, 5, 5])
        actions = game.get_available_actions()

        assert len(actions) == 1
        assert actions[0] == Action(Action.SAVE_DICE, 2)

    def test_bust_condition(self):
        """Test that BUST action is the only option when no valid moves exist."""
        # Hand has 5. Threw only 5s.
        game = GameState(hand=[5], dice_throw=[5, 5, 5])
        actions = game.get_available_actions()

        assert len(actions) == 1
        assert actions[0] == Action(Action.BUST)

        # Executing bust should zero score and stop round
        new_state = game.execute_action(Action(Action.BUST))
        assert new_state.score == 0
        assert new_state.stopped_round is True

    def test_stop_round_scoring(self):
        """Test scoring validation when stopping."""
        # Hand: 5 (worm), 5, 4. Total = 5+5+4 = 14
        game = GameState(hand=[6, 6, 4], dice_throw=[])

        new_state = game.execute_action(Action(Action.STOP))

        assert new_state.stopped_round is True
        # 6 (worm) counts as 5 points
        assert new_state.score == 5 + 5 + 4

    def test_get_possible_rolls_probabilities(self):
        """
        Test that probability calculations sum to 1 and are correct for simple cases.
        """
        game = GameState(hand=[])  # 8 dice
        # This might be slow if we check all, calling it implies it works
        # Let's check a smaller case for exact math

        # Case: 1 die left
        game.hand = [1, 2, 3, 4, 5, 6, 6]  # 7 dice in hand, 1 left
        # execute_action w/ ROLL updates state based on hand size

        outcomes = game.get_possible_rolls()
        # 1 die: 6 outcomes (1,2,3,4,5,6), each prob 1/6
        assert len(outcomes) == 6

        total_prob = sum(prob for _, prob in outcomes)
        assert math.isclose(total_prob, 1.0)

        for roll, prob in outcomes:
            assert math.isclose(prob, 1 / 6)
            assert len(roll) == 1

    def test_apply_roll_outcome(self):
        """Test deterministic application of roll outcome."""
        game = GameState(hand=[])
        roll = [1, 3, 2]
        new_state = game.apply_roll_outcome(roll)

        assert new_state.dice_throw == [1, 2, 3]  # Should be sorted
        assert new_state.dice_throw is not roll  # Should be copy/new list
        assert game.dice_throw == []  # Original untouched (default is empty list)

    def test_stop_round_without_worm_is_zero(self):
        """Test that stopping without a worm (6) results in a score of 0."""
        # Hand: 5, 5. sum would be 10, but no worm.
        game = GameState(hand=[5, 5], dice_throw=[])

        new_state = game.execute_action(Action(Action.STOP))

        assert new_state.stopped_round is True
        assert new_state.score == 0

    def test_dice_are_sorted(self):
        """Test that dice throws are always sorted to handle permutations."""
        g = GameState(hand=[])
        # Roll multiple times to ensure we don't get lucky with a random sorted roll
        for _ in range(10):
            rolled_state = g.execute_action(Action(Action.ROLL))
            assert rolled_state.dice_throw == sorted(rolled_state.dice_throw), (
                f"Dice throw {rolled_state.dice_throw} is not sorted"
            )
