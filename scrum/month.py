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
    sub_parser.add_argument('-m', '--month', default=None, type=int)
    sub_parser.add_argument('-y', '--year', default=None, type=int)
    return month_subcommand

def month_subcommand(args):
    today = datetime.date.today()
    month = today.month if args.month is None else args.month
    year = today.year if args.year is None else args.year
    scrum_parser = ScrumParser('')
    days = scrum_parser.parse(open(settings.SCRUM_FILEPATH).readlines())
    config = get_config()
    month_report(month, year, days, config)

def month_report(month, year, days, config):
    month_config = config['month']
    round_to = int(month_config.get('round_to', 15))
    projects = defaultdict(decimal.Decimal)
    num_days = 0
    for day, projects_work in days:
        if (day.year, day.month) < (year, month):
            break
        elif (day.year, day.month) > (year, month):
            continue
        worked_in_the_day = False
        for pw in projects_work:
            if 'work_time' not in pw or pw['work_time'] == 0:
                continue
            worked_in_the_day = True
            projects[pw['project']] += decimal.Decimal(format_minutes_as_hours(pw['work_time'], round_to=round_to))
        if worked_in_the_day:
            num_days += 1
    for item in projects.items():
        print('%s - %s' % item)
    print('total - %s' % sum(tuple(v for v in projects.values())))
    print('num days - %s (expected %s hours, 4 hours per day)' % (num_days, num_days * 4))
