import argparse

from scrumparser import ScrumParser
from commands import COMMANDS
from utils import get_matching_projects_work
import month as _
import timezone as _
import printers as _

def main():
    arg_parser = argparse.ArgumentParser()
#     arg_parser.add_argument('-p', '--processor', help="run the processor. By"
#         " default only print processors run.", action="append")
#     arg_parser.add_argument('-d', '--day', help="days to run the processors for. "
#         "If no day is given, use the last day with data in the file. "
#         "Only single day processors will be executed if this option is used.",
#         action="append")
#     arg_parser.add_argument('-l', '--listprocessors', help="list all available"
#         " processors.", action='store_true')
    
    sub_parsers = arg_parser.add_subparsers()
    for _, command_setup_func in sorted(COMMANDS.items()):
        sub_parser = sub_parsers.add_parser(command_setup_func.command_name, **command_setup_func.sub_parser_args)
        handler_func = command_setup_func(sub_parser)
        if handler_func is not None:
            sub_parser.set_defaults(func=handler_func)

    args = arg_parser.parse_args()
    args.func(args)
#         processors = [spreadsheet_printer, current_worked_time_printer,
#                   per_activity_printer, scrum_printer]

def old_main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', '--day', help="days to run the processors for. "
        "If no day is given, use the last day with data in the file. "
        "Only single day processors will be executed if this option is used.",
        action="append")
    arg_parser.add_argument('-l', '--listprocessors', help="list all available"
        " processors.", action='store_true')

    args = arg_parser.parse_args()

    days_to_execute = args.day
    
    processors = [spreadsheet_printer, current_worked_time_printer,
              per_activity_printer, scrum_printer]

    scrum_parser = ScrumParser('')
    if days_to_execute:
        processors = [p for p in processors if not getattr(p, 'multiple_days_processor', False)]
        days = scrum_parser.parse(open('/home/brunore/Desktop/cs_data.txt').readlines())
        projects_work_for_days = get_matching_projects_work(days_to_execute, days)
        for projects_work in projects_work_for_days:
            for processor in processors:
                processor(projects_work)
    else:
        for processor in processors:
            days = scrum_parser.parse(open('/home/brunore/Desktop/cs_data.txt').readlines())
            if getattr(processor, 'multiple_days_processor', False):
                processor(days)
            else:
                _, projects_work = days.next()
                processor(projects_work)



if __name__ == '__main__':
    main()