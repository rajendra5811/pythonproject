import logging

# Debug: Detailed information, typically of interest only when diagnosing problems.
# INFO: Confirmation that`things are working as expected.
#WARNING: An indication that something unexpected happened, or indicative of some problem in the near future.The software is still working as expected.
#ERROR: Due to a more serious problem, the software has not been able to perform some function.
# CRITICAl: A serious error, indicating that the program itself may be unable to continue running.

logging.basicConfig(level = logging.DEBUG)
#logging.basicConfig(filename = 'test.log', level = logging.DEBUG)
def add(x,y):
    return x + y

def subtract(x,y):
    return x-y

def multiply(x,y):
    return x*y

def divide(x,y):
    return x/y

num_1 = 20
num_2 = 10

add_result = add(num_1, num_2)
logging.warnings('Add: {} + {} = {}'.format(num_1, num_2, add_result))

sub_result = subtract(num_1, num_2)
logging.warnings('Sub: {} - {} = {}'.format(num_1, num_2, sub_result))

mul_result =  multiply(num_1, num_2)
logging.warnings('Mul: {} * {} = {}'.format(num_1, num_2, mul_result))

div_result = divide(num_1, num_2)
logging.warnings('Div: {} / {} = {}'.format(num_1, num_2, div_result))