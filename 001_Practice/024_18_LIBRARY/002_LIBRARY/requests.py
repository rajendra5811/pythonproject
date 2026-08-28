import os
import requests

api_key = os.getenv('ALPHAVANTAGE_API_KEY')
url = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol={}&apikey={}'
symbols = ['AAPL', 'GOOG','TSLA','MSFT']
results = []

for symbol in symbols:
    print('Working on symbol {}'.format(symbol))
    response = requests.get(url.format(symbol,api_key))
    results.append(response.json())
print('you did it!')