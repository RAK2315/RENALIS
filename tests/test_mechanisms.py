import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from fastapi import HTTPException
from backend import mechanisms as m
from backend import app as service
from backend.model import observations


class MechanismTests(unittest.TestCase):
    def result(self, **changes):
        args = dict(patient_id='RNL-014',cutoff=90,rate=650,profile='constant',channels=list(m.CHANNELS),evidence=[])
        args.update(changes)
        return m.analyze(**args)

    def test_bp_ambiguity_produces_different_intervention_predictions(self):
        a = self.result()
        self.assertTrue(a['comparison_unresolved'])
        self.assertTrue(all(f['fit_rmse_mm_hg'] < 3 for f in a['families']))
        self.assertGreater(max(f['alternative_effect_mm_hg'] for f in a['families'])-min(f['alternative_effect_mm_hg'] for f in a['families']),10)
        self.assertGreaterEqual(len({f['preferred_rate_ml_h'] for f in a['families']}),2)

    def test_future_data_and_hidden_fixture_never_enter_selection(self):
        m.base_cloud.cache_clear()
        expected=self.result()
        changed=tuple({**r,'sbp':200.,'uf_ml_h':300} if r['minute']>90 else r for r in observations('RNL-014'))
        m.base_cloud.cache_clear()
        with patch('backend.mechanisms.observations',return_value=changed), patch('backend.measurement_fixtures.acquire_fixture',side_effect=AssertionError('hidden measurement accessed')):
            other=self.result()
        self.assertEqual(expected,other)
        m.base_cloud.cache_clear()

    def test_measurement_has_decision_value_and_bp_can_be_uninformative(self):
        a=self.result()
        bp=next(c for c in a['measurement_candidates'] if c['channel']=='repeat_bp' and c['offset_minutes']==0)
        self.assertLess(bp['decision_value'],.001)
        best=max(a['measurement_candidates'],key=lambda c:c['net_value'])
        self.assertEqual(a['recommended_measurement'],best if best['net_value']>.001 else None)
        self.assertTrue(any(c['information_gain_bits']>.1 for c in a['measurement_candidates']))
        self.assertTrue(all('noise_sd' in c for c in a['measurement_candidates']))
        unavailable=self.result(channels=[])
        self.assertIsNone(unavailable['recommended_measurement'])
        self.assertTrue(unavailable['comparison_unresolved'])
        expensive=self.result(burden_weight=3)
        self.assertIsNone(expensive['recommended_measurement'])

    def test_information_gain_is_not_equated_with_decision_value(self):
        cloud=m.base_cloud('RNL-014',90)
        weights=m.normalize(cloud.log_weights)
        # Information can identify a family even when every family prefers action 0.
        losses=np.column_stack([np.zeros(len(weights)),np.ones(len(weights))])
        result=m.measurement_value(cloud,weights,losses,'cardiac_output',0)
        self.assertGreater(result['information_gain_bits'],.5)
        self.assertEqual(result['decision_value'],0.)
        self.assertLess(result['net_value'],0.)

    def test_evidence_is_released_by_time_and_contradiction_downgrades(self):
        future={'id':1,'channel':'relative_blood_volume','value':85.,'source':'manual','available_minute':95}
        a=self.result(evidence=[future])
        self.assertEqual(a['evidence'],[])
        self.assertEqual(a['families'],self.result()['families'])
        measured={**future,'available_minute':90}
        b=self.result(evidence=[measured])
        self.assertGreater(b['families'][0]['weight'],a['families'][0]['weight'])
        self.assertFalse(any(c['channel']=='relative_blood_volume' and c['offset_minutes']==0 for c in b['measurement_candidates']))
        impossible=self.result(evidence=[{**measured,'value':120.}])
        self.assertEqual(impossible['authority'],'contradicted')
        self.assertIsNone(impossible['recommended_measurement'])
        self.assertTrue(impossible['evidence'][0]['contradiction'])

    def test_guard_states_and_end_horizon(self):
        for pid,cutoff,state in [('RNL-014',120,'current_event'),('RNL-032',90,'stale'),('RNL-027',240,'complete')]:
            a=self.result(patient_id=pid,cutoff=cutoff)
            self.assertEqual(a['authority'],state)
            self.assertEqual(a['measurement_candidates'],[])
            self.assertEqual(a['trajectories'],[])
            self.assertEqual(a['landscape'],[])
            self.assertTrue(all(f['preferred_rate_ml_h'] is None for f in a['families']))
            self.assertIsNone(a['carry_over'])
        near=self.result(patient_id='RNL-027',cutoff=235)
        self.assertEqual(near['horizon'],5)
        self.assertTrue(all(c['offset_minutes']<=5 for c in near['measurement_candidates']))

    def test_stepdown_at_current_rate_keeps_constant_factual_reference(self):
        cloud=m.base_cloud('RNL-014',90)
        a=self.result(rate=cloud.current_rate,profile='step_down')
        self.assertTrue(any(f['alternative_effect_mm_hg']>0 for f in a['families']))
        for f,constant in zip(a['families'],self.result(rate=cloud.current_rate)['families']):
            self.assertEqual(f['current_end_sbp'],constant['current_end_sbp'])
        self.assertEqual(a['landscape'][a['selected_rate_index']]['profile'],'step_down')

    def test_delayed_measurement_cannot_retroactively_change_removal(self):
        cloud=m.base_cloud('RNL-014',90)
        delayed=m.project(cloud,350,delay_minutes=10)
        factual=m.project(cloud,cloud.current_rate)
        np.testing.assert_allclose(delayed['bp'][:11],factual['bp'][:11])
        np.testing.assert_allclose(delayed['removed'][:11],factual['removed'][:11])
        self.assertLess(delayed['removed'][-1,0],factual['removed'][-1,0])

    def test_pressure_origin_advances_between_cuff_readings(self):
        at_cuff=m.base_cloud('RNL-014',90)
        later=m.base_cloud('RNL-014',93)
        expected=m.project(at_cuff,at_cuff.current_rate,horizon=3)['bp'][-1]
        np.testing.assert_allclose(later.anchor,expected,rtol=1e-12)
        self.assertTrue(np.all(later.anchor<at_cuff.anchor))

    def test_noise_and_burden_assumptions_affect_measurement_value(self):
        cloud=m.base_cloud('RNL-014',90)
        weights=m.normalize(cloud.log_weights)
        losses=np.column_stack([m.decision_losses(m.project(cloud,r),cloud.removed_ml,2600) for r in (350,650,1400)])
        exact=m.measurement_value(cloud,weights,losses,'cardiac_output',0)
        with patch.dict(m.CHANNELS['cardiac_output'],noise=10.):
            noisy=m.measurement_value(cloud,weights,losses,'cardiac_output',0)
        self.assertGreater(exact['information_gain_bits'],noisy['information_gain_bits'])
        self.assertGreaterEqual(exact['decision_value'],noisy['decision_value'])

    def test_a_discriminating_observation_can_produce_conditional_agreement(self):
        a=self.result(evidence=[{'id':1,'channel':'cardiac_output','available_minute':90,'value':5.1,'source':'manual'}])
        self.assertEqual(a['authority'],'inspect')
        self.assertGreater(a['families'][1]['weight'],.75)
        self.assertTrue(a['comparison_unresolved'])  # Mixed support remains; do not force agreement.


