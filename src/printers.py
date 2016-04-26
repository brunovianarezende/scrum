import datetime

from utils import format_minutes, get_matching_projects_work
from commands import scrum_command
from scrumparser import ScrumParser

def _printers():
    return [
        ('current', current_worked_time_printer),
        ('per_activity', per_activity_printer),
        ('scrum', scrum_printer),
    ]

@scrum_command("printer")
def printer_subcommand_config(sub_parser):
    sub_parser.add_argument('-d', '--day', help="days to run the processors for. "
        "If no day is given, use the last day with data in the file. "
        "It can't be use together with the scrum printer",
        action="append")
    sub_parser.add_argument('-p', '--printer', help="Printers to be executed. If "
        "not given, all printers will execute. Available: %s" % ', '.join("'%s'" % n for n, _ in _printers()),
        action="append")
    return printer_subcommand

def printer_subcommand(args):
    days_to_execute = args.day
    if not args.printer:
        printers = [p for _, p in _printers()]
    else:
        printers_dict = dict(_printers())
        printers = []
        for printer_id in args.printer:
            printer = printers_dict.get(printer_id)
            if not printer:
                print "'%s' doesn't exist" % printer_id
            else:
                printers.append(printer)

    scrum_parser = ScrumParser('')

    if days_to_execute:
        valid_printers = [p for p in printers if p != scrum_printer]
        days = scrum_parser.parse(open('/home/brunore/Desktop/cs_data.txt').readlines())
        projects_work_for_days = get_matching_projects_work(days_to_execute, days)
        for projects_work in projects_work_for_days:
            for printer in valid_printers:
                printer(projects_work)
    else:
        for printer in printers:
            days = scrum_parser.parse(open('/home/brunore/Desktop/cs_data.txt').readlines())
            if scrum_printer == printer:
                printer(days)
            else:
                _, projects_work = days.next()
                printer(projects_work)

def current_worked_time_printer(projects_work):
    full_data = all('work_time_partial' not in pw for pw in projects_work)
    if not full_data:
        print_current_worked_time(projects_work)
        print ''

def per_activity_printer(projects_work):
    print_time_per_activity(projects_work)
    print ''

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
    def _worked_time_til_now(worked, pending):
        now = datetime.datetime.now()
        normalized = now.hour * 60 + now.minute
        total = worked
        hour, minute = (int(p) for p in pending.split(':'))
        total += normalized - (hour*60 + minute)
        return total
    total_global = 0
    print 'time spent per activity group:'
    for pw in projects_work:
        if 'time_groups' in pw:
            time_groups = pw['time_groups']
        else:
            total = 0
            if 'work_time' not in pw:
                worked, pending = pw['work_time_partial']
                total += _worked_time_til_now(worked, pending)
            time_groups = {1: pw.get('work_time', total)}
        data = {}
        for activity in pw['activities']:
            time_group = activity.get('time_group', 1)
            time_data = data.setdefault(time_group, {})
            time_data['time'] = time_groups[time_group]
            time_data.setdefault('activities', []).append(activity)
        for _, time_data in sorted(data.iteritems()):
            try:
                total_global += time_data['time']
                print format_minutes(time_data['time'])
            except:
                worked, pending = time_data['time']
                activity_time = _worked_time_til_now(worked, pending)
                total_global += activity_time
                print format_minutes(activity_time)
            for a in time_data['activities']:
                ticket = a['ticket']
                if ticket.isdigit():
                    ticket = '#' + ticket
                print '%s (%s) - %s' % (ticket, a['title'], a['description'])
    print 'total time at the day: %s' % format_minutes(total_global)
    print 'missing time: %s' % format_minutes(8*60 - total_global)

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
