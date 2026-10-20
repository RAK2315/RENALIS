import unittest
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from unittest.mock import patch
import numpy as np
from backend import mechanisms as m
from backend import app as service


class PolicyAccountingTests(unittest.TestCase):
    def test_waiting_compares_against_best_immediate_action(self):
        cloud=m.base_cloud('RNL-014',90)
        w=m.normalize(cloud.log_weights)
        immediate=np.zeros((len(w),2))
        delayed=np.ones((len(w),2))
        result=m.measurement_value(cloud,w,delayed,'cardiac_output',5,
                                   immediate_losses=immediate)
        self.assertAlmostEqual(result['decision_value'],-1.,places=5)
        self.assertAlmostEqual(result['waiting_loss'],1.,places=5)
        self.assertLess(result['net_value'],-1.)

    def test_failed_acquisition_has_cost_and_no_information_value(self):
        cloud=m.base_cloud('RNL-014',90);w=m.normalize(cloud.log_weights)
        losses=np.column_stack([np.zeros(len(w)),np.ones(len(w))])
        result=m.measurement_value(cloud,w,losses,'cardiac_output',0,failure_probability=1)
        self.assertEqual(result['information_gain_bits'],0)
        self.assertEqual(result['decision_value'],0)
        self.assertLess(result['net_value'],0)

    def test_quadrature_is_checked_against_a_finer_reference(self):
        cloud=m.base_cloud('RNL-014',90);w=m.normalize(cloud.log_weights)
        losses=np.column_stack([m.decision_losses(m.project(cloud,r),cloud.removed_ml,3500) for r in [350,800,1400]])
        a=m.measurement_value(cloud,w,losses,'cardiac_output',0,quadrature_nodes=9)
        b=m.measurement_value(cloud,w,losses,'cardiac_output',0,quadrature_nodes=41)
        self.assertLess(abs(a['decision_value']-b['decision_value']),.02)


class HistoryLearningTests(unittest.TestCase):
    def test_future_sessions_and_hidden_authored_priors_are_not_inputs(self):
        from backend.history import learn
        from backend.history_fixtures import completed_sessions
        records=completed_sessions('RNL-014');baseline=learn(records)
        future={**records[0],'available_minute':10,'readings':[{'minute':0,'sbp':40,'quality':'valid'}]}
        self.assertEqual(learn((*records,future)),baseline)
        mutated=tuple({**s,'readings':[{**r,'sbp':r['sbp']+r['minute']*.1} for r in s['readings']]} for s in records)
        self.assertNotAlmostEqual(learn(mutated)['refill_l_h'],baseline['refill_l_h'])

    def test_no_history_is_an_explicit_population_cold_start(self):
        from backend.history import learn
        r=learn([])
        self.assertEqual(r['sessions_used'],0);self.assertEqual(r['refill_l_h'],.88)
        self.assertGreaterEqual(r['refill_sd'],.24)


