import csv
import json
from pathlib import Path
from difflib import SequenceMatcher


class ControlMappingAgent:
    """
    Agent E - Control Mapping.

    This agent maps extracted regulatory changes to existing controls.

    Input:
    - runs/<run_id>/extracted_changes.json
    - bundles/<scenario>/control_inventory.csv

    Output:
    - runs/<run_id>/control_mapping.json
    """

    def __init__(self, bundle_dir: Path, run_dir: Path, audit=None):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = audit

    def run(self) -> dict:
        self.log("Agent E Control Mapping started.")

        extracted_changes = self.load_extracted_changes()
        controls = self.load_control_inventory()

        mappings = []

        for change in extracted_changes:
            best_match = self.find_best_control_match(change, controls)
            mappings.append(best_match)

        output = {
            "agent": "Agent E - Control Mapping",
            "total_changes": len(extracted_changes),
            "total_controls": len(controls),
            "mappings": mappings,
        }

        self.write_json("control_mapping.json", output)

        self.log(f"Agent E mapped {len(mappings)} regulatory changes to controls.")
        self.log("Agent E Control Mapping completed.")

        return output

    def load_extracted_changes(self) -> list:
        input_path = self.run_dir / "extracted_changes.json"

        if not input_path.exists():
            raise FileNotFoundError(
                f"Missing extracted_changes.json. Agent B must run before Agent E. Path: {input_path}"
            )

        with open(input_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict) and "changes" in data:
            return data["changes"]

        if isinstance(data, list):
            return data

        raise ValueError("Invalid extracted_changes.json format. Expected key: 'changes'.")

    def load_control_inventory(self) -> list:
        control_path = self.bundle_dir / "control_inventory.csv"

        if not control_path.exists():
            raise FileNotFoundError(f"Missing control inventory file: {control_path}")

        controls = []

        with open(control_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                controls.append(
                    {
                        "control_id": row.get("control_id", "").strip(),
                        "name": row.get("name", "").strip(),
                        "description": row.get("description", "").strip(),
                        "owner": row.get("owner", "").strip(),
                        "business_unit": row.get("business_unit", "").strip(),
                        "frequency": row.get("frequency", "").strip(),
                    }
                )

        if not controls:
            raise ValueError("control_inventory.csv is empty or invalid.")

        return controls

    def find_best_control_match(self, change: dict, controls: list) -> dict:
        requirement_text = change.get("requirement_text", "")
        change_id = change.get("change_id", "UNKNOWN")
        evidence_refs = change.get("evidence_refs", [])

        best_control = None
        best_score = 0.0

        for control in controls:
            score = self.calculate_control_score(requirement_text, control)

            if score > best_score:
                best_score = score
                best_control = control

        coverage_status = self.determine_coverage_status(best_score)
        missing_elements = self.identify_missing_elements(
            requirement_text=requirement_text,
            best_score=best_score,
            coverage_status=coverage_status,
        )

        if best_control is None or coverage_status == "missing":
            return {
                "change_id": change_id,
                "control_id": None,
                "control_name": None,
                "coverage_status": "missing",
                "coverage_score": round(best_score, 2),
                "missing_elements": missing_elements,
                "recommended_action": "Create a new control to address this regulatory requirement.",
                "evidence_refs": evidence_refs,
            }

        return {
            "change_id": change_id,
            "control_id": best_control["control_id"],
            "control_name": best_control["name"],
            "coverage_status": coverage_status,
            "coverage_score": round(best_score, 2),
            "missing_elements": missing_elements,
            "recommended_action": self.create_recommended_action(coverage_status),
            "evidence_refs": evidence_refs,
        }

    def calculate_control_score(self, requirement_text: str, control: dict) -> float:
        """
        Calculates a simple matching score between a regulatory requirement
        and an existing control.

        Score is based on:
        - text similarity
        - shared keywords
        - domain-related words
        """

        control_text = " ".join(
            [
                control.get("name", ""),
                control.get("description", ""),
                control.get("business_unit", ""),
            ]
        )

        similarity_score = self.text_similarity(requirement_text, control_text) * 100
        keyword_score = self.keyword_overlap_score(requirement_text, control_text)

        final_score = (similarity_score * 0.65) + (keyword_score * 0.35)

        return min(final_score, 100.0)

    def text_similarity(self, text_a: str, text_b: str) -> float:
        text_a = text_a.lower().strip()
        text_b = text_b.lower().strip()

        if not text_a or not text_b:
            return 0.0

        return SequenceMatcher(None, text_a, text_b).ratio()

    def keyword_overlap_score(self, text_a: str, text_b: str) -> float:
        words_a = self.extract_keywords(text_a)
        words_b = self.extract_keywords(text_b)

        if not words_a or not words_b:
            return 0.0

        overlap = words_a.intersection(words_b)
        return (len(overlap) / len(words_a)) * 100

    def extract_keywords(self, text: str) -> set:
        stop_words = {
            "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "by",
            "with", "must", "shall", "should", "is", "are", "be", "before",
            "after", "within", "at", "least", "this", "that", "as"
        }

        words = text.lower().replace(".", " ").replace(",", " ").replace(";", " ").split()

        keywords = {
            word.strip()
            for word in words
            if len(word.strip()) > 2 and word.strip() not in stop_words
        }

        return keywords

    def determine_coverage_status(self, score: float) -> str:
        if score >= 75:
            return "full"
        if score >= 45:
            return "partial"
        return "missing"

    def identify_missing_elements(
        self,
        requirement_text: str,
        best_score: float,
        coverage_status: str,
    ) -> list:
        requirement_lower = requirement_text.lower()
        missing = []

        if coverage_status == "full":
            return []

        if coverage_status == "missing":
            missing.append("No existing control sufficiently matches this requirement.")

        if "enhanced" in requirement_lower:
            missing.append("Enhanced due diligence is not clearly covered.")

        if "high-risk" in requirement_lower or "high risk" in requirement_lower:
            missing.append("High-risk customer handling is not fully documented.")

        if "within" in requirement_lower or "days" in requirement_lower:
            missing.append("Implementation deadline is not reflected in the existing control.")

        if "record" in requirement_lower or "retain" in requirement_lower:
            missing.append("Record retention requirement may need stronger control evidence.")

        if not missing and best_score < 75:
            missing.append("Existing control only partially covers the requirement.")

        return missing

    def create_recommended_action(self, coverage_status: str) -> str:
        if coverage_status == "full":
            return "No new control required. Existing control appears sufficient."

        if coverage_status == "partial":
            return "Update the existing control to fully cover the new regulatory requirement."

        return "Create a new control to address this regulatory requirement."

    def write_json(self, filename: str, data: dict) -> None:
        output_path = self.run_dir / filename

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def log(self, message: str) -> None:
        if self.audit:
            self.audit.log(message)