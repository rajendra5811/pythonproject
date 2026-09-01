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