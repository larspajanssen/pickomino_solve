# Use official Python image
FROM python:3.12-slim

# Install uv directly from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy lock files first
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: Sync exactly from uv.lock
# --no-install-project: Don't install the package itself yet, just dependencies
RUN uv sync --frozen --no-install-project

# Copy the rest of the code
COPY . .

# Install the project itself
RUN uv sync --frozen

# Expose port
EXPOSE 6000

# Start FastAPI app using 'uv run' to ensure we use the virtual environment
CMD ["uv", "run", "uvicorn", "pickomino_solver.main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "6000"]
