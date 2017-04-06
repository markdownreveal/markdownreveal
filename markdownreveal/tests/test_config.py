"""
Markdownreveal config module tests.
"""
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from markdownreveal.config import update_config
from markdownreveal.config import load_config


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
