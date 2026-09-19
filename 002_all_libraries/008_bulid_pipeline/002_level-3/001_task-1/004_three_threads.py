import threading
import time

def write_to_file(filename: str, content: str):
    # Simulate I/O waiting
    time.sleep(1)
    with open(filename, "w") as f:
        f.write(content)
    print(f"Finished writing to {filename}")

# Create threads
t1 = threading.Thread(target=write_to_file, args=("file1.txt", "Content for file1"))
t2 = threading.Thread(target=write_to_file, args=("file2.txt", "Content for file2"))
t3 = threading.Thread(target=write_to_file, args=("file3.txt", "Content for file3"))

# Start all threads (they run concurrently, mostly waiting on I/O)
t1.start()
t2.start()
t3.start()

# Wait for all threads to finish
t1.join()
t2.join()
t3.join()

print("All files written.")