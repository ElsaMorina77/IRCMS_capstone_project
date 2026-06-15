import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Set


class GapAnalysisAgent:
    """
    Agent C: Gap Analysis

    Reads extracted_changes.json and current_policies.md,
    compares regulatory requirements against existing policy text,
    and writes gap_analysis.json.
    """

    def __init__(self, bundle_dir: Path, run_dir: Path, audit):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = audit

    def run(self) -> None:
        changes_path = self.run_dir / "extracted_changes.json"
        policies_path = self.bundle_dir / "current_policies.md"
        output_path = self.run_dir / "gap_analysis.json"

        if not changes_path.exists():
            raise FileNotFoundError(f"Missing required input: {changes_path}")

        if not policies_path.exists():
            raise FileNotFoundError(f"Missing required input: {policies_path}")

        extracted_changes = self._load_json(changes_path)
        policy_text = policies_path.read_text(encoding="utf-8")
        policy_sections = self._split_policy_sections(policy_text)

        gap_findings: List[Dict[str, Any]] = []

        for index, change in enumerate(extracted_changes, start=1):
            requirement_text = change.get("requirement_text", "")
            confidence = float(change.get("confidence", 0))

            best_match = self._find_best_policy_match(
                requirement_text, policy_sections)
            coverage_score = best_match["coverage_score"]
            matched_policy_section = best_match["matched_policy_section"]

            coverage_status = self._classify_coverage(
                coverage_score=coverage_score,
                confidence=confidence,
                matched_policy_section=matched_policy_section,
            )
            severity = self._classify_severity(coverage_status, change)
            recommendation = self._recommend_action(coverage_status, change)

            finding = {
                "finding_id": f"GAP-{index:03d}",
                "change_id": change.get("change_id"),
                "requirement_text": requirement_text,
                "change_type": change.get("change_type"),
                "domain": change.get("domain"),
                "matched_policy_section": matched_policy_section,
                "coverage_score": coverage_score,
                "coverage_status": coverage_status,
                "severity": severity,
                "confidence": confidence,
                "recommendation": recommendation,
                "evidence_refs": change.get("evidence_refs", []),
                "status": (
                    "open"
                    if coverage_status in ["gap", "partially_covered", "manual_review"]
                    else "closed"
                ),
            }

            gap_findings.append(finding)

        self._write_json(output_path, gap_findings)

        self.audit.log(
            f"Agent C Gap Analysis completed. "
            f"Created {len(gap_findings)} gap finding(s). "
            f"Output: {output_path}"
        )

    def _load_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write_json(self, path: Path, data: Any) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def _find_best_policy_match(
        self, requirement_text: str, policy_sections: List[str]
    ) -> Dict[str, Any]:
        requirement_clean = self._normalize_text(requirement_text)

        if not requirement_clean or not policy_sections:
            return {
                "coverage_score": 0,
                "matched_policy_section": "",
            }

        best_score = 0
        best_section = ""

        for section in policy_sections:
            section_clean = self._normalize_text(section)

            if not section_clean:
                continue

            if self._is_negative_policy_statement(section_clean, requirement_clean):
                section_score = 0
            else:
                section_score = self._score_section_match(
                    requirement_clean=requirement_clean,
                    section_clean=section_clean,
                )

            if section_score > best_score:
                best_score = section_score
                best_section = section

        return {
            "coverage_score": best_score,
            "matched_policy_section": best_section,
        }

    def _score_section_match(self, requirement_clean: str, section_clean: str) -> int:
        direct_similarity = SequenceMatcher(
            None, requirement_clean, section_clean
        ).ratio()

        requirement_keywords = self._extract_keywords(requirement_clean)
        section_keywords = self._extract_keywords(section_clean)

        if not requirement_keywords:
            keyword_overlap = 0.0
        else:
            matching_keywords = requirement_keywords.intersection(
                section_keywords)
            keyword_overlap = len(matching_keywords) / \
                len(requirement_keywords)

        obligation_alignment = self._score_obligation_alignment(
            requirement_clean=requirement_clean,
            section_clean=section_clean,
        )

        score = (
            (direct_similarity * 0.25)
            + (keyword_overlap * 0.50)
            + (obligation_alignment * 0.25)
        ) * 100

        return round(score)

    def _score_obligation_alignment(self, requirement_clean: str, section_clean: str) -> float:
        obligation_terms = {
            "verify",
            "verification",
            "identity",
            "due",
            "diligence",
            "records",
            "retain",
            "retention",
            "keep",
            "high",
            "risk",
        }

        requirement_terms = self._extract_keywords(
            requirement_clean).intersection(obligation_terms)
        section_terms = self._extract_keywords(
            section_clean).intersection(obligation_terms)

        if not requirement_terms:
            return 0.0

        overlap = requirement_terms.intersection(section_terms)
        return len(overlap) / len(requirement_terms)

    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_keywords(self, text: str) -> Set[str]:
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "to",
            "of",
            "for",
            "in",
            "on",
            "with",
            "by",
            "is",
            "are",
            "be",
            "this",
            "that",
            "within",
            "must",
            "shall",
            "required",
            "requires",
            "requirement",
            "bank",
            "banks",
            "institution",
            "institutions",
            "financial",
            "current",
            "policy",
            "policies",
            "describe",
            "describes",
            "new",
        }

        words = set(text.split())
        return {word for word in words if len(word) > 3 and word not in stop_words}

    def _classify_coverage(
        self,
        coverage_score: int,
        confidence: float,
        matched_policy_section: str,
    ) -> str:
        if confidence < 0.60:
            return "manual_review"

        if not matched_policy_section:
            return "gap"

        if coverage_score >= 75:
            return "covered"

        if coverage_score >= 30:
            return "partially_covered"

        return "gap"

    def _classify_severity(self, coverage_status: str, change: Dict[str, Any]) -> str:
        change_type = change.get("change_type", "")
        effective_date = change.get("effective_date")

        if coverage_status == "covered":
            return "low"

        if coverage_status == "manual_review":
            return "medium"

        if effective_date:
            return "high"

        if change_type in [
            "kyc_requirement",
            "enhanced_due_diligence_requirement",
            "record_retention_requirement",
        ]:
            return "high" if coverage_status == "gap" else "medium"

        return "medium"

    def _recommend_action(self, coverage_status: str, change: Dict[str, Any]) -> str:
        change_type = change.get("change_type", "requirement")

        if coverage_status == "covered":
            return "No remediation required. Existing policy appears to cover this requirement."

        if coverage_status == "partially_covered":
            return f"Update existing policy language to fully address {change_type}."

        if coverage_status == "manual_review":
            return "Send to compliance/legal review due to low extraction confidence."

        return f"Create or update policy controls to address missing coverage for {change_type}."

    def _split_policy_sections(self, policy_text: str) -> List[str]:
        sections = []

        for line in policy_text.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            sections.append(line)

        return sections

    def _is_negative_policy_statement(self, policy_section: str, requirement_text: str) -> bool:
        negative_phrases = [
            "does not describe",
            "does not include",
            "does not require",
            "not describe",
            "not included",
            "not required",
            "no policy",
            "missing",
        ]

        has_negative_language = any(
            phrase in policy_section for phrase in negative_phrases
        )

        if not has_negative_language:
            return False

        requirement_keywords = self._extract_keywords(requirement_text)
        section_keywords = self._extract_keywords(policy_section)

        if not requirement_keywords:
            return False

        overlap = len(requirement_keywords.intersection(section_keywords))

        return overlap >= 2
