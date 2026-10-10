import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent


def read_json(file):
    with open(file, "r") as f:
        return json.load(f)


# BATCH
def load_stocks():

    stocks = read_json(BASE / "stocks.json")

    lookup = {}

    for stock in stocks:
        lookup[stock["symbol"]] = stock

    return lookup


# STREAM
def stream_trades():

    trades = read_json(BASE / "trades.json")

    for trade in trades:
        yield trade


# PROCESS
def process_trades(stocks):

    summary = defaultdict(lambda: {
        "trades": 0,
        "quantity": 0,
        "value": 0
    })

    for trade in stream_trades():

        symbol = trade["symbol"]

        # Reject unknown stock
        if symbol not in stocks:
            continue

        price = trade["price"]
        quantity = trade["quantity"]

        value = price * quantity

        summary[symbol]["trades"] += 1
        summary[symbol]["quantity"] += quantity
        summary[symbol]["value"] += value

    return summary


# REPORT
def print_report(stocks, summary):

    for symbol, data in summary.items():

        stock = stocks[symbol]

        print(
            stock["company"],
            "|",
            stock["sector"],
            "|",
            data
        )


def main():

    stocks = load_stocks()

    summary = process_trades(stocks)

    print_report(stocks, summary)


if __name__ == "__main__":
    main()