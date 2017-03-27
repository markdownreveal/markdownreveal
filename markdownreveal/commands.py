from tempfile import TemporaryDirectory
from pathlib import Path
from shutil import make_archive
from shutil import copytree
from shutil import rmtree

import click
from click_default_group import DefaultGroup
from livereload import Server
from watchdog.observers import Observer

from . import Handler
from . import generate
from . import load_config


@click.group(cls=DefaultGroup, default='show', default_if_no_args=True)
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
        root=config['output_path'],
        restart_delay=0,
        debug=True,
        open_url=True,
        open_url_delay=0,
        host='localhost',
        port=8123,
    )


@cli.command()
@click.argument('markdown_file')
def zip(markdown_file: Path):
    """
    Generate a ZIP file with the presentation.
    """
    markdown_file = Path(markdown_file)

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir) / 'out'
        generate(markdown_file)
        config = load_config()
        copytree(src=config['output_path'], dst=tmpdir)
        make_archive(markdown_file.stem, format='zip', root_dir=tmpdir)


@cli.command()
def clean():
    """
    Clean local Markdownreveal files.
    """
    config = load_config()
    rmtree(config['local_path'], ignore_errors=True)
