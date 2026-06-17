import json
from pathlib import Path

from ircm.agents.agent_b_extraction import ExtractionAgent


class DummyAudit:
    def log(self, message: str) -> None:
        pass


def test_agent_b_ignores_non_mandatory_guidance(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    run_dir = tmp_path / "run"
    bundle_dir.mkdir()
    run_dir.mkdir()

    evidence_index = {
        "evidence": [
            {
                "evidence_id": "EV-001",
                "text": "Regulated institutions should ensure that customer due diligence documentation is written clearly and remains easily understandable for internal reviewers.",
            },
            {
                "evidence_id": "EV-002",
                "text": "This guidance does not introduce new mandatory control obligations.",
            },
            {
                "evidence_id": "EV-003",
                "text": "Institutions are encouraged to maintain clear wording in procedural documents where appropriate.",
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

    assert extracted_changes == []
