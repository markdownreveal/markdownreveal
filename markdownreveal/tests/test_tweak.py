"""
Markdownreveal tweak module tests.
"""
from markdownreveal.tweak import find_indexes


def test_find_indexes():
    """
    Test `find_indexes()` function.
    """
    haystack = ['asdf qwer', 'foo bar', 'foo qwerbar', 'barasdf qwe']
    assert find_indexes(haystack, 'qwer') == [0, 2]
