# IRCMS Capstone Project

## Intelligent Regulatory Change Management System

IRCMS is a deterministic multi-agent prototype for regulatory change management.  
It ingests a regulation or a scenario bundle, extracts structured regulatory changes, compares them with internal policy and controls, estimates business impact, and generates review-ready compliance artifacts.

The project is designed as an MVP:
- deterministic Python rules remain the source of truth
- agents communicate through structured files in a shared run folder
- outputs are traceable back to evidence references
- OCR/document-intake support exists in Agent A

---

## What Works

The current prototype supports:

- Agent A intake and evidence normalization
- Agent B deterministic regulatory change extraction
- Agent C gap analysis against internal policies
- Agent D deterministic impact scoring and process/system mapping
- Agent E control mapping against control inventory
- Agent H final triage and report generation
- scenario-bundle runs end to end
- OCR-capable image intake in Agent A when Tesseract is installed
- PDF text extraction in Agent A when `pypdf` is installed
- scanned PDF OCR fallback in Agent A when Tesseract and Poppler are installed
- automated regression tests

Verified scenarios include:
- downstream system impact
- effective date already passed
- informational guidance with no action required

---

## Pipeline

```text
Scenario Bundle / Regulation Input
        |
        v
Agent A - Intake and Evidence Indexing
        |
        v
Agent B - Change Extraction
        |
        v
Agent C - Gap Analysis
        |
        v
Agent D - Impact Assessment
        |
        v
Agent E - Control Mapping
        |
        v
Agent H - Triage and Final Reports
        |
        v
Run Artifacts
```

---

## Agents

### Agent A - Intake

Agent A validates bundle inputs and converts the regulation source into a normalized `evidence_index.json`.

Current supported regulation sources:
- `.txt`
- `.md`
- `.html`
- `.htm`
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`
- `.bmp`
- `.tif`
- `.tiff`
- basic `http/https` HTML or PDF URLs

Agent A output:
- `context_packet.json`
- `evidence_index.json`

Notes:
- born-digital PDFs use text extraction first
- scanned PDFs can fall back to OCR
- images use OCR
- all sources are normalized into the same evidence structure for downstream agents

### Agent B - Change Extraction

Agent B reads `evidence_index.json` and writes `extracted_changes.json`.

Current extraction behavior includes:
- deterministic keyword/rule-based extraction
- confidence scoring
- effective date detection
- threshold-update attachment
- effective-date support-line attachment
- filtering of non-mandatory informational guidance

### Agent C - Gap Analysis

Agent C compares extracted changes against internal policy text and writes `gap_analysis.json`.

Current behavior includes:
- deterministic coverage classification
- severity assignment
- recommendation generation
- effective date pass-through
- business-unit attachment

### Agent D - Impact Assessment

Agent D maps findings to processes, systems, and business units, then writes:
- `impact_assessment.json`
- `impact_matrix.csv`

Current scoring considers:
- severity
- coverage status
- process criticality
- number of impacted processes
- number of impacted systems
- short implementation windows
- overdue effective dates

### Agent E - Control Mapping

Agent E compares extracted changes with the control inventory and writes `control_mapping.json`.

Current behavior includes:
- best-match control search
- coverage scoring
- partial / missing control detection
- recommended action generation

### Agent H - Final Triage and Reports

Agent H combines upstream outputs and writes:
- `change_register.json`
- `metrics.json`
- `remediation_plan.md`
- `exceptions.md`
- `approval_packet.json`

Current reporting includes:
- final statuses
- review routing
- remediation actions with due dates
- exceptions with next actions
- approval packet with evidence package
- throughput, gap rate, and deadline-proximity metrics

---

## Scenario Bundle Format

A scenario bundle contains the inputs for one regulatory case.

Typical bundle contents:
- `manifest.yaml`
- `regulation.txt` or another supported regulation file
- `current_policies.md`
- `control_inventory.csv`
- `process_map.csv`

Optional:
- `jurisdiction_scope_file`

Example `manifest.yaml`:

```yaml
bundle_id: scenario_01_kyc_60_days
title: New KYC Requirement Effective in 60 Days
regulation_file: regulation.txt
current_policies_file: current_policies.md
control_inventory_file: control_inventory.csv
process_map_file: process_map.csv
reference_date: 2026-06-18
business_units:
  - Retail Banking
  - Compliance
