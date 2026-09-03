from multiprocessing import Process
import time

def cpu_bound_task():
    count = 0
    for _ in range(10**7):
        count += 1  

def main():
    start_time = time.time()
    processes = [Process(target=cpu_bound_task) for _ in range(4)]
    for process in processes:
        process.start()
    for process in processes:
        process.join()

    print(f"Time taken with multiprocessing: {time.time() - start_time:.3f} seconds")

if __name__ == "__main__":
    main()


import threading
import time

def cpu_bound_task():
    count = 0
    for _ in range(10**7):
        count += 1

def main():
    start_time = time.time()
    threads = [threading.Thread(target=cpu_bound_task) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print(f"Time taken with threads: {time.time() - start_time:.3f} seconds")
if __name__ == "__main__":
    main()