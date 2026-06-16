from pathlib import Path


class TriageAgent:
    """
    Agent H - Triage and final reporting.

    This is only a placeholder for now.
    Later it will read outputs from Agents B, C, D, and E
    and create final reports.
    """

    def __init__(self, bundle_dir: Path, run_dir: Path, audit):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = audit

    def run(self) -> None:
        self.audit.log("Agent H Triage started.")

        self.create_placeholder_remediation_plan()
        self.create_placeholder_exceptions_file()
        self.create_placeholder_metrics_file()

        self.audit.log("Agent H created placeholder final reports.")
        self.audit.log("Agent H Triage completed.")

    def create_placeholder_remediation_plan(self) -> None:
        output_path = self.run_dir / "remediation_plan.md"

        content = """# Remediation Plan

This is a placeholder remediation plan.

Final remediation actions will be generated after Agents B, C, D, and E are implemented.
"""

        output_path.write_text(content, encoding="utf-8")

    def create_placeholder_exceptions_file(self) -> None:
        output_path = self.run_dir / "exceptions.md"

        content = """# Exceptions Report

No exceptions generated yet.

This file will be updated when full triage logic is implemented.
"""

        output_path.write_text(content, encoding="utf-8")

    def create_placeholder_metrics_file(self) -> None:
        output_path = self.run_dir / "metrics.json"

        content = """{
    "status": "placeholder",
    "agents_completed": ["Agent A", "Agent H"],
    "message": "Full metrics will be available after all agents are implemented."
}
"""

        output_path.write_text(content, encoding="utf-8")