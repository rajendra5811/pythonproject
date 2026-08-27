import httpx

r = httpx.get( "https://api.github.com/user",auth=("user", "pass")) # get request to url
print(r)
r = httpx.get( "https://httpbin.org/get") # simple get api
print(r)
r = httpx.post( "https://httpbin.org/post")
print(r)
r = httpx.delete( "https://httpbin.org/delete")
print(r)
r = httpx.optional( "https://httpbin.org/optional")
print(r)
r = httpx.post( "https://httpbin.org/post")
print(r)
print(r.status_code)
"""200 → successful
401 → authentication failed
403 → forbidden/rate limit
404 → not found
500 → server error"""
print(r.content)
print(r.headers["content-type"])
print(r.encoding)
print(r.json)