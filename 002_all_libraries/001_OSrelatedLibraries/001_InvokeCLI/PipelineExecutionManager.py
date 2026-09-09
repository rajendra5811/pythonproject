import os
import sys
from pathlib import Path
import subprocess
from typing import List, Optional

class PipelineExecutionManager:
    def __init__(self, staging_dir: str = "data/staging"):
        # 1. pathlib: Setup object-oriented paths
        self.root_path = Path.cwd()
        self.staging_path = self.root_path / staging_dir
        
        # 2. os: Pull environment configurations securely
        self.db_user = os.getenv("DB_USER", "default_user")
        self.environment = os.getenv("ENV", "development")
        
        # 3. sys: Inspect runtime arguments passed via CLI
        self.runtime_args = sys.argv[1:]
        
    def prepare_workspace(self) -> None:
        """Ensure local staging directory exists using pathlib."""
        self.staging_path.mkdir(parents=True, exist_ok=True)
        print(f"[{self.environment.upper}] Workspace ready at: {self.staging_path}")
        
        if self.runtime_args:
            print(f"Captured runtime batch parameters: {self.runtime_args}")

    def run_external_cli_task(self, command: list[str]) -> bool:
        """Execute external command-line tools (e.g., dbt) using subprocess."""
        try:
            print(f"Executing external command: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            print("Subprocess STDOUT:\n", result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Subprocess FAILED with exit code {e.returncode}")
            print("Subprocess STDERR:\n", e.stderr)
            sys.exit(1) # Gracefully kill script on failure

# Example execution simulation
if __name__ == "__main__":
    manager = PipelineExecutionManager()
    manager.prepare_workspace()