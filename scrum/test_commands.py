import unittest

from . import commands

class TestFunctions(unittest.TestCase):
    def test_scrum_command(self):
        registered_commands = commands.COMMANDS
        commands.COMMANDS = {}
        try:
            @commands.scrum_command('test')
            def test_definition(days):
                pass
            self.assertEqual({'test': test_definition}, commands.COMMANDS)
            self.assertEqual(test_definition.command_name, 'test')
            self.assertEqual(test_definition.sub_parser_args, {})
            @commands.scrum_command('test', description="something nice")
            def test_definition(days):
                pass
            self.assertEqual(test_definition.command_name, 'test')
            self.assertEqual(test_definition.sub_parser_args, {'description': 'something nice'})
        finally:
            commands.COMMANDS = registered_commands
