# IRCMS Demo Script

## 1. Problem

Regulatory changes can affect policies, controls, systems, and business processes. Manual review is slow and hard to audit.

## 2. Solution

IRCMS is a multi-agent prototype that reads a regulatory change bundle and generates structured compliance outputs.

## 3. Pipeline

Scenario Bundle → Agent A Intake → Agent B Extraction → Agent C Gap Analysis → Agent D Impact Assessment → Agent E Control Mapping → Agent H Final Reports

## 4. Demo Scenario

We will run the KYC 60-day scenario.

Command:

```bash
python main.py --bundle bundles/scenario_01_kyc_60_days