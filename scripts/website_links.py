from bs4 import BeautifulSoup
from functools import partial
import re
from urllib.parse import urljoin, urlparse

PREFIX = r'https?://(?:www\.)?'
DOMAIN = '[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})'
SITES = {
    'bitcointalk.org/': 'Bitcointalk',
    'medium.com/@?([a-z0-9_\-]+)/?(?:\?|#|$)': 'Blog',
    DOMAIN + '/blog': 'Blog',
    'blog.' + DOMAIN: 'Blog',
    'facebook.com/': 'Facebook',
    '(?:[a-z]{2}-[a-z]{2}\\.)?facebook.com/': 'Facebook',
    'fb.com/': 'Facebook',
    'github.com/': 'Github',
    'instagram.com/': 'Instagram',
    'linkedin.com/(?:company/|pub/)': 'Linkedin',
    '(?:[a-z]{2}\\.)?linkedin.com/(?:company/|pub/)': 'Linkedin',
    'reddit.com/(?:r/|u/)': 'Reddit',
    '([a-z0-9]+).slack.com/?': 'Slack',
    't.me/': 'Telegram',
    'telegram.me/': 'Telegram',
    'twitter.com/@?([a-z0-9_]+)/?(?:\?|#|$)': 'Twitter',
    'youtube.com/': 'YouTube'
}
PATTERN = re.compile(r'%s(%s)' % (PREFIX, '|'.join(SITES.keys())), flags=re.I)


def is_absolute(url):
    return bool(urlparse(url).netloc)


def get_links(url, html_doc):
    refs = set()
    soup = BeautifulSoup(html_doc, 'html.parser')

    absolutize = partial(urljoin, url)
    extract_absolute_href = lambda a_href: absolutize(a_href["href"])
    for href in map(extract_absolute_href, soup.find_all("a", href=True)):
        match = PATTERN.match(href)
        if match:
            refs.add(href)
    return [(classify_link(link), link) for link in refs]


def classify_link(link):
    matching_expr_filter = lambda expr: re.match(PREFIX + expr, link, flags=re.I)
    matching_expr = next(filter(matching_expr_filter, SITES.keys()), None)
    return SITES[matching_expr] if matching_expr else None
