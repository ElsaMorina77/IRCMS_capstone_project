import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


MANDATORY_KEYWORDS = [
    "must",
    "shall",
    "required",
    "requires",
    "prohibited",
    "effective",
    "within",
    "deadline",
    "threshold",
    "verify",
    "verification",
    "customer identity",
    "kyc",
]

NON_MANDATORY_KEYWORDS = [
    "should",
    "encouraged",
    "guidance",
    "recommended",
    "may",
    "where appropriate",
]

NON_MANDATORY_PHRASES = [
    "does not introduce new mandatory control obligations",
    "does not introduce new mandatory obligations",
    "for internal reviewers",
    "written clearly",
    "easily understandable",
    "clear wording",
]

DEADLINE_ONLY_PATTERNS = [
    r"\bthis requirement becomes effective within \d+ days\b",
    r"\bthis requirement became effective within \d+ days\b",
    r"\beffective within \d+ days\b",
    r"\bthis requirement became effective on\b",
    r"\bthis requirement becomes effective on\b",
    r"\bbecame effective on\b",
    r"\beffective on\b",
    r"\bcomes into force on\b",
    r"\bmust be implemented within \d+ days\b",
]

THRESHOLD_UPDATE_ONLY_PATTERNS = [
    r"\bthis threshold replaces\b",
    r"\breplaces the previous review threshold\b",
    r"\breplaces the previous threshold\b",
    r"\bthe previous review threshold of\b",
]


