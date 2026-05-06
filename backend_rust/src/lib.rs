pub mod game;


#[cfg(test)]
mod tests {
    use crate::game::max_expected_score;

use super::*;

    #[test]
    fn compute_no_worm() {
        let state = game::GameState::new(
            vec![5, 5], None
        ).unwrap();
        assert_eq!(state.compute_score(), 0)
    }

    #[test]
    fn compute_with_worm() {
        let state = game::GameState::new(
            vec![5, 6], None
        ).unwrap();
        assert_eq!(state.compute_score(), 10)
    }

    #[test]
    fn stop_at_full_hand() {
        let state = game::GameState::new(
            vec![5, 5 , 5 ,5,5,5,5,5], None
        ).unwrap();
        let state_actions = state.available_actions();
        assert_eq!(state_actions, [game::Action::Stop]);
    }

    #[test]
    fn bust_at_no_option() {
        let state = game::GameState::new(
            vec![5, 5 , 5 ,5,5,5], Some(vec![5, 5])
        ).unwrap();
        let state_actions = state.available_actions();
        assert_eq!(state_actions, [game::Action::Bust]);
    }

    #[test]
    fn test_save_dice_options() {
        let state = game::GameState::new(
            vec![5, 5 , 5 ,5,5,5], Some(vec![5, 6])
        ).unwrap();
        let state_actions = state.available_actions();
        assert_eq!(state_actions, [game::Action::SaveDice(6)]);
    }

    #[test]
    fn test_roll_or_stop() {
        let state = game::GameState::new(
            vec![5, 5 , 5 ,5,5,5], None
        ).unwrap();
        let state_actions = state.available_actions();
        assert!(
            state_actions.contains(&game::Action::Roll) & state_actions.contains(&game::Action::Stop)
        )
    }

    #[test]
    fn test_max_expected_score_stop() {
        let state = game::GameState::new(
            vec![5, 6, 4, 3, 6, 6, 2], None
        ).unwrap();

        // Action::Stop

        let exp_score = max_expected_score(&state, game::Action::Stop);
        assert_eq!(exp_score, 29.);

    }

    #[test]
    fn test_max_expected_score_roll() {
        let state = game::GameState::new(
            vec![5, 6, 4, 3, 6, 6, 2], None
        ).unwrap();

        // Action::Roll
        let exp_score = max_expected_score(&state, game::Action::Roll);
        assert_eq!(exp_score, 5.);
    }

    #[test]
    fn test_max_expected_score_bust() {
        let state = game::GameState::new(
            vec![5, 6, 4, 3, 6, 6, 2], Some(vec![2])
        ).unwrap();

        let exp_score = max_expected_score(&state, game::Action::Bust);
        assert_eq!(exp_score, 0.);
    }

    #[test]
    fn test_max_expected_score_save_dice() {
        let state = game::GameState::new(
            vec![5, 6, 4, 3, 6, 6], Some(vec![2])
        ).unwrap();

        let exp_score = max_expected_score(&state, game::Action::SaveDice(2));
        assert_eq!(exp_score, 29.)
    }

    #[test]
    fn test_max_expected_score_performance() {
        let state1 = game::GameState::new(
            vec![6, 6, 6], None
        ).unwrap();

        let state2 = game::GameState::new(
            vec![2, 2, 2], None
        ).unwrap();

        let exp_score1 = max_expected_score(&state1, game::Action::Roll);
        let exp_score2 = max_expected_score(&state2, game::Action::Roll);
        assert!(exp_score1 > exp_score2);
        assert!(exp_score1 > 0.);
        assert!(exp_score2 > 0.);
    }
}
