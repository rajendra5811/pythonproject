import re

c = '123jhon#$@^6773'
import re

a = 'charlie and the chocolate factory'
b = '0123456798'
c = '123jhon#$@^6773'
match = re.findall("[atx]",a) #[atx] returns a match where one of the specified characters(a,t,orx) are present
print(match)
match = re.findall("[a-t]",a) #[a-t] returns a match for any lower case character, alphabetically b/w a and h.
print(match)
match = re.findall("[^atx]",a) #[atx] returns a match for any char Except a,t, and x.
print(match)
match = re.findall("[0123]",c) #[atx] returns a match where any of the specified digits are present.
print(match)
match = re.findall("[0-9]",c) #[atx] returns a match for any digit b/w 0 & 9.
print(match)
match = re.findall("[0-7][0-9*]",c) #[atx] returns a match for two digit from 00 & 79.
print(match)
match = re.findall("[a-zA-Z]",c) #[a-zA-Z] returns a match for any character aplhabetically b/w a to z, and uppercase letter A to Z
print(match)
match = re.findall("[@$]",c) #[@$] returns a match for any symbol character in string
print(match)
# re.complie() re.split(98) means 98 will removed re.sub() re.subn() re.escape() re.search()
#sequence (string to lists)
a = "harry1 potter2345"
match =  re.search(r'\Ah', a)
print(match)
match =  re.search(r'ha\B', a)
print(match)
match =  re.search(r'\bha', a) # opposite 
print(match)
match = re.findall(r'\d', a)# numeric
print(match)
match = re.findall(r'\D',a)# non-numeric
print(match)
match = re.findall(r'\s',a)# whitespace
print(match)
match = re.findall(r'\S',a)# non-whitespace
print(match)
match = re.findall(r'\w',a)# alphanumeric
print(match)
match = re.findall(r'\W',a)# non-alphanumeric
print(match)
match = re.findall(r'5\Z',a)
print(match)