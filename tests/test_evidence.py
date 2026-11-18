import sys,tempfile,unittest,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from audit_results import ROOT,audit
from replay_training import build_plan
class EvidenceTests(unittest.TestCase):
    def test_verified_metrics(self):
        rows=audit();self.assertEqual(len(rows),3)
        self.assertEqual(max(rows,key=lambda r:r['validation_aucpr'])['model'],'MultilayerPerceptron')
    def test_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copytree(ROOT/'evidence',root/'evidence')
            f=root/'evidence/original/graph-metadata.json';f.write_text('[]')
            with self.assertRaisesRegex(ValueError,'checksum'):audit(root)
    def test_replay_excludes_runtime_metadata(self):
        steps=build_plan(ROOT/'evidence/original','test_replay')
        trains=[s for s in steps if s['query']=='CALL gds.beta.pipeline.linkPrediction.train($graph, $config)']
        self.assertEqual(len(trains),3)
        for s in trains:
            self.assertNotIn('jobId',s['parameters']['config'])
            self.assertFalse(s['parameters']['config']['storeModelToDisk'])
        self.assertFalse(any('DELETE' in s['query'] or '.drop(' in s['query'] for s in steps))
    def test_bad_prefix_rejected(self):
        with self.assertRaises(ValueError):build_plan(ROOT/'evidence/original','bad prefix')
if __name__=='__main__':unittest.main()
