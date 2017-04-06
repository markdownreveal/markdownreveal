import os
import re
import tarfile
import collections
from hashlib import sha1
from pathlib import Path
from subprocess import check_output
from urllib.request import urlretrieve
from threading import Timer
from pkg_resources import resource_filename
from typing import Any
from typing import List
from typing import Dict

import yaml
import requests
from pypandoc import convert_file
from watchdog.events import FileSystemEventHandler
from watchdog.observers.inotify_buffer import InotifyBuffer

from .tweak import tweak_html


__version__ = '0.1.1'

Config = Dict[Any, Any]
TarMembers = List[tarfile.TarInfo]


def update_config(template: Config, config: Config) -> Config:
    """
    Update a dictionary with key-value pairs found in another one.

    It is a recursive update.

    Parameters
    ----------
    template
        Initial dictionary to update.
    config
        New dictionary to update the original with.

    Returns
    -------
        The resulting (updated) dictionary.
    """
    if not config:
        return template
    for key, value in config.items():
        if isinstance(value, collections.Mapping):
            recurse = update_config(template.get(key, {}), value)
            template[key] = recurse
        else:
            template[key] = config[key]
    return template


def complete_config(config: Config) -> Config:
    """
    Complete configuration with complete paths and parameters.

    Parameters
    ----------
    config
        Input configuration.

    Returns
    -------
        The completed configuration.
    """
    # Allow changing home path through environment variable (for testing)
    home = Path(os.environ.get('MARKDOWNREVEAL_HOME', str(Path.home())))
    config['local_path'] = home / config['local_path']
    config['output_path'] = config['local_path'] / 'out'
    config['reveal_extra']['theme'] = config['theme']
    return config


def load_config() -> Config:
    """
    Load configuration file template.

    Returns
    -------
        The configuration file template.
    """
    # Default Markdownreveal configuration
    config_template = resource_filename(__name__, 'config.template.yaml')
    config = yaml.load(open(config_template))

    # Local configuration (load first for style path)
    local_config = {}
    config_file = Path('config.yaml')
    if config_file.exists():
        local_config = yaml.load(config_file.read_text())
        update_config(config, local_config)
    complete_config(config)

    # Style configuration
    style_config = {}
    config_file = config['output_path'] / 'markdownrevealstyle' / 'config.yaml'
    if config_file.exists():
        style_config = yaml.load(config_file.read_text())
        update_config(config, style_config)
    complete_config(config)

    # Local configuration (override style configuration)
    update_config(config, local_config)
    complete_config(config)

    return config


def latest_project_release(github: str) -> str:
    """
    Fetch the latest project release tag.

    Parameters
    ----------
    github
        The name of the GitHub project.

    Notes
    -----
    For now, only GitHub projects are supported.
    """
    releases = 'https://api.github.com/repos/%s/releases' % github
    response = requests.get(releases)
    # Try with GitHub API first
    if response.status_code == 200:
        return response.json()[0]['tag_name']
    # Try to parse latest release manually...
    response = requests.get('https://github.com/%s/releases' % github)
    return re.findall('/%s/releases/tag/([^"]*)' % github,
                      response.text, flags=re.IGNORECASE)[0]


def clean_tar_members(members: TarMembers) -> TarMembers:
    """
    Strip .tar components (i.e.: remove top-level directory) from members.

    Parameters
    ----------
    members
        A list of .tar members.

    Returns
    -------
        A clean .tar member list with the stripped components.
    """
    clean = []
    for member in members:
        path = Path(member.name)
        if path.is_absolute():
            continue
        parts = path.parts[1:]
        if not parts:
            continue
        if parts[0] == 'test':
            continue
        member.name = str(Path(*parts))
        clean.append(member)
    return clean


def initialize_localdir(config: Config) -> Path:
    """
    Initialize local directory with the required reveal.js files.

    Parameters
    ----------
    config
        Markdownreveal configuration.

    Returns
    -------
        Path where output files will be generated, with a symbolic link to
        the corresponding reveal.js downloaded files.
    """
    localdir = config['local_path']

    # Initialize local directory
    outdir = localdir / 'out'
    outdir.mkdir(parents=True, exist_ok=True)

    # reveal.js
    initialize_localdir_project(
        github='hakimel/reveal.js',
        outdir=outdir,
        localdir=localdir,
        project_version=config['reveal_version'],
        name='revealjs',
        download_url='https://github.com/{project}/archive/{version}.tar.gz'
    )

    # KaTeX
    initialize_localdir_project(
        github='Khan/KaTeX',
        outdir=outdir,
        localdir=localdir,
        project_version=config['katex_version'],
        name='katex',
        download_url='https://github.com/{project}/' +
                     'releases/download/{version}/katex.tar.gz'
    )

    # Style
    initialize_localdir_style(outdir, localdir, config['style'])

    return outdir


