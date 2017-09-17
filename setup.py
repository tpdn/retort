from os import path

from retort import __version__
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

tests_require = [name.rstrip() for name in open('requirements.txt').readlines()]


setup(
    name='retort',
    version=__version__,
    python_requires='>=3.3',
    description='Retort is a schema migration tool for SQLAlchemy.',
    long_description=long_description,
    license='BSD License (2-Clause)',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Database :: Front-Ends',
    ],
    keywords='SQLAlchemy migrations',
    author='NAKAMORI Ryosuke',
    author_email='me@tpdn.kim',
    url='https://github.com/tpdn/retort',
    packages=['retort'],
    package_dir={'retort': 'retort'},
    package_data={'retort': ['data/retort_conf_example.py.txt']},
    install_requires=[
        'SQLAlchemy', 'alembic', 'autopep8'
    ],
    tests_require=tests_require,
    test_suite='nose.collector',
    entry_points={
        'console_scripts': 'retort = retort.command:command'
    },
)
