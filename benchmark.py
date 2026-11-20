#!/usr/bin/env python3
"""Benchmark PyBot vs Rustbot performance comparison."""

import subprocess
import time
import json
import os
from pathlib import Path

# Test queries
TEST_QUERIES = [
    "hi, i'm Sam",
    "my kettle is full of limescale, how do i get rid of it?",
    "how do I make pancakes?",
    "what's the capital of France?",
    "how do I fix a leaking faucet?",
]

def measure_time(cmd_args: list[str], cwd: str, timeout: float = 15.0) -> tuple[float, str]:
    """Measure execution time and get output."""
    try:
        start = time.perf_counter()
        result = subprocess.run(
            cmd_args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.perf_counter() - start
        return elapsed, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return timeout, "TIMEOUT"
    except Exception as e:
        return timeout, f"ERROR: {e}"

def run_benchmark(pybot_dir: str, rustbot_dir: str, output_file: str = "benchmark_results.json"):
    """Run benchmark comparison between PyBot and Rustbot."""
    results = {
        "pybot": {},
        "rustbot": {},
        "comparison": {}
    }
    
    print("=" * 60)
    print("PyBot vs Rustbot Performance Benchmark")
    print("=" * 60)
    print()
    
    # Warm-up PyBot
    print("Warming up PyBot...")
    measure_time(["python3", "-m", "pybot", "-p", "test"], pybot_dir)
    
    # Warm-up Rustbot
    print("Warming up Rustbot...")
    measure_time(["./target/release/rustbot", "-p", "test"], rustbot_dir)
    
    print()
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"Test {i}/{len(TEST_QUERIES)}: '{query[:40]}...' ")
        
        # Benchmark PyBot
        pybot_time, pybot_output = measure_time(
            ["python3", "-m", "pybot", "-p", query],
            pybot_dir
        )
        
        # Benchmark Rustbot
        rustbot_time, rustbot_output = measure_time(
            ["./target/release/rustbot", "-p", query],
            rustbot_dir
        )
        
        # Calculate speedup
        speedup = pybot_time / rustbot_time if rustbot_time > 0 else float('inf')
        
        results["pybot"][f"query_{i}"] = {
            "query": query,
            "time_seconds": round(pybot_time, 4),
            "output": pybot_output[:100]  # Truncate for readability
        }
        
        results["rustbot"][f"query_{i}"] = {
            "query": query,
            "time_seconds": round(rustbot_time, 4),
            "output": rustbot_output[:100]
        }
        
        results["comparison"][f"query_{i}"] = {
            "pybot_time": round(pybot_time, 4),
            "rustbot_time": round(rustbot_time, 4),
            "speedup": round(speedup, 2)
        }
        
        print(f"  PyBot:      {pybot_time:.4f}s")
        print(f"  Rustbot:    {rustbot_time:.4f}s")
        print(f"  Speedup:    {speedup:.2f}x")
        print()
    
    # Save results
    with open(os.path.join(rustbot_dir, output_file), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary statistics
    pybot_times = [v["time_seconds"] for v in results["pybot"].values()]
    rustbot_times = [v["time_seconds"] for v in results["rustbot"].values()]
    
    avg_pybot = sum(pybot_times) / len(pybot_times)
    avg_rustbot = sum(rustbot_times) / len(rustbot_times)
    avg_speedup = avg_pybot / avg_rustbot if avg_rustbot > 0 else float('inf')
    
    print("=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Average PyBot time:     {avg_pybot:.4f}s")
    print(f"Average Rustbot time:   {avg_rustbot:.4f}s")
    print(f"Average Speedup:        {avg_speedup:.2f}x")
    print()
    print(f"Results saved to: {os.path.join(rustbot_dir, output_file)}")
    
    return results

if __name__ == "__main__":
    pybot_dir = "/projects/sandbox/pybot"
    rustbot_dir = "/projects/sandbox/Rustbot"
    
    if not os.path.isdir(pybot_dir):
        print(f"Error: PyBot directory not found: {pybot_dir}")
        exit(1)
    
    if not os.path.isdir(rustbot_dir):
        print(f"Error: Rustbot directory not found: {rustbot_dir}")
        exit(1)
    
    run_benchmark(pybot_dir, rustbot_dir)
