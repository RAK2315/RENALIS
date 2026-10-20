import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from backend import app as service, mechanisms as m
from backend.discrimination import plan, score


class SequentialDiscriminationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = patch.object(service, 'DB_PATH', Path(self.tmp.name)/'test.sqlite')
        self.db.start()
        self.body = dict(cutoff=90, rate_ml_h=650, equipment='research')
        self.pid = 'RNL-014'

    def tearDown(self):
        self.db.stop()
        self.tmp.cleanup()

    def investigate(self, **settings):
        return service.investigation(self.pid, service.LabInput(**{**self.body, **settings}))

    def acquire(self, channel, **settings):
        return service.acquire_measurement(self.pid, service.MeasurementInput(**{**self.body, **settings}, channel=channel))

    def test_actual_sequential_acquisition_selects_rbv_without_a_manual_number(self):
        initial = self.investigate()['discrimination_plan']
        self.assertEqual(initial['objective'], 'whole_bank')
        self.assertEqual(initial['recommended']['channel'], 'cardiac_output')
        first = self.acquire('cardiac_output')
        self.assertEqual(first['record']['value'], 3.74)
        current = self.investigate()
        p = current['discrimination_plan']
        self.assertEqual(p['objective'], 'pair')
        self.assertEqual({r['id'] for r in p['pair']}, {'volume', 'cardiac'})
        self.assertEqual(p['recommended']['channel'], 'relative_blood_volume')
        self.assertIsNone(current['recommended_measurement'])  # Different objective.
        candidates = {c['channel']:c for c in p['candidates']}
        self.assertGreater(candidates['relative_blood_volume']['pair_information_bits'], .35)
        self.assertLess(candidates['repeat_bp']['pair_information_bits'], .001)
        second = self.acquire(p['recommended']['channel'], offset_minutes=p['recommended']['offset_minutes'])
        self.assertEqual(second['record']['value'], 85.)
        after = self.investigate()
        self.assertTrue(after['comparison_unresolved'])
        self.assertGreater(after['families'][0]['weight'], .65)
        self.assertGreater(after['families'][2]['weight'], .30)
        self.assertEqual(after['discrimination_plan']['latest_evidence']['value'], 85.)
        self.assertNotEqual(after['discrimination_plan']['recommended']['offset_minutes'], 0)

    def test_selection_cannot_look_at_device_fixture_or_future_reading(self):
        self.acquire('cardiac_output')
        baseline = self.investigate()['discrimination_plan']
        with patch('backend.app.acquire_fixture', side_effect=AssertionError('Fixture leaked into planning')):
            self.assertEqual(self.investigate()['discrimination_plan'], baseline)
        cloud = m.base_cloud(self.pid,90)
        evidence = service.released_evidence(self.pid,90)
        future = {'id':99,'channel':'relative_blood_volume','value':120,'available_minute':100,'source':'manual'}
        w,_ = m.assimilate(cloud,evidence)
        future_w,_ = m.assimilate(cloud,evidence+[future])
        np.testing.assert_array_equal(w,future_w)

    def test_noise_failure_and_equipment_change_planning(self):
        self.acquire('cardiac_output')
        narrow = self.investigate()['discrimination_plan']['recommended']
        wide = self.investigate(noise_multiplier=4)['discrimination_plan']['recommended']
        self.assertLess(wide['pair_information_bits'],narrow['pair_information_bits'])
        self.assertGreater(wide['ranges'][0]['range'][2]-wide['ranges'][0]['range'][0],narrow['ranges'][0]['range'][2]-narrow['ranges'][0]['range'][0])
        failed = self.investigate(failure_probability=1)['discrimination_plan']
        self.assertIsNone(failed['recommended'])
        self.assertTrue(all(c['pair_information_bits']==0 for c in failed['candidates']))
        basic = self.investigate(equipment='basic')['discrimination_plan']
        self.assertEqual([c['channel'] for c in basic['candidates']],['repeat_bp'])
        self.assertIsNone(basic['recommended'])

    def test_all_recommendations_are_feasible_and_current_slot_is_not_reused(self):
        self.acquire('cardiac_output')
        r = self.investigate()
        feasible = {(c['channel'],c['offset_minutes']) for c in r['measurement_candidates']}
        for c in r['discrimination_plan']['candidates']:
            self.assertIn((c['channel'],c['offset_minutes']),feasible)
            if c['channel']=='cardiac_output': self.assertGreater(c['offset_minutes'],0)
        cloud = m.base_cloud(self.pid,90)
        w,_ = m.assimilate(cloud,service.released_evidence(self.pid,90))
        pending = {**r, 'acquisition_log': r['acquisition_log'] + [
            {'channel':'relative_blood_volume','available_minute':90,'request_cutoff':85,'active':1,'status':'pending'}]}
        self.assertFalse(any(c['channel']=='relative_blood_volume' and c['offset_minutes']==0
                             for c in plan(cloud,w,pending)['candidates']))
        # Failure is a charged, idempotent request; don't suggest the same click.
        self.acquire('relative_blood_volume',failure_probability=1)
        p = self.investigate()['discrimination_plan']
        self.assertFalse(any(c['channel']=='relative_blood_volume' and c['offset_minutes']==0 for c in p['candidates']))

    def test_preview_weights_match_actual_bayesian_update_at_displayed_value(self):
        self.acquire('cardiac_output')
        current = self.investigate()
        r = current['discrimination_plan']['recommended']
        cloud = m.base_cloud(self.pid,90)
        evidence = service.released_evidence(self.pid,90)
        for example in r['examples']:
            w,_ = m.assimilate(cloud,evidence+[{'id':99,'channel':r['channel'],'value':example['value'],
                'available_minute':r['observation_minute'],'observed_minute':r['observation_minute'],
                'noise_sd':r['noise_sd'],'source':'hypothetical'}])
            np.testing.assert_allclose(m.family_mass(w),example['family_weights'],atol=.000051)

    def test_quadrature_and_failure_mixture_are_consistent(self):
        self.acquire('cardiac_output')
        current = self.investigate()
        c = current['discrimination_plan']['recommended']
        cloud = m.base_cloud(self.pid,90)
        w,_ = m.assimilate(cloud,service.released_evidence(self.pid,90))
        pair = np.argsort(-m.family_mass(w))[:2]
        fine = score(cloud,w,c,pair,quadrature_nodes=41)
        self.assertLess(abs(fine['pair_information_bits']-c['pair_information_bits']),.002)
        failed = score(cloud,w,c,pair,failure_probability=.25)
        self.assertAlmostEqual(failed['pair_information_bits'],.75*c['pair_information_bits'],places=5)
        self.assertAlmostEqual(failed['pair_error_after'],.75*c['pair_error_after']+.25*c['pair_error_before'],places=5)

    def test_guards_exhaustion_and_concentration_do_not_force_an_experiment(self):
        self.assertEqual(self.investigate(cutoff=120)['discrimination_plan']['status'],'withheld')
        cloud = m.base_cloud(self.pid,90)
        w,_ = m.assimilate(cloud,[])
        analysis = m.analyze(self.pid,90,650,'constant',[],[])
        self.assertEqual(plan(cloud,w,analysis)['status'],'no_discriminator')
        concentrated = np.zeros(len(w));concentrated[:m.N]=1/m.N
        self.assertEqual(plan(cloud,concentrated,analysis)['status'],'supported')

    def test_immutable_report_captures_adaptive_plan_and_original_evidence(self):
        self.acquire('cardiac_output')
        current = self.investigate()
        saved = service.save_lab(self.pid, service.SaveLabInput(**self.body,capture_kind='investigation',expected_revision=current['revision']))
        self.acquire('relative_blood_volume')
        stored = service.lab_run(self.pid,saved['id'])['result']
        self.assertEqual(stored['discrimination_plan'],current['discrimination_plan'])
        self.assertEqual(stored['discrimination_plan']['latest_evidence']['value'],3.74)


if __name__ == '__main__':
    unittest.main()
