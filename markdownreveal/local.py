import os
import tarfile
from hashlib import sha1
from pathlib import Path
from urllib.request import urlretrieve

import requests

from .typing import Config
from .typing import TarMembers


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
    response = requests.get(
        'https://github.com/%s/releases/latest' % github, allow_redirects=True
    )
    return response.url.split('/')[-1]


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
            raise NotImplementedError('Please, report this unexpected error!')
        parts = path.parts[1:]
        if not parts:
            continue
        if parts[0] == 'test':
            continue
        member.name = str(Path(*parts))
        clean.append(member)
    return clean


def initialize_localdir_project(
    github: str,
    outdir: Path,
    localdir: Path,
    project_version: str,
    name: str,
    download_url: str,
) -> Path:
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
        download_url = download_url.format(
            project=github, version=project_version
        )
        reveal_tar, headers = urlretrieve(download_url)
        with tarfile.open(reveal_tar) as tar:
            members = clean_tar_members(tar.getmembers())
            tar.extractall(str(project_path), members)
        os.remove(reveal_tar)
    symlink = outdir / name
    if symlink.exists():
        symlink.unlink()
    symlink.symlink_to(project_path, target_is_directory=True)


def initialize_localdir_style(
    outdir: Path, localdir: Path, style_url: str
) -> Path:
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
        download_url='https://github.com/{project}/archive/{version}.tar.gz',
    )

    # KaTeX
    initialize_localdir_project(
        github='Khan/KaTeX',
        outdir=outdir,
        localdir=localdir,
        project_version=config['katex_version'],
        name='katex',
        download_url='https://github.com/{project}/'
        + 'releases/download/{version}/katex.tar.gz',
    )

    # Style
    initialize_localdir_style(outdir, localdir, config['style'])

    return outdir
