COMMANDS = {}

def scrum_command(name, **sub_parser_args):
    def inner(func):
        func.command_name = name
        func.sub_parser_args = sub_parser_args.copy()
        COMMANDS[name] = func
        return func
    return inner
