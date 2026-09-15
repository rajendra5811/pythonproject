import threading
import time

balance = 100
lock = threading.Lock()  # Create a lock object to synchronize access to the balance
def withdraw(amount):
    global balance
    with lock:  # Acquire the lock before accessing the shared resource
     if balance >= amount:
        print(f"Balance before withdrawal: {balance}")
        time.sleep(1)  # Simulate some processing time or I/o,logging,GC,schedular
        balance -= amount
        print(f"Balance after withdrawal of {amount}: {balance}")
     else:
        print(f"Insufficient funds for withdrawal of {amount}. Current balance: {balance}")

t1 = threading.Thread(target=withdraw, args=(100,))
t2 = threading.Thread(target=withdraw, args=(100,))
t1.start()
t2.start()
t1.join()
t2.join()

print(f"Final balance: {balance}") #-100 and 2 100's are withdrawn from the same balance of 100, which is a race condition.