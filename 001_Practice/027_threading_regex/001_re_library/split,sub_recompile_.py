import re

a = """ John has scored 89 marks. Lisa has scored 90 marks.  David has scored 70 marks"""
print(re.findall("[A-Z][a-z]*", a)) # words starting with capital letter

print(re.findall(re.compile("[a-d]"), a))
print(re.findall(re.compile("\d+"), a)) # digits like 90 but not as 9,0

# split
print(re.split("\d+",a))

# re.sub()
print(re.sub("\s+","",a))

# re.subn()
print(re.subn("\s+","",a)) #tuple and count of whitespace

# re.escape()
print(re.escape(a)) # replace space with \

# Match Object
match = re.search('\d', a)# numeric
print(match)
print(match.re)
print(match.string)
print(match.start())
print(match.end())
print(match.span())
print(match.group())