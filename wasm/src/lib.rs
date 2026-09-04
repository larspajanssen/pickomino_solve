use wasm_bindgen::prelude::*;

/// Convert a JavaScript request, execute the core solver, and return a plain JS object.
#[wasm_bindgen]
pub fn solve(request: JsValue) -> Result<JsValue, JsValue> {
    let request: pickomino_solver::SolveRequest = serde_wasm_bindgen::from_value(request)
        .map_err(|error| JsValue::from_str(&format!("Invalid solve request: {error}")))?;
    let result =
        pickomino_solver::solve(request).map_err(|error| JsValue::from_str(&error.to_string()))?;
    serde_wasm_bindgen::to_value(&result)
        .map_err(|error| JsValue::from_str(&format!("Could not serialize solve result: {error}")))
}
