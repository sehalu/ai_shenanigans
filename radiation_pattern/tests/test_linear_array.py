"""Tests for the linear array radiation pattern calculator."""

import numpy as np
import pytest
from ..linear_array import ArrayParameters, calculate_pattern, plot_radiation_pattern

def test_array_parameters_initialization():
    """Test proper initialization of ArrayParameters."""
    # Test default initialization
    params = ArrayParameters(n_elements=4, spacing_wavelength=0.5)
    assert params.n_elements == 4
    assert params.spacing_wavelength == 0.5
    assert np.all(params.amplitude_weights == np.ones(4))
    assert np.all(params.phase_weights == np.zeros(4))
    
    # Test custom weights
    custom_amp = np.array([1.0, 0.8, 0.8, 1.0])
    custom_phase = np.array([0, 30, 60, 90])
    params = ArrayParameters(
        n_elements=4,
        spacing_wavelength=0.5,
        amplitude_weights=custom_amp,
        phase_weights=custom_phase
    )
    assert np.all(params.amplitude_weights == custom_amp)
    assert np.all(params.phase_weights == custom_phase)

def test_array_parameters_validation():
    """Test validation of ArrayParameters."""
    with pytest.raises(ValueError):
        ArrayParameters(
            n_elements=4,
            spacing_wavelength=0.5,
            amplitude_weights=np.ones(3)  # Wrong size
        )
    
    with pytest.raises(ValueError):
        ArrayParameters(
            n_elements=4,
            spacing_wavelength=0.5,
            phase_weights=np.zeros(5)  # Wrong size
        )

def test_calculate_pattern_broadside():
    """Test radiation pattern calculation for broadside array."""
    params = ArrayParameters(n_elements=4, spacing_wavelength=0.5)
    theta = np.array([0.0])
    pattern = calculate_pattern(params, theta)
    
    # At broadside (0 degrees), pattern should be maximum
    assert np.abs(pattern[0]) == pytest.approx(params.n_elements, rel=1e-10)

def test_calculate_pattern_symmetry():
    """Test radiation pattern symmetry."""
    params = ArrayParameters(n_elements=4, spacing_wavelength=0.5)
    theta = np.array([-30.0, 30.0])
    pattern = calculate_pattern(params, theta)
    
    # Pattern should be symmetric for symmetric array
    assert np.abs(pattern[0]) == pytest.approx(np.abs(pattern[1]), rel=1e-10)

def test_plot_radiation_pattern():
    """Test that plotting functions return expected objects."""
    params = ArrayParameters(n_elements=4, spacing_wavelength=0.5)
    fig, (ax1, ax2) = plot_radiation_pattern(params)
    
    # Check that we got the expected plot objects
    assert ax1.get_xlabel() == 'Angle (degrees)'
    assert ax2.get_ylabel() == 'Magnitude (dB)'
    
    # Clean up
    plt.close(fig)