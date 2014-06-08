import datetime

import ply.lex as lex
import ply.yacc as yacc

class ScrumLexer(object):
    tokens = ('DAY', 'EOL', 'TIME', 'NA', 'LPARENTHESIS',
        'RPARENTHESIS', 'TITLE', 'ACTIVITY', 'SEPARATOR', 
        'DEFAULTPROJECT', 'PROJECTNAME', 'PROJECT', 'TASKIDENTIFIER'
    )
    states = (
        ('taskdescription', 'exclusive'),
        ('activity', 'exclusive'),
        ('defaultproject', 'exclusive'),
        ('project', 'exclusive'),
    )
    
    t_DAY = r'\d\d/\d\d/\d\d\d\d'
    t_EOL = r'\n'
    t_TASKIDENTIFIER = r'\#[^ \(]+'
    t_TIME = r'\d?\d:\d\d'
    t_NA = r'NA'
    t_ignore  = ' \t'
    t_taskdescription_TITLE = r'[^\)]+'
    t_activity_ACTIVITY = r'[^\n]+'
    t_defaultproject_PROJECTNAME = r'[^\n]+'
    t_project_PROJECTNAME = r'[^\n]+'
    t_project_ignore = ''
    t_defaultproject_ignore = ''
    t_taskdescription_ignore = ''
    t_activity_ignore = ''

    def t_PROJECT(self, t):
        r'Project:'
        t.lexer.begin('project')
        return t

    def t_project_EOL(self, t):
        r'\n'
        t.lexer.begin('INITIAL')
        return t

    def t_DEFAULTPROJECT(self, t):
        r'DefaultProject:'
        t.lexer.begin('defaultproject')
        return t

    def t_defaultproject_EOL(self, t):
        r'\n'
        t.lexer.begin('INITIAL')
        return t

    def t_LPARENTHESIS(self, t):
        r'\('
        t.type = 'LPARENTHESIS'
        t.lexer.begin('taskdescription')
        return t

    def t_SEPARATOR(self, t):
        r'-'
        t.lexer.begin('activity')
        return t
    
    def t_taskdescription_RPARENTHESIS(self, t):
        r'\)'
        t.lexer.begin('INITIAL')
        return t

    def t_activity_EOL(self, t):
        r'\n'
        t.lexer.begin('INITIAL')
        return t

    def t_error(self, t):
        print "initial: Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def t_taskdescription_error(self, t):
        print "taskdescription: Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def t_activity_error(self, t):
        print "activity: Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def t_defaultproject_error(self, t):
        print "defaultproject: Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def t_project_error(self, t):
        print "project: Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)


def convert_to_minutes(timestr):
    """
    >>> convert_to_minutes('9:54')
    594
    """
    hour, minutes = timestr.split(':')
    hour = int(hour.lstrip('0') or 0)
    minutes = int(minutes.lstrip('0') or 0)
    return hour * 60 + minutes


class PlyScrumParser(object):
    def __init__(self, default_project):
        lexer = ScrumLexer()
        lexer.build()
        self.default_project = default_project
        self._current_project = default_project
        self._times_groups = {}
        self._current_time_group = 1
        self.lexer = lexer.lexer
        self.tokens = lexer.tokens
        self.yacc = yacc.yacc(module=self)

    def parse(self, input_string):
        input_string = input_string.strip() + '\n'
        result = self.yacc.parse(input_string, lexer=self.lexer)
        self._current_project = self.default_project
        self._times_groups = {}
        self._current_time_group = 1
        return result

    def p_content(self, p):
        """content : dayinfo
                   | defaultproject"""
        p[0] = p[1]

    def p_dayinfo(self, p):
