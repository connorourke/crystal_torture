
from crystal_torture import __version__
from setuptools import setup

long_description = open('README.md').read()

config = {'name':'CrystalTorture',
     'version':'1.0.0',
     'description':'A Crystal Tortuosity Module',
     'long_description':long_description,
     'author':'Conn O\'Rourke',
     'author_email':'conn.orourke@gmail.com',
     'url':'https://github.com/connorourke/crystaltorture',
     'python_requires':'>=3.5'
     'packages':['crystal_torture']
     }

setup(**config)


