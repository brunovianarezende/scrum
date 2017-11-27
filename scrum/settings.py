MAPPINGS = {}
SCRUM_FILEPATH = None # it must be setup in local_settings.py file

try:
    from .local_settings import *
    print(SCRUM_FILEPATH)
except Exception as e:
    print("local settings couldn't be loaded: %s" % e)
    pass