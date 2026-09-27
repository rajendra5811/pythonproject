from functools import partial
import pandas_datareader as web

def get_stock_data(ticker, start, end):
    return web.DataReader(ticker, 'yahoo', start, end)

print(get_stock_data('AAPL', '2020-01-01', '2020-12-31'))

get_apple_data = partial(get_stock_data, 'AAPL')
print(get_apple_data('2020-01-01', '2020-12-31'))

get_google_data = partial(get_stock_data, 'GOOGL')
print(get_google_data('2020-01-01', '2020-12-31'))

get_amazon_data = partial(get_stock_data, 'AMZN')
print(get_amazon_data('2020-01-01', '2020-12-31'))

get_stock_data_from2018 = partial(get_stock_data, start='2018-01-01', end='2020-12-31')
print(get_stock_data_from2018('AAPL'))

