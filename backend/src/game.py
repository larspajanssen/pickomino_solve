import math
import random
from collections import Counter
from functools import lru_cache
from itertools import combinations_with_replacement
from typing import List, Optional


class Action:
    ROLL = "Roll dice"
    STOP = "Stop round"
    SAVE_DICE = "Save dice"
    BUST = "Bust"

    def __init__(self, name, optional_args: Optional[int] = None):
        self.name = name
        self.optional_args = optional_args

    def __str__(self):
        return f"({self.name}, {str(self.optional_args)})"

    def __eq__(self, other):
        return self.name == other.name and self.optional_args == other.optional_args

    def __hash__(self) -> int:
        return hash((self.name, self.optional_args))


class GameState:
    def __init__(
        self,
        hand: List[int],
        dice_throw: Optional[List[int]] = None,
        score: Optional[float] = 0.0,
    ):
        self.DIE = [1, 2, 3, 4, 5, 6]
        self.N_DICE = 8
        self.score = score

        self.hand = hand
        self.dice_throw = dice_throw if dice_throw is not None else []
        self.stopped_round = False

    def get_available_actions(self) -> List[Action]:
        if self.stopped_round:
            # Return no available actions when the round had been stopped
            return []

        if not self.dice_throw:
            actions = [Action(Action.ROLL), Action(Action.STOP)]
            return actions

        if len(self.hand) >= self.N_DICE:
            return [Action(Action.STOP)]

        if self.dice_throw:
            die_options = []
            for d in self.dice_throw:
                if not self._die_in_hand(d):
                    die_options.append(d)

            if not die_options:
                return [Action(Action.BUST)]

            return [Action(Action.SAVE_DICE, d) for d in set(die_options)]

    def execute_action(self, action: Action) -> "GameState":
        # Make game state immutable manually instead of deepcopy for performance
        new_hand = list(self.hand)
        new_dice_throw = list(self.dice_throw) if self.dice_throw else []
        new_score = self.score
        new_stopped_round = self.stopped_round

        if action.name == Action.ROLL:
            if new_dice_throw:
                raise Exception("dice_throw should be empty")

            # Generate random roll
            dice_count = self.N_DICE - len(new_hand)
            # Use self.DIE to determine range, effectively random.choice(self.DIE)
            roll = [random.choice(self.DIE) for _ in range(dice_count)]
            roll.sort()

            # Optimization: directly return the new state
            return GameState(
                hand=new_hand,
                dice_throw=roll,  # Sorted random roll
                score=new_score,
            )

        if action.name == Action.SAVE_DICE:
            for d in new_dice_throw:
                if action.optional_args == d:
                    new_hand.append(d)

            # Empty dice throw
            new_dice_throw = []

        if action.name == Action.BUST:
            new_score = 0
            new_stopped_round = True

        if action.name == Action.STOP:
            for dh in new_hand:
                if dh == 6:
                    # Transform worm to value of 5
                    dh = 5
                new_score += dh
            new_stopped_round = True

        new_state = GameState(hand=new_hand, dice_throw=new_dice_throw, score=new_score)
        new_state.stopped_round = new_stopped_round
        return new_state

    def apply_roll_outcome(self, roll: List[int]) -> "GameState":
        """
        Applies a specific dice roll outcome to the current state.
        This allows for deterministic transitions from a Chance Node.
        """
        if self.dice_throw:
            raise Exception("dice_throw should be empty before applying new roll")

        # Optimization: Manual copy
        new_hand = list(self.hand)
        # dice_throw is None or empty in self, so we just set the new one
        new_dice_throw = sorted(roll)

        new_state = GameState(
            hand=new_hand, dice_throw=new_dice_throw, score=self.score
        )
        new_state.stopped_round = self.stopped_round
        return new_state

    @lru_cache(maxsize=16)
    def get_possible_rolls(self) -> List[tuple[List[int], float]]:
        """
        Returns a list of all possible sorted dice rolls and their probabilities.
        Returns: List of (sorted_roll, respective probability)
        """
        num_dice = self.N_DICE - len(self.hand)
        return self._get_possible_rolls_cached(num_dice)

    @staticmethod
    @lru_cache(maxsize=16)
    def _get_possible_rolls_cached(num_dice: int) -> List[tuple[List[int], float]]:
        if num_dice <= 0:
            return []

        # Hardcoded for now as per original class
        DIE = [1, 2, 3, 4, 5, 6]
        num_faces = len(DIE)

        # All possible sorted combinations
        combs = list(combinations_with_replacement(DIE, num_dice))

        results = []
        total_outcomes = num_faces**num_dice

        for roll in combs:
            # Calculate weight using multinomial coefficient: n! / (n1! * n2! * ... * nk!)
            # where n is total dice, and ni is count of each face
            counts = Counter(roll)
            denominator = 1
            for count in counts.values():
                denominator *= math.factorial(count)

            weight = math.factorial(num_dice) // denominator
            probability = weight / total_outcomes

            results.append((list(roll), probability))

        return results

    def _die_in_hand(self, die: int) -> bool:
        if die in set(self.hand):
            return True
        else:
            return False
