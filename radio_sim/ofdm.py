"""
OFDM simulation module.

Implements basic OFDM transmission chain:
1. Bit generation
2. QPSK/16-QAM modulation
3. IFFT (OFDM symbol generation)
4. AWGN channel
5. FFT (OFDM demodulation)
6. Demodulation and BER calculation
"""

import numpy as np
from typing import Tuple, Union
import matplotlib.pyplot as plt
from numpy.typing import NDArray


class OFDMSimulator:
    """
    OFDM simulator for 5G PHY testing.
    
    Simulates a simple OFDM transmission with configurable parameters:
    - Number of subcarriers
    - Modulation scheme (QPSK, 16-QAM)
    - SNR levels
    """
    
    def __init__(self, 
                 n_subcarriers: int = 64,
                 modulation: str = "QPSK",
                 seed: int = 42):
        """
        Initialize OFDM simulator.
        
        Args:
            n_subcarriers: Number of OFDM subcarriers
            modulation: Modulation scheme ("QPSK" or "16QAM")
            seed: Random seed for reproducible results
        """
        self.n_subcarriers = n_subcarriers
        self.modulation = modulation
        self.rng = np.random.default_rng(seed)
        
        # Modulation constellation points
        if modulation == "QPSK":
            self.constellation = np.array([1+1j, -1+1j, -1-1j, 1-1j]) / np.sqrt(2)
            self.bits_per_symbol = 2
        elif modulation == "16QAM":
            # 16-QAM constellation (Gray coded)
            self.constellation = np.array([
                -3-3j, -3-1j, -3+3j, -3+1j,
                -1-3j, -1-1j, -1+3j, -1+1j,
                 3-3j,  3-1j,  3+3j,  3+1j,
                 1-3j,  1-1j,  1+3j,  1+1j
            ]) / np.sqrt(10)
            self.bits_per_symbol = 4
        else:
            raise ValueError(f"Unsupported modulation: {modulation}")
    
    def generate_bits(self, n_bits: int) -> np.ndarray:
        """Generate random bits."""
        return self.rng.integers(0, 2, size=n_bits, dtype=np.uint8)
    
    def modulate(self, bits: np.ndarray) -> NDArray[np.complex128]:
        """
        Modulate bits to constellation symbols.
        
        Args:
            bits: Input bits array
            
        Returns:
            Complex symbols array
        """
        # Reshape bits into groups
        n_symbols = len(bits) // self.bits_per_symbol
        bit_groups = bits[:n_symbols * self.bits_per_symbol].reshape(-1, self.bits_per_symbol)
        
        # Convert bit groups to constellation indices (MSB first ordering)
        indices = np.sum(bit_groups * (2 ** np.arange(self.bits_per_symbol - 1, -1, -1)), axis=1)
        
        return self.constellation[indices].astype(np.complex128)
    
    def generate_ofdm_symbol(self, data_symbols: np.ndarray) -> np.ndarray:
        """
        Generate OFDM symbol using IFFT.
        
        Args:
            data_symbols: Modulated data symbols
            
        Returns:
            Time-domain OFDM symbol
        """
        # Pad or truncate to match number of subcarriers
        if len(data_symbols) > self.n_subcarriers:
            data_symbols = data_symbols[:self.n_subcarriers]
        elif len(data_symbols) < self.n_subcarriers:
            # Zero-pad in frequency domain
            padding = np.zeros(self.n_subcarriers - len(data_symbols), dtype=complex)
            data_symbols = np.concatenate([data_symbols, padding])
        
        # IFFT to convert to time domain
        time_signal = np.fft.ifft(data_symbols) * np.sqrt(self.n_subcarriers)
        
        return time_signal.astype(np.complex128)
    
    def add_awgn(self, signal: np.ndarray, snr_db: float) -> np.ndarray:
        """
        Add Additive White Gaussian Noise (AWGN) to signal.
        
        Args:
            signal: Input signal
            snr_db: Signal-to-noise ratio in dB
            
        Returns:
            Noisy signal
        """
        # Calculate signal power
        signal_power = np.mean(np.abs(signal) ** 2)
        
        # Calculate noise power from SNR
        snr_linear = 10 ** (snr_db / 10)
        noise_power = signal_power / snr_linear
        
        # Generate complex AWGN
        noise_real = self.rng.normal(0, np.sqrt(noise_power/2), len(signal))
        noise_imag = self.rng.normal(0, np.sqrt(noise_power/2), len(signal))
        noise = noise_real + 1j * noise_imag
        
        return signal + noise
    
    def demodulate_ofdm(self, received_signal: np.ndarray) -> np.ndarray:
        """
        Demodulate OFDM symbol using FFT.
        
        Args:
            received_signal: Received time-domain signal
            
        Returns:
            Frequency-domain symbols
        """
        return (np.fft.fft(received_signal) / np.sqrt(self.n_subcarriers)).astype(np.complex128)
    
    def demodulate_symbols(self, symbols: np.ndarray) -> np.ndarray:
        """
        Demodulate constellation symbols to bits.
        
        Args:
            symbols: Received symbols
            
        Returns:
            Demodulated bits
        """
        # Hard decision demodulation - find closest constellation point
        distances = np.abs(symbols[:, np.newaxis] - self.constellation[np.newaxis, :])
        indices = np.argmin(distances, axis=1)
        
        # Convert indices back to bits
        bits = []
        for idx in indices:
            bit_pattern = format(idx, f'0{self.bits_per_symbol}b')
            bits.extend([int(b) for b in bit_pattern])
        
        return np.array(bits, dtype=np.uint8)
    
    def calculate_ber(self, tx_bits: np.ndarray, rx_bits: np.ndarray) -> float:
        """
        Calculate Bit Error Rate (BER).
        
        Args:
            tx_bits: Transmitted bits
            rx_bits: Received bits
            
        Returns:
            BER value
        """
        # Ensure same length
        min_len = min(len(tx_bits), len(rx_bits))
        tx_bits = tx_bits[:min_len]
        rx_bits = rx_bits[:min_len]
        
        # Count errors
        errors = np.sum(tx_bits != rx_bits)
        ber = float(errors / min_len)
        
        return ber
    
    def simulate_transmission(self, n_bits: int, snr_db: float) -> Tuple[float, dict]:
        """
        Simulate complete OFDM transmission.
        
        Args:
            n_bits: Number of bits to transmit
            snr_db: SNR in dB
            
        Returns:
            Tuple of (BER, simulation_data)
        """
        # Generate and modulate data
        tx_bits = self.generate_bits(n_bits)
        tx_symbols = self.modulate(tx_bits)
        
        # Generate OFDM symbol
        ofdm_symbol = self.generate_ofdm_symbol(tx_symbols)
        
        # Add AWGN
        rx_signal = self.add_awgn(ofdm_symbol, snr_db)
        
        # Demodulate
        rx_symbols = self.demodulate_ofdm(rx_signal)
        rx_bits = self.demodulate_symbols(rx_symbols[:len(tx_symbols)])
        
        # Calculate BER
        ber = self.calculate_ber(tx_bits, rx_bits)
        
        # Return results with simulation data
        sim_data = {
            'tx_bits': tx_bits,
            'tx_symbols': tx_symbols,
            'ofdm_symbol': ofdm_symbol,
            'rx_signal': rx_signal,
            'rx_symbols': rx_symbols,
            'rx_bits': rx_bits,
            'snr_db': snr_db,
            'n_bits': n_bits,
            'modulation': self.modulation
        }
        
        return ber, sim_data


