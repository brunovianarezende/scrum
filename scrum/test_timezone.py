import unittest

from . import timezone
from . import settings

class TestFunctions(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.old_timezone_server = settings.TIMEZONE_SERVER
        settings.TIMEZONE_SERVER = 'http://timezone'
    
    def test_timezone_entry(self):
        pw = {'project': 'SomeProject', 'day': '19/06/2014', 'work_time': 155,
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
        self.assertEqual(expected, timezone.timezone_entry(pw))


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
        self.assertEqual(expected, timezone.create_add_timesheet_url(project_data, entry))
