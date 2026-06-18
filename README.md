# IRCMS Capstone Project

## Intelligent Regulatory Change Management System

IRCMS is a prototype system that helps process regulatory changes in a structured and explainable way.

The system takes a regulatory scenario as input, extracts the important requirements, compares them with existing policies and controls, checks business impact, and creates final reports for review.

This project is an MVP. It is not a production compliance platform, but it shows how a regulatory change management workflow can be automated using a multi-agent pipeline.

---

## What the project does

The project answers a simple question:

What should happen when a new regulation affects an organization?

To answer that, IRCMS runs the regulation through multiple agents. Each agent handles one part of the workflow.

The system can:

* read a regulatory scenario bundle
* create an evidence index from the regulation
* extract regulatory requirements
* compare requirements with internal policies
* identify policy gaps
* assess business, process, and system impact
* map requirements to existing controls
* create final remediation and approval reports
* keep an audit log of the workflow

---

## Workflow

```text
Scenario Bundle
      ↓
Agent A - Intake
      ↓
Agent B - Change Extraction
      ↓
Agent C - Gap Analysis
      ↓
Agent D - Impact Assessment
      ↓
Agent E - Control Mapping
      ↓
Agent H - Final Triage and Reports
      ↓
Generated Output Files
```

---

## Agents

### Agent A - Intake

Agent A reads the selected scenario bundle and validates the required files.

It creates:

```text
context_packet.json
evidence_index.json
```

Agent A converts the regulation into structured evidence items. These evidence items are then used by the next agents.

Agent A supports several regulation input types:

```text
.txt
.md
.pdf
.png
.jpg
.jpeg
.webp
.tif
.tiff
.bmp
.html
.htm
```

It also supports basic URL intake for HTML and PDF sources if the regulation file in the manifest is provided as a URL.

For PDFs, Agent A first tries normal text extraction. If the PDF is scanned and has no selectable text, OCR can be used as a fallback if the required OCR tools are installed.

---

### Agent B - Change Extraction

Agent B reads `evidence_index.json` and extracts regulatory changes or requirements.

It creates:

```text
extracted_changes.json
```

The output includes extracted requirement text, change type, domain, confidence, and evidence references.

---

### Agent C - Gap Analysis

Agent C compares the extracted regulatory changes with the current internal policies.

It creates:

```text
gap_analysis.json
```

This helps identify whether a current policy already covers the requirement, partially covers it, or does not cover it.

---

### Agent D - Impact Assessment

Agent D checks the business impact of each regulatory change.

It creates:

```text
impact_matrix.csv
```

The output includes impacted business units, processes, systems, impact score, impact level, and recommended owner.

---

### Agent E - Control Mapping

Agent E compares the extracted regulatory changes with the existing control inventory.

It creates:

```text
control_mapping.json
```

This shows whether existing controls fully cover, partially cover, or miss the new regulatory requirement.

---

### Agent H - Final Triage and Reports

Agent H combines the outputs from the previous agents and creates the final review files.

It creates:

```text
change_register.json
metrics.json
remediation_plan.md
exceptions.md
approval_packet.json
```

Agent H is the final reporting stage. It summarizes the workflow results, identifies actions that need review, creates remediation items, and prepares an approval packet.

---

## Project Structure

```text
IRCMS_capstone_project/
│
├── main.py
├── requirements.txt
├── README.md
│
├── bundles/
│   └── scenario_01_kyc_60_days/
│       ├── manifest.yaml
│       ├── regulation.txt
│       ├── current_policies.md
│       ├── control_inventory.csv
│       └── process_map.csv
│
├── demo/
│   └── demo_script.md
│
├── ircm/
│   ├── agents/
│   │   ├── agent_a_intake.py
│   │   ├── agent_b_extraction.py
│   │   ├── agent_c_gap_analysis.py
│   │   ├── agent_d_impact.py
│   │   ├── agent_e_control_mapping.py
│   │   └── agent_h_triage.py
│   │
│   ├── core/
│   │   ├── audit.py
│   │   ├── file_utils.py
│   │   └── orchestrator.py
│   │
│   └── schemas/
│       └── models.py
│
├── runs/
│   └── .gitkeep
│
└── tests/
```

---

## Scenario Bundles

A scenario bundle contains the input files for one regulatory case.

A normal bundle includes:

```text
manifest.yaml
regulation.txt
current_policies.md
control_inventory.csv
process_map.csv
```

Example bundle:

