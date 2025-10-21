"""
Simple demo script to visualize radiation patterns.
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
from linear_array import ArrayParameters, calculate_pattern

def plot_cartesian(n_elements_list, theta, patterns, patterns_db, steering_angle=0, snr_db=None, phase_error_std=None):
    """Create comparison plot in Cartesian coordinates."""
    fig = plt.figure(figsize=(20, 8))
    title = 'Radiation Pattern Comparison for Different Array Sizes\n' \
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
        ax1.plot(theta, np.abs(pattern))
        ax1.set_title(f'N = {n}')
        ax1.grid(True)
        if idx == 0:
            ax1.set_ylabel('Magnitude (Linear)')
        ax1.set_xlim(-180, 180)
        ax1.set_ylim(0, max(n_elements_list))
        
        # dB scale plot
        ax2 = fig.add_subplot(gs[1, idx])
        ax2.plot(theta, pattern_db)
        ax2.grid(True)
        if idx == 0:
            ax2.set_ylabel('Magnitude (dB)')
        ax2.set_xlabel('Angle (degrees)')
        ax2.set_xlim(-180, 180)
        ax2.set_ylim(-40, 0)
    
    plt.tight_layout()

def plot_polar(n_elements_list, theta, patterns, patterns_db, steering_angle=0, snr_db=None, phase_error_std=None):
    """Create comparison plot in polar coordinates."""
    fig = plt.figure(figsize=(20, 10))
    title = 'Radiation Pattern Comparison for Different Array Sizes\n' \
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
        ax1.plot(theta_rad, np.abs(pattern))
        ax1.set_title(f'N = {n}\nLinear Scale')
        ax1.grid(True)
        
        # dB scale plot
        ax2 = plt.subplot(2, len(n_elements_list), idx + 1 + len(n_elements_list), projection='polar')
        # Normalize dB pattern to positive values for polar plot
        pattern_db_norm = pattern_db - np.min(pattern_db)
        ax2.plot(theta_rad, pattern_db_norm)
        ax2.set_title(f'N = {n}\ndB Scale')
        ax2.grid(True)
    
    plt.tight_layout()

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
        args = parser.parse_args()
        
        print(f"Selected coordinate system: {args.coords}")
        print("Starting calculations...")
        
        # Array sizes to compare
        n_elements_list = [1, 2, 4, 8, 64]
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
            pattern = calculate_pattern(params, theta, snr_db=args.snr)
            pattern_db = 20 * np.log10(np.abs(pattern) / np.max(np.abs(pattern)))
            patterns.append(pattern)
            patterns_db.append(pattern_db)
        
        # Plot in the specified coordinate system
        if args.coords == 'polar':
            plot_polar(n_elements_list, theta, patterns, patterns_db, args.snr, args.phase_error)
        else:
            plot_cartesian(n_elements_list, theta, patterns, patterns_db, args.snr, args.phase_error)
        
        print("Displaying plot window...")
        plt.show(block=True)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()