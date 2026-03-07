use super::game::{Action, GameState};

pub struct TreeNode {
    state: GameState,
    parent: Option<Box<TreeNode>>,
    children: Vec<TreeNode>,
    score: u32,
    visits: u32,
    is_expanded: bool,
    is_terminal: bool,
}
impl TreeNode {
    fn new(state: GameState, parent: Option<Box<TreeNode>>) -> Self {
        TreeNode {
            state,
            parent,
            children: vec![],
            score: 0,
            visits: 0,
            is_expanded: false,
            is_terminal: false,
        }
    }

    fn compute_ucb(&self, c: f64) -> f64 {
        if self.visits == 0 {
            return f64::INFINITY;
        }
        (self.score as f64 / self.visits as f64)
            + c * ((self.visits as f64).ln() / self.visits as f64).sqrt()
    }

    fn simulate(&mut self) {}

    fn expand(&mut self) {}

    fn backpropagate(&mut self) {}
}

fn select(node: &TreeNode, c: f64) -> Option<&TreeNode> {
    let mut next_node = node;
    while next_node.is_expanded {
        // IF child node is a chance node then select according to probabilistic sample
        // TODO: implement logic for chance nodes?

        // ELSE select child with highest UCB value
        for child in &next_node.children {
            if child.is_terminal {
                continue; // Skip terminal nodes
            }
            let ucb = child.compute_ucb(c);
            if ucb > next_node.compute_ucb(c) {
                next_node = child;
            }
        }
    }
    if next_node.is_expanded {
        return None; // No more nodes to explore
    }
    Some(next_node)
}

pub fn run(hand: Vec<u8>, dice_throw: Option<Vec<u8>>, c: f64) -> Vec<Action> {
    let mut root: TreeNode = TreeNode::new(GameState::new(hand, dice_throw), None);
    // TODO: Implement logic for setting the loop size
    loop {
        // Iteration of MCTS algorithm
        match select(&root, c) {
            Some(node) => {
                node.expand(); // TODO: implement expansion logic - must implement that all terminal child nodes are marked as expanded
                node.simulate(); // TODO: implement simulation logic
                node.backpropagate(); // TODO: implement backpropagation logic
            }
            None => break, // No more nodes to explore
        }
    }
    // TODO: implement logic for computing best action from tree search results
    vec![Action::Roll] // Placeholder, implement logic to return best action based on tree search
}
