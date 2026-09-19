from pathlib import Path
import glob
import logging
logging.basicConfig(level=logging.INFO)
raw_dir = Path("raw")
if not raw_dir.exists():
    logging.error("Error: Could not find raw data directory")
else:

    for file_path in raw_dir.glob("*.json"):
        file = Path(file_path)
        if file.is_file():
            logging.info(f"Found: {file.name}")