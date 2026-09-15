import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()

def ramesh_task():
    print("Ramesh: Trying to acquire lock_a")
    lock_a.acquire()
    print("Ramesh: Acquired lock_a")
    time.sleep(1)  # Simulate some work
    print("Ramesh: Trying to acquire lock_b")
    lock_b.acquire()
    print("Ramesh: Acquired lock_b")
    lock_b.release()
    lock_a.release()

def suresh_task():
    print("Suresh: Trying to acquire lock_b")
    lock_b.acquire()
    print("Suresh: Acquired lock_b")
    time.sleep(1)  # Simulate some work
    print("Suresh: Trying to acquire lock_a")
    lock_a.acquire()
    print("Suresh: Acquired lock_a")
    lock_a.release()
    lock_b.release()

ramesh_thread = threading.Thread(target=ramesh_task)
suresh_thread = threading.Thread(target=suresh_task)

ramesh_thread.start()
suresh_thread.start()

ramesh_thread.join()
suresh_thread.join()

print("program completed")