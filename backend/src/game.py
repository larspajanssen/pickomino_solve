import copy
import math
import random
from collections import Counter
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
        dice_throw: Optional[List[int]] = [],
        score: Optional[float] = 0.0,
    ):
        self.DIE = [1, 2, 3, 4, 5, 6]
        self.N_DICE = 8
        self.score = score

        self.hand = hand
        self.dice_throw = dice_throw
        self.stopped_round = False

    def get_available_actions(self) -> List[Action]:
        if self.stopped_round:
            # Return no available actions when the round had been stopped
            return []

        if len(self.hand) >= self.N_DICE:
            return [Action(Action.STOP)]

        if not self.dice_throw:
            actions = [Action(Action.ROLL), Action(Action.STOP)]
            return actions

        if self.dice_throw:
            die_options = []
            for d in self.dice_throw:
                if not self._die_in_hand(d):
                    die_options.append(d)

            if not die_options:
                return [Action(Action.BUST)]

            return [Action(Action.SAVE_DICE, d) for d in set(die_options)]

    def execute_action(self, action: Action) -> "GameState":
        # Make game state immutable
        new_state = copy.deepcopy(self)

        if action.name == Action.ROLL:
            if new_state.dice_throw:
                raise Exception("dice_throw should be empty")

            # Generate random roll
            dice_count = new_state.N_DICE - len(new_state.hand)
            # Use self.DIE to determine range, effectively random.choice(self.DIE)
            roll = [random.choice(new_state.DIE) for _ in range(dice_count)]
            roll.sort()

            # Apply the roll using the new deterministic method
            new_state = new_state.apply_roll_outcome(roll)

        if action.name == Action.SAVE_DICE:
            for d in new_state.dice_throw:
                if action.optional_args == d:
                    new_state.hand.append(d)

            # Empty dice throw
            new_state.dice_throw = []

        if action.name == Action.BUST:
            new_state.score = 0
            new_state.stopped_round = True

        if action.name == Action.STOP:
            for dh in new_state.hand:
                if dh == 6:
                    # Transform worm to value of 5
                    dh = 5
                new_state.score += dh
            new_state.stopped_round = True

        return new_state

    def apply_roll_outcome(self, roll: List[int]) -> "GameState":
        """
        Applies a specific dice roll outcome to the current state.
        This allows for deterministic transitions from a Chance Node.
        """
        new_state = copy.deepcopy(self)
        if new_state.dice_throw:
            raise Exception("dice_throw should be empty before applying new roll")

        new_state.dice_throw = sorted(roll)
        return new_state

    def get_possible_rolls(self) -> List[tuple[List[int], float]]:
        """
        Returns a list of all possible sorted dice rolls and their probabilities.
        Returns: List of (sorted_roll, respective probability)
        """
        num_dice = self.N_DICE - len(self.hand)
        if num_dice <= 0:
            return []

        num_faces = len(self.DIE)

        # All possible sorted combinations
        combs = list(combinations_with_replacement(self.DIE, num_dice))

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
