import json
from pathlib import Path

import pytest

from ircm.agents.agent_a_intake import IntakeAgent


class DummyAudit:
    def __init__(self):
        self.messages = []

    def log(self, message: str) -> None:
        self.messages.append(message)


def create_test_bundle(tmp_path: Path) -> Path:
    bundle_dir = tmp_path / "scenario_test_bundle"
    bundle_dir.mkdir()

    (bundle_dir / "manifest.yaml").write_text(
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
""".strip(),
        encoding="utf-8",
    )

    (bundle_dir / "regulation.txt").write_text(
        """
Banks must verify customer identity before account opening.

Institutions shall perform enhanced due diligence for high-risk customers.

Customer due diligence records must be retained for at least five years.
""".strip(),
        encoding="utf-8",
    )

    (bundle_dir / "current_policies.md").write_text(
        """
# Current KYC Policy

The bank verifies customer identity during onboarding.
""".strip(),
        encoding="utf-8",
    )

    (bundle_dir / "control_inventory.csv").write_text(
        """
control_id,name,description,owner,business_unit,frequency
CTRL-001,Basic Identity Check,Staff verify customer identity,Compliance,Retail Banking,Daily
""".strip(),
        encoding="utf-8",
    )

    (bundle_dir / "process_map.csv").write_text(
        """
process_id,process_name,business_unit,systems,criticality,keywords
PROC-001,Customer Onboarding,Retail Banking,CRM;KYC Portal,High,customer;identity;onboarding
""".strip(),
        encoding="utf-8",
    )

    return bundle_dir


def test_agent_a_creates_context_packet_and_evidence_index(tmp_path):
    bundle_dir = create_test_bundle(tmp_path)
    run_dir = tmp_path / "run"
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

    assert context_path.exists()
    assert evidence_path.exists()

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

    assert result["bundle_id"] == "scenario_test_bundle"

    assert any("Agent A" in message for message in audit.messages)


def test_agent_a_raises_error_when_manifest_is_missing(tmp_path):
    bundle_dir = tmp_path / "bundle_without_manifest"
    bundle_dir.mkdir()

    run_dir = tmp_path / "run"
    run_dir.mkdir()

    audit = DummyAudit()

    agent = IntakeAgent(
        bundle_dir=bundle_dir,
        run_dir=run_dir,
        audit=audit,
    )

    with pytest.raises(FileNotFoundError, match="manifest"):
        agent.run()


def test_agent_a_raises_error_when_required_bundle_file_is_missing(tmp_path):
    bundle_dir = create_test_bundle(tmp_path)

    missing_file = bundle_dir / "regulation.txt"
    missing_file.unlink()

    run_dir = tmp_path / "run"
    run_dir.mkdir()

    audit = DummyAudit()

    agent = IntakeAgent(
        bundle_dir=bundle_dir,
        run_dir=run_dir,
        audit=audit,
    )

    with pytest.raises(FileNotFoundError, match="regulation"):
        agent.run()


def test_agent_a_evidence_ids_are_sequential(tmp_path):
    bundle_dir = create_test_bundle(tmp_path)
    run_dir = tmp_path / "run"
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