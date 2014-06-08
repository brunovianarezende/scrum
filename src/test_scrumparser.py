import unittest
import datetime

import scrumparser
scrumparser.DEV_MODE = True
from scrumparser import ScrumLexer, PlyScrumParser, ScrumParser

class TestScrumLexer(unittest.TestCase):
    def test_tokenizer(self):
        lexer = ScrumLexer()
        lexer.build()
        lexer_input = """\
01/12/2013 
12:45 2:31 NA #12345(a nice 123 word)- Word woRd2
DefaultProject: Nice Project
Project: new Project name
"""
        lexer.lexer.input(lexer_input)
        tokens = list(lexer.lexer)
        expected = [
            ('DAY', '01/12/2013'),
            ('EOL', '\n'),
            ('TIME', '12:45'),
            ('TIME', '2:31'),
            ('NA', 'NA'),
            ('TASKIDENTIFIER', '#12345'),
#             ('NUMBERSIGN', '#'),
#             ('NUMBER', '12345'),
            ('LPARENTHESIS', '('),
            ('TITLE', 'a nice 123 word'),
            ('RPARENTHESIS', ')'),
            ('SEPARATOR', '-'),
            ('ACTIVITY', ' Word woRd2'),
            ('EOL', '\n'),
            ('DEFAULTPROJECT', 'DefaultProject:'),
            ('PROJECTNAME', ' Nice Project'),
            ('EOL', '\n'),
            ('PROJECT', 'Project:'),
            ('PROJECTNAME', ' new Project name'),
            ('EOL', '\n'),
        ]
        for i, (ttype, value) in enumerate(expected):
            msg = 'token %s - %s - %s - %s' % (i, (ttype, value), tokens[i], tokens)
            self.assertEqual(tokens[i].type, ttype, msg)
            self.assertEqual(tokens[i].value, value, msg)
        self.assertEqual(len(tokens), len(expected), '%s - %s' % (expected, tokens))

