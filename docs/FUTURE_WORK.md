# Proposed STIX extension (not completed)

**Question:** do source-supported relational features improve report-level known-group attribution beyond the same entities and techniques?

The proposed workflow verifies report labels, groups campaigns before model development, masks direct actor identifiers, extracts source-supported entities/relationships, represents them in STIX 2.1 and compares matched feature arms. LR, SVM, RF and XGBoost will use the same partitions and tuning budgets. Macro F1 will be the primary metric. SHAP contributions will resolve to STIX records and original passages through a provenance index.

The editable diagram is in `diagrams/Proposed_STIX_Methodology.drawio`. Page 1 shows the flow; page 2 records the intended protocol. None of these planned activities is presented as an achieved improvement. The completed reconstruction's AUCPR scores evaluate a different task.
