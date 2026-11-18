"""New replay runner assembled from exported metadata, not the original executed script.
Requires the existing Baseline* database. Default: write a plan only; --execute trains.
Never drops database data, catalogue graphs, pipelines or models.
"""
import argparse
import json
import re
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path
from audit_results import ROOT, read

def build_plan(evidence, prefix):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', prefix):
        raise ValueError('Prefix must start with a letter and contain only letters, digits or underscores')
    graph = read(evidence/'graph-metadata.json')[0]
    config = graph['configuration']
    graph_name = prefix+'_graph'
    steps = [{'query':'CALL gds.graph.project($name, $nodes, $relationships)',
              'parameters':{'name':graph_name,'nodes':config['nodeProjection'],'relationships':config['relationshipProjection']},'save':'graph.json'}]
    methods = {'LogisticRegression':'gds.beta.pipeline.linkPrediction.addLogisticRegression',
               'RandomForest':'gds.beta.pipeline.linkPrediction.addRandomForest',
               'MultilayerPerceptron':'gds.alpha.pipeline.linkPrediction.addMLP'}
    for short in ('lr','rf','mlp'):
        pname = 'apt_paper_s1_v2' if short=='lr' else f'apt_paper_s1_{short}_pipeline_v2'
        info = read(evidence/(pname+'-pipeline.json'))[0]['pipelineInfo']
        meta = read(evidence/f'apt_paper_s1_{short}_v2-model-metadata.json')[0]
        pipeline = prefix+'_'+short+'_pipeline'
        def step(query, params, save=None):
            result={'query':query,'parameters':params}
            if save: result['save']=save
            steps.append(result)
        step('CALL gds.beta.pipeline.linkPrediction.create($name)', {'name':pipeline})
        step('CALL gds.beta.pipeline.linkPrediction.configureSplit($name, $config)', {'name':pipeline,'config':info['splitConfig']})
        for prop in info['featurePipeline']['nodePropertySteps']:
            step('CALL gds.beta.pipeline.linkPrediction.addNodeProperty($name, $procedure, $config)',
                 {'name':pipeline,'procedure':prop['name'].removeprefix('gds.'),'config':prop['config']})
        for feature in info['featurePipeline']['featureSteps']:
            step('CALL gds.beta.pipeline.linkPrediction.addFeature($name, $feature, $config)',
                 {'name':pipeline,'feature':feature['name'],'config':feature['config']})
        for family,candidates in info['trainingParameterSpace'].items():
            for candidate in candidates:
                params={k:v for k,v in candidate.items() if k!='methodName'}
                step(f'CALL {methods[family]}($name, $config)', {'name':pipeline,'config':params})
        allowed=('randomSeed','targetRelationshipType','negativeClassWeight','metrics','concurrency','sourceNodeLabel','targetNodeLabel')
        train={k:meta['trainConfig'][k] for k in allowed}
        train.update(pipeline=pipeline, modelName=prefix+'_'+short, storeModelToDisk=False)
        step('CALL gds.beta.pipeline.linkPrediction.train.estimate($graph, $config)', {'graph':graph_name,'config':train},short+'-estimate.json')
        step('CALL gds.beta.pipeline.linkPrediction.train($graph, $config)', {'graph':graph_name,'config':train},short+'-training.json')
        step('CALL gds.model.list($name)', {'name':train['modelName']},short+'-metadata.json')
    return steps

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prefix',default='replay_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S'))
    p.add_argument('--uri',default='bolt://localhost:7687');p.add_argument('--database',default='neo4j');p.add_argument('--user',default='neo4j')
    p.add_argument('--output',type=Path,default=ROOT/'runs');p.add_argument('--execute',action='store_true')
    a=p.parse_args();steps=build_plan(ROOT/'evidence/original',a.prefix)
    out=a.output/a.prefix;out.mkdir(parents=True,exist_ok=False)
    def save(name,data): (out/name).write_text(json.dumps(data,indent=2,default=str)+'\n',encoding='utf-8')
    save('plan.json',steps)
    if not a.execute:
        print('Plan only. No connection or training. Saved:',out/'plan.json');return
    from neo4j import GraphDatabase
    with GraphDatabase.driver(a.uri,auth=(a.user,getpass('Neo4j password: '))) as driver:
        def query(q,params=None):
            records,_,_=driver.execute_query(q,parameters_=params or {},database_=a.database)
            return [r.data() for r in records]
        driver.verify_connectivity()
        versions={'neo4j':query('CALL dbms.components()'),'gds':query('RETURN gds.version() AS version')}
        save('software-versions.json',versions)
        if versions['gds'][0]['version']!='2.6.0' or versions['neo4j'][0]['versions'][0]!='5.13.0':
            raise RuntimeError('Replay targets Neo4j 5.13.0 / GDS 2.6.0. Version mismatch; no training started.')
        counts=query('MATCH (n) WHERE n:BaselineReport OR n:BaselineGroup OR n:BaselineIoC RETURN count(n) AS nodes')
        rels=query('MATCH (a)-[r]->(b) WHERE (a:BaselineReport OR a:BaselineGroup OR a:BaselineIoC) AND (b:BaselineReport OR b:BaselineGroup OR b:BaselineIoC) AND type(r) IN ["HAS_IOC","HAS_APT_GROUP","KNOWN_AS"] RETURN count(r) AS relationships')
        save('preflight-counts.json',{'nodes':counts,'relationships':rels})
        if counts[0]['nodes']!=58842 or rels[0]['relationships']!=70395:
            raise RuntimeError('Database counts differ from recorded baseline. No training started. Counts alone do not prove content equality.')
        for i,step in enumerate(steps):
            result=query(step['query'],step['parameters'])
            save(step.get('save',f'step-{i:02}.json'),result)
            print(f'{i+1}/{len(steps)} completed')
    print('New run saved:',out,'Original evidence untouched. Models remain in memory.')

if __name__=='__main__':main()