class ExtractionAgent:
    """
    Agent B: Change Extraction

    Reads evidence_index.json from the run folder and extracts
    regulatory requirement changes into extracted_changes.json.
    """

    def __init__(self, bundle_dir: Path, run_dir: Path, audit):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = audit

    def run(self) -> None:
        evidence_path = self.run_dir / "evidence_index.json"
        output_path = self.run_dir / "extracted_changes.json"

        if not evidence_path.exists():
            raise FileNotFoundError(f"Missing required input: {evidence_path}")

        evidence_items = self._load_json(evidence_path)
        evidence_items = self._normalize_evidence_items(evidence_items)

        extracted_changes: List[Dict[str, Any]] = []

        for index, item in enumerate(evidence_items, start=1):
            evidence_id = item.get("evidence_id") or item.get(
                "id") or f"EV-{index:03d}"
            text = (
                item.get("text")
                or item.get("content")
                or item.get("paragraph")
                or item.get("source_text")
                or ""
            ).strip()

            if not text:
                continue

            if self._is_explicitly_non_mandatory(text):
                continue

            if self._is_deadline_only_statement(text):
                self._attach_deadline_to_previous_change(
                    extracted_changes=extracted_changes,
                    text=text,
                    evidence_id=evidence_id,
                )
                continue

            if self._is_threshold_update_only_statement(text):
                self._attach_threshold_update_to_previous_change(
                    extracted_changes=extracted_changes,
                    evidence_id=evidence_id,
                )
                continue

            if not self._is_requirement(text):
                continue

            change = {
                "change_id": f"CHG-{len(extracted_changes) + 1:03d}",
                "requirement_text": text,
                "change_type": self._detect_change_type(text),
                "domain": self._detect_domain(text),
                "jurisdiction": self._detect_jurisdiction(text),
                "effective_date": self._extract_effective_date(text),
                "confidence": self._score_confidence(text, evidence_id),
                "evidence_refs": [evidence_id],
                "status": "extracted",
            }

            extracted_changes.append(change)

        self._write_json(output_path, extracted_changes)

        self.audit.log(
            f"Agent B Extraction completed. "
            f"Extracted {len(extracted_changes)} change(s). "
            f"Output: {output_path}"
        )

    def _load_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write_json(self, path: Path, data: Any) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def _normalize_evidence_items(self, evidence_data: Any) -> List[Dict[str, Any]]:
        if isinstance(evidence_data, list):
            return evidence_data

        if isinstance(evidence_data, dict):
            for key in ["evidence", "evidence_index", "items", "paragraphs"]:
                if key in evidence_data and isinstance(evidence_data[key], list):
                    return evidence_data[key]

        raise ValueError("Unsupported evidence_index.json format.")

    def _is_explicitly_non_mandatory(self, text: str) -> bool:
        text_lower = text.lower()

        has_non_mandatory_phrase = any(
            phrase in text_lower for phrase in NON_MANDATORY_PHRASES
        )
        has_non_mandatory_language = any(
            keyword in text_lower for keyword in NON_MANDATORY_KEYWORDS
        )
        has_mandatory_language = any(
            keyword in text_lower for keyword in MANDATORY_KEYWORDS
        )

        if has_mandatory_language:
            return False

        if has_non_mandatory_phrase:
            return True

        if has_non_mandatory_language:
            return True

        return False

    def _is_requirement(self, text: str) -> bool:
        text_lower = text.lower()

        if self._is_explicitly_non_mandatory(text):
            return False

        if any(keyword in text_lower for keyword in MANDATORY_KEYWORDS):
            return True

        obligation_patterns = [
            r"\bfinancial institutions\b",
            r"\bbanks\b",
            r"\binstitutions\b",
            r"\bcustomers?\b",
            r"\bdue diligence\b",
            r"\brecords?\b",
        ]

        return any(re.search(pattern, text_lower) for pattern in obligation_patterns)

    def _is_deadline_only_statement(self, text: str) -> bool:
        text_lower = text.lower().strip()
        return any(re.search(pattern, text_lower) for pattern in DEADLINE_ONLY_PATTERNS)

    def _is_threshold_update_only_statement(self, text: str) -> bool:
        text_lower = text.lower().strip()
        return any(re.search(pattern, text_lower) for pattern in THRESHOLD_UPDATE_ONLY_PATTERNS)

    def _attach_deadline_to_previous_change(
        self,
        extracted_changes: List[Dict[str, Any]],
        text: str,
        evidence_id: str,
    ) -> None:
        if not extracted_changes:
            return

        effective_date = self._extract_effective_date(text)
        if not effective_date:
            return

        previous_change = extracted_changes[-1]
        previous_change["effective_date"] = effective_date

        if evidence_id not in previous_change["evidence_refs"]:
            previous_change["evidence_refs"].append(evidence_id)

        previous_change["confidence"] = min(
            round(previous_change["confidence"] + 0.05, 2),
            1.0,
        )

    def _attach_threshold_update_to_previous_change(
        self,
        extracted_changes: List[Dict[str, Any]],
        evidence_id: str,
    ) -> None:
        if not extracted_changes:
            return

        previous_change = extracted_changes[-1]
        previous_change["change_type"] = "threshold_update"

        if evidence_id not in previous_change["evidence_refs"]:
            previous_change["evidence_refs"].append(evidence_id)

        previous_change["confidence"] = min(
            round(previous_change["confidence"] + 0.05, 2),
            1.0,
        )

    def _detect_change_type(self, text: str) -> str:
        text_lower = text.lower()

        if any(
            word in text_lower
            for word in ["record", "records", "retain", "retention", "keep", "storage"]
        ):
            return "record_retention_requirement"

        if any(
            phrase in text_lower
            for phrase in [
                "enhanced customer due diligence",
                "enhanced due diligence",
                "high-risk customers",
                "high risk customers",
            ]
        ):
            return "enhanced_due_diligence_requirement"

        if any(
            phrase in text_lower
            for phrase in [
                "escalate suspicious",
                "alerts to the compliance function",
                "escalation",
                "compliance function for review",
            ]
        ):
            return "alert_escalation_requirement"

        if any(
            phrase in text_lower
            for phrase in [
                "suspicious transaction",
                "suspicious activity",
                "transaction monitoring",
                "monitor customer transactions",
                "monitor transactions",
            ]
        ):
            return "transaction_monitoring_requirement"

        if any(
            word in text_lower
            for word in ["kyc", "customer identity", "verification", "verify"]
        ):
            return "kyc_requirement"

        if "threshold" in text_lower:
            return "threshold_update"

        if (
            "prohibited" in text_lower
            or "not allowed" in text_lower
            or re.search(r"\bban\b", text_lower)
            or re.search(r"\bbanned\b", text_lower)
        ):
            return "prohibition"

        if any(word in text_lower for word in ["effective", "within", "deadline"]):
            return "deadline_requirement"

        return "general_regulatory_requirement"

    def _detect_domain(self, text: str) -> str:
        text_lower = text.lower()

        if any(
            phrase in text_lower
            for phrase in [
                "kyc",
                "customer identity",
                "verification",
                "customer due diligence",
                "high-risk customers",
            ]
        ):
            return "KYC"

        if any(
            phrase in text_lower
            for phrase in [
                "aml",
                "money laundering",
                "suspicious transaction",
                "suspicious activity",
                "transaction monitoring",
                "alerts",
                "compliance function",
            ]
        ):
            return "AML"

        if any(
            word in text_lower
            for word in ["records", "retention", "effective", "deadline"]
        ):
            return "General Compliance"

        return "General Compliance"

    def _detect_jurisdiction(self, text: str) -> str:
        text_lower = text.lower()

        if re.search(r"\b(switzerland|swiss)\b", text_lower):
            return "Switzerland"

        if re.search(r"\b(eu|european union)\b", text_lower):
            return "EU"

        if re.search(r"\b(uk|united kingdom)\b", text_lower):
            return "UK"

        if re.search(r"\b(us|u\.s\.|usa|united states)\b", text_lower):
            return "US"

        return "Unknown"

    def _extract_effective_date(self, text: str) -> Optional[str]:
        text_lower = text.lower()

        within_days_match = re.search(r"within\s+(\d+)\s+days", text_lower)
        if within_days_match:
            return f"within_{within_days_match.group(1)}_days"

        iso_date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)
        if iso_date_match:
            return iso_date_match.group(0)

        slash_date_match = re.search(r"\b\d{1,2}/\d{1,2}/\d{4}\b", text)
        if slash_date_match:
            return slash_date_match.group(0)

        long_date_match = re.search(
            r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},\s+\d{4}\b",
            text_lower,
        )
        if long_date_match:
            return long_date_match.group(0)

        return None

    def _score_confidence(self, text: str, evidence_id: str) -> float:
        text_lower = text.lower()
        score = 0.30

        if any(word in text_lower for word in ["must", "shall", "required", "requires"]):
            score += 0.25

        if any(word in text_lower for word in ["effective", "within", "deadline"]):
            score += 0.15

        if any(
            word in text_lower
            for word in ["kyc", "customer", "identity", "verification", "due diligence"]
        ):
            score += 0.15

        if any(
            word in text_lower
            for word in ["record", "records", "retention", "retain", "keep"]
        ):
            score += 0.10

        if evidence_id:
            score += 0.10

        return min(round(score, 2), 1.0)
