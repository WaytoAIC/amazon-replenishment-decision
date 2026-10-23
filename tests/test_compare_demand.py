import copy
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('compare_demand', Path(__file__).parents[1] / 'scripts/compare_demand.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sample():
    start = dt.date(2026, 1, 1)
    return {key: [{'date': (start + dt.timedelta(days=offset + i)).isoformat(),
                   'units': 2, 'sessions': 10} for i in range(7)]
            for key, offset in [('prior', 0), ('recent', 7)]}


class PairedEvidence(unittest.TestCase):
    def test_sales_with_zero_sessions_does_not_distort_comparable_conversion(self):
        x = sample(); x['recent'][6].update(units=20, sessions=0)
        r = m.compare(x)
        self.assertEqual(r['full_week_units'], [14, 32])
        self.assertEqual(r['valid_pairs'], 6)
        self.assertEqual(r['matched_recent']['units_per_session_pct'], 20)
        self.assertEqual(r['matched_prior']['units'], 12)
        self.assertEqual(r['coverage'], 'partial')

    def test_zero_sales_with_real_visitors_remains_in_sample(self):
        x = sample(); x['recent'][0]['units'] = 0
        r = m.compare(x)
        self.assertEqual(r['valid_pairs'], 7)
        self.assertAlmostEqual(r['matched_recent']['units_per_session_pct'], 100*12/70, places=5)

    def test_no_visits_cannot_generate_conversion_claim(self):
        x = sample()
        for d in x['recent']: d['sessions'] = None
        r = m.compare(x)
        self.assertEqual(r['full_week_units'], [14, 14])
        self.assertEqual(r['coverage'], 'unavailable')
        self.assertIsNone(r['matched_recent']['units_per_session_pct'])
        self.assertIsNone(r['matched_sessions_change_pct'])

    def test_missing_sales_day_or_shifted_week_is_rejected(self):
        x = sample(); x['prior'].pop()
        with self.assertRaises(ValueError): m.compare(x)
        x = sample()
        for d in x['recent']: d['date'] = (dt.date.fromisoformat(d['date'])+dt.timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError): m.compare(x)

    def test_bad_numeric_data_is_not_silently_filled(self):
        for value in (None, -1, 'NaN', 'Infinity'):
            x = copy.deepcopy(sample()); x['recent'][0]['units'] = value
            with self.assertRaises(ValueError): m.compare(x)


if __name__ == '__main__': unittest.main()
