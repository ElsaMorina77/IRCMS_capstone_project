# IRCMS Shared Data Schemas

This file explains the main data objects used between agents.

## ContextPacket

Created by Agent A.

Used to describe the selected scenario bundle.

## EvidenceIndex

Created by Agent A.

Stores regulation paragraphs with evidence IDs.

Example:

```json
{
  "evidence": [
    {
      "evidence_id": "EV-001",
      "source_file": "regulation.txt",
      "paragraph_number": 1,
      "text": "Financial institutions must verify customer identity."
    }
  ]
}