import shlex
import sys
import threading
import webbrowser
from pathlib import Path
from shutil import copytree
from shutil import make_archive
from shutil import rmtree
from subprocess import CalledProcessError
from subprocess import check_output
from subprocess import run
from tempfile import TemporaryDirectory

import click
from click_default_group import DefaultGroup
from livereload import Server
from tornado.autoreload import add_reload_hook
from tornado.ioloop import IOLoop
from watchdog.observers import Observer

from .config import load_config
from .convert import Handler
from .convert import generate


def shell(command):
    """
    Execute a shell command and return the output as a list of lines.
    """
    return check_output(shlex.split(command)).decode('utf').splitlines()


@click.group(cls=DefaultGroup, default='show')
@click.version_option(
    prog_name='Markdownreveal', message='%(prog)s %(version)s'
)
def cli():
    pass


@cli.command()
@click.argument('markdown_file')
@click.option(
    '-h',
    '--host',
    type=str,
    default='localhost',
    help='Listen on IP (default: localhost).',
)
@click.option(
    '-p',
    '--port',
    type=int,
    default=8123,
    help='Listen on port (default: 8123).',
)
@click.option(
    '-n',
    '--no-warmup',
    is_flag=True,
    help='Do not display the warmup slide, even if it exists in the'
    ' style folder (default: false).',
)
def show(
    markdown_file: Path,
    host: str = 'localhost',
    port: int = 8123,
    no_warmup: bool = False,
):
    """
    Visualize your presentation (default).
    """
    markdown_file = Path(markdown_file)
    config = load_config()

    # Initial generation
    generate(markdown_file, no_warmup=no_warmup)

    observer = Observer()
    url = 'http://{host}:{port}'.format(host=host, port=port)
    reload_url = url + '/forcereload'
    ignore_regexes = [r'.*/\.[^/]*']
    handler = Handler(
        regexes=['.*'], ignore_regexes=ignore_regexes, ignore_directories=True
    )
    handler.configure(markdown_file, reload_url)
    observer.schedule(handler, '.', recursive=True)
    observer.start()

    server = Server()
    server.root = str(config['output_path'])
    server.application(port, host, liveport=None, debug=True, live_css=True)
    threading.Thread(target=webbrowser.open, args=(url,)).start()
    add_reload_hook(lambda: IOLoop.instance().close(all_fds=True))
    IOLoop.instance().start()


@cli.command()
@click.argument('markdown_file')
@click.option(
    '-r',
    '--remote',
    type=str,
    default='origin',
    help='Choose a specific remote.',
)
def upload(markdown_file: Path, remote: str = 'origin'):
    """
    Upload your presentation.
    """
    markdown_file = Path(markdown_file)

    try:
        shell('git status')
        remote_url = shell('git remote get-url --push ' + remote)[0]
    except CalledProcessError:
        return

    if 'github' not in remote_url:
        error = 'Uploading only supported for GitHub repositories!'
        sys.stderr.write(error + '\n')
        return

    # We copy the directory because `git` does not follow symlinks...
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir) / 'out'
        generate(markdown_file)
        config = load_config()
        copytree(src=str(config['output_path']), dst=str(tmpdir))
        (tmpdir / '.nojekyll').touch()

        worktree = '--work-tree=%s' % tmpdir
        current = shell('git rev-parse --abbrev-ref HEAD')[0]
        shell('git checkout -B gh-pages')
        shell('git %s add .' % worktree)
        shell('git %s commit -m "Markdownreveal live presentation"' % worktree)
        shell('git %s push -f -u %s gh-pages' % (worktree, remote))
        shell('git %s checkout %s' % (worktree, current))

    repo = Path(remote_url.split(':')[-1])
    url = 'https://%s.github.io/%s/' % (repo.parent, repo.stem)
    sys.stdout.write('Presentation uploaded to:\n\n' + url + '\n\n')


@cli.command()
@click.argument('markdown_file')
def zip(markdown_file: Path):
    """
    Generate a ZIP file with the presentation.
    """
    markdown_file = Path(markdown_file)

    # We copy the directory because `make_archive` cannot follow symlinks...
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir) / 'out'
        generate(markdown_file)
        config = load_config()
        copytree(src=str(config['output_path']), dst=str(tmpdir))
        make_archive(markdown_file.stem, format='zip', root_dir=str(tmpdir))


@cli.command()
@click.argument('markdown_file')
@click.option(
    '-s',
    '--size',
    type=str,
    default='1920x1080',
    help='Page size (resolution); use 2048x1536 for 4:3.',
)
def pdf(markdown_file: str, size: str = '1920x1080'):
    """
    Generate a PDF file with the presentation.
    """
    if markdown_file.startswith('http'):
        presentation = markdown_file
    else:
        markdown_file = Path(markdown_file)
        generate(markdown_file)
        config = load_config()
        presentation = config['output_path'] / 'index.html'

    name = 'slides.pdf'
    command = 'decktape reveal --size={size} {presentation} {name}'.format(
        size=size, presentation=presentation, name=name
    )
    run(shlex.split(command))


@cli.command()
def clean():
    """
    Clean local Markdownreveal files.
    """
    config = load_config()
    rmtree(str(config['local_path']), ignore_errors=True)
