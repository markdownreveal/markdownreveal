from distutils.version import LooseVersion
from subprocess import check_output
from sys import platform
from threading import Timer
from typing import List

import requests
from pypandoc import convert_text
from pypandoc import get_pandoc_version
from watchdog.events import RegexMatchingEventHandler

from .config import load_config
from .local import initialize_localdir
from .tweak import tweak_html
from .typing import Config

if platform == 'linux':
    from watchdog.observers.inotify_buffer import InotifyBuffer

    # Reduce watchdog default buffer delay for faster response times
    InotifyBuffer.delay = 0.1


def pandoc_extra_to_args(config: Config) -> List[str]:
    """
    Transform Pandoc extra configuration options into Pandoc arguments.

    Parameters
    ----------
    config
        Markdownreveal configuration.

    Returns
    -------
        A list with all the Pandoc arguments.
    """
    arguments = []
    for key, value in config['pandoc_extra'].items():
        if isinstance(value, bool):
            if value:
                arguments.append('--' + key)
        else:
            arguments.append('--{}={}'.format(key, value))
    return arguments


def reveal_extra_to_args(config: Config) -> List[str]:
    """
    Transform reveal.js extra configuration options into Pandoc arguments.

    Parameters
    ----------
    config
        Markdownreveal configuration.

    Returns
    -------
        A list with all the Pandoc arguments.
    """
    arguments = []
    for key, value in config['reveal_extra'].items():
        arguments.extend(['-V', '%s=%s' % (key, value)])
    return arguments


def markdown_to_reveal(text: str, config: Config) -> str:
    """
    Transform a Markdown input file to an HTML (reveal.js) output string.

    Parameters
    ----------
    markdown_text
        Markdown text to convert to HTML.
    config
        Markdownreveal configuration.

    Returns
    -------
        The converted string.
    """
    extra_args = ['-s', '--slide-level=2', '-V', 'revealjs-url=revealjs']
    if config['katex']:
        pandoc_version = get_pandoc_version()
        if LooseVersion(pandoc_version) < LooseVersion('2.0'):
            extra_args.extend(
                [
                    '--katex=katex/katex.min.js',
                    '--katex-stylesheet=katex/katex.min.css',
                ]
            )
        else:
            extra_args.extend(['--katex=katex/'])
    extra_args.extend(pandoc_extra_to_args(config))
    extra_args.extend(reveal_extra_to_args(config))
    input_format = 'markdown'
    if config['emoji_codes']:
        input_format += '+emoji'
    output = convert_text(
        source=text, format=input_format, to='revealjs', extra_args=extra_args
    )

    # HTML substitution
    output = tweak_html(output, config)

    return output


def generate(markdown_file, no_warmup=False):
    """
    Generate Markdownreveal project.
    """
    # Reload config
    config = load_config()

    # If the --no-warmup option was specified, do not generate the warmup slide
    # The 'no_warmup' key in the config makes the tweak_html_warmup function
    # return None, skipping the slide generation
    config['no_warmup'] = no_warmup

    # Initialize localdir
    initialize_localdir(config)

    # rsync
    command = [
        'rsync',
        '--delete',
        '--exclude',
        'katex',
        '--exclude',
        'revealjs',
        '--exclude',
        'markdownrevealstyle',
        '--exclude',
        '.git',
        '-av',
        '%s/' % markdown_file.resolve().parent,
        '%s/' % config['output_path'],
    ]
    check_output(command)

    # Convert from markdown
    output = markdown_to_reveal(markdown_file.read_text(), config)

    # Write index.html
    index = config['output_path'] / 'index.html'
    index.write_text(output)


def generate_and_reload(markdown_file, reload_url):
    """
    Generate Markdownreveal project and reload web browser view.
    """
    generate(markdown_file)
    requests.get(reload_url)


class Handler(RegexMatchingEventHandler):
    def configure(self, markdown_file, reload_url, period=0.1):
        self.markdown_file = markdown_file
        self.reload_url = reload_url
        self.period = period
        self.timer = None
        self.set_timer()

    def on_any_event(self, event):
        if self.timer.is_alive():
            return
        self.set_timer()
        self.timer.start()

    def set_timer(self):
        self.timer = Timer(
            self.period,
            generate_and_reload,
            args=(self.markdown_file, self.reload_url),
        )
