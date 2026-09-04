# Regenwormen solver

[![prek](https://github.com/LarsPAJanssen/pickomino_solve/actions/workflows/pre-commit.yml/badge.svg?branch=main)](https://github.com/LarsPAJanssen/pickomino_solve/actions/workflows/pre-commit.yml)

A web-based implementation of the Regenwormen / Pickomino dice game with an AI solver. The React frontend calls a Rust solver compiled to WebAssembly directly in the browser.

![Regenwormen UI](assets/ui.png)

## Features

- Interactive browser UI with dice editing and live solver results.
- Rust-backed solver logic for faster action evaluation and search.
- Docker Compose setup for running the static app locally or on a server.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Rust and `wasm-bindgen-cli` for local WASM builds
- Node.js 20+ and npm

### Quick Start

Start the full application with Docker Compose:

```bash
docker compose up -d --build
```

Open `http://127.0.0.1:8080` after the build completes.

The frontend proxies API requests to the API container automatically, so you do not need to expose the API port publicly for normal use.

## Development

The project is split into three parts:

- `frontend/`: Vite, React, and TypeScript UI.
- `wasm/`: Thin `wasm-bindgen` adapter.
- `solver/`: Platform-independent Rust solver crate.

### Development

The performance-critical game logic is implemented in `solver/src/`.

```bash
cargo test
rustup target add wasm32-unknown-unknown
wasm-bindgen target/wasm32-unknown-unknown/release/pickomino_wasm.wasm --target web --out-dir wasm/pkg
cd frontend
npm install
npm run build
```

The solver accepts a request with `hand`, nullable `dice_throw`, and `tiles`, and returns ranked `actions`. The request is passed from TypeScript to WASM without an HTTP hop.

## License

[MIT](LICENSE)
