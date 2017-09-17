import os
import sys
from distutils.util import strtobool

from .constant import CONFIG_FILE_NAME
from .migration import Migration


def prompt(query):
    sys.stdout.write('%s [y/n]: ' % query)
    val = input()
    try:
        ret = strtobool(val)
    except ValueError:
        print('Please answer with a y/n\n')
        return prompt(query)
    return ret


def get_config():
    sys.path.append(os.getcwd())
    from importlib.machinery import SourceFileLoader
    retort_conf = SourceFileLoader('retort_conf', CONFIG_FILE_NAME).load_module()
    return retort_conf


def get_migrations(without_drop=False):
    config = get_config()
    return [Migration(target['engine'], target['metadata'], without_drop=without_drop) for target in config.TARGETS]


def print_codes(migrations, sql=False):
    for m in migrations:
        print_code(m, sql)


def print_code(migration, sql=False):
    print('====================')
    migration.print_engine_info()
    print('====================')
    migration.print_code(sql)