#         'dayinfo : DAY EOL intervals EOL activities'
        'dayinfo : DAY EOL projectsdata'
        result = [dict(d) for d in p[3]]
        for d in result:
            d.update(**{'day': p[1]})
        p[0] = result

    def p_projectsdata_multiple(self, p):
        'projectsdata : projectsdata changeprojectinfo projectdata'
        p[0] = p[1] + [p[3]]

    def p_changeprojectinfo(self, p):
        'changeprojectinfo : PROJECT PROJECTNAME EOL'
        self._current_project = p[2].strip()
        self._current_time_group = 1
        self._times_groups = {}

    def p_projectsdata_single(self, p):
        'projectsdata : projectdata'
        p[0] = [p[1]]

    def p_projectdata_fullintervals(self, p):
        'projectdata : activitiesdatamult'
        p[0] = dict(p[1])
        p[0]['project'] = self._current_project
        if len(self._times_groups) != 1:
            p[0]['time_groups'] = self._times_groups

    def p_projectdata_partialintervals(self, p):
        'projectdata : partialactivitiesdatamult'
        p[0] = dict(p[1])
        p[0]['project'] = self._current_project
        if len(self._times_groups) != 1:
            p[0]['time_groups'] = self._times_groups

    def p_activitiesdatamult_multiple(self, p):
        'activitiesdatamult : activitiesdatamult activitiesdata'
        merged = dict(p[1])
        merged['work_time'] += p[2]['work_time']
        merged['activities'].extend(p[2]['activities'])
        p[0] = merged

    def p_activitiesdatamult_single(self, p):
        'activitiesdatamult : activitiesdata'
        p[0] = p[1]

    def p_activitiesdata(self, p):
        'activitiesdata : intervals activities'
        self._times_groups[self._current_time_group] = p[1]
        self._current_time_group += 1
        p[0] = {'work_time': p[1], 'activities': p[2],}

    def p_partialactivitiesdatamult_multiple1(self, p):
        'partialactivitiesdatamult : activitiesdatamult partialactivitiesdata'
        p[0] = self._gen_partialactivities_data(p[1], p[2])

    def p_partialactivitiesdatamult_multiple2(self, p):
        'partialactivitiesdatamult : partialactivitiesdata activitiesdatamult'
        p[0] = self._gen_partialactivities_data(p[1], p[2])

    def p_partialactivitiesdatamult_multiple3(self, p):
        'partialactivitiesdatamult : activitiesdatamult partialactivitiesdata activitiesdatamult'
        partial = self._gen_partialactivities_data(p[1], p[2])
        p[0] = self._gen_partialactivities_data(partial, p[3])

    def _gen_partialactivities_data(self, item1, item2):
        result = {}
        if 'work_time_partial' in item1:
            partial, full = item1, item2
        else:
            partial, full = item2, item1
        partial_time, partial_interval = partial['work_time_partial']
        partial_time += full['work_time']
        activities = []
        activities.extend(item1['activities'])
        activities.extend(item2['activities'])
        result['work_time_partial'] = (partial_time, partial_interval)
        result['activities'] = activities
        return result

    def p_partialactivitiesdatamult_single(self, p):
        'partialactivitiesdatamult : partialactivitiesdata'
        p[0] = p[1]

    def p_partialactivitiesdata(self, p):
        'partialactivitiesdata : partialintervals activities'
        self._times_groups[self._current_time_group] = p[1]
        self._current_time_group += 1
        p[0] = {'work_time_partial': p[1], 'activities': p[2],}

    def p_defaultproject(self, p):
        'defaultproject : DEFAULTPROJECT PROJECTNAME EOL'
        self.default_project = p[2].strip()

    def p_intervals_multiple(self, p):
        'intervals : intervals interval'
        p[0] = p[1] + p[2]

    def p_intervals_single(self, p):
        'intervals : interval'
        p[0] = p[1]

    def p_interval(self, p):
        'interval : TIME TIME EOL'
        p[0] = convert_to_minutes(p[2]) - convert_to_minutes(p[1])

    def p_partialintervals_multiple(self, p):
        'partialintervals : intervals semiinterval'
        p[0] = (p[1], p[2])

    def p_partialintervals_single(self, p):
        'partialintervals : semiinterval'
        p[0] = (0, p[1])

    def p_semiinterval(self, p):
        'semiinterval : TIME EOL'
        p[0] = p[1]

    def p_activities(self, p):
        'activities : activity'
        p[0] = [p[1]]

    def p_activities_multiple(self, p):
        'activities : activities activity'
        p[0] = p[1] + [p[2]]

    def p_activity_single(self, p):
        'activity : taskidentifier LPARENTHESIS TITLE RPARENTHESIS SEPARATOR ACTIVITY EOL'
        p[0] = {
            'description': p[6].strip(),
            'ticket': p[1],
            'title': p[3].strip(),
        }
        if self._current_time_group != 1:
            p[0]['time_group'] = self._current_time_group

    def p_taskidentifier_available(self, p):
        'taskidentifier : TASKIDENTIFIER'
        p[0] = p[1].lstrip('#')

    def p_taskidentifier_notavailable(self, p):
        'taskidentifier : NA'
        p[0] = p[1]
    
    def p_error(self, error):
        print error

class ScrumParser(object):
    def __init__(self, default_project):
        self.parser = PlyScrumParser(default_project=default_project)

    def parse(self, lines):
        current_lines = []
        for line in lines:
            line = line.strip()
            if line:
                current_lines.append(line)
            elif not current_lines:
                pass
            else:
                item_str = '\n'.join(current_lines)
                current_lines = []
                result = self.parser.parse(item_str)
                if result:
                    day = datetime.datetime.strptime(result[0]['day'], '%d/%m/%Y').date()
                    yield day, result
