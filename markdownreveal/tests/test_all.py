import json
import time
from pathlib import Path
from tarfile import TarInfo
from tempfile import mkdtemp
from tempfile import mkstemp
from shutil import rmtree

import pytest

from markdownreveal import update_config
from markdownreveal import load_config
from markdownreveal import latest_revealjs_release
from markdownreveal import clean_revealjs_tar_members
from markdownreveal import initialize_localdir
from markdownreveal import markdown_to_reveal
from markdownreveal.tweak import find_indexes


def test_update_config():
    """
    Test `update_config()` function.
    """
    template = {'a': 1, 'b': 2, 'c': {'x': 3, 'y': 4}}
    config = {'b': 8, 'c': {'y': 0, 'z': 2}}
    result = {'a': 1, 'b': 8, 'c': {'x': 3, 'y': 0, 'z': 2}}
    assert update_config(template, config) == result


def test_load_config():
    """
    Test `load_congig()` function.
    """
    # Test configuration file template exists
    assert load_config()


def test_latest_revealjs_release():
    """
    Test `latest_revealjs_release()` function.
    """
    latest = latest_revealjs_release()
    numbers = latest.split('.')
    assert len(numbers) == 3
    assert all(n.isdecimal() for n in numbers)


def test_clean_revealjs_tar_members():
    """
    Test `clean_revealjs_tar_members()` function.
    """
    members = [TarInfo('toplevel'),
               TarInfo('toplevel/index.html'),
               TarInfo('toplevel/foo/bar.xyz')]
    output = [TarInfo('index.html'),
              TarInfo('foo/bar.xyz')]
    result = clean_revealjs_tar_members(members)
    assert all(x.name == y.name for x, y in zip(output, result))


@pytest.mark.parametrize('version,tag', [
    ('latest', latest_revealjs_release()),
    ('3.4.0', '3.4.0'),
])
def test_initialize_localdir(version, tag):
    """
    Test `initialize_localdir()` function.
    """
    localdir = Path(mkdtemp())
    out = initialize_localdir(localdir, version)
    package = json.load(open(str(out / 'revealjs' / 'package.json')))
    assert package['version'] == tag
    # If version is already downloaded initialization should be pretty fast
    t0 = time.time()
    out = initialize_localdir(localdir, version)
    assert time.time() - t0 < 0.01
    rmtree(str(localdir))


def test_find_indexes():
    """
    Test `find_indexes()` function.
    """
    haystack = ['asdf qwer', 'foo bar', 'foo qwerbar', 'barasdf qwe']
    assert find_indexes(haystack, 'qwer') == [0, 2]


def test_markdown_to_reveal():
    """
    Test `markdown_to_reveal()` function.
    """
    tmp = Path(mkstemp()[1])
    tmp.write_text('''
% Title
% Author
% Date

# Section

## Subsection

Once upon a time...

- there were
- some small worms
    ''')
    html = markdown_to_reveal(tmp, {})
    assert '<p>Once upon a time...</p>' in html
    assert '<li>there were</li>' in html
    tmp.unlink()
