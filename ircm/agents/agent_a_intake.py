import json
from pathlib import Path

import yaml


class IntakeAgent:
    """
    Agent A - Intake.

    Reads the scenario bundle, validates required files,
    creates context_packet.json and evidence_index.json.
    """

    def __init__(self, bundle_dir: Path, run_dir: Path, audit):
        self.bundle_dir = bundle_dir
        self.run_dir = run_dir
        self.audit = audit

    def run(self) -> dict:
        self.audit.log("Agent A Intake started.")

        manifest = self.load_manifest()
        self.validate_required_files(manifest)

        regulation_file = manifest["regulation_file"]
        regulation_text = self.read_text_file(regulation_file)

        context_packet = self.create_context_packet(manifest)
        evidence_index = self.create_evidence_index(
            regulation_text=regulation_text,
            regulation_file=regulation_file,
        )

        self.write_json("context_packet.json", context_packet)
        self.write_json("evidence_index.json", {"evidence": evidence_index})

        self.audit.log("Agent A created context_packet.json.")
        self.audit.log("Agent A created evidence_index.json.")
        self.audit.log("Agent A Intake completed.")

        return context_packet

    def load_manifest(self) -> dict:
        manifest_path = self.bundle_dir / "manifest.yaml"

        if not manifest_path.exists():
            raise FileNotFoundError(f"Missing manifest file: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as file:
            manifest = yaml.safe_load(file)

        if not manifest:
            raise ValueError("manifest.yaml is empty or invalid.")

        return manifest

    def validate_required_files(self, manifest: dict) -> None:
        required_keys = [
            "regulation_file",
            "current_policies_file",
            "control_inventory_file",
            "process_map_file",
        ]

        for key in required_keys:
            if key not in manifest:
                raise KeyError(f"Missing key in manifest.yaml: {key}")

            file_path = self.bundle_dir / manifest[key]

            if not file_path.exists():
                raise FileNotFoundError(f"Missing required bundle file: {file_path}")

    def read_text_file(self, filename: str) -> str:
        file_path = self.bundle_dir / filename

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def create_context_packet(self, manifest: dict) -> dict:
        return {
            "bundle_id": manifest.get("bundle_id"),
            "title": manifest.get("title"),
            "business_units": manifest.get("business_units", []),
            "expected_result": manifest.get("expected_result", []),
            "source_files": {
                "regulation": manifest["regulation_file"],
                "current_policies": manifest["current_policies_file"],
                "control_inventory": manifest["control_inventory_file"],
                "process_map": manifest["process_map_file"],
            },
        }

    def create_evidence_index(self, regulation_text: str, regulation_file: str) -> list:
        paragraphs = [
            paragraph.strip()
            for paragraph in regulation_text.split("\n")
            if paragraph.strip()
        ]

        evidence_items = []

        for index, paragraph in enumerate(paragraphs, start=1):
            evidence_items.append(
                {
                    "evidence_id": f"EV-{index:03}",
                    "source_file": regulation_file,
                    "paragraph_number": index,
                    "text": paragraph,
                }
            )

        return evidence_items

    def write_json(self, filename: str, data) -> None:
        output_path = self.run_dir / filename

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)