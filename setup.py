#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import distutils
import subprocess
from os.path import dirname, join

from setuptools import setup, find_packages


def read(*args):
    return open(join(dirname(__file__), *args)).read()


class ToxTestCommand(distutils.cmd.Command):
    """Distutils command to run tests via tox with 'python setup.py test'.

    Please note that in this package configuration tox uses the dependencies in
    ``requirements/dev.txt``, the list of dependencies in ``tests_require`` in
    ``setup.py`` is ignored!

    See https://docs.python.org/3/distutils/apiref.html#creating-a-new-distutils-command
    for more documentation on custom distutils commands.
    """
    description = "Run tests via 'tox'."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce("Running tests with 'tox'...", level=distutils.log.INFO)
        return subprocess.call(['tox'])


__version__="<unknown>"
exec(read('django_cms_tools', 'version.py'))


classifiers = """
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License v3.0 or above
Operating System :: OS Independent
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Framework :: Django
Topic :: Internet
"""

install_requires = [
    # 'six',
]


setup(
    name='django cms tools',
    version=__version__,
    description='Tools/helpers around Django-CMS',
    long_description=read('README.creole'),
    author='Jens Diemer',
    author_email='django-cms-tools@jensdiemer.de',
    url='https://github.com/jedie/django-cms-tools',
    license="GNU General Public License v3.0 or above",
    classifiers=[c.strip() for c in classifiers.splitlines()
                 if c.strip() and not c.startswith('#')],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requires,
    cmdclass={
        'test': ToxTestCommand,
    }
)
