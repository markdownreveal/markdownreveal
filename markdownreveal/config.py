import collections
import os
from pathlib import Path

import yaml
from pkg_resources import resource_filename

from .typing import Config


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
    config = yaml.safe_load(open(config_template))

    # Local configuration (load first for style path)
    local_config = {}
    config_file = Path('config.yaml')
    if config_file.exists():
        local_config = yaml.safe_load(config_file.read_text())
        update_config(config, local_config)
    complete_config(config)

    # Style configuration
    style_config = {}
    config_file = config['output_path'] / 'markdownrevealstyle' / 'config.yaml'
    if config_file.exists():
        style_config = yaml.safe_load(config_file.read_text())
        update_config(config, style_config)
    complete_config(config)

    # Local configuration (override style configuration)
    update_config(config, local_config)
    complete_config(config)

    return config
