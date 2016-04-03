import argparse

from commands import COMMANDS
import month as _
import timezone as _
import printers as _

def main():
    arg_parser = argparse.ArgumentParser()
    
    sub_parsers = arg_parser.add_subparsers()
    for _, command_setup_func in sorted(COMMANDS.items()):
        sub_parser = sub_parsers.add_parser(command_setup_func.command_name, **command_setup_func.sub_parser_args)
        handler_func = command_setup_func(sub_parser)
        if handler_func is not None:
            sub_parser.set_defaults(func=handler_func)

    args = arg_parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()