import datetime
import decimal
from collections import defaultdict

from utils import format_minutes_as_hours
from commands import scrum_command
from scrumparser import ScrumParser

@scrum_command("month")
def month_subcommand_config(sub_parser):
    return month_subcommand

def month_subcommand(args):
    scrum_parser = ScrumParser('')
    days = scrum_parser.parse(open('/home/brunore/Desktop/cs_data.txt').readlines())
    month_report(days)

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
