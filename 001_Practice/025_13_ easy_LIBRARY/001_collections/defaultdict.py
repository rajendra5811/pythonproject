from collections import defaultdict

data = defaultdict()
print(data)
print(type(data))
#print(issubclass(defaultdict))

inventory = {'Computer':1,'TV':2,'Phone':1}
inventory['Phone'] += 1
print(inventory)
inventory_dd = defaultdict(int)
print(inventory_dd)
#with defaultdict
users = {'Nik': 'delhi', 'Kate': 'mumbai','Evan':'chennai','Nick': 'delhi', 'Katty': 'mumbai','sam':'chennai'}

locations_old = defaultdict(list)
for person, location in users.items():  # if location in locations
    locations_old[location].append(person)
print(locations_old)