import csv
import json
from pathlib import Path
from datetime import datetime


class TriageAgent:
    """
    Agent H - Final Triage and Reporting.

    This agent produces final MVP reports from outputs created by previous agents.

    Inputs, if available:
    - extracted_changes.json
    - gap_analysis.json
    - impact_matrix.csv
    - control_mapping.json

    Outputs:
    - change_register.json
    - remediation_plan.md
    - exceptions.md
    - approval_packet.json
    - metrics.json

    The agent is safe for MVP:
    - It does not require pandas or pydantic.
    - It does not crash if B/C/D/E outputs are missing.
    - It creates useful placeholder-aware final reports.
    """

    def __init__(self, bundle_dir: Path, run_dir: Path, audit=None):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = audit

    def run(self) -> dict:
        self.log("Agent H Final Triage started.")

        changes = self.load_json_list("extracted_changes.json", "changes")
        gaps = self.load_json_list("gap_analysis.json", "findings")
        impacts = self.load_csv_rows("impact_matrix.csv")
        mappings = self.load_json_list("control_mapping.json", "mappings")

        change_register = self.build_change_register(
            changes=changes,
            gaps=gaps,
            impacts=impacts,
            mappings=mappings,
        )

        metrics = self.calculate_metrics(change_register)
        remediation_actions = self.build_remediation_actions(change_register)
        exceptions = self.build_exceptions(change_register)
        approval_packet = self.build_approval_packet(
            change_register=change_register,
            metrics=metrics,
            exceptions=exceptions,
        )

        self.write_json("change_register.json", {"changes": change_register})
        self.write_json("metrics.json", metrics)
        self.write_json("approval_packet.json", approval_packet)
        self.write_remediation_plan(remediation_actions, metrics)
        self.write_exceptions_report(exceptions, metrics)

        self.log("Agent H created change_register.json.")
        self.log("Agent H created remediation_plan.md.")
        self.log("Agent H created exceptions.md.")
        self.log("Agent H created approval_packet.json.")
        self.log("Agent H created metrics.json.")
        self.log("Agent H Final Triage completed.")

        return {
            "change_register": change_register,
            "metrics": metrics,
            "remediation_actions": remediation_actions,
            "exceptions": exceptions,
            "approval_packet": approval_packet,
        }

    def load_json_list(self, filename: str, list_key: str) -> list:
        file_path = self.run_dir / filename

        if not file_path.exists():
            self.log(
                f"Agent H warning: {filename} not found. Continuing with empty data.")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                value = data.get(list_key, [])
                return value if isinstance(value, list) else []

            if isinstance(data, list):
                return data

            return []

        except Exception as error:
            self.log(f"Agent H warning: Could not read {filename}: {error}")
            return []

    def load_csv_rows(self, filename: str) -> list:
        file_path = self.run_dir / filename

        if not file_path.exists():
            self.log(
                f"Agent H warning: {filename} not found. Continuing with empty data.")
            return []

        try:
            with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                return list(reader)

        except Exception as error:
            self.log(f"Agent H warning: Could not read {filename}: {error}")
            return []

    def build_change_register(self, changes: list, gaps: list, impacts: list, mappings: list) -> list:
        change_ids = set()

        for item in changes:
            if item.get("change_id"):
                change_ids.add(item["change_id"])

        for item in gaps:
            if item.get("change_id"):
                change_ids.add(item["change_id"])

        for item in impacts:
            if item.get("change_id"):
                change_ids.add(item["change_id"])

        for item in mappings:
            if item.get("change_id"):
                change_ids.add(item["change_id"])

        if not change_ids:
            return []

        register = []

        for change_id in sorted(change_ids):
            change = self.find_by_change_id(changes, change_id)
            gap = self.find_by_change_id(gaps, change_id)
            impact = self.find_by_change_id(impacts, change_id)
            mapping = self.find_by_change_id(mappings, change_id)

            risk_level = (
                self.get_value(impact, "risk_level", None)
                or self.get_value(impact, "impact_level", "unknown")
            )

            impact_score = self.safe_float(
                self.get_value(impact, "impact_score", 0))

            business_unit = (
                self.get_value(impact, "business_unit", None)
                or self.get_value(impact, "impacted_business_units", "unknown")
            )

            process_name = (
                self.get_value(impact, "process_name", None)
                or self.get_value(impact, "impacted_processes", "unknown")
            )

            coverage_status = self.get_value(
                mapping, "coverage_status", "unknown")
            coverage_score = self.safe_float(
                self.get_value(mapping, "coverage_score", 0))
            confidence = self.safe_float(self.get_value(
                change, "confidence", self.get_value(gap, "confidence", 0)))
            final_status = self.determine_final_status(
                gap=gap,
                risk_level=risk_level,
                impact_score=impact_score,
                coverage_status=coverage_status,
                confidence=confidence,
            )

            register.append(
                {
                    "change_id": change_id,
                    "requirement_text": self.get_value(change, "requirement_text", ""),
                    "change_type": self.get_value(change, "change_type", "unknown"),
                    "domain": self.get_value(change, "domain", "unknown"),
                    "confidence": confidence,
                    "gap_status": self.get_value(gap, "coverage_status", "unknown"),
                    "gap_severity": self.get_value(gap, "severity", "unknown"),
                    "business_unit": business_unit,
                    "process_name": process_name,
                    "impact_score": impact_score,
                    "risk_level": risk_level,
                    "control_id": self.get_value(mapping, "control_id", None),
                    "control_name": self.get_value(mapping, "control_name", None),
                    "control_coverage_status": coverage_status,
                    "control_coverage_score": coverage_score,
                    "recommended_action": self.build_recommended_action(gap, mapping, final_status),
                    "final_status": final_status,
                    "evidence_refs": self.get_evidence_refs(change, gap, mapping),
                }
            )

        return register

    def determine_final_status(
        self,
        gap: dict,
        risk_level: str,
        impact_score: float,
        coverage_status: str,
        confidence: float,
    ) -> str:
        risk_level_lower = str(risk_level).lower()
        coverage_lower = str(coverage_status).lower()

        if confidence < 0.7:
            return "legal_review_required"

        if impact_score >= 70 or risk_level_lower == "high":
            return "compliance_review_required"

        if coverage_lower == "missing":
            return "new_control_required"

        if coverage_lower == "partial":
            return "control_update_required"

        if gap and str(gap.get("severity", "")).lower() in ["high", "medium"]:
            return "remediation_required"

        return "monitor"

    def build_recommended_action(self, gap: dict, mapping: dict, final_status: str) -> str:
        if mapping and mapping.get("recommended_action"):
            return mapping["recommended_action"]

        if gap and gap.get("recommendation"):
            return gap["recommendation"]

        action_map = {
            "legal_review_required": "Send this change to legal or compliance review due to low confidence.",
            "compliance_review_required": "Escalate this change to compliance for review and approval.",
            "new_control_required": "Create a new control to address the regulatory requirement.",
            "control_update_required": "Update the existing control to fully cover the requirement.",
            "remediation_required": "Create a remediation action to close the identified gap.",
            "monitor": "No urgent remediation required. Continue monitoring.",
        }

        return action_map.get(final_status, "Review this change manually.")

    def calculate_metrics(self, change_register: list) -> dict:
        total_changes = len(change_register)

        total_gaps = 0
        high_risk_items = 0
        exceptions = 0
        remediation_required = 0

        for item in change_register:
            final_status = item.get("final_status", "")
            risk_level = str(item.get("risk_level", "")).lower()
            gap_severity = str(item.get("gap_severity", "")).lower()
            control_status = str(
                item.get("control_coverage_status", "")).lower()

            if gap_severity in ["medium", "high"] or control_status in ["partial", "missing"]:
                total_gaps += 1

            if risk_level == "high" or item.get("impact_score", 0) >= 70:
                high_risk_items += 1

            if final_status in ["legal_review_required", "compliance_review_required"]:
                exceptions += 1

            if final_status in ["new_control_required", "control_update_required", "remediation_required"]:
                remediation_required += 1

        pipeline_status = "completed"

        if exceptions > 0:
            pipeline_status = "review_required"
        elif remediation_required > 0:
            pipeline_status = "remediation_required"
        elif total_changes == 0:
            pipeline_status = "completed_with_missing_upstream_outputs"

        return {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_changes": total_changes,
            "total_gaps": total_gaps,
            "high_risk_items": high_risk_items,
            "remediation_required": remediation_required,
            "exceptions": exceptions,
            "pipeline_status": pipeline_status,
        }

    def build_remediation_actions(self, change_register: list) -> list:
        actions = []

        for index, item in enumerate(change_register, start=1):
            if item["final_status"] in [
                "new_control_required",
                "control_update_required",
                "remediation_required",
                "compliance_review_required",
                "legal_review_required",
            ]:
                actions.append(
                    {
                        "action_id": f"ACT-{index:03}",
                        "change_id": item["change_id"],
                        "owner": self.determine_owner(item),
                        "priority": self.determine_priority(item),
                        "action": item["recommended_action"],
                        "status": "open",
                        "evidence_refs": item.get("evidence_refs", []),
                    }
                )

        return actions

    def build_exceptions(self, change_register: list) -> list:
        exceptions = []

        for index, item in enumerate(change_register, start=1):
            if item["final_status"] in ["legal_review_required", "compliance_review_required"]:
                exceptions.append(
                    {
                        "exception_id": f"EXC-{index:03}",
                        "change_id": item["change_id"],
                        "reason": self.build_exception_reason(item),
                        "risk_level": item.get("risk_level", "unknown"),
                        "required_review": self.required_review_type(item),
                        "evidence_refs": item.get("evidence_refs", []),
                    }
                )

        return exceptions

    def build_approval_packet(self, change_register: list, metrics: dict, exceptions: list) -> dict:
        scenario_name = self.bundle_dir.name

        return {
            "scenario": scenario_name,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "final_status": metrics["pipeline_status"],
            "summary": {
                "total_changes": metrics["total_changes"],
                "total_gaps": metrics["total_gaps"],
                "high_risk_items": metrics["high_risk_items"],
                "remediation_required": metrics["remediation_required"],
                "exceptions": metrics["exceptions"],
            },
            "recommendation": self.build_final_recommendation(metrics),
            "changes_requiring_review": [
                item["change_id"]
                for item in change_register
                if item["final_status"] in ["legal_review_required", "compliance_review_required"]
            ],
            "exceptions": exceptions,
        }

    def write_remediation_plan(self, actions: list, metrics: dict) -> None:
        output_path = self.run_dir / "remediation_plan.md"

        lines = [
            "# Remediation Plan",
            "",
            "## Summary",
            "",
            f"- Total changes: {metrics['total_changes']}",
            f"- Total gaps: {metrics['total_gaps']}",
            f"- High-risk items: {metrics['high_risk_items']}",
            f"- Remediation required: {metrics['remediation_required']}",
            f"- Exceptions: {metrics['exceptions']}",
            f"- Pipeline status: {metrics['pipeline_status']}",
            "",
            "## Required Actions",
            "",
        ]

        if not actions:
            lines.append("No remediation actions were generated.")
        else:
            for action in actions:
                lines.extend(
                    [
                        f"### {action['action_id']}",
                        "",
                        f"- Change ID: {action['change_id']}",
                        f"- Owner: {action['owner']}",
                        f"- Priority: {action['priority']}",
                        f"- Status: {action['status']}",
                        f"- Action: {action['action']}",
                        f"- Evidence: {', '.join(action.get('evidence_refs', [])) or 'N/A'}",
                        "",
                    ]
                )

        output_path.write_text("\n".join(lines), encoding="utf-8")

    def write_exceptions_report(self, exceptions: list, metrics: dict) -> None:
        output_path = self.run_dir / "exceptions.md"

        lines = [
            "# Exceptions Report",
            "",
            "## Summary",
            "",
            f"- Total exceptions: {metrics['exceptions']}",
            "",
        ]

        if not exceptions:
            lines.append("No exceptions were generated.")
        else:
            for exception in exceptions:
                lines.extend(
                    [
                        f"## {exception['exception_id']}",
                        "",
                        f"- Change ID: {exception['change_id']}",
                        f"- Risk Level: {exception['risk_level']}",
                        f"- Required Review: {exception['required_review']}",
                        f"- Reason: {exception['reason']}",
                        f"- Evidence: {', '.join(exception.get('evidence_refs', [])) or 'N/A'}",
                        "",
                    ]
                )

        output_path.write_text("\n".join(lines), encoding="utf-8")

    def write_json(self, filename: str, data: dict) -> None:
        output_path = self.run_dir / filename

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def find_by_change_id(self, items: list, change_id: str) -> dict:
        for item in items:
            if item.get("change_id") == change_id:
                return item
        return {}

    def get_value(self, item: dict, key: str, default=None):
        if not item:
            return default

        value = item.get(key, default)

        if value == "":
            return default

        return value

    def get_evidence_refs(self, *items: dict) -> list:
        refs = []

        for item in items:
            if not item:
                continue

            evidence = item.get("evidence_refs", [])

            if isinstance(evidence, list):
                refs.extend(evidence)

        return sorted(set(refs))

    def safe_float(self, value) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def determine_owner(self, item: dict) -> str:
        final_status = item.get("final_status")

        if final_status == "legal_review_required":
            return "Legal / Compliance Team"

        if final_status == "compliance_review_required":
            return "Compliance Team"

        business_unit = item.get("business_unit")

        if business_unit and business_unit != "unknown":
            return business_unit

        return "Compliance Team"

    def determine_priority(self, item: dict) -> str:
        risk_level = str(item.get("risk_level", "")).lower()
        impact_score = item.get("impact_score", 0)

        if risk_level == "high" or impact_score >= 70:
            return "High"

        if risk_level == "medium" or impact_score >= 40:
            return "Medium"

        return "Low"

    def build_exception_reason(self, item: dict) -> str:
        if item.get("confidence", 1) < 0.7:
            return "Low extraction confidence requires manual legal or compliance review."

        if item.get("impact_score", 0) >= 70:
            return "High impact score requires compliance review before approval."

        if str(item.get("risk_level", "")).lower() == "high":
            return "High risk level requires compliance review."

        return "Manual review required based on final triage status."

    def required_review_type(self, item: dict) -> str:
        if item.get("confidence", 1) < 0.7:
            return "Legal Review"

        return "Compliance Review"

    def build_final_recommendation(self, metrics: dict) -> str:
        if metrics["pipeline_status"] == "review_required":
            return "Compliance or legal review is required before approval."

        if metrics["pipeline_status"] == "remediation_required":
            return "Remediation actions should be completed and reviewed by compliance."

        if metrics["pipeline_status"] == "completed_with_missing_upstream_outputs":
            return "Agent H completed, but upstream outputs from B/C/D/E were not available yet."

        return "No urgent remediation required. Continue monitoring."

    def log(self, message: str) -> None:
        if self.audit:
            self.audit.log(message)
