# Взято из https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile
# Use a Python image with uv pre-installed
FROM astral/uv:python3.14-bookworm-slim

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Install the project into `/application`
WORKDIR /application

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
# Bind mount to ingestion/ subdirectory so .venv is created in /application/ingestion/.venv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=ingestion/uv.lock,target=ingestion/uv.lock \
    --mount=type=bind,source=ingestion/pyproject.toml,target=ingestion/pyproject.toml \
    uv sync --locked --no-install-project --directory ingestion

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY ./ingestion /application/ingestion
COPY ./shared /application/shared
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --directory ingestion

# Place executables in the environment at the front of the path
ENV PATH="/application/ingestion/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Use the non-root user to run our application
USER nonroot

# Set working directory for the worker
WORKDIR /application/ingestion

# Run the ingestion worker by default
CMD ["uv", "run", "taskiq", "worker", "tasks:broker"]
