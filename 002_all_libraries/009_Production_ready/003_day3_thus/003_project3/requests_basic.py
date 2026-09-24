import httpx

from server import start_server

base = start_server()

r = httpx.get(f"{base}/users", params={"active": "true"}, timeout = 5)
print(r.status_code, r.headers["content-type"])
print(r.json())

r = httpx.get(f"{base}/users/1", timeout = 5)
print(r.status_code, r.json()["name"])

r = httpx.get(f"{base}/users", json={"name": "charlie"}, timeout = 5)
print(r.status_code, r.json())
print(len(httpx.get(f"{base}/users", timeout = 5).json()), "users now")

