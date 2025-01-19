import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import concurrent.futures
import argparse

BASE_URL = "http://localhost:8000"


# Create a session with connection pooling and retries
session = requests.Session()
retries = Retry(total=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries, pool_connections=100, pool_maxsize=100)
session.mount("http://", adapter)


def hello_world():
    return session.get(f"{BASE_URL}/")


def create_task():
    response = session.post(
        f"{BASE_URL}/tasks", json={"name": "Test Task", "done": False}
    )
    response.raise_for_status()
    return response.json()["id"]


def read_task(task_id):
    response = session.get(f"{BASE_URL}/tasks/{task_id}")
    response.raise_for_status()


def update_task(task_id):
    response = session.put(
        f"{BASE_URL}/tasks/{task_id}", json={"name": "Updated Task", "done": True}
    )
    response.raise_for_status()


def delete_task(task_id):
    response = session.delete(f"{BASE_URL}/tasks/{task_id}")
    response.raise_for_status()


def prepare_tasks(iterations, parallel_requests):
    task_ids = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=parallel_requests
    ) as executor:
        futures = [executor.submit(create_task) for _ in range(iterations)]
        for future in concurrent.futures.as_completed(futures):
            task_id = future.result()
            if task_id is not None:
                task_ids.append(task_id)
    return task_ids


def cleanup_tasks(task_ids, parallel_requests):
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=parallel_requests
    ) as executor:
        futures = [executor.submit(delete_task, task_id) for task_id in task_ids]
        concurrent.futures.wait(futures)


def benchmark_operation(
    operation, single_threaded, iterations, parallel_requests, task_ids=None
):
    if single_threaded:
        start_time = time.perf_counter()
        for task_id in task_ids or range(iterations):
            operation(task_id) if task_ids else operation()
        end_time = time.perf_counter()
    else:
        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=parallel_requests
        ) as executor:
            futures = [
                (
                    executor.submit(operation, task_id)
                    if task_ids
                    else executor.submit(operation)
                )
                for task_id in (task_ids or range(iterations))
            ]
            concurrent.futures.wait(futures)
        end_time = time.perf_counter()
    return (
        (end_time - start_time) / iterations * 1000
    )  # Average time per operation in milliseconds


def run_benchmarks(iterations, parallel_requests):
    benchmarks = [
        ("Hello World", hello_world, None),
        ("Create", create_task, None),
        ("Read", read_task, prepare_tasks),
        ("Update", update_task, prepare_tasks),
        ("Delete", delete_task, prepare_tasks),
    ]

    results = {}

    for name, operation, setup_function in benchmarks:
        task_ids = (
            setup_function(iterations, parallel_requests) if setup_function else None
        )

        # Benchmark single-threaded
        single_threaded_time = benchmark_operation(
            operation, True, iterations, parallel_requests, task_ids
        )
        results[name] = {"single_threaded": single_threaded_time}

        # Cleanup after single-threaded benchmark if necessary
        if task_ids and name != "Delete":
            cleanup_tasks(task_ids, parallel_requests)

        # Re-prepare tasks for multi-threaded benchmark if necessary
        task_ids = (
            setup_function(iterations, parallel_requests) if setup_function else None
        )

        # Benchmark multi-threaded
        multi_threaded_time = benchmark_operation(
            operation, False, iterations, parallel_requests, task_ids
        )
        results[name]["multi_threaded"] = multi_threaded_time

        # Cleanup after multi-threaded benchmark if necessary
        if task_ids and name != "Delete":
            cleanup_tasks(task_ids, parallel_requests)

        # Print results
        print(f"\nBenchmarking {name}:")
        print(f"  Single-threaded: {single_threaded_time:.6f} ms per operation")
        print(f"  Multi-threaded:  {multi_threaded_time:.6f} ms per operation")

    return results


def save_results(results, filename="benchmark_result.json"):
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {filename}")


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark FastAPI server performance")
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations for each operation (default: 100)",
    )
    parser.add_argument(
        "--parallel-requests",
        type=int,
        default=10,
        help="Number of parallel requests for multi-threaded tests (default: 10)",
    )
    return parser.parse_args()


def identify_server() -> str:
    return session.get(f"{BASE_URL}/info").text


if __name__ == "__main__":
    args = parse_args()
    server_name = identify_server()
    print(f"Server name: {server_name}")
    print(f"Running benchmark with {args.iterations} iterations for each operation")
    print(f"Using {args.parallel_requests} parallel requests for multi-threaded tests")
    benchmark_results = run_benchmarks(args.iterations, args.parallel_requests)
    save_results(benchmark_results, f"benchmark_results_{server_name}.json")
