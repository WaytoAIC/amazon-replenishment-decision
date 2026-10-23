"""Offline paired-week evidence, without causal claims or network access.

Input: prior/recent, each seven ordered daily {date, units, sessions} rows.
units is required; sessions may be null. Pair dates exactly seven days apart.
Output keeps full-week units separate from comparable traffic observations.
"""
import argparse
import datetime as dt
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def number(value):
    try:
        value = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Expected finite nonnegative number') from exc
    if not value.is_finite() or value < 0:
        raise ValueError('Expected finite nonnegative number')
    return value


def shown(value):
    return None if value is None else float(round(value, 6))


def compare(data):
    weeks = []
    for key in ('prior', 'recent'):
        records = data[key]
        if len(records) != 7:
            raise ValueError('Each window needs all seven daily sales records')
        week = [(dt.date.fromisoformat(r['date']), number(r['units']),
                 None if r.get('sessions') is None else number(r['sessions'])) for r in records]
        if any(b[0] - a[0] != dt.timedelta(days=1) for a, b in zip(week, week[1:])):
            raise ValueError('Daily records must be ordered, unique and consecutive')
        weeks.append(week)
    if weeks[1][0][0] - weeks[0][0][0] != dt.timedelta(days=7):
        raise ValueError('Only adjacent weeks with the same weekdays can be paired')
    paired, excluded = [], []
    for p, r in zip(*weeks):
        if p[2] is not None and r[2] is not None and p[2] > 0 and r[2] > 0:
            paired.append((p, r))
        else:
            excluded.append({'prior_date': p[0].isoformat(), 'recent_date': r[0].isoformat(),
                             'reason': 'Missing or zero sessions; no causal interpretation'})
    full = [sum(r[1] for r in w) for w in weeks]
    metrics = []
    for i in (0, 1):
        units = sum((p[i][1] for p in paired), Decimal(0))
        sessions = sum((p[i][2] for p in paired), Decimal(0))
        metrics.append({'units': shown(units), 'sessions': shown(sessions),
                        'units_per_session_pct': shown(100 * units / sessions) if sessions else None})
    def change(a, b):
        return shown(100 * (b - a) / a) if a else None
    return {'full_week_units': [shown(x) for x in full],
            'full_week_units_change_pct': change(*full),
            'valid_pairs': len(paired), 'excluded_pairs': excluded,
            'matched_prior': metrics[0], 'matched_recent': metrics[1],
            'matched_sessions_change_pct': change(
                Decimal(str(metrics[0]['sessions'])), Decimal(str(metrics[1]['sessions']))),
            'coverage': 'complete' if len(paired) == 7 else 'partial' if paired else 'unavailable',
            'interpretation_limit': 'Arithmetic evidence only; units/session is not order conversion. '
                                    'Partial observations cannot establish full-week causes.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(compare(json.loads(args.input.read_text())),
                                      ensure_ascii=False, indent=2) + '\n')
