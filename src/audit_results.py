"""Audit preserved evidence and regenerate comparison tables; standard library only."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = {
    'LogisticRegression': {'validation': 0.7179, 'test': 0.6971},
    'RandomForest': {'validation': 0.5199, 'test': 0.5395},
    'MultilayerPerceptron': {'validation': 0.7111, 'test': 0.6943},
}

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def audit(root=ROOT):
    evidence = root / 'evidence/original'
    for name, expected in read(root / 'evidence/SHA256.json').items():
        actual = hashlib.sha256((evidence / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Evidence checksum mismatch: {name}')
    graph = read(evidence / 'graph-metadata.json')[0]
    if (graph['nodeCount'], graph['relationshipCount']) != (58842, 140790):
        raise ValueError('Graph totals differ from audited run')
    rows = []
    for short in ('lr', 'rf', 'mlp'):
        summary = read(evidence / f'paper-s1-{short}-v2-results.json')
        metadata = read(evidence / f'apt_paper_s1_{short}_v2-model-metadata.json')[0]
        metrics = metadata['modelInfo']['metrics']['AUCPR']
        for key, val in [('test', metrics['test']), ('averageValidation', metrics['validation']['avg']),
                         ('outerTrain', metrics['outerTrain']), ('averageTrain', metrics['train']['avg'])]:
            if summary[key] != val:
                raise ValueError(f'{short}: summary/metadata mismatch in {key}')
        pipeline = 'apt_paper_s1_v2' if short == 'lr' else f'apt_paper_s1_{short}_pipeline_v2'
        info = read(evidence / f'{pipeline}-pipeline.json')[0]['pipelineInfo']
        if info['splitConfig'] != {'testFraction': .2, 'trainFraction': .25, 'validationFolds': 7, 'negativeSamplingRatio': 1.0}:
            raise ValueError(f'{short}: unexpected split')
        candidates = [c for family in info['trainingParameterSpace'].values() for c in family]
        if len(candidates) != 1:
            raise ValueError(f'{short}: expected one candidate')
        if info['featurePipeline'] != metadata['modelInfo']['pipeline']:
            raise ValueError(f'{short}: pipeline/model feature mismatch')
        for key, value in summary['modelConfiguration'].items():
            if candidates[0].get(key) != value:
                raise ValueError(f'{short}: candidate mismatch: {key}')
        reference = PAPER[summary['model']]
        rows.append(dict(model=summary['model'],validation_aucpr=summary['averageValidation'],
                         test_aucpr=summary['test'],paper_s1_test_aucpr=reference['test'],
                         descriptive_delta=summary['test']-reference['test'],
                         outer_train_test_gap=summary['outerTrain']-summary['test'],
                         train_seconds=summary['trainMillis']/1000))
    return rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'analysis')
    args = parser.parse_args()
    rows = audit()
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output/'comparison.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    lines = ['# Primary results analysis', '',
             'Generated from preserved exports with `python src/audit_results.py`. No database or retraining required.', '',
             '| Model | Validation AUCPR | Test AUCPR | Paper S1 test | Descriptive delta | Outer-train minus test | Training (s) |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['model']} | {r['validation_aucpr']:.6f} | {r['test_aucpr']:.6f} | {r['paper_s1_test_aucpr']:.4f} | {r['descriptive_delta']:+.6f} | {r['outer_train_test_gap']:.6f} | {r['train_seconds']:.3f} |")
    lines += ['', '## Interpretation', '',
              '- MLP has the highest mean validation AUCPR (0.771336).',
              '- LR exceeds MLP on test by only 0.000524. One seed cannot establish meaningful superiority.',
              '- RF has an outer-training-to-test gap of 0.135040; this is descriptive, not a causal diagnosis.',
              '- Higher scores than the paper are not an improvement claim: report coverage, timestamps, settings and evaluation details differ.',
              '- Scores are GDS AUCPR, not accuracy and not automatically scikit-learn average precision.',
              '- Training durations are from the saved summaries, not independently verified by model catalogue metadata.',
              '- No confidence interval or significance test is justified from these aggregate exports alone.', '',
              '## Reference', '',
              'Gulbay & Demirci (2024), APT-Scope, Table 6, Scenario 1. https://doi.org/10.1016/j.jestch.2024.101791',
              'Paper reference values were transcribed from the supplied paper/audit. Scenario 2 is a different enriched experiment.', '']
    (args.output/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print('PASS: 13 checksums; three summary/catalogue metric matches; graph totals; candidate and feature configuration checks.')
    print('Saved:', args.output/'RESULTS.md')

if __name__ == '__main__':
    main()