class TestParser(unittest.TestCase):
    def test_parse(self):
        def test_with_eol(parser_input, expected, parser=None):
            if parser is None:
                parser = PlyScrumParser(default_project='Project')
            for p in parser_input.strip(), parser_input.strip() + '\n':
                result = parser.parse(p)
                self.assertEqual(result, expected)

        parser_input = """\
26/07/2013
7:17 9:14
10:00 12:06
#4133 (Make Mariupol site and agent work together) - doing
#1 (new test) - doing too
NA (Not Available) - testing everything
"""
        expected = [
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together'
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test'
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available'
                 },
            ],
            'day': '26/07/2013',
            'work_time': 243,
            'project': 'Project',
            }
        ]
        test_with_eol(parser_input, expected)

        parser = PlyScrumParser(default_project='Project')
        parser_input = """\
DefaultProject: my Nice project
"""
        expected = None
        test_with_eol(parser_input, expected, parser=parser)
        for _ in parser_input.strip(), parser_input.strip() + '\n':
            self.assertEqual(parser.default_project, 'my Nice project')

        parser_input = """\
26/07/2013
7:17 9:14
10:00 12:06
#4133 (Make Mariupol site and agent work together) - doing
#1 (new test) - doing too
NA (Not Available) - testing everything
Project: New Project Name
1:14 2:05
#1234 (First) - First activity
NA (Second) - Second activity
#3 (Third) - Third activity
"""
        expected = [
            {
             'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together'
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test'
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available'
                 },
            ],
            'day': '26/07/2013',
            'work_time': 243,
            'project': 'Project',
            },
            {
             'activities': [
                {
                 'description': 'First activity',
                 'ticket': '1234',
                 'title': 'First',
                 },
                {
                 'description': 'Second activity',
                 'ticket': 'NA',
                 'title': 'Second',
                 },
                {
                 'description': 'Third activity',
                 'ticket': '3',
                 'title': 'Third'
                 },
            ],
            'day': '26/07/2013',
            'work_time': 51,
            'project': 'New Project Name',
            },
        ]
        test_with_eol(parser_input, expected)
        
        parser_input = """
26/07/2013
7:17
#4133 (Make Mariupol site and agent work together) - doing
#1 (new test) - doing too
NA (Not Available) - testing everything
"""
        expected = [
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together'
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test'
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available'
                 },
            ],
            'day': '26/07/2013',
            'work_time_partial': (0, '7:17'),
            'project': 'Project',
            }
        ]
        test_with_eol(parser_input, expected)

        parser_input = """
26/07/2013
7:17 9:17
9:18
#4133 (Make Mariupol site and agent work together) - doing
#1 (new test) - doing too
NA (Not Available) - testing everything
"""
        expected = [
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together'
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test'
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available'
                 },
            ],
            'day': '26/07/2013',
            'work_time_partial': (120, '9:18'),
            'project': 'Project',
            }
        ]
        test_with_eol(parser_input, expected)

        parser_input = """
23/07/2013
7:17 8:17
8:20 9:20
#4133 (Make Mariupol site and agent work together) - doing
13:25 14:26
#1 (new test) - doing too
NA (Not Available) - testing everything
Project: Other Project
7:17 9:17
#3 (3) - doing
#4 (4) - doing too
"""
        expected = [
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together',
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test',
                 'time_group': 2,
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available',
                 'time_group': 2,
                 },
            ],
            'time_groups': {
                1: 120,
                2: 61,
            },
            'day': '23/07/2013',
            'work_time': 181,
            'project': 'Project',
            },
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '3',
                 'title': '3',
                 },
                {
                 'description': 'doing too',
                 'ticket': '4',
                 'title': '4',
                 },
            ],
            'day': '23/07/2013',
            'work_time': 120,
            'project': 'Other Project',
            }
        ]
        test_with_eol(parser_input, expected)

        parser_input = """
23/07/2013
7:17 8:17
13:25 
#4133 (Make Mariupol site and agent work together) - doing
8:20 9:20
#1 (new test) - doing too
NA (Not Available) - testing everything
"""
        expected = [
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together',
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test',
                 'time_group': 2,
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available',
                 'time_group': 2,
                 },
            ],
            'time_groups': {
                1: (60, '13:25'),
                2: 60,
            },
            'day': '23/07/2013',
            'work_time_partial': (120, '13:25'),
            'project': 'Project',
            },
        ]
        test_with_eol(parser_input, expected)

        parser_input = """
23/07/2013
7:17 8:17
13:25 14:25
#4133 (Make Mariupol site and agent work together) - doing
8:20
#1 (new test) - doing too
NA (Not Available) - testing everything
"""
        expected = [
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together',
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test',
                 'time_group': 2,
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available',
                 'time_group': 2,
                 },
            ],
            'time_groups': {
                1: 120,
                2: (0, '8:20'),
            },
            'day': '23/07/2013',
            'work_time_partial': (120, '8:20'),
            'project': 'Project',
            },
        ]
        test_with_eol(parser_input, expected)

        parser_input = """
23/07/2013
7:17 8:17
#4133 (Make Mariupol site and agent work together) - doing
8:20
#1 (new test) - doing too
13:25 14:25
NA (Not Available) - testing everything
"""
        expected = [
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together',
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test',
                 'time_group': 2,
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available',
                 'time_group': 3,
                 },
            ],
            'time_groups': {
                1: 60,
                2: (0, '8:20'),
                3: 60,
            },
            'day': '23/07/2013',
            'work_time_partial': (120, '8:20'),
            'project': 'Project',
            },
        ]
        test_with_eol(parser_input, expected)

        parser_input = """
23/07/2013
7:17 8:17
#4133 (Make Mariupol site and agent work together) - doing
8:20
#1 (new test) - doing too
13:25
NA (Not Available) - testing everything
"""
        expected = None
        test_with_eol(parser_input, expected)

        parser_input = """
DefaultProject: Some default Project

23/07/2013
Project: my nice project
7:17 8:17
#4133 (Make Mariupol site and agent work together) - doing
8:20 8:25
#DC-10 (new test) - doing too
"""
        expected = [
            {
            'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together',
                 },
                {
                 'description': 'doing too',
                 'ticket': 'DC-10',
                 'title': 'new test',
                 'time_group': 2,
                 },
            ],
            'time_groups': {
                1: 60,
                2: 5,
            },
            'day': '23/07/2013',
            'work_time': 65,
            'project': 'my nice project',
            },
        ]
        test_with_eol(parser_input, expected)

