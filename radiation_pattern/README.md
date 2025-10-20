# Linear Array Radiation Pattern Calculator

This module provides tools for calculating and visualizing radiation patterns from linear antenna arrays. It supports arrays with variable number of elements and custom amplitude/phase weights.

## Features

- Calculate radiation patterns for linear arrays with arbitrary number of elements
- Support for custom amplitude and phase weights
- Visualization in both linear and logarithmic (dB) scales
- Performance measurement tools
- Comprehensive test suite

## Installation

The package requires the following dependencies:
- NumPy
- Matplotlib
- pytest (for running tests)

You can install these dependencies using pip:
```bash
pip install numpy matplotlib pytest
```

## Usage

### Basic Example

Here's a simple example of how to use the module:

```python
import numpy as np
from radiation_pattern.linear_array import ArrayParameters, plot_radiation_pattern

# Create an array with 8 elements spaced 0.5 wavelengths apart
params = ArrayParameters(
    n_elements=8,
    spacing_wavelength=0.5,
    # Optional: custom amplitude taper
    amplitude_weights=np.hamming(8)
)

# Plot the radiation pattern
fig, axes = plot_radiation_pattern(params)
plt.show()
```

### Array Size Comparison Demo

You can run a comparison of different array sizes using the provided demo script:

```python
from radiation_pattern.examples.array_comparison import plot_array_comparison
import matplotlib.pyplot as plt

# Create comparison plot for different array sizes
fig = plot_array_comparison()
plt.show()
```

This will create a figure showing radiation patterns for arrays with 1, 2, 4, 8, and 64 elements,
displaying both linear and logarithmic (dB) scales for each configuration.

## API Documentation

### ArrayParameters

A dataclass that holds the configuration for a linear array:

- `n_elements`: Number of antenna elements
- `spacing_wavelength`: Spacing between elements in wavelengths
- `amplitude_weights`: Optional array of amplitude weights
- `phase_weights`: Optional array of phase weights in degrees

### Functions

#### calculate_pattern(params, theta)

Calculates the radiation pattern for given array parameters and angles.

- `params`: ArrayParameters object
- `theta`: Array of angles in degrees
- Returns: Complex array containing the radiation pattern

#### plot_radiation_pattern(params, theta=None)

Creates plots of the radiation pattern in both linear and dB scale.

- `params`: ArrayParameters object
- `theta`: Optional array of angles (default: -180° to 180°)
- Returns: matplotlib Figure and Axes objects

#### measure_performance(n_elements_range)

Measures computation time and memory usage for different array sizes.

- `n_elements_range`: Range of number of elements to test
- Returns: Dictionary with performance metrics

## Testing

Run the tests using pytest:

```bash
pytest radiation_pattern/tests/
```