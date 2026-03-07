use super::game::{Action, GameState};

pub struct ValuedAction {
    action: Action,
    score: u32,
    visits: u32,
}
impl ValuedAction {
    fn value(&self) -> f64 {
        if self.visits == 0 {
            return 0.0;
        }
        self.score as f64 / self.visits as f64
    }
}

struct Node {
    state: GameState,
    children: Vec<Node>,
    is_terminal: bool,
}
impl Node {
    fn is_terminal(&mut self) -> bool {
        if !self.is_terminal {
            self.is_terminal = self.children.is_empty();
        }
        self.is_terminal
    }
}

struct ChanceNode {
    state: GameState,
    children: Vec<Node>,
}

trait NodeTraits {
    fn select(&self) -> &Node;
    fn expand(&mut self);
    fn best_child(&self) -> Option<&Node>;
}

fn select<T: NodeTraits>(node: &T, c: f64) -> &T {
    node
}


pub fn run(hand: Vec<u8>, dice_throw: Option<Vec<u8>>, c: f64) -> Vec<ValuedAction> {
    let mut root_node = Node {
        state: GameState::new(hand, dice_throw),
        children: vec![],
        is_terminal: false,
    };

    loop {
        let node = ;

    }
}
