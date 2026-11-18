"""Export a read-only portable JSONL snapshot of existing Baseline* nodes and edges.
This utility was added for future preservation; no historical snapshot is bundled.
"""
import argparse,json
from getpass import getpass
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path);p.add_argument('--uri',default='bolt://localhost:7687')
    p.add_argument('--user',default='neo4j');p.add_argument('--database',default='neo4j');a=p.parse_args()
    from neo4j import GraphDatabase
    a.output.mkdir(parents=True,exist_ok=False)
    nodes='MATCH (n) WHERE n:BaselineReport OR n:BaselineGroup OR n:BaselineIoC RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS properties'
    edges='MATCH (a)-[r]->(b) WHERE (a:BaselineReport OR a:BaselineGroup OR a:BaselineIoC) AND (b:BaselineReport OR b:BaselineGroup OR b:BaselineIoC) AND type(r) IN ["HAS_IOC","HAS_APT_GROUP","KNOWN_AS"] RETURN elementId(a) AS source, elementId(b) AS target, type(r) AS type, properties(r) AS properties'
    with GraphDatabase.driver(a.uri,auth=(a.user,getpass('Neo4j password: '))) as d:
        with d.session(database=a.database) as session:
            # Keep the source database quiescent during export. IDs refer to this export only.
            def export(tx):
                counts={}
                for name,q in [('nodes.jsonl',nodes),('relationships.jsonl',edges)]:
                    count=0
                    with (a.output/name).open('w',encoding='utf-8') as f:
                        for row in tx.run(q):f.write(json.dumps(row.data(),ensure_ascii=False,default=str)+'\n');count+=1
                    counts[name]=count
                return counts
            counts=session.execute_read(export)
    (a.output/'counts.json').write_text(json.dumps(counts,indent=2)+'\n')
    print(counts)
if __name__=='__main__':main()
