"""
Unit tests for OFDM simulation.

Tests the OFDM simulator with different configurations and verifies:
- BER performance at various SNR levels
- Modulation/demodulation correctness
- OFDM symbol generation
"""

import pytest
import numpy as np
from radio_sim.ofdm import OFDMSimulator


class TestOFDMSimulator:
    """Test cases for OFDM simulator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.simulator_qpsk = OFDMSimulator(modulation="QPSK", seed=42)
        self.simulator_16qam = OFDMSimulator(modulation="16QAM", seed=42)
    
    def test_initialization(self):
        """Test simulator initialization."""
        # Test QPSK
        assert self.simulator_qpsk.modulation == "QPSK"
        assert self.simulator_qpsk.bits_per_symbol == 2
        assert len(self.simulator_qpsk.constellation) == 4
        
        # Test 16-QAM
        assert self.simulator_16qam.modulation == "16QAM"
        assert self.simulator_16qam.bits_per_symbol == 4
        assert len(self.simulator_16qam.constellation) == 16
    
    def test_bit_generation(self):
        """Test random bit generation."""
        bits = self.simulator_qpsk.generate_bits(100)
        
        assert len(bits) == 100
        assert bits.dtype == np.uint8
        assert np.all((bits == 0) | (bits == 1))
    
    def test_qpsk_modulation(self):
        """Test QPSK modulation."""
        # Test known bit patterns
        bits = np.array([0, 0, 0, 1, 1, 0, 1, 1], dtype=np.uint8)
        symbols = self.simulator_qpsk.modulate(bits)
        
        assert len(symbols) == 4  # 8 bits / 2 bits per symbol
        assert symbols.dtype == np.complex128
        
        # Check that symbols are from QPSK constellation
        for symbol in symbols:
            distances = np.abs(symbol - self.simulator_qpsk.constellation)
            assert np.min(distances) < 1e-10
    
    def test_16qam_modulation(self):
        """Test 16-QAM modulation."""
        bits = np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=np.uint8)
        symbols = self.simulator_16qam.modulate(bits)
        
        assert len(symbols) == 2  # 8 bits / 4 bits per symbol
        assert symbols.dtype == np.complex128
        
        # Check that symbols are from 16-QAM constellation
        for symbol in symbols:
            distances = np.abs(symbol - self.simulator_16qam.constellation)
            assert np.min(distances) < 1e-10
    
    def test_ofdm_symbol_generation(self):
        """Test OFDM symbol generation."""
        # Generate some test symbols
        bits = self.simulator_qpsk.generate_bits(128)  # 64 QPSK symbols
        symbols = self.simulator_qpsk.modulate(bits)
        
        # Generate OFDM symbol
        ofdm_symbol = self.simulator_qpsk.generate_ofdm_symbol(symbols)
        
        assert len(ofdm_symbol) == self.simulator_qpsk.n_subcarriers
        assert ofdm_symbol.dtype == np.complex128
    
    def test_awgn_channel(self):
        """Test AWGN channel."""
        # Create a simple signal
        signal = np.ones(100, dtype=complex)
        
        # Add noise
        noisy_signal = self.simulator_qpsk.add_awgn(signal, snr_db=10)
        
        assert len(noisy_signal) == len(signal)
        assert noisy_signal.dtype == np.complex128
        
        # Check that noise was added (signals should be different)
        assert not np.allclose(signal, noisy_signal)
    
    def test_ofdm_demodulation(self):
        """Test OFDM demodulation (should be inverse of modulation)."""
        # Generate test symbols
        bits = self.simulator_qpsk.generate_bits(128)
        symbols = self.simulator_qpsk.modulate(bits)
        
        # OFDM modulation and demodulation
        ofdm_symbol = self.simulator_qpsk.generate_ofdm_symbol(symbols)
        demod_symbols = self.simulator_qpsk.demodulate_ofdm(ofdm_symbol)
        
        # Should recover original symbols (within numerical precision)
        np.testing.assert_allclose(
            symbols, 
            demod_symbols[:len(symbols)], 
            rtol=1e-10
        )
    
    def test_symbol_demodulation(self):
        """Test symbol demodulation."""
        # Test with perfect symbols (no noise)
        bits = np.array([0, 0, 0, 1, 1, 0, 1, 1], dtype=np.uint8)
        symbols = self.simulator_qpsk.modulate(bits)
        demod_bits = self.simulator_qpsk.demodulate_symbols(symbols)
        
        np.testing.assert_array_equal(bits, demod_bits)
    
    def test_ber_calculation(self):
        """Test BER calculation."""
        tx_bits = np.array([0, 1, 0, 1, 0], dtype=np.uint8)
        rx_bits = np.array([0, 0, 0, 1, 1], dtype=np.uint8)  # 2 errors out of 5
        
        ber = self.simulator_qpsk.calculate_ber(tx_bits, rx_bits)
        assert ber == 0.4  # 2/5 = 0.4


class TestBERPerformance:
    """Test BER performance at specific SNR levels."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.simulator = OFDMSimulator(modulation="QPSK", seed=42)
        self.n_bits = 50000  # Use more bits for reliable BER estimation
    
    def test_high_snr_ber_qpsk(self):
        """Test that BER is low at high SNR for QPSK."""
        snr_db = 20
        ber, _ = self.simulator.simulate_transmission(self.n_bits, snr_db)
        
        # At 20 dB SNR, QPSK should have very low BER
        assert ber < 1e-4, f"BER too high at {snr_db} dB SNR: {ber}"
    
    def test_medium_snr_ber_qpsk(self):
        """Test BER at medium SNR for QPSK."""
        snr_db = 10
        ber, _ = self.simulator.simulate_transmission(self.n_bits, snr_db)
        
        # At 10 dB SNR, QPSK should have reasonable BER
        assert ber < 1e-2, f"BER too high at {snr_db} dB SNR: {ber}"
    
    def test_low_snr_ber_qpsk(self):
        """Test BER at low SNR for QPSK."""
        snr_db = 0
        ber, _ = self.simulator.simulate_transmission(self.n_bits, snr_db)
        
        # At 0 dB SNR, BER should be high but not 0.5 (random)
        assert 0.01 < ber < 0.4, f"Unexpected BER at {snr_db} dB SNR: {ber}"
    
    @pytest.mark.parametrize("snr_db", [15, 18, 20])
    def test_ber_threshold_compliance(self, snr_db):
        """Test that BER meets threshold at high SNR (CI compliance test)."""
        ber, _ = self.simulator.simulate_transmission(self.n_bits, snr_db)
        
        # This is the key test for CI - BER should be ≤ 1e-5 at high SNR
        assert ber <= 1e-5, f"BER threshold violation at {snr_db} dB: {ber} > 1e-5"


