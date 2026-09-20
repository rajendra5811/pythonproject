from typing import Any
import time
import requests
import httpx
import asyncio

BASE_URL = "https://httpbin.org"

async def fetch_get(client: httpx.AsyncClient) -> Any:
    response = await client.get(f"{BASE_URL}/get")
    return response.json()

async def fetch_post(client: httpx.AsyncClient) -> Any:
    data_to_post = {"key": "value"}
    response = await client.post(f"{BASE_URL}/post", json = data_to_post)
    return response.json()

async def fetch_put(client: httpx.AsyncClient) -> Any:
    data_to_put = {"key": "updated_value"}
    response = await client.put(f"{BASE_URL}/put", json = data_to_put)
    return response.json()

async def fetch_delete(client: httpx.AsyncClient) -> Any:
    response = await client.delete(f"{BASE_URL}/delete")
    return response.json()  

async def main() -> None:
    start_time = time.time()

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_get(client),
            fetch_post(client),
            fetch_put(client),
            fetch_delete(client)
        ]
        results = await asyncio.gather(*tasks)

    for result in results:
        print("Result:", result)
    
    end_time = time.time()
    print(f"All HTTP requests completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()