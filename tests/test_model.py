import unittest
from unittest.mock import patch
import numpy as np
from backend.model import advance, observations, snapshot, scenario, PATIENTS, _filter


class TwinModelTests(unittest.TestCase):
    def test_conservation_and_nonnegative_compartments(self):
        plasma, tissue, removed = np.array([2.9, 3.5]), np.array([2.2, 3.8]), np.zeros(2)
        total = plasma + tissue + removed
        for _ in range(240):
            plasma, tissue, removed = advance(plasma, tissue, removed, np.array([.5, .9]),
                                             np.array([2.9, 3.5]), np.array([2.2, 3.8]), 1400)
            np.testing.assert_allclose(plasma + tissue + removed, total, atol=1e-12)
            self.assertTrue(np.all(plasma >= 0) and np.all(tissue >= 0))

    def test_future_observations_cannot_change_current_posterior(self):
        p = PATIENTS['RNL-014']
        baseline = _filter(p, 90)
        altered = tuple({**r, 'sbp': 50., 'uf_ml_h': 1400} if r['minute'] > 90 else r for r in observations(p.id))
        with patch('backend.model.observations', return_value=altered):
            other = _filter(p, 90)
        for key in ('plasma', 'tissue', 'refill', 'baseline'):
            np.testing.assert_array_equal(baseline[key], other[key])

    def test_stale_readings_abstain_and_already_low_is_not_advance_alert(self):
        stale = snapshot('RNL-032', 90)
        self.assertEqual(stale['alert']['status'], 'insufficient')
        self.assertIsNone(stale['alert']['crossing_fraction'])
        low = snapshot('RNL-014', 120)
        self.assertEqual(low['alert']['status'], 'current_event')
        self.assertIsNone(low['alert']['crossing_fraction'])

    def test_projection_stops_at_session_end(self):
        near_end = snapshot('RNL-027', 230)
        self.assertEqual(near_end['horizon'], 10)
        self.assertEqual(near_end['forecast']['trajectory'][-1]['minute'], 240)
        end = snapshot('RNL-027', 240)
        self.assertEqual(end['alert']['status'], 'complete')
        self.assertEqual(end['horizon'], 0)

    def test_scenario_preserves_twin_start_and_exposes_fluid_tradeoff(self):
        slow, fast = scenario('RNL-014', 90, 500, 'constant'), scenario('RNL-014', 90, 1200, 'constant')
        self.assertEqual(slow['trajectory'][0], fast['trajectory'][0])
        self.assertGreater(slow['remaining_target_ml'], fast['remaining_target_ml'])
        self.assertGreater(slow['final']['sbp'], fast['final']['sbp'])
        original = snapshot('RNL-014', 90)
        self.assertEqual(original['cutoff'], 90)

    def test_historical_prior_reaches_the_algorithm(self):
        p = PATIENTS['RNL-014']
        fused, population = _filter(p, 40, history=True), _filter(p, 40, history=False)
        self.assertNotAlmostEqual(float(np.mean(fused['refill'])), float(np.mean(population['refill'])), places=4)

    def test_replay_has_only_available_readings(self):
        data = snapshot('RNL-014', 90)
        self.assertTrue(all(r['minute'] <= 90 for r in data['history']))
        self.assertEqual(data['forecast']['trajectory'][0]['minute'], 90)


if __name__ == '__main__':
    unittest.main()
