# httpx is fully featured http client for python3 
#HTTPX itself supports both synchronous and asynchronous APIs, plus HTTP/1.1 and HTTP/2
import httpx
# instead of request get method using httpx.get method
r = httpx.get("https://api.github.com/user", auth =('user','pass'))
print(r)
#
print(r.status_code)
#
print(r.content)
print(r.headers['content-type'])
#


