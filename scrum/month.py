import datetime
import decimal
from collections import defaultdict

from . import settings
from .utils import format_minutes_as_hours
from .command_line import get_config
from .commands import scrum_command
from .scrumparser import ScrumParser

@scrum_command("month")
def month_subcommand_config(sub_parser):
    return month_subcommand

def month_subcommand(args):
    scrum_parser = ScrumParser('')
    days = scrum_parser.parse(open(settings.SCRUM_FILEPATH).readlines())
    config = get_config()
    month_report(days, config)

def month_report(days, config):
    month_config = config['month']
    round_to = int(month_config.get('round_to', 15))
    today = datetime.date.today()
    projects = defaultdict(decimal.Decimal)
    num_days = 0
    for day, projects_work in days:
        if (day.year, day.month) < (today.year, today.month):
            break
        elif (day.year, day.month) > (today.year, today.month):
            continue
        num_days += 1
        for pw in projects_work:
            if 'work_time' not in pw:
                continue
            projects[pw['project']] += decimal.Decimal(format_minutes_as_hours(pw['work_time'], round_to=round_to))
    for item in projects.items():
        print('%s - %s' % item)
    print('total - %s' % sum(tuple(v for v in projects.values())))
    print('num days - %s (%s hours)' % (num_days, num_days * 8))
