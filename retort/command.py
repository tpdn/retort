import os
import shutil
import sys
import time
from argparse import ArgumentParser

from . import cmd_helper, __version__


def main(args):
    pass


def init(args):
    stub_file_path = os.path.join(os.path.dirname(__file__), 'data', 'retort_conf_example.py.txt')
    if os.path.exists('./retort_conf.py'):
        print('retort_conf.py already exists.')
        return
    shutil.copyfile(stub_file_path, 'retort_conf.py')
    print('Create retort_conf.py.')


def apply(args):
    migrations = cmd_helper.get_migrations(args.without_drop)

    if not args.yes:
        cmd_helper.print_codes(migrations, args.sql)
        if not cmd_helper.prompt('Do you really want to apply this?'):
            print('Cancelled.')
            return
    print('')
    print('Applying migration......')
    for m in migrations:
        cmd_helper.print_code(m, args.sql)
        if not args.dry_run:
            t1 = time.time()
            m.apply()
            t2 = time.time()
            print('---> Processing time: ' + str(round((t2 - t1), 4)) + '(sec)')
    print('Complete!')


def print_operations(args):
    migrations = cmd_helper.get_migrations(args.without_drop)
    cmd_helper.print_codes(migrations, args.sql)


def command():
    parser = ArgumentParser(description='Retort v{}: schema migration tool for SQLAlchemy'.format(__version__))
    parser.set_defaults(func=main)
    parser.add_argument('--version', action='version', version=__version__)
    subparsers = parser.add_subparsers()

    subparser_init = subparsers.add_parser('init')
    subparser_init.set_defaults(func=init)

    subparser_apply = subparsers.add_parser('apply')
    subparser_apply.add_argument('--sql', action='store_const', const=True, default=False)
    subparser_apply.add_argument('--dry-run', action='store_const', const=True, default=False)
    subparser_apply.add_argument('--yes', action='store_const', const=True, default=False)
    subparser_apply.add_argument('--without-drop', action='store_const', const=True, default=False)
    subparser_apply.set_defaults(func=apply)

    subparser_print_operations = subparsers.add_parser('print_operations')
    subparser_print_operations.add_argument('--sql', action='store_const', const=True, default=False)
    subparser_print_operations.add_argument('--without-drop', action='store_const', const=True, default=False)
    subparser_print_operations.set_defaults(func=print_operations)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)
