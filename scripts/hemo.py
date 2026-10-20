"""Download, audit, and benchmark HEMOBP without using future session fields.

Run: python scripts/hemo.py download
     python scripts/hemo.py evaluate
Dataset units/cadence must be audited before fitting a physiological twin.
"""
from pathlib import Path
import argparse
import json
import hashlib
import urllib.request
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.metrics import mean_absolute_error, precision_recall_curve, average_precision_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'hemo'
MODELS = ROOT / 'data' / 'models'
FILES = {'idp.csv': '15142154', 'd1.csv': '15142151', 'vip.csv': '15142157'}
CHECKSUMS = {'idp.csv': '31d269f59bf4acc719f392ad9164d08a', 'd1.csv': '7db3b48bae2c73e3ecd731dbcd452233', 'vip.csv': 'ff1589610cf7aa3b3e01ba979b6bdc44'}


def validate_file(path):
    digest = hashlib.md5()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    if digest.hexdigest() != CHECKSUMS[path.name]:
        raise SystemExit(f'Checksum mismatch for {path.name}; investigate the local file before proceeding')


def download():
    DATA.mkdir(parents=True, exist_ok=True)
    for name, file_id in FILES.items():
        destination = DATA / name
        if destination.exists():
            validate_file(destination)
            print(f'{name}: existing file retained')
            continue
        print(f'Downloading {name}...', flush=True)
        temporary = destination.with_suffix('.part')
        with urllib.request.urlopen(f'https://ndownloader.figshare.com/files/{file_id}', timeout=90) as response, temporary.open('wb') as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        temporary.replace(destination)
        validate_file(destination)
        print(f'{name}: {destination.stat().st_size:,} bytes', flush=True)