class TestSimulationIntegration:
    """Integration tests for complete simulation chain."""
    
    def test_qpsk_simulation_chain(self):
        """Test complete QPSK simulation."""
        simulator = OFDMSimulator(modulation="QPSK", seed=42)
        ber, sim_data = simulator.simulate_transmission(1000, snr_db=15)
        
        # Check that all data is present
        assert 'tx_bits' in sim_data
        assert 'rx_bits' in sim_data
        assert 'snr_db' in sim_data
        assert sim_data['snr_db'] == 15
        assert sim_data['modulation'] == "QPSK"
        
        # Check data types and shapes
        assert isinstance(ber, float)
        assert 0 <= ber <= 1
        assert len(sim_data['tx_bits']) >= 1000
        assert len(sim_data['rx_bits']) <= len(sim_data['tx_bits'])
    
    def test_16qam_simulation_chain(self):
        """Test complete 16-QAM simulation."""
        simulator = OFDMSimulator(modulation="16QAM", seed=42)
        ber, sim_data = simulator.simulate_transmission(1000, snr_db=20)
        
        # 16-QAM should work but have higher BER than QPSK at same SNR
        assert isinstance(ber, float)
        assert 0 <= ber <= 1
        assert sim_data['modulation'] == "16QAM"
    
    def test_reproducibility(self):
        """Test that simulation is reproducible with same seed."""
        sim1 = OFDMSimulator(modulation="QPSK", seed=42)
        sim2 = OFDMSimulator(modulation="QPSK", seed=42)
        
        ber1, _ = sim1.simulate_transmission(1000, snr_db=10)
        ber2, _ = sim2.simulate_transmission(1000, snr_db=10)
        
        assert ber1 == ber2, "Simulation should be reproducible with same seed"
    
    def test_different_seeds_different_results(self):
        """Test that different seeds give different results."""
        sim1 = OFDMSimulator(modulation="QPSK", seed=42)
        sim2 = OFDMSimulator(modulation="QPSK", seed=123)
        
        # Use lower SNR where there's more variability
        ber1, _ = sim1.simulate_transmission(1000, snr_db=5)
        ber2, _ = sim2.simulate_transmission(1000, snr_db=5)
        
        # Results should be different (very low probability of being exactly equal)
        assert ber1 != ber2, "Different seeds should give different results"


if __name__ == "__main__":
    pytest.main([__file__])
