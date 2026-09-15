# Two threads competing for a lock

import threading
import time
from datetime import datetime

lock = threading.Lock()


def log(message):
    """Print the current time and the thread name so that we can observe the order of events"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    thread_name = threading.current_thread().name
    print(f"[{timestamp}] [{thread_name:<12}] {message}")


def worker():
    """Worker function that tries to acquire the lock, does some work, and then releases the lock"""
    log("Attempting to acquire lock.acquire()")
    lock.acquire()

    try:
        log("Successfully acquired the lock")
        # Hold the lock for a while to simulate some work being done
        log("Entering critical section")
        time.sleep(2)
        log("Exiting critical section")
    finally:
        log("Releasing lock")
        lock.release()


thread_a = threading.Thread(target=worker, name="Worker-A")
thread_b = threading.Thread(target=worker, name="Worker-B")

log("Starting worker-A")
thread_a.start()

# Wait a bit before starting the second thread to increase the chance of contention
time.sleep(0.5)

log("Starting worker-B")
thread_b.start()

thread_a.join()
thread_b.join()

log("Both threads have finished execution")