def plot_constellation(symbols: np.ndarray, title: str = "Constellation") -> None:
    """Plot constellation diagram."""
    plt.figure(figsize=(8, 6))
    plt.scatter(symbols.real, symbols.imag, alpha=0.7)
    plt.grid(True)
    plt.xlabel('In-phase')
    plt.ylabel('Quadrature')
    plt.title(title)
    plt.axis('equal')
    plt.show()


def plot_ber_curve(snr_range: np.ndarray, ber_values: np.ndarray, 
                  modulation: str = "QPSK") -> None:
    """Plot BER vs SNR curve."""
    plt.figure(figsize=(10, 6))
    plt.semilogy(snr_range, ber_values, 'o-', label=f'{modulation} Simulation')
    
    # Add quality thresholds
    plt.axhline(y=1e-5, color='green', linestyle='--', alpha=0.7, label='5G Target (1e-5)')
    plt.axhline(y=1e-3, color='orange', linestyle='--', alpha=0.7, label='Voice Quality (1e-3)')
    
    plt.grid(True)
    plt.xlabel('SNR (dB)')
    plt.ylabel('Bit Error Rate (BER)')
    plt.title(f'BER vs SNR for {modulation} OFDM')
    plt.legend()
    
    # Save plot to file
    filename = f'ber_curve_{modulation.lower()}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"📊 BER curve saved as '{filename}'")
    plt.show()
