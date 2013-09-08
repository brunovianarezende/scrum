import re, datetime

def main():
    parser = ScrumParser()
    days = parser.parse(open('/home/brunore/Desktop/cs_data.txt').readlines())
    day, projects_work = days.next()
    print_for_spread_sheet(projects_work)
    print ''
    today = datetime.datetime.now()
    scrum_data = [(day, projects_work)]
    if day.weekday() in (5, 6):
        for day, projects_work in days:
            scrum_data.append((day, projects_work))
            if day.weekday() not in (5, 6):
                break
    print_for_scrum(today, scrum_data)

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

def print_for_scrum(today, scrum_data):
    print '[today]'
    print '\n'
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
    

from pprint import pprint
def compare(a, b):
    if a != b:
        pprint(a)
        pprint(b)

class ScrumParser(object):
    """
    >>> content = '''
    ... 26/07/2013
    ... 7:17 9:14
    ... 10:00 12:06
    ... #4133 (Make Mariupol site and agent work together) - doing
    ... '''
    >>> parser = ScrumParser(default_project='Project')
    >>> compare(parser.parse_item(content.split('\\n')), [{'activities': [
    ...     {'description': 'doing',
    ...      'ticket': '4133',
    ...     'title': 'Make Mariupol site and agent work together'}],
    ...  'day': '26/07/2013', 'project': 'Project', 'work_time': 243}])
    >>> content = '''
    ... 26/07/2013
    ... 7:17 9:14
    ... 10:00 12:06
    ... #4133 (Make Mariupol site and agent work together) - doing
    ... BrandX
    ... 12:15 12:45
    ... #4134 (some work in BrandX) - doing task
    ... NA (other work in BrandX) - doing
    ... '''
    >>> compare(parser.parse_item(content.split('\\n')), [
    ...     {'project': 'Project', 'day': '26/07/2013', 'work_time': 243,
    ...      'activities': [
    ...          {'description': 'doing', 'ticket': '4133',
    ...          'title': 'Make Mariupol site and agent work together'},
    ...       ]
    ...    },
    ...     {'project': 'BrandX', 'day': '26/07/2013', 'work_time': 30,
    ...      'activities': [
    ...          {'description': 'doing task', 'ticket': '4134',
    ...           'title': 'some work in BrandX'},
    ...          {'description': 'doing', 'ticket': 'NA',
    ...           'title': 'other work in BrandX'},
    ...      ]
    ...    }
    ... ])
    >>> content = '''
    ... 26/07/2013
    ... 7:17 9:14
    ... 10:00 12:06
    ... #4133 (Make Mariupol site and agent work together) - doing
    ... 
    ... 25/07/2013
    ... BrandX
    ... 12:15 12:45
    ... #4134 (some work in BrandX) - doing task
    ... NA (other work in BrandX) - doing
    ...
    ... Default Project: Bla
    ...
    ... 24/07/2013
    ... 12:15 12:45
    ... #4134 (some work in BrandX) - doing task
    ... NA (other work in BrandX) - doing'''
    >>> items = parser.parse(content.split('\\n'))
    >>> item = items.next()
    >>> compare(item, (datetime.datetime(2013, 7, 26, 0, 0), [{'activities': [
    ...     {'description': 'doing',
    ...      'ticket': '4133',
    ...     'title': 'Make Mariupol site and agent work together'}],
    ...  'day': '26/07/2013', 'project': 'Project', 'work_time': 243}]))
    >>> item = items.next()
    >>> item = items.next()
    >>> item[0]
    datetime.datetime(2013, 7, 24, 0, 0)
    >>> item[1][0]['project']
    'Bla'
    >>> items.next() # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    StopIteration
    """

    def __init__(self, default_project=''):
        self.default_project = default_project

    def parse_item(self, lines):
        result = []
        current_line_type = ''
        # day is the same for all lines being processed and appears only once
        day = ''
        for line in lines:
            line = line.strip()
            if not line:
                continue
            line_type, value = self._process_line(line)
            if not current_line_type or\
                (current_line_type == 'activities'
                 and line_type != current_line_type):
                item = {'activities': [], 'work_time': 0,
                    'project': self.default_project, 'day': day}
                result.append(item)
            current_line_type = line_type
            if line_type == 'day':
                item['day'] = value
                day = value
            elif line_type == 'time':
                item['work_time'] += value
            elif line_type == 'activities':
                item['activities'].append(value)
            elif line_type == 'project':
                item['project'] = value

        return result

    def _process_line(self, line):
        if is_day(line):
            return 'day', line
        elif is_time(line):
            return 'time', process_time(line)
        elif is_activity(line):
            ticket, title, description = process_activity(line)
            activity = {
                'ticket': ticket,
                'title': title,
                'description': description
            }
            return 'activities', activity
        else:
            return 'project', line

    def parse(self, lines):
        def _item(lines):
            parsed = self.parse_item(lines_current_item)
            day = datetime.datetime.strptime(parsed[0]['day'], '%d/%m/%Y')
            return day, parsed
        lines_current_item = []
        for line in lines:
            line = line.strip()
            if not line and not lines_current_item:
                continue
            elif not line and lines_current_item:
                yield _item(lines_current_item)
                lines_current_item = []
            elif line and 'default project' in line.lower():
                self.default_project = line.split(':')[-1].strip()
            else:
                lines_current_item.append(line)
        if lines_current_item:
            yield _item(lines_current_item)

DAY_PATTERN = re.compile(r'\d\d/\d\d/\d\d\d\d')
def is_day(line):
    """
    >>> is_day('26/07/2013')
    True
    >>> is_day('7:17 9:14')
    False
    >>> is_day('')
    False
    >>> is_day('#4133 (Make Mariupol site and agent work together) - doing')
    False
    """
    return DAY_PATTERN.match(line) is not None

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


ACTIVITY_PATTERN = re.compile("#?([^ ]+) \((.+)\) - (.+)")
def is_activity(line):
    """
    >>> is_activity('#1234 (Make Mariupol site and agent work together) - working in task')
    True
    >>> is_activity('NA (Make Mariupol site and agent work together) - doing')
    True
    >>> is_activity('7:17 9:14')
    False
    >>> is_activity('')
    False
    >>> is_activity('any string')
    False
    """
    return ACTIVITY_PATTERN.match(line) is not None

def process_activity(line):
    """
    >>> process_activity('NA (Make Mariupol site and agent work together) - doing')
    ('NA', 'Make Mariupol site and agent work together', 'doing')
    >>> process_activity('#1234 (Make Mariupol site and agent work together) - working in task')
    ('1234', 'Make Mariupol site and agent work together', 'working in task')
    """
    return ACTIVITY_PATTERN.match(line).groups()

TIME_PATTERN = re.compile(r'(\d?\d:\d\d) (\d?\d:\d\d)')

def is_time(line):
    """
    >>> is_time('7:17 9:14')
    True
    >>> is_time('07:17 09:14')
    True
    >>> is_time('07:17 ')
    False
    >>> is_time('#4133 (Make Mariupol site and agent work together) - doing')
    False
    """
    return TIME_PATTERN.match(line) is not None

def process_time(line):
    """
    >>> process_time('07:17 09:14')
    117
    >>> process_time('0:00 0:05')
    5
    """
    start, end = TIME_PATTERN.match(line).groups()
    def convert_to_minutes(timestr):
        hour, minutes = timestr.split(':')
        hour = int(hour.lstrip('0') or 0)
        minutes = int(minutes.lstrip('0') or 0)
        return hour * 60 + minutes
    return convert_to_minutes(end) - convert_to_minutes(start)

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