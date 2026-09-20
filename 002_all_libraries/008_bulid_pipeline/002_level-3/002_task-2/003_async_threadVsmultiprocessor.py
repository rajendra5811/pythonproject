import time
import asyncio
import threading
import multiprocessing

def do_work(task_id: int, duration: float = 0.1) -> str:
    """Simulates a CPU-bound task by sleeping for a specified duration."""
    time.sleep(duration)
    return f"Task {task_id} completed after {duration} seconds."

def run_async(tasks: int = 5) -> list[str]:
    """Runs a specified number of tasks asynchronously."""
    results = []
    for i in range(tasks):
        result = do_work(i, duration=0.1)
        results.append(result)
    return results

def run_threading(tasks: int = 5) -> list[str]:
    """Runs a specified number of tasks using threading."""
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=tasks) as executor:
        results = list(executor.map(do_work, range(tasks)))
    return results

def run_multiprocessing(tasks: int = 5) -> list[str]:
    """Runs a specified number of tasks using multiprocessing."""
    from multiprocessing import Pool

    with Pool(processes=tasks) as pool:
        results = pool.map(do_work, range(tasks))
    return results

if __name__ == "__main__":
    num_tasks = 5

    # Run tasks asynchronously
    start_time = time.time()
    async_results = run_async(num_tasks)
    async_duration = time.time() - start_time
    print(f"Async results: {async_results}")
    print(f"Async duration: {async_duration:.4f} seconds")

    # Run tasks using threading
    start_time = time.time()
    threading_results = run_threading(num_tasks)
    threading_duration = time.time() - start_time
    print(f"Threading results: {threading_results}")
    print(f"Threading duration: {threading_duration:.4f} seconds")

    # Run tasks using multiprocessing
    start_time = time.time()
    multiprocessing_results = run_multiprocessing(num_tasks)
    multiprocessing_duration = time.time() - start_time
    print(f"Multiprocessing results: {multiprocessing_results}")
    print(f"Multiprocessing duration: {multiprocessing_duration:.4f} seconds")      
