from threading import *
from time import sleep
class Hello(Thread):
    def run(self):
        for i in range(8):
            print('Hello')
            sleep(2)

class Hi(Thread):
    def run(self):
        for i in range(8):
            print("Hi")
            sleep(2)
t1 = Hello()
t2 = Hi()

t1.start()
sleep(0.2)
t2.start()
t1.join()
t2.join()
print("Bye")