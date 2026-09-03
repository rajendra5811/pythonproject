class MyRange:
    def __init__(self, start, end):
        self.valueart
        self.end = end

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < self.end:
            value = self.current
            self.current += 1
            return value
        else:
            raise StopIteration
def my_range(start, end):
    current = start
    while current < end:
        yield current
        current += 1
nums = MyRange(1, 5)

for num in nums:
    print(num)