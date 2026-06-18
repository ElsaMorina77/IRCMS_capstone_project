from pathlib import Path


class AuditLogger:
    """
    Writes simple audit messages to audit_log.md inside the run folder.
    """

    def __init__(self, run_dir: Path):
        self.audit_file = run_dir / "audit_log.md"
        self.sequence = 0
        self.audit_file.write_text("", encoding="utf-8")

    def log(self, message: str) -> None:
        self.sequence += 1

        with open(self.audit_file, "a", encoding="utf-8") as file:
            file.write(f"- [{self.sequence:03d}] {message}\n")
