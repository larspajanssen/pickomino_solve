import math
import random
import time
from typing import Callable, TypedDict

from .game import Action, GameState

# HistoryPoint removed for memory optimization.


class ResultAction(TypedDict):
    expected_score: float
    action: Action
    visit_count: int


class Node:
    def __init__(
        self, state: GameState, parent: "Node" = None, action_taken: Action = None
    ):
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        self.children = {}  # type: dict[Action, Node]
        self.N = 0  # Visit count
        self.Q = 0.0  # Total score

        # A copy of available actions to track which ones have been expanded
        self.unvisited_actions = list(state.get_available_actions())

    def is_fully_expanded(self) -> bool:
        """Checks if all available actions from this node have been expanded."""
        return len(self.unvisited_actions) == 0

    def is_terminal_node(self) -> bool:
        """Checks if the game state at this node is a terminal state."""
        return self.state.stopped_round

    def __repr__(self):
        return f"Node(Q={self.Q:.2f}, N={self.N}, Actions Left={len(self.unvisited_actions)})"


class ChanceNode:
    def __init__(self, state: GameState, parent: Node, action_taken: Action):
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        self.children = []  # List of child Nodes (outcomes)
        self.probabilities = []  # Corresponding probabilities
        self.N = 0
        self.Q = 0.0

    def is_terminal_node(self) -> bool:
        return False

    def is_fully_expanded(self) -> bool:
        return True


