import json
import re
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

class PipelineRecordSanitizer:
    def __init__(self, target_date_str: Optional[str] = None):
        # 1. datetime: Set execution temporal window
        if target_date_str:
            self.execution_date = datetime.strptime(target_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            self.execution_date = datetime.now(timezone.utc)
            
        # Define a regex pattern for extracting standard user IDs from messy strings
        self.user_id_pattern = re.compile(r"USR-[0-9]{5}")

    def clean_and_parse_record(self, raw_json_payload: str) -> Dict[str, Any]:
        """Parse raw string payloads using json, re, math, and datetime."""
        # 2. json: Deserialization
        try:
            record = json.loads(raw_json_payload)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}

        # 3. re: Extract clean patterns from dirty text fields
        raw_text = record.get("raw_message", "")
        matched_id = self.user_id_pattern.search(raw_text)
        extracted_user_id = matched_id.group(0) if matched_id else "UNKNOWN"

        # 4. math: Validate numerical integrity
        raw_score = record.get("score", float("nan"))
        if math.isnan(raw_score):
            normalized_score = 0.0
        else:
            normalized_score = math.ceil(raw_score)

        # 5. datetime: Append structured temporal metadata & partition keys
        processed_record = {
            "user_id": extracted_user_id,
            "score": normalized_score,
            "ingest_timestamp": self.execution_date.isoformat(),
            "partition_dt": self.execution_date.strftime("%Y%m%d")
        }
        
        return processed_record

# Example execution simulation
if __name__ == "__main__":
    sanitizer = PipelineRecordSanitizer("2026-06-01")
    sample_payload = '{"raw_message": "Event logged by USR-12345 successfully", "score": 42.2}'
    print(sanitizer.clean_and_parse_record(sample_payload))