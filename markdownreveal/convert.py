from subprocess import check_output
from sys import platform
from threading import Timer
from typing import List

from pypandoc import convert_text
from watchdog.events import FileSystemEventHandler

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
    extra_args = [
        '-s',
        '--slide-level=2',
        '-V', 'revealjs-url=revealjs',
    ]
    if config['katex']:
        extra_args.extend([
            '--katex=katex/katex.min.js',
            '--katex-stylesheet=katex/katex.min.css',
        ])
    extra_args.extend(pandoc_extra_to_args(config))
    extra_args.extend(reveal_extra_to_args(config))
    input_format = 'markdown'
    if config['emoji_codes']:
        input_format += '+emoji'
    output = convert_text(
        source=text,
        format=input_format,
        to='revealjs',
        extra_args=extra_args,
    )

    # HTML substitution
    output = tweak_html(output, config)

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
    output = markdown_to_reveal(markdown_file.read_text(), config)

    # Write index.html
    index = config['output_path'] / 'index.html'
    index.write_text(output)

    # Reload view
    with open(str(config['output_path'] / '.reload'), 'a') as f:
        f.write('x\n')


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
