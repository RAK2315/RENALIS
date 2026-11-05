import unittest
from backend import ehr
from backend.history import patient_history
from backend.mechanisms import base_cloud
from backend.model import snapshot


class HealthRecordTests(unittest.TestCase):
    def test_low_albumin_lowers_the_starting_refill(self):
        self.assertLess(ehr.lab_refill_prior('RNL-014'), ehr.POPULATION_REFILL_L_H)
        self.assertGreater(ehr.lab_refill_prior('RNL-027'), ehr.POPULATION_REFILL_L_H)
        self.assertEqual(ehr.lab_refill_prior('unknown'), ehr.POPULATION_REFILL_L_H)

    def test_history_shrinks_toward_the_lab_adjusted_value(self):
        memory = patient_history('RNL-014')
        self.assertEqual(memory['population_refill_l_h'], ehr.lab_refill_prior('RNL-014'))

    def test_heart_failure_and_beta_blocker_raise_the_cardiac_prior(self):
        self.assertEqual(ehr.family_prior('RNL-014'), [.25, .25, .25, .25])
        leela = ehr.family_prior('RNL-032')
        self.assertGreater(leela[2], ehr.family_prior('RNL-041')[2])
        self.assertGreater(ehr.family_prior('RNL-041')[2], .25)
        self.assertAlmostEqual(sum(leela), 1, places=3)

    def test_prior_reaches_the_cause_comparison(self):
        cloud = base_cloud('RNL-032', 0)
        self.assertEqual(cloud.prior['family_prior'], ehr.family_prior('RNL-032'))

    def test_record_is_exposed_and_genetics_marked_unused(self):
        record = snapshot('RNL-014', 90)['patient']['record']
        self.assertEqual(record['labs']['albumin_g_dl'], 3.1)
        self.assertIsNone(record['genetic_markers'])
        self.assertTrue(any(e['field'] == 'Genetic markers' and not e['used'] for e in record['effects']))


if __name__ == '__main__':
    unittest.main()


class SmartwatchTests(unittest.TestCase):
    def test_watch_stream_has_gaps_and_reaches_the_twin(self):
        import numpy as np
        from backend.model import PATIENTS, _filter, observations
        rows = observations('RNL-014')
        self.assertTrue(any(r['hr'] is None for r in rows))
        self.assertGreater(rows[200]['hr'], rows[0]['hr'])  # rises as blood volume falls
        with_watch = _filter(PATIENTS['RNL-014'], 90)
        without = _filter(PATIENTS['RNL-014'], 90, wearable=False)
        self.assertFalse(np.allclose(with_watch['plasma'], without['plasma']))

    def test_beta_blocker_blunts_heart_rate_rise(self):
        from backend.model import hr_gain
        self.assertLess(hr_gain('RNL-041'), hr_gain('RNL-014'))
