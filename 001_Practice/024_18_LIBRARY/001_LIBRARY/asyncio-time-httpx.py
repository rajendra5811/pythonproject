import asyncio
import httpx
import time

 async def main1():
    async with httpx.AsyncClient() as client:
       pokemons = []
       for number in range(1, 151):
          pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{number}'
          resp = await client.get(pokemon_url)
          pokemons.append(resp.json()['name']) 

 start_time = time.time()
 asyncio.run(main1())
 print(f"HTTPX Async: {time.time() -start_time} seconds.")

 async def get_pokemon(client, url):
        resp = await client.get(url)
        return resp.json()['name']
 async def main2():
   async with httpx.AsyncClient() as client:
      tasks = []
      for number in range(1, 151):
         url = f'https://pokeapi.co/api/v2/pokemon/{number}'
         tasks.append(asyncio.create_task(get_pokemon(client, url)))
      original_pokemon = await asyncio.gather(*tasks)

 start_time = time.time()
 asyncio.run(main2())
 print(f"HTTPX Async with tasks: {time.time() -start_time} seconds.")       