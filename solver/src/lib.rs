use serde::{Deserialize, Serialize};
use std::collections::HashMap;

pub mod game;

pub type DiceCounts = [u8; game::N_FACES as usize];

#[derive(Debug, Clone, Deserialize)]
pub struct SolveRequest {
    pub hand: DiceCounts,
    pub dice_throw: Option<DiceCounts>,
    pub tiles: Vec<u8>,
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct ActionResult {
    pub action: String,
    pub expected_value: f64,
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct SolveResult {
    pub actions: Vec<ActionResult>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct SolveError(pub String);

impl std::fmt::Display for SolveError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

/// Solve a validated game state using the platform-independent Rust core.
pub fn solve(request: SolveRequest) -> Result<SolveResult, SolveError> {
    let state = game::GameState::new(request.hand, request.dice_throw)
        .map_err(|err| SolveError(err.to_string()))?;
    let valid_tiles =
        game::create_valid_tiles(request.tiles).map_err(|err| SolveError(err.to_string()))?;
    let mut cache = HashMap::new();
    let actions = state
        .available_actions()
        .map(|action| ActionResult {
            action: action.to_string(),
            expected_value: game::max_expected_score(&state, action, &valid_tiles, &mut cache),
        })
        .collect();

    Ok(SolveResult { actions })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn solve_serializes_action_names_and_values() {
        let result = solve(SolveRequest {
            hand: [0, 1, 1, 1, 1, 3],
            dice_throw: None,
            tiles: (21..=36).collect(),
        })
        .unwrap();

        assert_eq!(result.actions[0].action, "Roll");
        assert_eq!(result.actions[1].action, "Stop");
        assert_eq!(result.actions[1].expected_value, 3.0);
    }

    #[test]
    fn solve_rejects_empty_tiles() {
        let error = solve(SolveRequest {
            hand: [0; 6],
            dice_throw: None,
            tiles: vec![],
        })
        .unwrap_err();
        assert!(error.to_string().contains("between 21 and 36"));
    }

    #[test]
    fn solve_rejects_more_than_eight_dice() {
        let error = solve(SolveRequest {
            hand: [255; 6],
            dice_throw: None,
            tiles: vec![21],
        })
        .unwrap_err();
        assert!(error.to_string().contains("smaller than 8"));
    }
}
