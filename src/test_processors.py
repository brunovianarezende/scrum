import unittest

import gspread

import processors
import settings

TEST_WORKSHEET = '1qcG2e2p654i7Svg0ZGDOh_ArpHgnKJRHfwdgyPMQfuw'

class TestFunctions(unittest.TestCase):

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
    
    def test_first_empty_line(self):
        gc = gspread.login(settings.GOOGLE_DRIVE_USER, settings.GOOGLE_DRIVE_PWD)
        sh = gc.open_by_key(TEST_WORKSHEET)
        ws = sh.add_worksheet(title="test worksheet", rows="10", cols="10")
        try:
            self.assertEqual(1, processors.first_empty_line(ws))
            ws.update_cell(1, 1, 'some value')
            ws.update_cell(2, 1, 'other value')
            self.assertEqual(3, processors.first_empty_line(ws))
            ws.update_cell(10, 1, 'last value')
            self.assertEqual(11, processors.first_empty_line(ws))
        finally:
            sh.del_worksheet(ws)

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


#     def test_update_photobox_spreadsheet(self):
#         settings.PHOTOBOX_SPREADSHEET_KEY = TEST_WORKSHEET
#         gc = gspread.login(settings.GOOGLE_DRIVE_USER, settings.GOOGLE_DRIVE_PWD)
#         sh = gc.open_by_key(TEST_WORKSHEET)
#         ws = sh.add_worksheet(title="Bruno", rows="10", cols="7")
#         try:
#             projects_works = [
#                 {'project': 'AnyProject', 'day': '19/06/2014'},
#             ]
#             days = iter([('19/06/2014', projects_works)])
#             processors.update_photobox_spreadsheet(days)
#     
#             projects_works = [
#                 {'project': 'AnyProject', 'day': '19/06/2014'},
#                 {'project': 'Photobox', 'day': '19/06/2014', 'work_time': 243,
#                  'activities': [
#                     {'description': 'a description',
#                      'ticket': 'ticket',
#                      'title': 'title',
#                      },
#                     {'description': 'another description',
#                      'ticket': 'another ticket',
#                      'title': 'another title',
#                      },
#                  ]}
#             ]
#             days = iter([('19/06/2014', projects_works)])
#         finally:
#             sh.del_worksheet(ws)
#         
