# 5G-PHY-CI-Pipeline

[![CI Pipeline](https://github.com/yourusername/5g-phy-ci-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/5g-phy-ci-pipeline/actions/workflows/ci.yml)

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
# Build image
docker build -t 5g-phy-ci .

# Run tests in container
docker run --rm 5g-phy-ci
```

## Development Roadmap

- [x] Session 1: Hello OFDM - Basic OFDM simulation
- [x] Session 2: Baseline BER - Add AWGN noise and BER calculation
- [x] Session 3: Unit Tests - PyTest test suite
- [ ] Session 4: Docker - Containerization
- [ ] Session 5: CI - GitHub Actions workflow
- [ ] Session 6: Robot Report - Robot Framework integration
- [ ] Session 7: Polish - Documentation and final touches

## License

MIT License - see [LICENSE](LICENSE) file for details.
