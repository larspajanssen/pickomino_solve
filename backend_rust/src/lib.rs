mod game;




#[cfg(test)]
mod tests {
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
}
