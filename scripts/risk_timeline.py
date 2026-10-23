"""Offline demand/sellable-supply scenarios. No APIs, defaults for business rules, or orders.

Input: mode ('factual'/'scenario'), initial_stock, forecast[{date,units}],
supplies[{id,remaining_qty,sellable_date,date_basis,state,pool_key?}],
safety_days?, review_date?, max_stock_at_review?. Receipts available at start of day.
'factual' means no assumed receipt dates, not that forecasts are realized facts.
"""
import argparse
import datetime as dt
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def number(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Expected a finite nonnegative number') from exc
    if not result.is_finite() or result < 0:
        raise ValueError('Expected a finite nonnegative number')
    return result


def display(value):
    # Display precision only; all internal arithmetic retains Decimal precision.
    return float(value.quantize(Decimal("0.000001")))


def evaluate(data):
    mode = data.get('mode', 'factual')
    if mode not in ('factual', 'scenario'):
        raise ValueError('Unknown mode')
    forecast = data['forecast']
    if not forecast:
        raise ValueError('Forecast is empty')
    dates = [dt.date.fromisoformat(x['date']) for x in forecast]
    if any(b - a != dt.timedelta(days=1) for a, b in zip(dates, dates[1:])):
        raise ValueError('Forecast dates must be ordered, unique and consecutive')
    stock = number(data['initial_stock'])
    safety = None if data.get('safety_days') is None else number(data['safety_days'])
    review = data.get('review_date')
    cap = data.get('max_stock_at_review')
    if cap is not None and (review is None or dt.date.fromisoformat(review) not in dates):
        raise ValueError('An inventory ceiling requires a review date in the horizon')
    if cap is not None:
        cap = number(cap)
    receipts, excluded, assumptions = {}, [], []
    ids, pools = set(), set()
    for supply in data.get('supplies', []):
        key = supply['id']
        if key in ids:
            raise ValueError('Duplicate supply id')
        ids.add(key)
        pool = supply.get('pool_key')
        if pool and pool in pools:
            raise ValueError('Same physical supply counted more than once')
        if pool:
            pools.add(pool)
        qty = number(supply['remaining_qty'])
        date = supply.get('sellable_date')
        basis = supply.get('date_basis', 'unknown')
        if supply.get('state') == 'unplaced' or not date or basis not in ('confirmed', 'assumed'):
            excluded.append({'id': key, 'reason': 'Not committed or no supported sellable date',
                             'remaining_qty': display(qty)})
            continue
        if basis == 'assumed':
            if mode != 'scenario':
                raise ValueError('Assumed sellable dates require scenario mode')
            assumptions.append(key)
        day = dt.date.fromisoformat(date)
        if day < dates[0]:
            raise ValueError('Past receipt may already be included in initial stock')
        receipts[day] = receipts.get(day, Decimal(0)) + qty
    timeline = []
    total_unmet = Decimal(0)
    surplus = None
    for item, day in zip(forecast, dates):
        demand = number(item['units'])
        opening, receipt = stock, receipts.get(day, Decimal(0))
        available = opening + receipt
        unmet = max(Decimal(0), demand - available)
        stock = max(Decimal(0), available - demand)
        total_unmet += unmet
        buffer = None if safety is None else demand * safety
        timeline.append({'date': day.isoformat(), 'opening': display(opening),
                         'sellable_receipts': display(receipt), 'demand': display(demand),
                         'closing': display(stock), 'unmet': display(unmet),
                         'safety_stock': None if buffer is None else display(buffer),
                         'below_safety': None if buffer is None else stock < buffer})
        if cap is not None and day.isoformat() == review:
            surplus = display(max(Decimal(0), stock - cap))
    shortage = [x['date'] for x in timeline if x['unmet'] > 0]
    breaches = [x['date'] for x in timeline if x['below_safety']]
    return {'mode': mode, 'conditional_receipts': assumptions,
            'excluded_supplies': excluded, 'timeline': timeline,
            'first_shortage': shortage[0] if shortage else None,
            'last_shortage': shortage[-1] if shortage else None,
            'shortage_days': len(shortage), 'unmet_units': display(total_unmet),
            'first_below_safety': breaches[0] if breaches else None,
            'ending_stock': display(stock), 'surplus_at_review': surplus,
            'business_writes': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(json.loads(args.input.read_text(encoding='utf-8')))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
