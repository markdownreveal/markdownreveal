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


__version__ = '0.0.7'

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


def load_config() -> Config:
    """
    Load configuration file template.

    Returns
    -------
        The configuration file template.
    """
    config_template = resource_filename(__name__, 'config.template.yaml')
    config = yaml.load(open(config_template))
    config_file = Path('config.yaml')
    if config_file.exists():
        update_config(config, yaml.load(open(config_file)))
    config['local_path'] = Path.home() / config['local_path']
    config['output_path'] = config['local_path'] / 'out'
    config['reveal_extra']['theme'] = config['theme']
    return config


def latest_revealjs_release() -> str:
    """
    Fetch the latest reveal.js release tag.
    """
    releases = 'https://api.github.com/repos/hakimel/reveal.js/releases'
    response = requests.get(releases)
    # Try with GitHub API first
    if response.status_code == 200:
        return response.json()[0]['tag_name']
    # Try to parse latest release manually...
    response = requests.get('https://github.com/hakimel/reveal.js/releases')
    return re.findall('/hakimel/reveal.js/releases/tag/([^"]*)',
                      response.text)[0]


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


def initialize_localdir(localdir: Path, reveal_version: str,
                        style_url: str) -> Path:
    """
    Initialize local directory with the required reveal.js files.

    Parameters
    ----------
    localdir
        Path to store local files.
    reveal_version
        String with the reveal.js version to use (i.e.: `3.0.1`). The value
        `latest` is also allowed.
    style_url
        String with the URL to download the style from.

    Returns
    -------
        Path where output files will be generated, with a symbolic link to
        the corresponding reveal.js downloaded files.
    """
    # Initialize local directory
    outdir = localdir / 'out'
    outdir.mkdir(parents=True, exist_ok=True)

    initialize_localdir_revealjs(outdir, localdir, reveal_version)
    initialize_localdir_style(outdir, localdir, style_url)

    return outdir


def initialize_localdir_revealjs(outdir: Path, localdir: Path,
                                 reveal_version: str) -> Path:
    """
    Initialize local directory with the required style files.

    Parameters
    ----------
    outdir
        Path where output files will be generated, with a symbolic link to
        the corresponding reveal.js downloaded files.
    localdir
        Path to store local files.
    reveal_version
        String with the reveal.js version to use (i.e.: `3.0.1`). The value
        `latest` is also allowed.
    """
    # Download reveal.js
    reveal_path = localdir / reveal_version
    if not reveal_path.exists():
        if reveal_version == 'latest':
            reveal_version = latest_revealjs_release()
        url = 'https://github.com/hakimel/reveal.js/archive/%s.tar.gz'
        url = url % reveal_version
        reveal_tar, headers = urlretrieve(url)
        with tarfile.open(reveal_tar) as tar:
            members = clean_tar_members(tar.getmembers())
            tar.extractall(str(reveal_path), members)
        os.remove(reveal_tar)
    symlink = outdir / 'revealjs'
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(reveal_path, target_is_directory=True)


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


def markdown_to_reveal(input_file: Path, reveal_extra: Config) -> str:
    """
    Transform a Markdown input file to an HTML (reveal.js) output string.

    Parameters
    ----------
    input_file
        Input file path, containing the Markdown code.
    reveal_extra
        Extra configuration parameters for reveal.js.

    Returns
    -------
        The converted string.
    """
    extra_args = [
        '-s',
        '--slide-level=2',
        '-V', 'revealjs-url=revealjs',
    ]
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
    initialize_localdir(config['local_path'],
                        config['reveal_version'],
                        config['style'])

    # rsync
    command = [
        'rsync',
        '--delete',
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
                                reveal_extra=config['reveal_extra'])

    # HTML substitution
    output = tweak_html(output, config)

    # Write index.html
    index = config['output_path'] / 'index.html'
    index.write_text(output)

    # Reload view
    with open(config['output_path'] / '.reload', 'a') as f:
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
