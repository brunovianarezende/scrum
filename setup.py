from setuptools import setup

setup(name='Scrum',
      version='0.1',
      author='Bruno Rezende',
      author_email='brunovianarezende@gmail.com',
      packages=['scrum'],
      zip_safe=False,
      entry_points={
          'console_scripts': ['scrum=scrum.command_line:main'],
      })

