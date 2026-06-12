from pathlib import Path


class Orchestrator:
    def __init__(self, bundle_dir: Path, run_dir: Path):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir

    def run_pipeline(self):
        print("[1/6] Agent A Intake - placeholder")
        print("[2/6] Agent B Extraction - placeholder")
        print("[3/6] Agent C Gap Analysis - placeholder")
        print("[4/6] Agent D Impact Assessment - placeholder")
        print("[5/6] Agent E Control Mapping - placeholder")
        print("[6/6] Agent H Triage - placeholder")