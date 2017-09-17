
===========
Retort
===========

Retort is a schema migration tool for
`SQLAlchemy <https://www.sqlalchemy.org>`__, compares DB schema against
table metadata, and updates DB schema according to this.

It depends on the `Alembic
autogenerate <http://alembic.zzzcomputing.com/en/latest/autogenerate.html>`__.

Requirements
------------

Retort works with

- Python 3.3+
- SQLAlchemy
- Alembic
- autopep8

Installation
------------

via pip
#######

.. code:: bash

    $ pip install retort

via setup.py
############

.. code:: bash

    $ python setup.py install

Basic Usage Examples
---------------------

Generate config file (retort\_config.py)

.. code:: bash

    (venv) tpdn@example:~/retort_example$ retort init
    Create retort_conf.py.

Edit config file

.. code:: python

    # retort_config.py
    from model import user

    TARGETS = [
        {
            'engine': user.engine, #sqlalchemy engine
            'metadata': user.Base.metadata #sqlalchemy metadata
        },
    ]

.. code:: python

    # model/user.py
    from sqlalchemy import Column, Integer, String, create_engine
    from sqlalchemy.ext.declarative import declarative_base


    engine = create_engine('mysql+pymysql://foobar:abcdef@localhost/retort_test_db')
    Base = declarative_base()


    class User(Base):
        __tablename__ = 'users'

        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        fullname = Column(String(255))
        xyz = Column(String(255))

Apply

.. code:: bash

    (venv) tpdn@example:~/retort_example$ retort apply
    ====================
    url: mysql+pymysql://foobar:abcdef@localhost/retort_test_db
    logging_name: None
    ====================
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('fullname', sa.String(length=255), nullable=True),
                    sa.Column('xyz', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    Do you really want to apply this? [y/n]: y

    Applying migration......
    ====================
    url: mysql+pymysql://foobar:abcdef@localhost/retort_test_db
    logging_name: None
    ====================
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('fullname', sa.String(length=255), nullable=True),
                    sa.Column('xyz', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    ---> Processing time: 0.0894(sec)
    Complete!

Update model(remove xyz column)

.. code:: python

    # model/user.py
    from sqlalchemy import Column, Integer, String, create_engine
    from sqlalchemy.ext.declarative import declarative_base


    engine = create_engine('mysql+pymysql://foobar:abcdef@localhost/retort_test_db')
    Base = declarative_base()


    class User(Base):
        __tablename__ = 'users'

        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        fullname = Column(String(255))
        # xyz = Column(String(255))

Apply with --sql option

.. code:: bash

    (venv) tpdn@example:~/retort_example$ retort apply --sql
    ====================
    url: mysql+pymysql://foobar:abcdef@localhost/retort_test_db
    logging_name: None
    ====================
    ALTER TABLE users DROP COLUMN xyz;

    Do you really want to apply this? [y/n]: y

    Applying migration......
    ====================
    url: mysql+pymysql://foobar:abcdef@localhost/retort_test_db
    logging_name: None
    ====================
    ALTER TABLE users DROP COLUMN xyz;

    ---> Processing time: 0.0745(sec)
    Complete!

Commands and Options
--------------------

::

    retort init

    retort apply
      --sql # print sql mode
      --dry-run # dry run (no database update)
      --yes # skip confirmation
      --without-drop # without drop operations (DROP TABLE, DROP COLUMN, DROP INDEX, DROP CONSTRAINT)

    retort print_operations
      --sql
      --without-drop

Author
-------

**NAKAMORI Ryosuke** - https://github.com/tpdn

Licence
-------

BSD License (2-Clause)