def initialize_localdir_project(github: str, outdir: Path, localdir: Path,
                                project_version: str, name: str,
                                download_url: str) -> Path:
    """
    Initialize local directory with the specified project.

    Parameters
    ----------
    github
        The name of the GitHub project.
    outdir
        Path where output files will be generated, with a symbolic link to
        the corresponding project downloaded files.
    localdir
        Path to store local files.
    project_version
        String with the project version to use (i.e.: `3.0.1`). The value
        `latest` is also allowed.
    name
        A name for the local downloaded project.
    download_url
        URL to download the project from. In example:
        `'https://github.com/{project}/archive/{version}.tar.gz'`

    Notes
    -----
    For now, only GitHub projects are supported.
    """
    # Download project
    project_path = localdir / name / project_version
    if not project_path.exists():
        if project_version == 'latest':
            project_version = latest_project_release(github=github)
        download_url = download_url.format(project=github,
                                           version=project_version)
        reveal_tar, headers = urlretrieve(download_url)
        with tarfile.open(reveal_tar) as tar:
            members = clean_tar_members(tar.getmembers())
            tar.extractall(str(project_path), members)
        os.remove(reveal_tar)
    symlink = outdir / name
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(project_path, target_is_directory=True)


def initialize_localdir_style(outdir: Path, localdir: Path,
                              style_url: str) -> Path:
    """
    Initialize local directory with the required style files.

    Parameters
    ----------
    outdir
        Path where output files will be generated, with a symbolic link to
        the corresponding reveal.js downloaded files.
    localdir
        Path to store local files.
    style_url
        String with the URL to download the style from.
    """
    # Style
    symlink = outdir / 'markdownrevealstyle'
    if symlink.exists():
        symlink.unlink()
    if not style_url:
        return outdir
    style_version = sha1(style_url.encode('utf')).hexdigest()
    style_path = localdir / style_version
    if not style_path.exists():
        style_tar, headers = urlretrieve(style_url)
        with tarfile.open(style_tar) as tar:
            members = clean_tar_members(tar.getmembers())
            tar.extractall(str(style_path), members)
        os.remove(style_tar)
    symlink.symlink_to(style_path, target_is_directory=True)


def markdown_to_reveal(input_file: Path, reveal_extra: Config,
                       katex: bool) -> str:
    """
    Transform a Markdown input file to an HTML (reveal.js) output string.

    Parameters
    ----------
    input_file
        Input file path, containing the Markdown code.
    reveal_extra
        Extra configuration parameters for reveal.js.
    katex
        Whether to use KaTeX for math rendering.

    Returns
    -------
        The converted string.
    """
    extra_args = [
        '-s',
        '--slide-level=2',
        '-V', 'revealjs-url=revealjs',
    ]
    if katex:
        extra_args.extend([
            '--katex=katex/katex.min.js',
            '--katex-stylesheet=katex/katex.min.css',
        ])
    for key, value in reveal_extra.items():
        extra_args.extend(['-V', '%s=%s' % (key, value)])
    output = convert_file(
        source_file=str(input_file),
        format='md',
        to='revealjs',
        extra_args=extra_args,
    )
    return output


def generate(markdown_file):
    """
    TODO
    """
    # Reload config
    config = load_config()

    # Initialize localdir
    initialize_localdir(config)

    # rsync
    command = [
        'rsync',
        '--delete',
        '--exclude', 'katex',
        '--exclude', 'revealjs',
        '--exclude', 'markdownrevealstyle',
        '--exclude', '.git',
        '-av',
        '%s/' % markdown_file.resolve().parent,
        '%s/' % config['output_path'],
    ]
    check_output(command)

    # Convert from markdown
    output = markdown_to_reveal(markdown_file,
                                reveal_extra=config['reveal_extra'],
                                katex=config['katex'])

    # HTML substitution
    output = tweak_html(output, config)

    # Write index.html
    index = config['output_path'] / 'index.html'
    index.write_text(output)

    # Reload view
    with open(str(config['output_path'] / '.reload'), 'a') as f:
        f.write('x\n')


# Reduce watchdog default buffer delay for faster response times
InotifyBuffer.delay = 0.1


class Handler(FileSystemEventHandler):
    def __init__(self, markdown_file, period=0.1):
        self.markdown_file = markdown_file
        self.period = period
        self.timer = None
        self.set_timer()

    def on_any_event(self, event):
        if self.timer.is_alive():
            return
        self.set_timer()
        self.timer.start()

    def set_timer(self):
        self.timer = Timer(self.period, generate, args=(self.markdown_file,))
