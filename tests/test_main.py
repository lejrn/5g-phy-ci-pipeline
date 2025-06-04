"""
Integration tests for the main simulation entry point.
"""

import pytest
import subprocess
import sys
from radio_sim.main import run_simulation, main


class TestMainSimulation:
    """Test the main simulation function."""
    
    def test_run_simulation_qpsk(self):
        """Test running QPSK simulation."""
        results = run_simulation(
            modulation="QPSK",
            n_bits=1000,
            snr_range=(10, 15, 5),
            seed=42
        )
        
        assert 'snr_values' in results
        assert 'ber_values' in results
        assert 'modulation' in results
        assert results['modulation'] == "QPSK"
        assert len(results['snr_values']) == len(results['ber_values'])
    
    def test_run_simulation_16qam(self):
        """Test running 16-QAM simulation."""
        results = run_simulation(
            modulation="16QAM",
            n_bits=1000,
            snr_range=(15, 20, 5),
            seed=42
        )
        
        assert results['modulation'] == "16QAM"
        assert len(results['ber_values']) > 0
    
    def test_cli_interface(self):
        """Test CLI interface by running as subprocess."""
        # Test basic execution - use current working directory (Docker-compatible)
        result = subprocess.run([
            sys.executable, "-m", "radio_sim.main",
            "--bits", "1000",
            "--snr-start", "10",
            "--snr-stop", "15",
            "--snr-step", "5"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "Simulation completed successfully!" in result.stdout


class TestPerformanceRequirements:
    """Test that simulation meets performance requirements."""
    
    def test_ber_performance_requirements(self):
        """Test BER performance meets CI requirements."""
        # This is the key test for CI pipeline
        results = run_simulation(
            modulation="QPSK",
            n_bits=10000,
            snr_range=(15, 20, 1),
            seed=42
        )
        
        # All BER values at high SNR should be below threshold
        high_snr_indices = results['snr_values'] >= 15
        high_snr_bers = results['ber_values'][high_snr_indices]
        
        for i, ber in enumerate(high_snr_bers):
            snr = results['snr_values'][high_snr_indices][i]
            assert ber <= 1e-5, f"BER requirement violation: {ber} > 1e-5 at {snr} dB"


if __name__ == "__main__":
    pytest.main([__file__])
