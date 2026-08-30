from functools import reduce, total_ordering, cached_property

print(reduce(lambda x,y: x+y, [1,2,3,4,5], 10))
@total_ordering
class Car:
    def __init__(self, model, mileage):
        self.model = model
        self.mileage = mileage

    def __eq__(self, other):
        return self.mileage == other.mileage
    def __lt__(self, other):
        return self.mileage < other.mileage
c1 = Car("Audi", 700)
c2 = Car("BMW", 800)
print(c1 == c2)
print(c1 < c2)

class Marksheet:
    def __init__(self, *grades):
        self.grades = grades

    @cached_property
    def total(self):
        print("Calculating total.")
        return sum(self.grades)
    @cached_property
    def average(self):
        print("Calculating average.")
        return self.total/len(self.grades)
m = Marksheet(100, 90, 95)
print(m.average)
print(m.total)