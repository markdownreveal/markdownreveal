import re
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


def find_style_file(filename, config):
    """
    TODO
    """
    outpath = config['local_path'] / 'out'
    filepath = outpath / config['style_path'] / config[filename]
    if not filepath.exists():
        filepath = outpath / 'markdownrevealstyle' / config[filename]
    if not filepath.exists():
        return
    return filepath.relative_to(filepath.parents[1])


def tweak_html_footer(html, footer):
    """
    TODO
    """
    if not footer:
        return False
    text = '<div class="markdownreveal_footer">%s</div>' % footer
    for index in find_indexes(html, '<div class=\"reveal\">'):
        html.insert(index + 1, text)
    return True


def tweak_html_header(html, header):
    """
    TODO
    """
    if not header:
        return
    text = '<div class="markdownreveal_header">%s</div>' % header
    for index in find_indexes(html, '<div class=\"reveal\">'):
        html.insert(index + 1, text)


def tweak_html_warmup(html, config):
    """
    TODO
    """
    if config.get("no_warmup"):
        return
    fname = find_style_file('style_warmup', config)
    if not fname:
        return
    text = '<section><img src="%s" /></section>' % fname
    index = find_indexes(html, 'div class="slides"')[0]
    html.insert(index + 1, text)


def tweak_html_logo(html, config):
    """
    TODO
    """
    fname = find_style_file('style_logo', config)
    if not fname:
        return
    text = '<div class="logo"><img src="%s" /></div>' % fname
    for index in find_indexes(html, '<div class=\"reveal\">'):
        html.insert(index + 1, text)


def tweak_html_background(html, config):
    """
    TODO
    """
    fname = find_style_file('style_background', config)
    if not fname:
        return
    for index in find_indexes(html, '^<section.*'):
        html[index] = html[index].replace(
            '<section', '<section data-background="%s"' % fname, 1
        )


def tweak_html_css(html, config):
    """
    TODO
    """
    fname = find_style_file('style_custom_css', config)
    if not fname:
        return
    index = find_indexes(html, 'stylesheet.*id="theme"')[0]
    text = '<link rel="stylesheet" href="%s">' % fname
    html.insert(index + 1, text)
    return True


def tweak_html_emoji(html):
    """
    Add required scripts to parse emojis and display them with a consistent
    style in all browsers.
    """
    text = """
<script src="https://twemoji.maxcdn.com/v/latest/twemoji.min.js"
  crossorigin="anonymous"></script>
<script>
  function addEvent(element, eventName, fn) {
    if (element.addEventListener)
      element.addEventListener(eventName, fn, false);
    else if (element.attachEvent)
      element.attachEvent('on' + eventName, fn);
  }

  addEvent(window, 'load', function() {
    twemoji.parse(document.body, {'folder': 'svg', 'ext': '.svg'});
  });
</script>
"""
    html.insert(find_indexes(html, '</head>')[0], text)


def tweak_html(html, config):
    """
    TODO
    """
    html = html.splitlines()
    tweak_html_footer(html, config['footer'])
    tweak_html_header(html, config['header'])
    tweak_html_warmup(html, config)
    tweak_html_logo(html, config)
    tweak_html_background(html, config)
    tweak_html_css(html, config)
    tweak_html_emoji(html)
    return '\n'.join(html)
