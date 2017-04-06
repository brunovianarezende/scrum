from urllib.parse import quote

import requests

from . import settings
from .utils import format_minutes_as_hours, get_matching_projects_work
from .commands import scrum_command
from .scrumparser import ScrumParser

@scrum_command("zone")
def timezone_subcommand_config(sub_parser):
    sub_parser.add_argument('-d', '--day', help="days to run the processors for. "
        "If no day is given, use the last day with data in the file. ",
        action="append")
    return timezone_subcommand

def timezone_subcommand(args):
    days_to_execute = args.day

    for projects_work in _projects_works(days_to_execute):
            update_timezone(projects_work)

def _projects_works(days_to_execute):
    scrum_parser = ScrumParser('')
    days = scrum_parser.parse(open(settings.SCRUM_FILEPATH).readlines())

    if days_to_execute:
        return get_matching_projects_work(days_to_execute, days)
    else:
        _, projects_work = next(days)
        return [projects_work]

def update_timezone(projects_work):
    for pw in projects_work:
        project_id = pw['project'].lower()
        if project_id not in settings.MAPPINGS:
            print("'%s' is not mapped" % project_id )
        else:
            if 'work_time' in pw:
                entry = timezone_entry(pw)
                project_data = settings.MAPPINGS[project_id]
                url = create_add_timesheet_url(project_data, entry)
                requests.get(url, auth=(settings.TIMEZONE_USER, settings.TIMEZONE_PWD))
                print('%s - created entry for day %s' % (project_id, pw['day']))

def timezone_entry(pw):
    result = {}
    result['date'] = '%s-%s-%s' % tuple(reversed(pw['day'].split('/')))
    result['hours'] = format_minutes_as_hours(pw['work_time'])
    result['description'] = " / ".join(('%s (%s) - %s' % (a['ticket'], a['title'], a['description']))
            for a in pw['activities'])
    return result

def create_add_timesheet_url(project_data, entry):
    all_data = {}
    for d in (project_data, entry):
        for key, value in d.items():
            all_data[key.lower()] = quote(str(value))
    parameters = sorted(['projectId', 'roleId', 'hours', 'date', 'description'])
    querystring = '&'.join('%s=%s' % (p, all_data[p.lower()]) for p in parameters)
    return settings.TIMEZONE_SERVER + "/Api/AddTimesheet?" + querystring

