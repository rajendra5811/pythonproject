import threading
import time
import random

counter = 0
iters = 20

def increment_many():

    global counter
    for _ in range(iters):  
        current_value = counter
        print(f"Current value: {current_value}")
        time.sleep(random.uniform(0.01, 0.1))
        counter = current_value + 1

num_threads = 5
threads = [threading.Thread(target=increment_many, name ="increment_thread_{i}") for _ in range(num_threads)]

print(f"{len(threads)} threads created.")

for thread in threads:
    thread.start()

print("All threads have finished.")

for thread in threads:
    thread.join()

print("expected counter value: ", num_threads * iters) # 5*20 = 100
print(f"Final counter value: {counter}")