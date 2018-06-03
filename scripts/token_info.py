import logging
from requests.exceptions import ConnectionError, MissingSchema, TooManyRedirects
from rfc3986 import uri_reference
import sys
from utils import *
from website_links import classify_link
import yaml
from yaml_utils import *

LISTINGS = get_forkdelta_listings()

DEFAULT_LINK_FIELDS = frozenset(
    ("Website", "Bitcointalk", "Blog", "Whitepaper", "Twitter", "Telegram",
     "Reddit"))


def get_basic_info(addr):
    ethplorer_tokeninfo = get_token_info(addr)
    info = dict(
        addr=addr, decimals=int(ethplorer_tokeninfo.get("decimals", -1)))
    info.update(
        {k: ethplorer_tokeninfo.get(k, "")
         for k in ("name", "symbol")})
    return info


def scrape_etherscan(addr):
    etherscan_doc = get_etherscan_token_page(addr)

    links = get_etherscan_contact_info(addr, html_doc=etherscan_doc)
    notice = get_etherscan_notice(addr, html_doc=etherscan_doc)

    return dict(links=links, notice=notice)


def scrape_coinmarketcap(addr):
    ethdb_entry = get_cmc_ethdb_entry(addr)
    if not ethdb_entry:
        return {"links": []}

    links = [(classify_link(v) or k, v)
             for (k, v) in ethdb_entry["links"].items()
             if not k.startswith("Explorer")]

    cmc_link = "https://coinmarketcap.com/currencies/{}/".format(
        ethdb_entry["website_slug"])
    links.append(("CoinMarketCap", cmc_link))

    return dict(links=links)


def scrape_website(url, render_website=False):
    try:
        html_doc = get_website(url, render_website)
    except (ConnectionError, MissingSchema, TooManyRedirects):
        logging.exception("Failed to fetch {} listed on {}".format(
            website_link, addr))
        return dict(links=[], metas=[])

    metas = get_website_metas(url, html_doc)
    links = get_website_links(url, html_doc)
    if len(links) == 0:
        logging.debug("0 links found, retrying with rendered website")
        # Retry with render
        return scrape_website(url, render_website=True)

    return dict(links=links, metas=metas)


def tuples_with_unique_values(list_of_tuples):
    return [(k, v)
            for (v, k) in dict(((v, k) for (k, v) in list_of_tuples)).items()]


def main(addr, website=None, parse_website=True, guide_mode=True):
    addr = addr.lower()
    print(addr)
    try:
        listing = get_basic_info(addr)
    except:
        logging.exception("Error while retrieving basic information")
        listing = {"addr": addr, "name": "", "symbol": "", "decimals": -1}

    etherscan_info = scrape_etherscan(addr)
    coinmarketcap_info = scrape_coinmarketcap(addr)

    links = etherscan_info["links"] + coinmarketcap_info["links"]
    if website is not None:
        links += [("Website", website)]

    website_metas = []
    if parse_website:
        website_predicate = lambda t: t[0] == "Website"
        website_links = set([v for (k, v) in filter(website_predicate, links)])
        for website_link in website_links:
            logging.debug("Scraping '%s'", website_link)
            website_info = scrape_website(website_link)
            links += website_info["links"]
            website_metas += website_info["metas"]

    links = tuples_with_unique_values(
        [(k, (get_canonical_url(v) or v
              if uri_reference(v).scheme in ("http", "https") else v))
         for (k, v) in links])

    conflicting_symbol_filter = lambda e: e["name"] == listing["symbol"] and e["addr"] != listing["addr"]
    conflicting_listing = next(
        filter(conflicting_symbol_filter, get_forkdelta_listings()), None)

    if conflicting_listing:
        listing["__FORKDELTA_CUSTOM_SYMBOL"] = "AVOID CONFLICT WITH {}".format(
            conflicting_listing["addr"])

    if etherscan_info["notice"] is not None:
        listing["notice"] = LiteralString(etherscan_info["notice"])

    links = sorted(links)
    if guide_mode:
        link_fields = set((entry[0] for entry in links))
        missing_link_fields = DEFAULT_LINK_FIELDS - link_fields
        placeholder_links = [(field, "ADD OR DELETE LINE")
                             for field in missing_link_fields]
    else:
        placeholder_links = []

    listing.update({
        "links": [{
            entry[0]: entry[1]
        } for entry in links + placeholder_links]
    })

    description = ""
    description_meta_filter = lambda e: e[0] in ("description", "og:description")
    if any(filter(description_meta_filter, website_metas)):
        # Use ljust below to keep YAML from getting double new-lines
        if guide_mode:
            description += comment_line("The following options were found")
            description += comment_line(
                "You may need to edit them and you MUST delete commented lines"
            )
        for (meta_name, meta_content) in filter(description_meta_filter,
                                                website_metas):
            if meta_content:
                description += comment_line(
                    "From the website: {} meta tag".format(meta_name))
                description += meta_content.strip()
                description += "\n"

    if guide_mode and not description:
        description = "FILL ME IN"

    listing.update({"description": LiteralString(description.strip())})

    return yaml.dump(
        listing,
        default_flow_style=False,
        explicit_start=True,
        width=YAML_WIDTH,
        indent=YAML_INDENT,
        allow_unicode=True)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(main(sys.argv[1], sys.argv[2]))
    elif len(sys.argv) == 2:
        print(main(sys.argv[1]))
    else:
        print("Usage: script.py <token address> [website url]")
        exit(1)
