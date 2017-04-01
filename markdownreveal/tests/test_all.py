import json
import os
import time
from pathlib import Path
from tarfile import TarInfo
from tempfile import mkdtemp
from tempfile import mkstemp
from tempfile import TemporaryDirectory
from shutil import rmtree

import pytest

from markdownreveal import update_config
from markdownreveal import load_config
from markdownreveal import latest_project_release
from markdownreveal import clean_tar_members
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


def test_load_config_default():
    """
    Test `load_config()` with default configuration template.
    """
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        # Change home directory for testing
        os.environ['MARKDOWNREVEAL_HOME'] = str(tmpdir)
        # Load configuration
        config = load_config()

    assert config['local_path'] == tmpdir / '.markdownreveal'
    assert config['output_path'] == config['local_path'] / 'out'
    assert config['footer'] == ''
    assert config['header'] == ''
    assert 'markdownreveal/style-default' in config['style']


def test_load_config_local():
    """
    Test `load_config()` with local configuration file.
    """
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        # Change home directory for testing
        os.environ['MARKDOWNREVEAL_HOME'] = str(tmpdir)
        # Create local configuration file
        config_file = tmpdir / 'config.yaml'
        config_file.write_text('footer: "local footer"\n'
                               'header: "local header"\n'
                               'style: "https://other/style/file.tar.gz"')
        # Load configuration
        old = Path.cwd()
        os.chdir(str(tmpdir))
        config = load_config()
        os.chdir(str(old))

    assert config['local_path'] == tmpdir / '.markdownreveal'
    assert config['output_path'] == config['local_path'] / 'out'
    assert config['footer'] == 'local footer'
    assert config['header'] == 'local header'
    assert 'other/style' in config['style']


def test_load_config_local_and_style():
    """
    Test `load_config()` with local and style configuration files. Local file
    should always override style, which should override template.
    """
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        # Change home directory for testing
        os.environ['MARKDOWNREVEAL_HOME'] = str(tmpdir)
        # Create local configuration file
        config_file = tmpdir / 'config.yaml'
        config_file.write_text('footer: "local footer"')
        # Create style configuration file
        style_path = tmpdir / '.markdownreveal' / 'out' / 'markdownrevealstyle'
        style_path.mkdir(parents=True)
        config_file = style_path / 'config.yaml'
        config_file.write_text('footer: "style footer"\n'
                               'header: "style header"')
        # Load configuration
        old = Path.cwd()
        os.chdir(str(tmpdir))
        config = load_config()
        os.chdir(str(old))

    assert config['local_path'] == tmpdir / '.markdownreveal'
    assert config['output_path'] == config['local_path'] / 'out'
    assert config['footer'] == 'local footer'
    assert config['header'] == 'style header'
    assert 'markdownreveal/style-default' in config['style']


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
