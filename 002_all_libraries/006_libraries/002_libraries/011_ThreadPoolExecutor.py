import time
import threading
from concurrent.futures import ThreadPoolExecutor

def send_email(name):
    print(f"Sending email to {name}")
    print(f"on {threading.current_thread().name}")
    time.sleep(2)  # Simulate an I/O operation
    print(f"Email sent to {name}")
    print(f"on {threading.current_thread().name}")
    return 100

start_time = time.time()
with ThreadPoolExecutor(max_workers=3) as executor:
    future_ramesh = executor.submit(send_email, "Ramesh") 
    print(future_ramesh.result()) 
    future_suresh = executor.submit(send_email, "Suresh") 
    print(future_suresh.result())
    future_rajesh = executor.submit(send_email, "Rajesh") 
    print(future_rajesh.result())
    future_mahesh = executor.submit(send_email, "Mahesh")
    print(future_mahesh.result())
    future_amit = executor.submit(send_email, "Amit")
    print(future_amit.result())
    future_vijay = executor.submit(send_email, "Vijay")
    print(future_vijay.result())
    print(future_ramesh.running(), future_ramesh.done())
    print(future_ramesh.result())  
    print(future_ramesh.running(), future_ramesh.done(), future_ramesh.result())

end_time = time.time()
print(f"Total time taken: {end_time - start_time:.2f} seconds")
