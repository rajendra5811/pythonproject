import time
import threading 

start = time.perf_counter() # using performance counter to track time

def do_something():
    print('sleeping 1 second..')
    time.sleep(1)  # wait sleep 
    print('done')
t1 = threading.Thread(target = do_something)
t2 = threading.Thread(target = do_something)
t1.start()
t2.start()
do_something()
do_something()
finish = time.perf_counter()
print(f"Finshed in {round(finish-start, 2)} second(s)")