import os
import requests
import asyncio
import aiohttp
import time
import json

api_key = os.getenv('ALPHAVANTAGE_API_KEY')
url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol={}&apikey={}'
symbols = ['AAPL', 'GOOG','TSLA','MSFT', 'AAPL', 'AAPL','GOOG','AAPL', 'GOOG','TSLA','MSFT', 'AAPL', 'AAPL','GOOG','AAPL', 'GOOG','TSLA','MSFT', 'AAPL', 'AAPL','GOOG']
results = []
for symbol in symbols:
    print(f"Working on symbol {symbol}")
    resp = requests.get(url.format(symbol, api_key), verify=False)
    results.append(resp.json())
    time.sleep(0.2)  # simple rate-limiting

with open("stock_overviews.json", "w") as f:
    json.dump(results, f, indent=2)