from typing import List, Optional, Tuple, TypedDict

class ActionDict(TypedDict):
    type: str  # e.g., "Roll", "SaveDice", "Stop", "Bust"
    value: Optional[int]  # e.g., 5 for SaveDice, or None for others

def compute_state_scores(
    hand: List[int], throw: Optional[List[int]]
) -> List[Tuple[ActionDict, float]]:
    """
    Computes the expected maximum scores for all available actions
    given the current hand and the optional current dice throw.
    """
    ...