class ChallengeTests(unittest.TestCase):
    def test_independent_policies_share_budget_and_keep_all_failures(self):
        from backend.challenges import run_challenges
        report=run_challenges()
        self.assertEqual(len(report['records']),report['cases']*3)
        self.assertEqual(report['observation_budget'],1)
        self.assertTrue(all(c['passed'] for c in report['safeguards']))
        for row in report['records']:
            self.assertGreaterEqual(row['regret'],0)
            self.assertLessEqual(row['burden'],.055)
        self.assertEqual({r['cases'] for r in report['summaries']},{108})
        # Improvement is not an acceptance assertion: preserve negative results.
        self.assertTrue(any(r['worse_than_bp_only']>0 for r in report['summaries']))


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.patcher=patch.object(service,'DB_PATH',Path(self.tmp.name)/'test.sqlite')
        self.patcher.start()
        self.pid='RNL-014'
        self.body=dict(cutoff=90,rate_ml_h=650,channels=list(m.CHANNELS))

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def test_delayed_release_archive_audit_and_immutable_save(self):
        record=service.acquire_measurement(self.pid,service.MeasurementInput(**self.body,channel='relative_blood_volume',offset_minutes=5))
        self.assertEqual(record['available_minute'],95)
        self.assertEqual(service.released_evidence(self.pid,90),[])
        released=service.released_evidence(self.pid,95)
        self.assertEqual(len(released),1)
        args=service.LabInput(**{**self.body,'cutoff':95})
        result=service.compute_lab(self.pid,args)
        saved=service.save_lab(self.pid,service.SaveLabInput(**args.model_dump(),expected_revision=result['revision']))
        service.reset_measurements(self.pid)
        self.assertEqual(service.released_evidence(self.pid,95),[])
        report=service.lab_run(self.pid,saved['id'])
        self.assertEqual(report['result']['revision'],result['revision'])
        self.assertEqual(len(report['result']['evidence']),1)
        with self.assertRaises(HTTPException) as error:
            service.save_lab(self.pid,service.SaveLabInput(**args.model_dump(),expected_revision=result['revision']))
        self.assertEqual(error.exception.status_code,409)
        with service.connection() as db:
            self.assertEqual(db.execute('SELECT active FROM measurements').fetchone()[0],0)

    def test_acquisition_is_idempotent_and_unavailable_channel_rejected(self):
        body=service.MeasurementInput(**self.body,channel='cardiac_output')
        first=service.acquire_measurement(self.pid,body)
        second=service.acquire_measurement(self.pid,body)
        self.assertEqual(first['record']['id'],second['record']['id'])
        self.assertTrue(second['reused'])
        with self.assertRaises(HTTPException) as error:
            service.acquire_measurement(self.pid,service.MeasurementInput(**{**self.body,'channels':[]},channel='repeat_bp'))
        self.assertEqual(error.exception.status_code,409)

    def test_bad_manual_values_rejected_and_patient_records_isolated(self):
        with self.assertRaises(HTTPException) as error:
            service.acquire_measurement(self.pid,service.MeasurementInput(**self.body,channel='cardiac_output',source='manual',value=99))
        self.assertEqual(error.exception.status_code,422)
        result=service.compute_lab(self.pid,service.LabInput(**self.body))
        saved=service.save_lab(self.pid,service.SaveLabInput(**self.body,expected_revision=result['revision']))
        with self.assertRaises(HTTPException) as error:
            service.lab_run('RNL-027',saved['id'])
        self.assertEqual(error.exception.status_code,404)

    def test_original_workspace_withholds_current_event_scenarios(self):
        for operation in (service.compare,service.save_branch):
            with self.assertRaises(HTTPException) as error:
                operation(self.pid,service.ScenarioInput(cutoff=120,rate_ml_h=650))
            self.assertEqual(error.exception.status_code,409)

    def test_landing_example_is_read_only_and_independent_of_workspace_evidence(self):
        service.demo_example.cache_clear()
        service.acquire_measurement(self.pid,service.MeasurementInput(**self.body,channel='cardiac_output'))
        with patch.object(service,'released_evidence',side_effect=AssertionError('landing used acquired evidence')):
            example=service.demo_example()
        self.assertEqual(example['evidence'],[])
        self.assertEqual(example['authority'],'inspect')
        self.assertAlmostEqual(sum(f['weight'] for f in example['families']),1.,places=3)
        self.assertEqual(len(example['families']),4)
        self.assertEqual(len(service.released_evidence(self.pid,90)),1)

    def test_project_documents_are_allowlisted_and_exist(self):
        documents=service.project_documents()
        self.assertGreaterEqual(len(documents),9)
        for record in documents:
            response=service.project_document(record['id'])
            self.assertTrue(Path(response.path).is_file())
            self.assertEqual(response.headers['x-content-type-options'],'nosniff')
        for invalid in ('../LICENSE','app.py','renalis.sqlite','unknown'):
            with self.assertRaises(HTTPException) as error:
                service.project_document(invalid)
            self.assertEqual(error.exception.status_code,404)


if __name__=='__main__':
    unittest.main()
