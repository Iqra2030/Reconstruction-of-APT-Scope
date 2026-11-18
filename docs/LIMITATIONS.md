# Limitations and claim boundaries

1. **Approximate reconstruction:** 743 reports were used versus 783 reported by the paper. The exact historical report manifest is unavailable here.
2. **Feature differences:** the reconstruction did not include the paper's timestamp feature. Some settings were inferred or taken from installed defaults.
3. **Split interpretation:** testFraction=0.2 and trainFraction=0.25 imply approximately 20% overall training links. The authors' exact API inputs remain unresolved.
4. **Candidate-pair task:** this is transductive link prediction. A report may occur across relationship partitions. It does not establish generalisation to entirely unseen reports or campaigns.
5. **Sampled negatives:** unrecorded associations are not verified false associations. A 1:1 negative ratio differs from ranking every possible group and changes the evaluation distribution.
6. **Alias context:** names occurring together were used to create KNOWN_AS context. This does not independently prove aliases. If held-out annotations contributed to these links, indirect label information may be present. This is a risk requiring provenance review, not proof of leakage.
7. **One candidate and one seed:** the run does not establish statistical significance, robust model ranking or an optimal hyperparameter configuration.
8. **Metric definition:** exports record GDS AUCPR. Prediction scores are absent, so tie handling and equivalence to the paper's trapezoidal calculation cannot be independently recalculated. Do not relabel this metric as average precision or accuracy.
9. **Incomplete preservation:** no trained model binaries, database snapshot, exact pair memberships or full executable historical pipeline were included. Matching exported seeds/configurations does not independently establish identical test memberships across models.
10. **No demonstrated new contribution:** the proposed STIX report classifier remains future work. Higher reconstruction scores are descriptive differences between non-equivalent experiments.

## Follow-up experiments, separately labelled

Freeze these v2 results. Audit aliases, preserve a graph snapshot and source hashes, request author artifacts, and predefine multi-seed and alias-exclusion experiments. Do not tune changes against the existing test scores and present them as corrections to the same frozen experiment.
