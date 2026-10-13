from datetime import datetime
import logging
from pathlib import Path
import re
import shutil

# 1. Configure Production Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("EnterpriseLogPipeline")


class LogPipeline:

  def __init__(self, base_dir: str):
    self.base_path = Path(base_dir)
    self.incoming_dir = self.base_path / "incoming"
    self.archive_dir = self.base_path / "archive"
    self.error_dir = self.base_path / "errors"

    # Ensure required directory structure exists
    for directory in [self.incoming_dir, self.archive_dir, self.error_dir]:
      directory.mkdir(parents=True, exist_ok=True)

    # Regex for standard microservice log format:
    # Example: 2026-03-30 08:30:15 [AUTH-SRV] ERROR: Invalid token provided
    self.log_pattern = re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
        r"\[(?P<service>[\w-]+)\]\s+"
        r"(?P<level>INFO|WARN|ERROR|FATAL):\s+"
        r"(?P<message>.+)$"
    )

  def run(self):
    logger.info("Starting log pipeline execution cycle.")
    log_files = list(self.incoming_dir.glob("*.log"))

    if not log_files:
      logger.info("No incoming log files found to process.")
      return

    for file_path in log_files:
      self._process_file(file_path)

    logger.info("Log pipeline execution cycle completed successfully.")

  def _process_file(self, file_path: Path):
    logger.info(f"Processing file: {file_path.name}")
    metrics = {"total_lines": 0, "parsed_lines": 0, "failed_lines": 0}
    service_aggregates = {}

    archive_sub_dir = self.archive_dir / datetime.now().strftime("%Y-%m-%d")
    archive_sub_dir.mkdir(exist_ok=True)

    try:
      with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
          metrics["total_lines"] += 1
          cleaned_line = line.strip()

          if not cleaned_line:
            continue  # Skip empty lines

          match = self.log_pattern.match(cleaned_line)
          if match:
            metrics["parsed_lines"] += 1
            data = match.groupdict()
            service = data["service"]
            level = data["level"]

            # Aggregate errors/warnings per service
            service_aggregates.setdefault(
                service, {"INFO": 0, "WARN": 0, "ERROR": 0, "FATAL": 0}
            )
            if level in service_aggregates[service]:
              service_aggregates[service][level] += 1
          else:
            metrics["failed_lines"] += 1
            logger.warning(
                f"Malformed log format in {file_path.name} at line {line_num}:"
                f" '{cleaned_line}'"
            )

      # Log Aggregation Summary
      logger.info(f"Aggregation summary for {file_path.name}: {metrics}")
      for service, counts in service_aggregates.items():
        logger.info(f"Service '{service}' stats -> {counts}")

      # Safe Archive Move
      destination = archive_sub_dir / file_path.name
      shutil.move(str(file_path), str(destination))
      logger.info(f"Successfully archived {file_path.name} to {destination}")

    except Exception as e:
      logger.error(f"Critical failure processing {file_path.name}: {e}")
      # Move corrupted/unhandled files to error quarantine directory
      error_dest = self.error_dir / file_path.name
      shutil.move(str(file_path), str(error_dest))
      logger.error(f"Quarantined failed file to {error_dest}")


# --- Execution Example ---
if __name__ == "__main__":
  # Initialize pipeline pointing to a local workspace directory
  pipeline = LogPipeline(
      base_dir=str(Path(__file__).resolve().parent / "simple_logs")
  )
  pipeline.run()