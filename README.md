## How to run

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

## How to install additional commands

* in your own repository, create your new commands (more info on this in [How to develop your own commands](#how-to-develop-your-own-commands))
* in ~/.scrumrc file (create it if you don't  have it yet) add a `[extensions]` section and put a reference to the module where your command is. For example:

```
[extensions]
mymodule.mycommands=
```

ATTENTION: the '=' after your module is important!

Then, install your repository to the same virtualenv where the scrum repository is (e.g. `pip install mymodule`).

What `scrum` does is to import your module at startup. All your commands decorated with `@scrum_command("thecommandname")` will be registered and will be available in the command line.

## How to develop your own commands

In your own repository, create python functions that receives as parameter a [ArgumentParser](https://docs.python.org/3/library/argparse.html) object. Annotate such functions with `@scrum_command("thecommandname")`. That's it. You can now add any logic you desire.

You can see an example of a command at [https://github.com/brunovianarezende/scrum/blob/master/scrum/month.py], it shows how to:

- create a command
- read configuration from ~/.scrumrc
- read and parse the file with the scrum content itself

Some utilities functions that one can use to implement the commands can be found at https://github.com/brunovianarezende/scrum/blob/master/scrum/utils.py.