class MCTS:
    def __init__(self, initial_game_state: GameState, c_param: float = math.sqrt(2)):
        self.root = Node(initial_game_state)
        self.c_param = c_param

    def _select(self) -> Node:
        """
        Selection phase: Traverse the tree to find a node to expand or simulate from.
        Uses UCB1 formula to balance exploration and exploitation.
        """
        current_node = self.root

        # If the current node is not fully expanded, return it for expansion
        while current_node.is_fully_expanded() and not current_node.is_terminal_node():
            # If we hit a ChanceNode (which should be fully expanded immediately upon creation),
            # we must sample a child to continue the traversal (simulation of the roll).
            if isinstance(current_node, ChanceNode):
                # Sample a child based on probabilities
                current_node = random.choices(
                    current_node.children, weights=current_node.probabilities, k=1
                )[0]
                continue

            best_ucb = -float("inf")
            best_child = None

            for action, child in current_node.children.items():
                # UCB1 formula: Q/N + c * sqrt(ln(Parent_N) / N)
                if child.N == 0:
                    ucb = float(
                        "inf"
                    )  # Prioritize unvisited children for immediate exploration
                else:
                    ucb = (child.Q / child.N) + self.c_param * math.sqrt(
                        math.log(current_node.N) / child.N
                    )

                if ucb > best_ucb:
                    best_ucb = ucb
                    best_child = child
            if best_child is None:
                return current_node  # No valid child found, return current node
            current_node = best_child
        # If the root is not fully expanded, always return it for expansion
        return current_node

    def _expand(self, node: Node) -> Node:
        """
        Expansion phase: Create a new child node for an unvisited action.
        """
        if node.is_terminal_node() or node.is_fully_expanded():
            # If the node is terminal or fully expanded, expansion is not possible/needed.
            return node

        # Choose a random unvisited action to expand
        action = random.choice(node.unvisited_actions)
        node.unvisited_actions.remove(action)

        if action.name == Action.ROLL:
            # Create a ChanceNode
            chance_node = ChanceNode(node.state, parent=node, action_taken=action)
            node.children[action] = chance_node

            # Immediately fully expand the ChanceNode
            possible_outcomes = node.state.get_possible_rolls()

            for roll, prob in possible_outcomes:
                # Create the specific outcome state
                child_state = node.state.apply_roll_outcome(roll)
                child_node = Node(
                    child_state, parent=chance_node, action_taken=None
                )  # action_taken is implicitly the roll outcome

                chance_node.children.append(child_node)
                chance_node.probabilities.append(prob)

            return chance_node
        else:
            new_state = node.state.execute_action(action)
            new_child = Node(new_state, parent=node, action_taken=action)
            node.children[action] = new_child
            return new_child

    def _simulate(self, node: Node) -> float:
        """
        Simulation (Rollout) phase: Play out a random game from the given node's state
        until a terminal state is reached, and return the final score.
        """
        current_rollout_state = node.state
        while not current_rollout_state.stopped_round:
            available_actions = current_rollout_state.get_available_actions()
            if (
                not available_actions
            ):  # No more actions, game might be implicitly stopped
                break
            random_action = random.choice(available_actions)
            current_rollout_state = current_rollout_state.execute_action(random_action)

        return current_rollout_state.score

    def _backpropagate(self, node: Node, score: float):
        """
        Backpropagation phase: Update visit counts and total scores for all nodes
        on the path from the simulated node up to the root.
        """
        current_node = node
        while current_node is not None:
            current_node.N += 1
            current_node.Q += score
            current_node = current_node.parent

    TIME_CHECK_INTERVAL = 25
    MONITOR_POINTS_TARGET = 20

    def run(
        self,
        num_simulations: int | None = None,
        thinking_time: float | None = None,
        callback: Callable | None = None,
        cancellation_token: any = None,
    ) -> list[ResultAction]:
        """
        Runs the MCTS algorithm. Can be stopped by a fixed number of simulations
        OR by a time limit (thinking_time in seconds).
        """
        if num_simulations is None and thinking_time is None:
            raise ValueError(
                "Either num_simulations or thinking_time must be provided."
            )

        # Setup monitoring intervals
        monitor_interval_sims = None
        monitor_interval_time = None

        if num_simulations is not None:
            monitor_interval_sims = max(
                1, num_simulations // self.MONITOR_POINTS_TARGET
            )

        if thinking_time is not None:
            monitor_interval_time = thinking_time / self.MONITOR_POINTS_TARGET

        start_time = time.time()
        next_monitor_time = (
            start_time + monitor_interval_time if monitor_interval_time else None
        )

        i = 0
        while True:
            # --- Stopping Conditions ---
            # 1. Simulation count limit
            if num_simulations is not None and i >= num_simulations:
                break

            # 2. Time limit and Cancellation (batched check for performance)
            if i % self.TIME_CHECK_INTERVAL == 0:
                if cancellation_token and cancellation_token.is_set():
                    break

                if thinking_time is not None:
                    current_time = time.time()
                    if current_time - start_time >= thinking_time:
                        break

                    # Check monitor time (batched)
                    if (
                        next_monitor_time is not None
                        and current_time >= next_monitor_time
                    ):
                        if callback:
                            callback(self._get_results())
                        next_monitor_time += monitor_interval_time

            i += 1

            # --- MCTS Step ---
            self._step()

            # --- Monitoring (Simulations) ---
            if monitor_interval_sims is not None and i % monitor_interval_sims == 0:
                if callback:
                    callback(self._get_results())

        # Return final results
        return self._get_results()

    def _step(self):
        """Performs one iteration of MCTS: Select, Expand, Simulate, Backpropagate."""
        # 1. Selection
        leaf_node = self._select()

        # 2. Expansion
        if not leaf_node.is_terminal_node():
            node_to_simulate_from = self._expand(leaf_node)
            if isinstance(node_to_simulate_from, ChanceNode):
                node_to_simulate_from = random.choices(
                    node_to_simulate_from.children,
                    weights=node_to_simulate_from.probabilities,
                    k=1,
                )[0]
        else:
            node_to_simulate_from = leaf_node

        # 3. Simulation
        score = self._simulate(node_to_simulate_from)

        # 4. Backpropagation
        self._backpropagate(node_to_simulate_from, score)

    def _get_results(self) -> list[ResultAction]:
        """Compiles the final results from the root node."""
        if not self.root.children:
            raise Exception("root does not have children")

        results = []
        for action, child in self.root.children.items():
            avg_score = child.Q / child.N if child.N > 0 else 0
            results.append(
                {
                    "expected_score": avg_score,
                    "action": action,
                    "visit_count": child.N,
                }
            )
        return results
