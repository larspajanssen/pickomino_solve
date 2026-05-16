# Pickomino Solver Backend

This directory contains the FastAPI wrapper around the Rust-backed Pickomino solver.

The backend accepts normalized dice state from the frontend, calls the solver exposed by `backend_rust/`, and serializes the ranked actions returned to the browser.

## API

### `POST /api/run`

Request body:

- `hand`: frequency vector of length 6 for the saved dice
- `dice_throw`: optional frequency vector of length 6 for the current throw

Example:

```json
{
  "hand": [0, 0, 0, 0, 1, 1],
  "dice_throw": [0, 1, 0, 0, 0, 1]
}
```

The response contains an `actions` array with action labels and expected values.

## Development

### Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv)
- Rust toolchain (`cargo`, `rustup`), because the Python package builds the solver extension from `../backend_rust`

### Setup

```bash
uv sync
```

### Running the server

```bash
uv run uvicorn pickomino_solver.main:app --reload --host 0.0.0.0 --port 6000
```

### Solver Development

The Rust crate lives in `../backend_rust/`.

```bash
cd ../backend_rust
cargo test
```
