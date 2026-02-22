# Use official uv image with Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a container
ENV UV_LINK_MODE=copy

# Install dependencies first for better caching
# --frozen: Sync exactly from uv.lock
# --no-install-project: Don't install the project itself yet, just dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the code
COPY . .

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Expose port
EXPOSE 6000

# Start FastAPI app using 'uv run' to ensure we use the virtual environment
CMD ["uv", "run", "uvicorn", "pickomino_solver.main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "6000"]