class InvestigationConsistencyTests(unittest.TestCase):
    def test_predictive_ranges_reflect_noise_and_delayed_observation_time(self):
        from backend.insights import explain
        cloud=m.base_cloud('RNL-014',80);w=m.normalize(cloud.log_weights)
        losses=np.zeros((len(w),2))
        narrow=explain(cloud,w,losses,1,[350,650],85)[0]
        wide=explain(cloud,w,losses,4,[350,650],85)[0]
        self.assertEqual(wide['observation_minute'],85)
        for a,b in zip(narrow['families'],wide['families']):
            self.assertGreater(b['range'][2]-b['range'][0],a['range'][2]-a['range'][0])
        self.assertEqual(wide['possible_results'][0]['rate_ml_h'],350)

    def test_longitudinal_conserves_fluid_and_uses_current_evidence(self):
        from backend.longitudinal import simulate
        a=simulate('RNL-014',80,650,12,2400,800,2)
        b=simulate('RNL-014',80,650,12,2400,800,2,[{'channel':'relative_blood_volume','value':85,'available_minute':80,'source':'manual research'}])
        self.assertLess(a['mass_balance_max_error_l'],1e-9)
        self.assertEqual(len(a['rows']),2)
        self.assertNotEqual(a['rows'],b['rows'])

    def test_fhir_example_has_resolvable_references_and_no_future_observations(self):
        bundle=service.fhir_example('RNL-014',80)
        self.assertEqual(bundle['type'],'collection')
        ids={f"{e['resource']['resourceType']}/{e['resource']['id']}" for e in bundle['entry']}
        for e in bundle['entry']:
            r=e['resource']
            for k in ['subject','device']:
                if k in r:self.assertIn(r[k]['reference'],ids)
            if r['resourceType']=='Observation':
                self.assertEqual(r['valueQuantity']['code'],'mm[Hg]')
                self.assertLessEqual(int(r['id'].rsplit('-',1)[-1]),80)

    def test_transport_rejects_a_profile_it_does_not_model(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            service.LongitudinalInput(cutoff=80,rate_ml_h=650,profile='step_down')


class EvidenceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.patch=patch.object(service,'DB_PATH',Path(self.tmp.name)/'test.sqlite');self.patch.start()
        self.body=dict(cutoff=60,rate_ml_h=650,equipment='research')
        self.pid='RNL-027'
    def tearDown(self):self.patch.stop();self.tmp.cleanup()

    def test_concurrent_schema_initialization(self):
        def read(_):
            with service.connection() as db:return len(list(db.execute('PRAGMA table_info(measurements)')))
        with ThreadPoolExecutor(max_workers=8) as pool:counts=list(pool.map(read,range(16)))
        self.assertEqual(len(set(counts)),1)

    def test_failed_acquisition_is_idempotent_and_charged(self):
        body=service.MeasurementInput(**self.body,channel='cardiac_output',failure_probability=1)
        first=service.acquire_measurement(self.pid,body);again=service.acquire_measurement(self.pid,body)
        self.assertEqual(first['status'],'failed');self.assertTrue(again['reused'])
        self.assertEqual(service.released_evidence(self.pid,60),[])
        ledger=service.acquisition_log(self.pid,60)
        self.assertEqual(len(ledger),1);self.assertGreater(ledger[0]['burden'],0)

    def test_manual_evidence_can_follow_a_failed_device_without_erasing_failure(self):
        service.acquire_measurement(self.pid,service.MeasurementInput(**self.body,channel='repeat_bp',failure_probability=1))
        result=service.acquire_measurement(self.pid,service.MeasurementInput(**self.body,channel='repeat_bp',source='manual',value=130))
        self.assertEqual(result['record']['value'],130)
        self.assertEqual([r['status'] for r in service.acquisition_log(self.pid,60)],['failed','success'])
        self.assertEqual(len(service.released_evidence(self.pid,60)),1)

    def test_correction_is_append_only_and_does_not_rewrite_past(self):
        first=service.acquire_measurement(self.pid,service.MeasurementInput(**self.body,channel='repeat_bp',source='manual',value=130))
        before=service.released_evidence(self.pid,60)
        corrected=service.correct_measurement(self.pid,first['record']['id'],service.CorrectionInput(cutoff=65,value=132,reason='QA verified transcription correction'))
        self.assertEqual(service.released_evidence(self.pid,60),before)
        self.assertEqual(service.released_evidence(self.pid,65)[0]['value'],132)
        self.assertEqual(corrected['supersedes'],first['record']['id'])
        service.reset_measurements(self.pid)
        self.assertEqual(service.released_evidence(self.pid,60),[])

    def test_artifact_is_retained_but_not_assimilated(self):
        service.acquire_measurement(self.pid,service.MeasurementInput(**self.body,channel='repeat_bp',source='manual',value=40,quality='artifact'))
        result=service.compute_lab(self.pid,service.LabInput(**self.body))
        self.assertEqual(result['evidence'],[]);self.assertEqual(result['acquisition_log'][0]['status'],'artifact')
        service.save_lab(self.pid,service.SaveLabInput(**self.body,expected_revision=result['revision']))

    def test_observation_time_is_used_instead_of_release_time(self):
        cloud=m.base_cloud(self.pid,70)
        e={'channel':'repeat_bp','value':130,'available_minute':70,'observed_minute':60,'source':'manual'}
        original=m.sensor_prediction
        with patch.object(m,'sensor_prediction',wraps=original) as prediction:m.assimilate(cloud,[e])
        self.assertEqual(prediction.call_args.args[2],60)

    def test_equipment_is_enforced_server_side(self):
        from fastapi import HTTPException
        with self.assertRaises(HTTPException):service.acquire_measurement(self.pid,service.MeasurementInput(cutoff=60,rate_ml_h=650,equipment='basic',channel='cardiac_output'))

    def test_immutable_investigation_retains_previews_and_history_learning(self):
        current=service.investigation(self.pid,service.LabInput(**self.body))
        saved=service.save_lab(self.pid,service.SaveLabInput(**self.body,capture_kind='investigation',expected_revision=current['revision']))
        original=service.lab_run(self.pid,saved['id'])['result']
        self.assertEqual(original['counterevidence'],current['counterevidence'])
        self.assertEqual(original['historical_learning'],current['historical_learning'])
        self.assertEqual(original['request_settings']['equipment'],'research')
        self.assertEqual(original['request_settings']['noise_multiplier'],1)
        service.reset_measurements(self.pid)
        self.assertEqual(service.lab_run(self.pid,saved['id'])['result'],original)


if __name__=='__main__':unittest.main()
