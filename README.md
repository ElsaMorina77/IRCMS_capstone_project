# IRCMS Capstone Project

## Intelligent Regulatory Change Management System

IRCMS is a prototype system that helps process regulatory changes in a structured way.

The idea is simple: a regulation comes in, the system reads it, extracts the important requirements, checks them against existing policies and controls, identifies possible gaps, estimates business impact, and creates final reports for review.

This is not meant to be a full production compliance platform. It is an MVP that shows how a regulatory change management workflow could be automated using a multi-agent pipeline.

---

## What this project does

The project takes a regulatory scenario bundle as input and runs it through a sequence of agents.

Each agent has one responsibility:

1. Read and prepare the input files
2. Extract regulatory requirements
3. Compare requirements with current policies
4. Assess business and system impact
5. Map requirements to existing controls
6. Generate final remediation and review reports

At the end, the system creates structured output files that can be reviewed by a compliance team.

---

## Pipeline

The system follows this workflow:

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
Generated Artifacts
Agents
Agent A - Intake

Agent A reads the selected scenario bundle and validates that the required files exist.

It creates:

context_packet.json
evidence_index.json

Agent A also supports different input formats for the regulation file. It can work with normal text files, markdown files, PDFs, images, and basic HTML input. The goal of Agent A is to normalize different input sources into the same evidence_index.json format so the rest of the pipeline can work normally.

Supported regulation input types:

.txt
.md
.pdf
.png
.jpg
.jpeg
.tif
.tiff
.bmp
.html
.htm

PDF support tries to extract text first. If the PDF is scanned and has no selectable text, OCR can be used as a fallback if the required OCR tools are installed.

Agent B - Change Extraction

Agent B reads the evidence index and extracts regulatory changes or requirements.

It creates:

extracted_changes.json

This output includes extracted requirement text, change type, domain, confidence, and evidence references.

Agent C - Gap Analysis

Agent C compares the extracted changes with the current internal policies.

It creates:

gap_analysis.json

This helps identify whether the current policy already covers the new requirement, partially covers it, or does not cover it.

Agent D - Impact Assessment

Agent D checks how much impact a regulatory change may have on the business.

It creates:

impact_matrix.csv

This includes impacted processes, systems, business units, impact score, and impact level.

Agent E - Control Mapping

Agent E compares the regulatory changes with the control inventory.

It creates:

control_mapping.json

This shows whether existing controls fully cover, partially cover, or miss the new requirement.

Agent H - Final Triage and Reports

Agent H combines the outputs from the previous agents and creates the final reports.

It creates:

change_register.json
metrics.json
remediation_plan.md
exceptions.md
approval_packet.json

Agent H is the final step of the workflow. It summarizes the results, identifies items that need review, and creates remediation actions.

Project Structure
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
├── ircm/
│   ├── agents/
│   │   ├── agent_a_intake.py
│   │   ├── agent_b_extraction.py
│   │   ├── agent_c_gap_analysis.py
│   │   ├── agent_d_impact.py
│   │   ├── agent_e_control_mapping.py
│   │   └── agent_h_triage.py
│   │
│   └── core/
│       ├── audit.py
│       ├── file_utils.py
│       └── orchestrator.py
│
├── runs/
│   └── .gitkeep
│
└── tests/
Scenario Bundles

A scenario bundle is a folder that contains all input files needed for one regulatory case.

A normal bundle contains:

manifest.yaml
regulation.txt
current_policies.md
control_inventory.csv
process_map.csv

Example:

bundles/scenario_01_kyc_60_days/

The manifest.yaml file tells the system which files to use.

Example:

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

If the regulation is an HTML file, PDF, or image, only the regulation_file value needs to change.

Example:

regulation_file: regulation.html

or:

regulation_file: regulation.pdf
How to Run
1. Create a virtual environment

Python 3.11 is recommended.

py -3.11 -m venv .venv

Activate it on Windows:

.venv\Scripts\activate
2. Install dependencies
python -m pip install -r requirements.txt

Some OCR features may require extra system tools such as Tesseract OCR or Poppler. The normal text-based pipeline does not require those tools.

3. Run the pipeline
python main.py --bundle bundles/scenario_01_kyc_60_days

Expected output:

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
Generated Outputs

Each run creates a new timestamped folder inside:

runs/

Example:

runs/20260618_034734_scenario_01_kyc_60_days/

A successful run should generate files like:

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
Important Output Files
audit_log.md

Shows what happened during the pipeline run.

evidence_index.json

Contains the regulation text split into evidence items.

extracted_changes.json

Contains the regulatory requirements extracted by Agent B.

gap_analysis.json

Shows policy gaps found by Agent C.

impact_matrix.csv

Shows impacted processes, systems, business units, and impact level.

control_mapping.json

Shows whether existing controls cover the extracted requirements.

remediation_plan.md

Human-readable remediation actions.

metrics.json

Summary of the final results.

approval_packet.json

Final structured packet for review and approval.

OCR and Document Intake

Agent A supports document intake as an optional feature.

The normal and safest input is still a plain text file:

regulation.txt

For PDFs:

regulation_file: regulation.pdf

For HTML:

regulation_file: regulation.html

For image OCR:

regulation_file: regulation.png

The rest of the pipeline does not change because Agent A always creates the same evidence_index.json format.

OCR support may require extra setup:

Tesseract OCR
Poppler for scanned PDFs

If these tools are not installed, the text-based pipeline still works.