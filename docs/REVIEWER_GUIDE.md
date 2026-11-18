# Reviewer guide

## Five-minute inspection

1. **Scope:** README states this is an approximate reports-only Scenario 1 reconstruction.
2. **Results:** `analysis/RESULTS.md` compares three models with the paper, without an improvement claim.
3. **Primary evidence:** open `evidence/original/apt_paper_s1_lr_v2-model-metadata.json`; inspect `modelInfo.metrics.AUCPR`. Repeat for RF and MLP.
4. **Settings:** inspect the three `*-pipeline.json` exports and each model's `trainConfig`.
5. **Limitations:** read `docs/LIMITATIONS.md` before interpreting higher scores.

## Verification checklist

| Check | How to verify | What it establishes |
|---|---|---|
| Export consistency | `python src/audit_results.py` | Summaries equal saved catalogue scores |
| Evidence integrity | Same audit checks `evidence/SHA256.json` | Files match the preserved archive member hashes |
| Source archive identity | `evidence/archive-provenance.json` | Hash of the supplied ZIP, not an independent timestamp signature |
| Graph size | `graph-metadata.json` | 58,842 projected nodes and 140,790 directed entries |
| GDS and Neo4j versions | `software-versions.json` | GDS 2.6.0 and Neo4j Community 5.13.0 |
| Candidate count | Pipeline `trainingParameterSpace` | One fixed candidate per model |
| Model persistence | `loaded`, `stored` in model exports | Models were loaded but not stored to disk |
| Test independence limits | Audit and limitations documents | Link split, not report/campaign split |
| Proposed extension status | `docs/FUTURE_WORK.md` | STIX classifier remains planned |

## Optional live demonstration

On the student's original database, run the read-only queries in `docs/VERIFY_DATABASE.cypher`. A newly installed empty Neo4j instance cannot reproduce the experiment from this repository alone. The original populated database or a validated snapshot is required.

The offline audit verifies stored evidence. It neither reruns training nor independently verifies every original report or relationship.
