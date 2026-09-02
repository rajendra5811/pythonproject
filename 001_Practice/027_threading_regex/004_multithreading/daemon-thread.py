import threading
import time

def infinite_task():
    while True:
        print("Running ...")
        time.sleep()

def main():
    daemon_thread = threading.Thread
    (target = infinite_task)
    daemon_thread.daemon = True
    daemon_thread.start()
    time.sleep(3)
    print("Main thread finished.")

if __name__ == "__main__":
    main()
