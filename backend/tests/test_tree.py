from pickomino_solver import MCTS, Action, GameState, Node


class DummyAction(Action):
    def __init__(self, optional_args=None):
        super().__init__("Save dice", optional_args)


class DummyGameState(GameState):
    def __init__(self, stopped_round=False, score=0, actions=None):
        self.stopped_round = stopped_round
        self.score = score
        self._actions = actions if actions is not None else [DummyAction()]

    def get_available_actions(self):
        return self._actions

    def execute_action(self, action):
        # Returns a terminal state after any action
        return DummyGameState(stopped_round=True, score=self.score + 1, actions=[])


def test_node_not_expanded_for_terminal():
    """
    Test that _expand does not expand a node if the state is terminal.
    Should return the same node and not add any children.
    """
    terminal_state = DummyGameState(stopped_round=True, score=42, actions=[])
    node = Node(terminal_state)
    mcts = MCTS(terminal_state)
    expanded_node = mcts._expand(node)
    assert expanded_node is node
    assert node.children == {}


def test_node_expansion_for_non_terminal():
    """
    Test that _expand creates a new child node for a non-terminal state.
    Should return a new node and add one child to the parent node.
    """
    non_terminal_state = DummyGameState(
        stopped_round=False, score=0, actions=[DummyAction()]
    )
    node = Node(non_terminal_state)
    mcts = MCTS(non_terminal_state)
    expanded_node = mcts._expand(node)
    assert expanded_node is not node
    assert len(node.children) == 1


def test_simulation_returns_score():
    """
    Test that _simulate returns a score greater than or equal to the initial score.
    Ensures simulation does not decrease the score.
    """
    state = DummyGameState(stopped_round=False, score=5, actions=[DummyAction()])
    node = Node(state)
    mcts = MCTS(state)
    score = mcts._simulate(node)
    assert score >= 5


def test_terminal_node_visits():
    """
    Test that MCTS visits terminal nodes and they accumulate visit counts (N).
    """
    # Create a state where the only action is STOP, which leads to a terminal state
    state = DummyGameState(stopped_round=False, score=40, actions=[Action(Action.STOP)])

    mcts = MCTS(state)
    simulations = 50
    mcts.run(num_simulations=simulations)

    root = mcts.root

    # We expect the root to have 1 child (STOP)
    assert len(root.children) == 1
    stop_action = Action(Action.STOP)
    assert stop_action in root.children

    child = root.children[stop_action]
    assert child.is_terminal_node()

    # The child should have been visited roughly the same amount as the root (minus maybe 1 for initial expansion)
    assert child.N > 1, "Terminal child node should be visited more than once"
    assert child.N >= simulations - 1, (
        "Terminal child node should capture almost all visits"
    )


def test_backpropagation_updates_nodes():
    """
    Test that _backpropagate correctly updates visit count (N) and value (Q) for nodes.
    Both the child and its parent should be updated after backpropagation.
    """
    state = DummyGameState(stopped_round=False, score=0, actions=[DummyAction()])
    root = Node(state)
    child_state = state.execute_action(DummyAction())
    child = Node(child_state, parent=root, action_taken=DummyAction())
    score = 10
    mcts = MCTS(state)
    mcts._backpropagate(child, score)
    assert child.N == 1
    assert child.Q == score
    assert root.N == 1
