#Client methods  accept the same arguments as httpx.get(), httpx.post()
import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://www.example.com/')
        print(response)
    asyncio.run(main())

with httpx.Client() as client:
    headers = {'X-Custom':'value'}
    r = client.get('https://example.com', headers = headers)
    print(r.status_code, r.json())

# Sharing configuration across requests
url = 'http://httpbin.org/headers'
headers = {'User-Agent': 'my-app/0.0.1'}

with httpx.Client(headers = headers) as client:
    r = client.get(url)
    print(r.json()['headers']['User-Agent'])