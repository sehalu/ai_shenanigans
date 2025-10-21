"""
Demo script to visualize radiation patterns with different steering angles using the hybrid Python/C implementation.
Shows how beam steering affects the radiation pattern of a linear array.

Usage: python demo_steering.py [--snr SNR_DB] [--phase-error STD_DEG]
"""
import sys
import os
import argparse
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for interactive plots
import matplotlib.pyplot as plt
from linear_array_hybrid import ArrayParameters, calculate_pattern

def plot_steering_comparison(angles, theta, patterns, patterns_db, snr_db=None, phase_error_std=None):
    """Create comparison plot in polar coordinates for different steering angles."""
    # Convert theta to radians for polar plot
    theta_rad = np.deg2rad(theta)
    
    # Set up the figure with two rows: linear and dB scale
    fig = plt.figure(figsize=(20, 10))
    title = 'Radiation Pattern for Different Steering Angles (N=64, d=0.5λ)'
    if snr_db is not None:
        title += f'\nSNR: {snr_db} dB'
    if phase_error_std is not None:
        title += f'\nPhase Error σ: {phase_error_std}°'
    fig.suptitle(title, fontsize=16)
    
    # Plot each steering angle
    n_angles = len(angles)
    for idx, (angle, pattern, pattern_db) in enumerate(zip(angles, patterns, patterns_db)):
        # Linear scale plot
        ax1 = plt.subplot(2, n_angles, idx + 1, projection='polar')
        pattern_abs = np.abs(pattern)
        ax1.plot(theta_rad, pattern_abs / np.max(pattern_abs))  # Normalize
        ax1.set_title(f'Steering: {angle}°\nLinear Scale')
        ax1.grid(True)
        
        # Add main beam marker
        beam_angle = np.deg2rad(angle)
        ax1.plot([beam_angle, beam_angle], [0, 1], 'r--', alpha=0.5)
        
        # dB scale plot
        ax2 = plt.subplot(2, n_angles, idx + 1 + n_angles, projection='polar')
        # Scale dB pattern for polar plot (map -60 to 0 dB to 0 to 1)
        pattern_db_scaled = (pattern_db + 60) / 60  # Scale -60:0 dB to 0:1
        pattern_db_scaled = np.clip(pattern_db_scaled, 0, 1)  # Clip to valid range
        ax2.plot(theta_rad, pattern_db_scaled)
        ax2.set_title(f'Steering: {angle}°\ndB Scale (-60 to 0 dB)')
        ax2.grid(True)
        
        # Add main beam marker
        ax2.plot([beam_angle, beam_angle], [0, 1], 'r--', alpha=0.5)
    
    plt.tight_layout()

def main():
    """Create and display the steering angle comparison plot."""
    try:
        parser = argparse.ArgumentParser(
            description='Display radiation patterns for different steering angles.')
        parser.add_argument('--snr', type=float, default=None,
                          help='Signal-to-Noise Ratio in dB for adding AWGN (default: no noise)')
        parser.add_argument('--phase-error', type=float, default=None,
                          help='Standard deviation of phase errors in degrees (default: no phase errors)')
        args = parser.parse_args()
        
        print("Calculating radiation patterns for different steering angles...")
        
        # Fixed parameters
        n_elements = 64  # Fixed number of elements
        theta = np.linspace(-180, 180, 721)  # 0.5 degree resolution
        steering_angles = [-60, -30, 0, 30, 60]  # Different steering angles to demonstrate
        
        # Calculate patterns for all steering angles
        patterns = []
        patterns_db = []
        for angle in steering_angles:
            params = ArrayParameters(
                n_elements=n_elements,
                spacing_wavelength=0.5,
                steering_angle=angle,
                phase_error_std=args.phase_error if args.phase_error is not None else 0.0
            )
            pattern = calculate_pattern(params, theta, snr_db=args.snr)
            pattern_abs = np.abs(pattern)
            max_val = np.max(pattern_abs)
            # Add small offset to prevent log of zero, and limit dynamic range to -60 dB
            pattern_db = 20 * np.log10(np.maximum(pattern_abs, max_val * 1e-6) / max_val)
            patterns.append(pattern)
            patterns_db.append(pattern_db)
        
        # Create and display the plot
        plot_steering_comparison(steering_angles, theta, patterns, patterns_db, 
                               args.snr, args.phase_error)
        
        print("Displaying plot window...")
        plt.show(block=True)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()