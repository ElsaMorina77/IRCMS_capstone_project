from pathlib import Path

from ircm.agents.agent_a_intake import IntakeAgent
from ircm.agents.agent_b_extraction import ExtractionAgent
from ircm.agents.agent_c_gap_analysis import GapAnalysisAgent
from ircm.agents.agent_d_impact import ImpactAssessmentAgent
from ircm.agents.agent_e_control_mapping import ControlMappingAgent
from ircm.agents.agent_h_triage import TriageAgent
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

        print("[3/6] Agent C Gap Analysis started")
        agent_c = GapAnalysisAgent(
            bundle_dir=self.bundle_dir,
            run_dir=self.run_dir,
            audit=self.audit,
        )
        agent_c.run()
        print("[3/6] Agent C Gap Analysis complete")

        print("[4/6] Agent D Impact Assessment started")
        agent_d = ImpactAssessmentAgent(
            bundle_dir=self.bundle_dir,
            run_dir=self.run_dir,
            audit=self.audit,
        )
        agent_d.run()
        print("[4/6] Agent D Impact Assessment complete")

        print("[5/6] Agent E Control Mapping started")
        agent_e = ControlMappingAgent(
            bundle_dir=self.bundle_dir,
            run_dir=self.run_dir,
            audit=self.audit,
        )
        agent_e.run()
        print("[5/6] Agent E Control Mapping complete")

        print("[6/6] Agent H Triage started")
        agent_h = TriageAgent(
            bundle_dir=self.bundle_dir,
            run_dir=self.run_dir,
            audit=self.audit,
        )
        agent_h.run()
        print("[6/6] Agent H Triage complete")

        self.audit.log("IRCMS pipeline completed.")