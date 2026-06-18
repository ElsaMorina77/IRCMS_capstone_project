# IRCMS Shared Data Schemas

This file explains the main data objects passed between IRCMS agents.

## ContextPacket

Created by Agent A.

Used to describe the selected scenario bundle, source files, and intake metadata.

Example:

```json
{
  "bundle_id": "scenario_04_downstream_system_impact",
  "title": "Cross-System Customer Risk Data Synchronization Requirement",
  "business_units": ["Compliance", "Operations", "Technology"],
  "expected_result": ["high_impact", "downstream_systems_affected"],
  "source_files": {
    "regulation": "regulation.txt",
    "current_policies": "current_policies.md",
    "control_inventory": "control_inventory.csv",
    "process_map": "process_map.csv",
    "jurisdiction_scope": "jurisdiction_scope.yaml"
  },
  "intake_metadata": {
    "regulation_source_type": "pdf",
    "extraction_method": "pdf_text_extraction",
    "ocr_used": false
  }
}
```

## EvidenceIndex

Created by Agent A.

Stores normalized regulation evidence so downstream agents can use the same structure
regardless of whether the source was TXT, HTML, PDF, OCR, or a URL.

Example:

```json
{
  "evidence": [
    {
      "evidence_id": "EV-001",
      "source_file": "regulation.pdf",
      "source_type": "pdf",
      "extraction_method": "pdf_text_extraction",
      "ocr_used": false,
      "paragraph_number": 1,
      "text": "Financial institutions must verify customer identity before account activation."
    }
  ]
}
```

## ExtractedChanges

Created by Agent B.

Stores structured regulatory changes extracted from the evidence index.

Example:

```json
{
  "changes": [
    {
      "change_id": "CHG-001",
      "requirement_text": "Banks shall document sanctions screening results in the compliance system.",
      "change_type": "general_regulatory_requirement",
      "domain": "General Compliance",
      "jurisdiction": "Unknown",
      "effective_date": "2026-01-15",
      "confidence": 0.7,
      "evidence_refs": ["EV-002", "EV-003"],
      "status": "extracted"
    }
  ]
}
```

## GapAnalysis

Created by Agent C.

Stores deterministic gap findings and preserves business-unit context and effective dates.

Example:

```json
{
  "findings": [
    {
      "finding_id": "GAP-001",
      "change_id": "CHG-001",
      "requirement_text": "Banks shall document sanctions screening results in the compliance system.",
      "change_type": "general_regulatory_requirement",
      "domain": "General Compliance",
      "business_units": ["Compliance"],
      "effective_date": "2026-01-15",
      "matched_policy_section": "Screening results are recorded inconsistently across systems.",
      "coverage_score": 29,
      "coverage_status": "gap",
      "severity": "high",
      "confidence": 0.7,
      "recommendation": "Create or update policy controls to address missing coverage for general_regulatory_requirement.",
      "evidence_refs": ["EV-002", "EV-003"],
      "status": "open"
    }
  ]
}
```

## ImpactAssessment

Created by Agent D.

Stores impact scoring and downstream process/system mapping for each finding.

Example:

```json
{
  "impacts": [
    {
      "impact_id": "IMP-001",
      "finding_id": "GAP-001",
      "change_id": "CHG-001",
      "requirement_text": "Banks shall document sanctions screening results in the compliance system.",
      "change_type": "general_regulatory_requirement",
      "domain": "General Compliance",
      "severity": "high",
      "coverage_status": "gap",
      "effective_date": "2026-01-15",
      "impact_score": 100,
      "impact_level": "high",
      "system_count": 3,
      "process_count": 2,
      "impacted_processes": ["PROC-071", "PROC-072"],
      "impacted_systems": ["Screening Engine", "Compliance Tracker", "Document Repository"],
      "impacted_business_units": ["Compliance"],
      "recommended_owner": "Compliance",
      "status": "assessed",
      "evidence_refs": ["EV-002", "EV-003"]
    }
  ]
}
```

## ControlMappingResult

Created by Agent E.

Stores final control coverage decisions for each extracted change.

Example:

```json
{
  "agent": "Agent E - Control Mapping",
  "total_changes": 1,
  "total_controls": 2,
  "mappings": [
    {
      "change_id": "CHG-001",
      "control_id": "CTRL-071",
      "control_name": "Screening Record Entry",
      "coverage_status": "partial",
      "coverage_score": 52.4,
      "missing_elements": ["Existing control only partially covers the requirement."],
      "recommended_action": "Update the existing control to fully cover the new regulatory requirement.",
      "evidence_refs": ["EV-002", "EV-003"]
    }
  ]
}
```

## Metrics

Created by Agent H.

Stores final run-level KPI values, throughput, and deadline proximity summary.

Example:

```json
{
  "generated_at": "2026-06-18 14:00:00",
  "total_changes": 3,
  "total_gaps": 3,
  "high_risk_items": 2,
  "remediation_required": 1,
  "exceptions": 2,
  "gap_rate": 100.0,
  "throughput": {
    "changes_processed": 3,
    "gaps_identified": 3
  },
  "deadline_proximity": {
    "dated_items": 1,
    "overdue_items": 1,
    "short_window_items": 0
  },
  "pipeline_status": "review_required"
}
```
