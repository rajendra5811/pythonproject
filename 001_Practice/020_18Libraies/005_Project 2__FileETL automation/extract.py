import requests
 
def extract():
    """Pull the top 20 coins by market cap from the CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 20,
        "page": 1,
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()   # stop loudly if the API returns an error
    return response.json()        # a list of dictionaries