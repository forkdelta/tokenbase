from bs4 import BeautifulSoup
import re

PREFIX = r'https?://(?:www\.)?'
DOMAIN = '[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})'
SITES = {
    'bitcointalk.org/': 'Bitcointalk',
    'medium.com/': 'Blog',
    DOMAIN + '/blog': 'Blog',
    'blog.' + DOMAIN: 'Blog',
    'facebook.com/': 'Facebook',
    '(?:[a-z]{2}-[a-z]{2}\\.)?facebook.com/': 'Facebook',
    'fb.com/': 'Facebook',
    'github.com/': 'Github',
    'instagram.com/': 'Instagram',
    'linkedin.com/(?:company/|in/|pub/)': 'Linkedin',
    '(?:[a-z]{2}\\.)?linkedin.com/(?:company/|in/|pub/)': 'Linkedin',
    'reddit.com/(?:r/|u/)': 'Reddit',
    '([a-z0-9]+).slack.com/?': 'Slack',
    't.me/': 'Telegram',
    'telegram.me/': 'Telegram',
    'twitter.com/': 'Twitter',
    'youtube.com/': 'YouTube'
}
PATTERN = re.compile(
    r'%s(%s)' % (PREFIX, '|'.join(SITES.keys())),
    flags=re.I)


def is_absolute(url):
    from urllib.parse import urlparse
    return bool(urlparse(url).netloc)


def get_links(html_doc):
    refs = set()
    soup = BeautifulSoup(html_doc, 'html.parser')

    absolute_href_filter = lambda el: is_absolute(el["href"])
    for a in filter(absolute_href_filter, soup.find_all("a", href=True)):
        link = a["href"]
        match = PATTERN.match(link)
        if match:
            refs.add(link)

    links = []
    for ref in refs:
        matching_expr_filter = lambda expr: re.match(PREFIX + expr, ref, flags=re.I)
        matching_expr = next(filter(matching_expr_filter, SITES.keys()), None)
        links.append((SITES[matching_expr], ref))
    return links


def get_absolute_url(base_url, relative_url):
    try:
        from urlparse import urljoin  # Python2
    except ImportError:
        from urllib.parse import urljoin  # Python3
    return urljoin(base_url, relative_url)
