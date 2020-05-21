import os
from setuptools import setup, find_namespace_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
    """
    Get package version (without import the package, which may or may not work)
    :return: version info in maj.min.bld.0 format
    """
    version_dict = {}
    exec(open("src/aspire/version.py").read(), version_dict)
    return version_dict['version']


setup(
    name='aspire',
    version=get_version(),

    description='Algorithms for Single Particle Reconstruction',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license="GPLv3",
    url='https://github.com/ComputationalCryoEM/ASPIRE-Python',
    author='Joakim Anden, Yoel Shkolnisky, Itay Sason, Robbie Brook, Vineet Bansal, Junchao Xia',
    author_email='devs.aspire@gmail.com',

    install_requires=[
        'importlib_resources>=1.0.2',
        'mrcfile',
        'python-box',
        'console_progressbar',
        'pyfftw',
        'click',
        'matplotlib',
        'numpy',
        'pandas>=0.23.4',
        'scipy>=1.3.0',
        'tqdm',
        'scikit-learn',
        'scikit-image'
    ],

    # Note, we probably do not want pycuda in the mainline.
    #  Many users (without CUDA) would not be able to install correctly.
    #  Use PEP-0508 syntax to declare optional requirement here.
    #  Usage:
    #    pip install aspire[gpu]
    #  or
    #    pip install -e .[gpu]
    extra_requires={
        'gpu': ['pycuda'],
        'finufft': ['finufftpy'],
    },

    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    package_data={'aspire': ['config.ini'], 'aspire.data': ['*.*']},

    zip_safe=True,
    test_suite='tests',

    classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ]
)
