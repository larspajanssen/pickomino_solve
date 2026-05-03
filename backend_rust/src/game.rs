use std::collections::HashSet;
use std::fmt;

#[derive(PartialEq, Eq, Hash, Debug)]
pub enum Action {
    Roll,
    Stop,
    SaveDice(u8),
    Bust,
}

static DIE: &[u8] = &[1, 2, 3, 4, 5, 6];
const N_DICE: u8 = 8;
const WORM: u8 = 6;

#[derive(Debug)]
pub struct GameStateCreationError;
impl fmt::Display for GameStateCreationError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Number of dice in game must me smaller than {N_DICE}")
    }
}


pub struct GameState {
    hand: Vec<u8>,
    dice_throw: Option<Vec<u8>>,
}
impl GameState {
    pub fn new(hand: Vec<u8>, dice_throw: Option<Vec<u8>>) -> Result<GameState, GameStateCreationError> {
        let valid_size = hand.len() + dice_throw.as_ref().map(|v| v.len()).unwrap_or(0) <= N_DICE.into();
        match valid_size {
            true => {
                Ok(GameState { hand, dice_throw })
            }
            false => Err(GameStateCreationError),
        }
    }

    pub fn available_actions(&self) -> Vec<Action> {
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

    pub fn compute_score(&self) -> u8 {
        if !self.hand.contains(&WORM) {
            return 0;
        }
        self.hand.iter().map(|&die| {
            match die {
                6 => 5,
                val => val,
            }
        }).sum()
    }
}

// pub fn expected_score(state: GameState, action: Action) -> u8 {
//     match action {
//         Action::Bust => 0,
//         Action::Stop => state.compute_score(),
//         Action::SaveDice(d) =>

//     }
// }
