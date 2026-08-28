import asyncio
import os
import aiohttp

api_key = os.getenv("ALPHAVANTAGE_API_KEY")
url = "https://www.alphavantage.co/query?function=OVERVIEW&symbol={}&apikey={}"
symbols = ['AAPL', 'GOOG','TSLA','MSFT', 'AAPL', 'AAPL','GOOG','AAPL', 'GOOG','TSLA','MSFT', 'AAPL', 'AAPL','GOOG','AAPL', 'GOOG','TSLA','MSFT', 'AAPL', 'AAPL','GOOG']
results = []

#start = time.time()

async def get_symbols():
  async with aiohttp.ClientSession() as session:
    for symbol in symbols:
      print("Working on symbol {}".format(symbol))
      # Pass ssl=False inside client method or connector, not session.get()
      # Use await session.get(...) correctly
      async with session.get(
          url.format(symbol, api_key), ssl=False
      ) as response:
        data = await response.json()
        results.append(data)
      # Optional: Add a small delay if hitting rate limits (e.g., await asyncio.sleep(0.5))


asyncio.run(get_symbols())