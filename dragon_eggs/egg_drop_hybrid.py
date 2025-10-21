"""
Hybrid Python/C implementation of the Dragon Egg Drop problem.
Uses ctypes to call optimized C functions for the performance-critical parts.
"""
import os
import sys
import time
import ctypes
from ctypes import Structure, c_uint32, c_double
from typing import Tuple

class EggDropResult(Structure):
    """Mirror of the C structure for results"""
    _fields_ = [
        ("breaking_floor", c_uint32),
        ("drops_used", c_uint32),
        ("optimal_drops", c_uint32),
        ("execution_time_ns", c_double)
    ]

def load_egg_drop_lib() -> ctypes.CDLL:
    """Load the compiled C library"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set the correct library name based on platform
    if sys.platform == 'win32':
        lib_path = os.path.join(script_dir, 'egg_drop_lib.dll')
        # Compile the library if it doesn't exist
        if not os.path.exists(lib_path):
            os.system(f'gcc -O3 -shared -o "{lib_path}" "{os.path.join(script_dir, "egg_drop_lib.c")}" -lm')
    else:
        lib_path = os.path.join(script_dir, 'egg_drop_lib.so')
        if not os.path.exists(lib_path):
            os.system(f'gcc -O3 -fPIC -shared -o "{lib_path}" "{os.path.join(script_dir, "egg_drop_lib.c")}" -lm')
    
    try:
        lib = ctypes.CDLL(lib_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load C library: {e}")
    
    # Set up function signatures
    lib.find_breaking_point.argtypes = [c_uint32, c_uint32]
    lib.find_breaking_point.restype = EggDropResult
    
    lib.get_optimal_drops.argtypes = [c_uint32]
    lib.get_optimal_drops.restype = c_uint32
    
    return lib

class HybridEggDropSolver:
    """Python wrapper for the C implementation"""
    def __init__(self):
        self.lib = load_egg_drop_lib()
    
    def find_breaking_point(self, breaking_floor: int, total_floors: int) -> Tuple[int, int, int, float]:
        """Find the breaking point using the C implementation"""
        result = self.lib.find_breaking_point(breaking_floor, total_floors)
        return (
            result.breaking_floor,
            result.drops_used,
            result.optimal_drops,
            result.execution_time_ns
        )
    
    def get_optimal_drops(self, total_floors: int) -> int:
        """Get optimal number of drops needed"""
        return self.lib.get_optimal_drops(total_floors)

def benchmark_hybrid():
    """Benchmark the hybrid implementation"""
    print("\nHybrid Python/C Implementation Benchmark")
    print("-" * 40)
    
    solver = HybridEggDropSolver()
    buildings = [100, 1000, 10000, 100000, 1000000]
    iterations = 10000
    
    total_time_ns = 0.0
    total_drops = 0
    
    for floors in buildings:
        breaking_floor = floors // 2  # Test middle floor
        
        # Warm-up runs
        for _ in range(100):
            solver.find_breaking_point(breaking_floor, floors)
        
        min_time_ns = float('inf')
        max_time_ns = 0
        avg_time_ns = 0
        total_iter_drops = 0
        
        # Benchmark runs
        for _ in range(iterations):
            _, drops, optimal, time_ns = solver.find_breaking_point(breaking_floor, floors)
            total_iter_drops += drops
            
            min_time_ns = min(min_time_ns, time_ns)
            max_time_ns = max(max_time_ns, time_ns)
            avg_time_ns += time_ns
        
        avg_time_ns /= iterations
        total_time_ns += avg_time_ns
        total_drops += total_iter_drops
        
        print(f"\n{floors}-story building:")
        print(f"  Optimal drops: {optimal}")
        print(f"  Avg drops used: {total_iter_drops / iterations:.2f}")
        print(f"  Min time: {min_time_ns:.3f} ns ({min_time_ns/1e6:.6f} ms)")
        print(f"  Max time: {max_time_ns:.3f} ns ({max_time_ns/1e6:.6f} ms)")
        print(f"  Avg time: {avg_time_ns:.3f} ns ({avg_time_ns/1e6:.6f} ms)")
        print(f"  Throughput: {1000.0/avg_time_ns:.2f} M ops/sec")
    
    print("\nOverall Statistics:")
    print(f"  Total time: {total_time_ns:.3f} ns ({total_time_ns/1e6:.6f} ms)")
    print(f"  Average drops per test: {total_drops/(len(buildings)*iterations):.2f}")

def demonstrate_hybrid():
    """Demonstrate the hybrid implementation with test cases"""
    print("Dragon Egg Drop Problem - Hybrid Python/C Implementation")
    print("-" * 50)
    
    solver = HybridEggDropSolver()
    test_cases = [
        (100, 50),     # 100-floor building, breaking at 50
        (1000, 500),   # 1000-floor building, breaking at 500
        (10, 5),       # 10-floor building, breaking at 5
        (1, 1),        # Edge case: 1-floor building
        (2, 2)         # Edge case: 2-floor building
    ]
    
    for floors, breaking in test_cases:
        print(f"\nTesting {floors}-story building:")
        print(f"Breaking floor: {breaking}")
        
        found_floor, drops, optimal, time_ns = solver.find_breaking_point(breaking, floors)
        
        print(f"Found floor: {found_floor}")
        print(f"Drops used: {drops}/{optimal}")
        print(f"Time: {time_ns:.3f} ns ({time_ns/1e6:.6f} ms)")

if __name__ == '__main__':
    demonstrate_hybrid()
    benchmark_hybrid()