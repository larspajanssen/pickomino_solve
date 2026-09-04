# Pickomino Solver — Rust/WASM + React Refactor Plan

## Implementation status

The core migration described below is implemented in this checkout. Browser end-to-end coverage is intentionally omitted; the remaining unchecked item is optional Web Worker support.

## 1. Goal

Refactor the current Pickomino solver application from:

```text
Browser
  ↓
Frontend
  ↓
FastAPI
  ↓
PyO3
  ↓
Rust solver
```

to:

```text
Browser
┌───────────────────────────────────────┐
│ React + TypeScript                    │
│        │                              │
│        ▼                              │
│ Rust/WASM                             │
│        │                              │
│        ▼                              │
│ Pure Rust Pickomino solver            │
└───────────────────────────────────────┘
```

The desired production application has **no backend server**. The Rust solver runs directly in the user's browser through WebAssembly.

The application can be deployed either:

1. as static files to a static hosting provider, or
2. as a **single lightweight container image** containing the React/WASM static assets and a static web server.

The primary architectural goal is to remove unnecessary runtime boundaries while preserving the existing solver behaviour.

---

## 2. Why this architecture

This project is a particularly good candidate for Rust/WASM because:

- The computationally important part is already written in Rust.
- The existing Python/FastAPI layer is thin and primarily bridges requests into Rust.
- The solver is deterministic and self-contained.
- There is no obvious requirement for secrets, authentication, a database, or server-side state.
- Solver requests can be executed entirely on the user's machine.
- The frontend only needs to submit game state and receive solver results.
- Removing HTTP/FastAPI/PyO3 eliminates several layers of overhead and maintenance.

### Benefits

- One programming backend language: Rust.
- React/TypeScript for the UI.
- No Python runtime.
- No FastAPI.
- No PyO3 boundary.
- No API server.
- No CORS concerns.
- No request latency for solver calls.
- Works offline after the application has loaded.
- Potentially deployable as completely static files.
- Very small production deployment.
- Rust solver remains reusable outside the browser.

### Main risk

The main additional complexity is the Rust → WebAssembly toolchain and JS/WASM integration.

Do not compensate for this by coupling the solver to WASM. The solver should remain a normal, browser-independent Rust library.

---

# 3. Target architecture

Use a Rust workspace with a pure solver crate and a thin WASM adapter.

```text
pickomino_solve/
│
├── Cargo.toml
│
├── solver/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── game.rs
│       ├── solver.rs
│       ├── actions.rs
│       └── types.rs
│
├── wasm/
│   ├── Cargo.toml
│   └── src/
│       └── lib.rs
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── wasm.ts
│       ├── types.ts
│       └── components/
│
├── Dockerfile
└── README.md
```

Conceptually:

```text
                    ┌──────────────┐
                    │ React / TS   │
                    └──────┬───────┘
                           │
                    clean TS API
                           │
                    ┌──────▼───────┐
                    │ WASM adapter │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Rust solver  │
                    │     core     │
                    └──────────────┘
```

The solver core must not depend on:

- React
- JavaScript
- WebAssembly
- Axum
- HTTP
- browser APIs

---

# 4. Migration principles

## 4.1 Preserve solver behaviour

Do not rewrite the solver algorithm unnecessarily.

The first objective is architectural migration, not algorithmic improvement.

Existing solver behaviour should become the regression baseline.

## 4.2 Keep boundaries explicit

The WASM crate is an adapter, not the solver.

The desired dependency direction is:

```text
frontend
   ↓
wasm
   ↓
solver
```

Never:

```text
solver
   ↓
wasm
```

or:

```text
solver
   ↓
JavaScript/browser APIs
```

## 4.3 Keep the public WASM API small

React should see a small, stable API such as:

```typescript
const result = solve({
    hand: [...],
    diceThrow: [...],
    tiles: [...]
});
```

It should not need to know about internal Rust structs or implementation details.

## 4.4 Separate UI state from game logic

React owns:

- selected dice
- UI state
- loading state
- errors
- presentation

Rust owns:

- game rules
- legal actions
- scoring
- probabilities
- expected values
- solver/search
- memoization

Do not duplicate game rules in TypeScript.

---

# 5. Phase 0 — Establish the behavioural baseline

Before changing the architecture, document and test the existing behaviour.

## Tasks

### 5.1 Document the current API

Capture the current request and response format used by `/api/run`.

Record:

- request fields
- data types
- optional fields
- validation rules
- response fields
- action representation
- expected-value semantics
- error behaviour

### 5.2 Create golden test cases

Create representative solver inputs and expected outputs.

