import itertools

counter = itertools.count(start = 5, step = 5)
print(next(counter))
print(next(counter))
print(next(counter))

counter1 = itertools.count()
for num in counter1:
    print(num)

counter2 = itertools.count()
data = [100, 200,300,400]

daily_data = list(zip(itertools.count(), data))
print(daily_data)