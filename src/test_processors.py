import unittest

import gspread

import processors
import settings

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
        sh = gc.open_by_key('1qcG2e2p654i7Svg0ZGDOh_ArpHgnKJRHfwdgyPMQfuw')
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
    
    def test_rows_for_spreadsheet(self):
        pass