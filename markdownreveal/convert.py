from subprocess import check_output
from threading import Timer

from pypandoc import convert_text
from watchdog.events import FileSystemEventHandler
from watchdog.observers.inotify_buffer import InotifyBuffer

from .config import load_config
from .local import initialize_localdir
from .tweak import tweak_html
from .typing import Config


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
    reveal_extra = config['reveal_extra']
    pandoc_extra = config['pandoc_extra']

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
    for key, value in reveal_extra.items():
        extra_args.extend(['-V', '%s=%s' % (key, value)])
    for key, value in pandoc_extra.items():
        if isinstance(value, bool):
            if value:
                extra_args.append('--' + key)
        else:
            extra_args.extend(['--' + key, value])
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