expected_result:
  - gap_detected
  - high_impact
  - remediation_required
```

If you want to test HTML, PDF, or OCR, only `regulation_file` needs to point to that source.

---

## Project Structure

```text
IRCMS_capstone_project/
|
|-- main.py
|-- requirements.txt
|-- README.md
|
|-- bundles/
|-- runs/
|-- tests/
|
`-- ircm/
    |-- agents/
    |   |-- agent_a_intake.py
    |   |-- agent_b_extraction.py
    |   |-- agent_c_gap_analysis.py
    |   |-- agent_d_impact.py
    |   |-- agent_e_control_mapping.py
    |   `-- agent_h_triage.py
    |
    |-- core/
    |   |-- audit.py
    |   |-- file_utils.py
    |   |-- orchestrator.py
    |   `-- validation.py
    |
    |-- policies/
    |   `-- rules.yaml
    |
    `-- schemas/
        |-- models.py
        `-- schema_examples.md
```

---

## Installation

### Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### Optional OCR / PDF system tools

For OCR and scanned PDF support on Windows, install:

- Tesseract OCR
- Poppler

Example with `winget`:

```powershell
winget install --id UB-Mannheim.TesseractOCR -e
winget install --id oschwartz10612.Poppler -e
```

If the executables are not immediately available in the current shell, add them to `PATH` for the session:

```powershell
$env:Path += ";C:\Program Files\Tesseract-OCR"
$env:Path += ";C:\Users\DELL\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
```

Verify:

```powershell
tesseract --version
pdftoppm -h
```

---

## How To Run

Run one scenario bundle:

```powershell
python main.py --bundle bundles\scenario_01_kyc_60_days
```

Run with a stable output folder for deterministic reruns:

```powershell
python main.py --bundle bundles\scenario_01_kyc_60_days --run-id review_s01
```

Example successful output:

```text
IRCMS project started.
Selected bundle: bundles\scenario_01_kyc_60_days
Run directory: runs\<timestamp>_scenario_01_kyc_60_days
[1/6] Agent A Intake started
[1/6] Agent A Intake complete
[2/6] Agent B Extraction started
[2/6] Agent B Extraction complete
[3/6] Agent C Gap Analysis started
[3/6] Agent C Gap Analysis complete
[4/6] Agent D Impact Assessment started
[4/6] Agent D Impact Assessment complete
[5/6] Agent E Control Mapping started
[5/6] Agent E Control Mapping complete
[6/6] Agent H Triage started
[6/6] Agent H Triage complete
Pipeline completed.
```

By default, each run creates a timestamped folder inside `runs/`.
If you pass `--run-id`, the pipeline writes to a stable folder name for reproducible reruns.

---

## Generated Artifacts

A successful run typically generates:

- `audit_log.md`
- `context_packet.json`
- `evidence_index.json`
- `extracted_changes.json`
- `gap_analysis.json`
- `impact_assessment.json`
- `impact_matrix.csv`
- `control_mapping.json`
- `change_register.json`
- `metrics.json`
- `remediation_plan.md`
- `exceptions.md`
- `approval_packet.json`

---

## Testing

Run all tests:

```powershell
pytest tests -q
```

Current regression coverage includes:
- Agent B ignores non-mandatory guidance
- Agent B attaches threshold and effective-date support lines
- Agent D raises impact for overdue effective dates

---

## Current Limitations

The project is a strong prototype, but some advanced features are still future work:

- PDF/image evidence now includes basic page-level source pointers, but not fine-grained paragraph-level legal bounding boxes
- OCR quality depends on document quality and Tesseract output
- business-unit mapping is heuristic, not fully finding-specific in all cases
- LangGraph / LangChain integration is planned but not implemented

---

## Future Direction

Planned future improvements:
- LangGraph as workflow skeleton
- LangChain only for controlled fallback/helper calls
- normalized evidence contract across TXT / HTML / PDF / OCR inputs
- stronger runtime schema enforcement
- better OCR cleanup and ambiguity fallback

Design principle:
- LLM may suggest
- Python rules must validate
- final compliance decisions stay deterministic
