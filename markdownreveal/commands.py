import os
import sys
import shlex
from subprocess import run
from subprocess import check_output
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory
from pathlib import Path
from shutil import copytree
from shutil import make_archive
from shutil import move
from shutil import rmtree
from urllib import request
from urllib.error import URLError

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
@click.version_option()
def cli():
    pass


@cli.command()
@click.argument('markdown_file')
def show(markdown_file: Path):
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
        debug=True,
        open_url=True,
        open_url_delay=0,
        host='localhost',
        port=8123,
    )


@cli.command()
@click.argument('markdown_file')
def upload(markdown_file: Path):
    """
    Upload your presentation.
    """
    markdown_file = Path(markdown_file)

    try:
        shell('git status')
    except CalledProcessError as error:
        return
    origin = shell('git config remote.origin.url')[0]
    if 'github' not in origin:
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
        shell('git %s push -f -u origin gh-pages' % worktree)
        shell('git %s checkout %s' % (worktree, current))

    repo = Path(origin.split(':')[-1])
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
@click.argument('url')
def pdf(url: str):
    """
    Generate a PDF file with the presentation.
    """
    try:
        code = request.urlopen(url).getcode()
    except URLError:
        raise ValueError('Invalid URL provided!')

    if code != 200:
        raise ValueError('Unexpected server response!')

    with TemporaryDirectory() as tmpdir:
        name = 'slides.pdf'
        tmpdir = Path(tmpdir)
        command = 'docker run --user={uid}:{gid} --rm --net="host" ' + \
                  '-v {tmp}:{tmp}:Z -w {tmp} astefanutti/decktape ' + \
                  '{url} {name}'
        command = command.format(
            uid=os.getuid(),
            gid=os.getgid(),
            tmp=tmpdir,
            url=url,
            name=name,
        )
        run(shlex.split(command))
        move(str(tmpdir/name), str(Path.cwd()))


@cli.command()
def clean():
    """
    Clean local Markdownreveal files.
    """
    config = load_config()
    rmtree(str(config['local_path']), ignore_errors=True)
