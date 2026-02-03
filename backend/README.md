# Pickomino Solver Backend

This is the backend for the Pickomino (Regenwormen) solver, implemented as a FastAPI application.

## Features
- Monte Carlo Tree Search (MCTS) implementation for optimal move calculation.
- REST API for game state evaluation.

## Development

### Prerequisites
- [uv](https://github.com/astral-sh/uv)

### Setup
```bash
uv sync
```

### Running the server
```bash
uv run uvicorn pickomino_solver.main:app --reload
```
