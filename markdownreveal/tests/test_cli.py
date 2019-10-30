from os.path import dirname
from pathlib import Path

from markdownreveal.commands import zip as cmd_zip


def test_zip(clirunner, validate_cliresult):
    """
    Test `zip` cli command.
    """
    with clirunner.isolated_filesystem():
        markdown_file = Path(dirname(__file__), 'resources', 'presentation.md')
        result = clirunner.invoke(cmd_zip, [str(markdown_file)])
        validate_cliresult(result)
