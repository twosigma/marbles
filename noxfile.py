from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import os
from pathlib import Path
import shutil
import sys

import nox

if os.environ.get('GITHUB_ACTIONS', False):
    nox.options.pythons = [os.environ['PYTHON']]

    platform = os.environ['PLATFORM']
    if platform.startswith('windows'):
        nox.options.keywords = 'win32'
    elif platform.startswith('macos'):
        nox.options.keywords = 'darwin'
    elif platform.startswith('ubuntu'):
        nox.options.keywords = 'linux'
    else:
        raise RuntimeError(f'Unknown platform: {platform}')

    nox.options.error_on_missing_interpreters = True
    nox.options.error_on_external_run = True
else:
    # local development defaults
    nox.options.sessions = ['test', 'flake8']
    nox.options.reuse_existing_virtualenvs = True

SUPPORTED_PYTHONS = ('3.8', '3.9', '3.10')
MIN_SUPPORTED_PYTHON = '3.8'
SUPPORTED_PLATFORMS = ('win32', 'darwin', 'linux')


def sync_session(
    *envs, python=SUPPORTED_PYTHONS, platforms=SUPPORTED_PLATFORMS, **kwargs
):
    kwargs.setdefault('python', python)

    def decorator(f):
        @nox.session(**kwargs)
        @nox.parametrize('platform', platforms)
        @wraps(f)
        def wrapper(session: nox.Session, *args, platform, **kwargs):
            if platform != sys.platform:
                session.skip(f'not running on {platform}')

            session.install('pip-tools')
            reqs_dir = Path('requirements')
            concrete_reqs = [str(reqs_dir / f'{env}.txt') for env in envs]
            if platform == 'win32':
                concrete_reqs.append(str(reqs_dir / 'windows.txt'))

            session.run_always('pip-sync', *concrete_reqs)
            return f(session, *args, **kwargs)
        return wrapper
    return decorator


@nox.session(python=MIN_SUPPORTED_PYTHON)
def pip_compile(session: nox.Session):
    session.install('pip-tools')
    args = ['--no-emit-index-url', '--generate-hashes']

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
        content = content.replace(f"{Path.cwd()}/", "")
        f.write_text(content)


@sync_session('base')
def test(session: nox.Session):
    session.install('-e', 'marbles/core', '-e', 'marbles/mixins')
    for subpackage in ('marbles/core', 'marbles/mixins'):
        with session.chdir(subpackage):
            session.run('python', '-m', 'unittest', 'discover', 'tests')


@sync_session('coverage', tags=['actions-test'])
def coverage(session: nox.Session):
    session.install('-e', 'marbles/core', '-e', 'marbles/mixins')
    session.run('coverage', 'erase')

    with session.chdir('marbles/core'):
        session.run('coverage', 'run', '-m', 'unittest', 'discover', 'tests')
    examples_dir = Path('marbles/core/example_packages')
    for f in examples_dir.glob("**/*.coverage*"):
        shutil.move(str(f), 'marbles/core')

    with session.chdir('marbles/mixins'):
        session.run('coverage', 'run', '-m', 'unittest', 'discover', 'tests')

    session.run('coverage', 'combine', 'marbles/core',
                'marbles/mixins/.coverage', '.')
    session.run('coverage', 'report')
    session.run('coverage', 'html')
    session.run('coverage', 'xml')


@sync_session('lint', python=MIN_SUPPORTED_PYTHON, tags=['actions-check'])
def flake8(session: nox.Session):
    session.run('flake8')


@sync_session('docs', python=MIN_SUPPORTED_PYTHON, tags=['actions-check'])
def docs(session: nox.Session):
    session.install('-e', 'marbles/core', '-e', 'marbles/mixins')
    session.run('sphinx-build', '-b', 'html', '-Ea',
                '-d', 'build/sphinx/doctrees',
                'docs', 'build/sphinx/html')


@sync_session('package', python=MIN_SUPPORTED_PYTHON, tags=['actions-check'])
def package(session: nox.Session):
    for d in ('dist', 'marbles/core/dist', 'marbles/mixins/dist'):
        shutil.rmtree(d, ignore_errors=True)
    for d in ('.', 'marbles/core', 'marbles/mixins'):
        session.run('python', '-m', 'build', d)


@sync_session('package', python=MIN_SUPPORTED_PYTHON)
def upload(session: nox.Session):
    session.run(
        'twine', 'upload',
        '--repository', 'testpypi',
        'dist/*', 'marbles/core/dist/*', 'marbles/mixins/dist/*',
    )
