# Shared  memory in multithreading can lead to race conditions if not handled properly
import threading

shared_list = []

def append_to_list(tag):
    """Function to append an item to the shared list."""
    for _ in range(100000):
        shared_list.append(f"{tag}{i}")

t1 = threading.Thread(target=append_to_list, args=("Thread-1",))
t2 = threading.Thread(target=append_to_list, args=("Thread-2",))

t1.start()
t2.start()

t1.join()
t2.join()

print(f"Final list: {shared_list}")
