FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app/backend

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/root/.cargo/bin:${PATH}"

# Build tools are required because the Python package builds a Rust extension.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates curl \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y --profile minimal \
    && rm -rf /var/lib/apt/lists/*

# Install dependency set first to maximize layer cache reuse.
COPY backend/pyproject.toml backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy project sources and install the package.
COPY backend ./
COPY backend_rust /app/backend_rust
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

EXPOSE 6000

CMD ["uv", "run", "uvicorn", "pickomino_solver.main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "6000"]
