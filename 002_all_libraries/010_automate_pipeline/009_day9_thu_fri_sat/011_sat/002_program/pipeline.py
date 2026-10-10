import json
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent


def read_json(file):
    with open(file, "r") as f:
        return json.load(f)


# ------------------
# BATCH: CURRENCIES
# ------------------

def load_currencies():

    currencies = read_json(BASE / "currencies.json")

    lookup = {}

    for currency in currencies:
        lookup[currency["currency"]] = currency

    return lookup


# ------------------
# BATCH: FX RATES
# ------------------

def load_rates():

    rates = read_json(BASE / "rates.json")

    lookup = {}

    for rate in rates:
        lookup[rate["pair"]] = rate["rate"]

    return lookup


# ------------------
# STREAM: TRADES
# ------------------

def stream_trades():

    trades = read_json(BASE / "trades.json")

    for trade in trades:
        yield trade


# ------------------
# PROCESS
# ------------------

def process_trades(rates):

    summary = defaultdict(lambda: {
        "trades": 0,
        "buy": 0,
        "sell": 0,
        "usd_value": 0
    })

    for trade in stream_trades():

        pair = trade["pair"]

        # Unknown currency pair
        if pair not in rates:
            continue

        amount = trade["amount"]
        rate = rates[pair]

        usd_value = amount * rate

        summary[pair]["trades"] += 1
        summary[pair]["usd_value"] += usd_value

        if trade["side"] == "BUY":
            summary[pair]["buy"] += amount

        elif trade["side"] == "SELL":
            summary[pair]["sell"] += amount

    return summary


# ------------------
# REPORT
# ------------------

def print_report(summary):

    for pair, data in summary.items():

        print(
            pair,
            "→ trades:",
            data["trades"],
            "→ buy:",
            data["buy"],
            "→ sell:",
            data["sell"],
            "→ USD:",
            round(data["usd_value"], 2)
        )


def main():

    currencies = load_currencies()

    rates = load_rates()

    summary = process_trades(rates)

    print_report(summary)


if __name__ == "__main__":
    main()