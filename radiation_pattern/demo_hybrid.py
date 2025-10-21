"""
Simple demo script to visualize radiation patterns using the hybrid Python/C implementation.
Run this script directly to see the comparison plot.
Usage: python demo.py [cartesian|polar]
"""
import sys
import os
import argparse

# Add the parent directory to Python path to find the radiation_pattern package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for interactive plots
import matplotlib.pyplot as plt
from linear_array_hybrid import ArrayParameters, calculate_pattern

def plot_cartesian(n_elements_list, theta, patterns, patterns_db, steering_angle=0, snr_db=None, phase_error_std=None):
    """Create comparison plot in Cartesian coordinates."""
    fig = plt.figure(figsize=(20, 8))
    title = 'Radiation Pattern Comparison for Different Array Sizes (Hybrid C/Python)\n' \
            f'Element Spacing: 0.5λ, Steering Angle: {steering_angle}°'
    if snr_db is not None:
        title += f'\nSNR: {snr_db} dB'
    if phase_error_std is not None:
        title += f'\nPhase Error σ: {phase_error_std}°'
    fig.suptitle(title, fontsize=16)
    
    gs = plt.GridSpec(2, len(n_elements_list), figure=fig)
    
    for idx, (n, pattern, pattern_db) in enumerate(zip(n_elements_list, patterns, patterns_db)):
        # Linear scale plot
        ax1 = fig.add_subplot(gs[0, idx])
        pattern_abs = np.abs(pattern)
        max_val = np.max(pattern_abs)
        ax1.plot(theta, pattern_abs / max_val)  # Normalize to max value
        ax1.set_title(f'N = {n}')
        ax1.grid(True)
        if idx == 0:
            ax1.set_ylabel('Normalized Magnitude')
        ax1.set_xlim(-180, 180)
        ax1.set_ylim(0, 1.1)  # Normalized scale with small margin
        
        # dB scale plot
        ax2 = fig.add_subplot(gs[1, idx])
        ax2.plot(theta, pattern_db)
        ax2.grid(True)
        if idx == 0:
            ax2.set_ylabel('Magnitude (dB)')
        ax2.set_xlabel('Angle (degrees)')
        ax2.set_xlim(-180, 180)
        ax2.set_ylim(-60, 0)  # Extend range to -60 dB
    
    plt.tight_layout()

def plot_polar(n_elements_list, theta, patterns, patterns_db, steering_angle=0, snr_db=None, phase_error_std=None):
    """Create comparison plot in polar coordinates."""
    fig = plt.figure(figsize=(20, 10))
    title = 'Radiation Pattern Comparison for Different Array Sizes (Hybrid C/Python)\n' \
            f'Element Spacing: 0.5λ, Steering Angle: {steering_angle}°'
    if snr_db is not None:
        title += f'\nSNR: {snr_db} dB'
    if phase_error_std is not None:
        title += f'\nPhase Error σ: {phase_error_std}°'
    fig.suptitle(title, fontsize=16)
    
    # Convert theta to radians for polar plot
    theta_rad = np.deg2rad(theta)
    
    for idx, (n, pattern, pattern_db) in enumerate(zip(n_elements_list, patterns, patterns_db)):
        # Linear scale plot
        ax1 = plt.subplot(2, len(n_elements_list), idx + 1, projection='polar')
        pattern_abs = np.abs(pattern)
        ax1.plot(theta_rad, pattern_abs / np.max(pattern_abs))  # Normalize
        ax1.set_title(f'N = {n}\nLinear Scale')
        ax1.grid(True)
        
        # dB scale plot
        ax2 = plt.subplot(2, len(n_elements_list), idx + 1 + len(n_elements_list), projection='polar')
        # Scale dB pattern for polar plot (map -60 to 0 dB to 0 to 1)
        pattern_db_scaled = (pattern_db + 60) / 60  # Scale -60:0 dB to 0:1
        pattern_db_scaled = np.clip(pattern_db_scaled, 0, 1)  # Clip to valid range
        ax2.plot(theta_rad, pattern_db_scaled)
        ax2.set_title(f'N = {n}\ndB Scale')
        ax2.grid(True)
    
    plt.tight_layout()

