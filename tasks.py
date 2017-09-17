from invoke import task
from retort import __version__


@task
def build(ctx):
    ctx.run('python setup.py sdist bdist_wheel')


@task
def upload_pypi(ctx, _all=False, testpypi=False, dry_run=False):
    if _all:
        command = 'twine upload dist/*'
    else:
        command = 'twine upload dist/retort-{}*'.format(__version__)
    if testpypi:
        command = command + ' -r testpypi'

    if dry_run:
        print(command)
    else:
        ctx.run(command)
