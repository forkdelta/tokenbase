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

def get_links(html_doc):
    refs = set()
    soup = BeautifulSoup(html_doc, 'html.parser')
    for a in soup.find_all("a", href=True):
        link = a["href"]
        match = PATTERN.match(link)
        if match:
            refs.add(link)

    links = []
    for ref in refs:
        matching_expr_filter = lambda expr: re.match(PREFIX + expr, ref, flags=re.I)
        matching_expr = next(filter(matching_expr_filter, SITES.keys()), None)
        links.append((SITES[matching_expr], link))
    return links