def compare_with_python():
    """Compare performance with pure Python implementation for all array sizes."""
    import linear_array  # Original pure Python implementation
    
    n_elements_list = [1, 2, 4, 8, 64]
    theta = np.linspace(-180, 180, 721)
    
    print("\nPerformance Comparison:")
    print("-" * 60)
    print(f"{'N Elements':<10} {'Python (ms)':<12} {'Hybrid (ms)':<12} {'Speedup':<8} {'Max Diff':<10}")
    print("-" * 60)
    
    for n in n_elements_list:
        params_py = linear_array.ArrayParameters(n_elements=n, spacing_wavelength=0.5)
        params_c = ArrayParameters(n_elements=n, spacing_wavelength=0.5)
        
        # Test Python implementation
        start_time = plt.time.time()
        pattern_py = linear_array.calculate_pattern(params_py, theta)
        py_time = (plt.time.time() - start_time) * 1000  # Convert to ms
        
        # Test hybrid implementation
        start_time = plt.time.time()
        pattern_c = calculate_pattern(params_c, theta)
        c_time = (plt.time.time() - start_time) * 1000  # Convert to ms
        
        # Compare results
        max_diff = np.max(np.abs(pattern_py - pattern_c))
        speedup = py_time / c_time if c_time > 0 else float('inf')
        
        print(f"{n:<10d} {py_time:>11.3f} {c_time:>11.3f} {speedup:>7.1f}x {max_diff:>9.2e}")

def main():
    """Create and display the comparison plot."""
    try:
        parser = argparse.ArgumentParser(description='Display radiation patterns in different coordinate systems.')
        parser.add_argument('coords', nargs='?', choices=['cartesian', 'polar'], default='cartesian',
                          help='Coordinate system to use (cartesian or polar)')
        parser.add_argument('--snr', type=float, default=None,
                          help='Signal-to-Noise Ratio in dB for adding AWGN (default: no noise)')
        parser.add_argument('--phase-error', type=float, default=None,
                          help='Standard deviation of phase errors in degrees (default: no phase errors)')
        parser.add_argument('--steering', type=float, default=None,
                          help='Main beam steering angle in degrees (default: 0°)')
        parser.add_argument('--compare', action='store_true',
                          help='Run performance comparison with pure Python implementation')
        args = parser.parse_args()
        
        print(f"Selected coordinate system: {args.coords}")
        print("Starting calculations...")
        
        # Array sizes to compare
        n_elements_list = [8, 16, 32, 64, 128]  # Use larger arrays to better show steering
        theta = np.linspace(-180, 180, 721)  # 0.5 degree resolution
        
        # Calculate patterns for all array sizes
        patterns = []
        patterns_db = []
        for n in n_elements_list:
            params = ArrayParameters(
                n_elements=n,
                spacing_wavelength=0.5,
                steering_angle=args.steering if args.steering is not None else 0.0,
                phase_error_std=args.phase_error if args.phase_error is not None else 0.0
            )
            pattern = calculate_pattern(params, theta, snr_db=args.snr)  # Pass SNR parameter here
            pattern_abs = np.abs(pattern)
            max_val = np.max(pattern_abs)
            # Add small offset to prevent log of zero, and limit dynamic range to -60 dB
            pattern_db = 20 * np.log10(np.maximum(pattern_abs, max_val * 1e-6) / max_val)
            patterns.append(pattern)
            patterns_db.append(pattern_db)
        
        # Plot in the specified coordinate system
        if args.coords == 'polar':
            plot_polar(n_elements_list, theta, patterns, patterns_db, 
                      steering_angle=args.steering if args.steering is not None else 0.0,
                      snr_db=args.snr, phase_error_std=args.phase_error)
        else:
            plot_cartesian(n_elements_list, theta, patterns, patterns_db,
                         steering_angle=args.steering if args.steering is not None else 0.0,
                         snr_db=args.snr, phase_error_std=args.phase_error)
        
        if args.compare:
            compare_with_python()
        
        print("Displaying plot window...")
        plt.show(block=True)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()