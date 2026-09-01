import time
import concurrent.futures
import threading

start = time.perf_counter() # using performance counter to track time

def do_something(seconds):
    print('sleeping {seconds} second..')
    time.sleep(seconds)  # wait sleep 
    return f'done sleeping...{seconds}'
with concurrent.futures.ThreadPoolExecutor() as executor:
   secs = [5,4,3,2,1]
   #results = [executor.submit(do_something, sec) for sec in secs]
   results = executor.map(do_something, secs)

   for result in results:
       print(result)
   #for f in concurrent.futures.as_completed(results):
         #print(f.result())
   # f1 = executor.submit(do_something, 1)
    #f2 = executor.submit(do_something, 1)
    #print(f1.result())
    #print(f2.result())
# t1 = threading.Thread(target = do_something)
# t2 = threading.Thread(target = do_something)
# t1.start()
# t2.start()
# t1.join()
# t2.join()

#threads = []
#for _ in range(10):
 #   t = threading.Thread(target=do_something, args = [1.5])
   # t.start()
   # threads.append(t)
#for thread in threads:
   # thread.join()
finish = time.perf_counter()
print(f"Finshed in {round(finish-start, 2)} second(s)")