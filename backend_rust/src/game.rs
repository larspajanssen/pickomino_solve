enum Action {
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
    score: u32,
}
impl GameState {
    fn available_actions(&self) -> Vec<Action> {
        if self.hand.len() == N_DICE as usize {
            return vec![Action::Stop];
        }
        match self.dice_throw {
            None => vec![Action::Roll, Action::Stop],
            Some(ref dice) => {
                let mut die_options: Vec<u8> = Vec::new();
                // For each die in throw that is not in hand add to options
                for die in dice {
                    if !self.hand.contains(die) && !die_options.contains(die) {
                        die_options.push(*die);
                    }
                }
                // if no options, then bust
                // else add all options as Action::SaveDice(die_option)
                if die_options.is_empty() {
                    vec![Action::Bust]
                } else {
                    let mut actions = Vec::new();
                    for die in die_options {
                        actions.push(Action::SaveDice(die));
                    }
                    actions
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
