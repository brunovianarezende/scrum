TIMEZONE_SERVER = None
TIMEZONE_USER = None
TIMEZONE_PWD = None
MAPPINGS = {}
SCRUM_FILEPATH = None # it must be setup in local_settings.py file

try:
    from local_settings import *
except:
    pass