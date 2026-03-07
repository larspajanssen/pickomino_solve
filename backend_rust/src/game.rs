use std::collections::HashSet;

#[derive(PartialEq, Eq, Hash, Debug)]
pub enum Action {
    Roll,
    Stop,
    SaveDice(u8),
    Bust,
}

static DIE: &[u8] = &[1, 2, 3, 4, 5, 6];
const N_DICE: u8 = 8;

pub struct GameState {
    hand: Vec<u8>,
    dice_throw: Option<Vec<u8>>,
}
impl GameState {
    pub fn new(hand: Vec<u8>, dice_throw: Option<Vec<u8>>) -> Self {
        GameState { hand, dice_throw }
    }
}

pub trait State {
    fn available_actions(&self) -> Vec<Action>;
    fn compute_score(&self) -> u32;
}

impl State for GameState {
    fn available_actions(&self) -> Vec<Action> {
        if self.hand.len() >= N_DICE as usize {
            return vec![Action::Stop];
        }
        match self.dice_throw {
            None => vec![Action::Roll, Action::Stop],
            Some(ref dice) => {
                let actions: HashSet<Action> = dice
                    .iter()
                    .filter(|die| !self.hand.contains(die))
                    .map(|&die| Action::SaveDice(die))
                    .collect();

                if actions.is_empty() {
                    vec![Action::Bust]
                } else {
                    actions.into_iter().collect()
                }
            }
        }
    }

    fn compute_score(&self) -> u32 {
        let mut score = 0;
        if self.hand.contains(&6) {
            for die in &self.hand {
                score += *die as u32;
            }
        }
        score
    }
}
