def return_major_minor_python():

    import sys

    return str(sys.version_info[0])+"."+str(sys.version_info[1])


def return_include_dir():
    from distutils.util import get_platform    
    return get_platform()+'-'+return_major_minor_python()
 

def setup_tort_ext(args,parent_package='',top_path=''):
    from numpy.distutils.misc_util import Configuration
    from os.path import join
    import sys

    config = Configuration('',parent_package,top_path)
    tort_src = [join('crystal_torture/','tort.f90')]

    config.add_library('_tort', sources=tort_src,
                           extra_f90_compile_args = [ args["compile_args"]],
                           extra_link_args=[args["link_args"]])

    sources = [join('crystal_torture','f90wrap_tort.f90')]
    
    config.add_extension(name='_tort',
                          sources=sources,
                          extra_f90_compile_args = [ args["compile_args"]],
                          extra_link_args=[args["link_args"]],
                          libraries=['_tort'],
                          include_dirs=['build/temp.' + return_include_dir()])

    dist_src = [join('crystal_torture/','dist.f90')]
    config.add_extension(name='dist',
                          sources=dist_src,
                          extra_f90_compile_args = [ args["compile_args"]],
                          extra_link_args=[args["link_args"]])


    return config


def check_compiler_gnu():

    result = subprocess.check_output('gfortran --version | grep GNU',shell=True)
    return('GNU' in str(result))

def check_f2py_compiler():

    result = subprocess.check_output('f2py -c --help-fcompiler | grep -A 1 \'Fortran compilers found\' ',shell=True)
    print(result)

    if not check_compiler_gnu():
        print(' GNU compiler not installed. Checking f2py comompiler - this is UNTESTED' )
        print(' Speculatively setting flags - if compile fails, or OpenMP doesn\'t work install gfortran and retry')

     
    if 'GNU' in str(result):
        print('Found gnu compiler. Setting OpenMP flag to \'-fopenmp\'')
        compile_args = '-fopenmp -lgomp -O3'
        link_args = '-lgomp'
    elif 'Intel' in str(result):
        print('Found intel compiler. Setting OpenMP flag to \'-openmp\'')
        compile_args = '-openmp -O3'
        link_args = ''
    elif 'Portland' in str(result):
        print('Found portland compiler. Setting OpenMP flag to \'-mp\'')
        compile_args = '-mp -O3'
        link_args = ''
    elif 'NAG' in str(result):
        print('Found NAG compiler. Setting OpenMP flag to \'-openmp\'')
        compile_args = '-openmp -O3'
        link_args = '' 
    else:   
        print('Not sure what compiler f2py uses. Speculatively setting OpenMP flag to \'-openmp\'')
        compile_args = '-openmp -O3'
        link_args = ''

    args = {'link_args':link_args,'compile_args':compile_args}

    return args



def install_dependencies():
    if '--user' in sys.argv:
        cmd = ['pip install -r requirements.txt --user']
    else:
        cmd = ['pip install -r requirements.txt']
    subprocess.call(cmd, shell=True)

def install_numpy():
    if '--user' in sys.argv:
        cmd = ['pip install numpy --user']
    else:
        cmd = ['pip install numpy']
    subprocess.call(cmd, shell=True)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if __name__ == '__main__':

    import sys
    import subprocess
    import os
    
    install_numpy()
    install_dependencies()
    
    from numpy.distutils.core import setup

#    version_file = open(os.getcwd()+'/crystal_torture/'+ 'VERSION')
#    __version__ = version_file.read().strip()
    exec(open('crystal_torture/version.py').read())

    args = check_f2py_compiler()

    config = {'name':'CrystalTorture',
              'version':__version__,
              'project_description':'A Crystal Tortuosity Module',
              'description':'A Crystal Tortuosity Module',
              'long_description': open('README.txt').read(),
              'long_description_content_type':'text/markdown',
              'author':'Conn O\'Rourke',
     'author_email':'conn.orourke@gmail.com',
     'url':'https://github.com/connorourke/crystaltorture',
     'python_requires':'>=3.3',
     'packages':['crystal_torture'],
     'package_dir':{'crystal_torture':'crystal_torture'},
     'package_data':{'crystal_torture':['*so','*tort*','*dist*','*o*']},
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
                          'numpy==1.14.5',
                          'packaging==17.1',
                          'palettable==3.1.1',
                          'pandas==0.20.1',
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

    config_tort = setup_tort_ext(args,parent_package='crystal_torture',top_path='')
    config2 = dict(config,**config_tort.todict())

    setup(**config2)   

