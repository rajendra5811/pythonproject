import json
import re
import math
from datetime import datetime, timezone

def run_micro_pipeline(raw_payload: str) -> dict:
    # 1. json: Deserialize string to dict
    data = json.loads(raw_payload)
    
    # 2. re: Extract pattern from messy text (e.g., "ID-9921")
    match = re.search(r"ID-[0-9]+", data.get("log", ""))
    user_id = match.group(0) if match else "UNKNOWN"
    
    # 3. math: Clean floating point boundaries
    raw_val = data.get("metric", float("nan"))
    clean_score = 0 if math.isnan(raw_val) else math.ceil(raw_val)
    
    # 4. datetime: Generate UTC timestamp & daily partition key
    now = datetime.now(timezone.utc)
    
    return {
        "user_id": user_id,
        "metric": clean_score,
        "dt": now.strftime("%Y-%m-%d"),
        "loaded_at": now.isoformat()
    }

# Test execution
if __name__ == "__main__":
    payload = '{"log": "Transaction processed for ID-44910 successfully", "metric": 12.1}'
    print(run_micro_pipeline(payload))