Include:

- empty/initial state
- normal dice throws
- multiple legal actions
- forced actions
- bust situations
- missing tiles
- boundary tile values
- unusual but valid dice states
- invalid input

Prefer testing meaningful solver outcomes rather than exact incidental ordering unless ordering is part of the contract.

### 5.3 Benchmark the current solver

Measure:

1. pure solver execution time if possible
2. current Python → PyO3 → Rust request time
3. representative worst-case solver time

These numbers provide a before/after performance baseline.

---

# 6. Phase 1 — Extract a clean Rust solver core

Refactor the existing Rust implementation so it is a normal Rust library independent of PyO3.

## Target API

Conceptually:

```rust
pub fn solve(request: SolveRequest) -> Result<SolveResult, SolveError>
```

Introduce explicit domain types where useful.

For example:

```rust
pub struct SolveRequest {
    pub hand: DiceCounts,
    pub dice_throw: DiceCounts,
    pub tiles: Vec<u8>,
}

pub struct SolveResult {
    pub actions: Vec<ActionResult>,
}
```

Internally it is fine to continue using efficient representations such as:

```rust
type DiceCounts = [u8; 6];
```

but consider wrapping low-level representations in domain types when that improves correctness or readability.

## Validation

Validation should live close to the domain model.

Examples:

- exactly six dice counts
- valid dice values
- valid tile values
- valid number of dice
- valid game-state combinations

Do not rely on the frontend for correctness.

---

# 7. Phase 2 — Remove PyO3 from the solver core

The current PyO3 functionality exists only to expose the Rust implementation to Python.

Move/remove:

- `#[pyclass]`
- `#[pyfunction]`
- `#[pymodule]`
- Python-specific conversion code
- PyO3 dependencies

The solver crate should become ordinary Rust.

At the end of this phase:

```text
cargo test
```

should test the solver without Python.

Do not delete the Python/FastAPI application until the new implementation has reached parity.

---

# 8. Phase 3 — Create the Rust workspace

Convert the repository to a Cargo workspace.

Example:

```toml
[workspace]
members = [
    "solver",
    "wasm",
]
resolver = "2"
```

The dependency graph should be:

```text
wasm
  ↓
solver
```

The solver crate should remain usable independently.

Potential future consumers could include:

```text
solver
 ├── wasm
 ├── native CLI
 └── native server
```

This keeps future architectural options open.

---

# 9. Phase 4 — Build the WASM adapter

Create a dedicated `wasm` crate.

Likely tooling:

- `wasm-bindgen`
- `serde`
- `serde-wasm-bindgen`
- appropriate WASM target/tooling

The adapter should translate between JavaScript objects and Rust domain types.

Conceptually:

```rust
#[wasm_bindgen]
pub fn solve(request: JsValue) -> Result<JsValue, JsValue> {
    let request: SolveRequest =
        serde_wasm_bindgen::from_value(request)?;

    let result = solver::solve(request)?;

    Ok(serde_wasm_bindgen::to_value(&result)?)
}
```

The exact implementation should be determined during implementation based on the current Rust types and WASM tooling.

## Important

Keep the adapter extremely thin.

It should primarily handle:

```text
JS object
   ↓
Rust request
   ↓
solver
   ↓
Rust result
   ↓
JS object
```

Do not put game logic here.

---

# 10. Phase 5 — Define the TypeScript-facing API

The generated WASM bindings should be hidden behind a small TypeScript module.

For example:

```text
frontend/src/wasm.ts
```

React should interact with:

```typescript
solve(request);
```

rather than directly interacting with generated WASM internals.

Define TypeScript types corresponding to the public application API.

Example:

```typescript
export interface SolveRequest {
  hand: number[];
  diceThrow: number[];
  tiles: number[];
}

export interface ActionResult {
  action: string;
  expectedValue: number;
}

export interface SolveResult {
  actions: ActionResult[];
}
```

Prefer generated TypeScript declarations where practical, but keep the frontend-facing interface intentionally stable and understandable.

---

# 11. Phase 6 — Replace the frontend with React + TypeScript

Create a Vite-based React application.

Recommended baseline:

- React
- TypeScript
- Vite

Avoid introducing additional state-management libraries unless the UI actually needs them.

Start by reproducing the current functionality.

Do not simultaneously redesign the entire user experience.

## Suggested structure

```text
frontend/src/
├── main.tsx
├── App.tsx
├── wasm.ts
├── types.ts
└── components/
    ├── GameBoard.tsx
    ├── DicePool.tsx
    ├── SavedDice.tsx
    ├── AvailableTiles.tsx
    ├── SolverResults.tsx
    └── Controls.tsx
```

