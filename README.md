How to run:

* make sure you have python >= 3.5 installed
* make sure venv is installed
* get the project (git clone git@github.com:brunovianarezende/scrum.git)
* create a virtual env (eg 'cd scrum && python3 -m venv .envs/scrum')
* activate the virtual env (eg 'source .envs/scrum/bin/activate')
* install the dependencies:
    * `pip install -r requirements.txt`
    * `pip install -e .`
* create a scrum/local_settings.py file pointing to the default file with the timings
* execute the scrum command: `scrum` or `scrum -h`
* To execute the tests, just execute: 'pytest'