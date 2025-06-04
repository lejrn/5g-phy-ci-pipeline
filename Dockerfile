# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry configuration
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create virtual environment (we're in container)
RUN poetry config virtualenvs.create false

# Install dependencies (without installing the project itself yet)
RUN poetry install --only=main,test,robot --no-root

# Copy source code
COPY radio_sim/ ./radio_sim/
COPY tests/ ./tests/
COPY robot/ ./robot/
COPY README.md .

# Install the project itself now that all files are present
RUN poetry install --only-root

# Set Python path
ENV PYTHONPATH=/app

# Set the entrypoint to use poetry run python -m radio_sim
ENTRYPOINT ["poetry", "run", "python", "-m", "radio_sim"]

# Default command shows help when no arguments provided
CMD ["--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD poetry run python -c "import radio_sim; print('OK')" || exit 1
