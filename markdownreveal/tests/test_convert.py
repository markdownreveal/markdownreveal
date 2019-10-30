"""
Markdownreveal convert module tests.
"""
from os.path import dirname
from pathlib import Path

import yaml

from markdownreveal.config import load_config
from markdownreveal.convert import generate
from markdownreveal.convert import markdown_to_reveal
from markdownreveal.convert import pandoc_extra_to_args
from markdownreveal.convert import reveal_extra_to_args


def test_pandoc_extra_to_args():
    """
    Test `pandoc_extra_to_args()` function.
    """
    text_config = '''
pandoc_extra:
  activated: on
  deactivated: off
  other: 42
    '''
    config = yaml.safe_load(text_config)
    args = pandoc_extra_to_args(config)
    assert len(args) == 2
    assert '--activated' in args
    assert '--deactivated' not in args
    assert '--other=42' in args


def test_reveal_extra_to_args():
    """
    Test `reveal_extra_to_args()` function.
    """
    text_config = '''
reveal_extra:
  key0: value0
  key1: value1
    '''
    config = yaml.safe_load(text_config)
    args = reveal_extra_to_args(config)
    assert len(args) == 4
    assert args[::2] == ['-V', '-V']
    assert 'key0=value0' in args
    assert 'key1=value1' in args


def test_markdown_to_reveal():
    """
    Test `markdown_to_reveal()` function.
    """
    text = '''% Title
% Author
% Date

# Section

## Subsection

Once upon a time

- there were
- some small worms
    '''
    config = load_config()
    html = markdown_to_reveal(text=text, config=config)
    assert '<h1 class="title">Title</h1>' in html
    assert '<p>Once upon a time</p>' in html
    assert '<li>there were</li>' in html


def test_markdown_to_reveal_katex():
    """
    Katex math rendering.
    """
    text = '$$ a^2 = \\sqrt{b^2 + c^2} $$'
    config = load_config()
    # Katex rendering
    config['katex'] = True
    html = markdown_to_reveal(text=text, config=config)
    assert 'katex/katex.min.js' in html
    assert text not in html
    assert text.split('$$')[1].strip() in html
    # No Katex rendering
    config['katex'] = False
    html = markdown_to_reveal(text=text, config=config)
    assert 'katex/katex.min.js' not in html
    assert text in html


def test_markdown_to_reveal_emoji_codes():
    """
    Emoji codes.
    """
    text = ':smile:'
    config = load_config()
    # Emoji codes
    config['emoji_codes'] = True
    html = markdown_to_reveal(text=text, config=config)
    assert '😄' in html
    assert text not in html
    # No emoji codes
    config['emoji_codes'] = False
    html = markdown_to_reveal(text=text, config=config)
    assert '😄' not in html
    assert text in html


def test_generate():
    """
    Test `generate()` function.
    """
    markdown_file = Path(dirname(__file__), 'resources', 'presentation.md')
    generate(markdown_file)
