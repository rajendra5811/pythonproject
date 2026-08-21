import pandas as pd
from datetime import datetime, timezone
 
def transform(raw_records):
    """Keep the useful columns, clean them, and stamp each row."""
    df = pd.DataFrame(raw_records)
 
    # 1. keep only the columns we actually need
    df = df[["id", "symbol", "name", "current_price", "market_cap"]]
 
    # 2. rename to clearer names
    df = df.rename(columns={
        "current_price": "price_usd",
        "market_cap": "market_cap_usd",
    })
 
    # 3. force numbers to be numbers, and drop rows with no price
    df["price_usd"] = pd.to_numeric(df["price_usd"], errors="coerce")
    df = df.dropna(subset=["price_usd"])
 
    # 4. record when this batch was pulled
    df["loaded_at"] = datetime.now(timezone.utc)
 
    return df