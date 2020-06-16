#!/usr/bin/env python
from setuptools import find_packages, setup
import versioneer

README = open('README.md', 'r').read()


setup(
    name='markdown-language-server',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    description='Markdown Language Server for the Language Server Protocol',

    long_description=README,

    # The project's main homepage.
    url='https://github.com/ompugao/markdown-language-server',

    author='Shohei Fujii',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'test', 'test.*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'configparser; python_version<"3.0"',
        'future>=0.14.0; python_version<"3"',
        'backports.functools_lru_cache; python_version<"3.2"',
        'python-jsonrpc-server>=0.3.2',
        'pluggy',
        'ujson<=1.35; platform_system!="Windows"'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[test]
    extras_require={
        'all': [
        ],
        'test': ['versioneer', 'ipython', 'pylint', 'pytest', 'mock', 'pytest-cov',
                 'coverage', 'numpy', 'pandas', 'matplotlib',
                 'pyqt5;python_version>="3"'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'mdls = mdls.__main__:main',
        ],
        'mdls': [
            'hogehoge = mdls.plugins.hogehoge'
        ]
    },
)
