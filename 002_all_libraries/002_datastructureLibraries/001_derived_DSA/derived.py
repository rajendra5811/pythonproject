import json
import re
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

class EventPayloadSanitizer:
    def __init__(self, raw_json_string: str):
        # 1. json: Deserialize raw string into Python dictionary
        try:
            self.payload: Dict[str, Any] = json.loads(raw_json_string)
        except json.JSONDecodeError:
            self.payload = {}
            
        # 2. re: Compile regex patterns for efficient cleaning of PII fields
        self.phone_regex = re.compile(r"\D+") # Matches anything that is NOT a digit
        
        # 3. datetime: Set pipeline execution baseline timeline
        self.current_time = datetime.now(timezone.utc)

    def scrub_pii_fields(self) -> None:
        """Sanitize phone numbers using re module pattern matching."""
        raw_phone = self.payload.get("phone", "")
        if raw_phone:
            # Strip all non-digit characters (dashes, spaces, parentheses)
            clean_phone = self.phone_regex.sub("", raw_phone)
            self.payload["clean_phone"] = clean_phone

    def evaluate_temporal_freshness(self) -> bool:
        """Check if event timestamp is within an acceptable 7-day window using datetime."""
        event_time_str = self.payload.get("event_timestamp")
        if not event_time_str:
            return False
            
        # Parse string to datetime object
        event_time = datetime.strptime(event_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        max_age = timedelta(days=7)
        
        # Calculate freshness
        return (self.current_time - event_time) <= max_age

    def validate_metrics(self) -> Dict[str, Any]:
        """Ensure financial or telemetry metrics are clean numbers using math."""
        raw_value = self.payload.get("metric_value", 0.0)
        
        # Guard against NaN or Inf values
        if math.isnan(raw_value) or math.isinf(raw_value):
            self.payload["metric_value"] = 0.0
        else:
            # Round up for clean batch storage reporting
            self.payload["metric_value"] = math.ceil(raw_value)
            
        return self.payload

    def process(self) -> Optional[Dict[str, str]]:
        """Run full sanitization pipeline and generate a date partition key."""
        if not self.payload or not self.evaluate_temporal_freshness():
            return None
            
        self.scrub_pii_fields()
        validated_data = self.validate_metrics()
        
        # Extract date for data lake partitioning string format
        event_dt = datetime.strptime(self.payload["event_timestamp"], "%Y-%m-%d %H:%M:%S")
        partition_path = event_dt.strftime("year=%Y/month=%m/day=%d")
        
        return {
            "partition": partition_path,
            "serialized_output": json.dumps(validated_data)
        }

# Example execution simulation
if __name__ == "__main__":
    sample_json = json.dumps({
        "event_timestamp": "2026-06-01 12:00:00",
        "phone": "+1 (555) 019-2834",
        "metric_value": 45.2
    })
    
    sanitizer = EventPayloadSanitizer(sample_json)
    result = sanitizer.process()
    print(result)