import datetime
import decimal
from itertools import groupby
from collections import defaultdict
import urllib
import requests

import settings

PROCESSORS = {}

__all__ = ['PROCESSORS']

def register_processor(name):
    def inner(func):
        PROCESSORS[name] = func
        return func
    return inner

def multiple_days_processor(func):
    func.multiple_days_processor = True
    return func

@register_processor('zone')
def update_timezone(projects_work):
    for pw in projects_work:
        project_id = pw['project'].lower()
        if project_id not in settings.MAPPINGS:
            print "'%s' is not mapped" % project_id 
        else:
            if 'work_time' in pw:
                entry = timezone_entry(pw)
                project_data = settings.MAPPINGS[project_id]
                url = create_add_timesheet_url(project_data, entry)
                requests.get(url, auth=(settings.TIMEZONE_USER, settings.TIMEZONE_PWD))
                print '%s - created entry for day %s' % (project_id, pw['day'])
            
def create_add_timesheet_url(project_data, entry):
    all_data = {}
    for d in (project_data, entry):
        for key, value in d.iteritems():
            all_data[key.lower()] = urllib.quote(str(value))
    parameters = sorted(['projectId', 'roleId', 'hours', 'date', 'description'])
    querystring = '&'.join('%s=%s' % (p, all_data[p.lower()]) for p in parameters)
    return settings.TIMEZONE_SERVER + "/Api/AddTimesheet?" + querystring

def timezone_entry(pw):
    result = {}
    result['date'] = '%s-%s-%s' % tuple(reversed(pw['day'].split('/')))
    result['hours'] = format_minutes_as_hours(pw['work_time'])
    result['description'] = " / ".join(('%s (%s) - %s' % (a['ticket'], a['title'], a['description']))
            for a in pw['activities'])
    return result

def first_empty_line(ws):
    current = ws.row_count
    while not (current == 0 or ws.cell(current, 1).value):
        current -= 1
    return current + 1

def rows_for_main_spreadsheet(projects_work):
    rows = []
    for pw in projects_work:
        ids, titles, descriptions = format_activities([
            (a['ticket'], a['title'], a['description'])
            for a in pw['activities']
        ])
        worked_time = format_minutes(pw['work_time'])
        day, project = pw['day'], pw['project']
        rows.append((day, project, ids, titles, worked_time, descriptions))
    return rows

@multiple_days_processor
@register_processor("month")
def month_report(days):
    today = datetime.datetime.now().date()
    current_month = today.month
#    current_month = 11
    projects = defaultdict(decimal.Decimal)
    num_days = 0
    for day, projects_work in days:
        if day.month < current_month:
            break
        elif day.month > current_month:
            continue
        num_days += 1
#         print day, projects_work
        for pw in projects_work:
            if 'work_time' not in pw:
                continue
            projects[pw['project']] += decimal.Decimal(format_minutes_as_hours(pw['work_time']))
    for item in projects.iteritems():
        print '%s - %s' % item
    print 'total - %s' % sum(tuple(v for v in projects.itervalues()))
    print 'num days - %s (%s hours)' % (num_days, num_days * 8)

def format_activities(activities):
    """
    >>> format_activities([
    ...     ('4133', 'Make Mariupol site and agent work together', 'doing'),
    ... ])
    ('4133', 'Make Mariupol site and agent work together', 'doing')
    >>> format_activities([
    ...     ('4133', 'Make Mariupol site and agent work together', 'doing'),
    ...     ('NA', 'Other title', 'other description'),
    ... ])
    ('4133 / NA', 'Make Mariupol site and agent work together / Other title', 'doing / other description')
    """
    grouped = zip(*activities)
    return tuple(' / '.join(i) for i in grouped)

def format_minutes(minutes):
    """
    >>> format_minutes(117)
    '1:57'
    >>> format_minutes(3)
    '0:03'
    """
    hours_str = str(minutes / 60)
    minutes_str = str(minutes % 60).rjust(2, '0')
    return ':'.join((hours_str, minutes_str))

def rows_for_soulmates_spreadsheet(projects_work):
    for pw in projects_work:
        if pw['project'].lower() == 'soulmates':
            result = []
            key = lambda a: a.get('time_group', 1)
            for time_group, activities in groupby(sorted(pw['activities'], key=key), key=key):
                activities = list(activities)
                work_time = pw.get('time_groups', {}).get(time_group, pw['work_time'])
                ids = ' / '.join('%s (%s)' % (a['ticket'], a['title'])
                    for a in activities)
                descriptions = ' / '.join(a['description'] for a in activities)
                worked_time = format_minutes_as_hours(work_time)
                day = switch_month_and_day_in_representation(pw['day'])
                project, area, activity = '', '', 'Development'
                result.append((day, project, area, ids, activity, worked_time, descriptions))
            return result
    return None

def rows_for_interflex_spreadsheet(projects_work):
    for pw in projects_work:
        if pw['project'].lower() == 'interflex':
            result = []
            key = lambda a: a.get('time_group', 1)
            for time_group, activities in groupby(sorted(pw['activities'], key=key), key=key):
                activities = list(activities)
                work_time = pw.get('time_groups', {}).get(time_group, pw['work_time'])
                ids = ' / '.join('%s (%s)' % (a['ticket'], a['title'])
                    for a in activities)
                descriptions = ' / '.join(a['description'] for a in activities)
                worked_time = format_minutes_as_hours(work_time)
                day = switch_month_and_day_in_representation(pw['day'])
                project, area, activity = '', '', 'Development'
                result.append((day, project, area, ids, activity, worked_time, descriptions))
            return result
    return None

def rows_for_fraunhofer_spreadsheet(projects_work):
    for pw in projects_work:
        if pw['project'].lower() == 'fraunhofer':
            result = []
            key = lambda a: a.get('time_group', 1)
            for time_group, activities in groupby(sorted(pw['activities'], key=key), key=key):
                activities = list(activities)
                work_time = pw.get('time_groups', {}).get(time_group, pw['work_time'])
                ids = ' / '.join('%s (%s)' % (a['ticket'], a['title'])
                    for a in activities)
                descriptions = ' / '.join(a['description'] for a in activities)
                worked_time = format_minutes_as_hours(work_time)
                day = switch_month_and_day_in_representation(pw['day'])
                project, area, activity = '', '', 'Development'
                result.append((day, project, area, ids, activity, worked_time, descriptions))
            return result
    return None

def switch_month_and_day_in_representation(day):
    """
    >>> switch_month_and_day_in_representation('12/10/2014')
    '10/12/2014'
    """
    return datetime.datetime.strptime(day, '%d/%m/%Y').strftime('%m/%d/%Y')

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
    """
    base = minutes / 60
    mod = minutes % 60
    candidates = (0, 15, 30, 45, 60)
    distances = tuple(abs(mod - c) for c in candidates)
    index_min = distances.index(min(distances))
    match = candidates[index_min]
    value = base + decimal.Decimal(match) / 60
    return str(value)

def update_cells_from_row(ws, row, values):
    cells = []
    for i, value in enumerate(values):
        cell = ws.cell(row, i + 1)
        cell.value = value
        cells.append(cell)
    ws.update_cells(cells)
