import json
import shutil
from datetime import datetime
from pathlib import Path
from getpass import getpass
from neo4j import GraphDatabase

root = Path(r"C:\APT-Scope")
output = root / ("paper-s1-v2-evidence-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
output.mkdir(exist_ok=False)

pipelines = [
    "apt_paper_s1_v2",
    "apt_paper_s1_rf_pipeline_v2",
    "apt_paper_s1_mlp_pipeline_v2",
]
models = [
    "apt_paper_s1_lr_v2",
    "apt_paper_s1_rf_v2",
    "apt_paper_s1_mlp_v2",
]

def save(name, data):
    (output / name).write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )

with GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", getpass("Neo4j password: "))
) as driver:
    driver.verify_connectivity()

    def query(text, **parameters):
        records, _, _ = driver.execute_query(
            text, parameters_=parameters, database_="neo4j"
        )
        return [record.data() for record in records]

    save("software-versions.json", {
        "neo4j": query("CALL dbms.components()"),
        "gds": query("RETURN gds.version() AS version")
    })

    for name in pipelines:
        rows = query("CALL gds.pipeline.list($name)", name=name)
        if not rows:
            raise RuntimeError("Pipeline missing: " + name)
        save(name + "-pipeline.json", rows)

    for name in models:
        rows = query("CALL gds.model.list($name)", name=name)
        if not rows:
            raise RuntimeError("Model missing: " + name)
        save(name + "-model-metadata.json", rows)

    save("graph-metadata.json", query(
        "CALL gds.graph.list($name)",
        name="apt_paper_s1_graph_v2"
    ))

for name in [
    "paper-s1-lr-v2-results.json",
    "paper-s1-rf-v2-results.json",
    "paper-s1-mlp-v2-results.json",
    "paper-s1-v2-comparison.csv",
]:
    shutil.copy2(root / name, output / name)

print("Evidence saved to:", output)
print("Files saved:", len(list(output.iterdir())))
print("Configuration and metrics exported; trained model binaries are NOT included.")
print("No models retrained and no database data changed.")
