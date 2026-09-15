# SITUMATE PROCESSOR OR THREADING WORING MAKE TEA AND COFFEE WITHOUT WAITING FOR EACH OTHER 
import time
def make_coffee():
    print("Starting to make coffee...")
    time.sleep(2)  
    print("Coffee is ready!")

def make_tea():
    print("Starting to make tea...")
    time.sleep(2)  
    print("Tea is ready!")  

time_start = time.time()
make_coffee()
make_tea()
time_end = time.time()
print(f"Total time taken: {time_end - time_start:.2f} seconds") #Total time taken: 4.00 seconds