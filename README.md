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