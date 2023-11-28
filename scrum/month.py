import datetime
import decimal

from collections import defaultdict
from functools import reduce

from .utils import format_minutes_as_hours, format_minutes
from .command_line import get_config, get_scrum_file_content
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
    days = scrum_parser.parse(get_scrum_file_content())
    config = get_config()
    month_report(month, year, days, config)

def month_report(month, year, days, config):
    round_to = int(config.get('month', 'round_to', fallback=15))
    num_hours_per_day = int(config.get('common', 'num_hours_per_day', fallback=8))

    projects = defaultdict(lambda : (0, decimal.Decimal()))
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
            (total, rounded) = projects[pw['project']]
            total += pw['work_time']
            rounded += decimal.Decimal(format_minutes_as_hours(pw['work_time'], round_to=round_to))
            projects[pw['project']] = (total, rounded)
        if worked_in_the_day:
            num_days += 1
    print(f'Rounded to {round_to} minutes.')
    format_project_data = lambda project, total, rounded: f'{project} - {rounded} (total: {format_minutes(total, pad_hours=True)})'
    for item in projects.items():
        project, (total, rounded) = item
        print(format_project_data(project, total, rounded))
    total, rounded = reduce(lambda a, b: tuple(sum(p) for p in zip(a, b)), projects.values(), (0, decimal.Decimal()))
    print(format_project_data('total', total, rounded))
    print(f'num days - {num_days} (expected {num_days * num_hours_per_day} hours, {num_hours_per_day} hours per day)')
