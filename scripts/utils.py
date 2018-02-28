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


LOGO_DEFAULT_KEY = "default"
LOGO_SIZES_KEY = "sizes"
LOGO_SIZES = {
    # Twitter sizes
    "coin_market_cap": {"16x16": "icon", "32x32": "sd", "64x64": "md", "128x128": "hd"},
    # Twitter sizes
    "twitter": {"normal": "icon", "bigger": "sd", "200x200": "md", "400x400": "hd"}
}


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
        logo.update({"icon": get_absolute_url(website_url, favicon.get("href"))})
        logo.update({LOGO_DEFAULT_KEY: logo.get("icon")})

    md_icon = soup.find("link", rel="apple-touch-icon")
    if md_icon:
        logo.update({"md": get_absolute_url(website_url, md_icon.get("href"))})
        logo.update({LOGO_DEFAULT_KEY: logo.get("md")})

    sizes = []
    for link in soup.find_all("link", {'rel': ['icon', '']}):
        if link.get(LOGO_SIZES_KEY):
            sizes.append({link.get(LOGO_SIZES_KEY): get_absolute_url(website_url, link.get("href"))})
            if logo.get(LOGO_DEFAULT_KEY) is None:
                logo.update({LOGO_DEFAULT_KEY: get_absolute_url(website_url, link.get("href"))})
        else:
            continue

    if len(sizes) > 0:
        logo.update({"sizes": sizes})

    return logo if len(logo) > 0 else None


COINMARKETCAP_TOKEN_URL = "https://coinmarketcap.com/currencies/{}/"

LOGOS_DEFAULT_SIZE = {
    "coin_market_cap": "32x32",
    "twitter": "200x200"
}
COINMARKETCAP_LOGO_URL = "https://files.coinmarketcap.com/static/img/coins/{size}/{filename}"


def generate_sizes_urls(logo_url, default_size=LOGOS_DEFAULT_SIZE["coin_market_cap"]):
    """
    Generate a list of dict that contains possible logo sizes from coinMarketCap 
    :param logo_url: logo URL extracted from coinMarketCap token page
    :param default_size: the image size to be used as default
    :return: 
    """
    filename = logo_url.split("/")[-1]
    result = {
        LOGO_SIZES_KEY: [],
    }
    coin_market_cap_sizes = LOGO_SIZES["coin_market_cap"]
    for size in coin_market_cap_sizes.keys():
        logo_url = COINMARKETCAP_LOGO_URL.format(**{"size": size, "filename": filename})
        result[LOGO_SIZES_KEY].append({size: logo_url})
        if size == default_size:
            result.update({LOGO_DEFAULT_KEY: logo_url})

        result.update({coin_market_cap_sizes[size]: logo_url})

    return result if len(result.get(LOGO_SIZES_KEY)) > 0 else None


def get_logo_from_coinmarketcap(token_name, html_doc=None):
    """
    Scrape token logo url from CoinMarketCap token page if found
    :param token_name: coinMarketCap name
    :param html_doc: specific HTML code
    :return:
    """
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_request(COINMARKETCAP_TOKEN_URL, token_name, as_json=False)

    soup = BeautifulSoup(html_doc, 'html.parser')

    error_404 = soup.find("div", {"class": "title-404"})
    if error_404 is None:
        img_url = soup.find("h1", {"class": "text-large"})
        return generate_sizes_urls(img_url.select("img")[0].get("src"))
    else:
        # print("Token does not exist in CoinMarketCap")
        return None


TWITTER_LOGO_URL = "{url}/{filename}_{size}.{ext}"


def get_logo_from_twitter(twitter_profile, html_doc=None, default_size=LOGOS_DEFAULT_SIZE["twitter"]):
    """
    Scrape token logo url from CoinMarketCap token page if found
    :param twitter_profile: twitter profile url
    :param html_doc: specific HTML code
    :return:
    """
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_request(twitter_profile, as_json=False)

    soup = BeautifulSoup(html_doc, 'html.parser')
    logo_url = soup.find("img", {"class": "ProfileAvatar-image"}).get("src")

    if logo_url:
        result = {}
        url = "/".join(logo_url.split("/")[:-1])
        img = logo_url.split("/")[-1]
        filename = img.split("_")[0]
        ext = img.split(".")[-1]
        twitter_sizes = LOGO_SIZES["twitter"]
        for size in twitter_sizes.keys():
            result.update({
                twitter_sizes[size]: TWITTER_LOGO_URL.format(url=url, filename=filename, size=size, ext=ext)
            })
            if size == default_size:
                result.update({
                    LOGO_DEFAULT_KEY: TWITTER_LOGO_URL.format(url=url, filename=filename, size=size, ext=ext)
                })
        return result
    else:
        return None


def get_token_logo(website_url, website_doc=None, token_name=None, twitter_profile=None):
    """
    Scrape lgo from different sources
    :param website_url: token website 
    :param token_name: coinMarketCap token name
    :param twitter_profile: twitter profile url
    :param website_doc: specific HTML code
    :return: 
    """
    logos = {}

    token_name = token_name[0][1] if len(token_name) > 0 else None
    logos_from_coinmarketcap = None
    if token_name:
        logos_from_coinmarketcap = get_logo_from_coinmarketcap(token_name)
        if logos_from_coinmarketcap:
            logos.update(logos_from_coinmarketcap)

    # Get logos from twitter
    twitter_profile = twitter_profile[0][1] if len(twitter_profile) > 0 else None
    if twitter_profile and not logos_from_coinmarketcap:
        logos_from_twitter = get_logo_from_twitter(twitter_profile)
        logos.update(logos_from_twitter)

    # The last resort is to get logos from website of the token
    if not logos:
        logos_from_website = get_logo_from_website(website_url, html_doc=website_doc) or {}
        logos.update(logos_from_website)

    return logos if logos else None
