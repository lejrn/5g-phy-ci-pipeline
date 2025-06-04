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

## License

MIT License - see [LICENSE](LICENSE) file for details.
