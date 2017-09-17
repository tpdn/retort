from alembic.operations.ops import CreateTableOp, DropTableOp, UpgradeOps
from alembic.runtime.environment import MigrationContext
from nose.tools import *
from retort.migration import DROP_OPERATIONS, Migration
from sqlalchemy import Column, Integer, MetaData, String
from sqlalchemy.ext.declarative import declarative_base

from .target_databases import Target
from .util import captured_output


def setup():
    Target.drop_and_create_database()


class TestGetMigrationContext:
    @classmethod
    def metadata(cls):
        Base = declarative_base()
        return Base.metadata

    def test(self):
        engine = Target.get_engine()
        migration = Migration(engine, self.metadata)
        context = migration.get_migration_context()
        assert_is_instance(context, MigrationContext)

    def test_as_sql(self):
        engine = Target.get_engine()
        migration = Migration(engine, self.metadata)
        context = migration.get_migration_context(as_sql=True)
        assert_is_instance(context, MigrationContext)
        assert_true(context.as_sql)


class TestMigrationOps:
    def create_table(self):
        Base = declarative_base()
        engine = Target.get_engine()

        class ExistingFooBar(Base):
            __tablename__ = 'foobar'
            id = Column(Integer, primary_key=True)
            name = Column(String(10))
            foo = Column(String(10))
            xxx = Column(String(10))
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def setup(self):
        Target.drop_all_table()
        self.Base = declarative_base()
        self.engine = Target.get_engine()

        class FooBar(self.Base):
            __tablename__ = 'foobar'
            id = Column(Integer, primary_key=True)
            name = Column(String(10))
            yyy = Column(String(10))

    def is_included_operations(self, migration_ops, expected_operations):
        if not hasattr(migration_ops, 'ops') or len(migration_ops.ops) is 0:
            return isinstance(migration_ops, expected_operations)
        return any(self.is_included_operations(ops, expected_operations) for ops in migration_ops.ops)

    def is_included_drop_operations(self, migration_ops):
        return self.is_included_operations(migration_ops, DROP_OPERATIONS)

    def test_create_table(self):
        migration = Migration(self.engine, self.Base.metadata)
        migration_ops = migration.migration_ops
        assert_is_instance(migration_ops, UpgradeOps)
        ok_(len(migration_ops.ops) == 1)
        assert_is_instance(migration_ops.ops[0], CreateTableOp)

    def test_drop_table(self):
        self.create_table()
        base_without_table = declarative_base()
        migration = Migration(self.engine, base_without_table.metadata)
        migration_ops = migration.migration_ops
        assert_is_instance(migration_ops, UpgradeOps)
        ok_(len(migration_ops.ops) == 1)
        assert_is_instance(migration_ops.ops[0], DropTableOp)

    def test_alter_table(self):
        self.create_table()
        migration = Migration(self.engine, self.Base.metadata)
        migration_ops = migration.migration_ops
        assert_is_instance(migration_ops, UpgradeOps)
        ok_(self.is_included_drop_operations(migration_ops))

    def test_alter_without_drop_operation(self):
        self.create_table()
        migration = Migration(self.engine, self.Base.metadata, without_drop=True)
        migration_ops = migration.migration_ops
        assert_is_instance(migration_ops, UpgradeOps)
        ok_(not self.is_included_drop_operations(migration_ops))


class TestApply:
    def create_table(self):
        Base = declarative_base()
        engine = Target.get_engine()

        class ExistingFooBar(Base):
            __tablename__ = 'foobar'
            id = Column(Integer, primary_key=True)
            name = Column(String(10))
            foo = Column(String(10))
            xxx = Column(String(10))
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def setup(self):
        Target.drop_all_table()
        self.create_table()
        self.Base = declarative_base()
        self.engine = Target.get_engine()

        class FooBar(self.Base):
            __tablename__ = 'foobar'
            id = Column(Integer, primary_key=True)
            name = Column(String(10))
            yyy = Column(String(10))

    def teardown(self):
        Target.drop_all_table()

    def test(self):
        migration = Migration(self.engine, self.Base.metadata)
        migration.apply()
        meta = MetaData()
        meta.reflect(bind=self.engine)
        foobar_table = meta.tables['foobar']
        assert_is_instance(foobar_table.columns['id'].type, Integer)
        assert_is_instance(foobar_table.columns['name'].type, String)
        assert_is_instance(foobar_table.columns['yyy'].type, String)
        assert_raises(KeyError, lambda: foobar_table.columns['foo'])
        assert_raises(KeyError, lambda: foobar_table.columns['xxx'])


class TestPrintEngineInfo:
    @classmethod
    def metadata(cls):
        Base = declarative_base()
        return Base.metadata

    def test(self):
        engine = Target.get_engine()
        migration = Migration(engine, self.metadata)
        with captured_output() as (out, _err):
            migration.print_engine_info()
        outputs = out.getvalue().split('\n')
        eq_(len(outputs), 3)
        eq_(outputs[0], 'url: {}'.format(engine.url))
        eq_(outputs[1], 'logging_name: None')
        eq_(outputs[2], '')

    def test_with_logging_name(self):
        logging_name = 'testing'
        engine = Target.get_engine(logging_name=logging_name)
        migration = Migration(engine, self.metadata)
        with captured_output() as (out, _err):
            migration.print_engine_info()
        outputs = out.getvalue().split('\n')
        eq_(len(outputs), 3)
        eq_(outputs[0], 'url: {}'.format(engine.url))
        eq_(outputs[1], 'logging_name: testing')
        eq_(outputs[2], '')
