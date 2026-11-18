# Reconstruction audit

APT Scope Reconstruction and Results Audit

Iqra Ilyas | MS Cybersecurity | 25i-7703
18 November 2026 | Reports-only experiment v2

An approximate reconstruction of APT-Scope’s reports-only link-prediction experiment has been completed using Neo4j Graph Data Science. This report checks the exported evidence against the published results. The three models ran successfully, but differences in data, features and configuration prevent a claim of exact replication or improvement over the paper.

Verified results


| Model | Mean train | Outer train | Validation | Test | Seconds |
| --- | --- | --- | --- | --- | --- |
| LR | 0.79684 | 0.79631 | 0.76776 | 0.79609 | 1.695 |
| RF | 0.82159 | 0.81381 | 0.72158 | 0.67877 | 16.509 |
| MLP | 0.80868 | 0.80511 | 0.77134 | 0.79557 | 14.339 |



All scores are GDS AUCPR, not classification accuracy. The exported model metrics agree exactly with the manually saved result summaries. Training times come from the saved summaries and the execution outputs; the model catalogue does not independently verify these timings.

MLP has the highest mean validation AUCPR (0.77134). LR has the highest test AUCPR (0.79609), only 0.000524 above MLP. This single-seed result does not establish a statistically meaningful difference. RF has a larger outer-training-to-test gap (0.13504).

Evidence checked

The archive contains 13 files: three pipeline exports, three model metadata exports, graph metadata, software versions, three result summaries, a comparison CSV and the export script. Verified software is Neo4j Community 5.13.0 with GDS 2.6.0. All three models are marked loaded=true and stored=false.

The archive preserves metadata and scores. It does not contain trained model binaries, raw report data, a database backup, exact split memberships, prediction scores or a complete executable reconstruction script.



Comparison with the published experiment

Table 6 of Gulbay and Demirci [1] distinguishes Scenario 1 (APT reports only) from Scenario 2 (reports plus external CTI enrichment). The appropriate numerical reference here is Scenario 1. The paper’s 0.9236 LR test score belongs to Scenario 2 and is not the target for this reports-only run.


| Model | Paper validation | Our validation | Paper test | Our test |
| --- | --- | --- | --- | --- |
| LR | .7179 | .7678 | .6971 | .7961 |
| RF | .5199 | .7216 | .5395 | .6788 |
| MLP | .7111 | .7713 | .6943 | .7956 |



The observed test differences are +9.90 percentage points for LR, +13.93 for RF and +10.13 for MLP. These are descriptive differences between non-equivalent experiments, not measured improvements attributable to a new method.

Reconstruction differences


| Aspect | Paper or unresolved original setting | This run |
| --- | --- | --- |
| Report coverage | 783 reports; 239 without actors [1, p. 10] | 743 reports; 255 without groups in earlier data checks |
| Link features | Creation timestamp and embedding [1, p. 9] | Embedding only; original timestamps unavailable |
| Model candidates | Multiple candidates and parameter spaces [1, p. 9] | One fixed candidate per model family |
| Split | 20% test, 20% train, seven folds [1, p. 10] | testFraction .2; trainFraction .25 of remainder |
| Negative sampling | Exact ratio not established from inspected material | One sampled negative per positive |
| Embedding settings | Exact settings not recovered | 128 dimensions; weights [0,1,1]; seed 42 |
| Graph construction | Exact historical graph not recovered | Custom baseline parsing and domain classification |



The paper’s split wording was interpreted as 20% of all target relationships for training. This corresponds to trainFraction=0.25 after removing a 20% test set under documented GDS semantics [2]. Whether the authors instead supplied trainFraction=0.2 remains unresolved. Counts are subject to implementation rounding.

The 743-report coverage and earlier per-label counts are supported by the session’s data checks, not by a row-level dataset included in this archive. Exact report identities and content equivalence cannot be independently checked from these exports.



Verified graph and pipeline configuration

