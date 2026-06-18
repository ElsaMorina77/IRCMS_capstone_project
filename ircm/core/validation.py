import json
from pathlib import Path

from ircm.schemas.models import (
    ApprovalPacket,
    ChangeRegister,
    ContextPacket,
    ControlMappingResult,
    EvidenceIndex,
    ExtractedChanges,
    GapAnalysis,
    ImpactMatrix,
    Metrics,
)


def validate_run_outputs(run_dir: Path) -> None:
    validators = {
        "context_packet.json": _validate_context_packet,
        "evidence_index.json": _validate_evidence_index,
        "extracted_changes.json": _validate_extracted_changes,
        "gap_analysis.json": _validate_gap_analysis,
        "impact_assessment.json": _validate_impact_assessment,
        "control_mapping.json": _validate_control_mapping,
        "metrics.json": _validate_metrics,
        "change_register.json": _validate_change_register,
        "approval_packet.json": _validate_approval_packet,
    }

    for filename, validator in validators.items():
        file_path = run_dir / filename
        if not file_path.exists():
            continue

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        validator(data)


def _validate_context_packet(data: dict) -> None:
    ContextPacket.model_validate(data)


def _validate_evidence_index(data: dict) -> None:
    EvidenceIndex.model_validate(data)


def _validate_extracted_changes(data) -> None:
    if isinstance(data, list):
        ExtractedChanges.model_validate({"changes": data})
        return

    ExtractedChanges.model_validate(data)


def _validate_gap_analysis(data) -> None:
    if isinstance(data, list):
        GapAnalysis.model_validate({"findings": data})
        return

    GapAnalysis.model_validate(data)


def _validate_impact_assessment(data) -> None:
    if isinstance(data, list):
        ImpactMatrix.model_validate({"impacts": data})
        return

    ImpactMatrix.model_validate(data)


def _validate_control_mapping(data) -> None:
    ControlMappingResult.model_validate(data)


def _validate_metrics(data: dict) -> None:
    Metrics.model_validate(data)


def _validate_change_register(data: dict) -> None:
    ChangeRegister.model_validate(data)


def _validate_approval_packet(data: dict) -> None:
    ApprovalPacket.model_validate(data)
