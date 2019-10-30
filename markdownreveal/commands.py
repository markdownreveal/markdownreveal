import sys
import shlex
from subprocess import run
from subprocess import check_output
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory
from pathlib import Path
from shutil import copytree
from shutil import make_archive
from shutil import rmtree

import click
from click_default_group import DefaultGroup
from livereload import Server
from watchdog.observers import Observer

from .convert import Handler
from .convert import generate
from .config import load_config


def shell(command):
    """
    Execute a shell command and return the output as a list of lines.
    """
    return check_output(shlex.split(command)).decode('utf').splitlines()


@click.group(cls=DefaultGroup, default='show')
@click.version_option(
    prog_name='Markdownreveal',
    message='%(prog)s %(version)s'
)
def cli():
    pass


@cli.command()
@click.argument('markdown_file')
@click.option('-h', '--host', type=str, default='localhost',
              help='Listen on IP (default: localhost).')
@click.option('-p', '--port', type=int, default=8123,
              help='Listen on port (default: 8123).')
def show(markdown_file: Path, host: str='localhost', port: int=8123):
    """
    Visualize your presentation (default).
    """
    markdown_file = Path(markdown_file)

    observer = Observer()
    handler = Handler(markdown_file)
    # Initial generation
    generate(markdown_file)
    observer.schedule(handler, '.', recursive=True)
    observer.start()

    server = Server()
    config = load_config()
    server.watch(str(config['output_path'] / '.reload'), delay=0)
    server.serve(
        root=str(config['output_path']),
        restart_delay=0,
        debug=False,
        open_url_delay=0.1,
        host=host,
        port=port,
    )


@cli.command()
@click.argument('markdown_file')
@click.option('-r', '--remote', type=str, default='origin',
              help='Choose a specific remote.')
def upload(markdown_file: Path, remote: str='origin'):
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
def pdf(markdown_file: str):
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
    command = 'decktape reveal {presentation} {name}'.format(
        presentation=presentation,
        name=name,
    )
    run(shlex.split(command))


@cli.command()
def clean():
    """
    Clean local Markdownreveal files.
    """
    config = load_config()
    rmtree(str(config['local_path']), ignore_errors=True)
