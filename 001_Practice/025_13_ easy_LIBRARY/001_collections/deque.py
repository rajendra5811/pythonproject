from collections import deque
list_items = [1,2,3,4,5]
list_items.insert(0,0) #insert
print(list_items)
items = deque([1,2,3,4,5])
print(type(items))
items.appendleft(0)
print(items)
#methods
items.append(6)
print(items)
items.extend([7,8,9])
items.extendleft([11,22,33])
print(items.pop())