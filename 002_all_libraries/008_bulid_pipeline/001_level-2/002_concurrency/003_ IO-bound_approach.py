import asyncio
import time

async def  do_async_work(task_id: int, duration: float = 0.1) -> str:
    print(f"Task {task_id} started.")
    await asyncio.sleep(2)  # Simulate an asynchronous operation
    print(f"Task {task_id} completed.")

async def run_asyncio(tasks: int = 5) -> list[str]:
    start_time = time.time()
    task_list = [do_async_work(i, 0.1) for i in range(tasks)]
    results = await asyncio.gather(*task_list)
    end_time = time.time()
    print(f"All tasks completed in {end_time - start_time:.2f} seconds.")
    return results

if __name__ == "__main__":
    print("Starting async tasks...")
    start_time = time.perf_counter()
    results = asyncio.run(run_asyncio(5))
    elapsed_time = time.perf_counter() - start_time
    print(f"Results: {results}")
    for result in results:
        print(result)

    print(f"Total execution time: {elapsed_time:.2f} seconds.")
    print("Tasks ran concurrently using asynico (modern I/O-bound approach).")