# IRCMS Demo Script

## 1. Project Introduction

This project is called IRCMS, which stands for Intelligent Regulatory Change Management System.

The goal of the project is to show how a regulatory change can be processed through a structured workflow. Instead of manually reading a regulation, identifying requirements, checking policies, mapping controls, and creating reports, the system automates these steps through a multi-agent pipeline.

This is an MVP prototype. It is not a production compliance platform, but it shows how the workflow can be automated in a clear and explainable way.

---

## 2. Problem

Organizations often need to react to new regulatory requirements.

A typical regulatory change process includes:

```text
reading the regulation
finding the important requirements
checking if current policies already cover them
identifying gaps
checking business impact
mapping the changes to controls
creating remediation actions
preparing final review documents
```

Doing this manually can be slow and inconsistent.

IRCMS solves this by splitting the workflow into several agents, where each agent has one specific responsibility.

---

## 3. Solution Overview

The system uses a multi-agent pipeline.

The full workflow is:

```text
Agent A - Intake
Agent B - Change Extraction
Agent C - Gap Analysis
Agent D - Impact Assessment
Agent E - Control Mapping
Agent H - Final Triage and Reports
```

Each agent reads the output from the previous step and creates a new structured output file.

At the end, the system generates final reports that can be reviewed by a compliance or risk team.

---

## 4. Agent Explanation

### Agent A - Intake

Agent A reads the scenario bundle and validates that all required files exist.

It creates:

```text
context_packet.json
evidence_index.json
```

The evidence index contains the regulation split into evidence items.

Agent A also supports different document input types such as text, markdown, PDF, images, and HTML. OCR can be used for scanned documents if the required OCR tools are installed.

---

### Agent B - Change Extraction

Agent B reads the evidence index and extracts regulatory requirements.

It creates:

```text
extracted_changes.json
```

This file contains the important changes found in the regulation.

---

### Agent C - Gap Analysis

Agent C compares the extracted changes with the current policy.

It creates:

```text
gap_analysis.json
```

This shows whether the existing policy fully covers, partially covers, or does not cover each requirement.

---

### Agent D - Impact Assessment

Agent D checks the possible business impact.

It creates:

```text
impact_matrix.csv
```

This includes impacted business units, processes, systems, impact score, and impact level.

---

### Agent E - Control Mapping

Agent E compares regulatory changes with the control inventory.

It creates:

```text
control_mapping.json
```

This shows whether existing controls cover the requirement or if updates are needed.

---

### Agent H - Final Triage and Reports

Agent H combines the previous outputs and creates the final reports.

It creates:

```text
change_register.json
metrics.json
remediation_plan.md
exceptions.md
approval_packet.json
```

This is the final stage of the workflow.

---

## 5. Demo Command

To run the system, use:

```bash
python main.py --bundle bundles/scenario_01_kyc_60_days
```

Expected output:

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

## 6. Files to Show During Demo

After running the command, open the newest folder inside:

```text
runs/
```

Show these files:

### `audit_log.md`

Shows that each agent ran in order.

### `evidence_index.json`

Shows how the regulation was split into evidence items.

### `extracted_changes.json`

Shows the requirements extracted from the regulation.

### `gap_analysis.json`

Shows policy gaps.

### `impact_matrix.csv`

Shows the affected business areas, processes, systems, and impact level.

### `control_mapping.json`

Shows whether the requirement is covered by existing controls.

### `remediation_plan.md`

Shows recommended actions.

### `metrics.json`

Shows summary metrics and final status.

### `approval_packet.json`

Shows the final structured review packet.

---

## 7. Example Demo Explanation

A simple way to explain the run:

The system starts with a scenario bundle. Agent A reads the regulation and creates an evidence index. Agent B extracts the important regulatory requirements. Agent C compares those requirements with the current policy to find gaps. Agent D checks the business and system impact. Agent E maps the changes to existing controls. Finally, Agent H combines all outputs and creates the final remediation and approval reports.

---

## 8. What Makes the Workflow Logical

The workflow follows the same order a real regulatory change process would follow:

```text
intake first
then extraction
then policy comparison
then impact assessment
then control mapping
then final reporting
```

This makes the system easy to explain and easy to audit.

Each agent has a clear input and output, so the workflow is modular.

---

## 9. MVP Scope

The current project includes:

```text
command-line execution
scenario bundles
multi-agent pipeline
document intake support
evidence indexing
change extraction
gap analysis
impact assessment
control mapping
final reporting
audit logging
basic tests
```

This is enough to demonstrate a working end-to-end MVP.

---

## 10. Limitations

This is a prototype.

Current limitations:

```text
rules are simplified
no database is used
no full web interface is included
OCR depends on external tools
HTML parsing is basic
human review is still required
```

These limitations are normal for an MVP and can be improved in future versions.

---

## 11. Future Work

Possible future improvements include:

```text
Streamlit interface
LangGraph orchestration
LLM support for Agent B extraction
better OCR handling
more scenarios
stronger tests
human approval workflow
exportable PDF reports
```

---

## 12. Closing Explanation

IRCMS demonstrates how a regulatory change can move through a structured agent workflow from intake to final remediation reporting. The main value of the project is that every step creates clear outputs and an audit trail, making the process easier to understand, review, and improve.
