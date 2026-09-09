import os
import sys
import subprocess
from pathlib import Path
from typing import List

class DropZoneIngestionDispatcher:
    def __init__(self, drop_zone_dir: str = "incoming_data"):
        # 1. pathlib: Object-oriented scan of the local drop zone
        self.drop_zone = Path.cwd() / drop_zone_dir
        
        # 2. os: Pull environment configurations (e.g., target cloud bucket)
        self.target_bucket = os.getenv("DATA_LAKE_BUCKET", "s3://my-default-lake-landing")
        self.max_file_age_days = int(os.getenv("MAX_FILE_AGE", "7"))
        
        # 3. sys: Capture runtime arguments (e.g., checking for a dry-run flag)
        self.is_dry_run = "--dry-run" in sys.argv
        
    def scan_and_validate_files(self) -> List[Path]:
        """Find pending CSV/Parquet files in the drop zone using pathlib."""
        if not self.drop_zone.exists():
            print(f"Drop zone does not exist. Creating: {self.drop_zone}")
            self.drop_zone.mkdir(parents=True, exist_ok=True)
            return []
            
        # pathlib: recursive glob for incoming datasets
        pending_files = list(self.drop_zone.glob("**/*.csv")) + list(self.drop_zone.glob("**/*.parquet"))
        print(f"Found {len(pending_files)} files ready for ingestion.")
        return pending_files

    def sync_to_storage(self) -> bool:
        """Trigger an external system sync tool (like AWS CLI) via subprocess."""
        files = self.scan_and_validate_files()
        if not files:
            print("No files to sync. Exiting gracefully.")
            sys.exit(0)
            
        # Build external command
        cmd = ["aws", "s3", "sync", str(self.drop_zone), self.target_bucket]
        if self.is_dry_run:
            cmd.append("--dry-run")
            print("Running in DRY-RUN mode.")

        try:
            print(f"Invoking external sync command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print("Sync STDOUT:\n", result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Sync failed with error code {e.returncode}")
            print("Sync STDERR:\n", e.stderr)
            sys.exit(2)

# Example execution simulation
if __name__ == "__main__":
    dispatcher = DropZoneIngestionDispatcher()
    # dispatcher.sync_to_storage()