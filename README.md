# IRCMS Capstone Project

## Intelligent Regulatory Change Management System

IRCMS is a prototype multi-agent system that analyzes regulatory changes and produces structured compliance outputs.

The system reads a regulatory scenario bundle, extracts important regulatory requirements, checks them against existing internal policies and controls, identifies gaps, scores business impact, and generates final remediation and audit artifacts.

---

## Project Goal

The goal of this capstone project is to build a working regulatory change management pipeline.

The system should show how multiple agents can work together to process a regulation from intake to final remediation planning.

The focus is not to build a large production application.  
The focus is to build a clean, working prototype that can be explained and demonstrated clearly.

---

## System Pipeline

The project is built as a six-agent pipeline:

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
Agent H - Triage and Final Reports
      ↓
Generated Run Artifacts

## MVP Scope

This project is currently implemented as a rule-based MVP. The goal is to prove the full regulatory change pipeline before adding optional UI, LangGraph, or LLM features.

## Scenario List

- scenario_01_kyc_60_days
- scenario_02_low_risk_update
- scenario_03_deadline_passed
- scenario_04_low_confidence_language
- scenario_05_partial_control_match
- scenario_06_policy_conflict
- scenario_07_many_systems_impacted
- scenario_08_informational_guidance

## Future Improvements

- LangGraph wrapper
- Streamlit GUI
- Optional LLM extraction in Agent B
- Human review step for low-confidence or high-risk changes