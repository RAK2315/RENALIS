"""Verify published aggregate/report contracts without downloading patient data."""
import hashlib,json,zipfile
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))

policy=read('docs/policy-validation-v04.json');rows=policy['records']
assert len(rows)==768 and policy['cases']==192
assert all(n==4 for n in Counter(r['case'] for r in rows).values())
for summary in policy['summaries']:
    selected=[r for r in rows if r['policy']==summary['policy']]
    assert len(selected)==192
    assert abs(sum(r['regret'] for r in selected)/192-summary['mean_regret'])<.000011
    assert abs(sum(r['total_policy_regret'] for r in selected)/192-summary['mean_total_policy_regret'])<.000011
    assert sum(r['failed'] for r in selected)==summary['failures']
    assert all(abs(r['total_policy_regret']-r['regret']-r['burden']-r['wait_minutes']*.002)<.000002 for r in selected)
assert policy['analysis_amendment']['policy_unchanged']
expected=hashlib.sha256(json.dumps(policy['protocol'],sort_keys=True).encode()).hexdigest()
assert expected==policy['protocol_sha256']

observed=read('docs/observed-v04.json')
assert observed['split']['patient_overlap']==0
assert observed['audit']['matched_machine_rows']+observed['audit']['unmatched_or_outside_interval_rows']==observed['audit']['input_machine_rows']
assert observed['audit']['current_session_end_fields_excluded']
assert observed['audit']['history_end_before_current_start']
assert 'assumption' in observed['audit']['clock_offset_status']

files=['README.md','LICENSE','THIRD_PARTY_NOTICES.md','docs/model-card.md','docs/clinical-study-protocol.md',
       'docs/data-capture-schema.json','docs/submission-checklist.md','docs/implementation-decisions-v04.md',
       'docs/demo-walkthrough-v04.md','output/pdf/RENALIS_Architecture_v04.pdf',
       'output/pdf/RENALIS_Project_Presentation_v04.pdf','output/pdf/RENALIS_Research_Strategy_and_Master_Plan.pdf']
for f in files:assert (ROOT/f).stat().st_size>100,f
for name,count in [('RENALIS_Architecture_v04_Final.pptx',3),('RENALIS_Project_Presentation_v04_Final.pptx',16)]:
    with zipfile.ZipFile(ROOT/'output/presentations'/name) as z:
        assert len([n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')])==count
        assert len([n for n in z.namelist() if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml')])==count
        if count==16:assert len([n for n in z.namelist() if n.endswith('.xlsx')])==2
manifest={'status':'passed','policy_records':len(rows),'policy_cases':192,'observed_test_windows':observed['test_rows'],
          'administrative_publication_verified':False,'clinical_validation_completed':False,
          'files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}}
out=ROOT/'artifacts/qa/release-verification.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(manifest,indent=2));print('Release contracts, 768 policy records, observed audit and submission documents verified.')
