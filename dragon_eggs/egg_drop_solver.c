#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
#include <stdbool.h>
#ifdef _WIN32
#include <windows.h>
#endif

#ifndef TIME_UTC
#define TIME_UTC 1
#endif

/**
 * Get current time in nanoseconds
 */
static inline int64_t get_time_ns(void)
{
#ifdef _WIN32
  LARGE_INTEGER frequency;
  LARGE_INTEGER start;
  QueryPerformanceFrequency(&frequency);
  QueryPerformanceCounter(&start);
  return (int64_t)((start.QuadPart * 1000000000) / frequency.QuadPart);
#else
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return (int64_t)ts.tv_sec * 1000000000LL + ts.tv_nsec;
#endif
}

/**
 * Structure to hold egg drop simulation results
 */
typedef struct
{
  uint32_t breaking_floor;    // The floor where egg breaks
  uint32_t drops_used;        // Number of drops used
  uint32_t optimal_drops;     // Theoretical optimal drops
  double execution_time_ns;   // Time taken in nanoseconds
} EggDropResult;

/**
 * Calculate optimal number of drops needed for n floors
 * Uses formula: k(k+1)/2 ≥ n where k is drops needed
 * 
 * @param total_floors Number of floors in building
 * @return Minimum drops needed
 */
static inline uint32_t calculate_optimal_drops(uint32_t total_floors)
{
  return (uint32_t)ceil((-1.0 + sqrt(1.0 + 8.0 * total_floors)) / 2.0);
}

/**
 * Calculate optimal drop points for first egg
 * Uses pre-allocated array for better performance
 * 
 * @param total_floors Number of floors in building
 * @param drop_points Pre-allocated array to store drop points
 * @param max_points Size of drop_points array
 * @return Number of drop points calculated
 */
static uint32_t calculate_drop_points(uint32_t total_floors, uint32_t* drop_points, uint32_t max_points)
{
  uint32_t current_floor = 0;
  uint32_t step = calculate_optimal_drops(total_floors);
  uint32_t points = 0;
  
  while (step > 0 && current_floor + step <= total_floors && points < max_points)
  {
    current_floor += step;
    drop_points[points++] = current_floor;
    step--;
  }
  
  return points;
}

/**
 * Binary search through drop points
 * 
 * @param drop_points Array of drop points
 * @param num_points Number of points in array
 * @param breaking_floor Floor where egg breaks
 * @param drops_used Pointer to drops counter
 * @return Previous safe floor
 */
static inline uint32_t binary_search_drops(const uint32_t* drop_points, 
                                         uint32_t num_points,
                                         uint32_t breaking_floor,
                                         uint32_t* drops_used)
{
  uint32_t left = 0;
  uint32_t right = num_points - 1;
  uint32_t previous_floor = 0;
  
  while (left <= right)
  {
    uint32_t mid = (left + right) >> 1;  // Faster than division by 2
    uint32_t floor = drop_points[mid];
    (*drops_used)++;
    
    if (floor == breaking_floor)
    {
      return floor;
    }
    else if (floor > breaking_floor)
    {
      right = mid - 1;
    }
    else
    {
      previous_floor = floor;
      left = mid + 1;
    }
  }
  
  return previous_floor;
}

/**
 * Find breaking point using optimal strategy
 * 
 * @param breaking_floor Floor where egg breaks
 * @param total_floors Total floors in building
 * @return EggDropResult with simulation results
 */
EggDropResult find_breaking_point(uint32_t breaking_floor, uint32_t total_floors)
{
  int64_t start_time = get_time_ns();
  EggDropResult result = {0};
  result.breaking_floor = breaking_floor;
  result.optimal_drops = calculate_optimal_drops(total_floors);
  
  // Static allocation for better performance
  // Max possible drops is sqrt(2*MAX_UINT32) which is much less than 1000
  static uint32_t drop_points[1000];
  uint32_t num_points = calculate_drop_points(total_floors, drop_points, 1000);
  
  // First egg - Binary search for larger buildings
  uint32_t previous_floor;
  if (num_points > 10)
  {
    previous_floor = binary_search_drops(drop_points, num_points, breaking_floor, &result.drops_used);
    if (previous_floor == breaking_floor)
    {
      result.execution_time_ns = (double)(get_time_ns() - start_time);
      return result;
    }
  }
  else  // Linear search for small buildings
  {
    previous_floor = 0;
    for (uint32_t i = 0; i < num_points; i++)
    {
      result.drops_used++;
      if (drop_points[i] >= breaking_floor)
      {
        previous_floor = (i > 0) ? drop_points[i-1] : 0;
        break;
      }
      previous_floor = drop_points[i];
    }
  }
  
  // Second egg - Linear search in found interval
  // Use pointer arithmetic for efficiency
  uint32_t* floor_ptr = &previous_floor;
  while (++(*floor_ptr) <= breaking_floor)
  {
    result.drops_used++;
    if (*floor_ptr >= breaking_floor)
    {
      break;
    }
  }
  
  result.execution_time_ns = (double)(get_time_ns() - start_time);
  return result;
}

