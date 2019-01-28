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

def build_f90_src_for_tests():
    import os
    os.chdir('crystal_torture/')
    subprocess.call('pwd', shell=True)
    subprocess.call('ls', shell=True)
    subprocess.call('./build_tort.sh', shell=True)
    os.chdir('../')


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if __name__ == '__main__':

    import sys
    import subprocess
    import os
    
    install_numpy()
    install_dependencies()
    build_f90_src_for_tests()
    
    from numpy.distutils.core import setup

    exec(open('crystal_torture/version.py').read())

    args = check_f2py_compiler()

    config = {'name':'CrystalTorture',
              'version':__version__,
              'project_description':'A Crystal Tortuosity Module',
              'description':'A Crystal Tortuosity Module',
              'long_description': open('README.md').read(),
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
     'install_requires': ['coverage',
                          'numpy',
                          'pymatgen'
                          ]
}

    config_tort = setup_tort_ext(args,parent_package='crystal_torture',top_path='')
    config2 = dict(config,**config_tort.todict())

    setup(**config2)   

