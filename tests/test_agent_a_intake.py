import json
import shutil
import sys
import tempfile
from pathlib import Path


# Make project root importable when running:
# python tests\test_agent_a_intake.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ircm.agents.agent_a_intake import IntakeAgent


class DummyAudit:
    def __init__(self):
        self.messages = []

    def log(self, message: str) -> None:
        self.messages.append(message)


def write_file(path: Path, content: str) -> None:
    path.write_text(content.strip(), encoding="utf-8")


def create_test_bundle(base_dir: Path) -> Path:
    bundle_dir = base_dir / "scenario_test_bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    write_file(
        bundle_dir / "manifest.yaml",
        """
bundle_id: scenario_test_bundle
title: Test Regulatory Bundle
regulation_file: regulation.txt
current_policies_file: current_policies.md
control_inventory_file: control_inventory.csv
process_map_file: process_map.csv
business_units:
  - Compliance
  - Retail Banking
expected_result:
  - gap_detected
  - remediation_required
        """,
    )

    write_file(
        bundle_dir / "regulation.txt",
        """
Banks must verify customer identity before account opening.

Institutions shall perform enhanced due diligence for high-risk customers.

Customer due diligence records must be retained for at least five years.
        """,
    )

    write_file(
        bundle_dir / "current_policies.md",
        """
# Current KYC Policy

The bank verifies customer identity during onboarding.
        """,
    )

    write_file(
        bundle_dir / "control_inventory.csv",
        """
control_id,name,description,owner,business_unit,frequency
CTRL-001,Basic Identity Check,Staff verify customer identity,Compliance,Retail Banking,Daily
        """,
    )

    write_file(
        bundle_dir / "process_map.csv",
        """
process_id,process_name,business_unit,systems,criticality,keywords
PROC-001,Customer Onboarding,Retail Banking,CRM;KYC Portal,High,customer;identity;onboarding
        """,
    )

    return bundle_dir


def test_agent_a_creates_context_packet_and_evidence_index() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        bundle_dir = create_test_bundle(base_dir)
        run_dir = base_dir / "run"
        run_dir.mkdir()

        audit = DummyAudit()

        agent = IntakeAgent(
            bundle_dir=bundle_dir,
            run_dir=run_dir,
            audit=audit,
        )

        result = agent.run()

        context_path = run_dir / "context_packet.json"
        evidence_path = run_dir / "evidence_index.json"

        assert context_path.exists(), "context_packet.json was not created"
        assert evidence_path.exists(), "evidence_index.json was not created"

        context = json.loads(context_path.read_text(encoding="utf-8"))
        evidence_index = json.loads(evidence_path.read_text(encoding="utf-8"))

        assert context["bundle_id"] == "scenario_test_bundle"
        assert context["title"] == "Test Regulatory Bundle"
        assert "Compliance" in context["business_units"]
        assert context["source_files"]["regulation"] == "regulation.txt"

        assert "evidence" in evidence_index
        assert len(evidence_index["evidence"]) == 3

        first_evidence = evidence_index["evidence"][0]

        assert first_evidence["evidence_id"] == "EV-001"
        assert first_evidence["source_file"] == "regulation.txt"
        assert first_evidence["paragraph_number"] == 1
        assert "verify customer identity" in first_evidence["text"].lower()

        # These fields exist if you added OCR/document intake metadata.
        # This keeps the test compatible with both the old and improved Agent A.
        if "source_type" in first_evidence:
            assert first_evidence["source_type"] in ["text", "plain_text"]

        if "ocr_used" in first_evidence:
            assert first_evidence["ocr_used"] is False

        assert result["bundle_id"] == "scenario_test_bundle"
        assert any("Agent A" in message for message in audit.messages)


def test_agent_a_raises_error_when_manifest_is_missing() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        bundle_dir = base_dir / "bundle_without_manifest"
        bundle_dir.mkdir()

        run_dir = base_dir / "run"
        run_dir.mkdir()

        audit = DummyAudit()

        agent = IntakeAgent(
            bundle_dir=bundle_dir,
            run_dir=run_dir,
            audit=audit,
        )

        try:
            agent.run()
            raise AssertionError("Expected FileNotFoundError for missing manifest.yaml")
        except FileNotFoundError as error:
            assert "manifest" in str(error).lower()


def test_agent_a_raises_error_when_required_file_is_missing() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        bundle_dir = create_test_bundle(base_dir)

        # Remove required regulation file.
        (bundle_dir / "regulation.txt").unlink()

        run_dir = base_dir / "run"
        run_dir.mkdir()

        audit = DummyAudit()

        agent = IntakeAgent(
            bundle_dir=bundle_dir,
            run_dir=run_dir,
            audit=audit,
        )

        try:
            agent.run()
            raise AssertionError("Expected FileNotFoundError for missing regulation.txt")
        except FileNotFoundError as error:
            assert "regulation" in str(error).lower()


def test_agent_a_evidence_ids_are_sequential() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        bundle_dir = create_test_bundle(base_dir)
        run_dir = base_dir / "run"
        run_dir.mkdir()

        audit = DummyAudit()

        agent = IntakeAgent(
            bundle_dir=bundle_dir,
            run_dir=run_dir,
            audit=audit,
        )

        agent.run()

        evidence_path = run_dir / "evidence_index.json"
        evidence_index = json.loads(evidence_path.read_text(encoding="utf-8"))

        evidence_ids = [
            item["evidence_id"]
            for item in evidence_index["evidence"]
        ]

        assert evidence_ids == ["EV-001", "EV-002", "EV-003"]


def run_all_tests() -> None:
    print("Running Agent A intake tests...")

    test_agent_a_creates_context_packet_and_evidence_index()
    print("✓ context_packet.json and evidence_index.json test passed")

    test_agent_a_raises_error_when_manifest_is_missing()
    print("✓ missing manifest test passed")

    test_agent_a_raises_error_when_required_file_is_missing()
    print("✓ missing required file test passed")

    test_agent_a_evidence_ids_are_sequential()
    print("✓ sequential evidence IDs test passed")

    print("\nAll Agent A intake tests passed.")


if __name__ == "__main__":
    run_all_tests()