/**
 * Benchmark the solution with various building sizes
 */
void benchmark_solution(void)
{
  printf("\nPerformance Benchmark\n");
  printf("--------------------\n");
  
  const uint32_t buildings[] = {100, 1000, 10000, 100000, 1000000};
  const size_t num_buildings = sizeof(buildings) / sizeof(buildings[0]);
  const int iterations = 10000;  // Increased for better statistics
  
  double total_time_ns = 0.0;
  uint64_t total_drops = 0;
  
  for (size_t i = 0; i < num_buildings; i++)
  {
    uint32_t floors = buildings[i];
    uint32_t breaking_floor = floors / 2;  // Test middle floor for worst case
    
    // Run multiple iterations for more accurate timing
    const int iterations = 10000;  // Increased for better statistics
    double min_time_ns = INFINITY;
    double max_time_ns = 0;
    double avg_time_ns = 0;
    uint32_t total_iter_drops = 0;
    
    // Warm-up runs to ensure CPU is at full speed
    for (int w = 0; w < 100; w++)
    {
      find_breaking_point(breaking_floor, floors);
    }
    
    for (int j = 0; j < iterations; j++)
    {
      EggDropResult result = find_breaking_point(breaking_floor, floors);
      total_iter_drops += result.drops_used;
      
      if (result.execution_time_ns < min_time_ns) min_time_ns = result.execution_time_ns;
      if (result.execution_time_ns > max_time_ns) max_time_ns = result.execution_time_ns;
      avg_time_ns += result.execution_time_ns;
    }
    
    avg_time_ns /= iterations;
    total_time_ns += avg_time_ns;
    total_drops += total_iter_drops;
    
    printf("\n%u-story building:\n", floors);
    printf("  Optimal drops: %u\n", calculate_optimal_drops(floors));
    printf("  Avg drops used: %.2f\n", (double)total_iter_drops / iterations);
    printf("  Min time: %.3f ns (%.6f ms)\n", min_time_ns, min_time_ns / 1000000.0);
    printf("  Max time: %.3f ns (%.6f ms)\n", max_time_ns, max_time_ns / 1000000.0);
    printf("  Avg time: %.3f ns (%.6f ms)\n", avg_time_ns, avg_time_ns / 1000000.0);
    printf("  Throughput: %.2f M ops/sec\n", 1000.0 / avg_time_ns);
  }
  
  printf("\nOverall Statistics:\n");
  printf("  Total time: %.3f ns (%.6f ms)\n", total_time_ns, total_time_ns / 1000000.0);
  printf("  Average drops per test: %.2f\n", (double)total_drops / (num_buildings * iterations));
}

/**
 * Demonstrate the solution with various test cases
 */
void demonstrate_solution(void)
{
  printf("Dragon Egg Drop Problem - C Implementation\n");
  printf("----------------------------------------\n");
  
  // Test cases with different building heights
  const uint32_t test_cases[][2] = {
    {100, 50},    // 100-floor building, breaking at 50
    {1000, 500},  // 1000-floor building, breaking at 500
    {10, 5},      // 10-floor building, breaking at 5
    {1, 1},       // Edge case: 1-floor building
    {2, 2}        // Edge case: 2-floor building
  };
  
  const size_t num_cases = sizeof(test_cases) / sizeof(test_cases[0]);
  
  for (size_t i = 0; i < num_cases; i++)
  {
    uint32_t floors = test_cases[i][0];
    uint32_t breaking = test_cases[i][1];
    
    printf("\nTesting %u-story building:\n", floors);
    printf("Breaking floor: %u\n", breaking);
    
    EggDropResult result = find_breaking_point(breaking, floors);
    
    printf("Found floor: %u\n", result.breaking_floor);
    printf("Drops used: %u/%u\n", result.drops_used, result.optimal_drops);
    printf("Time: %.3f ns (%.6f ms)\n", result.execution_time_ns, result.execution_time_ns / 1000000.0);
  }
}

int main(void)
{
  demonstrate_solution();
  benchmark_solution();
  return 0;
}