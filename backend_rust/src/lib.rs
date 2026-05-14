pub mod game;


#[cfg(test)]
mod tests {
    use crate::game::max_expected_score;
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn compute_no_worm() {
        let state = game::GameState::new(
            [0, 0, 0, 0, 2, 0], None
        ).unwrap();
        assert_eq!(state.compute_score(), 0)
    }

    #[test]
    fn compute_with_worm() {
        let state = game::GameState::new(
            [0, 0, 0, 0, 1, 1], None
        ).unwrap();
        assert_eq!(state.compute_score(), 10)
    }

    #[test]
    fn stop_at_full_hand() {
        let state = game::GameState::new(
            [0, 0, 0, 0, 8, 0], None
        ).unwrap();
        let state_actions = state.available_actions();
        itertools::assert_equal(state_actions, [game::Action::Stop]);
    }

    #[test]
    fn bust_at_no_option() {
        let state = game::GameState::new(
            [0, 0, 0, 0, 6, 0], Some([0, 0, 0, 0, 2, 0])
        ).unwrap();
        let state_actions = state.available_actions();
        itertools::assert_equal(state_actions, [game::Action::Bust]);
    }

    #[test]
    fn test_save_dice_options() {
        let state = game::GameState::new(
            [0, 0, 0, 0, 6, 0], Some([0, 0, 0, 0, 1, 1])
        ).unwrap();
        let state_actions = state.available_actions();
        itertools::assert_equal(state_actions, [game::Action::SaveDice(6)]);
    }

    #[test]
    fn test_roll_or_stop() {
        let state = game::GameState::new(
            [0, 0, 0, 0, 6, 0], None
        ).unwrap();
        let state_actions: Vec<game::Action> = state.available_actions().collect();
        assert!(
            state_actions.contains(&game::Action::Roll) & state_actions.contains(&game::Action::Stop)
        )
    }

    #[test]
    fn test_max_expected_score_stop() {
        let mut cache = HashMap::new();
        let state = game::GameState::new(
            [0, 1, 1, 1, 1, 3], None
        ).unwrap();

        // Action::Stop

        let exp_score = max_expected_score(&state, game::Action::Stop, &mut cache);
        assert_eq!(exp_score, 29.);

    }

    #[test]
    fn test_max_expected_score_roll() {
        let mut cache = HashMap::new();

        let state = game::GameState::new(
            [0, 1, 1, 1, 1, 3], None
        ).unwrap();

        // Action::Roll
        let exp_score = max_expected_score(&state, game::Action::Roll, &mut cache);
        assert_eq!(exp_score, 5.);
    }

    #[test]
    fn test_max_expected_score_bust() {
        let mut cache = HashMap::new();

        let state = game::GameState::new(
            [0, 1, 1, 1, 1, 3],Some([0, 1, 0, 0, 0, 0])
        ).unwrap();

        let exp_score = max_expected_score(&state, game::Action::Bust, &mut cache);
        assert_eq!(exp_score, 0.);
    }

    #[test]
    fn test_max_expected_score_save_dice() {
        let mut cache = HashMap::new();

        let state = game::GameState::new(
            [0, 0, 1, 1, 1, 3], Some([0, 1, 0, 0, 0, 0])
        ).unwrap();

        let exp_score = max_expected_score(&state, game::Action::SaveDice(2), &mut cache);
        assert_eq!(exp_score, 29.)
    }

    #[test]
    fn test_max_expected_score_performance() {
        let mut cache = HashMap::new();

        let state1 = game::GameState::new(
            [0, 0, 0, 0, 0, 3], None
        ).unwrap();

        let state2 = game::GameState::new(
            [0, 3, 0, 0, 0, 0], None
        ).unwrap();

        let exp_score1 = max_expected_score(&state1, game::Action::Roll, &mut cache);
        let exp_score2 = max_expected_score(&state2, game::Action::Roll, &mut cache);
        assert!(exp_score1 > exp_score2);
        assert!(exp_score1 > 0.);
        assert!(exp_score2 > 0.);
    }
}
