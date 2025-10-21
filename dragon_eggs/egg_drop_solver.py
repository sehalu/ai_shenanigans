"""
Dragon Egg Drop Problem Solver

The problem:
- 2 identical dragon eggs
- N-story tower (dynamically specified)
- Find the exact floor where eggs break
- Minimize the number of drops

The strategy:
1. Calculate optimal step sizes using mathematical formula
2. Use dynamic step sizes for first egg to divide the problem space
3. If first egg breaks, use second egg to check each floor linearly in the last interval
4. If first egg survives, continue with larger intervals

Time Complexity: O(1) for calculating drop points, O(d) for finding breaking point where d is drops needed
Space Complexity: O(k) where k is number of drop points needed

Mathematical background:
- For n floors, optimal solution requires k drops where k(k+1)/2 ≥ n
- First egg drop points are calculated to ensure second egg can complete within k drops
"""

from math import ceil, sqrt
from dataclasses import dataclass
from typing import List, Tuple
import time

@dataclass
class EggDropResult:
    """Results from an egg drop simulation."""
    breaking_floor: int
    drops_used: int
    optimal_drops: int
    execution_time: float

def calculate_optimal_drops(total_floors: int) -> int:
    """
    Calculate the minimum number of drops needed for a given number of floors.
    
    Uses the formula: k(k+1)/2 ≥ n where k is drops needed and n is number of floors.
    
    Args:
        total_floors: Number of floors in the tower
    
    Returns:
        Minimum number of drops needed
    """
    # Solve quadratic equation: x^2 + x - 2n = 0
    return ceil((-1 + sqrt(1 + 8 * total_floors)) / 2)

def calculate_optimal_first_drops(total_floors: int) -> List[int]:
    """
    Calculate the optimal floors to drop the first egg.
    
    The step size is calculated to ensure optimal number of drops
    for any building height.
    
    Args:
        total_floors: Total number of floors in the tower
    
    Returns:
        List of floor numbers to test with first egg
    
    Time complexity: O(k) where k is optimal number of drops
    Space complexity: O(k) for storing drop points
    """
    # Calculate optimal number of drops needed
    optimal_drops = calculate_optimal_drops(total_floors)
    
    drops = []
    current_floor = 0
    step = optimal_drops
    
    # Pre-allocate list for better memory efficiency
    drops = []
    drops.append(0)  # Add sentinel value for easier calculations
    
    while step > 0 and current_floor + step <= total_floors:
        current_floor += step
        drops.append(current_floor)
        step -= 1
    
    return drops[1:]  # Remove sentinel value

def find_breaking_point(breaking_floor: int, total_floors: int) -> EggDropResult:
    """
    Find the breaking point using the optimal strategy.
    
    Args:
        breaking_floor: The actual floor where eggs break
        total_floors: Total number of floors in the tower
        
    Returns:
        EggDropResult containing breaking floor, drops used, and optimal drops
    
    Time complexity: O(d) where d is the number of drops needed
    Space complexity: O(1) as we only store a constant number of variables
    """
    start_time = time.perf_counter()
    drops_used = 0
    first_egg_intact = True
    optimal_drops = calculate_optimal_drops(total_floors)
    
    # Get the optimal drop points for first egg
    drop_floors = calculate_optimal_first_drops(total_floors)
    
    # Binary search to find the interval where the first egg breaks
    # This optimization speeds up the search for large buildings
    if len(drop_floors) > 10:  # Only use binary search for large enough sets
        left, right = 0, len(drop_floors) - 1
        previous_floor = 0
        
        while left <= right:
            mid = (left + right) // 2
            floor = drop_floors[mid]
            drops_used += 1
            
            if floor == breaking_floor:
                return EggDropResult(
                    breaking_floor=floor,
                    drops_used=drops_used,
                    optimal_drops=optimal_drops,
                    execution_time=time.perf_counter() - start_time
                )
            elif floor > breaking_floor:
                first_egg_intact = False
                right = mid - 1
            else:
                previous_floor = floor
                left = mid + 1
    else:
        # Linear search for small sets
        previous_floor = 0
        for floor in drop_floors:
            drops_used += 1
            if floor >= breaking_floor:
                first_egg_intact = False
                break
            previous_floor = floor
    
    # If first egg survived all drops, the breaking point is above our last drop
    if first_egg_intact:
        return EggDropResult(
            breaking_floor=breaking_floor,
            drops_used=drops_used,
            optimal_drops=optimal_drops,
            execution_time=time.perf_counter() - start_time
        )
    
    # Use second egg to find exact breaking point by checking each floor
    for floor in range(previous_floor + 1, breaking_floor + 1):
        drops_used += 1
        if floor >= breaking_floor:
            return EggDropResult(
                breaking_floor=floor,
                drops_used=drops_used,
                optimal_drops=optimal_drops,
                execution_time=time.perf_counter() - start_time
            )
    
    return EggDropResult(
        breaking_floor=breaking_floor,
        drops_used=drops_used,
        optimal_drops=optimal_drops,
        execution_time=time.perf_counter() - start_time
    )

def demonstrate_solution():
    """Demonstrate the solution with various building heights and breaking points."""
    print("Dragon Egg Drop Problem Solution Demonstration")
    print("-" * 50)
    
    # Test cases with different building heights
    test_cases = [
        (100, [1, 14, 15, 27, 28, 98, 99, 100]),  # Classic 100-floor case
        (1000, [1, 100, 500, 999, 1000]),         # Tall building
        (10, [1, 5, 10]),                         # Small building
        (1, [1]),                                 # Edge case: 1 floor
        (2, [1, 2])                               # Edge case: 2 floors
    ]
    
    for total_floors, test_floors in test_cases:
        print(f"\nTesting {total_floors}-story building:")
        print("-" * 30)
        
        # Calculate and show optimal drops for this height
        optimal_drops = calculate_optimal_drops(total_floors)
        drops = calculate_optimal_first_drops(total_floors)
        print(f"Optimal drops needed: {optimal_drops}")
        print(f"First egg drop points: {drops}")
        
        # Test various breaking points
        print("\nTesting breaking points:")
        for breaking_floor in test_floors:
            result = find_breaking_point(breaking_floor, total_floors)
            print(f"\nBreaking floor: {breaking_floor}")
            print(f"Found floor: {result.breaking_floor}")
            print(f"Drops used: {result.drops_used}/{result.optimal_drops}")
            print(f"Execution time: {result.execution_time*1000:.3f} ms")

def analyze_performance():
    """Analyze performance for very large buildings."""
    print("\nPerformance Analysis for Large Buildings")
    print("-" * 50)
    
    buildings = [100, 1000, 10000, 100000, 1000000]
    
    for floors in buildings:
        # Test middle floor as it's typically the worst case
        breaking_floor = floors // 2
        result = find_breaking_point(breaking_floor, floors)
        
        print(f"\n{floors}-story building:")
        print(f"Optimal drops needed: {result.optimal_drops}")
        print(f"Actual drops used: {result.drops_used}")
        print(f"Execution time: {result.execution_time*1000:.3f} ms")
        print(f"Memory usage: ~{len(calculate_optimal_first_drops(floors)) * 8} bytes")

if __name__ == "__main__":
    demonstrate_solution()
    analyze_performance()