from datetime import datetime
from pathlib import Path


class AuditLogger:
    """
    Writes simple audit messages to audit_log.md inside the run folder.
    """

    def __init__(self, run_dir: Path):
        self.audit_file = run_dir / "audit_log.md"

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.audit_file, "a", encoding="utf-8") as file:
            file.write(f"- [{timestamp}] {message}\n")