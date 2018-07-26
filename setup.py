
#from crystal_torture import __version__
from setuptools import setup
import subprocess
import distutils.cmd
import distutils.log
import os

class BuildDistCommand(distutils.cmd.Command):
    """
    Command to compile and wrap dist.f90
    """

    description = 'wrap and compile dist.f90'
    user_options = []

    def initialize_options(self):
       """Set default values for options."""
       # Each user option must be listed here with their default value.
       self.pylint_rcfile = ''

    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
           assert os.path.exists(self.pylint_rcfile), (
                'Pylint config file %s does not exist.' % self.pylint_rcfile)

    def run(self):
        """Run command to compile & wrap"""

        command = ['f2py -c --opt=\'-O3\' --f90flags=\'-fopenmp\' -lgomp -m dist dist.f90']
        top_dir = os.getcwd()
        src_dir = top_dir + '/crystal_torture'
        os.chdir(src_dir)
        self.announce(
            'Running command: %s' % str(command),level=distutils.log.INFO)
        subprocess.check_call(command,shell=True)
        os.chdir(top_dir)

class BuildTortCommand(distutils.cmd.Command):
    """
    Command to compile and wrap tort.f90
    """

    description = 'wrap and compile tort.f90'
    user_options = []

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.pylint_rcfile = ''

    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
           assert os.path.exists(self.pylint_rcfile), (
                 'Pylint config file %s does not exist.' % self.pylint_rcfile)

    def run(self):
        """Run command to compile & wrap"""
    
        command1 = ['gfortran -c -O3 -fPIC tort.f90']
        command2 = ['f2py-f90wrap -c --opt=\'-O3\' --f90flags=\'-fopenmp\' -lgomp -m _tort f90wrap_tort.f90 tort.o']

        top_dir = os.getcwd()
        src_dir = top_dir + '/crystal_torture'
        os.chdir(src_dir)
        self.announce(
            'Running command: %s' % str(command1),level=distutils.log.INFO)
        subprocess.check_call(command1, shell=True)
        self.announce(
            'Running command: %s' % str(command2),level=distutils.log.INFO)
        subprocess.check_call(command2,shell=True)
        os.chdir(top_dir)


long_description = open('README.md').read()

config = {'name':'CrystalTorture',
     'version':"1.0.0",#__version__,
     'description':'A Crystal Tortuosity Module',
     'long_description':long_description,
     'author':'Conn O\'Rourke',
     'author_email':'conn.orourke@gmail.com',
     'url':'https://github.com/connorourke/crystaltorture',
     'python_requires':'>=3.5',
     'packages':['crystal_torture'],
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

setup(cmdclass={'dist':BuildDistCommand, 'tort':BuildTortCommand},**config)
#setup(**config)

