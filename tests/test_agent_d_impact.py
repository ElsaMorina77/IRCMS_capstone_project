import json
from pathlib import Path

from ircm.agents.agent_d_impact import ImpactAssessmentAgent


class DummyAudit:
    def log(self, message: str) -> None:
        pass


def test_agent_d_increases_impact_for_overdue_effective_date(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    run_dir = tmp_path / "run"
    bundle_dir.mkdir()
    run_dir.mkdir()

    gap_analysis = [
        {
            "finding_id": "GAP-001",
            "change_id": "CHG-001",
            "requirement_text": "Banks shall document sanctions screening results in the compliance system.",
            "change_type": "general_regulatory_requirement",
            "domain": "General Compliance",
            "effective_date": "2026-01-15",
            "coverage_status": "gap",
            "severity": "high",
            "evidence_refs": ["EV-001"],
        }
    ]

    process_map = """process_id,process_name,business_unit,systems,criticality,keywords
PROC-001,Sanctions Screening,Compliance,Screening Engine;Compliance Tracker;Document Repository,high,sanctions screening compliance documentation
"""

    with (run_dir / "gap_analysis.json").open("w", encoding="utf-8") as file:
        json.dump(gap_analysis, file)

    with (bundle_dir / "process_map.csv").open("w", encoding="utf-8") as file:
        file.write(process_map)

    agent = ImpactAssessmentAgent(
        bundle_dir=bundle_dir,
        run_dir=run_dir,
        audit=DummyAudit(),
    )
    agent.run()

    with (run_dir / "impact_assessment.json").open("r", encoding="utf-8") as file:
        impact_results = json.load(file)

    assert len(impact_results) == 1

    result = impact_results[0]
    assert result["effective_date"] == "2026-01-15"
    assert result["impact_level"] == "high"
    assert result["impact_score"] >= 80
