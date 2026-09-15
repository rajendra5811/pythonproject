import threading
import time
import random

counter = 0
iters = 20
lock = threading.Lock()  # Create a lock object to synchronize access to the counter


def increment_many():
    global counter
    # Try to acquire the lock with a timeout
    if not lock.acquire(timeout=10):
        # Could not acquire lock within timeout; skip work for this thread
        return

    try:
        for _ in range(iters):
            current_value = counter
            print(f"[{threading.current_thread().name}] Current value: {current_value}")
            time.sleep(random.uniform(0.01, 0.1))
            counter = current_value + 1
    finally:
        lock.release()


num_threads = 5
threads = [
    threading.Thread(target=increment_many, name=f"increment_thread_{i}")
    for i in range(num_threads)
]

print(f"{len(threads)} threads created.")

for thread in threads:
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All threads have finished.")
print("Expected counter value:", num_threads * iters)  # 5*20 = 100
print(f"Final counter value: {counter}")