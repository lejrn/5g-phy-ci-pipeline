#!/bin/bash
# Development helper script for 5G PHY CI Pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    echo "5G PHY CI Pipeline - Development Helper"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup       - Set up development environment"
    echo "  test        - Run all tests"
    echo "  test-fast   - Run fast tests only"
    echo "  sim         - Run simulation"
    echo "  robot       - Run Robot Framework tests"
    echo "  docker      - Build and test Docker image"
    echo "  lint        - Run linting and type checking"
    echo "  clean       - Clean build artifacts"
    echo "  help        - Show this help"
    echo ""
}

# Setup development environment
setup_env() {
    print_status "Setting up development environment..."
    
    # Check if Poetry is installed
    if ! command -v poetry &> /dev/null; then
        print_error "Poetry is not installed. Please install Poetry first."
        echo "Visit: https://python-poetry.org/docs/#installation"
        exit 1
    fi
    
    # Install dependencies
    print_status "Installing dependencies with Poetry..."
    poetry install
    
    print_status "Setup complete! You can now run: poetry shell"
}

# Run tests
run_tests() {
    print_status "Running all tests..."
    poetry run pytest tests/ -v --tb=short
}

# Run fast tests
run_fast_tests() {
    print_status "Running fast tests..."
    poetry run pytest tests/ -v --tb=short -m "not slow"
}

# Run simulation
run_simulation() {
    print_status "Running OFDM simulation..."
    poetry run radio-sim --bits 5000 --snr-start 10 --snr-stop 20 --snr-step 2
}

# Run Robot Framework tests
run_robot() {
    print_status "Running Robot Framework tests..."
    mkdir -p robot/results
    poetry run robot --outputdir robot/results robot/
    print_status "Robot results available in robot/results/"
}

# Docker build and test
run_docker() {
    print_status "Building Docker image..."
    docker build -t 5g-phy-ci:latest .
    
    print_status "Testing Docker image..."
    docker run --rm 5g-phy-ci:latest
    
    print_status "Running simulation in Docker..."
    docker run --rm 5g-phy-ci:latest poetry run radio-sim --bits 1000 --snr-start 15 --snr-stop 20
}

# Run linting
run_lint() {
    print_status "Running linting and type checking..."
    
    print_status "Running flake8..."
    poetry run flake8 radio_sim tests --count --select=E9,F63,F7,F82 --show-source --statistics
    poetry run flake8 radio_sim tests --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    print_status "Running mypy..."
    poetry run mypy radio_sim --ignore-missing-imports
    
    print_status "Running black (check only)..."
    poetry run black --check radio_sim tests
}

# Clean build artifacts
clean_artifacts() {
    print_status "Cleaning build artifacts..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # Remove test artifacts
    rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml
    
    # Remove Robot artifacts
    rm -rf robot/results/ robot/log.html robot/output.xml robot/report.html
    
    # Remove build artifacts
    rm -rf build/ dist/ *.egg-info/
    
    print_status "Clean complete!"
}

# Main script logic
case "${1:-help}" in
    setup)
        setup_env
        ;;
    test)
        run_tests
        ;;
    test-fast)
        run_fast_tests
        ;;
    sim)
        run_simulation
        ;;
    robot)
        run_robot
        ;;
    docker)
        run_docker
        ;;
    lint)
        run_lint
        ;;
    clean)
        clean_artifacts
        ;;
    help|*)
        show_help
        ;;
esac
