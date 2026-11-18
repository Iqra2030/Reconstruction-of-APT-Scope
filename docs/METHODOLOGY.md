# Reconstruction methodology and configuration

## Completed original session

1. Installed Neo4j Community 5.13.0, APOC 5.13.0 and GDS 2.6.0 on Windows.
2. Used the existing extracted IOC files for 743 reports. Parsed evidence, removed duplicate report/value pairs, checked formats and retained uncertain values for review. This was not a new PDF extraction system.
3. Built `BaselineReport`, `BaselineGroup` and `BaselineIoC` nodes with `HAS_IOC`, `HAS_APT_GROUP` and `KNOWN_AS` relationships. Earlier exploratory graph objects were separate from these baseline labels.
4. Projected all three labels and relationship types as an undirected GDS graph. No database node properties were projected.
5. Used native GDS link-prediction pipelines, FastRP node properties, Hadamard pair features and one candidate per model.
6. Exported configurations, catalogue metrics and saved summaries. Preserved the original evidence unchanged.

## Shared settings verified in exports

| Setting | Value |
|---|---|
| Source / target labels | BaselineReport / BaselineGroup |
| Target relationship | HAS_APT_GROUP |
| Context relationship types | HAS_IOC, KNOWN_AS |
| Context node label | BaselineIoC |
| Test fraction | 0.2 |
| Train fraction of test complement | 0.25 |
| Interpretation | About 60% feature links, 20% training links, 20% test links |
| Validation folds | 7 |
| Negative sampling ratio | 1.0 |
| Random seed / training concurrency | 42 / 1 |
| Embedding dimensions | 128 |
| FastRP iteration weights | [0.0, 1.0, 1.0] |
| Node self-influence / normalisation strength | 0.0 / 0.0 |
| Feature | HADAMARD on paperEmbedding |
| Metric | AUCPR |
| Stored trained binaries | No |

The original graph projection used readConcurrency=4, while FastRP and training used concurrency=1. Counts are subject to split rounding. It is unresolved whether the authors interpreted their train fraction identically.

## Classifiers

- **LR:** minEpochs=1, maxEpochs=100, learningRate=0.001, batchSize=100, patience=1, tolerance=0.001, penalty=0, focusWeight=0, classWeights=[].
- **MLP:** same optimiser settings, hiddenLayerSizes=[100].
- **RF:** 100 trees, GINI, maxDepth=2147483647, minSplitSize=2, minLeafSize=1, numberOfSamplesRatio=1.0.

These are recorded installed-default candidates, not recovered author hyperparameters. `maxTrials=10` in the pipeline is a ceiling, not ten executed trials.

## New packaging utilities

The executable replay utility assembles calls from the exported configuration, uses new catalogue names, and requires the existing baseline database. It does not recreate the missing historical preprocessing or data-import process. Counts are checked before training but cannot establish exact content equality.
