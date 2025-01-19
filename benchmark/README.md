# Benchmark script

## Usage

1. Run the benchmark

First run the benchmark script for each server.

Make sure that either the [FastAPI](../python_fastapi/), [Rocket](../rust_rocket/) or [Axum](../rust_axum/) server is running on port 8000.

Then run the benchmark script with:
```
uv run benchmark.py
```

This will create a `benchmark_results_<server_name>.json` file for each server.

2. Plot the results

Then run the plot script with:
```
uv run plot_results.py
```
