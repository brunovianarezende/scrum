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


def update_cells_from_row(ws, row, values):
    for i, value in enumerate(values):
        ws.update_cell(row, i+1, value)
