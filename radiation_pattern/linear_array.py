"""
Linear Array Radiation Pattern Calculator

This module provides tools for calculating and visualizing radiation patterns
from linear antenna arrays with variable number of elements.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional
from dataclasses import dataclass
import time

@dataclass
class ArrayParameters:
    """Parameters defining a linear antenna array."""
    n_elements: int
    spacing_wavelength: float
    steering_angle: float = 0.0  # Main beam steering angle in degrees
    amplitude_weights: Optional[np.ndarray] = None
    phase_weights: Optional[np.ndarray] = None
    phase_error_std: float = 0.0  # Standard deviation of phase errors in degrees
    _phase_errors: Optional[np.ndarray] = None

    def __post_init__(self):
        """Validate and initialize weights if not provided."""
        if self.amplitude_weights is None:
            self.amplitude_weights = np.ones(self.n_elements)
        if self.phase_weights is None:
            self.phase_weights = np.zeros(self.n_elements)
        
        if len(self.amplitude_weights) != self.n_elements:
            raise ValueError("Amplitude weights must match number of elements")
        if len(self.phase_weights) != self.n_elements:
            raise ValueError("Phase weights must match number of elements")
        
        # Generate random phase errors
        if self.phase_error_std > 0:
            self._phase_errors = np.random.normal(0, self.phase_error_std, self.n_elements)
        else:
            self._phase_errors = np.zeros(self.n_elements)
    
    def get_total_phases(self) -> np.ndarray:
        """Get the total phase for each element including errors."""
        return self.phase_weights + self._phase_errors
    
    def regenerate_phase_errors(self):
        """Generate new random phase errors. Useful for Monte Carlo simulations."""
        if self.phase_error_std > 0:
            self._phase_errors = np.random.normal(0, self.phase_error_std, self.n_elements)
        else:
            self._phase_errors = np.zeros(self.n_elements)

def add_awgn(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Add Additive White Gaussian Noise to a signal.
    
    Args:
        signal: Complex signal to add noise to
        snr_db: Signal-to-Noise Ratio in dB
        
    Returns:
        Signal with added noise
    """
    # Calculate signal power
    signal_power = np.mean(np.abs(signal)**2)
    
    # Calculate noise power from SNR
    snr_linear = 10**(snr_db/10)
    noise_power = signal_power / snr_linear
    
    # Generate complex noise
    noise = np.random.normal(0, np.sqrt(noise_power/2), signal.shape) + \
            1j * np.random.normal(0, np.sqrt(noise_power/2), signal.shape)
    
    return signal + noise

def calculate_pattern(params: ArrayParameters, theta: np.ndarray, snr_db: Optional[float] = None) -> np.ndarray:
    """
    Calculate the radiation pattern for a linear array.
    
    Args:
        params: ArrayParameters object containing array configuration
        theta: Array of angles (in degrees) to calculate pattern for
        snr_db: Optional Signal-to-Noise Ratio in dB for adding AWGN
        
    Returns:
        Complex array containing the radiation pattern
    """
    # Convert to radians
    theta_rad = np.deg2rad(theta)
    steering_rad = np.deg2rad(params.steering_angle)
    
    # Calculate phase progression
    k = 2 * np.pi  # Wavenumber (normalized to wavelength)
    d = params.spacing_wavelength
    
    # Element positions
    positions = np.arange(params.n_elements) * d
    
    # Calculate steering vector for each angle relative to steering angle
    steering_vectors = np.exp(1j * k * positions[:, np.newaxis] * (np.sin(theta_rad) - np.sin(steering_rad)))
    
    # Apply weights and phase errors
    total_phases = np.deg2rad(params.get_total_phases())  # Convert to radians
    weights = params.amplitude_weights * np.exp(1j * total_phases)
    
    # Calculate pattern
    pattern = np.dot(weights, steering_vectors)
    
    # Add noise if SNR is specified
    if snr_db is not None:
        pattern = add_awgn(pattern, snr_db)
    
    return pattern

def plot_radiation_pattern(params: ArrayParameters, theta: Optional[np.ndarray] = None) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot the radiation pattern in both linear and dB scale.
    
    Args:
        params: ArrayParameters object containing array configuration
        theta: Optional array of angles. If None, uses -180 to 180 degrees
        
    Returns:
        Figure and Axes objects containing the plots
    """
    if theta is None:
        theta = np.linspace(-180, 180, 721)  # 0.5 degree resolution
    
    # Calculate pattern
    pattern = calculate_pattern(params, theta)
    
    # Convert to dB, normalized
    pattern_db = 20 * np.log10(np.abs(pattern) / np.max(np.abs(pattern)))
    
    # Create subplot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    # Plot linear scale
    ax1.plot(theta, np.abs(pattern))
    ax1.set_title('Radiation Pattern (Linear Scale)')
    ax1.set_xlabel('Angle (degrees)')
    ax1.set_ylabel('Magnitude')
    ax1.grid(True)
    
    # Plot dB scale
    ax2.plot(theta, pattern_db)
    ax2.set_title('Radiation Pattern (dB Scale)')
    ax2.set_xlabel('Angle (degrees)')
    ax2.set_ylabel('Magnitude (dB)')
    ax2.set_ylim(-40, 0)  # Common range for radiation patterns
    ax2.grid(True)
    
    plt.tight_layout()
    return fig, (ax1, ax2)

def measure_performance(n_elements_range: range) -> dict:
    """
    Measure performance metrics for different array sizes.
    
    Args:
        n_elements_range: Range of number of elements to test
        
    Returns:
        Dictionary containing performance metrics
    """
    results = {
        'n_elements': [],
        'calc_time': [],
        'memory_usage': [],
    }
    
    theta = np.linspace(-180, 180, 721)
    
    for n in n_elements_range:
        params = ArrayParameters(n_elements=n, spacing_wavelength=0.5)
        
        # Measure calculation time
        start_time = time.time()
        _ = calculate_pattern(params, theta)
        calc_time = time.time() - start_time
        
        # Estimate memory usage (theoretical, in bytes)
        memory_usage = (
            n * 16 +  # Complex weights (8 bytes real + 8 bytes imag)
            len(theta) * 8 +  # Theta array (double precision)
            n * len(theta) * 16  # Steering vectors (complex)
        )
        
        results['n_elements'].append(n)
        results['calc_time'].append(calc_time)
        results['memory_usage'].append(memory_usage)
    
    return results