#dictionary
details_dict ={'Name':'raj', 'Age':'50','location':'telangana','Education':'Metriculation'}
print(nick_dict['Age'])
from collections import namedtuple
p = namedtuple('Person', ['Name','Age','location','Education'])
details_dict = p('ravi',88,'tamil nadiu','intermedate')
print(details_dict)
print(type(p))
print(issubclass(p , tuple))
print(p[0])
print(p.Age)
# default values
p1 =namedtuple('student',['Name','Age', 'Location','Company'], defaults = ['Telangana','intermedate'])
ravi = p1('ravi',45)
print(ravi, p1._field_defaults)
