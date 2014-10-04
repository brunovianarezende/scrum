import datetime
import decimal
from itertools import groupby

import gspread

import settings

PROCESSORS = {}

__all__ = ['PROCESSORS']

def register_processor(name):
    def inner(func):
        PROCESSORS[name] = func
        return func
    return inner

@register_processor('main_spreadsheet')
def update_main_spreadsheet(days):
    _, projects_work = days.next()
    full_data = all('work_time_partial' not in pw for pw in projects_work)
    if not full_data:
        return
    gc = gspread.login(settings.GOOGLE_DRIVE_USER, settings.GOOGLE_DRIVE_PWD)
    doc = gc.open_by_key(settings.MAIN_SPREADSHEET_KEY)
    ws = doc.worksheet('From Oct 2013')
    num_rows = ws.row_count
    row_to_update = first_empty_line(ws)
    if row_to_update > num_rows:
        ws.add_rows(10)
    new_rows = rows_for_main_spreadsheet(projects_work)
    if row_to_update + len(new_rows) > num_rows:
        ws.add_rows(len(new_rows))
    for i, new_row in enumerate(new_rows):
        update_cells_from_row(ws, row_to_update + i, new_row)

@register_processor('soulmates')
def update_soulmates_spreadsheet(days):
    _, projects_work = days.next()
    full_data = all('work_time_partial' not in pw for pw in projects_work)
    if not full_data:
        return
    gc = gspread.login(settings.GOOGLE_DRIVE_USER, settings.GOOGLE_DRIVE_PWD)
    doc = gc.open_by_key(settings.SOULMATES_SPREADSHEET_KEY)
    ws = doc.worksheet('Bruno')
    num_rows = ws.row_count
    row_to_update = first_empty_line(ws)
    if row_to_update > num_rows:
        ws.add_rows(10)
    new_rows = rows_for_soulmates_spreadsheet(projects_work)
    if row_to_update + len(new_rows) > num_rows:
        ws.add_rows(len(new_rows))
    for i, new_row in enumerate(new_rows):
        update_cells_from_row(ws, row_to_update + i, new_row)

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
