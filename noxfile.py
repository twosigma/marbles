from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import os
from pathlib import Path
import shutil
import sys

import nox

if os.environ.get('GITHUB_ACTIONS', False):
    nox.options.error_on_missing_interpreters = True
    nox.options.error_on_external_run = True
else:
    # local development defaults
    nox.options.sessions = ['test', 'flake8']
    nox.options.reuse_existing_virtualenvs = True

SUPPORTED_PYTHONS = ('3.8', '3.9', '3.10')
MIN_SUPPORTED_PYTHON = '3.8'


def sync_session(*envs, install_marbles=False, **kwargs):
    '''Nox session decorator that uses pip-sync to manage dependencies.'''
    def decorator(f):
        @nox.session(**kwargs)
        @wraps(f)
        def wrapper(session: nox.Session, *args, **kwargs):
            session.install('pip-tools')
            concrete_reqs = [f'requirements/{env}.txt' for env in envs]
            if install_marbles and sys.platform == 'win32':
                concrete_reqs.append('requirements/windows.txt')
            session.run_always('pip-sync', *concrete_reqs)

            if install_marbles:
                session.install('-e', 'marbles/core', '-e', 'marbles/mixins')
            return f(session, *args, **kwargs)

        return wrapper
    return decorator


@sync_session('base', python=SUPPORTED_PYTHONS, install_marbles=True)
def test(session: nox.Session):
    '''Run tests, without coverage.'''
    for subpackage in ('marbles/core', 'marbles/mixins'):
        with session.chdir(subpackage):
            session.run('python', '-m', 'unittest', 'discover', 'tests')


@sync_session('coverage', python=SUPPORTED_PYTHONS, install_marbles=True,
              tags=['actions-test'])
def coverage(session: nox.Session):
    '''Run tests, with coverage.'''
    session.run('coverage', 'erase')

    with session.chdir('marbles/core'):
        session.run('coverage', 'run', '-m', 'unittest', 'discover', 'tests')
    examples_dir = Path('marbles/core/example_packages')
    for f in examples_dir.glob('**/*.coverage*'):
        shutil.move(str(f), 'marbles/core')

    with session.chdir('marbles/mixins'):
        session.run('coverage', 'run', '-m', 'unittest', 'discover', 'tests')

    session.run('coverage', 'combine', 'marbles/core',
                'marbles/mixins/.coverage', '.')
    session.run('coverage', 'report')
    session.run('coverage', 'html')
    session.run('coverage', 'xml')


@sync_session('lint', tags=['actions-check'])
def flake8(session: nox.Session):
    '''Lint with flake8.'''
    session.run('flake8')


@sync_session('docs', install_marbles=True, tags=['actions-check'])
def docs(session: nox.Session):
    '''Build docs with Sphinx.'''
    session.run('sphinx-build', '-b', 'html', '-Ea',
                '-d', 'build/sphinx/doctrees',
                'docs', 'build/sphinx/html')


@sync_session('package', tags=['actions-check'])
def package(session: nox.Session):
    '''Build source and wheel distributions.'''
    for d in ('dist', 'marbles/core/dist', 'marbles/mixins/dist'):
        shutil.rmtree(d, ignore_errors=True)
    for d in ('.', 'marbles/core', 'marbles/mixins'):
        session.run('python', '-m', 'build', d)


@nox.session
def upload(session: nox.Session):
    '''Upload distributions to PyPI'''
    session.install('twine')
    session.run(
        'twine', 'upload',
        'dist/*', 'marbles/core/dist/*', 'marbles/mixins/dist/*',
    )


@nox.session(python=MIN_SUPPORTED_PYTHON)
def pip_compile(session: nox.Session):
    '''Refresh concrete dependencies using pip-compile.

    You can upgrade our pinned dependencies by running ``nox -s pip_compile --
    -U``.
    '''
    session.install('pip-tools')
    args = ['--generate-hashes']

    for subpackage in ('marbles/core', 'marbles/mixins'):
        with session.chdir(subpackage):
            session.run('pip-compile', *args, *session.posargs)

    reqs_dir = Path('requirements')
    infiles = [
        req for req in reqs_dir.glob('*.in')
        if req.stem != 'windows' or sys.platform == 'win32'
    ]
    with ThreadPoolExecutor() as executor:
        executor.map(
            lambda infile: session.run(
                'pip-compile', *args, *session.posargs, str(infile)
            ),
            infiles
        )

    # Remove after https://github.com/jazzband/pip-tools/pull/1650
    for f in reqs_dir.glob('*.txt'):
        content = f.read_text()
        content = content.replace(f'{Path.cwd()}/', '')
        f.write_text(content)


@nox.session
def bumpversion(session: nox.Session):
    '''Update the version number: pass "major", "minor", or "patch".

    Use with positional arguments, e.g. ``nox -s bumpversion -- minor``.
    '''
    session.install('bump2version')
    session.run('bumpversion', *session.posargs)
