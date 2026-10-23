import copy
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('risk_timeline', Path(__file__).parents[1] / 'scripts/risk_timeline.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def scenario(daily=10, stock=140, days=20):
    start = dt.date(2026, 10, 23)
    return {'initial_stock': stock, 'forecast': [{'date': (start + dt.timedelta(days=i)).isoformat(),
            'units': daily} for i in range(days)], 'supplies': []}


def receipt(date='2026-11-03', qty=140, **extra):
    return dict(id='batch-A', remaining_qty=qty, sellable_date=date, date_basis='confirmed', **extra)


class BusinessBehavior(unittest.TestCase):
    def test_traffic_increase_can_break_a_timely_route(self):
        base = scenario(); base['supplies'] = [receipt()]
        fast = scenario(daily=14); fast['supplies'] = [receipt()]
        self.assertEqual(m.evaluate(base)['unmet_units'], 0)
        self.assertEqual(m.evaluate(fast)['first_shortage'], '2026-11-02')
        self.assertEqual(m.evaluate(fast)['unmet_units'], 14)

    def test_earlier_supply_can_eliminate_shortage(self):
        x = scenario(daily=14); x['supplies'] = [receipt('2026-11-01')]
        self.assertEqual(m.evaluate(x)['unmet_units'], 0)

    def test_late_receipt_does_not_erase_lost_sales(self):
        x = scenario(daily=10, stock=10, days=3)
        x['supplies'] = [receipt('2026-10-25', 100)]
        r = m.evaluate(x)
        self.assertEqual(r['unmet_units'], 10)
        self.assertEqual(r['ending_stock'], 90)

    def test_delivery_window_and_draft_do_not_count_as_sellable(self):
        x = scenario(stock=0, days=2)
        x['supplies'] = [dict(id='window', remaining_qty=50, sellable_date='2026-10-23',
                             date_basis='delivery_only'),
                         receipt('2026-10-23', 50, state='unplaced')]
        self.assertEqual(m.evaluate(x)['unmet_units'], 20)
        self.assertEqual(len(m.evaluate(x)['excluded_supplies']), 2)

    def test_assumptions_are_explicit_and_not_facts(self):
        x = scenario(); x['supplies'] = [receipt()]; x['supplies'][0]['date_basis'] = 'assumed'
        with self.assertRaises(ValueError): m.evaluate(x)
        x['mode'] = 'scenario'
        self.assertEqual(m.evaluate(x)['conditional_receipts'], ['batch-A'])

    def test_procurement_and_shipment_same_pool_cannot_double_count(self):
        x = scenario(); x['supplies'] = [receipt(pool_key='one-physical-batch')]
        y = copy.deepcopy(x['supplies'][0]); y['id'] = 'purchase-reference'; x['supplies'].append(y)
        with self.assertRaises(ValueError): m.evaluate(x)

    def test_slow_sales_raise_surplus_against_explicit_target(self):
        base = scenario(stock=300, daily=10, days=10)
        base.update(review_date='2026-11-01', max_stock_at_review=200)
        slower = copy.deepcopy(base)
        for day in slower['forecast']: day['units'] = 5
        self.assertEqual(m.evaluate(base)['surplus_at_review'], 0)
        self.assertEqual(m.evaluate(slower)['surplus_at_review'], 50)

    def test_no_surplus_claim_without_approved_ceiling(self):
        x = scenario(stock=300, daily=0, days=3)
        self.assertIsNone(m.evaluate(x)['surplus_at_review'])
        self.assertEqual(m.evaluate(x)['ending_stock'], 300)

    def test_safety_risk_precedes_stockout(self):
        x = scenario(stock=40, days=4); x['safety_days'] = 2
        r = m.evaluate(x)
        self.assertEqual(r['first_below_safety'], '2026-10-25')
        self.assertIsNone(r['first_shortage'])

    def test_repeating_daily_average_displays_business_quantity(self):
        x = scenario(stock=100, daily=10/3, days=60)
        self.assertEqual(m.evaluate(x)["unmet_units"], 100)

    def test_bad_dates_and_negative_stock_are_rejected(self):
        x = scenario(); x['forecast'][1]['date'] = x['forecast'][0]['date']
        with self.assertRaises(ValueError): m.evaluate(x)
        x = scenario(stock=-1)
        with self.assertRaises(ValueError): m.evaluate(x)


if __name__ == '__main__': unittest.main()