The exact component boundaries can evolve after the initial migration.

---

# 12. Phase 7 — Integrate WASM into React

Application startup should initialize the WASM module.

Conceptually:

```text
React application
      │
      ▼
initialize WASM
      │
      ▼
render application
```

When the user requests a solution:

```text
React state
    ↓
SolveRequest
    ↓
WASM
    ↓
Rust solver
    ↓
SolveResult
    ↓
React state
    ↓
UI
```

There should be no HTTP request involved.

---

# 13. Phase 8 — Consider a Web Worker

Do not introduce a Web Worker automatically.

First benchmark the WASM solver.

If solver execution is short enough, direct WASM calls are simplest.

If solving takes long enough to block the browser's main thread, move WASM execution into a Web Worker:

```text
React
  │
  ▼
Web Worker
  │
  ▼
Rust/WASM
  │
  ▼
Solver
```

Use this only when required by measured performance.

The architecture should make this possible without changing the solver itself.

---

# 14. Phase 9 — Testing

Testing should exist at three levels.

## 14.1 Rust solver tests

Preserve and expand the existing Rust unit tests.

Test:

- scoring
- legal actions
- expected values
- state transitions
- memoization correctness
- edge cases

These tests must run without WASM.

## 14.2 WASM/API compatibility tests

Verify that:

```text
JavaScript input
    ↓
WASM conversion
    ↓
Rust solver
    ↓
JavaScript output
```

produces the same results as the Rust core.

Use the golden test cases from Phase 0.

## 14.3 React tests

Test important UI behaviour:

```text
user changes dice
→ state changes

user requests solution
→ WASM solver called

solver returns results
→ results displayed
```

Avoid testing implementation details unnecessarily.

## 14.4 End-to-end test

Add at least one browser-level test covering:

```text
open application
→ configure game
→ solve
→ verify result
```

---

# 15. Phase 10 — Remove FastAPI and Python

Only after the Rust/WASM implementation has reached parity:

Delete the old backend.

Remove:

- FastAPI
- Python package
- PyO3 bindings
- Python dependency management
- backend Docker setup
- old API glue

Update documentation to describe the browser/WASM architecture.

The final runtime dependency chain should be:

```text
React
  ↓
WASM
  ↓
Rust solver
```

---

# 16. Phase 11 — Production build

Use Vite to produce static frontend assets.

Conceptually:

```bash
npm run build
```

produces:

```text
dist/
├── index.html
├── assets/
│   ├── *.js
│   ├── *.css
│   └── *.wasm
└── ...
```

The WASM binary is simply another static asset downloaded by the browser.

---

# 17. Deployment option A — Static hosting

This is the cleanest deployment model.

Deploy the `dist/` directory to any static hosting provider.

Examples:

```text
GitHub Pages
Cloudflare Pages
Netlify
S3-compatible storage
nginx
```

There is no application server.

After the initial page and WASM have loaded, solver execution is local to the browser.

The application can potentially work offline if the appropriate caching/PWA strategy is added later.

---

# 18. Deployment option B — Single Docker image

If Docker is preferred, package the static files into one image.

The container does **not** need to run Rust.

It only needs to serve:

```text
index.html
JS
CSS
WASM
```

Architecture:

```text
┌───────────────────────────────┐
│ pickomino image               │
│                               │
│ lightweight static server     │
│                               │
│   ├── React assets            │
│   └── Rust/WASM assets        │
└───────────────────────────────┘
```

A multi-stage Docker build is recommended:

```text
Stage 1
Rust/WASM build
        +
React build
        ↓
Stage 2
static web server
        ↓
small production image
```

The final image should contain no:

- Python
- Rust compiler
- Node.js
- Cargo
- development dependencies

Only the generated static assets and the static web server should remain.

---

# 19. Docker deployment target

The desired Docker invocation should eventually be no more complicated than:

```bash
docker build -t pickomino .
docker run -p 8080:80 pickomino
```

No separate Compose, backend, or frontend services are required.

---

# 20. CI/CD

Add a CI pipeline that performs:

```text
1. cargo test
2. WASM build
3. frontend typecheck
4. frontend tests
5. frontend production build
6. end-to-end tests
7. Docker build
```

A useful dependency structure is:

```text
                 cargo test
                     │
                     ▼
              WASM compilation
                     │
                     ▼
              frontend build
                     │
                     ▼
              integration tests
                     │
                     ▼
                Docker build
```

If static hosting is chosen, deployment can happen directly from the generated `dist/` directory.

