import os
from abc import ABCMeta, abstractmethod

from sqlalchemy import MetaData, create_engine

USER = os.environ.get('DB_USER', 'retort_test_user')
PASSWORD = os.environ.get('DB_PASSWORD', 'retort_test_user')
HOST = os.environ.get('DB_HOST', 'localhost')
NAME = os.environ.get('DB_NAME', 'retort_test_db')


class AbstractDatabase(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def drop_and_create_database(cls):
        pass

    @classmethod
    @abstractmethod
    def get_engine(cls, logging_name=None):
        pass

    @classmethod
    def drop_all_table(cls):
        meta = MetaData()
        engine = cls.get_engine()
        meta.reflect(bind=engine)
        meta.drop_all(engine)
        engine.dispose()

    @classmethod
    def get_url(cls, without_dbname=False):
        if without_dbname:
            return '{}+{}://{}:{}@{}'.format(cls.DIALECT, cls.DRIVER, USER, PASSWORD, HOST)
        else:
            return '{}+{}://{}:{}@{}/{}'.format(cls.DIALECT, cls.DRIVER, USER, PASSWORD, HOST, NAME)


class MySQL(AbstractDatabase):
    DIALECT = 'mysql'
    DRIVER = 'pymysql'

    @classmethod
    def drop_and_create_database(cls):
        engine = create_engine(cls.get_url(without_dbname=True))
        drop_str = 'DROP DATABASE IF EXISTS {};'.format(NAME)
        create_str = 'CREATE DATABASE {};'.format(NAME)
        engine.execute(drop_str)
        engine.execute(create_str)
        engine.dispose()

    @classmethod
    def get_engine(cls, logging_name=None):
        return create_engine(cls.get_url(), logging_name=logging_name)


class PostgreSQL(AbstractDatabase):
    DIALECT = 'postgresql'
    DRIVER = 'psycopg2'

    @classmethod
    def drop_and_create_database(cls):
        engine = create_engine(cls.get_url(without_dbname=True), isolation_level='AUTOCOMMIT')
        drop_str = 'DROP DATABASE IF EXISTS {};'.format(NAME)
        create_str = 'CREATE DATABASE {};'.format(NAME)
        engine.execute(drop_str)
        engine.execute(create_str)
        engine.dispose()

    @classmethod
    def get_engine(cls, logging_name=None):
        return create_engine(cls.get_url(), logging_name=logging_name, isolation_level='AUTOCOMMIT')


_target_dialect = os.environ.get('TARGET_DIALECT', 'mysql')

if _target_dialect == 'mysql':
    Target = MySQL
elif _target_dialect == 'postgresql':
    Target = PostgreSQL
else:
    Target = None
