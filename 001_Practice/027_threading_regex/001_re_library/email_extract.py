import re

def extract_emails(text):
    # Regular expression pattern for matching email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Find all email addresses in the given text
    emails = re.findall(email_pattern, text)
    
    return emails
text1 =  "rajveer@gmail.com"
extract_emails(text1)