def evaluate():
    for name in FILES:
        if not (DATA / name).exists():
            raise SystemExit('Download the versioned data first: python scripts/hemo.py download')
        validate_file(DATA / name)
    print('Reading observed patient and machine tables...', flush=True)
    idp = pd.read_csv(DATA/'idp.csv', dtype={'pid': str})
    vip = pd.read_csv(DATA/'vip.csv', dtype={'pid': str}, low_memory=False)
    required = {'pid','datatime','measuretime','sbp','dbp','uf','blood_flow','time','dia_temp_value','conductivity'}
    if not required.issubset(vip.columns):
        raise SystemExit(f'Unexpected machine schema: missing {required - set(vip.columns)}')
    input_rows = len(vip)
    vip['timestamp'] = pd.to_datetime(vip['datatime'], errors='coerce')
    vip = vip.dropna(subset=['pid','timestamp','measuretime','time','sbp'])
    vip = vip[(vip.sbp.between(30,220)) & (vip.time.between(0,300))].sort_values(['pid','timestamp'])
    # Infer episode boundaries from large time gaps or resets in elapsed session time.
    # This avoids splitting midnight-crossing sessions at calendar-day boundaries.
    group = vip.groupby('pid', sort=False)
    gap = group.timestamp.diff().dt.total_seconds().div(3600)
    reset = group['time'].diff() < -30
    boundary = gap.isna() | (gap > 6) | reset
    vip['episode'] = boundary.groupby(vip.pid).cumsum().astype(int)
    # The same BP is repeated in multiple machine packets. Take its first appearance,
    # retaining only contemporaneous settings, rather than the last future packet.
    readings = vip.drop_duplicates(['pid','episode','measuretime'], keep='first').copy()
    readings = readings.merge(idp[['pid','birthday','DM','gender']], on='pid', how='inner', validate='many_to_one')
    readings['age'] = readings.timestamp.dt.year - pd.to_numeric(readings.birthday, errors='coerce')
    readings['diabetes'] = pd.to_numeric(readings.DM, errors='coerce')
    readings['female'] = (readings.gender == 'F').astype(int)
    readings = readings[readings.age.between(18,100)].sort_values(['pid','episode','timestamp'])
    g = readings.groupby(['pid','episode'], sort=False)
    readings['previous_sbp'] = g.sbp.shift()
    readings['previous_minutes'] = (readings.timestamp - g.timestamp.shift()).dt.total_seconds().div(60)
    readings['trend_mm_hg_min'] = (readings.sbp-readings.previous_sbp) / readings.previous_minutes.replace(0,np.nan)
    readings['next_sbp'] = g.sbp.shift(-1)
    readings['next_minutes'] = (g.timestamp.shift(-1)-readings.timestamp).dt.total_seconds().div(60)
    # Labels are created from the next distinct BP, never from held-forward values.
    cohort = readings[(readings.sbp > 90) & readings.next_minutes.between(5,35)].copy()
    cohort = cohort.dropna(subset=['next_sbp'])
    if cohort.pid.nunique() < 10 or len(cohort) < 1000:
        raise SystemExit('Not enough eligible distinct BP observations for an observed-data baseline')
    train_idx, test_idx = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=42).split(cohort, groups=cohort.pid))
    train, test = cohort.iloc[train_idx].copy(), cohort.iloc[test_idx].copy()
    if len(train) > 100000:
        train = train.sample(100000, random_state=42)
    dynamic = ['sbp','dbp','uf','blood_flow','time','dia_temp_value','conductivity','trend_mm_hg_min','previous_minutes']
    fused = dynamic + ['age','diabetes','female']
    scores = []
    scores.append({'label': 'Last observed BP', 'mae_mm_hg': round(mean_absolute_error(test.next_sbp,test.sbp),3)})
    for label, columns in [('Dynamic-only baseline',dynamic),('Historical + dynamic baseline',fused)]:
        model = HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=20,l2_regularization=8,learning_rate=.08,random_state=42)
        model.fit(train[columns],train.next_sbp)
        predicted = model.predict(test[columns])
        scores.append({'label':label,'mae_mm_hg':round(mean_absolute_error(test.next_sbp,predicted),3)})
        MODELS.mkdir(parents=True,exist_ok=True)
        joblib.dump({'model':model,'features':columns},MODELS/('hemo_fused.joblib' if columns == fused else 'hemo_dynamic.joblib'))
    print('Fitting the next-low-BP event baseline with a separate patient-held-out threshold-validation set...', flush=True)
    fit_idx, validation_idx = next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=43).split(train,groups=train.pid))
    fit, validation = train.iloc[fit_idx], train.iloc[validation_idx]
    classifier = HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=16,l2_regularization=12,learning_rate=.08,random_state=42)
    classifier.fit(fit[fused],(fit.next_sbp<=90).astype(int))
    validation_scores = classifier.predict_proba(validation[fused])[:,1]
    precisions, recalls, thresholds = precision_recall_curve((validation.next_sbp<=90).astype(int),validation_scores)
    eligible = np.where(recalls[:-1]>=.75)[0]
    threshold = float(thresholds[eligible[-1]]) if len(eligible) else .5
    event_scores = classifier.predict_proba(test[fused])[:,1]
    event_truth = (test.next_sbp<=90).astype(int)
    predicted_events = event_scores >= threshold
    event_result = {'endpoint':'Next distinct measured SBP ≤90 mmHg; current SBP >90; gap 5–35 minutes',
                    'threshold_selected_on':'Patient-disjoint validation set; target recall at least 0.75',
                    'validation_patients':int(validation.pid.nunique()),'classifier_fit_patients':int(fit.pid.nunique()),
                    'test_sensitivity':round(recall_score(event_truth,predicted_events),3),
                    'test_ppv':round(precision_score(event_truth,predicted_events,zero_division=0),3),
                    'test_pr_auc':round(average_precision_score(event_truth,event_scores),3),
                    'test_false_positive_windows':int(((~event_truth.astype(bool))&predicted_events).sum()),
                    'test_positive_windows':int(event_truth.sum()),'score_threshold':round(threshold,5),
                    'score_calibration':'Raw classifier scores; clinical probability calibration not evaluated',
                    'alert_accounting':'Window-level results; not consolidated patient-day alert burden'}
    joblib.dump({'model':classifier,'features':fused,'threshold':threshold},MODELS/'hemo_event.joblib')
    result = {'status':'evaluated','dataset':'HEMOBP v3 · Taiwan retrospective observations',
              'source':'https://figshare.com/articles/dataset/Hemrec_VIP_csv/6260654/3','license':'CC BY 4.0',
              'input_machine_rows':input_rows,'distinct_bp_rows':len(readings),'eligible_windows':len(cohort),
              'train_rows_used':len(train),'test_rows':len(test),'train_patients':int(train.pid.nunique()),'test_patients':int(test.pid.nunique()),
              'patient_overlap':int(len(set(train.pid)&set(test.pid))),
              'test_next_low_bp_windows':int((test.next_sbp<=90).sum()),
              'median_next_reading_minutes':round(float(test.next_minutes.median()),2),
              'models':scores,'event_model':event_result,'task':'Next distinct BP regression for elapsed gaps 5–35 minutes; current SBP >90',
              'cleaning':{'sbp_range_mm_hg':[30,220],'elapsed_session_range_minutes':[0,300],'checksums':'Verified against HEMOBP v3 deposit'},
              'limitations':['Retrospective single-deposit benchmark, not prospective clinical validation.',
                'Episodes inferred from elapsed-time resets and timestamp gaps; needs independent session audit.',
                'Repeated measurement IDs collapsed to their first occurrence.',
                'Machine ultrafiltration field used in source units; physiological unit reconciliation remains required.',
                'No post-session weights or future machine-setting changes used as predictor inputs.',
                'No external country validation; alerts and scenario effects not clinically validated.',
                'd1.csv downloaded for the later session audit; weightend is deliberately excluded.',
                'This baseline has not been integrated into the synthetic particle-twin forecast.']}
    (MODELS/'hemo_metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['download','evaluate'])
    args=parser.parse_args()
    download() if args.command == 'download' else evaluate()
