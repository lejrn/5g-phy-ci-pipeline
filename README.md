# 5G-PHY-CI-Pipeline

[![CI Pipeline](https://github.com/lejrn/5g-phy-ci-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/lejrn/5g-phy-ci-pipeline/actions/workflows/ci.yml)

A test pipeline for radio signal code. A Python script simulates OFDM and LDPC/Turbo coding, PyTest checks the error rate, Robot Framework turns test logs into a clean HTML report. All of this runs automatically in CI and pushes results as build artifacts.

## Project in One Sentence
Create a tiny Python program that simulates a 5G radio link, wrap it with PyTest + Robot Framework for automatic checks and shiny reports, and let GitHub Actions build & test it on every push.

## High-Level System Design

```
Developer Laptop ──▶ GitHub repo
│
▼
GitHub Actions Workflow
┌────────────────┬────────────────┐
│ Step 1: Build  │ Step 2: Run    │
│ Docker image   │ PyTest suite   │
├────────────────┼────────────────┤
│ Step 3: Run    │ Step 4: Upload │
│ Robot report   │ HTML artifact  │
└────────────────┴────────────────┘
```

## Components

- **Radio-sim module** (`radio_sim/`) – Python functions that generate OFDM symbols, add noise, decode, and return bit-error-rate (BER).
- **Tests** (`tests/`) – PyTest cases that assert BER ≤ 1e-5 for several SNR points.
- **Robot suite** (`robot/`) – Calls the CLI entry-point, checks exit code, and logs results in plain English.
- **Docker image** – Runs the whole pipeline the same way on every machine.
- **GitHub Actions** – YAML workflow that builds → tests → publishes report.html.

## Quick Start

### Prerequisites
- Python 3.10+
- Poetry

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd 5g-phy-ci-pipeline

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

### Run Tests
```bash
# Run unit tests
poetry run pytest

# Run simulation
poetry run radio-sim

# Generate Robot Framework report
poetry run robot robot/
```

### Docker
```bash
# Quick Docker setup (installs Docker if needed)
./get-docker.sh

# Build image
docker build -t 5g-phy-ci .

# Run tests in container
docker run --rm 5g-phy-ci

# Use comprehensive run script
./run.sh                    # Interactive menu
./run.sh docker-test        # Run Docker tests
./run.sh robot              # Generate Robot reports
./run.sh demo               # Visual BER demo
```

### Visual Demo
```bash
# Run interactive BER visualization
poetry run python visual_test_demo.py
# Opens matplotlib plots showing BER curves and constellation diagrams
```

## Development Roadmap

- [x] Session 1: Hello OFDM - Basic OFDM simulation
- [x] Session 2: Baseline BER - Add AWGN noise and BER calculation
- [x] Session 3: Unit Tests - PyTest test suite
- [x] Session 4: Docker - Containerization with multi-stage build
- [x] Session 5: CI - GitHub Actions workflow with comprehensive validation
- [x] Session 6: Robot Report - Robot Framework integration with HTML reports
- [x] Session 7: Polish - Documentation, utility scripts, and final touches

### Implementation Highlights

- **Complete OFDM Implementation**: QPSK/16-QAM modulation, AWGN channel, BER calculation
- **Comprehensive Testing**: 23 PyTest unit tests with 95%+ code coverage
- **Robot Framework Integration**: End-to-end testing with beautiful HTML reports
- **Docker Containerization**: Multi-stage builds for development and production
- **Full CI/CD Pipeline**: GitHub Actions with parallel test execution, coverage reporting
- **Utility Scripts**: Easy setup (`get-docker.sh`), execution (`run.sh`), and demo (`visual_test_demo.py`)
- **Performance Validation**: Automated BER threshold checking and performance reporting

## GitHub Actions CI/CD Workflow Guide

The project uses a comprehensive GitHub Actions workflow (`.github/workflows/ci.yml`) that demonstrates production-ready CI/CD practices. This section explains the workflow structure and syntax to help you understand and customize the pipeline.

### Workflow Overview

The CI pipeline consists of **4 parallel jobs** with smart dependencies:

```
test (foundation job)
├── docker (containerization testing)
├── robot (end-to-end testing)  
└── performance (BER validation)
```

### Workflow Structure & Syntax

#### 1. **Workflow Metadata**
```yaml
name: 5G PHY CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.11'
```

- **`name`**: Workflow display name in GitHub Actions tab
- **`on`**: **Triggers** - runs on pushes to `main`/`develop` or PRs to `main`
- **`env`**: Global environment variables accessible via `${{ env.PYTHON_VERSION }}`

#### 2. **Job Dependencies & Parallelization**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    # No dependencies - runs first
    
  docker:
    runs-on: ubuntu-latest
    needs: test              # Waits for test job success
    
  robot:
    needs: test              # Runs in parallel with docker/performance
    
  performance:
    needs: test
```

The `needs:` keyword creates dependencies, optimizing build time while ensuring quality gates.

#### 3. **Common Step Patterns**

**Setup Pattern** (repeated across jobs):
```yaml
steps:
- name: Checkout code
  uses: actions/checkout@v4
  
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    
- name: Install Poetry
  uses: snok/install-poetry@v1
  with:
    version: latest
    virtualenvs-create: true
    virtualenvs-in-project: true
```

**Actions vs Commands**:
- **`uses:`** - Pre-built GitHub Actions from marketplace
- **`run:`** - Shell commands executed in the runner

#### 4. **Advanced Features**

**Caching for Speed**:
```yaml
- name: Load cached venv
  id: cached-poetry-dependencies
  uses: actions/cache@v3
  with:
    path: .venv
    key: venv-${{ runner.os }}-${{ steps.setup-python.outputs.python-version }}-${{ hashFiles('**/poetry.lock') }}

- name: Install dependencies
  if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
  run: poetry install --no-interaction --no-root
```

- **Cache key** includes OS, Python version, and dependency hash
- **Conditional execution** with `if:` saves time when cache hits

**Artifact Collection**:
```yaml
- name: Upload test coverage artifacts
  uses: actions/upload-artifact@v4
  if: always()                    # Runs even if previous steps failed
  with:
    name: coverage-report
    path: htmlcov/
```

#### 5. **Job-by-Job Breakdown**

**`test` Job - Foundation**:
- Code quality: linting (flake8), type checking (mypy)
- Unit testing with coverage reporting
- Test simulation execution
- Codecov integration for coverage tracking

**`docker` Job - Containerization**:
- Docker image building and testing
- **Key Fix**: Uses `--entrypoint=""` to bypass container entrypoint for pytest
- Validates containerized simulation execution

**`robot` Job - End-to-End Testing**:
- Robot Framework acceptance tests
- Docker image building for Robot tests that need containers
- HTML report generation and artifact upload

**`performance` Job - Validation**:
- Automated BER threshold checking (fails if BER > 1e-6 at high SNR)
- Multi-modulation performance comparison (QPSK vs 16-QAM)
- JSON performance report generation

#### 6. **Docker Integration Gotchas**

The Dockerfile uses an `ENTRYPOINT` that can cause issues:
```dockerfile
ENTRYPOINT ["poetry", "run", "python", "-m", "radio_sim"]
```

**Problem**: Running `docker run image pytest` becomes `radio_sim pytest` (invalid)

**Solution**: Override entrypoint for tests:
```yaml
# For running tests inside container
docker run --rm --entrypoint="" 5g-phy-ci:latest poetry run pytest -v

# For running simulation (uses entrypoint)
docker run --rm 5g-phy-ci:latest --bits 1000 --snr-start 15 --snr-stop 20
```

#### 7. **Best Practices Demonstrated**

1. **Parallel Execution**: Jobs run simultaneously where possible
2. **Smart Dependencies**: `needs:` prevents resource waste
3. **Comprehensive Caching**: Speeds up repeated builds
4. **Artifact Preservation**: Test results, coverage, and reports saved
5. **Conditional Steps**: `if: always()` ensures cleanup even on failure
6. **Version Pinning**: `@v4` for reliable action versions
7. **Environment Consistency**: Same Python version across all jobs

### Customizing the Workflow

To modify the pipeline for your project:

1. **Change Python version**: Update `PYTHON_VERSION` environment variable
2. **Add new jobs**: Follow the same pattern with appropriate `needs:` dependencies
3. **Modify triggers**: Adjust `on:` section for different branch strategies
4. **Add integrations**: Include services like Slack notifications, deployment steps
5. **Customize artifacts**: Modify `upload-artifact` steps for your specific outputs

This workflow demonstrates enterprise-grade CI/CD practices suitable for production environments, with comprehensive testing, containerization, and automated quality gates.

## License
