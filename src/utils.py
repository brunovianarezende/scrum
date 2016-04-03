import decimal
import re

def get_matching_projects_work(days_to_execute, days):
    def _match(day):
        day_str = day.strftime('%d/%m/%Y')
        for dte in days_to_execute:
            if re.match(dte, day_str):
                return True
        return False
    days_to_execute = set(days_to_execute)
    result = []
    for day, projects_work in days:
        if _match(day):
            result.append(projects_work)
    return list(reversed(result))

def format_activities(activities):
    """
    >>> format_activities([
    ...     ('4133', 'Make SomeProject site and agent work together', 'doing'),
    ... ])
    ('4133', 'Make SomeProject site and agent work together', 'doing')
    >>> format_activities([
    ...     ('4133', 'Make SomeProject site and agent work together', 'doing'),
    ...     ('NA', 'Other title', 'other description'),
    ... ])
    ('4133 / NA', 'Make SomeProject site and agent work together / Other title', 'doing / other description')
    """
    grouped = zip(*activities)
    return tuple(' / '.join(i) for i in grouped)

def format_minutes(minutes):
    """
    >>> format_minutes(117)
    '1:57'
    >>> format_minutes(3)
    '0:03'
    >>> format_minutes(-3)
    '-0:03'
    """
    sign = '' if minutes >= 0 else '-'
    minutes = abs(minutes)
    hours_str = str(minutes / 60)
    minutes_str = str(minutes % 60).rjust(2, '0')
    return sign + ':'.join((hours_str, minutes_str))

def format_minutes_as_hours(minutes):
    """
    >>> all(format_minutes_as_hours(t) == '2'for t in (117, 123))
    True
    >>> all(format_minutes_as_hours(t) == '4.25'for t in (255, 254, 262))
    True
    >>> all(format_minutes_as_hours(t) == '4.5'for t in (270, 263, 277))
    True
    >>> all(format_minutes_as_hours(t) == '4.75'for t in (285, 278, 292))
    True
    >>> [format_minutes_as_hours(-t) for t in (45, 38, 52)]
    ['-0.75', '-0.75', '-0.75']
    """
    base = minutes / 60
    mod = minutes % 60
    candidates = (0, 15, 30, 45, 60)
    distances = tuple(abs(mod - c) for c in candidates)
    index_min = distances.index(min(distances))
    match = candidates[index_min]
    value = base + decimal.Decimal(match) / 60
    return str(value)
