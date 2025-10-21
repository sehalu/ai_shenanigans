#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <complex.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

// PCG Random Number Generator state
typedef struct {
    uint64_t state;
    uint64_t inc;
} pcg32_random_t;

// Initialize PCG RNG
static pcg32_random_t rng = { 0x853c49e6748fea9bULL, 0xda3e39cb94b95bdbULL };

// PCG Random Number Generator implementation
static uint32_t pcg32_random(void) {
    uint64_t oldstate = rng.state;
    rng.state = oldstate * 6364136223846793005ULL + rng.inc;
    uint32_t xorshifted = ((oldstate >> 18u) ^ oldstate) >> 27u;
    uint32_t rot = oldstate >> 59u;
    return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
}

// Seed the PCG RNG
EXPORT void seed_rng(uint64_t seed) {
    rng.state = seed;
    rng.inc = (seed << 1) | 1;
    pcg32_random(); // Advance state
}

// Generate random normal using Box-Muller transform
static double randn(double mean, double std_dev) {
    double u1, u2, z;
    static bool has_spare = false;
    static double spare;

    if (has_spare) {
        has_spare = false;
        return mean + std_dev * spare;
    }

    do {
        u1 = (double)pcg32_random() / UINT32_MAX;
        u2 = (double)pcg32_random() / UINT32_MAX;
    } while (u1 <= 1e-7);  // Avoid log(0)

    double r = sqrt(-2.0 * log(u1));
    double theta = 2.0 * M_PI * u2;
    z = r * cos(theta);
    spare = r * sin(theta);
    has_spare = true;

    return mean + std_dev * z;
}

/**
 * Calculate radiation pattern for a linear array
 * 
 * @param n_elements Number of array elements
 * @param spacing_wavelength Spacing between elements in wavelengths
 * @param amplitude_weights Array of amplitude weights (length n_elements)
 * @param phase_weights Array of phase weights in degrees (length n_elements)
 * @param phase_error_std Standard deviation of phase errors in degrees
 * @param theta_deg Array of angles in degrees
 * @param n_theta Length of theta array
 * @param pattern_out Output array for pattern (length n_theta)
 * @return 0 on success, -1 on error
 */
EXPORT int calculate_pattern(
    int n_elements,
    double spacing_wavelength,
    double steering_angle,  // Steering angle in degrees
    const double* amplitude_weights,
    const double* phase_weights,
    double phase_error_std,  // Standard deviation of phase errors in degrees
    const double* theta_deg,
    int n_theta,
    double complex* pattern_out
) {
    // Constants
    const double k = 2.0 * M_PI;  // Wavenumber (normalized to wavelength)
    const double d = spacing_wavelength;

    // Pre-calculate total phases in radians, including fresh random errors
    double* total_phases = (double*)malloc(n_elements * sizeof(double));
    if (!total_phases) return -1;

    for (int i = 0; i < n_elements; i++) {
        double phase_error = phase_error_std > 0 ? randn(0, phase_error_std) : 0;
        total_phases[i] = (phase_weights[i] + phase_error) * M_PI / 180.0;
    }

    // Convert steering angle to radians
    const double steering_rad = steering_angle * M_PI / 180.0;
    const double sin_steering = sin(steering_rad);

    // Calculate pattern for each angle
    #pragma omp parallel for if(n_theta > 1000)
    for (int t = 0; t < n_theta; t++) {
        const double theta_rad = theta_deg[t] * M_PI / 180.0;
        const double sin_theta = sin(theta_rad);
        double complex sum = 0;

        // Calculate contribution from each element
        for (int n = 0; n < n_elements; n++) {
            const double position = n * d;
            const double phase = k * position * (sin_theta - sin_steering) + total_phases[n];
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
        signal[i] += noise_std * (randn(0, 1) + I * randn(0, 1));
    }

    return 0;
}