The graph export confirms 58,842 nodes and 140,790 projected relationships. All three relationship types are undirected: HAS_IOC, HAS_APT_GROUP and KNOWN_AS. GDS stores both directions, so 140,790 must not be reported as that many distinct source facts. No node properties were projected from the database.


| Setting | Verified configuration |
| --- | --- |
| Prediction target | BaselineReport → HAS_APT_GROUP → BaselineGroup |
| Context | BaselineIoC nodes; HAS_IOC and KNOWN_AS links |
| FastRP | 128 dimensions; iteration weights [0,1,1] |
| Other FastRP settings | Self influence 0; normalisation strength 0; seed 42; concurrency 1 |
| Link feature | HADAMARD of paperEmbedding |
| Split | Test .2; train .25 of test complement; seven validation folds |
| Negative settings | Sampling ratio 1.0; evaluation negativeClassWeight 1.0 |
| Training | Seed 42; concurrency 1; AUCPR metric |



Model settings

LR: minimum 1 and maximum 100 epochs; learning rate 0.001; batch size 100; patience 1; tolerance 0.001; penalty 0; focus weight 0; classWeights exported as an empty list.

MLP: the same exported optimiser settings as LR, plus one hidden layer of 100 neurons. These are installed GDS defaults selected for the reconstruction, not recovered author settings.

RF: 100 trees; GINI criterion; maximum depth 2147483647; minimum split size 2; minimum leaf size 1; sample ratio 1.0. The exported candidate does not list every potentially implicit implementation default.

Each trainingParameterSpace contains exactly one non-empty family with one fixed candidate. The catalogue’s maxTrials=10 is an upper bound, not evidence of ten trials. The execution outputs reported bestTrial=1. No hyperparameter search was performed in this run.

What the metadata does not prove

The split and feature configurations match across models. Exact held-out pair membership is not exported, so an identical test set cannot be independently demonstrated from the archive alone. The seed and graph match, but metadata equality is not a substitute for saved memberships. The files also do not establish convergence, significance or prediction calibration.



Interpretation and remaining work

This is transductive relationship prediction. Reports can occur in multiple relationship partitions, unlike the earlier report-disjoint experiment. The earlier all-candidate AP results and these sampled-pair GDS AUCPR scores answer different evaluation questions and must not be shown as a simple before-and-after improvement.

Missing links are sampled as negatives; they are not verified non-attributions. With a 1:1 sampling ratio, evaluation prevalence differs sharply from ranking every candidate group. AUCPR is sensitive to the evaluation distribution, so the results do not establish deployment precision for unknown reports.

KNOWN_AS links were derived from group names appearing together in source annotations and retained as context. If such links encode information from held-out annotations, they may provide indirect label information. This is a potential leakage route requiring a provenance audit, not proof that the implementation leaked target edges. Co-occurrence also does not independently validate alias identity.

The paper describes trapezoidal precision–recall area [1, p. 9]. This run records GDS AUCPR. We have not independently recalculated that metric from saved test predictions or verified its tie handling against the authors’ implementation. It must not be relabelled as scikit-learn average precision.



References and evidence

[1] B. Gulbay and M. Demirci, “APT-scope: A novel framework to predict advanced persistent threat groups from enriched heterogeneous information network of cyber threat intelligence,” Engineering Science and Technology, an International Journal, vol. 57, 101791, 2024. doi:10.1016/j.jestch.2024.101791. Methodology pp. 8–9; Table 6 and report counts p. 10.

[2] Neo4j, Configuring the pipeline. https://neo4j.com/docs/graph-data-science/current/machine-learning/linkprediction-pipelines/config/ . Current documentation explains split semantics; installed settings were checked against the GDS 2.6.0 exports.

Primary run evidence: paper-s1-v2-evidence-20261118-020357.zip. SHA-256: 975c149e49338911e133069846aae05a31afe88162a774f0f3fd96e6380e0fb0
