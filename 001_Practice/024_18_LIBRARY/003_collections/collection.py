from collections import Counter
counts = Counter()
print(counts)
print(type(counts))
print(issubclass(Counter, dict))

cities = [ "Mumbai","Delhi","Mumbai","Chennai","Delhi","Mumbai"]

city_counts = Counter(cities)

print(city_counts)
city_counts.most_common(2)