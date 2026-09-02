from time import sleep
import threading


def worker(event):
    print("worker waiting for event to start.")
    event.wait() 
    print("Worker starting work.")
    for _ in range(5):
        print("Worker starting work.")
        time.sleep(1)
    print("Worker finished")

def main():
    event = threading.Event()
    thread = threading.Thread(target = worker, args = (event,))
    thread.start()
    time.sleep()
    event.set()
    thread.join()

if __name__ == "__main__":
    main()