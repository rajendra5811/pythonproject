# Partial Function Example

This project demonstrates how to use Python's `functools.partial` to preconfigure function arguments and reuse a data-fetching function for multiple stock tickers.

## Project files

- `001_partial_function.py` - contains the sample code that fetches stock data using Yahoo Finance via `pandas_datareader`.

## What it does

The script defines a function called `get_stock_data(ticker, start, end)` and then creates several partial functions for different tickers:

- `AAPL`
- `GOOGL`
- `AMZN`

This reduces repeated argument passing and makes the function call cleaner and easier to read.

## Requirements

Install the dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Run the script

```bash
python 001_partial_function.py
```

## Notes

This example uses `pandas_datareader` to fetch historical stock data from Yahoo Finance. Internet access is required for the script to run successfully.
