import datetime

from scrumparser import ScrumParser

def main():
    parser = ScrumParser('')
    days = parser.parse(open('/home/brunore/Desktop/cs_data2.txt').readlines())
    day, projects_work = days.next()
    full_data = True
    for pw in projects_work:
        if 'work_time_partial' in pw:
            full_data = False
            break
    if full_data:
        print_for_spread_sheet(projects_work)
    print ''
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

if __name__ == '__main__':
    main()