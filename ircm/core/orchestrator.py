from pathlib import Path

from ircm.agents.agent_a_intake import IntakeAgent
from ircm.agents.agent_h_triage import TriageAgent
from ircm.agents.agent_b_extraction import ExtractionAgent
from ircm.core.audit import AuditLogger


class Orchestrator:
    """
    Runs the IRCMS pipeline in the correct order.
    """

    def __init__(self, bundle_dir: Path, run_dir: Path):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = AuditLogger(run_dir)

    def run_pipeline(self) -> None:
        self.audit.log("IRCMS pipeline started.")

        print("[1/6] Agent A Intake started")
        agent_a = IntakeAgent(
            bundle_dir=self.bundle_dir,
            run_dir=self.run_dir,
            audit=self.audit,
        )
        agent_a.run()
        print("[1/6] Agent A Intake complete")

        print("[2/6] Agent B Extraction started")
        agent_b = ExtractionAgent(
            bundle_dir=self.bundle_dir,
            run_dir=self.run_dir,
            audit=self.audit,
        )
        agent_b.run()
        print("[2/6] Agent B Extraction complete")

        print("[3/6] Agent C Gap Analysis - waiting for teammate")
        self.audit.log(
            "Agent C Gap Analysis skipped: teammate implementation pending.")

        print("[4/6] Agent D Impact Assessment - waiting for teammate")
        self.audit.log(
            "Agent D Impact Assessment skipped: teammate implementation pending.")

        print("[5/6] Agent E Control Mapping - waiting for teammate")
        self.audit.log(
            "Agent E Control Mapping skipped: teammate implementation pending.")

        print("[6/6] Agent H Triage started")
        agent_h = TriageAgent(
            bundle_dir=self.bundle_dir,
            run_dir=self.run_dir,
            audit=self.audit,
        )
        agent_h.run()
        print("[6/6] Agent H Triage complete")

        self.audit.log("IRCMS pipeline completed.")
