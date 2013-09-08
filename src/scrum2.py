import ply.lex as lex

class ScrumLexer(object):
    tokens = ('DAY', 'EOL', 'TIME', 'NA', 'NUMBER', 'LPARENTHESIS',
        'RPARENTHESIS', 'DESCRIPTION', 'ACTIVITY', 'SEPARATOR',
    )
    literals = ('#',)
    states = (
        ('taskdescription', 'exclusive'),
        ('activity', 'exclusive'),
    )
    
    t_DAY = r'\d\d/\d\d/\d\d\d\d'
    t_EOL = r'\n'
    t_TIME = r'\d\d:\d\d'
    t_NA = r'NA'
    t_NUMBER = r'\d+'
    t_ignore  = ' \t'
    t_taskdescription_DESCRIPTION = r'[^\)]+'
    t_activity_ACTIVITY = r'[^\n]+'
    t_taskdescription_ignore = ''
    t_activity_ignore = ''

    # Match the first (. Enter text state.
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

    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)


"""
26/07/2013
7:17 9:14
10:00 12:06
#4133 (Make Mariupol site and agent work together) - doing

dayinfo : DAY \n interval \n activity
interval : TIME TIME | semiinterval
semiinterval : TIME
activity : issue (words) - words
issue : NA | #NUMBER
words : words WORD | WORD
"""

# lexer = lex.lex()

# def main():
#     text = "26/07/2013\n"
#     lexer.input(text)
#     for token in lexer:
#         print token
# 
# if __name__ == '__main__':
#     main()