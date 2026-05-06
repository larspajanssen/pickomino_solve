use std::collections::{HashMap, HashSet};
use std::fmt;
use itertools::Itertools;

#[derive(PartialEq, Eq, Hash, Debug, Clone, Copy)]
pub enum Action {
    Roll,
    Stop,
    SaveDice(u8),
    Bust,
}

static DIE: &[u8] = &[1, 2, 3, 4, 5, 6];
const N_FACES: u8 = 6;
const N_DICE: u8 = 8;
const WORM: u8 = 6;

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

#[derive(Debug, Clone)]
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

pub fn max_expected_score(state: &GameState, action: Action) -> f64 {
    match action {
        Action::Bust => 0 as f64,
        Action::Stop => state.compute_score() as f64,
        Action::SaveDice(select_die) => {
            match &state.dice_throw {
                Some(dice_throw) => {
                    let mut new_hand = state.hand.clone();

                    let saved_dice: Vec<u8> = dice_throw
                        .iter()
                        .filter(|&&die| die == select_die).copied().collect();

                    new_hand.extend(saved_dice);
                    let new_state = GameState::new(new_hand, None).unwrap();

                    new_state.available_actions().iter().map(
                        |&a| max_expected_score(&new_state, a)
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
                let max_exp_next_score = prob_state.state.available_actions().iter().map(|&a| max_expected_score(&prob_state.state, a)).reduce(f64::max).unwrap();
                prob_state.prob * max_exp_next_score
            }).sum() // sum all prob * max_exp_value_prob_state to arrive at max_exp_value

        }

    }
}

fn create_distinct_roll_outcomes_iter(state: &GameState) -> impl Iterator<Item = ProbGameState> {
    let throw_count = (N_DICE as usize) - state.hand.len();
    let n_outcomes = (N_FACES as f64).powi(throw_count as i32);

    // Calculate weight using multinomial coefficient: n! / (n1! * n2! * ... * nk!)
    // where n is total dice, and ni is count of each face
    DIE.iter().combinations_with_replacement(throw_count)
    .map(move |outcome | {
            let prob = (
                compute_relative_probability(&outcome)
            ) / (n_outcomes);

            let outcome: Vec<u8> = outcome.into_iter().cloned().collect();

            let new_game_state = GameState::new(
                state.hand.clone(),
                Some(outcome)
            ).expect("Failed to create GameState");

            ProbGameState{
                prob,
                state: new_game_state,
            }

        })

}

fn compute_relative_probability(outcome: &Vec<&u8>) -> f64 {
    let counts = counter(outcome);
    let num_dice = outcome.len();

    (factorial(num_dice) as f64) / (
        counts.iter().map(
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

fn counter(input: &[&u8]) -> Vec<u8> {
    let mut counts = HashMap::new();
    let mut order = Vec::new();

    for &&num in input {
        let count = counts.entry(num).or_insert(0u8);
        if *count == 0 {
            order.push(num);
        }
        *count += 1;
    }

    order.into_iter()
        .map(|num| counts[&num])
        .collect()

}