class TestScrumParser(unittest.TestCase):
    def test_parse(self):
        parser_input = """\
DefaultProject: Project

26/07/2013
7:17 9:14
10:00 12:06
#4133 (Make Mariupol site and agent work together) - doing
#1 (new test) - doing too
NA (Not Available) - testing everything
Project: New Project Name
1:14 2:05
#1234 (First) - First activity
NA (Second) - Second activity
#3 (Third) - Third activity

25/07/2013
7:17 9:14
10:00 12:06
#1234 (title) - doing

DefaultProject: other project

24/07/2013
7:17 9:14
10:00 12:06
#25 (other title) - really doing

23/07/2013
7:17 9:17
10:00 11:00
#4133 (Make Mariupol site and agent work together) - doing
11:00 11:15
#1 (new test) - doing too
11:15 12:00
NA (Not Available) - testing everything
Project: New Project Name
13:05 14:05
#1234 (First) - First activity
NA (Second) - Second activity
#3 (Third) - Third activity
"""

        parser = ScrumParser('')
        items = parser.parse(parser_input.split('\n'))
        expected = (datetime.date(2013, 7, 26), [
            {
             'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together'
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test'
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available'
                 },
            ],
            'day': '26/07/2013',
            'work_time': 243,
            'project': 'Project',
            },
            {
             'activities': [
                {
                 'description': 'First activity',
                 'ticket': '1234',
                 'title': 'First',
                 },
                {
                 'description': 'Second activity',
                 'ticket': 'NA',
                 'title': 'Second',
                 },
                {
                 'description': 'Third activity',
                 'ticket': '3',
                 'title': 'Third'
                 },
            ],
            'day': '26/07/2013',
            'work_time': 51,
            'project': 'New Project Name',
            },
        ])
        self.assertEqual(items.next(), expected)

        expected = (datetime.date(2013, 7, 25), [
            {
             'activities': [
                {
                 'description': 'doing',
                 'ticket': '1234',
                 'title': 'title'
                 },
            ],
            'day': '25/07/2013',
            'work_time': 243,
            'project': 'Project',
            },
        ])
        self.assertEqual(items.next(), expected)

        expected = (datetime.date(2013, 7, 24), [
            {
             'activities': [
                {
                 'description': 'really doing',
                 'ticket': '25',
                 'title': 'other title'
                 },
            ],
            'day': '24/07/2013',
            'work_time': 243,
            'project': 'other project',
            },
        ])
        self.assertEqual(items.next(), expected)

        expected = (datetime.date(2013, 7, 23), [
            {
             'activities': [
                {
                 'description': 'doing',
                 'ticket': '4133',
                 'title': 'Make Mariupol site and agent work together'
                 },
                {
                 'description': 'doing too',
                 'ticket': '1',
                 'title': 'new test',
                 'time_group': 2,
                 },
                {
                 'description': 'testing everything',
                 'ticket': 'NA',
                 'title': 'Not Available',
                 'time_group': 3,
                 },
            ],
            'time_groups': {
                1: 180,
                2: 15,
                3: 45,
            },
            'day': '23/07/2013',
            'work_time': 240,
            'project': 'other project',
            },
            {
             'activities': [
                {
                 'description': 'First activity',
                 'ticket': '1234',
                 'title': 'First',
                 },
                {
                 'description': 'Second activity',
                 'ticket': 'NA',
                 'title': 'Second',
                 },
                {
                 'description': 'Third activity',
                 'ticket': '3',
                 'title': 'Third'
                 },
            ],
            'day': '23/07/2013',
            'work_time': 60,
            'project': 'New Project Name',
            },
        ])
        self.assertEqual(items.next(), expected)

        self.assertRaises(StopIteration, items.next)