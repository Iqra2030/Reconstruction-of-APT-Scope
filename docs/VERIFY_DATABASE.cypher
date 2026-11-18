// Read-only checks on the student's original baseline database.
CALL dbms.components();
RETURN gds.version() AS gds;
MATCH (r:BaselineReport) RETURN count(r) AS reports;
MATCH (g:BaselineGroup) RETURN count(g) AS rawGroupNames;
MATCH (i:BaselineIoC) RETURN count(i) AS indicators;
MATCH (a)-[r]->(b)
WHERE (a:BaselineReport OR a:BaselineGroup OR a:BaselineIoC)
  AND (b:BaselineReport OR b:BaselineGroup OR b:BaselineIoC)
  AND type(r) IN ['HAS_IOC','HAS_APT_GROUP','KNOWN_AS']
RETURN type(r) AS relationshipType, count(r) AS storedRelationships;
CALL gds.graph.list('apt_paper_s1_graph_v2')
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;
CALL gds.model.list() YIELD modelName, modelInfo, loaded, stored
WHERE modelName IN ['apt_paper_s1_lr_v2','apt_paper_s1_rf_v2','apt_paper_s1_mlp_v2']
RETURN modelName, modelInfo.metrics AS metrics, loaded, stored;
