import unittest

from scrum2 import ScrumLexer

class TestScrumLexer(unittest.TestCase):
    def test_tokenizer(self):
        lexer = ScrumLexer()
        lexer.build()
        lexer_input = """\
01/12/2013 
12:45 NA #12345(a nice 123 word)- Word woRd2
"""
        lexer.lexer.input(lexer_input)
        tokens = list(lexer.lexer)
        expected = [
            ('DAY', '01/12/2013'),
            ('EOL', '\n'),
            ('TIME', '12:45'),
            ('NA', 'NA'),
            ('#', '#'),
            ('NUMBER', '12345'),
            ('LPARENTHESIS', '('),
            ('DESCRIPTION', 'a nice 123 word'),
            ('RPARENTHESIS', ')'),
            ('SEPARATOR', '-'),
            ('ACTIVITY', ' Word woRd2'),
            ('EOL', '\n'),
        ]
        for i, (ttype, value) in enumerate(expected):
            msg = 'token %s - %s - %s - %s' % (i, (ttype, value), tokens[i], tokens)
            self.assertEqual(tokens[i].type, ttype, msg)
            self.assertEqual(tokens[i].value, value, msg)
        self.assertEqual(len(tokens), len(expected), '%s - %s' % (expected, tokens))