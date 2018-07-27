
import subprocess
from distutils.core import setup, Command
import distutils.log
import os
import sys
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info


def check_compiler_gnu():

    result = subprocess.check_output('f2py -c --help-fcompiler | grep -A 1 \'Fortran compilers found\' ',shell=True)

    return('GNU' in str(result))


def custom_command():    
    """Run command to compile & wrap"""

    if check_compiler_gnu():
        command = ['f2py -c --opt=\'-O3\' --f90flags=\'-fopenmp\' -lgomp -m dist dist.f90 > /home/cor/temp']
    
        command1 = ['gfortran -c -O3 -fPIC tort.f90']
        command2 = ['f2py-f90wrap -c --opt=\'-O3\' --f90flags=\'-fopenmp\' -lgomp -m _tort f90wrap_tort.f90 tort.o']

        top_dir = os.getcwd()
        src_dir = top_dir + '/crystal_torture'
        os.chdir(src_dir)
        subprocess.check_call(command1, shell=True)
        subprocess.check_call(command2,shell=True)
        subprocess.check_call(command,shell=True)
        os.chdir(top_dir)
    else:
        sys.exit("Error: f2py is using a compiler other than gfortran. Please install gfortran.")

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        custom_command()

class CustomDevelopCommand(develop):
    def run(self):
        develop.run(self)
        custom_command()

class CustomEggInfoCommand(egg_info):
    def run(self):
        egg_info.run(self)
        custom_command()


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


version_file = open(os.getcwd()+'/crystal_torture/'+ 'VERSION')
__version__ = version_file.read().strip()

config = {'name':'CrystalTorture',
     'version':__version__,
     'project_description':'A Crystal Tortuosity Module',
     'description':'A Crystal Tortuosity Module',
     'long_description': read('README.md'),
     'long_description_content_type':'text/markdown',
     'author':'Conn O\'Rourke',
     'author_email':'conn.orourke@gmail.com',
     'url':'https://github.com/connorourke/crystaltorture',
     'python_requires':'>=3.5',
     'packages':['crystal_torture'],
     'package_dir':{'crystal_torture':'crystal_torture'},
     'package_data':{'crystal_torture':['*so','*tort*','*dist*']},
     'name': 'crystal_torture',
     'license': 'MIT',
     'install_requires': [ 'alabaster==0.7.11',
                          'Babel==2.6.0',
                          'backcall==0.1.0',
                          'bleach==2.1.3',
                          'certifi==2018.4.16',
                          'chardet==3.0.4',
                          'coverage==4.5.1',
                          'cycler==0.10.0',
                          'ddt==1.2.0',
                          'decorator==4.3.0',
                          'docutils==0.14',
                          'entrypoints==0.2.3',
                          'numpy==1.14.5',
                          'f90wrap==0.1.4',
                          'html5lib==1.0.1',
                          'idna==2.7',
                          'imagesize==1.0.0',
                          'ipykernel==4.8.2',
                          'ipython==6.4.0',
                          'ipython-genutils==0.2.0',
                          'ipywidgets==7.2.1',
                          'jedi==0.12.1',
                          'Jinja2==2.10',
                          'jsonschema==2.6.0',
                          'jupyter==1.0.0',
                          'jupyter-client==5.2.3',
                          'jupyter-console==5.2.0',
                          'jupyter-core==4.4.0',
                          'kiwisolver==1.0.1',
                          'MarkupSafe==1.0',
                          'matplotlib==2.2.2',
                          'mistune==0.8.3',
                          'monty==1.0.3',
                          'mpmath==1.0.0',
                          'nbconvert==5.3.1',
                          'nbformat==4.4.0',
                          'notebook==5.5.0',
                          'packaging==17.1',
                          'palettable==3.1.1',
                          'pandas==0.23.1',
                          'pandocfilters==1.4.2',
                          'parso==0.3.1',
                          'pexpect==4.6.0',
                          'pickleshare==0.7.4',
                          'prompt-toolkit==1.0.15',
                          'ptyprocess==0.6.0',
                          'PyDispatcher==2.0.5',
                          'Pygments==2.2.0',
                          'pymatgen==2018.6.27',
                          'pyparsing==2.2.0',
                          'python-dateutil==2.7.3',
                          'pytz==2018.5',
                          'pyzmq==17.0.0',
                          'qtconsole==4.3.1',
                          'requests==2.19.1',
                          'ruamel.yaml==0.15.42',
                          'scipy==1.1.0',
                          'Send2Trash==1.5.0',
                          'simplegeneric==0.8.1',
                          'six==1.11.0',
                          'snowballstemmer==1.2.1',
                          'spglib==1.10.3.65',
                          'Sphinx==1.7.6',
                          'sphinxcontrib-websupport==1.1.0',
                          'sympy==1.1.1',
                          'tabulate==0.8.2',
                          'terminado==0.8.1',
                          'testpath==0.3.1',
                          'tornado==5.1',
                          'traitlets==4.3.2',
                          'urllib3==1.23',
                          'wcwidth==0.1.7',
                          'webencodings==0.5.1',
                          'widgetsnbextension==3.2.1']
}


setup(
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },**config
)
