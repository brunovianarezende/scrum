import argparse
import datetime
import re

from scrumparser import ScrumParser
from processors import PROCESSORS, multiple_days_processor

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--processor', help="run the processor. By"
        " default only print processors run.", action="append")
    arg_parser.add_argument('-d', '--day', help="days to run the processors for. "
        "If no day is given, use the last day with data in the file. "
        "Only single day processors will be executed if this option is used.",
        action="append")
    arg_parser.add_argument('-l', '--listprocessors', help="list all available"
        " processors.", action='store_true')
    
    args = arg_parser.parse_args()

    if args.listprocessors:
        print 'optional processors:'
        print '\n'.join('- %s' % k for k in PROCESSORS.keys())
        return
    days_to_execute = args.day
    
    if args.processor:
        processors = [PROCESSORS[p] for p in args.processor
                              if p in PROCESSORS]
    else:
        processors = [spreadsheet_printer, current_worked_time_printer,
                  per_activity_printer, scrum_printer]

    scrum_parser = ScrumParser('')
    if days_to_execute:
        processors = [p for p in processors if not getattr(p, 'multiple_days_processor', False)]
        days = scrum_parser.parse(open('/home/brunore/Desktop/cs_data.txt').readlines())
        projects_work_for_days = get_matching_projects_work(days_to_execute, days)
        for projects_work in projects_work_for_days:
            for processor in processors:
                processor(projects_work)
    else:
        for processor in processors:
            days = scrum_parser.parse(open('/home/brunore/Desktop/cs_data.txt').readlines())
            if getattr(processor, 'multiple_days_processor', False):
                processor(days)
            else:
                _, projects_work = days.next()
                processor(projects_work)

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
#         if day.strftime('%d/%m/%Y') in days_to_execute:
        if _match(day):
            result.append(projects_work)
    return list(reversed(result))

def spreadsheet_printer(projects_work):
    full_data = all('work_time_partial' not in pw for pw in projects_work)
    if full_data:
        print_for_spread_sheet(projects_work)
        print ''

def current_worked_time_printer(projects_work):
    full_data = all('work_time_partial' not in pw for pw in projects_work)
    if not full_data:
        print_current_worked_time(projects_work)
        print ''

def per_activity_printer(projects_work):
    print_time_per_activity(projects_work)
    print ''

@multiple_days_processor
def scrum_printer(days):
    day, projects_work = days.next()
    today = datetime.datetime.now().date()
    if today == day:
        today_scrum_data = (day, projects_work)
        day, projects_work = days.next()
    else:
        today_scrum_data = None
    scrum_data = [(day, projects_work)]
    if day.weekday() in (5, 6):
        for day, projects_work in days:
            scrum_data.append((day, projects_work))
            if day.weekday() not in (5, 6):
                break
    print_for_scrum(today, scrum_data, today_scrum_data)

DAYS = dict(enumerate(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']))

def print_current_worked_time(projects_work):
    now = datetime.datetime.now()
    normalized = now.hour * 60 + now.minute
    total = 0
    for pw in projects_work:
        if 'work_time_partial' not in pw:
            total += pw['work_time']
        else:
            worked, pending = pw['work_time_partial']
            total += worked
            hour, minute = (int(p) for p in pending.split(':'))
            total += normalized - (hour*60 + minute)
    print 'worked time: ', format_minutes(total)

def print_time_per_activity(projects_work):
    total_global = 0
    print 'time spent per activity group:'
    for pw in projects_work:
        if 'time_groups' in pw:
            time_groups = pw['time_groups']
        else:
            total = 0
            if 'work_time' not in pw:
                now = datetime.datetime.now()
                normalized = now.hour * 60 + now.minute
                worked, pending = pw['work_time_partial']
                total = worked
                hour, minute = (int(p) for p in pending.split(':'))
                total += normalized - (hour*60 + minute)
            time_groups = {1: pw.get('work_time', total)}
        data = {}
        for activity in pw['activities']:
            time_group = activity.get('time_group', 1)
            time_data = data.setdefault(time_group, {})
            time_data['time'] = time_groups[time_group]
            time_data.setdefault('activities', []).append(activity)
        for _, time_data in sorted(data.iteritems()):
            total_global += time_data['time']
            print format_minutes(time_data['time'])
            for a in time_data['activities']:
                ticket = a['ticket']
                if ticket.isdigit():
                    ticket = '#' + ticket
                print '%s (%s) - %s' % (ticket, a['title'], a['description'])
    print 'total time at the day: %s' % format_minutes(total_global)
    print 'missing time: %s' % format_minutes(8*60 - total_global)

def print_for_spread_sheet(projects_work):
    for pw in projects_work:
        ids, titles, descriptions = format_activities([
            (a['ticket'], a['title'], a['description'])
            for a in pw['activities']
        ])
        worked_time = format_minutes(pw['work_time'])
        day, project = pw['day'], pw['project']
        print '\t'.join((day, project, ids, titles, worked_time, descriptions))

def print_for_scrum(today, scrum_data, today_scrum_data):
    print 'data for scrum:'
    for scrum_day, projects_work in scrum_data:
        if scrum_day.weekday() in (5, 6):
            scrum_day = DAYS[scrum_day.weekday()]
        elif (today - scrum_day).days == 1:
            scrum_day = 'yesterday'
        else:
            scrum_day = DAYS[scrum_day.weekday()]
        print '[%s]' % scrum_day
        for project_work in projects_work:
            for a in project_work['activities']:
                ticket = a['ticket']
                if ticket.isdigit():
                    ticket = '#' + ticket
                print '%s (%s) - %s' % (ticket, a['title'], a['description'])
    print ''
    print '[today]'
    if today_scrum_data:
        _, projects_work = today_scrum_data
        for project_work in projects_work:
            for a in project_work['activities']:
                ticket = a['ticket']
                if ticket.isdigit():
                    ticket = '#' + ticket
                print '%s (%s) - %s' % (ticket, a['title'], a['description'])
    
    print ''
    print '[obstacles]'
    print '#None'

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
    a_minutes = abs(minutes)
    hours_str = str(a_minutes / 60)
    minutes_str = str(a_minutes % 60).rjust(2, '0')
    result = ':'.join((hours_str, minutes_str))
    if minutes < 0:
        return '-' + result
    else:
        return result

if __name__ == '__main__':
    main()