"""
Linear Array Radiation Pattern Calculator - Hybrid Python/C Implementation

This module provides tools for calculating and visualizing radiation patterns
from linear antenna arrays with variable number of elements. Performance-critical
calculations are performed in compiled C code.
"""

import os
import sys
import ctypes
import numpy as np
import numpy.ctypeslib as npct
import matplotlib.pyplot as plt
from typing import Tuple, Optional
from dataclasses import dataclass
import time

# Load the C library
def load_radiation_pattern_lib() -> ctypes.CDLL:
    """Load the compiled C library"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if sys.platform == 'win32':
        lib_path = os.path.join(script_dir, 'radiation_pattern_lib.dll')
        if not os.path.exists(lib_path):
            os.system(f'gcc -O3 -shared -o "{lib_path}" "{os.path.join(script_dir, "radiation_pattern_lib.c")}" -lm')
    else:
        lib_path = os.path.join(script_dir, 'radiation_pattern_lib.so')
        if not os.path.exists(lib_path):
            os.system(f'gcc -O3 -fPIC -shared -o "{lib_path}" "{os.path.join(script_dir, "radiation_pattern_lib.c")}" -lm')
    
    try:
        lib = ctypes.CDLL(lib_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load C library: {e}")
    
    # Set up function signatures
    array_1d_double = npct.ndpointer(dtype=np.float64, ndim=1, flags='CONTIGUOUS')
    array_1d_complex = npct.ndpointer(dtype=np.complex128, ndim=1, flags='CONTIGUOUS')
    
    lib.calculate_pattern.argtypes = [
        ctypes.c_int,          # n_elements
        ctypes.c_double,       # spacing_wavelength
        array_1d_double,       # amplitude_weights
        array_1d_double,       # phase_weights
        array_1d_double,       # phase_errors
        array_1d_double,       # theta_deg
        ctypes.c_int,          # n_theta
        array_1d_complex       # pattern_out
    ]
    lib.calculate_pattern.restype = ctypes.c_int
    
    lib.add_awgn.argtypes = [
        array_1d_complex,      # signal
        ctypes.c_int,          # n_samples
        ctypes.c_double        # snr_db
    ]
    lib.add_awgn.restype = ctypes.c_int
    
    return lib

# Load the C library on module import
_lib = load_radiation_pattern_lib()

@dataclass
class ArrayParameters:
    """Parameters defining a linear antenna array."""
    n_elements: int
    spacing_wavelength: float
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
        
        # Ensure arrays are contiguous and double precision
        self.amplitude_weights = np.ascontiguousarray(self.amplitude_weights, dtype=np.float64)
        self.phase_weights = np.ascontiguousarray(self.phase_weights, dtype=np.float64)
        self._phase_errors = np.ascontiguousarray(self._phase_errors, dtype=np.float64)
    
    def get_total_phases(self) -> np.ndarray:
        """Get the total phase for each element including errors."""
        return self.phase_weights + self._phase_errors
    
    def regenerate_phase_errors(self):
        """Generate new random phase errors. Useful for Monte Carlo simulations."""
        if self.phase_error_std > 0:
            self._phase_errors = np.random.normal(0, self.phase_error_std, self.n_elements)
        else:
            self._phase_errors = np.zeros(self.n_elements)
        self._phase_errors = np.ascontiguousarray(self._phase_errors, dtype=np.float64)

def calculate_pattern(params: ArrayParameters, theta: np.ndarray, snr_db: Optional[float] = None) -> np.ndarray:
    """
    Calculate the radiation pattern for a linear array using C implementation.
    
    Args:
        params: ArrayParameters object containing array configuration
        theta: Array of angles (in degrees) to calculate pattern for
        snr_db: Optional Signal-to-Noise Ratio in dB for adding AWGN
        
    Returns:
        Complex array containing the radiation pattern
    """
    # Ensure theta is contiguous and double precision
    theta = np.ascontiguousarray(theta, dtype=np.float64)
    
    # Prepare output array
    pattern = np.zeros(len(theta), dtype=np.complex128)
    
    # Call C function to calculate pattern
    result = _lib.calculate_pattern(
        params.n_elements,
        params.spacing_wavelength,
        params.amplitude_weights,
        params.phase_weights,
        params._phase_errors,
        theta,
        len(theta),
        pattern
    )
    
    if result != 0:
        raise RuntimeError("Failed to calculate radiation pattern")
    
    # Add noise if SNR is specified
    if snr_db is not None:
        result = _lib.add_awgn(pattern, len(pattern), snr_db)
        if result != 0:
            raise RuntimeError("Failed to add AWGN")
    
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

def compare_implementations(n_elements: int = 100, n_angles: int = 721) -> None:
    """
    Compare performance between Python and C implementations.
    
    Args:
        n_elements: Number of array elements
        n_angles: Number of angles to calculate
    """
    import linear_array  # Original pure Python implementation
    
    theta = np.linspace(-180, 180, n_angles)
    params_py = linear_array.ArrayParameters(n_elements=n_elements, spacing_wavelength=0.5)
    params_c = ArrayParameters(n_elements=n_elements, spacing_wavelength=0.5)
    
    # Test Python implementation
    start_time = time.time()
    pattern_py = linear_array.calculate_pattern(params_py, theta)
    py_time = time.time() - start_time
    
    # Test C implementation
    start_time = time.time()
    pattern_c = calculate_pattern(params_c, theta)
    c_time = time.time() - start_time
    
    # Compare results
    max_diff = np.max(np.abs(pattern_py - pattern_c))
    
    print(f"\nPerformance Comparison ({n_elements} elements, {n_angles} angles):")
    print("-" * 60)
    print(f"Python time:    {py_time*1000:.3f} ms")
    print(f"C time:         {c_time*1000:.3f} ms")
    print(f"Speedup:        {py_time/c_time:.1f}x")
    print(f"Max difference: {max_diff:.2e}")

if __name__ == '__main__':
    # Example usage
    print("This module contains the hybrid Python/C implementation.")
    print("For demonstrations, run demo_hybrid.py instead:")
    print("  python demo_hybrid.py [cartesian|polar] [--snr SNR] [--phase-error STD] [--compare]")
    print("\nExample commands:")
    print("  python demo_hybrid.py cartesian              # Show cartesian plot")
    print("  python demo_hybrid.py polar                  # Show polar plot")
    print("  python demo_hybrid.py --snr 20              # Add 20dB SNR noise")
    print("  python demo_hybrid.py --phase-error 5        # Add 5° phase errors")
    print("  python demo_hybrid.py --compare             # Compare with pure Python")