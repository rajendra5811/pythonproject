import threading

counter = 0
counter_lock = threading.Lock()

def increment():
    global counter
    with counter_lock:
        for _ in range(10000):
            counter += 1

def main():
    global counter
    threads = []
    for i in range(3):
        thread = threading.Thread
        (target = increment)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()