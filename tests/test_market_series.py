import importlib.util
from pathlib import Path
import unittest

s = importlib.util.spec_from_file_location('market_series', Path(__file__).parents[1]/'scripts/market_series.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)


def sample():
    return {'requested_asin':'SYNTHETIC-A','marketplace':'US','start_ms':86400000,'end_ms':259200000,
            'data':{'asin':'SYNTHETIC-A','dataAsin':'SYNTHETIC-A','marketplace':'US'}}


class MarketObservations(unittest.TestCase):
    def test_reverse_series_is_sorted_and_latest_in_day_selected(self):
        x=sample();x['data']['price']=[{'timePoint':172800001,'value':20},{'timePoint':86400001,'value':10},{'timePoint':86400002,'value':11}]
        r=m.summarize(x)['series']['price']
        self.assertEqual(r['observed_days'],2)
        self.assertEqual(r['first']['value'],11)
        self.assertEqual(r['last']['value'],20)

    def test_sentinels_and_out_of_window_do_not_become_zero(self):
        x=sample();x['data']['bsr']=[{'timePoint':86400001,'value':-1},{'timePoint':172800001,'value':100},{'timePoint':259200001,'value':99}]
        r=m.summarize(x)['series']['bsr']
        self.assertEqual(r['observed_days'],1);self.assertEqual(r['invalid_points'],1)
        self.assertEqual(r['out_of_window_points'],1);self.assertEqual(r['first']['value'],100)
        self.assertIsNone(m.summarize(x)['series']['buyBox']['last'])

    def test_parent_data_remains_parent_and_identifiers_not_exported(self):
        x=sample();x['data'].update(dataAsin='SYNTHETIC-P',parentAsin='SYNTHETIC-P')
        r=m.summarize(x);self.assertEqual(r['data_level'],'parent_fallback')
        self.assertNotIn('SYNTHETIC',str(r))

    def test_wrong_response_scope_is_rejected(self):
        x=sample();x['data']['marketplace']='JP'
        with self.assertRaises(ValueError):m.summarize(x)
        x=sample();x['data']['asin']='SYNTHETIC-B'
        with self.assertRaises(ValueError):m.summarize(x)


if __name__ == '__main__':unittest.main()
