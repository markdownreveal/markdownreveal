import re
from pathlib import Path
from typing import List


def find_indexes(haystack: List[str], regex: str) -> List[int]:
    """
    Find indexes in a list where a regular expression matches.

    Parameters
    ----------
    haystack
        List of strings.
    regex
        Regular expression to match.

    Returns
    -------
        The indexes where the regular expression was found.
    """
    return [i for i, item in enumerate(haystack) if re.search(regex, item)]


def tweak_html_css(html, custom_css):
    """
    TODO
    """
    if not custom_css:
        return
    index = find_indexes(html, 'stylesheet.*id="theme"')[0]
    text = '<link rel="stylesheet" href="%s">' % custom_css
    html.insert(index + 1, text)


def tweak_html_warmup(html, warmup):
    """
    TODO
    """
    if not warmup.exists():
        return
    text = '<section><img src="%s" /></section>' % warmup
    index = find_indexes(html, 'div class="slides"')[0]
    html.insert(index + 1, text)


def tweak_html_footer(html, footer):
    """
    TODO
    """
    if not footer:
        return
    text = '<div class="footer">%s</div>' % footer
    for index in find_indexes(html, '<div class=\"reveal\">'):
        html.insert(index + 1, text)


def tweak_html_header(html, header):
    """
    TODO
    """
    if not header:
        return
    text = '<div class="header">%s</div>' % header
    for index in find_indexes(html, '<div class=\"reveal\">'):
        html.insert(index + 1, text)


def tweak_html_logo(html, logo):
    """
    TODO
    """
    if not logo.exists():
        return
    text = '<div class="logo"><img src="%s" /></div>' % logo
    for index in find_indexes(html, '<div class=\"reveal\">'):
        html.insert(index + 1, text)


def tweak_html_background(html, background):
    """
    TODO
    """
    if not background.exists():
        return
    text = '<section data-background="%s">' % background
    for index in find_indexes(html, '<section>'):
        html[index] = html[index].replace('<section>', text)


def tweak_html(html, config):
    """
    TODO
    """
    html = html.splitlines()
    tweak_html_css(html, config['custom_css'])
    tweak_html_warmup(html, Path(config['warmup']))
    tweak_html_footer(html, config['footer'])
    tweak_html_header(html, config['header'])
    tweak_html_logo(html, Path(config['logo']))
    tweak_html_background(html, Path(config['background']))
    return '\n'.join(html)
