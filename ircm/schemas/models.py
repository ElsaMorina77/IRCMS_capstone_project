from typing import List, Optional
from pydantic import BaseModel, Field


class SourceFileSet(BaseModel):
    regulation: str
    current_policies: str
    control_inventory: str
    process_map: str


class ContextPacket(BaseModel):
    bundle_id: str
    title: str
    business_units: List[str]
    expected_result: List[str] = []
    source_files: SourceFileSet


class EvidenceItem(BaseModel):
    evidence_id: str
    source_file: str
    paragraph_number: int
    text: str


class EvidenceIndex(BaseModel):
    evidence: List[EvidenceItem]


class RegulatoryChange(BaseModel):
    change_id: str
    requirement_text: str
    change_type: str
    domain: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: List[str]


class ExtractedChanges(BaseModel):
    changes: List[RegulatoryChange]


class GapFinding(BaseModel):
    finding_id: str
    change_id: str
    gap_type: str
    coverage_status: str
    coverage_score: float = Field(ge=0.0, le=100.0)
    severity: str
    recommendation: str
    evidence_refs: List[str]


class GapAnalysis(BaseModel):
    findings: List[GapFinding]


class ImpactAssessment(BaseModel):
    change_id: str
    business_unit: str
    process_name: str
    systems_impacted: List[str]
    deadline_score: int = Field(ge=1, le=5)
    gap_score: int = Field(ge=1, le=5)
    impact_score: float = Field(ge=0.0, le=5.0)
    risk_level: str


class ImpactMatrix(BaseModel):
    impacts: List[ImpactAssessment]


class ControlMapping(BaseModel):
    change_id: str
    control_id: Optional[str] = None
    coverage_status: str
    coverage_score: float = Field(ge=0.0, le=100.0)
    missing_elements: List[str] = []
    recommended_action: str


class ControlMappingResult(BaseModel):
    mappings: List[ControlMapping]


class RemediationAction(BaseModel):
    action_id: str
    change_id: str
    owner: str
    action: str
    priority: str
    due_date: Optional[str] = None
    status: str = "open"


class ExceptionItem(BaseModel):
    exception_id: str
    change_id: str
    reason: str
    risk_level: str
    required_review: str


class Metrics(BaseModel):
    total_changes: int
    total_gaps: int
    high_risk_items: int
    exceptions: int
    pipeline_status: str