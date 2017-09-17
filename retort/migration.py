import importlib
import re

import autopep8
import sqlalchemy
from alembic.autogenerate.api import AutogenContext, produce_migrations, render
from alembic.operations import Operations
from alembic.runtime.environment import MigrationContext

from .constant import DEFAULT_OPTS, DROP_OPERATIONS
from .error import MigrationError


class Migration:
    def __init__(self, engine, metadata, without_drop=False, opts=None):
        self.engine = engine
        self.metadata = metadata
        self._without_drop = without_drop
        self._opts = DEFAULT_OPTS.copy()
        if opts:
            self._opts.update(opts)
        self._is_applied = False
        self._migration_ops = None
        self._autogen_context = None

    @property
    def is_applied(self):
        return self._is_applied

    def get_migration_context(self, as_sql=False):
        opts = self._opts.copy()
        opts['as_sql'] = as_sql
        return MigrationContext.configure(self.engine.connect(), opts=opts)

    @property
    def migration_ops(self):
        if not self._migration_ops:
            migration_context = self.get_migration_context()
            self._migration_ops = produce_migrations(migration_context, self.metadata).upgrade_ops
            if self._without_drop:
                self._remove_drop_ops(self._migration_ops)
        return self._migration_ops

    def _remove_drop_ops(self, migration_ops):
        if hasattr(migration_ops, 'ops'):
            migration_ops.ops = [x for x in migration_ops.ops if not isinstance(x, DROP_OPERATIONS)]
            for ops in migration_ops.ops:
                self._remove_drop_ops(ops)

    @property
    def autogen_context(self):
        if not self._autogen_context:
            opts = {
                'sqlalchemy_module_prefix': 'sa.',
                'alembic_module_prefix': 'op.',
                'render_item': None,
                'render_as_batch': False,
            }
            self._autogen_context = AutogenContext(self.get_migration_context(), opts=opts)
        return self._autogen_context

    def get_code(self):
        python_code = render._render_cmd_body(self.migration_ops, self.autogen_context)
        code_without_comment_and_indent = '\n'.join(
            [x for x in python_code.split('\n') if not x.startswith('#')])
        return autopep8.fix_code(code_without_comment_and_indent)

    def get_globals(self, op):
        dialect = self.autogen_context.dialect
        _globals = {
            'op': op,
            'sa': sqlalchemy,
        }
        matching_result = re.match(r'sqlalchemy\.dialects\.(\w+)', type(dialect).__module__)
        if matching_result:
            modname = matching_result.group(0)
            _globals.update({type(dialect).name: importlib.import_module(modname)})
        return _globals

    def apply(self):
        if self.is_applied:
            raise MigrationError
        with Operations.context(self.get_migration_context()) as op:
            python_code = self.get_code()
            exec(python_code, self.get_globals(op))
        self._is_applied = True

    def print_engine_info(self):
        print('\n'.join([
            'url: ' + str(self.engine.url),
            'logging_name: ' + str(self.engine.logging_name),
        ]))

    def print_code(self, sql=False):
        if sql:
            with Operations.context(self.get_migration_context(as_sql=True)) as op:
                python_code = self.get_code()
                exec(python_code, self.get_globals(op))
        else:
            print(self.get_code())
