from alembic.operations.ops import DropColumnOp, DropConstraintOp, DropIndexOp, DropTableOp

CONFIG_FILE_NAME = 'retort_conf.py'
DROP_OPERATIONS = (DropTableOp, DropColumnOp, DropIndexOp, DropConstraintOp)
DEFAULT_OPTS = {'compare_type': True, 'compare_server_default': True}
