"""
Linear Array Radiation Pattern Calculator package.

This package provides tools for analyzing and visualizing radiation patterns
from linear antenna arrays.
"""

from .linear_array import ArrayParameters, calculate_pattern, plot_radiation_pattern, measure_performance

__all__ = ['ArrayParameters', 'calculate_pattern', 'plot_radiation_pattern', 'measure_performance']