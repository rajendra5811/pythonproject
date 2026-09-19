# create a json file with the bus travel data with timestamp logging 

import logging
from datetime import datetime, timedelta, timezone
import json

logging.basicConfig(level=logging.INFO)

bus_data = [
    {"route": "A", "passengers": 50, "timestamp": datetime.now(timezone.utc)},
    {"route": "B", "passengers": 30, "timestamp": datetime.now(timezone.utc)},
    {"route": "C", "passengers": 70, "timestamp": datetime.now(timezone.utc)},
]
# Convert datetime objects to ISO format strings for JSON
bus_data_serializable = [
    {
        "route": item["route"],
        "passengers": item["passengers"],
        "timestamp": item["timestamp"].isoformat(),
    }
    for item in bus_data
]
# Write data to a JSON file
with open("bus_travel_data.json", "w") as f:
    json.dump(bus_data_serializable, f)

# Log the timestamp of the data
for item in bus_data_serializable:
    logging.info(f"Bus route {item['route']} had {item['passengers']} passengers at {item['timestamp']}")