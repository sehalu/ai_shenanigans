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

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

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
 * Calculate optimal number of drops needed for n floors
 */
static inline uint32_t calculate_optimal_drops(uint32_t total_floors)
{
  return (uint32_t)ceil((-1.0 + sqrt(1.0 + 8.0 * total_floors)) / 2.0);
}

/**
 * Calculate optimal drop points for first egg
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
    uint32_t mid = (left + right) >> 1;
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
 * Find breaking point using optimal strategy - exported function
 */
EXPORT EggDropResult find_breaking_point(uint32_t breaking_floor, uint32_t total_floors)
{
  int64_t start_time = get_time_ns();
  EggDropResult result = {0};
  result.breaking_floor = breaking_floor;
  result.optimal_drops = calculate_optimal_drops(total_floors);
  
  static uint32_t drop_points[1000];
  uint32_t num_points = calculate_drop_points(total_floors, drop_points, 1000);
  
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
  else
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
 * Calculate optimal drops - exported function
 */
EXPORT uint32_t get_optimal_drops(uint32_t total_floors)
{
  return calculate_optimal_drops(total_floors);
}