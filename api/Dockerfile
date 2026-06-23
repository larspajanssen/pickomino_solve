# Stage 1: Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app/api

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/root/.cargo/bin:${PATH}"

# Build tools are required because the Python package builds a Rust extension.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates curl \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y --profile minimal \
    && rm -rf /var/lib/apt/lists/*

# Install dependency set first to maximize layer cache reuse.
COPY api/pyproject.toml api/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy project sources and compile the package in non-editable mode.
COPY api ./
COPY solver /app/solver
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Stage 2: Runtime stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runner

WORKDIR /app/api

# Copy the built virtual environment
COPY --from=builder /app/api/.venv /app/api/.venv

# Add virtual environment binaries to the PATH
ENV PATH="/app/api/.venv/bin:${PATH}"

EXPOSE 6000

# Run uvicorn directly from the virtual environment
CMD ["uvicorn", "pickomino_solver.main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "6000"]
