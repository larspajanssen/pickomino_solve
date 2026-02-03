# MCTS Regenwormen

A web-based implementation of the "Regenwormen" (Pickomino) dice game, featuring a powerful AI opponent powered by Monte Carlo Tree Search (MCTS).

![Regenwormen UI](assets/ui.png)

## Features

- **Interactive UI**: Play the game using a modern, dark-themed web interface with clickable 3D dice.
- **Smart AI**: Analyze moves using a Monte Carlo Tree Search (MCTS) backend that suggests the best actions.
- **Data Visualization**: Real-time convergence graphs showing how the AI evaluates different moves.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- *Or* Python 3.12+ (for local backend development)

### Quick Start (Docker)

To start the full application (frontend + backend):

```bash
docker-compose up -d --build
```

The application will be available at:
- Frontend: `http://localhost:80` (or configured port)
- Backend API: `http://localhost:6000`

## Development

The project is structured into two main components:

- **`frontend/`**: The web interface (HTML/CSS/JS).
- **`backend/`**: The Python FastAPI application and MCTS logic.

### Backend Setup (Local)
Dependencies are managed with `uv`.

```bash
cd backend
uv sync
uv run main.py
```

## AI Implementation

The core of this project is the **Monte Carlo Tree Search (MCTS)** algorithm located in `backend/src/tree.py`.

### Future Roadmap: Game Logic & UI

#### Valid End Scores & Tile Logic
Currently, the game accepts any gathered sum as a valid score. In the physical game of Pickomino (Regenwormen), a turn is only successful if:
1. The total score matches a tile still available on the board (values 21–36).
2. At least one "Worm" (dice value 5/6) has been saved.

**Proposed Solution Direction:**
- **Backend Logic**: Update `GameState.execute_action` in `backend/src/game.py`. Specifically, in the `Action.STOP` handler, validate the `score` against the available tile set. If invalid, the result should be a **BUST** (score = 0).
- **Frontend UI**:
    - Dynamically disable or dim the "Stop" button in `frontend/app.js` when the current hand does not meet the valid score requirements.
    - Highlight valid target tiles in the UI to guide the player (or AI).
- **Configuration**: Add a new configuration panel to allow users to toggle which tiles are "available" (e.g., to simulate a mid-game state where tiles 21, 24, and 30 have already been taken).

#### Performance: The "Big Engine Upgrade"
To significantly increase the number of simulations (and thus AI strength) without simpler heuristics, we plan to compile the Python logic.
- **Goal**: Performance boost.
- **Mechanism**: Use `mypyc` or `Cython` to compile `tree.py` and `game.py` into native C extensions, bypassing the Python interpreter loop for the MCTS "hot path".



## Hosting on Ubuntu Server

This guide assumes a fresh Ubuntu installation (tested on 20.04/22.04 LTS). We use a **pull-based deployment strategy**: code is pulled from Git, and Docker builds the containers directly on the server.

### 1. Deployment

Clone the repository and start the application.

```bash
# Clone the repository (HTTPS - No keys required for public repos)
git clone https://github.com/LarsPAJanssen/pickomino_solve.git
cd pickomino_solve

# Start the application
# This builds the images and starts containers in the background
docker-compose up -d --build
```

The application is now running:
- **Frontend**: `http://<YOUR_SERVER_IP>`
- **Backend**: `http://<YOUR_SERVER_IP>:6000`

### 2. Management & Updates

Common maintenance tasks.

```bash
# View logs (follow mode)
docker-compose logs -f

# Update Application
git pull origin main       # Get latest code
docker-compose up -d --build # Rebuild and restart only changed containers

# Stop Application
docker-compose down
```

## License

[MIT](LICENSE)
