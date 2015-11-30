import unittest

import processors
import settings

TEST_WORKSHEET = '1qcG2e2p654i7Svg0ZGDOh_ArpHgnKJRHfwdgyPMQfuw'

class TestFunctions(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.old_timezone_server = settings.TIMEZONE_SERVER
        settings.TIMEZONE_SERVER = 'http://timezone'
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        settings.TIMEZONE_SERVER = self.old_timezone_server

    def test_register_processor(self):
        registered_processors = processors.PROCESSORS
        processors.PROCESSORS = {}
        try:
            @processors.register_processor('test')
            def test(days):
                pass
            self.assertEqual({'test': test}, processors.PROCESSORS)
        finally:
            processors.PROCESSORS = registered_processors

    def test_timezone_entry(self):
        pw = {'project': 'Soulmates', 'day': '19/06/2014', 'work_time': 155,
             'activities': [
                {'description': 'a description',
                 'ticket': 'ticket',
                 'title': 'title',
                 },
                {'description': 'another description',
                 'ticket': 'another ticket',
                 'title': 'another title',
                 },
                {'description': 'one more description',
                 'ticket': 'one more ticket',
                 'title': 'one more title',
                 'time_group': 2,
                 },
             ],
             'time_groups': {
                1: 120,
                2: 35,
             }
        }

        expected = {
            'hours': '2.5',
            'description': """\
ticket (title) - a description / \
another ticket (another title) - another description / \
one more ticket (one more title) - one more description\
""",
            'date': '2014-06-19',
        }
        self.assertEqual(expected, processors.timezone_entry(pw))

    def test_create_add_timesheet_url(self):
        project_data = {
            "ProjectID":7172,
            "RoleID":5
        }
        entry = {
            'hours': '2.5',
            'description': "my description",
            'date': '2014-06-19',
        }
        settings.TIMEZONE_SERVER = "http://timezone"
        expected = settings.TIMEZONE_SERVER + "/Api/AddTimesheet?date=2014-06-19&description=my%20description&hours=2.5&projectId=7172&roleId=5"
        self.assertEqual(expected, processors.create_add_timesheet_url(project_data, entry))

    def test_rows_for_soulmates_spreadsheet(self):
        projects_works = [
            {'project': 'AnyProject', 'day': '19/06/2014'},
        ]

        self.assertEqual(processors.rows_for_soulmates_spreadsheet(projects_works), None)

        projects_works = [
            {'project': 'AnyProject', 'day': '19/06/2014'},
            {'project': 'Soulmates', 'day': '19/06/2014', 'work_time': 155,
             'activities': [
                {'description': 'a description',
                 'ticket': 'ticket',
                 'title': 'title',
                 },
                {'description': 'another description',
                 'ticket': 'another ticket',
                 'title': 'another title',
                 },
             ]}
        ]
        expected = [('06/19/2014', '', '',
                    'ticket (title) / another ticket (another title)',
                    'Development', '2.5', 'a description / another description')]
        self.assertEqual(processors.rows_for_soulmates_spreadsheet(projects_works),
            expected)

        projects_works = [
            {'project': 'AnyProject', 'day': '19/06/2014'},
            {'project': 'Soulmates', 'day': '19/06/2014', 'work_time': 155,
             'activities': [
                {'description': 'a description',
                 'ticket': 'ticket',
                 'title': 'title',
                 },
                {'description': 'another description',
                 'ticket': 'another ticket',
                 'title': 'another title',
                 },
                {'description': 'one more description',
                 'ticket': 'one more ticket',
                 'title': 'one more title',
                 'time_group': 2,
                 },
             ],
             'time_groups': {
                1: 120,
                2: 35,
             }
             }
        ]
        expected = [('06/19/2014', '', '',
                    'ticket (title) / another ticket (another title)',
                    'Development', '2', 'a description / another description'),
                    ('06/19/2014', '', '',
                     'one more ticket (one more title)',
                     'Development', '0.5', 'one more description')
                   ]
        self.assertEqual(processors.rows_for_soulmates_spreadsheet(projects_works),
            expected)
