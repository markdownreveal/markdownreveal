"""
Markdownreveal local module tests.
"""
import json
import time
from pathlib import Path
from tarfile import TarInfo
from tempfile import mkdtemp
from shutil import rmtree

import pytest

from markdownreveal.local import latest_project_release
from markdownreveal.local import clean_tar_members
from markdownreveal.local import initialize_localdir


def test_latest_project_release():
    """
    Test `latest_project_release()` function.
    """
    # Latest reveal.js version
    latest = latest_project_release(github='hakimel/reveal.js')
    numbers = latest.split('.')
    assert len(numbers) == 3
    assert all(n.isdecimal() for n in numbers)
    # Latest KaTeX version
    latest = latest_project_release(github='khan/katex')
    assert latest[0] == 'v'
    latest = latest[1:]
    numbers = latest.split('.')
    assert len(numbers) == 3
    assert all(n.isdecimal() for n in numbers)


def test_clean_tar_members():
    """
    Test `clean_tar_members()` function.
    """
    members = [TarInfo('toplevel'),
               TarInfo('toplevel/index.html'),
               TarInfo('toplevel/foo/bar.xyz')]
    output = [TarInfo('index.html'),
              TarInfo('foo/bar.xyz')]
    result = clean_tar_members(members)
    assert all(x.name == y.name for x, y in zip(output, result))


@pytest.mark.parametrize(
    'reveal_version,katex_version,reveal_tag,katex_tag', [
        (
            'latest',
            'latest',
            latest_project_release(github='hakimel/reveal.js'),
            latest_project_release(github='khan/katex')
        ),
        (
            '3.4.0',
            'v0.7.1',
            '3.4.0',
            'v0.7.1'
        ),
    ]
)
def test_initialize_localdir(reveal_version, katex_version, reveal_tag,
                             katex_tag):
    """
    Test `initialize_localdir()` function.
    """
    localdir = Path(mkdtemp())
    config = {
        'local_path': localdir,
        'reveal_version': reveal_version,
        'katex_version': katex_version,
        'style': '',
    }
    out = initialize_localdir(config)
    package = json.load(open(str(out / 'revealjs' / 'package.json')))
    assert package['version'] == reveal_tag
    katex_readme = out / 'katex' / 'README.md'
    assert katex_tag[1:] in katex_readme.read_text()
    # If version is already downloaded initialization should be pretty fast
    t0 = time.time()
    out = initialize_localdir(config)
    assert time.time() - t0 < 0.01
    rmtree(str(localdir))