```text
bundles/scenario_01_kyc_60_days/
```

The `manifest.yaml` file tells the system which files to use.

Example:

```yaml
bundle_id: scenario_01_kyc_60_days
title: New KYC Requirement Effective in 60 Days
regulation_file: regulation.txt
current_policies_file: current_policies.md
control_inventory_file: control_inventory.csv
process_map_file: process_map.csv
business_units:
  - Retail Banking
  - Compliance
expected_result:
  - gap_detected
  - high_impact
  - remediation_required
```

If the regulation is a PDF, HTML file, or image, only the `regulation_file` value needs to change.

Examples:

```yaml
regulation_file: regulation.pdf
```

```yaml
regulation_file: regulation.html
```

```yaml
regulation_file: regulation.png
```

---

## How to Run

Python 3.11 is recommended.

### 1. Create a virtual environment

```bash
py -3.11 -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

---

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

### 3. Run the pipeline

```bash
python main.py --bundle bundles/scenario_01_kyc_60_days
```

Expected terminal output:

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

---

## Generated Output Files

Each run creates a timestamped folder inside:

```text
runs/
```

Example:

```text
runs/20260618_034734_scenario_01_kyc_60_days/
```

A successful run should generate files like:

```text
audit_log.md
context_packet.json
evidence_index.json
extracted_changes.json
gap_analysis.json
impact_matrix.csv
control_mapping.json
change_register.json
metrics.json
remediation_plan.md
exceptions.md
approval_packet.json
```

---

## Main Output Files

### `audit_log.md`

Shows the execution trace of the pipeline.

### `context_packet.json`

Contains basic scenario context and source file information.

### `evidence_index.json`

Contains the regulation split into evidence items.

### `extracted_changes.json`

Contains the regulatory requirements extracted by Agent B.

### `gap_analysis.json`

Shows policy coverage and gaps.

### `impact_matrix.csv`

Shows business impact, impacted processes, systems, and impact level.

### `control_mapping.json`

Shows how regulatory changes map to existing controls.

### `change_register.json`

Combines the main workflow results into a final register.

### `metrics.json`

Contains summary metrics and final pipeline status.

### `remediation_plan.md`

Human-readable remediation actions.

### `exceptions.md`

Items that require review or exception handling.

### `approval_packet.json`

Final structured packet for review and approval.

---

## OCR and Document Intake

Agent A supports document intake as an optional feature.

Normal text input works without extra system tools:

```text
.txt
.md
.html
.htm
digital PDFs with selectable text
```

OCR input needs extra system tools:

```text
image OCR requires Tesseract OCR
scanned PDF OCR requires Tesseract OCR and Poppler
```

This means the text-based workflow works normally without OCR setup, while scanned documents require the additional tools.

---

## Testing

Run the full test suite:

```bash
python -m pytest
```

Run the main scenario manually:

```bash
python main.py --bundle bundles/scenario_01_kyc_60_days
```

The project is working correctly if:

```text
all tests pass
all agents complete
Pipeline completed appears in the terminal
a new run folder is created
the expected output files are generated
audit_log.md shows the workflow
```

---

## MVP Scope

The current version focuses on a working command-line MVP.

Included in the MVP:

```text
scenario bundle input
file-based regulation intake
document intake support in Agent A
evidence indexing
change extraction
gap analysis
impact assessment
control mapping
final triage reports
audit logging
basic tests
```

The system is rule-based and designed to be understandable and explainable.

---

## Limitations

This is a prototype and not a real compliance decision system.

Current limitations:

```text
rules are simplified
no database is used
no full web interface is included
OCR quality depends on document quality
HTML parsing is basic
human review is still required for real regulatory decisions
```

---

## Future Improvements

Possible improvements:

```text
add a Streamlit interface
add LangGraph orchestration
add optional LLM extraction in Agent B
improve OCR handling
add more regulatory scenarios
add stronger test coverage
add human approval workflow
add exportable reports
```

---

## Notes for Submission

Generated files and local environment folders should not be committed.

Avoid submitting:

```text
.venv/
__pycache__/
.pytest_cache/
runs/<generated_run_folders>/
*.zip
```

The repository should include source code, scenario bundles, tests, and documentation only.

---

## Short Demo Explanation

IRCMS takes a regulatory scenario bundle and processes it through a chain of agents. Each agent performs one step of the regulatory change workflow. The system starts by reading the regulation, then extracts requirements, checks policies and controls, assesses impact, and creates final remediation and approval reports.
