import os
import argparse
import sys
import configparser
import importlib

def get_config():
    scrum_rc_path = os.path.expanduser("~/.scrumrc")
    if os.path.exists(scrum_rc_path):
        config = configparser.ConfigParser()
        config.read(scrum_rc_path)
        return config
    else:
        return None

def get_config_extensions():
    config = get_config()
    if config is not None:
        if 'extensions' in config:
            return list(config['extensions'])
    else:
        return []

def get_scrum_file_content():
    with open(settings.SCRUM_FILEPATH, encoding='UTF-8') as f:
        return f.readlines()

default_extensions = ['scrum.month', 'scrum.printers']
extensions = default_extensions + get_config_extensions()

for extension in extensions:
    importlib.__import__(extension)

from scrum import settings
from scrum.commands import COMMANDS

def main():
    if settings.SCRUM_FILEPATH is None:
        print('Attention: SCRUM_FILEPATH must have a value configured in local_settings.py file')
        return
    arg_parser = argparse.ArgumentParser()

    sub_parsers = arg_parser.add_subparsers()
    for _, command_setup_func in sorted(COMMANDS.items()):
        sub_parser = sub_parsers.add_parser(command_setup_func.command_name, **command_setup_func.sub_parser_args)
        handler_func = command_setup_func(sub_parser)
        if handler_func is not None:
            sub_parser.set_defaults(func=handler_func)

    arg_parser.set_default_subparser('printer')
    args = arg_parser.parse_args()
    args.func(args)


def set_default_subparser(self, name, args=None):
    """default subparser selection. Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    , tested with 2.7, 3.2, 3.3, 3.4
    it works with 2.6 assuming argparse is installed

    COPIED FROM http://stackoverflow.com/a/26379693/1922026
    """
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
        if not subparser_found:
            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if args is None:
                sys.argv.insert(1, name)
            else:
                args.insert(0, name)

argparse.ArgumentParser.set_default_subparser = set_default_subparser

if __name__ == '__main__':
    main()
