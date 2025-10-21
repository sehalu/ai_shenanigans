#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <complex.h>
#include <stdbool.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

/**
 * Calculate radiation pattern for a linear array
 * 
 * @param n_elements Number of array elements
 * @param spacing_wavelength Spacing between elements in wavelengths
 * @param amplitude_weights Array of amplitude weights (length n_elements)
 * @param phase_weights Array of phase weights in degrees (length n_elements)
 * @param phase_errors Array of phase errors in degrees (length n_elements)
 * @param theta_deg Array of angles in degrees
 * @param n_theta Length of theta array
 * @param pattern_out Output array for pattern (length n_theta)
 * @return 0 on success, -1 on error
 */
EXPORT int calculate_pattern(
    int n_elements,
    double spacing_wavelength,
    const double* amplitude_weights,
    const double* phase_weights,
    const double* phase_errors,
    const double* theta_deg,
    int n_theta,
    double complex* pattern_out
) {
    // Constants
    const double k = 2.0 * M_PI;  // Wavenumber (normalized to wavelength)
    const double d = spacing_wavelength;

    // Pre-calculate total phases in radians
    double* total_phases = (double*)malloc(n_elements * sizeof(double));
    if (!total_phases) return -1;

    for (int i = 0; i < n_elements; i++) {
        total_phases[i] = (phase_weights[i] + phase_errors[i]) * M_PI / 180.0;
    }

    // Calculate pattern for each angle
    #pragma omp parallel for if(n_theta > 1000)
    for (int t = 0; t < n_theta; t++) {
        const double theta_rad = theta_deg[t] * M_PI / 180.0;
        const double sin_theta = sin(theta_rad);
        double complex sum = 0;

        // Calculate contribution from each element
        for (int n = 0; n < n_elements; n++) {
            const double position = n * d;
            const double phase = k * position * sin_theta + total_phases[n];
            sum += amplitude_weights[n] * (cos(phase) + I * sin(phase));
        }

        pattern_out[t] = sum;
    }

    free(total_phases);
    return 0;
}

/**
 * Add Additive White Gaussian Noise (AWGN) to a signal
 * 
 * @param signal Complex signal array
 * @param n_samples Number of samples
 * @param snr_db Signal-to-Noise Ratio in dB
 * @return 0 on success, -1 on error
 */
EXPORT int add_awgn(
    double complex* signal,
    int n_samples,
    double snr_db
) {
    // Calculate signal power
    double signal_power = 0;
    for (int i = 0; i < n_samples; i++) {
        signal_power += cabs(signal[i]) * cabs(signal[i]);
    }
    signal_power /= n_samples;

    // Calculate noise power from SNR
    const double snr_linear = pow(10.0, snr_db / 10.0);
    const double noise_power = signal_power / snr_linear;
    const double noise_std = sqrt(noise_power / 2.0);

    // Add complex noise to signal
    #pragma omp parallel for if(n_samples > 1000)
    for (int i = 0; i < n_samples; i++) {
        // Box-Muller transform for Gaussian random numbers
        double u1, u2, z1, z2;
        do {
            u1 = (double)rand() / RAND_MAX;
            u2 = (double)rand() / RAND_MAX;
        } while (u1 <= 1e-7);  // Avoid log(0)

        z1 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
        z2 = sqrt(-2.0 * log(u1)) * sin(2.0 * M_PI * u2);

        signal[i] += noise_std * (z1 + I * z2);
    }

    return 0;
}