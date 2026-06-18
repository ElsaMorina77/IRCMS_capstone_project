import json
from pathlib import Path

from ircm.agents.agent_b_extraction import ExtractionAgent


class DummyAudit:
    def log(self, message: str) -> None:
        pass


def test_agent_b_attaches_threshold_and_effective_date_lines(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    run_dir = tmp_path / "run"
    bundle_dir.mkdir()
    run_dir.mkdir()

    evidence_index = {
        "evidence": [
            {
                "evidence_id": "EV-001",
                "text": "Financial institutions must review cash transactions above 9,000 EUR for enhanced monitoring.",
            },
            {
                "evidence_id": "EV-002",
                "text": "This threshold replaces the previous review threshold of 10,000 EUR.",
            },
            {
                "evidence_id": "EV-003",
                "text": "Banks shall document sanctions screening results in the compliance system.",
            },
            {
                "evidence_id": "EV-004",
                "text": "This requirement became effective on 2026-01-15.",
            },
        ]
    }

    with (run_dir / "evidence_index.json").open("w", encoding="utf-8") as file:
        json.dump(evidence_index, file)

    agent = ExtractionAgent(
        bundle_dir=bundle_dir,
        run_dir=run_dir,
        audit=DummyAudit(),
    )
    agent.run()

    with (run_dir / "extracted_changes.json").open("r", encoding="utf-8") as file:
        extracted_changes = json.load(file)

    assert len(extracted_changes) == 2

    threshold_change = extracted_changes[0]
    assert threshold_change["change_type"] == "threshold_update"
    assert threshold_change["evidence_refs"] == ["EV-001", "EV-002"]

    effective_date_change = extracted_changes[1]
    assert effective_date_change["effective_date"] == "2026-01-15"
    assert effective_date_change["evidence_refs"] == ["EV-003", "EV-004"]
