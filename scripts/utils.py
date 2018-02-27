import json
import requests

from website_links import get_absolute_url

REQUESTS_USERAGENT = 'ForkDelta Token Discovery 0.0.1'


def get_request(url, url_param=None, as_json=False):
    """
    Make HTTP get request using the bellow params
    :param url: URL used for the request 
    :param url_param: For now it accepts only one URL parameter
    :param as_json: True if json needed el it will return text
    :return: Json or Text
    """
    if url_param:
        url = url.format(url_param)

    r = requests.get(url, headers={'User-Agent': REQUESTS_USERAGENT})
    if as_json:
        return r.json()
    else:
        return r.text


FORKDELTA_LISTINGS_URL = "https://rawgit.com/forkdelta/forkdelta.github.io/master/config/main.json"


def get_forkdelta_listings(filepath_or_url=FORKDELTA_LISTINGS_URL):
    """
    Load ForkDelta currently listed tokens from the main config
    :param filepath_or_url: ForkDelta Configuration file path 
    :return: List of dict for token symbols and names
    """
    if filepath_or_url.startswith("file://"):
        with open(filepath_or_url) as f:
            return json.load(f)["tokens"]
    else:
        r = requests.get(FORKDELTA_LISTINGS_URL)
        return r.json()["tokens"]


GET_TOKEN_INFO = "https://api.ethplorer.io/getTokenInfo/{}?apiKey=freekey"


def get_token_info(addr):
    """
    Get information of a specific token from Ethplorer 
    :param addr: token address
    :return: dict object with token info
    """
    return get_request(GET_TOKEN_INFO, url_param=addr, as_json=True)


ETHERSCAN_TOKEN_URL = "https://etherscan.io/token/{}"


def get_etherscan_token_page(addr):
    """
    Get token page as HTML from Etherscan 
    :param addr: Token address
    :return: HTML for the token page
    """
    return get_request(ETHERSCAN_TOKEN_URL, url_param=addr, as_json=False)


def get_etherscan_contact_info(addr, html_doc=None):
    """
    Scrape official links area from Etherscan token page 
    :param addr: token address
    :param html_doc: specific HTML code for token page
    :return: list of the available links
    """
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_etherscan_token_page(addr)

    soup = BeautifulSoup(html_doc, 'html.parser')
    return [a.get("data-original-title") for a in
            soup.find(id="ContentPlaceHolder1_tr_officialsite_2").select("ul li a")]


def get_etherscan_notice(addr, html_doc=None):
    """
    Scrape notice from Etherscan token page
    :param addr: token address 
    :param html_doc: specific HTML code for token page
    :return: 
    """
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_etherscan_token_page(addr)

    soup = BeautifulSoup(html_doc, 'html.parser')
    alert_element = soup.select("body > div.wrapper > div > div.alert.alert-warning")
    if alert_element:
        alert_element = alert_element[0]
        button = alert_element.find("button")
        button.extract()
        return alert_element.decode_contents(formatter="html")
    return None


FORKDELTA_GUIDE_URL = "https://rawgit.com/forkdelta/forkdelta.github.io/master/tokenGuides/{}.ejs"


def get_forkdelta_guide(symbol):
    """
    Get a specific token guide from ForkDelta tokenGuides
    :param symbol: token symbol
    :return: HTML for the token guide
    """
    return get_request(FORKDELTA_GUIDE_URL, symbol, as_json=False)


def get_fd_token_website(guide_contents):
    """
    Scrape token website from token guide
    :param guide_contents: HTML code for the token guide 
    :return: website url of the toke
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(guide_contents, 'html.parser')
    footer_link = next(iter(soup.select("blockquote footer a")), None)
    if footer_link:
        return footer_link.attrs["href"]
    return None


def get_fd_token_description(guide_contents):
    """
    Scrape token description from token guide 
    :param guide_contents: 
    :return: 
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(guide_contents, 'html.parser')
    content_extractor = lambda paragraph: paragraph.decode_contents(formatter="html")
    guide_description = list(map(content_extractor, soup.select("blockquote p")))
    if guide_description:
        return "\n".join(guide_description)
    return None


def get_website(url):
    """
    Get the token website as HTML
    :param url: website URL
    :return: HTML code of the token
    """
    import requests

    r = requests.get(url, headers={'User-Agent': REQUESTS_USERAGENT})
    # When debugging website encoding issues...
    # print(r.headers['content-type'], r.encoding, r.apparent_encoding)

    if r.apparent_encoding.lower().startswith("utf"):
        r.encoding = r.apparent_encoding
        html_doc = r.text
    else:
        html_doc = r.text

    return html_doc


def get_website_metas(url, html_doc=None):
    """
    Scrape useful info from meta tags from token website
    :param url: website url
    :param html_doc: specific HTML code
    :return: list of tuple contains scrapped data
    """
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_website(url)

    soup = BeautifulSoup(html_doc, 'html.parser')
    meta_tags = soup.find_all('meta')

    metas = []
    for meta in meta_tags:
        if "name" in meta.attrs and meta.attrs["name"] == "description":
            if meta.attrs["content"].strip():
                metas.append((meta.attrs["name"], meta.attrs["content"]))
        elif "property" in meta.attrs and meta.attrs["property"].startswith("og:"):
            if meta.attrs["content"].strip():
                metas.append((meta.attrs["property"], meta.attrs["content"]))
    return metas


def get_website_links(url, html_doc=None):
    """
    Scrape links from website based on regex defined in website_links module
    :param url: website URL 
    :param html_doc: specific HTML code
    :return: list of all found links that matches the regex patern
    """

    from website_links import get_links

    if not html_doc:
        html_doc = get_website(url)

    return get_links(html_doc)


def get_logo_from_website(website_url, html_doc=None):
    """
    Scrape token logo url from its website
    :param website_url: website token url 
    :param html_doc: specific HTML code
    :return: list of token logo with different sizes
    """
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_request(website_url, as_json=False)

    soup = BeautifulSoup(html_doc, 'html.parser')

    logo = {}
    favicon = soup.find("link", rel="shortcut icon")
    if favicon:
        logo.update({"favicon": get_absolute_url(website_url, favicon.get("href"))})
        logo.update({"default": logo.get("favicon")})

    md_icon = soup.find("link", rel="apple-touch-icon")
    if md_icon:
        logo.update({"md": get_absolute_url(website_url, md_icon.get("href"))})
        logo.update({"default": logo.get("md")})

    sizes = []
    for link in soup.find_all("link", {'rel': ['icon', '']}):
        if link.get("sizes"):
            sizes.append({link.get("sizes"): get_absolute_url(website_url, link.get("href"))})
            if logo.get("default") is None:
                logo.update({"default": get_absolute_url(website_url, link.get("href"))})
        else:
            continue

    if len(sizes) > 0:
        logo.update({"sizes": sizes})

    return logo if len(logo) > 0 else None
