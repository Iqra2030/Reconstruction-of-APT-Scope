# Verification and reproduction steps

## A. Verify the archived results on any computer

Install Python 3.10 or later, download/clone this repository, and open its root directory:

```powershell
python src/audit_results.py
python -m unittest discover -s tests -v
```

No Neo4j or third-party Python packages are needed. The analysis CSV and Markdown are generated from the archived summaries after agreement checks against model metadata. Four tests verify consistency, tamper detection, and replay-plan safety.

## B. Inspect the planned training calls without connecting

```powershell
python src/replay_training.py --prefix review_plan_01
```

Read `runs/review_plan_01/plan.json`. Choose a fresh prefix each time. This command creates no database connection and does not train. The replay script was newly assembled from metadata; it is not the original script that produced the archived scores.

## C. Rerun training on the existing student database

**Prerequisite:** the original populated Baseline graph (or a separately validated restoration) must already exist. An empty database will fail preflight. The repository does not include enough artifacts to reconstruct that database exactly from raw reports.

1. Start the existing Neo4j Community 5.13.0 server with GDS 2.6.0. Keep the console window running.
2. Run the read-only checks in `docs/VERIFY_DATABASE.cypher` in Neo4j Browser.
3. Use a separate PowerShell window to prepare the driver environment:

```powershell
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' src/replay_training.py --prefix replay_review_01 --execute
```

The password is requested interactively and never written to source. The runner checks versions and aggregate database counts, uses fresh graph/pipeline/model names, obtains memory estimates and trains three models. It writes fresh outputs under `runs/` and does not overwrite original evidence. It never deletes database records or existing catalogue models. A failure may leave newly created in-memory catalogue objects; use a fresh prefix after resolving the failure. Graph and model memory must fit the local server.

**Validation boundary:** plan generation and unit tests passed in the packaging environment. Live replay was not executed here because the student's local Windows Neo4j instance is not connected. Exact historical scores are not guaranteed, even on a graph with matching counts.

## D. Preserve the missing graph snapshot

Keep the source database quiescent, then run:

```powershell
& '.\.venv\Scripts\python.exe' src/export_graph_snapshot.py --output snapshots/baseline-review-01
```

This read-only utility exports nodes and relationships with properties to JSONL. It is new preservation code, not evidence that a historical snapshot already exists. Review exported properties before sharing. Also preserve the original preparation scripts, source file hashes and dataset manifest from `C:\APT-Scope`.

## E. Original evidence exporter

`evidence/original/export_paper_s1_evidence.py` is byte-preserved from the original session. It expects `C:\APT-Scope`, the original catalogue names, and the four manually saved summary/CSV files. It exports metadata only, not trained binaries. Rerunning it requires the original catalogue objects still to be loaded.

## Dependency provenance

Neo4j Community 5.13.0 and GDS 2.6.0 are verified by exports. The Python driver pin 6.4.1 follows the supplied installation transcript. The offline verification path uses only Python's standard library and does not depend on the live-driver version.
