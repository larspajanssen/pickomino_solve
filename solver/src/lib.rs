use std::collections::HashMap;
use pyo3::{exceptions::PyValueError, prelude::*};

use crate::game::GameState;
pub mod game;

#[pymodule]
fn pickomino_solver(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_state_scores, m)?)?;
    Ok(())
}

/// Python-facing wrapper around a solver action.
///
/// Exposes action fields as properties to simplify serialization in FastAPI.
#[pyclass]
pub struct PyAction {
    /// Internal Rust action.
    pub inner: game::Action,
}

#[pymethods]
impl PyAction {
    // Expose a way for Python to check what kind of action it is
    #[getter]
    fn action_type(&self) -> String {
        match self.inner {
            game::Action::Roll => "Roll".to_string(),
            game::Action::Stop => "Stop".to_string(),
            game::Action::SaveDice(_) => "SaveDice".to_string(),
            game::Action::Bust => "Bust".to_string(),
        }
    }

    // Expose the value if it's a SaveDice action, otherwise return None
    #[getter]
    fn dice_value(&self) -> Option<u8> {
        match self.inner {
            game::Action::SaveDice(val) => Some(val),
            _ => None,
        }
    }
}

#[pyfunction]
/// Compute expected scores for all available actions in a given game state.
///
/// Returns a list of `(action, expected_score)` tuples for the current state.
pub fn compute_state_scores(
    hand: [u8; game::N_FACES as usize],
    throw: Option<[u8; game::N_FACES as usize]>,
    tiles: Vec<u8>,
) -> PyResult<Vec<(PyAction, f64)>> {
    let state = GameState::new(hand, throw).map_err(|err| {
        PyValueError::new_err(format!("Problem initializing state: {err}"))
    })?;
    let valid_tiles = game::create_valid_tiles(tiles).map_err(|err| {
        PyValueError::new_err(format!("Problem initializing tiles: {err}"))
    })?;
    let mut cache = HashMap::new();
    let result = state.available_actions().map(|action| {
        let score = game::max_expected_score(&state, action, &valid_tiles, &mut cache);
        (PyAction{ inner: action }, score)
    }).collect();

    Ok(result)

}
