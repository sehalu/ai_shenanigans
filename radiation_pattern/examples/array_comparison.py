"""
Demo script showing radiation patterns for different array sizes.
"""

import numpy as np
import matplotlib.pyplot as plt
from radiation_pattern.linear_array import ArrayParameters, calculate_pattern

def plot_array_comparison(spacing_wavelength=0.5):
    """
    Create a comparison plot of radiation patterns for different array sizes.
    
    Args:
        spacing_wavelength: Spacing between elements in wavelengths
    """
    # Array sizes to compare
    n_elements_list = [1, 2, 4, 8, 64]
    theta = np.linspace(-180, 180, 721)  # 0.5 degree resolution
    
    # Create subplots
    fig = plt.figure(figsize=(20, 8))
    fig.suptitle('Radiation Pattern Comparison for Different Array Sizes\n'
                f'Element Spacing: {spacing_wavelength}λ', fontsize=16)
    
    # Create two rows of subplots: linear scale and dB scale
    gs = plt.GridSpec(2, len(n_elements_list), figure=fig)
    
    # Plot each array size
    for idx, n in enumerate(n_elements_list):
        # Create array parameters
        params = ArrayParameters(n_elements=n, spacing_wavelength=spacing_wavelength)
        
        # Calculate pattern
        pattern = calculate_pattern(params, theta)
        pattern_db = 20 * np.log10(np.abs(pattern) / np.max(np.abs(pattern)))
        
        # Linear scale plot
        ax1 = fig.add_subplot(gs[0, idx])
        ax1.plot(theta, np.abs(pattern))
        ax1.set_title(f'N = {n}')
        ax1.grid(True)
        if idx == 0:
            ax1.set_ylabel('Magnitude (Linear)')
        ax1.set_xlim(-180, 180)
        ax1.set_ylim(0, max(n_elements_list))  # Scale y-axis to maximum possible value
        
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
    return fig

if __name__ == '__main__':
    # Create and show the comparison plot
    fig = plot_array_comparison()
    plt.show()
    
    # Optionally save the figure
    fig.savefig('array_comparison.png', dpi=300, bbox_inches='tight')