import csv
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Set

from ircm.core.policy import get_policy_value, resolve_reference_date


class ImpactAssessmentAgent:
    """
    Agent D: Impact Assessment

    Reads gap_analysis.json and process_map.csv, identifies impacted
    processes/systems/business units, and writes:
    - impact_assessment.json
    - impact_matrix.csv
    """

    def __init__(self, bundle_dir: Path, run_dir: Path, audit):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = audit
        self.reference_date = resolve_reference_date(bundle_dir)
        self.medium_system_threshold = int(
            get_policy_value(
                "impact",
                "downstream_systems_medium_threshold",
                default=3,
            )
        )
        self.high_system_threshold = int(
            get_policy_value(
                "impact",
                "downstream_systems_high_threshold",
                default=5,
            )
        )

    def run(self) -> None:
        gaps_path = self.run_dir / "gap_analysis.json"
        process_map_path = self.bundle_dir / "process_map.csv"

        impact_json_path = self.run_dir / "impact_assessment.json"
        impact_csv_path = self.run_dir / "impact_matrix.csv"

        if not gaps_path.exists():
            raise FileNotFoundError(f"Missing required input: {gaps_path}")

        if not process_map_path.exists():
            raise FileNotFoundError(
                f"Missing required input: {process_map_path}")

        gap_findings = self._load_json(gaps_path)
        process_rows = self._load_process_map(process_map_path)

        impact_results: List[Dict[str, Any]] = []

        for finding in gap_findings:
            impacted_processes = self._match_processes(finding, process_rows)
            impact_score = self._calculate_impact_score(
                finding, impacted_processes)
            impact_level = self._classify_impact_level(impact_score)

            impacted_systems = self._collect_unique_values(
                impacted_processes, "systems", split_on=";"
            )
            impacted_business_units = self._collect_unique_values(
                impacted_processes, "business_unit"
            )
            impacted_process_ids = [row["process_id"]
                                    for row in impacted_processes]

            result = {
                "impact_id": f"IMP-{finding['finding_id'].split('-')[-1]}",
                "finding_id": finding.get("finding_id"),
                "change_id": finding.get("change_id"),
                "requirement_text": finding.get("requirement_text"),
                "change_type": finding.get("change_type"),
                "domain": finding.get("domain"),
                "severity": finding.get("severity"),
                "coverage_status": finding.get("coverage_status"),
                "effective_date": finding.get("effective_date"),
                "impact_score": impact_score,
                "impact_level": impact_level,
                "system_count": len(impacted_systems),
                "process_count": len(impacted_process_ids),
                "impacted_processes": impacted_process_ids,
                "impacted_systems": impacted_systems,
                "impacted_business_units": impacted_business_units,
                "recommended_owner": self._recommend_owner(impacted_business_units),
                "status": "assessed",
                "evidence_refs": finding.get("evidence_refs", []),
            }

            impact_results.append(result)

        self._write_json(impact_json_path, impact_results)
        self._write_impact_matrix_csv(impact_csv_path, impact_results)

        self.audit.log(
            f"Agent D Impact Assessment completed. "
            f"Created {len(impact_results)} impact record(s). "
            f"Outputs: {impact_json_path}, {impact_csv_path}"
        )

    def _load_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _load_process_map(self, path: Path) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []

        with path.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(
                    {
                        "process_id": row.get("process_id", "").strip(),
                        "process_name": row.get("process_name", "").strip(),
                        "business_unit": row.get("business_unit", "").strip(),
                        "systems": row.get("systems", "").strip(),
                        "criticality": row.get("criticality", "").strip(),
                        "keywords": row.get("keywords", "").strip(),
                    }
                )

        return rows

    def _write_json(self, path: Path, data: Any) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def _write_impact_matrix_csv(self, path: Path, impact_results: List[Dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as file:
            fieldnames = [
                "impact_id",
                "finding_id",
                "change_id",
                "change_type",
                "domain",
                "severity",
                "coverage_status",
                "effective_date",
                "impact_score",
                "impact_level",
                "system_count",
                "process_count",
                "impacted_processes",
                "impacted_systems",
                "impacted_business_units",
                "recommended_owner",
                "status",
            ]

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for result in impact_results:
                writer.writerow(
                    {
                        "impact_id": result["impact_id"],
                        "finding_id": result["finding_id"],
                        "change_id": result["change_id"],
                        "change_type": result["change_type"],
                        "domain": result["domain"],
                        "severity": result["severity"],
                        "coverage_status": result["coverage_status"],
                        "effective_date": result["effective_date"] or "",
                        "impact_score": result["impact_score"],
                        "impact_level": result["impact_level"],
                        "system_count": result["system_count"],
                        "process_count": result["process_count"],
                        "impacted_processes": ";".join(result["impacted_processes"]),
                        "impacted_systems": ";".join(result["impacted_systems"]),
                        "impacted_business_units": ";".join(result["impacted_business_units"]),
                        "recommended_owner": result["recommended_owner"],
                        "status": result["status"],
                    }
                )

    def _match_processes(
        self, finding: Dict[str, Any], process_rows: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        requirement_text = finding.get("requirement_text", "")
        change_type = finding.get("change_type", "")
        domain = finding.get("domain", "")

        requirement_keywords = self._extract_keywords(requirement_text)
        signal_keywords = self._change_type_keywords(change_type, domain)

        matches: List[Dict[str, str]] = []

        for row in process_rows:
            process_keywords = self._extract_keywords(row.get("keywords", ""))
            process_name_keywords = self._extract_keywords(
                row.get("process_name", ""))

            overlap = requirement_keywords.intersection(process_keywords)
            signal_overlap = signal_keywords.intersection(
                process_keywords.union(process_name_keywords))

            if overlap or signal_overlap:
                matches.append(row)

        if matches:
            return matches

        for row in process_rows:
            if domain == "KYC" and "kyc" in row.get("keywords", "").lower():
                matches.append(row)

        return matches

    def _calculate_impact_score(
        self, finding: Dict[str, Any], impacted_processes: List[Dict[str, str]]
    ) -> int:
        severity = finding.get("severity", "medium")
        coverage_status = finding.get("coverage_status", "gap")
        requirement_text = finding.get("requirement_text", "").lower()

        severity_score_map = {
            "high": 45,
            "medium": 30,
            "low": 15,
        }
        score = severity_score_map.get(severity, 30)

        if coverage_status == "gap":
            score += 15
        elif coverage_status == "partially_covered":
            score += 5
        elif coverage_status == "manual_review":
            score += 5

        highest_criticality_bonus = 0
        for process in impacted_processes:
            criticality = process.get("criticality", "").lower()
            if criticality == "high":
                highest_criticality_bonus = max(highest_criticality_bonus, 15)
            elif criticality == "medium":
                highest_criticality_bonus = max(highest_criticality_bonus, 8)

        score += highest_criticality_bonus

        impacted_systems = self._collect_unique_values(
            impacted_processes, "systems", split_on=";"
        )
        impacted_system_count = len(impacted_systems)

        score += min(len(impacted_processes) * 4, 10)

        if impacted_system_count >= self.high_system_threshold:
            score += 15
        elif impacted_system_count >= self.medium_system_threshold:
            score += 8

        if "without delay" in requirement_text:
            score += 10

        if "effective_date" in finding and finding.get("effective_date"):
            effective_date = str(finding.get("effective_date")).strip()

            if effective_date.startswith("within_"):
                score += 10
            else:
                try:
                    effective = date.fromisoformat(effective_date)
                    reference_date = date.fromisoformat(self.reference_date)

                    if effective < reference_date:
                        score += 20
                    elif effective == reference_date:
                        score += 15
                except ValueError:
                    pass

        return min(score, 100)

    def _classify_impact_level(self, impact_score: int) -> str:
        if impact_score >= 70:
            return "high"
        if impact_score >= 40:
            return "medium"
        return "low"

    def _recommend_owner(self, business_units: List[str]) -> str:
        if not business_units:
            return "Compliance"

        if "Compliance" in business_units:
            return "Compliance"

        return business_units[0]

    def _collect_unique_values(
        self, rows: List[Dict[str, str]], key: str, split_on: str = None
    ) -> List[str]:
        values: List[str] = []

        for row in rows:
            raw_value = row.get(key, "").strip()
            if not raw_value:
                continue

            if split_on:
                parts = [part.strip()
                         for part in raw_value.split(split_on) if part.strip()]
                values.extend(parts)
            else:
                values.append(raw_value)

        seen: Set[str] = set()
        ordered_unique: List[str] = []

        for value in values:
            if value not in seen:
                seen.add(value)
                ordered_unique.append(value)

        return ordered_unique

    def _extract_keywords(self, text: str) -> Set[str]:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s;]", " ", text)

        stop_words = {
            "the", "a", "an", "and", "or", "to", "of", "for", "in", "on",
            "with", "by", "is", "are", "be", "this", "that", "must", "shall",
            "required", "requires", "current", "policy", "process", "system",
            "customer", "customers"
        }

        tokens = re.split(r"[\s;]+", text)
        return {token for token in tokens if token and len(token) > 2 and token not in stop_words}

    def _change_type_keywords(self, change_type: str, domain: str) -> Set[str]:
        keywords: Set[str] = set()

        if domain == "KYC":
            keywords.update(
                {"kyc", "identity", "onboarding", "due", "diligence"})

        mapping = {
            "kyc_requirement": {"identity", "verify", "verification", "onboarding"},
            "enhanced_due_diligence_requirement": {"due", "diligence", "risk", "review"},
            "record_retention_requirement": {"records", "storage", "crm"},
            "deadline_requirement": {"compliance", "review", "tracker"},
            "threshold_update": {"review", "risk"},
            "prohibition": {"compliance", "review"},
        }

        keywords.update(mapping.get(change_type, set()))
        return keywords
