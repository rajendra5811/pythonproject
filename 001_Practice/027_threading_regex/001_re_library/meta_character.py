import re
# \ Used to drop the special meaning of character following it
# []  Represent a character class
# ^  Matches the beginning
# $ Matches the end
# . matches any character except newline
# | Matches with any char separated by it (OR)
#? Matches 0 or one occurence
# * any  no.of occurences
# + One or more occurences
# {} Indicate the no.of occurences of a preceding regex to match
#  () Enclose a group of Regex
b = "ayushi.jail@gmail.com"
match = re.search(r"[@]",b)
print(match)
match = re.search(r"\.",b)
print(match)
match = re.search(r"|.",b)
print(match)
match = re.findall(r"[i]",b)
print(match)
match = re.search(r"^a",b)
print(match)
match = re.search(r"$com",b)
print(match)
match = re.search(r"?a",b)
print(match)
match = re.search(r"+a",b)
print(match)
match = re.search(r"jail{1-2}",b)
print(match)
match = re.search(r"(j|g)ail",b)
print(match)
match = re.search(r'a\A')
print(match)
match = re.search(r'a\B')
print(match)