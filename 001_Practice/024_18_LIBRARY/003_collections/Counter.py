from collections import Counter
counts = Counter()
print(counts)
print(type(counts))
print(issubclass(Counter, dict))

cities = [ "Mumbai","Delhi","Mumbai","Chennai","Delhi","Mumbai"]

city_counts = Counter(cities)

print(city_counts)
print(city_counts.most_common(2)) # tuple
print(city_counts.most_common()[2]) # 
print(city_counts.get('Munbai')) 

# update method in Counter

city_counts.update(['Hyderabad','Kolkata','Nagpur','Bengalaru',"Hyderabad","Patna"])
print(city_counts)
#del method in Counter
del city_counts['Patna']
