from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SourceFileSet(BaseModel):
    regulation: str
    current_policies: str
    control_inventory: str
    process_map: str
    jurisdiction_scope: Optional[str] = None


class IntakeMetadata(BaseModel):
    regulation_source_type: str
    extraction_method: str
    ocr_used: bool


class ContextPacket(BaseModel):
    bundle_id: str
    title: str
    business_units: List[str]
    expected_result: List[str] = []
    source_files: SourceFileSet
    intake_metadata: Optional[IntakeMetadata] = None
    reference_date: Optional[str] = None


class EvidenceItem(BaseModel):
    evidence_id: str
    source_file: str
    source_type: Optional[str] = None
    extraction_method: Optional[str] = None
    ocr_used: Optional[bool] = None
    paragraph_number: int
    text: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    bbox: Optional[Dict[str, Any]] = None


class EvidenceIndex(BaseModel):
    evidence: List[EvidenceItem]


class RegulatoryChange(BaseModel):
    change_id: str
    requirement_text: str
    change_type: str
    domain: str
    jurisdiction: Optional[str] = None
    effective_date: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: List[str]
    status: Optional[str] = "extracted"


class ExtractedChanges(BaseModel):
    changes: List[RegulatoryChange]


class GapFinding(BaseModel):
    finding_id: str
    change_id: str
    requirement_text: str
    change_type: str
    domain: str
    business_units: List[str] = []
    effective_date: Optional[str] = None
    matched_policy_section: str = ""
    coverage_status: str
    coverage_score: float = Field(ge=0.0, le=100.0)
    severity: str
    confidence: float = Field(ge=0.0, le=1.0)
    recommendation: str
    evidence_refs: List[str]
    status: str


class GapAnalysis(BaseModel):
    findings: List[GapFinding]


class ImpactAssessment(BaseModel):
    impact_id: str
    finding_id: str
    change_id: str
    requirement_text: str
    change_type: str
    domain: str
    severity: str
    coverage_status: str
    effective_date: Optional[str] = None
    impact_score: float = Field(ge=0.0, le=100.0)
    impact_level: str
    system_count: Optional[int] = Field(default=None, ge=0)
    process_count: Optional[int] = Field(default=None, ge=0)
    impacted_processes: List[str]
    impacted_systems: List[str]
    impacted_business_units: List[str]
    recommended_owner: str
    status: str
    evidence_refs: List[str]


class ImpactMatrix(BaseModel):
    impacts: List[ImpactAssessment]


class ControlMapping(BaseModel):
    change_id: str
    control_id: Optional[str] = None
    control_name: Optional[str] = None
    coverage_status: str
    coverage_score: float = Field(ge=0.0, le=100.0)
    missing_elements: List[str] = []
    recommended_action: str
    evidence_refs: List[str] = []


class ControlMappingResult(BaseModel):
    agent: Optional[str] = None
    total_changes: Optional[int] = None
    total_controls: Optional[int] = None
    mappings: List[ControlMapping]


class RemediationAction(BaseModel):
    action_id: str
    change_id: str
    owner: str
    action: str
    priority: str
    due_date: Optional[str] = None
    status: str = "open"
    evidence_refs: List[str] = []


class ExceptionItem(BaseModel):
    exception_id: str
    change_id: str
    reason: str
    risk_level: str
    required_review: str
    next_action: Optional[str] = None
    evidence_refs: List[str] = []


class Metrics(BaseModel):
    generated_at: Optional[str] = None
    total_changes: int
    total_gaps: int
    high_risk_items: int
    remediation_required: int
    exceptions: int
    gap_rate: Optional[float] = None
    throughput: Optional[Dict[str, int]] = None
    deadline_proximity: Optional[Dict[str, int]] = None
    pipeline_status: str


class ChangeRegisterItem(BaseModel):
    change_id: str
    requirement_text: str
    change_type: str
    domain: str
    effective_date: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    gap_status: str
    gap_severity: str
    business_unit: Any
    process_name: Any
    impact_score: float = Field(ge=0.0, le=100.0)
    risk_level: str
    control_id: Optional[str] = None
    control_name: Optional[str] = None
    control_coverage_status: str
    control_coverage_score: float = Field(ge=0.0, le=100.0)
    recommended_action: str
    final_status: str
    evidence_refs: List[str] = []


class ChangeRegister(BaseModel):
    changes: List[ChangeRegisterItem]


class ApprovalPacketSummary(BaseModel):
    total_changes: int
    total_gaps: int
    high_risk_items: int
    remediation_required: int
    exceptions: int


class ApprovalEvidenceItem(BaseModel):
    change_id: str
    requirement_text: str
    final_status: str
    risk_level: str
    impact_score: float = Field(ge=0.0, le=100.0)
    control_coverage_status: str
    evidence_refs: List[str] = []


class ApprovalPacket(BaseModel):
    scenario: str
    final_status: str
    summary: ApprovalPacketSummary
    recommendation: str
    changes_requiring_review: List[str] = []
    evidence_package: List[ApprovalEvidenceItem] = []
    exceptions: List[ExceptionItem] = []