Add proper automated release versioning for GitHub as well. Configure something like commitizen for this.

---

# 21. Performance benchmarking

Benchmark before and after the migration.

Measure:

### Solver

```text
native Rust solver
WASM solver
```

### Application

```text
current HTTP request
WASM invocation
```

### Browser

Measure:

- WASM download size
- WASM initialization time
- solve execution time
- UI responsiveness

Do not optimize prematurely.

The main expected improvement is architectural simplicity and removal of the HTTP/Python/PyO3 path, rather than necessarily a dramatic improvement in the solver algorithm itself.

---

# 22. Security considerations

Because the application becomes client-side:

- There are no server secrets to protect.
- There is no solver API to expose.
- User input stays in the browser.
- There is no backend attack surface for solver requests.

However, still validate inputs in Rust.

The browser is untrusted from the perspective of the Rust domain model even though the application is local.

# 23. Recommended commit sequence

Keep the migration incremental.

### Commit 1

```text
Add regression fixtures for current solver/API behaviour
```

### Commit 2

```text
Refactor Rust solver into standalone library API
```

### Commit 3

```text
Add domain types and validation
```

### Commit 4

```text
Convert Rust project to workspace
```

### Commit 5

```text
Add WASM adapter
```

### Commit 6

```text
Add WASM integration tests
```

### Commit 7

```text
Create React TypeScript frontend
```

### Commit 8

```text
Integrate Pickomino UI with WASM solver
```

### Commit 9

```text
Add browser integration tests
```

### Commit 10

```text
Remove FastAPI and PyO3 backend
```

### Commit 11

```text
Add production static build
```

### Commit 12

```text
Add single-container deployment
```

### Commit 13

```text
Update documentation for WASM architecture
```

This allows individual stages to be reviewed and tested independently.

---

# 25. Definition of done

The refactor is complete when all of the following are true:

- [ ] Rust solver is independent of Python and PyO3.
- [ ] Rust solver has a clean library API.
- [ ] Solver regression tests pass.
- [ ] WASM crate exposes a small stable API.
- [ ] WASM results match native Rust results.
- [ ] React + TypeScript frontend replaces the old frontend.
- [ ] React does not contain duplicated game/solver logic.
- [ ] Browser calls Rust/WASM directly.
- [ ] No `/api/run` HTTP request is required.
- [ ] FastAPI is removed.
- [ ] Python dependencies are removed.
- [ ] PyO3 is removed.
- [ ] Production build produces static React + WASM assets.
- [ ] Application works when served by a simple static web server.
- [ ] Docker can package the complete application into one image.
- [ ] No development toolchain is required in the production image.
- [x] CI runs Rust, WASM, frontend, and production-container builds.
- [x] A repeatable native solver benchmark is available.
- [x] Conventional commits and GitHub release automation are configured for changes merged into `main`.

Intentionally omitted:

- Browser end-to-end tests. The requested scope excludes them; Rust, WASM/build, TypeScript, and frontend test-command checks remain automated.
- [ ] README documents the new architecture and development workflow.

Completed in this implementation:

- [x] Rust solver is independent of Python and PyO3.
- [x] Rust workspace contains a pure solver crate and thin WASM adapter.
- [x] React + TypeScript frontend calls WASM directly without `/api/run`.
- [x] Native solver tests and production TypeScript/WASM build pass.
- [x] Single-container static deployment is configured.

### Implementation notes

- The public request preserves the existing API shape: `dice_throw` is nullable because it represents whether a throw is currently pending.
- The first implementation uses direct WASM calls from React. A Web Worker remains optional and should be added only if browser profiling shows main-thread blocking.
- The migration is delivered incrementally on `refactor/to-rust-wasm-ts`; Git commits and pushes are available when explicitly requested.

---

# 26. Final target

The preferred end state is:

```text
                       PICKOMINO
                           │
              ┌────────────┴────────────┐
              │                         │
         React / TS                 Rust core
              │                         │
              │                    game + solver
              │                         │
              └──────────┬──────────────┘
                         │
                     WASM adapter
                         │
                         ▼
                    Browser runtime
```

For deployment:

```text
Option 1:

Static hosting
└── React + WASM


Option 2:

Single Docker image
└── static web server
      ├── React
      └── WASM
```

There is no need for a Rust HTTP server unless a future requirement introduces server-side functionality.

The key architectural decision is therefore:

> **Make the Rust solver the platform-independent core, expose it to React through a very thin WASM adapter, and keep deployment entirely static.**

This gives Pickomino the smallest and cleanest architecture while preserving the option to add a native CLI, HTTP server, or other frontend later without rewriting the solver.
