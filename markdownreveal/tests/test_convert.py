"""
Markdownreveal convert module tests.
"""
from os.path import dirname
from pathlib import Path
from tempfile import mkstemp

from markdownreveal.convert import markdown_to_reveal
from markdownreveal.convert import generate


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
    html = markdown_to_reveal(tmp, reveal_extra={}, katex=True)
    assert '<p>Once upon a time...</p>' in html
    assert '<li>there were</li>' in html
    tmp.unlink()


def test_generate():
    """
    Test `generate()` function.
    """
    markdown_file = Path(dirname(__file__), 'resources', 'presentation.md')
    generate(markdown_file)
