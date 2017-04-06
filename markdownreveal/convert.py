from pathlib import Path
from subprocess import check_output
from threading import Timer

from pypandoc import convert_file
from watchdog.events import FileSystemEventHandler
from watchdog.observers.inotify_buffer import InotifyBuffer

from .config import load_config
from .local import initialize_localdir
from .tweak import tweak_html
from .typing import Config


def markdown_to_reveal(input_file: Path, reveal_extra: Config,
                       katex: bool) -> str:
    """
    Transform a Markdown input file to an HTML (reveal.js) output string.

    Parameters
    ----------
    input_file
        Input file path, containing the Markdown code.
    reveal_extra
        Extra configuration parameters for reveal.js.
    katex
        Whether to use KaTeX for math rendering.

    Returns
    -------
        The converted string.
    """
    extra_args = [
        '-s',
        '--slide-level=2',
        '-V', 'revealjs-url=revealjs',
    ]
    if katex:
        extra_args.extend([
            '--katex=katex/katex.min.js',
            '--katex-stylesheet=katex/katex.min.css',
        ])
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
    output = markdown_to_reveal(markdown_file,
                                reveal_extra=config['reveal_extra'],
                                katex=config['katex'])

    # HTML substitution
    output = tweak_html(output, config)

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
