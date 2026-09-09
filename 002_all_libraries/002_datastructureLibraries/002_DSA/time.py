import json
import re
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class WebServerLogParser:
    def __init__(self, raw_log_lines: List[str]):
        # 1. re: Compile regex pattern to parse unstructured Apache/Nginx text log strings
        # Target format: 192.168.1.10 - - [01/Jun/2026:12:00:00 +0000] "GET /api/v1/data HTTP/1.1" 500 1234
        self.log_pattern = re.compile(
            r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<endpoint>\S+) \S+" (?P<status>\d+) (?P<bytes>\S+)'
        )
        self.raw_log_lines = raw_log_lines
        self.current_time = datetime.now(timezone.utc)

    def parse_and_structure_logs(self) -> List[Dict[str, Any]]:
        """Parse unstructured text logs into structured schema dictionaries."""
        structured_records = []
        error_count = 0

        for line in self.raw_log_lines:
            match = self.log_pattern.search(line)
            if not match:
                continue
            
            log_data = match.groupdict()
            
            # 2. datetime: Parse complex log timezone strings into ISO format
            try:
                dt_obj = datetime.strptime(log_data["timestamp"], "%d/%b/%Y:%H:%M:%S %z")
                log_data["iso_timestamp"] = dt_obj.isoformat()
            except ValueError:
                continue

            # 3. math: Handle numerical conversions, edge cases, and safety checks
            status_code = int(log_data["status"])
            if status_code >= 500:
                error_count += 1
            
            raw_bytes = log_data["bytes"]
            if raw_bytes == "-" or math.isnan(float(raw_bytes if raw_bytes != "-" else 0)):
                log_data["bytes_transferred"] = 0
            else:
                # Round up fractional byte chunks using math.ceil
                log_data["bytes_transferred"] = math.ceil(float(raw_bytes))

            structured_records.append(log_data)

        return structured_records

    def export_to_json_stream(self, records: List[Dict[str, Any]]) -> str:
        """Serialize structured dictionaries into JSON lines using json module."""
        # json.dumps converts objects to string lines for data lake stream insertion
        return "\n".join([json.dumps(record) for record in records])

# Example execution simulation
if __name__ == "__main__":
    sample_logs = [
        '192.168.1.50 - - [01/Jun/2026:10:15:30 +0000] "GET /v1/orders HTTP/1.1" 200 540',
        '10.0.0.12 - - [01/Jun/2026:10:15:32 +0000] "POST /v1/checkout HTTP/1.1" 500 -'
    ]
    
    parser = WebServerLogParser(sample_logs)
    parsed = parser.parse_and_structure_logs()
    json_stream = parser.export_to_json_stream(parsed)
    print("Serialized JSON Lines Stream:\n", json_stream)