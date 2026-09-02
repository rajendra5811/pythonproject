import threading
import time
import queue

def producer(queue):
    for i in range(5):
        item = f"item{i}"
        print(f"Producing {item}")
        queue.put(item)
        time.sleep(1)
    queue.put(None) #Signal to consumer that

def consumer(queue):
    while True:
        item = queue.get()
        if item is None:
            break
        print(f"Consuming {item}")
        time.sleep(2)
def main():
    q = queue.Queue()
    producer_thread = threading.Thread(target = producer, args =(q,))
    consumer_thread = threading.Thread(target = consumer, args =(q,))
    producer_thread.start()
    consumer_thread.start()
    producer_thread.join()   
    consumer_thread.join()
    print("Main thread finished")
        

if __name__ == "__main__":
    main()