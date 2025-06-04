"""
Main entry point for the 5G PHY simulation.

Runs OFDM simulation and calculates BER for different SNR values.
"""

import numpy as np
import argparse
import sys
from radio_sim.ofdm import OFDMSimulator, plot_ber_curve


def run_simulation(modulation: str = "QPSK", 
                  n_bits: int = 10000,
                  snr_range: tuple = (0, 20, 2),
                  seed: int = 42) -> dict:
    """
    Run OFDM simulation across SNR range.
    
    Args:
        modulation: Modulation scheme
        n_bits: Number of bits to simulate
        snr_range: (start, stop, step) for SNR in dB
        seed: Random seed
        
    Returns:
        Dictionary with simulation results
    """
    print(f"5G PHY CI Pipeline - OFDM Simulation")
    print(f"Modulation: {modulation}")
    print(f"Bits per simulation: {n_bits}")
    print(f"SNR range: {snr_range[0]} to {snr_range[1]} dB (step: {snr_range[2]})")
    print("-" * 50)
    
    # Initialize simulator
    simulator = OFDMSimulator(modulation=modulation, seed=seed)
    
    # Generate SNR values
    snr_values = np.arange(snr_range[0], snr_range[1] + snr_range[2], snr_range[2])
    ber_values = []
    
    # Run simulation for each SNR
    for snr_db in snr_values:
        ber, sim_data = simulator.simulate_transmission(n_bits, snr_db)
        ber_values.append(ber)
        
        print(f"SNR: {snr_db:2d} dB, BER: {ber:.2e}")
        
        # Check if BER is acceptable (for CI testing)
        if snr_db >= 15 and ber > 1e-5:
            print(f"WARNING: High BER ({ber:.2e}) at SNR {snr_db} dB")
    
    ber_array = np.array(ber_values)
    
    # Summary
    print("-" * 50)
    print(f"Simulation completed successfully!")
    print(f"Best BER: {np.min(ber_array):.2e} at {snr_values[np.argmin(ber_array)]} dB")
    
    return {
        'snr_values': snr_values,
        'ber_values': ber_array,
        'modulation': modulation,
        'n_bits': n_bits,
        'seed': seed
    }


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="5G PHY OFDM Simulation Pipeline"
    )
    
    parser.add_argument(
        '--modulation', '-m',
        choices=['QPSK', '16QAM'],
        default='QPSK',
        help='Modulation scheme (default: QPSK)'
    )
    
    parser.add_argument(
        '--bits', '-b',
        type=int,
        default=10000,
        help='Number of bits to simulate (default: 10000)'
    )
    
    parser.add_argument(
        '--snr-start',
        type=int,
        default=0,
        help='Starting SNR in dB (default: 0)'
    )
    
    parser.add_argument(
        '--snr-stop',
        type=int,
        default=20,
        help='Ending SNR in dB (default: 20)'
    )
    
    parser.add_argument(
        '--snr-step',
        type=int,
        default=2,
        help='SNR step in dB (default: 2)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Show BER curve plot'
    )
    
    args = parser.parse_args()
    
    try:
        # Run simulation
        results = run_simulation(
            modulation=args.modulation,
            n_bits=args.bits,
            snr_range=(args.snr_start, args.snr_stop, args.snr_step),
            seed=args.seed
        )
        
        # Plot if requested
        if args.plot:
            plot_ber_curve(
                results['snr_values'], 
                results['ber_values'],
                results['modulation']
            )
        
        # Return 0 for success (important for CI)
        return 0
        
    except Exception as e:
        print(f"ERROR: Simulation failed - {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
