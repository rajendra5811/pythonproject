import httpx

from server import start_server

base = start_server()

r = httpx.get(f"{base}/users/99", timeout = 5)
print(r.status_code, r.json()["error"])

for path, kwargs in [("/users", {"json": {}), ("/boom", {})]:
    try:
         method = httpx.post if kwargs else httpx.get
        method(f"{base}{path}", **kwargs, timeout = 5).raise_for_status()
    except httpx.HTTPStatusError as err:
        print(err.response.status_code, err.response.json()["error"])

  try:
    httpx.get(f"{base}/slow", timeout = 0.2)
except httpx.TimeoutException as err:
    print("timed out after 0.2s")

try:
    httpx.get(f"{base}/slow", timeout = 1)
except httpx.ConnectTimeout as err:
    print("connection refused")