"""Summarize private SellerSprite series into anonymous observations; no forecast.

Input: requested_asin, marketplace, start_ms, end_ms (exclusive), data (keepa_info.data).
UTC is used explicitly. Negative sentinel values are excluded, never filled with zero.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path


def summarize(x):
    data = x['data']
    start, end = int(x['start_ms']), int(x['end_ms'])
    if end <= start:
        raise ValueError('Invalid observation window')
    if data.get('marketplace') != x['marketplace'] or data.get('asin') != x['requested_asin']:
        raise ValueError('Response scope does not match request')
    source = data.get('dataAsin')
    level = ('requested_asin' if source == x['requested_asin'] else
             'parent_fallback' if source and source == data.get('parentAsin') else
             'other_asin' if source else 'unknown')
    series = {}
    for field in ('price', 'buyBox', 'bsr', 'rating', 'reviews', 'sellers'):
        daily = {}; rejected = outside = 0
        for row in data.get(field) or []:
            stamp, value = row.get('timePoint'), row.get('value')
            if isinstance(stamp, bool) or not isinstance(stamp, (int, float)) or not math.isfinite(stamp):
                rejected += 1; continue
            if not start <= stamp < end:
                outside += 1; continue
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0 or (field == 'bsr' and value == 0)):
                rejected += 1; continue
            day = dt.datetime.fromtimestamp(stamp / 1000, dt.timezone.utc).date().isoformat()
            if day not in daily or stamp > daily[day]['timePoint']:
                daily[day] = {'timePoint': stamp, 'date': day, 'value': value}
            elif stamp == daily[day]['timePoint'] and value != daily[day]['value']:
                raise ValueError('Conflicting observations at the same timestamp')
        ordered = sorted(daily.values(), key=lambda r:r['timePoint'])
        series[field] = {'observed_days': len(ordered), 'invalid_points': rejected,
                         'out_of_window_points': outside,
                         'first': ordered[0] if ordered else None, 'last': ordered[-1] if ordered else None,
                         'observations': ordered}
    return {'timezone': 'UTC', 'data_level': level, 'series': series,
            'decision_limit': 'External observations only; no actual unit sales or causal proof. '
                              'Do not replace internal demand or infer data for missing dates.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.write_text(json.dumps(summarize(json.loads(a.input.read_text())), ensure_ascii=False, indent=2)+'\n')
