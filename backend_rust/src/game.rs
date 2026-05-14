use std::{collections::HashMap, fmt};
use itertools::Itertools;

#[derive(PartialEq, Eq, Hash, Debug, Clone, Copy)]
pub enum Action {
    Roll,
    Stop,
    SaveDice(u8),
    Bust,
}

type Cache = HashMap<(GameState, Action), f64>;

pub struct ActionIter {
    actions: [Action; N_FACES as usize + 2],
    index: usize,
    len: usize,
}
impl Iterator for ActionIter {
    type Item = Action;
    fn next(&mut self) -> Option<Self::Item> {
        if self.index < self.len {
            let res = Some(self.actions[self.index]);
            self.index += 1;
            res
        } else {
            None
        }
    }
}

const N_FACES: u8 = 6;
const N_DICE: u8 = 8;
const WORM_INDEX: u8 = 5;
const WORM_FACE_VALUE: u8 = 6;


#[derive(Debug)]
pub struct GameStateCreationError;
impl fmt::Display for GameStateCreationError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Number of dice in game must me smaller than {N_DICE}")
    }
}

struct ProbGameState {
    prob: f64,
    state: GameState,
}

#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)]
pub struct GameState {
    hand: [u8; N_FACES as usize],
    dice_throw: Option<[u8; N_FACES as usize]>,
}
impl GameState {
    pub fn new(hand: [u8; N_FACES as usize], dice_throw: Option<[u8; N_FACES as usize]>) -> Result<GameState, GameStateCreationError> {
        let valid_size = hand.iter().sum::<u8>() + dice_throw.unwrap_or([0; N_FACES as usize]).iter().sum::<u8>() <= N_DICE;
        match valid_size {
            true => {
                Ok(GameState { hand, dice_throw })
            }
            false => Err(GameStateCreationError),
        }
    }

    pub fn available_actions(&self) -> ActionIter {
        let mut actions = [Action::Stop; 8];
        let mut len = 0;

        let hand_count = self.hand.iter().sum::<u8>();

        if hand_count >= N_DICE {
            actions[0] = Action::Stop;
            return ActionIter { actions, index: 0, len: 1 }
        }
        match self.dice_throw {
            None => {
                actions[0] = Action::Roll;
                actions[1] = Action::Stop;
                ActionIter { actions, index: 0, len: 2 }
            }
            Some(dice) => {
                for idx in 0..N_FACES {
                    if dice[idx as usize] > 0 && self.hand[idx as usize] == 0 {
                        actions[len] = Action::SaveDice(idx + 1);
                        len += 1;
                    }
                }
                if len == 0 {
                    actions[0] = Action::Bust;
                    len = 1;
                }
                ActionIter { actions, index: 0, len }

            }
        }
    }

    pub fn compute_score(&self) -> u8 {
        if self.hand[WORM_INDEX as usize] == 0 {
            return 0;
        }
        self.hand.iter().enumerate().map(|(i, &count)| {
            let face_val = (i+1) as u8;
            let score = match face_val {
                WORM_FACE_VALUE => 5,
                val => val,
            };
            count * score
        }).sum()
    }
}

pub fn max_expected_score(
    state: &GameState,
    action: Action,
    cache: &mut Cache,
) -> f64 {
    if let Some(&score) = cache.get(&(*state, action)) {
        return score;
    }
    let result = match action {
        Action::Bust => 0.0,
        Action::Stop => {
            state.compute_score() as f64
        },
        Action::SaveDice(select_die) => {
            match &state.dice_throw {
                Some(dice_throw) => {
                    let select_die_idx = select_die - 1;
                    let count_selected_dice = dice_throw[select_die_idx as usize];
                    let mut new_state = *state;
                    new_state.hand[select_die_idx as usize] += count_selected_dice;
                    new_state.dice_throw = None;
                    new_state.available_actions().map(
                        |a| max_expected_score(&new_state, a, cache)
                    ).reduce(f64::max).unwrap()
                },
                _ => panic!("No dice thrown, while selecting die is not allowed"),
            }

        },
        Action::Roll => {
            let outcomes_iter = create_distinct_roll_outcomes_iter(state);
            // Compute weighted average over max_expected_score of ProbStates
            outcomes_iter.map(
                // For each possible state multiply its probability
                // with the max_expected_score of that probabilistic state
                |prob_state| {
                // Compute over all actions of a next state the max expected score
                let max_exp_next_score = prob_state.state.available_actions().map(|a| max_expected_score(&prob_state.state, a, cache)).reduce(f64::max).unwrap();
                prob_state.prob * max_exp_next_score
            }).sum() // sum all prob * max_exp_value_prob_state to arrive at max_exp_value
        }
    };
    cache.insert((*state, action), result);

    result
}

fn create_distinct_roll_outcomes_iter(state: &GameState) -> impl Iterator<Item = ProbGameState> {
    let throw_count: usize = (N_DICE - state.hand.iter().sum::<u8>()) as usize;
    let throw_count_factorial = factorial(throw_count);
    let total_outcomes = (N_FACES as f64).powi(throw_count as i32);

    let outcome_values = (0..N_FACES).combinations_with_replacement(throw_count);
    outcome_values.map(move |outcome| {
        let mut frequency_map = [0u8; N_FACES as usize];
        for face in outcome {
            frequency_map[face as usize] += 1;
        }
        let mut new_state = *state;
        new_state.dice_throw = Some(frequency_map);

        ProbGameState {
            prob: compute_relative_probability(&frequency_map, throw_count_factorial) / total_outcomes,
            state: {
                new_state
            }
        }
        }
    )


}

fn compute_relative_probability(frequency_map: &[u8; N_FACES as usize], n_total_factorial: usize) -> f64 {
    n_total_factorial as f64 / (
        frequency_map.iter().map(
            |&count| factorial(count as usize) as f64
        ).product::<f64>()
    )
}

fn factorial(integer: usize) -> usize {
    if integer < 2 {
        return 1
    }
    integer * factorial(integer - 1)
}
