"""
Markdownreveal convert module tests.
"""
from os.path import dirname
from pathlib import Path

from markdownreveal.config import load_config
from markdownreveal.convert import markdown_to_reveal
from markdownreveal.convert import generate


def test_markdown_to_reveal():
    """
    Test `markdown_to_reveal()` function.
    """
    text = '''% Title
% Author
% Date

# Section

## Subsection

Once upon a time...

- there were
- some small worms
    '''
    config = load_config()
    html = markdown_to_reveal(text=text, config=config)
    assert '<h1 class="title">Title</h1>' in html
    assert '<p>Once upon a time...</p>' in html
    assert '<li>there were</li>' in html


def test_markdown_to_reveal_katex():
    """
    Katex math rendering.
    """
    text = '$$ a^2 = \sqrt{b^2 + c^2} $$'
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
