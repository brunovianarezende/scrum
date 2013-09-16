import unittest

from scrum2 import ScrumLexer, PlyScrumParser, ScrumParser

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
            ('NUMBERSIGN', '#'),
            ('NUMBER', '12345'),
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
        parser = PlyScrumParser(default_project='Project')
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
        for p in parser_input.strip(), parser_input.strip() + '\n':
            result = parser.parse(p)
            self.assertEqual(result, expected)

        parser = PlyScrumParser(default_project='Project')
        parser_input = """\
DefaultProject: my Nice project
"""
        expected = None
        for p in parser_input.strip(), parser_input.strip() + '\n':
            result = parser.parse(p)
            self.assertEqual(result, expected)
            self.assertEqual(parser.default_project, 'my Nice project')

        parser = PlyScrumParser(default_project='Project')
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
        for p in parser_input.strip(), parser_input.strip() + '\n':
            result = parser.parse(p)
            self.assertEqual(result, expected)

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
            'work_time_partial': 0,
            'project': 'Project',
            }
        ]
        for p in parser_input.strip(), parser_input.strip() + '\n':
            result = parser.parse(p)
            self.assertEqual(result, expected)

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
            'work_time_partial': 120,
            'project': 'Project',
            }
        ]
        for p in parser_input.strip(), parser_input.strip() + '\n':
            result = parser.parse(p)
            self.assertEqual(result, expected)

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
"""
        parser = ScrumParser('')
        items = parser.parse(parser_input.split('\n'))
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
        self.assertEqual(items.next(), expected)

        expected = [
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
        ]
        self.assertEqual(items.next(), expected)

        expected = [
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
        ]
        self.assertEqual(items.next(), expected)

        self.assertRaises(StopIteration, items.next)